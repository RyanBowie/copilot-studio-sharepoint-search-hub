"""Offline evaluation of the formatter's small expression subset, not a cloud runtime."""

import re
import unittest
from urllib.parse import unquote

from test_search_export_flow import FLOW, walk_actions


def evaluate_format(expression, context):
    tokens = re.findall(r"'(?:[^']|'')*'|\?\[|[A-Za-z_]\w*|\d+|[(),\]]", expression.removeprefix("@"))
    position = 0

    def parse():
        nonlocal position
        token = tokens[position]
        position += 1
        if token.startswith("'"):
            node = ("literal", token[1:-1].replace("''", "'"))
        elif token in ("true", "false"):
            node = ("literal", token == "true")
        elif token.isdigit():
            node = ("literal", int(token))
        else:
            assert tokens[position] == "("
            position += 1
            arguments = []
            while tokens[position] != ")":
                arguments.append(parse())
                if tokens[position] != ")":
                    assert tokens[position] == ","
                    position += 1
            position += 1
            node = (token, arguments)
        while position < len(tokens) and tokens[position] == "?[":
            position += 1
            key = parse()
            assert tokens[position] == "]"
            position += 1
            node = ("get", [node, key])
        return node

    def evaluate(node):
        name, values = node
        if name == "literal":
            return values
        if name == "if":
            return evaluate(values[1] if evaluate(values[0]) else values[2])
        values = [evaluate(value) for value in values]
        functions = {
            "variables": lambda key: context["variables"][key],
            "body": lambda key: context["bodies"][key],
            "triggerBody": lambda: context["trigger"],
            "get": lambda obj, key: (obj or {}).get(key),
            "and": lambda *args: all(args),
            "equals": lambda a, b: a == b,
            "greater": lambda a, b: a > b,
            "length": len,
            "string": lambda value: "" if value is None else str(value),
            "concat": lambda *args: "".join(str(value) for value in args),
            "decodeUriComponent": unquote,
            "join": lambda values, separator: separator.join(values),
            "coalesce": lambda *args: next((value for value in args if value is not None), None),
            "replace": lambda value, old, new: value.replace(old, new),
        }
        return functions[name](*values)

    tree = parse()
    assert position == len(tokens), "Unparsed formatter expression"
    return evaluate(tree)


def fictional_context():
    lines = [
        f"| **[{'🌐' if i % 2 == 0 else '📄'} Example {'page' if i % 2 == 0 else 'document'} {i:02}](https://contoso.sharepoint.com/sites/Fictional/"
        f"{'SitePages' if i % 2 == 0 else 'Documents'}/example-{i:02}.{'aspx' if i % 2 == 0 else 'docx'})**"
        " | 2026-09-01 | 2026-09-10 | `example`; `synthetic` |"
        for i in range(1, 11)
    ]
    return {"variables": {"Started": True, "PreviewRows": [{}] * 10, "PreviewLines": lines,
                          "IndexTotal": 112, "Result": "Original startup status."},
            "trigger": {"scope": "All"}, "bodies": {"Selected_profile": {"mail": "example.user@example.invalid"}}}


class SuccessFormattingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        definition = FLOW.build_definition(FLOW.load_policy(), (FLOW.TARGET / "RuntimeSearchResults.template.xlsx").read_bytes())
        cls.actions = {name: action for name, action, *_ in walk_actions(definition["actions"])}
        cls.expression = cls.actions["Format_chat_result"]["inputs"]

    def test_success_has_restrained_hierarchy_and_pending_delivery_callout(self):
        text = evaluate_format(self.expression, fictional_context())
        self.assertTrue(text.startswith("## 🔎 SharePoint results\n\n**Scope:** All · **Index estimate:** 112"))
        self.assertIn("> 📄 **Private Excel export started**\n> **Verified recipient:** example.user@example.invalid", text)
        self.assertIn("> Delivery is pending.", text)
        self.assertIn("only after row and access verification", text)
        summary = text.split("### Verified matches")[0]
        self.assertEqual(summary.count("🔎") + summary.count("📄"), 2)
        self.assertNotIn("<", text)

    def test_ten_table_rows_and_all_values_are_reused_without_rewriting(self):
        context = fictional_context()
        text = evaluate_format(self.expression, context)
        table = "\n".join([
            "| File or page | Created (UTC) | Modified (UTC) | Stored tags |",
            "| --- | :---: | :---: | --- |",
            *context["variables"]["PreviewLines"],
        ])
        self.assertIn(table, text)
        self.assertEqual(text.count("| **["), 10)
        self.assertNotIn("🔎", self.actions["Remember_preview_line"]["inputs"]["value"])
        self.assertIn("📄", self.actions["Remember_preview_line"]["inputs"]["value"])

    def test_nonstarted_results_are_verbatim_without_profile_access(self):
        for result in ("No matches. No workbook or email was created.", "No search was run.", "Authentication failed."):
            context = fictional_context()
            context["variables"].update(Started=False, PreviewRows=[], Result=result)
            context["bodies"] = {}
            self.assertEqual(evaluate_format(self.expression, context), result)

    def test_unavailable_preview_retains_original_warning_and_status(self):
        context = fictional_context()
        context["variables"].update(PreviewRows=[], PreviewLines=[])
        context["bodies"] = {}
        self.assertEqual(evaluate_format(self.expression, context),
                         "Original startup status.\n\nA verified chat preview is unavailable. The private export will still verify its results before delivery.")

    def test_footer_preserves_limits_privacy_count_semantics_and_recipient_escaping(self):
        context = fictional_context()
        context["bodies"]["Selected_profile"]["mail"] = "example_user@example.invalid"
        text = evaluate_format(self.expression, context)
        self.assertIn(r"example\_user@example.invalid", text)
        for value in ("10 results", "20 checked candidates", "1000 rows", "2000 candidates",
                      "40 search pages", "12 batches of 20 sites", "Source permissions still apply",
                      "Exports may be partial", "final exported-row count", "omission details"):
            self.assertIn(value, text)
        self.assertIn("\n\n---\n\n**Preview:**", text)


if __name__ == "__main__":
    unittest.main()
