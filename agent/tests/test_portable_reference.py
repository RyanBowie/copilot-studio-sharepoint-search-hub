import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import yaml
from openpyxl import load_workbook


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from search_contract import load_policy, validate_policy

SPEC = importlib.util.spec_from_file_location("portable_flow", ROOT / "scripts" / "build-search-export-flow.py")
FLOW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FLOW)


class PortableReferenceTests(unittest.TestCase):
    def setUp(self):
        self.policy = load_policy()

    def test_reference_is_explicitly_fictional_not_verified(self):
        self.assertEqual(self.policy["configurationMode"], "fictional-reference")
        self.assertEqual(self.policy["tenantOrigin"], "https://contoso.sharepoint.com")
        self.assertEqual(len(self.policy["sites"]), 4)
        self.assertEqual({site["department"] for site in self.policy["sites"]}, {"CorpNet", "HR", "Finance", "IT"})
        for key in ("hubRegistrationVerified", "hubSearchVerified", "metadataFieldsVerified", "searchLocatorFieldsVerified"):
            self.assertIs(self.policy[key], False)

    def test_empty_scope_unknown_department_and_outside_tenant_fail_closed(self):
        cases = [
            ("sites", []),
            ("scopeMode", "verified-hub-all"),
            ("searchSiteUrl", "https://elsewhere.sharepoint.com/sites/CorpNet"),
            ("tenantOrigin", "https://contoso.sharepoint.com@evil.example"),
            ("tenantOrigin", "http://contoso.sharepoint.com"),
        ]
        for key, value in cases:
            with self.subTest(key=key, value=value):
                policy = copy.deepcopy(self.policy)
                policy[key] = value
                with self.assertRaises(ValueError):
                    FLOW.compile_scopes(policy)
        for key, value in (("url", "https://elsewhere.sharepoint.com/sites/HR"), ("department", "Unknown"),
                           ("url", "https://contoso.sharepoint.com/sites/HR?extra=1")):
            policy = copy.deepcopy(self.policy)
            policy["sites"][1][key] = value
            with self.assertRaises(ValueError):
                FLOW.compile_scopes(policy)

    def test_safety_limits_and_resource_ids_are_validated(self):
        policy = copy.deepcopy(self.policy)
        policy["limits"]["maxBatches"] = 999
        with self.assertRaises(ValueError):
            validate_policy(policy)
        policy = copy.deepcopy(self.policy)
        policy["sites"][0]["siteId"] = "NOT_A_GUID"
        with self.assertRaises(ValueError):
            validate_policy(policy)

    def test_configured_mode_cannot_claim_unverified_or_fictional_resources(self):
        policy = copy.deepcopy(self.policy)
        policy["configurationMode"] = "configured"
        with self.assertRaisesRegex(ValueError, "independently verified"):
            validate_policy(policy)
        for key in ("hubRegistrationVerified", "hubSearchVerified", "metadataFieldsVerified", "searchLocatorFieldsVerified"):
            policy[key] = True
        with self.assertRaisesRegex(ValueError, "fictional"):
            validate_policy(policy)

    def test_no_embedded_connection_fallback_and_all_five_references_are_required(self):
        references = FLOW.connection_references()
        for bad in (
            {key: value for key, value in references.items() if key != "shared_office365"},
            {**references, "shared_office365": {**references["shared_office365"], "runtimeSource": "embedded"}},
            {**references, "shared_office365": {**references["shared_office365"], "api": {"name": "different"}}},
        ):
            with patch.object(FLOW.json, "loads", return_value=bad):
                with self.assertRaises(ValueError):
                    FLOW.connection_references()

    def test_yaml_and_flow_bindings_retain_invoker_only_tool(self):
        for source in ROOT.rglob("*.mcs.yml"):
            with self.subTest(source=source.name):
                self.assertIsInstance(yaml.safe_load(source.read_text(encoding="utf-8-sig")), dict)
        action = yaml.safe_load((ROOT / "actions" / "SearchAndExport.mcs.yml").read_text())
        topic = yaml.safe_load((ROOT / "topics" / "SearchSharePoint.mcs.yml").read_text())
        call = next(node for node in topic["beginDialog"]["actions"] if node["kind"] == "InvokeFlowAction")
        self.assertEqual(call["flowId"], action["action"]["flowId"])
        self.assertEqual(action["action"]["connectionProperties"]["mode"], "Invoker")
        self.assertIn("up to ten", action["modelDescription"])
        self.assertIn("Created/Modified UTC", action["modelDescription"])
        self.assertIn("up to ten", topic["beginDialog"]["actions"][0]["activity"])
        self.assertEqual(set(call["input"]["binding"]), {"query", "scope"})
        source = yaml.safe_load((ROOT / "connectionreferences.mcs.yml").read_text())
        expected = {ref["connection"]["connectionReferenceLogicalName"] for ref in FLOW.connection_references().values()}
        self.assertEqual({ref["connectionReferenceLogicalName"] for ref in source["connectionReferences"]}, expected)

    def test_current_scope_always_combines_explicit_inventory_and_hub(self):
        scopes = FLOW.compile_scopes(self.policy)
        self.assertEqual(set(scopes), {"All", "CorpNet", "HR", "Finance", "IT"})
        for batches in scopes.values():
            for batch in batches:
                self.assertIn("DepartmentId:" + self.policy["hubSiteCollectionId"], batch["Kql"])
                self.assertIn('SiteID:"', batch["Kql"])

    def test_base_workbook_is_blank_and_contains_no_external_links(self):
        path = ROOT / "exports" / "template" / "CorpNetSearchResults.template.xlsx"
        book = load_workbook(path)
        try:
            self.assertTrue(all(cell.value is None for cell in book["Results"][9]))
            self.assertTrue(book["ExportInfo"]["B6"].value.startswith("TEMPLATE"))
            self.assertFalse(book._external_links)
            for sheet in book:
                for row in sheet:
                    for cell in row:
                        self.assertNotIn(cell.data_type, {"f", "e"})
                        self.assertIsNone(cell.hyperlink)
        finally:
            book.close()

    def test_generated_reference_embeds_only_expected_runtime_template(self):
        import base64
        definition = json.loads((FLOW.TARGET / "definition.json").read_text())
        def walk(value):
            if isinstance(value, dict):
                for key, nested in value.items():
                    if key == "$content":
                        yield nested
                    yield from walk(nested)
            elif isinstance(value, list):
                for nested in value:
                    yield from walk(nested)
        embedded = list(walk(definition))
        self.assertEqual(len(embedded), 1)
        self.assertEqual(base64.b64decode(embedded[0]), (FLOW.TARGET / "RuntimeSearchResults.template.xlsx").read_bytes())


if __name__ == "__main__":
    unittest.main()
