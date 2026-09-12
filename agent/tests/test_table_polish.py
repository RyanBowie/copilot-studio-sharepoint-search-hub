import copy
import json
import random
import unittest

from markdown_preview_harness import Table, evaluate
from test_search_export_flow import FLOW, walk_actions


HEADER = "| File or page | Created (UTC) | Modified (UTC) | Stored tags |\n| --- | :---: | :---: | --- |"
URL = "https://contoso.sharepoint.com/sites/IT/Documents/Example.docx"


def context(title="Device guidance", tags="IT;Devices;New starters", name="Example.docx", kind="Guidance"):
    return {
        "outputs": {"Preview_row": {"Title": title, "Tags": tags, "Type": kind, "URL": URL,
                                    "CreatedUTC": "2026-09-01T12:34:56.1234567Z",
                                    "ModifiedUTC": "2026-09-10T08:15:27.7654321Z"}},
        "bodies": {"Read_preview_item": {"File": {"Name": name}}},
    }


class TablePolishTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        definition = FLOW.build_definition(FLOW.load_policy(), (FLOW.TARGET / "RuntimeSearchResults.template.xlsx").read_bytes())
        cls.actions = {name: value for name, value, *_ in walk_actions(definition["actions"])}

    def render(self, value):
        current = copy.deepcopy(value)
        selected = self.actions["Select_preview_tag_labels"]["inputs"]
        parts = evaluate(selected["from"], current)
        current["bodies"]["Select_preview_tag_labels"] = [
            evaluate(selected["select"], {**current, "item": part}) for part in parts
        ]
        line = evaluate(self.actions["Remember_preview_line"]["inputs"]["value"], current)
        return line, Table(HEADER + "\n" + line).rows[1]

    def test_bold_title_and_glyph_are_inside_the_only_link(self):
        line, row = self.render(context())
        self.assertTrue(line.startswith("| **[📄 Device guidance]("))
        self.assertEqual(row[0]["links"], [URL])
        self.assertEqual(row[0]["text"], "📄 Device guidance")
        self.assertEqual(row[0]["strongLinkText"], row[0]["text"])
        self.assertEqual(row[0]["outsideLink"], "")

    def test_glyph_uses_the_existing_verified_file_page_predicate_not_documenttype_guessing(self):
        for name, category, glyph in (("Guide.aspx", "Policy", "🌐 "), ("GUIDE.ASPX", "DOCX", "🌐 "),
                                      ("Example.docx", "Page", "📄 "), ("Example.xlsx", "Finance", "📄 "),
                                      ("", "Page", ""), (None, "Page", "")):
            with self.subTest(name=name, category=category):
                _, row = self.render(context(name=name, kind=category))
                self.assertEqual(row[0]["text"], glyph + "Device guidance")
        self.assertIn("Read_preview_item", self.actions["Remember_preview_line"]["inputs"]["value"])
        self.assertNotIn("['Type']", self.actions["Remember_preview_line"]["inputs"]["value"])

    def test_four_separate_columns_have_centered_unchanged_utc_dates(self):
        value = context()
        before = copy.deepcopy(value)
        _, row = self.render(value)
        self.assertEqual(len(row), 4)
        self.assertEqual([cell["text"] for cell in row[1:3]], ["2026-09-01", "2026-09-10"])
        self.assertEqual([cell["attrs"].get("style") for cell in row[1:3]], ["text-align:center"] * 2)
        self.assertEqual(value, before)
        self.assertNotIn("2026", row[0]["text"])

    def test_missing_dates_and_tags_keep_plain_explicit_markers(self):
        value = context(tags="")
        value["outputs"]["Preview_row"].update(CreatedUTC="", ModifiedUTC=None)
        _, row = self.render(value)
        self.assertEqual([cell["text"] for cell in row[1:]], ["Not supplied"] * 3)
        self.assertEqual(row[3]["code"], [])

    def test_short_individual_ascii_labels_are_code_styled_without_changing_values(self):
        _, row = self.render(context())
        self.assertEqual(row[3]["code"], ["IT", "Devices", "New starters"])
        self.assertEqual(row[3]["text"], "IT; Devices; New starters")
        self.assertEqual(row[3]["links"], [])

    def test_code_labels_are_bounded_and_unsafe_or_wide_values_remain_plain(self):
        for tag in ("x" * 17, "東京", "emoji🙂", "`tick`", "pipe|value", "<script>", "&copy;",
                    "[click](https://example.invalid)", " a", "a ", "a\tb", "a\nb", "a\rb"):
            with self.subTest(tag=tag):
                _, row = self.render(context(tags=tag))
                self.assertEqual(row[3]["code"], [])
                self.assertEqual(row[3]["links"], [])
                self.assertEqual(row[3]["text"], tag.replace("\r", " ").replace("\n", " ").strip())
        _, row = self.render(context(tags="x" * 16))
        self.assertEqual(row[3]["code"], ["x" * 16])

    def test_empty_segments_and_delimiters_are_preserved_not_filtered(self):
        _, row = self.render(context(tags="one;;two;"))
        self.assertEqual(row[3]["text"], "one; ; two;")
        self.assertEqual(row[3]["code"], ["one", "two"])
        self.assertNotIn("Not supplied", row[3]["text"])

    def test_existing_two_hundred_character_cutoff_and_notice_are_preserved(self):
        for raw in ("x" * 199, "x" * 200, "x" * 201, "x" * 197 + ";xx", "a;" * 200):
            value = context(tags=raw)
            line, row = self.render(value)
            spaced = raw.replace(";", "; ")
            expected = spaced[:200] + "... (full tags in Excel)" if len(spaced) > 200 else spaced
            self.assertEqual(row[3]["text"], expected.strip())
            self.assertEqual("full tags in Excel" in line, len(spaced) > 200)
            self.assertEqual(value["outputs"]["Preview_row"]["Tags"], raw)
            if len(spaced) > 200:
                self.assertEqual(row[3]["code"], [])

    def test_entities_backticks_pipes_and_markdown_never_create_extra_cells_or_links(self):
        values = ["[click](javascript:alert(1))", "![image](https://example.invalid/x)",
                  r"backslash\|pipe", "x`y``z", "&lt;b&gt;&copy;&#124;", "<b>not HTML</b>",
                  "**bold** _emphasis_", "trailing title ", " leading title", "@{outputs('secret')}"]
        for value in values:
            with self.subTest(value=value):
                _, row = self.render(context(title=value, tags=value))
                self.assertEqual(len(row), 4)
                self.assertEqual(row[0]["text"], "📄 " + value)
                self.assertEqual(row[0]["strongLinkText"], row[0]["text"])
                self.assertEqual(row[0]["links"], [URL])
                self.assertEqual(row[3]["text"], value.replace(";", "; ").strip())
                self.assertEqual(row[3]["links"], [])

    def test_deterministic_injection_fuzz_keeps_exact_title_and_tag_characters(self):
        generator = random.Random(7319)
        alphabet = "Ab9 _-*[]()!`|\\\\<>&#~;🙂"
        for _ in range(100):
            value = "".join(generator.choice(alphabet) for _ in range(35))
            _, row = self.render(context(title=value, tags=value))
            self.assertEqual(len(row), 4)
            self.assertEqual(row[0]["text"], "📄 " + value)
            self.assertEqual(row[0]["strongLinkText"], row[0]["text"])
            self.assertEqual(row[3]["text"], value.replace(";", "; ").strip())
            self.assertEqual(row[3]["links"], [])

    def test_label_projection_is_bounded_and_has_no_new_connector_or_output_contract(self):
        action = self.actions["Select_preview_tag_labels"]
        self.assertEqual(action["type"], "Select")
        self.assertEqual(action["runAfter"], {"Remember_preview_url": ["Succeeded"]})
        self.assertEqual(self.actions["Remember_preview_line"]["runAfter"], {"Select_preview_tag_labels": ["Succeeded"]})
        self.assertIn("lessOrEquals(length(item()),16)", action["inputs"]["select"])
        self.assertEqual(self.actions["Respond_to_agent"]["inputs"]["body"], {"result": "@outputs('Format_chat_result')"})
        self.assertEqual((FLOW.PREVIEW_ROWS, FLOW.PREVIEW_CANDIDATES, FLOW.PAGE_SIZE), (10, 20, 100))
        parts = evaluate(action["inputs"]["from"], context(tags=";" * 10000))
        self.assertEqual(len(parts), 1)
        self.assertLessEqual(len(parts[0]), 226)


if __name__ == "__main__":
    unittest.main()
