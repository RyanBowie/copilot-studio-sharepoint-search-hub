import hashlib
import importlib.util
import io
import json
import unittest

import jsonschema
from PIL import Image
import yaml

from test_search_export_flow import FLOW, ROOT
import banner_cards as BANNER


def objects(value):
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from objects(item)
    elif isinstance(value, list):
        for item in value:
            yield from objects(item)


class RichBannerTests(unittest.TestCase):
    def test_all_five_context_cards_validate_against_official_schema_15(self):
        schema = json.loads((ROOT / "cards" / "schema" / "adaptive-card-1.5.json").read_text())
        jsonschema.Draft6Validator.check_schema(schema)
        validator = jsonschema.Draft6Validator(schema)
        for scope in BANNER.SCOPES:
            card = BANNER.card(scope)
            validator.validate(card)
            self.assertEqual(card["version"], "1.5")
            self.assertEqual(card["body"][0]["text"], f"{scope} SharePoint search")

    def test_context_does_not_claim_success_export_or_delivery(self):
        for scope in BANNER.SCOPES:
            card = BANNER.card(scope)
            text = " ".join(str(node.get("text", "")) for node in objects(card)).lower()
            for forbidden in ("success", "delivered", "export started", "verified matches", "found"):
                self.assertNotIn(forbidden, text)
            self.assertIn("selected accounts", text)

    def test_card_has_no_table_results_actions_inputs_or_host_width_override(self):
        for node in objects(BANNER.card("HR")):
            kind = node.get("type", "")
            self.assertNotEqual(kind, "Table")
            self.assertFalse(kind.startswith(("Action.", "Input.")))
            if kind == "ColumnSet":
                self.assertLessEqual(len(node["columns"]), 2)
            self.assertNotIn("msteams", node)

    def test_images_are_inline_pngs_with_alt_text_and_small_bounded_payload(self):
        for scope in BANNER.SCOPES:
            card = BANNER.card(scope)
            data = json.dumps(card, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            self.assertLessEqual(len(data), BANNER.MAX_CARD_BYTES)
            images = [node for node in objects(card) if node.get("type") == "Image"]
            self.assertEqual(len(images), 2)
            self.assertTrue(all(image["url"].startswith("data:image/png;base64,") and image["altText"] for image in images))
            self.assertEqual(card["fallbackText"], f"{scope} SharePoint search")

    def test_original_scope_images_and_unmodified_official_icon_have_provenance(self):
        manifest = json.loads((ROOT / "cards" / "assets.json").read_text())
        self.assertEqual(set(manifest["themes"]), set(BANNER.SCOPES))
        for value in manifest["themes"].values():
            path = ROOT / "cards" / value["file"]
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), value["sha256"])
            with Image.open(path) as image:
                self.assertEqual(image.size, (640, 96))
                self.assertEqual(image.format, "PNG")
            self.assertLess(path.stat().st_size, 3000)
        value = manifest["thirdParty"]["assets/sharepoint-48.png"]
        self.assertTrue(value["source"].startswith("https://res.cdn.office.net/"))
        self.assertEqual(hashlib.sha256((ROOT / "cards" / "assets" / "sharepoint-48.png").read_bytes()).hexdigest(), value["sha256"])
        self.assertIn("Fabric Assets License", (ROOT / "cards" / "NOTICE.md").read_text())
        self.assertIn("MIT License", (ROOT / "cards" / "schema" / "LICENSE").read_text())

    def test_banner_generator_is_reproducible(self):
        spec = importlib.util.spec_from_file_location("image_generator", ROOT / "scripts" / "build-rich-card-assets.py")
        generator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(generator)
        for scope in BANNER.SCOPES:
            stream = io.BytesIO()
            generator.banner(scope).save(stream, format="PNG", compress_level=9, optimize=False)
            self.assertEqual(stream.getvalue(), (ROOT / "cards" / "assets" / f"{scope}.png").read_bytes())

    def test_scope_mapping_is_fixed_and_unknown_scopes_fail_closed(self):
        for scope in ("Unknown", "hr", "", "https://example.invalid", "All,HR"):
            with self.assertRaisesRegex(ValueError, "Unapproved"):
                BANNER.card(scope)
        formula = BANNER.banner_node()["activity"]["attachments"][0]["cardContent"]
        self.assertIn("Switch(Topic.Department", formula)
        self.assertNotIn("Topic.SearchResult", formula)
        self.assertNotIn("ParseJSON", formula)

    def test_topic_banner_immediately_precedes_the_guarded_unchanged_result(self):
        topic = yaml.safe_load((ROOT / "topics" / "SearchSharePoint.mcs.yml").read_text(encoding="utf-8"))
        actions = topic["beginDialog"]["actions"]
        ids = [node["id"] for node in actions]
        index = ids.index(BANNER.NODE_ID)
        self.assertEqual(ids[index - 1], "checkSearchResult")
        self.assertEqual(ids[index + 1], "reportCount")
        self.assertGreater(index, ids.index("searchCount"))
        self.assertLess(ids.index("checkDepartment"), index)
        self.assertEqual(actions[index], BANNER.banner_node())
        self.assertFalse(actions[index]["disabled"])

    def test_flow_contract_and_verbatim_four_column_result_are_unchanged(self):
        definition = FLOW.build_definition(FLOW.load_policy(), (FLOW.TARGET / "RuntimeSearchResults.template.xlsx").read_bytes())
        response = definition["actions"]["Respond_to_agent"]
        self.assertEqual(response["inputs"]["body"], {"result": "@outputs('Format_chat_result')"})
        self.assertEqual(set(response["inputs"]["schema"]["properties"]), {"result"})
        self.assertEqual(response["runAfter"], {"Format_chat_result": ["Succeeded"]})
        topic = yaml.safe_load((ROOT / "topics" / "SearchSharePoint.mcs.yml").read_text(encoding="utf-8"))
        nodes = {node["id"]: node for node in topic["beginDialog"]["actions"]}
        self.assertEqual(nodes["searchCount"]["output"]["binding"], {"result": "Topic.SearchResult"})
        self.assertEqual(nodes["reportCount"]["activity"], "{Topic.SearchResult}")
        self.assertIn("| File or page | Created (UTC) | Modified (UTC) | Stored tags |",
                      definition["actions"]["Format_chat_result"]["inputs"])

    def test_generated_example_matches_the_real_template_without_result_data(self):
        expected = json.loads((ROOT / "cards" / "examples" / "HR.card.json").read_text())
        self.assertEqual(expected, BANNER.card("HR"))
        self.assertNotIn("sharepoint.com", json.dumps(expected))


if __name__ == "__main__":
    unittest.main()
