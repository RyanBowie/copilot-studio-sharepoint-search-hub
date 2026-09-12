from pathlib import Path
import sys
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from authoring_yaml import dump_authoring_yaml


class AuthoringYamlTests(unittest.TestCase):
    def test_long_single_line_scalars_are_not_soft_wrapped(self):
        message = "I can search approved files and pages. " * 12
        value = {"kind": "SendActivity", "activity": message}
        text = dump_authoring_yaml(value)
        self.assertEqual(yaml.safe_load(text), value)
        self.assertEqual(len(text.splitlines()), 2)

    def test_multiline_scalars_use_literal_blocks(self):
        value = {"instructions": "First line.\nSecond line.\nThird line."}
        text = dump_authoring_yaml(value)
        self.assertIn("instructions: |-\n", text)
        self.assertNotIn("\n\n", text)
        self.assertEqual(yaml.safe_load(text), value)

    def test_controlled_topic_retains_question_after_full_intro(self):
        topic = yaml.safe_load(
            (ROOT / "topics" / "SearchSharePoint.mcs.yml").read_text(encoding="utf-8-sig")
        )
        topic.pop("mcs.metadata", None)
        text = dump_authoring_yaml(topic)
        lines = text.splitlines()
        intro = topic["beginDialog"]["actions"][0]["activity"]
        line = next(index for index, value in enumerate(lines) if value.strip().startswith("activity:"))
        self.assertIn(intro, lines[line])
        self.assertEqual(lines[line + 1].strip(), "- kind: Question")
        self.assertEqual(yaml.safe_load(text), topic)
        expression = topic["beginDialog"]["actions"][2]["value"]
        self.assertTrue(any(expression in value for value in lines))


if __name__ == "__main__":
    unittest.main()
