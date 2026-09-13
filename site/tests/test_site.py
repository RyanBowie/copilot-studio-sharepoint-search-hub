import hashlib
import copy
import html
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re
import shutil
import textwrap
import unittest
from urllib.parse import unquote, urljoin, urlsplit
import uuid
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("build_site", ROOT / "scripts" / "build_site.py")
BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.elements = []
        self.ids = []
        self.text = []
        self.feed(text)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        self.elements.append((tag, attrs))
        if "id" in attrs:
            self.ids.append(attrs["id"])

    def handle_data(self, data):
        self.text.append(data)


class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output = ROOT / ".site-test-build" / ("run-" + uuid.uuid4().hex)
        BUILD.build(cls.output, write_docs=False)
        cls.html = (cls.output / "index.html").read_text(encoding="utf-8")
        cls.document = Document(cls.html)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.output)

    def test_tracked_html_is_reproducible_and_contains_no_unresolved_tokens(self):
        self.assertEqual((ROOT / "docs" / "index.html").read_text(encoding="utf-8"), BUILD.render(False))
        self.assertEqual(self.html, BUILD.render(True))
        self.assertNotIn("@@", self.html)

    def test_staging_is_exactly_the_explicit_allowlist(self):
        expected = {v[1] for v in BUILD.ASSETS.values()} | {"index.html", ".nojekyll", BUILD.MARKER}
        actual = {p.relative_to(self.output).as_posix() for p in self.output.rglob("*") if p.is_file()}
        self.assertEqual(actual, expected)
        self.assertFalse(any(part in {".git", ".mcs", "node_modules", ".site-browser-profile"}
                             for name in actual for part in Path(name).parts))
        for source, destination in BUILD.ASSETS.values():
            self.assertEqual((ROOT / source).read_bytes(), (self.output / destination).read_bytes())

    def test_every_local_link_and_image_resolves_under_a_project_prefix(self):
        base = "https://example.invalid/copilot-studio-sharepoint-search-hub/"
        ids = set(self.document.ids)
        for tag, attributes in self.document.elements:
            for attr in ("href", "src"):
                value = attributes.get(attr)
                if not value or value.startswith(("https://", "data:")):
                    continue
                resolved = urlsplit(urljoin(base, value))
                self.assertTrue(resolved.path.startswith("/copilot-studio-sharepoint-search-hub/"), value)
                if value.startswith("#"):
                    self.assertIn(resolved.fragment, ids)
                else:
                    relative = unquote(resolved.path.removeprefix("/copilot-studio-sharepoint-search-hub/"))
                    self.assertTrue((self.output / relative).is_file(), (tag, attr, value))

    def test_tracked_docs_links_also_resolve_locally(self):
        for _, attributes in Document(BUILD.render(False)).elements:
            for key in ("href", "src"):
                value = attributes.get(key, "")
                if not value or value.startswith(("#", "https://", "data:")):
                    continue
                self.assertTrue((ROOT / "docs" / unquote(urlsplit(value).path)).is_file(), value)

    def test_downloaded_solution_is_exact_and_visible_checksum_matches(self):
        solution = self.output / BUILD.ASSETS["solution"][1]
        self.assertEqual(solution.stat().st_size, 64159)
        self.assertEqual(hashlib.sha256(solution.read_bytes()).hexdigest(), BUILD.SOLUTION_SHA256)
        self.assertIn(BUILD.SOLUTION_SHA256, self.html)
        self.assertIn("64,159 bytes", self.html)
        self.assertEqual(len(json.loads((self.output / BUILD.ASSETS["settings"][1]).read_text())["ConnectionReferences"]), 5)

    def test_evidence_numbers_and_capture_boundaries_are_explicit(self):
        text = " ".join(self.document.text)
        for required in ("512 / 512", "499 documents", "13 pages", "ten collections", "26m46s",
                         "1,024", "250 + 250 + 12", "100 + 100 + 100 + 100 + 100 + 12",
                         "Pending at capture", "Historical 112-row workbook—not 512",
                         "first four", "new-tenant import UNVERIFIED", "inbox receipt",
                         "not a completed cross-user denial audit", "not relevance rank"):
            self.assertIn(required, text)
        self.assertIn("no new 512-row workbook UI capture", text)
        self.assertIn("no environment-variable values that automatically retarget", text)

    def test_coverage_breakdown_matches_all_ten_sites_and_rendered_tables(self):
        proof, _ = BUILD.load_evidence()
        coverage = BUILD.load_coverage(proof)
        self.assertEqual(
            [(row["label"], row["sites"], row["files"], row["pages"], row["total"])
             for row in coverage["departments"]],
            [("CorpNet", 1, 49, 1, 50), ("HR", 3, 150, 4, 154),
             ("Finance", 3, 150, 4, 154), ("IT", 3, 150, 4, 154)])
        self.assertEqual(len(coverage["sites"]), 10)
        for row in coverage["sites"]:
            expected = ((49, 1, 50) if row["label"] == "CorpNet hub" or row["label"].endswith("Main")
                        else (53, 2, 55) if row["label"].endswith("Operations") else (48, 1, 49))
            self.assertEqual((row["files"], row["pages"], row["total"]), expected)
        for table_id, rows, include_sites in (
                ("department-coverage", coverage["departments"], True),
                ("site-coverage", coverage["sites"], False)):
            table = re.search(rf'<table[^>]*id="{table_id}".*?</table>', self.html, re.S).group()
            self.assertIn(BUILD.coverage_rows(rows, include_sites), table)
            self.assertEqual(table.count('scope="row"'), len(rows) + 1)
        text = " ".join(self.document.text)
        for boundary in ("not a live tenant-wide inventory", "200 in library roots",
                         "200 in nested", "non-marker examples", "four fictional site references"):
            self.assertIn(boundary, text)
        self.assertIn('href="#coverage"', self.html)

    def test_coverage_rejects_changed_counts_unknown_types_and_duplicate_records(self):
        proof, _ = BUILD.load_evidence()
        source = json.loads((ROOT / BUILD.ASSETS["source-proof"][0]).read_text())
        blueprint = json.loads((ROOT / BUILD.ASSETS["blueprint"][0]).read_text())
        for mutation in ("site-count", "type", "duplicate", "folder-count", "body-proof"):
            with self.subTest(mutation=mutation):
                changed_source, changed_blueprint = copy.deepcopy(source), copy.deepcopy(blueprint)
                if mutation == "site-count":
                    changed_source["matchesBySiteKey"]["hr-main"] += 1
                elif mutation == "type":
                    changed_blueprint["artifacts"][0]["kind"] = "Unreviewed"
                elif mutation == "duplicate":
                    changed_blueprint["artifacts"][1] = copy.deepcopy(changed_blueprint["artifacts"][0])
                elif mutation == "folder-count":
                    changed_source["newRootDocuments"] -= 1
                else:
                    changed_source["indexReadiness"]["results"]["Body"]["ready"] = False
                with patch.object(BUILD.json, "loads", side_effect=[changed_source, changed_blueprint]):
                    with self.assertRaises(ValueError):
                        BUILD.load_coverage(proof)

    def test_accessible_structure_controls_and_progressive_enhancement(self):
        self.assertEqual(len(self.document.ids), len(set(self.document.ids)))
        self.assertEqual(len([tag for tag, _ in self.document.elements if tag == "h1"]), 1)
        tabs = [attrs for _, attrs in self.document.elements if attrs.get("role") == "tab"]
        self.assertEqual(len(tabs), 10)
        for attributes in tabs:
            self.assertIn(attributes["aria-controls"], self.document.ids)
        panels = [attrs for _, attrs in self.document.elements if attrs.get("role") == "tabpanel"]
        self.assertEqual(len(panels), 10)
        self.assertTrue(all("hidden" not in attrs for attrs in panels))
        for tag, attributes in self.document.elements:
            if tag == "img":
                self.assertTrue(attributes.get("alt"))
                self.assertGreater(int(attributes["width"]), 0)
                self.assertGreater(int(attributes["height"]), 0)
        for key in ("ArrowRight", "ArrowLeft", "ArrowDown", "ArrowUp", "Home", "End"):
            self.assertIn(f'"{key}"', self.html)
        self.assertIn('href="#main">Skip to content', self.html)

    def test_full_instructions_and_binding_are_derived_from_actual_source(self):
        source = (ROOT / "agent" / "agent.mcs.yml").read_text(encoding="utf-8")
        expected = textwrap.dedent(source.split("instructions: |-\n", 1)[1]
                                   .split("\ngptCapabilities:", 1)[0]).rstrip("\n")
        displayed = re.search(r'<pre[^>]*id="instruction-source"[^>]*><code>(.*?)</code></pre>',
                              self.html, re.S).group(1)
        self.assertEqual(html.unescape(displayed), expected)
        self.assertNotIn(hashlib.sha256(expected.encode()).hexdigest(), self.html)
        self.assertNotIn("SHA-256 of the displayed UTF-8 instruction text", self.html)
        details = BUILD.load_agent_details()
        self.assertEqual(details["instructions"], expected)
        for key in ("binding", "settings", "tool"):
            self.assertIn(html.escape(details[key], quote=True), self.html)
        self.assertIn("source text, not a screenshot of the instruction editor", self.html)

    def test_instruction_text_cannot_become_active_html(self):
        details = BUILD.load_agent_details()
        details["instructions"] = '<script>alert("untrusted")</script> & <img src=x>'
        with patch.object(BUILD, "load_agent_details", return_value=details):
            rendered = BUILD.render(True)
        self.assertIn(html.escape(details["instructions"], quote=True), rendered)
        self.assertNotIn(details["instructions"], rendered)

    def test_all_reviewed_site_pngs_are_embedded_with_visible_flow_walkthrough(self):
        images = {attrs["src"] for tag, attrs in self.document.elements if tag == "img"}
        expected = {destination for _, destination in BUILD.ASSETS.values() if destination.endswith(".png")}
        self.assertEqual(images, expected)
        self.assertEqual(len(images), 21)
        flow = self.html.split('id="agent-flow"', 1)[1].split('id="evidence"', 1)[0]
        self.assertNotIn("<details", flow)
        self.assertTrue(all("hidden" not in attrs for _, attrs in Document(flow).elements))
        self.assertEqual(len(re.findall(r"<img ", flow)), 9)
        for stage in ("start", "search", "hydration", "preview", "paging", "workbook", "privacy", "delivery"):
            self.assertIn(f'id="flow-{stage}"', flow)
        self.assertIn("predate the document-ID-only sort revision", flow)
        for key in ("agent-source", "agent-settings", "topic-source", "fallback-source", "tool-source"):
            self.assertIn('href="' + BUILD.ASSETS[key][1] + '"', self.html)

    def test_tools_explanation_distinguishes_agent_binding_from_connector_actions(self):
        catalogue = re.search(r'<table[^>]*id="connector-catalogue".*?</table>', self.html, re.S).group()
        self.assertEqual(catalogue.count('scope="row"'), 5)
        for operation in ("HttpRequest", "MyProfile_V2", "UserProfile_V2", "GetFileMetadataByPath",
                          "CreateFile", "PatchItem", "AddRowV2", "DeleteItem", "GetItems", "SendEmailV2"):
            self.assertIn(f"<code>{operation}</code>", catalogue)
        text = " ".join(self.document.text)
        for required in ("not five separate model-selected agent tools", "same capability",
                         "not independently", "no separate queue", "not a permission boundary",
                         "not agent tools", "not independently verified inbox receipt"):
            self.assertIn(required, text)

    def test_changed_connector_operation_fails_the_walkthrough_build(self):
        definition = json.loads((ROOT / BUILD.ASSETS["definition"][0]).read_text())
        def change_operations(value):
            if isinstance(value, dict):
                if "operationId" in value:
                    value["operationId"] = "UnreviewedOperation"
                for child in value.values():
                    change_operations(child)
            elif isinstance(value, list):
                for child in value:
                    change_operations(child)
        change_operations(definition)
        with patch.object(BUILD.json, "loads", return_value=definition):
            with self.assertRaisesRegex(ValueError, "five-connector operation catalogue"):
                BUILD.load_agent_details()

    def test_showcase_is_first_and_top_actions_match_the_companion_pattern(self):
        first = next(attrs for tag, attrs in self.document.elements if tag == "section")
        self.assertEqual(first["id"], "showcase")
        showcase = self.html.split('id="showcase"', 1)[1].split("</section>", 1)[0]
        images = [attrs for tag, attrs in Document(showcase).elements if tag == "img"]
        self.assertEqual([image["src"] for image in images],
                         [BUILD.ASSETS["it-inputs"][1], BUILD.ASSETS["it"][1]])
        primary = re.search(r'id="primary-actions">(.*?)</div>', showcase, re.S).group(1)
        links = [attrs for tag, attrs in Document(primary).elements if tag == "a"]
        self.assertEqual([a["href"] for a in links], [BUILD.ASSETS["solution"][1], "#setup", BUILD.REPOSITORY])
        self.assertIn("download", links[0])
        self.assertEqual(Document(primary).text, ["Download solution ZIP", "Import and configure", "View repository"])
        self.assertIn("new-tenant import is unverified", showcase)
        self.assertIn("typed before submission", showcase)
        self.assertIn("Copilot Studio agent · Microsoft 365 Copilot channel", showcase)
        self.assertIn("not Agent Builder", showcase)
        self.assertNotIn("built-in Microsoft 365 Copilot assistant", self.html)
        self.assertNotIn("Actual published M365 Copilot", self.html)

    def test_all_sharepoint_requests_and_helpers_match_the_actual_definition(self):
        reference = BUILD.load_sharepoint_reference()
        self.assertEqual(len(reference["entries"]), 12)
        methods = [entry["action"]["inputs"]["parameters"]["parameters/method"] for entry in reference["entries"]]
        self.assertEqual(methods.count("GET"), 9)
        self.assertEqual(methods.count("POST"), 3)
        definition = json.loads((ROOT / BUILD.ASSETS["definition"][0]).read_text())
        for entry in reference["entries"]:
            value = definition
            for part in entry["path"].strip("/").split("/"):
                value = value[part.replace("~1", "/").replace("~0", "~")]
            self.assertEqual(value, entry["action"])
            body = re.search(rf'id="sp-config-{entry["name"]}"[^>]*><code>(.*?)</code></pre>',
                             self.html, re.S).group(1)
            self.assertEqual(json.loads(html.unescape(body)), value["inputs"]["parameters"])
            self.assertIn(html.escape(json.dumps(value, indent=2)), self.html)
            for _, helper in entry["helpers"]:
                self.assertIn(html.escape(json.dumps(helper, indent=2)), self.html)
        self.assertIn(html.escape(reference["kql"]), self.html)
        self.assertEqual((ROOT / "docs" / "sharepoint-actions.md").read_text(encoding="utf-8"),
                         BUILD.sharepoint_reference_markdown(reference))

    def test_orchestration_inputs_and_banners_are_explained_as_test_choices(self):
        text = " ".join(self.document.text)
        for required in ("Classic orchestration for this topic-based test",
                         "Generative orchestration is an alternative",
                         "Change the orchestration setting",
                         "a generative variant has not been tested here",
                         "Both the department and search terms currently use free-text entry",
                         "multiple-choice question", "Optional output styling example",
                         "not required for search", "Keep, change or omit the banner"):
            self.assertIn(required, text)
        self.assertIn(BUILD.SOLUTION_SHA256, self.html)

    def test_sharepoint_reference_fails_if_an_action_has_no_description(self):
        definition = json.loads((ROOT / BUILD.ASSETS["definition"][0]).read_text())
        descriptions = json.loads((ROOT / "site" / "sharepoint-actions.json").read_text())
        example = BUILD.load_sharepoint_reference()["entries"][0]["action"]
        definition["actions"]["Undocumented_sharepoint_action"] = copy.deepcopy(example)
        with patch.object(BUILD.json, "loads", side_effect=[definition, descriptions]):
            with self.assertRaisesRegex(ValueError, "cover every actual action"):
                BUILD.load_sharepoint_reference()

    def test_sharepoint_reference_escapes_parameters_and_descriptions(self):
        reference = copy.deepcopy(BUILD.load_sharepoint_reference())
        untrusted = '<script>alert("request")</script>'
        reference["entries"][0]["purpose"] = untrusted
        reference["entries"][0]["action"]["inputs"]["parameters"]["dataset"] = untrusted
        rendered = BUILD.sharepoint_reference_html(reference)
        self.assertIn(html.escape(untrusted), rendered)
        self.assertNotIn(untrusted, rendered)

    def test_empty_tenant_setup_identifies_real_customization_and_missing_resources(self):
        setup = self.html.split('id="setup"', 1)[1].split('<section class="section" id="downloads"', 1)[0]
        table = re.search(r'<table[^>]*id="tenant-customization".*?</table>', setup, re.S).group()
        self.assertEqual(table.count('scope="row"'), 9)
        self.assertEqual(setup.count('<li class="card">'), 10)
        for key in ("tenantOrigin", "searchSiteUrl", "hubSiteCollectionId", "configurationMode",
                    "hubRegistrationVerified", "hubSearchVerified", "metadataFieldsVerified",
                    "searchLocatorFieldsVerified"):
            self.assertIn(key, setup)
        for boundary in ("does not create", "Already imported the untouched ZIP?",
                         "folderPath:", "Provided by run-only user", "not managed taxonomy",
                         "not provisioned by the solution", "Stock packaging tests intentionally reject",
                         "No pre-created shared export library"):
            self.assertIn(boundary, setup)
        self.assertIn(BUILD.ASSETS["search-policy"][1], setup)

    def test_theme_and_no_remote_runtime_dependencies(self):
        scripts = re.findall(r"<script>(.*?)</script>", self.html, flags=re.S)
        self.assertIn('const param = new URLSearchParams(window.location.search).get("scoutTheme");', scripts[0])
        self.assertIn('param || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");', scripts[0])
        self.assertIn('explicit === "light" || explicit === "dark"', scripts[1])
        self.assertIn('url.searchParams.set("scoutTheme", next)', self.html)
        self.assertIn('"Segoe UI", Aptos, Calibri, -apple-system, BlinkMacSystemFont, sans-serif', self.html)
        self.assertIn('Consolas, "Courier New", Courier, monospace', self.html)
        css = re.search(r"<style>(.*?)</style>", self.html, flags=re.S).group(1)
        components = css[css.index("* { box-sizing:"):]
        self.assertNotRegex(components, r"#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(")
        self.assertNotRegex(self.html, r"<script[^>]+src=|<iframe|<form|@import|localStorage|document\.cookie|fetch\(|XMLHttpRequest")
        self.assertIn("connect-src 'none'", self.html)
        self.assertIn("prefers-reduced-motion", self.html)

    def test_build_rejects_unsafe_output_and_unknown_staged_files(self):
        for destination in (ROOT, ROOT / "docs", ROOT / "solutions" / "other", ROOT.parent / "outside"):
            with self.assertRaises(ValueError):
                BUILD.checked_output(destination)
        unexpected = self.output / "not-public.txt"
        unexpected.write_text("do not delete or stage this")
        try:
            with self.assertRaises(ValueError):
                BUILD.checked_output(self.output)
            self.assertTrue(unexpected.exists())
        finally:
            unexpected.unlink()
        self.assertEqual(BUILD.checked_output(self.output), self.output)

    def test_main_text_and_links_have_normal_text_contrast_in_both_themes(self):
        def luminance(value):
            rgb = [int(value[i:i + 2], 16) / 255 for i in (1, 3, 5)]
            linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in rgb]
            return sum(v * weight for v, weight in zip(linear, (.2126, .7152, .0722)))

        styles = re.search(r"<style>(.*?)</style>", self.html, flags=re.S).group(1)
        blocks = re.findall(r'(?:^:root|html\[data-theme="dark"\]) \{(.*?)\}', styles, flags=re.S | re.M)[:2]
        self.assertEqual(len(blocks), 2)
        for block in blocks:
            colors = dict(re.findall(r"--cp-([\w-]+): (#[0-9a-f]{6});", block))
            for foreground in ("text", "text-soft", "accent"):
                for background in ("bg", "surface", "bg-elevated"):
                    high, low = sorted((luminance(colors[foreground]), luminance(colors[background])), reverse=True)
                    self.assertGreaterEqual((high + .05) / (low + .05), 4.5, (foreground, background))

    def test_changed_package_pin_fails_closed(self):
        with patch.object(BUILD, "SOLUTION_SHA256", "0" * 64):
            with self.assertRaisesRegex(ValueError, "Solution bytes changed"):
                BUILD.load_evidence()

    def test_rebuild_manifest_is_deterministic_and_has_correct_hashes(self):
        before = (self.output / BUILD.MARKER).read_bytes()
        BUILD.build(self.output, write_docs=False)
        self.assertEqual((self.output / BUILD.MARKER).read_bytes(), before)
        manifest = json.loads(before)
        for name, expected in manifest["sha256"].items():
            self.assertEqual(hashlib.sha256((self.output / name).read_bytes()).hexdigest(), expected)

    def test_workflow_is_manual_owner_gated_and_uses_pinned_official_actions(self):
        workflow = (ROOT / ".github" / "workflows" / "pages.yml").read_text()
        self.assertIn("workflow_dispatch:", workflow)
        self.assertNotRegex(workflow, r"(?m)^\s+(push|pull_request):")
        self.assertIn("enablement: false", workflow)
        for required in ("contents: read", "pages: write", "id-token: write", "github-pages",
                         "python -B scripts/build_site.py", "unittest discover -s site/tests", "path: _site"):
            self.assertIn(required, workflow)
        uses = re.findall(r"uses: ([^\s]+)", workflow)
        self.assertEqual(len(uses), 5)
        self.assertTrue(all(re.fullmatch(r"actions/[\w-]+@[0-9a-f]{40}", value) for value in uses))


if __name__ == "__main__":
    unittest.main()
