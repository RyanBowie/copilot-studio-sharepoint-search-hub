import base64
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import unittest
import xml.etree.ElementTree as ET
import zipfile

import yaml


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src"
AGENT = ROOT.parent / "agent"
FLOW_ID = "96794fbd-20ae-f111-aaab-002248403bef"
sys.path.insert(0, str(ROOT / "tools"))
from sync_reference import compiled_component


def walk(value):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


class SolutionReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.flow_path, = (SOURCE / "Workflows").glob("*.json")
        cls.flow = json.loads(cls.flow_path.read_text(encoding="utf-8"))
        cls.definition = cls.flow["properties"]["definition"]
        cls.components = {
            p.parent.name: yaml.safe_load(p.read_text(encoding="utf-8"))
            for p in (SOURCE / "botcomponents").glob("*/data")
        }
        cls.customizations = ET.parse(SOURCE / "Other" / "Customizations.xml")

    def test_all_source_documents_parse(self):
        for path in SOURCE.rglob("*"):
            if path.suffix == ".xml":
                ET.parse(path)
            elif path.suffix == ".json":
                json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(len(self.components), 16)
        for data in self.components.values():
            self.assertNotIn("mcs.metadata", data)
            self.assertIn(data["kind"], ("AdaptiveDialog", "TaskDialog", "GptComponentMetadata"))

    def test_portable_components_match_after_explicit_identity_binding(self):
        for schema, component in self.components.items():
            self.assertEqual(component, compiled_component(schema), schema)
        self.assertEqual(
            self.components["cnh_corpnetSearchHub.gpt.default"]["aISettings"]["model"]["modelNameHint"],
            "GPT5Chat")

    def test_native_definition_is_exact_standing_portable_source(self):
        portable = json.loads((AGENT / "flows" / "search-export" / "definition.json").read_text(encoding="utf-8"))
        self.assertEqual(self.definition, portable)

    def test_every_flow_reference_resolves_to_the_single_packaged_flow(self):
        refs = [node["flowId"] for component in self.components.values()
                for node in walk(component) if isinstance(node, dict) and "flowId" in node]
        self.assertEqual(refs, [FLOW_ID, FLOW_ID])
        manifest = ET.parse(SOURCE / "Other" / "Solution.xml")
        roots = manifest.findall(".//RootComponent")
        self.assertEqual([(v.attrib["type"], v.attrib["id"].strip("{}").lower()) for v in roots],
                         [("29", FLOW_ID)])
        association = ET.parse(SOURCE / "Assets" / "botcomponent_workflowset.xml").getroot()[0]
        self.assertEqual(association.attrib["workflowid.workflowid"], FLOW_ID)
        self.assertIn(association.attrib["botcomponentid.schemaname"], self.components)
        self.assertEqual(len(list((SOURCE / "Workflows").glob("*.json"))), 1)

    def test_bot_parent_and_active_component_membership(self):
        for path in (SOURCE / "botcomponents").glob("*/botcomponent.xml"):
            component = ET.parse(path).getroot()
            self.assertIn(component.attrib["schemaname"], self.components)
            self.assertEqual(component.findtext("parentbotid/schemaname"), "cnh_corpnetSearchHub")
            self.assertEqual(component.findtext("statecode"), "0")
        self.assertEqual(len(list((SOURCE / "Assets").iterdir())), 1)
        self.assertFalse(any("Untitled" in name or "SendanHTTP" in name for name in self.components))

    def test_five_invoker_references_have_no_connected_account_ids(self):
        references = self.flow["properties"]["connectionReferences"]
        self.assertEqual(set(references), {
            "shared_sharepointonline", "shared_office365", "shared_office365users",
            "shared_onedriveforbusiness", "shared_excelonlinebusiness"})
        declared = {r.attrib["connectionreferencelogicalname"]
                    for r in self.customizations.findall(".//connectionreference")}
        used = set()
        for reference in references.values():
            self.assertEqual(reference["runtimeSource"], "invoker")
            self.assertEqual(set(reference["connection"]), {"connectionReferenceLogicalName"})
            used.add(reference["connection"]["connectionReferenceLogicalName"])
        self.assertEqual(used, declared)
        self.assertEqual(len(declared), 5)

    def test_deployment_settings_are_unbound_and_have_no_current_environment_values(self):
        settings = json.loads((ROOT / "deployment-settings.template.json").read_text(encoding="utf-8-sig"))
        self.assertEqual(settings["EnvironmentVariables"], [])
        self.assertEqual(len(settings["ConnectionReferences"]), 5)
        self.assertTrue(all(v["ConnectionId"] == "" for v in settings["ConnectionReferences"]))
        self.assertEqual(settings["CopilotAgents"], [{
            "AadGroupId": "00000000-0000-0000-0000-000000000000", "Name": "cnh_corpnetSearchHub"}])

    def test_import_does_not_publish_enable_channels_or_activate_the_flow(self):
        config = json.loads((SOURCE / "bots" / "cnh_corpnetSearchHub" / "configuration.json").read_text())
        self.assertIs(config["publishOnImport"], False)
        self.assertEqual(config["channels"], [])
        self.assertIs(config["settings"]["GenerativeActionsEnabled"], False)
        metadata = ET.parse(next((SOURCE / "Workflows").glob("*.data.xml")))
        self.assertEqual(metadata.findtext("StateCode"), "0")
        self.assertEqual(metadata.findtext("StatusCode"), "1")
        bot = ET.parse(SOURCE / "bots" / "cnh_corpnetSearchHub" / "bot.xml")
        self.assertEqual(bot.findtext("authenticationmode"), "2")
        self.assertEqual(bot.findtext("authenticationtrigger"), "1")
        self.assertIsNone(bot.find("iconbase64"))

    def test_only_reviewed_intrinsic_or_fictional_guids_occur(self):
        allowed = {FLOW_ID} | {f"00000000-0000-4000-8000-{i:012d}" for i in range(1, 5)}
        pattern = r"(?i)\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b"
        for path in SOURCE.rglob("*"):
            if path.is_file():
                matches = re.findall(pattern, str(path.relative_to(SOURCE)) + path.read_text(encoding="utf-8-sig"))
                self.assertLessEqual({v.lower() for v in matches}, allowed, str(path))

    def test_no_connected_tenant_locators_or_secret_url_shapes(self):
        for path in SOURCE.rglob("*"):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8-sig")
            self.assertNotRegex(text.lower(), r"mngenv|org[0-9a-f]+\.crm\d*\.dynamics\.com|corpnetsearchpoc-")
            self.assertNotRegex(text, r"(?i)[?&](sig|access_token|client_secret)=")
            self.assertNotRegex(text, r"(?i)https://[^/'\"\s]+\.onmicrosoft\.com")
            hosts = re.findall(r"https://([A-Za-z0-9.-]+)(?=/|['\"])", text)
            self.assertLessEqual(set(hosts), {
                "adaptivecards.io", "contoso.sharepoint.com", "contoso-my.sharepoint.com",
                "schema.management.azure.com", "www.w3.org"})

    def test_embedded_workbook_is_the_exact_blank_portable_template(self):
        binaries = [base64.b64decode(value["$content"]) for value in walk(self.definition)
                    if isinstance(value, dict) and "$content" in value]
        self.assertEqual(len(binaries), 1)
        expected = (AGENT / "flows" / "search-export" / "RuntimeSearchResults.template.xlsx").read_bytes()
        self.assertEqual(binaries[0], expected)
        with zipfile.ZipFile(io.BytesIO(binaries[0])) as workbook:
            self.assertIsNone(workbook.testzip())

    def test_actual_solution_zip_is_unmanaged_and_contains_the_current_source(self):
        with zipfile.ZipFile(ROOT / "CorpNetSearchHubReference_1_0_0_0_unmanaged.zip") as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(len(archive.namelist()), len(set(archive.namelist())))
            manifest = ET.fromstring(archive.read("solution.xml"))
            self.assertEqual(manifest.findtext(".//Managed"), "0")
            self.assertEqual(manifest.findtext(".//UniqueName"), "cnh_CorpNetSearchHubReference")
            self.assertEqual(len(manifest.findall(".//MissingDependencies/*")), 0)
            for path in SOURCE.rglob("*"):
                if not path.is_file() or path.suffix == ".xml":
                    continue
                entry = path.relative_to(SOURCE).as_posix()
                self.assertEqual(archive.read(entry), path.read_bytes(), entry)
            self.assertNotIn("Assets/botcomponent_connectionreferenceset.xml", archive.namelist())


if __name__ == "__main__":
    unittest.main()
