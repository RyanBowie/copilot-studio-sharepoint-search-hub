"""Evaluate only the generated preview WDL subset, then parse native Markdown offline."""

from datetime import datetime
from html.parser import HTMLParser
import re
from urllib.parse import quote, unquote

from markdown_it import MarkdownIt


def evaluate(expression, context):
    tokens = re.findall(r"'(?:[^']|'')*'|\?\[|[A-Za-z_]\w*|\d+|[(),\]]", expression.removeprefix("@"))
    position = 0

    def parse():
        nonlocal position
        token = tokens[position]
        position += 1
        if token.startswith("'"):
            node = ("literal", token[1:-1].replace("''", "'"))
        elif token in ("true", "false", "null"):
            node = ("literal", {"true": True, "false": False, "null": None}[token])
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

    def run(node):
        name, values = node
        if name == "literal":
            return values
        if name == "if":
            return run(values[1] if run(values[0]) else values[2])
        values = [run(value) for value in values]
        functions = {
            "outputs": lambda key: context["outputs"][key],
            "body": lambda key: context["bodies"][key],
            "item": lambda: context["item"],
            "get": lambda obj, key: (obj or {}).get(key),
            "and": lambda *args: all(args),
            "equals": lambda a, b: a == b,
            "greater": lambda a, b: a > b,
            "lessOrEquals": lambda a, b: a <= b,
            "length": len, "trim": str.strip,
            "empty": lambda value: value is None or value in ("", [], {}),
            "string": lambda value: "" if value is None else str(value),
            "concat": lambda *args: "".join(str(value) for value in args),
            "decodeUriComponent": unquote,
            "uriComponent": lambda value: quote(value, safe="-._~"),
            "toLower": str.lower, "endsWith": lambda value, suffix: value.endswith(suffix),
            "join": lambda values, separator: separator.join(values),
            "split": str.split, "take": lambda value, count: value[:count],
            "createArray": lambda *args: list(args),
            "coalesce": lambda *args: next((value for value in args if value is not None), None),
            "replace": lambda value, old, new: value.replace(old, new),
            "formatDateTime": lambda value, pattern: datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%Y-%m-%d"),
        }
        return functions[name](*values)

    tree = parse()
    assert position == len(tokens), "Unparsed expression"
    return run(tree)


class Table(HTMLParser):
    def __init__(self, markdown):
        super().__init__(convert_charrefs=True)
        self.rows, self.stack = [], []
        self.cell = None
        self.feed(MarkdownIt("commonmark").enable("table").render(markdown))

    def handle_starttag(self, tag, attrs):
        self.stack.append(tag)
        if tag == "tr":
            self.rows.append([])
        if tag in ("td", "th"):
            self.cell = {"text": "", "links": [], "code": [], "outsideLink": "", "strongLinkText": "", "attrs": dict(attrs)}
            self.rows[-1].append(self.cell)
        if self.cell is not None and tag == "a":
            self.cell["links"].append(dict(attrs)["href"])
        if self.cell is not None and tag == "code":
            self.cell["code"].append("")

    def handle_endtag(self, tag):
        if tag in ("td", "th"):
            self.cell = None
        assert self.stack.pop() == tag

    def handle_data(self, data):
        if self.cell is not None:
            self.cell["text"] += data
            if "a" not in self.stack:
                self.cell["outsideLink"] += data
            elif "strong" in self.stack:
                self.cell["strongLinkText"] += data
            if "code" in self.stack:
                self.cell["code"][-1] += data
