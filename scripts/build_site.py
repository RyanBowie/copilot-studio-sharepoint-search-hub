"""Build tracked documentation HTML and a strictly allowlisted GitHub Pages site."""

import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import shutil
import struct


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "https://github.com/RyanBowie/copilot-studio-sharepoint-search-hub"
SOLUTION_SHA256 = "525136e9e96afaf5a90594cc14cf502555b16eb31680a9c64dc3b109ec925272"
SOLUTION_BYTES = 64159
TEMPLATE = ROOT / "site" / "index.template.html"
MARKER = ".site-build-manifest.json"

# Source paths are explicit: never discover publication material by walking the repository.
ASSETS = {
    "scale": ("docs/images/scale-512/owner-m365-preview-excerpt.png", "images/scale-512/owner-m365-preview-excerpt.png"),
    "scale-count": ("docs/images/scale-512/owner-m365-index-estimate.png", "images/scale-512/owner-m365-index-estimate.png"),
    "hr": ("docs/images/published-m365/published-m365-hr-full-output-67.png", "images/published-m365/published-m365-hr-full-output-67.png"),
    "hr-detail": ("docs/images/published-m365/published-m365-hr-table-100.png", "images/published-m365/published-m365-hr-table-100.png"),
    "it": ("docs/images/table-polish/published-m365-polished-table-100.png", "images/table-polish/published-m365-polished-table-100.png"),
    "it-inputs": ("docs/images/table-polish/published-m365-it-devices-inputs.png", "images/table-polish/published-m365-it-devices-inputs.png"),
    "excel": ("docs/images/live-workbook-compact.png", "images/live-workbook-compact.png"),
    "wiring": ("docs/images/styled-hr/topic-native-flow-binding.png", "images/styled-hr/topic-native-flow-binding.png"),
    "architecture": ("docs/images/architecture.svg", "images/architecture.svg"),
    "editable": ("docs/images/architecture.excalidraw", "images/architecture.excalidraw"),
    "solution": ("solutions/CorpNetSearchHubReference_1_0_0_0_unmanaged.zip", "downloads/CorpNetSearchHubReference_1_0_0_0_unmanaged.zip"),
    "definition": ("agent/flows/search-export/definition.json", "downloads/search-export.definition.json"),
    "blueprint": ("fixtures/corpnet-demo/scale-expected-results.example.json", "downloads/scale-expected-results.example.json"),
    "workbook": ("agent/flows/search-export/RuntimeSearchResults.template.xlsx", "downloads/RuntimeSearchResults.template.xlsx"),
    "settings": ("solutions/deployment-settings.template.json", "downloads/deployment-settings.template.json"),
    "scale-proof": ("docs/scale-runtime-validation-summary.json", "evidence/scale-runtime-validation-summary.json"),
    "source-proof": ("docs/scale-source-validation-summary.json", "evidence/scale-source-validation-summary.json"),
    "scale-provenance": ("docs/scale-512-capture-provenance.json", "evidence/scale-512-capture-provenance.json"),
    "hr-proof": ("docs/m365-validation-summary.json", "evidence/m365-validation-summary.json"),
    "it-proof": ("docs/table-polish-validation-summary.json", "evidence/table-polish-validation-summary.json"),
    "workbook-proof": ("docs/workbook-validation-summary.json", "evidence/workbook-validation-summary.json"),
    "package-proof": ("solutions/validation.json", "evidence/solution-validation.json"),
    "notice": ("NOTICE.md", "NOTICE.md"),
    "asset-notice": ("solutions/ASSET-NOTICE.md", "ASSET-NOTICE.md"),
    "agent-source": ("agent/agent.mcs.yml", "downloads/agent.mcs.yml"),
    "agent-settings": ("agent/settings.mcs.yml", "downloads/settings.mcs.yml"),
    "topic-source": ("agent/topics/SearchSharePoint.mcs.yml", "downloads/SearchSharePoint.mcs.yml"),
    "fallback-source": ("agent/topics/Search.mcs.yml", "downloads/Search.mcs.yml"),
    "tool-source": ("agent/actions/SearchAndExport.mcs.yml", "downloads/SearchAndExport.mcs.yml"),
    "studio-entry": ("docs/images/styled-hr/entrypoint-and-trigger.png", "images/styled-hr/entrypoint-and-trigger.png"),
    "studio-inputs": ("docs/images/styled-hr/area-and-query-inputs.png", "images/styled-hr/area-and-query-inputs.png"),
    "studio-output": ("docs/images/styled-hr/styled-result-rows-and-footer.png", "images/styled-hr/styled-result-rows-and-footer.png"),
    "topic-banner": ("docs/images/department-banners/topic-message-order.png", "images/department-banners/topic-message-order.png"),
    "flow-overview": ("docs/images/styled-hr/native-flow-overview.png", "images/styled-hr/native-flow-overview.png"),
    "flow-entry": ("docs/images/styled-hr/native-flow-entry.png", "images/styled-hr/native-flow-entry.png"),
    "flow-search": ("docs/images/styled-hr/native-initial-search.png", "images/styled-hr/native-initial-search.png"),
    "flow-paging": ("docs/images/styled-hr/native-paging-request.png", "images/styled-hr/native-paging-request.png"),
    "flow-source": ("docs/images/styled-hr/native-source-metadata-read.png", "images/styled-hr/native-source-metadata-read.png"),
    "flow-response": ("docs/images/styled-hr/native-response-and-continuation.png", "images/styled-hr/native-response-and-continuation.png"),
    "flow-excel": ("docs/images/styled-hr/native-excel-append.png", "images/styled-hr/native-excel-append.png"),
    "flow-access": ("docs/images/styled-hr/native-delivery-guard.png", "images/styled-hr/native-delivery-guard.png"),
    "flow-email": ("docs/images/styled-hr/native-verified-recipient-email.png", "images/styled-hr/native-verified-recipient-email.png"),
    "flow-provenance": ("docs/styled-capture-provenance.json", "evidence/styled-capture-provenance.json"),
    "search-policy": ("agent/runtime/search-policy.json", "downloads/search-policy.json"),
}


def source_path(relative):
    path = ROOT / relative
    resolved = path.resolve(strict=True)
    if (not resolved.is_relative_to(ROOT.resolve())
            or any(part.is_symlink() for part in (path, *path.parents) if part.is_relative_to(ROOT))):
        raise ValueError(f"Publication source escaped the repository: {relative}")
    return path


def load_evidence():
    proof = json.loads(source_path(ASSETS["scale-proof"][0]).read_text(encoding="utf-8"))
    expected = {
        "result": "PASS", "uniqueCallerHydratedRows": 512, "actualExcelRows": 512,
        "files": 499, "pages": 13, "collections": 10, "previewRows": 10, "columns": 4,
        "sourceTimestampAndCalendarComparisons": 1024, "omittedRows": 0, "duplicateIndexHits": 0,
        "finalChecksPassed": 25, "finalChecksTotal": 25, "pagingChecksPassed": 23, "pagingChecksTotal": 23,
        "dateMarkupChecksPassed": 15, "dateMarkupChecksTotal": 15, "completionStatus": "Complete",
        "processingErrors": False, "truncatedUpstream": False, "nativeSort": "[docid] ascending only",
    }
    for name, value in expected.items():
        if proof.get(name) != value:
            raise ValueError(f"Review website copy against changed runtime evidence: {name}")
    if proof["nativeSourcePageCounts"] != [100, 100, 100, 100, 100, 12]:
        raise ValueError("Unexpected native source paging evidence.")
    if proof["excelReadbackCounts"] != [250, 250, 12]:
        raise ValueError("Unexpected actual workbook readback evidence.")
    if round(proof["durations"]["totalSeconds"]) != 1606:
        raise ValueError("Review the observed-duration caption against changed evidence.")
    if proof["inputs"] != {"entrypoint": "Search SharePoint", "area": "All", "query": "hubspokeverify"}:
        raise ValueError("The gallery scenario and runtime evidence disagree.")
    if proof["caps"] != {"exportRows": 1000, "candidates": 2000, "sourcePages": 40,
                         "siteBatches": 12, "sitesPerBatch": 20, "exportLoopMinutes": 45,
                         "excelReadbackMinutes": 5}:
        raise ValueError("Review the documented finite bounds.")
    package = source_path(ASSETS["solution"][0]).read_bytes()
    if len(package) != SOLUTION_BYTES or hashlib.sha256(package).hexdigest() != SOLUTION_SHA256:
        raise ValueError("Solution bytes changed; review and deliberately update the website download pin.")
    package_proof = json.loads(source_path(ASSETS["package-proof"][0]).read_text(encoding="utf-8"))
    if package_proof["artifactSha256"] != SOLUTION_SHA256:
        raise ValueError("Package validation snapshot does not identify the downloadable ZIP.")
    definition = json.loads(source_path(ASSETS["definition"][0]).read_text(encoding="utf-8"))
    canonical = hashlib.sha256(json.dumps(definition, sort_keys=True).encode()).hexdigest()
    if canonical != package_proof["portableDefinitionCanonicalSha256"]:
        raise ValueError("Portable flow and package snapshot disagree.")
    if proof["definitionRevisionSha256"] != package_proof["sourceComponentGuard"]["afterDefinitionSha256"]:
        raise ValueError("Native runtime evidence and the package source revision disagree.")
    return proof, package_proof


def render(staged):
    proof, package_proof = load_evidence()
    coverage = load_coverage(proof)
    agent = load_agent_details()
    sharepoint = load_sharepoint_reference()
    facts = {
        "ROWS": str(proof["actualExcelRows"]),
        "FILES": str(proof["files"]),
        "PAGES": str(proof["pages"]),
        "SITES": str(proof["collections"]),
        "DATES": f'{proof["sourceTimestampAndCalendarComparisons"]:,}',
        "SOLUTION_SHA": SOLUTION_SHA256,
        "SOLUTION_BYTES": f"{SOLUTION_BYTES:,}",
        "NATIVE_SHA": proof["definitionRevisionSha256"],
        "PORTABLE_SHA": package_proof["portableDefinitionCanonicalSha256"],
        "REPO": REPOSITORY,
        "NEW_DOCUMENTS": str(coverage["source"]["newDocuments"]),
        "ROOT_DOCUMENTS": str(coverage["source"]["newRootDocuments"]),
        "NESTED_DOCUMENTS": str(coverage["source"]["newNestedDocuments"]),
        "AGENT_INSTRUCTIONS": agent["instructions"],
        "INSTRUCTIONS_SHA": hashlib.sha256(agent["instructions"].encode()).hexdigest(),
        "AGENT_SETTINGS": agent["settings"],
        "TOPIC_BINDING": agent["binding"],
        "TOOL_SOURCE": agent["tool"],
        "SP_ACTION_COUNT": str(len(sharepoint["entries"])),
        "SP_SCOPE_KQL": sharepoint["kql"],
    }
    coverage_html = {
        "COVERAGE_DEPARTMENTS": coverage_rows(coverage["departments"], include_sites=True),
        "COVERAGE_SITES": coverage_rows(coverage["sites"]),
        "SHAREPOINT_ACTIONS": sharepoint_reference_html(sharepoint),
    }

    def substitute(match):
        token = match.group(1)
        if token in coverage_html:
            return coverage_html[token]
        if token.startswith("ASSET:"):
            source, destination = ASSETS[token.split(":", 1)[1]]
            value = destination if staged else (
                source.removeprefix("docs/") if source.startswith("docs/") else "../" + source)
        elif token.startswith(("WIDTH:", "HEIGHT:")):
            kind, key = token.split(":", 1)
            raw = source_path(ASSETS[key][0]).read_bytes()
            if raw[:8] != b"\x89PNG\r\n\x1a\n":
                raise ValueError("An image dimension token must refer to a PNG.")
            width, height = struct.unpack(">II", raw[16:24])
            value = str(width if kind == "WIDTH" else height)
        else:
            value = facts[token]
        return html.escape(value, quote=True)

    rendered = re.sub(r"@@([A-Z][A-Z0-9_:-]*|ASSET:[a-z-]+|WIDTH:[a-z-]+|HEIGHT:[a-z-]+)@@",
                      substitute, TEMPLATE.read_text(encoding="utf-8"))
    if "@@" in rendered:
        raise ValueError("Unresolved website template token.")
    return rendered


def load_agent_details():
    source = source_path(ASSETS["agent-source"][0]).read_text(encoding="utf-8")
    lines = source.splitlines()
    if lines.count("instructions: |-") != 1:
        raise ValueError("Review the instructions renderer against changed agent YAML.")
    block = []
    for line in lines[lines.index("instructions: |-") + 1:]:
        if line and not line.startswith("  "):
            break
        block.append(line[2:] if line else "")
    instructions = "\n".join(block).rstrip("\n")
    if not instructions or "modelNameHint: GPT5Chat" not in source:
        raise ValueError("Review the agent/model explanation against changed source.")
    topic = source_path(ASSETS["topic-source"][0]).read_text(encoding="utf-8")
    marker = "    - kind: InvokeFlowAction\n"
    if topic.count(marker) != 1:
        raise ValueError("The walkthrough requires the single explicit topic flow invocation.")
    binding = marker + topic.split(marker, 1)[1].split("\n    - kind:", 1)[0]
    settings = source_path(ASSETS["agent-settings"][0]).read_text(encoding="utf-8")
    for required in ("authenticationMode: Integrated", "authenticationTrigger: Always",
                     "GenerativeActionsEnabled: false", "useModelKnowledge: false"):
        if required not in settings:
            raise ValueError("Review the configuration explanation: " + required)
    tool = source_path(ASSETS["tool-source"][0]).read_text(encoding="utf-8")
    if "kind: InvokeFlowTaskAction" not in tool or "mode: Invoker" not in tool:
        raise ValueError("The native-flow tool explanation no longer matches its source.")
    definition = json.loads(source_path(ASSETS["definition"][0]).read_text(encoding="utf-8"))
    operations = {}

    def inspect(value):
        if isinstance(value, dict):
            inputs = value.get("inputs")
            host = inputs.get("host") if isinstance(inputs, dict) else None
            if isinstance(host, dict) and "operationId" in host:
                operations.setdefault(host["connectionName"], set()).add(host["operationId"])
            for child in value.values():
                inspect(child)
        elif isinstance(value, list):
            for child in value:
                inspect(child)

    inspect(definition)
    expected = {
        "shared_sharepointonline": {"HttpRequest"},
        "shared_office365users": {"MyProfile_V2", "UserProfile_V2"},
        "shared_onedriveforbusiness": {"GetFileMetadataByPath", "CreateFile"},
        "shared_excelonlinebusiness": {"PatchItem", "AddRowV2", "DeleteItem", "GetItems"},
        "shared_office365": {"SendEmailV2"},
    }
    if operations != expected:
        raise ValueError("Review the five-connector operation catalogue against the current flow.")
    return {"instructions": instructions, "settings": settings, "binding": binding, "tool": tool}


def load_sharepoint_reference():
    definition = json.loads(source_path(ASSETS["definition"][0]).read_text(encoding="utf-8"))
    descriptions = json.loads(source_path("site/sharepoint-actions.json").read_text(encoding="utf-8"))
    actions = {}

    def visit(value, path=""):
        if isinstance(value, dict):
            children = value.get("actions")
            if isinstance(children, dict):
                for name, action in children.items():
                    if name in actions:
                        raise ValueError("Ambiguous action name in SharePoint reference: " + name)
                    actions[name] = (path + "/actions/" + name, action)
            for key, child in value.items():
                visit(child, path + "/" + key.replace("~", "~0").replace("/", "~1"))
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, path + "/" + str(index))

    visit(definition)
    selected = {}
    for name, (path, action) in actions.items():
        inputs = action.get("inputs")
        host = inputs.get("host", {}) if isinstance(inputs, dict) else {}
        if host.get("connectionName") == "shared_sharepointonline":
            if host.get("operationId") != "HttpRequest":
                raise ValueError("Review the SharePoint action type: " + name)
            selected[name] = (path, action)
    names = [entry["name"] for entry in descriptions]
    if len(names) != len(set(names)) or set(names) != set(selected):
        raise ValueError("SharePoint descriptions must cover every actual action exactly once.")
    entries = []
    for entry in descriptions:
        path, action = selected[entry["name"]]
        helpers = []
        for name in entry["helpers"]:
            if name not in actions:
                raise ValueError("Unknown SharePoint reference helper: " + name)
            helper = actions[name][1]
            helpers.append((name, {k: v for k, v in helper.items()
                                   if k not in {"actions", "else", "cases", "default"}}))
        entries.append({**entry, "path": path, "action": action, "helpers": helpers})
    kql = actions["Approved_scopes"][1]["inputs"]["All"][0]["Kql"]
    return {"entries": entries, "kql": kql}


def sharepoint_reference_html(reference):
    escape = html.escape
    blocks = ['<nav class="guide-jumps" aria-label="SharePoint action index">']
    for entry in reference["entries"]:
        name = escape(entry["name"], quote=True)
        blocks.append(f'<a href="#sp-{name}">{name.replace("_", " ")}</a>')
    blocks.append("</nav>")
    for entry in reference["entries"]:
        name = escape(entry["name"], quote=True)
        action = entry["action"]
        parameters = action["inputs"]["parameters"]
        blocks.append(f'<article class="card flow-step sp-action" id="sp-{name}">'
                      f'<span class="tag">{escape(parameters["parameters/method"])} / SharePoint HTTP</span>'
                      f'<h3>{name}</h3>')
        for label, key in (("Purpose", "purpose"), ("Response and downstream use", "response"),
                           ("Behavior and boundaries", "notes")):
            blocks.append(f'<p><strong>{label}.</strong> {escape(entry[key])}</p>')
        blocks.append('<h4 class="flow-step">Exact request configuration</h4>'
                      '<p class="small">Source expressions, not an executed request or sample response. '
                      'Site Address is <code>dataset</code>; URI is relative to that site.</p>'
                      f'<pre class="guide-source" id="sp-config-{name}" tabindex="0" '
                      f'aria-label="{name} request parameters"><code>'
                      f'{escape(json.dumps(parameters, indent=2))}</code></pre>')
        blocks.append(f'<p class="small">Action retry policy: '
                      f'<code>{escape(json.dumps(action["inputs"].get("retryPolicy")))}</code>. '
                      f'Run-after dependencies: <code>{escape(json.dumps(action.get("runAfter", {})))}</code>. '
                      'An empty object does not mean unconditional execution: enclosing scopes, '
                      'conditions and loop budgets still apply.</p>')
        blocks.append(f'<details class="sp-definition"><summary>Full action JSON and source location</summary>'
                      f'<p>JSON pointer in the complete definition:</p><code class="checksum">{escape(entry["path"])}</code>'
                      f'<pre class="guide-source" tabindex="0" aria-label="{name} complete action">'
                      f'<code>{escape(json.dumps(action, indent=2))}</code></pre></details>')
        for helper_name, helper in entry["helpers"]:
            title = escape(helper_name)
            snippet = (f'<pre class="guide-source" tabindex="0" aria-label="{title} source excerpt">'
                       f'<code>{escape(json.dumps(helper, indent=2))}</code></pre>')
            if helper_name in {"Initial_request", "Next_request"}:
                blocks.append(f'<h4 class="flow-step">Body-building Compose: {title}</h4>{snippet}')
            else:
                blocks.append(f'<details><summary>{title}: exact supporting expression</summary>'
                              f'<p class="small">Control excerpt; nested branches omitted.</p>{snippet}</details>')
        blocks.append("</article>")
    return "\n".join(blocks)


def sharepoint_reference_markdown(reference):
    lines = ["# SharePoint action request reference", "",
             "Generated from the current portable flow by `scripts/build_site.py`.",
             "Descriptions are maintained in `site/sharepoint-actions.json`; request JSON is read directly from source.",
             "All 12 definitions use SharePoint **Send an HTTP request to SharePoint** (`HttpRequest`).",
             "Loops can call an action repeatedly; this is not a count of requests in one run.",
             "Contoso addresses and zero-pattern site IDs are placeholders, not live settings.", "",
             "[On-page request catalogue](https://ryanbowie.github.io/copilot-studio-sharepoint-search-hub/#sharepoint-actions) · "
             "[Complete definition](../agent/flows/search-export/definition.json) · "
             "[New-tenant setup](setup.md#from-an-empty-sharepoint-tenant)", "",
             "## Actual portable All-scope KQL", "", "```text", reference["kql"], "```", ""]
    for entry in reference["entries"]:
        lines.extend(["## " + entry["name"], "", entry["purpose"], "", "**Response use:** " + entry["response"],
                      "", "**Boundaries:** " + entry["notes"], "", "**Source JSON pointer:** `" + entry["path"] + "`",
                      "", "```json", json.dumps(entry["action"], indent=2), "```", ""])
        for name, helper in entry["helpers"]:
            lines.extend(["### " + name, "", "Supporting source excerpt; nested branches omitted.", "",
                          "```json", json.dumps(helper, indent=2), "```", ""])
    return "\n".join(lines)


def load_coverage(proof):
    source = json.loads(source_path(ASSETS["source-proof"][0]).read_text(encoding="utf-8"))
    blueprint = json.loads(source_path(ASSETS["blueprint"][0]).read_text(encoding="utf-8"))
    labels = {
        "corpnet-main": ("CorpNet", "CorpNet hub"),
        "hr-main": ("HR", "HR - Main"),
        "hr-operations": ("HR", "HR - Operations"),
        "hr-fieldteam": ("HR", "HR - Field Team"),
        "finance-main": ("Finance", "Finance - Main"),
        "finance-operations": ("Finance", "Finance - Operations"),
        "finance-fieldteam": ("Finance", "Finance - Field Team"),
        "it-main": ("IT", "IT - Main"),
        "it-operations": ("IT", "IT - Operations"),
        "it-fieldteam": ("IT", "IT - Field Team"),
    }
    if (blueprint.get("synthetic") is not True or blueprint.get("query") != "hubspokeverify"
            or blueprint.get("scope") != "All" or source.get("query") != blueprint["query"]
            or source.get("scope") != blueprint["scope"]):
        raise ValueError("Coverage requires the reviewed synthetic All-scope marker corpus.")
    sites = {key: {"label": label, "department": department, "files": 0, "pages": 0, "total": 0}
             for key, (department, label) in labels.items()}
    identities, urls = set(), set()
    for item in blueprint["artifacts"]:
        key, kind = item["siteKey"], item["kind"]
        if (key not in sites or kind not in {"DOCX", "Page"}
                or item["department"] != sites[key]["department"]
                or item["id"] in identities or item["url"] in urls):
            raise ValueError("Unreviewed, inconsistent or duplicate coverage record.")
        identities.add(item["id"])
        urls.add(item["url"])
        sites[key]["files" if kind == "DOCX" else "pages"] += 1
        sites[key]["total"] += 1
    departments = {key: {"label": key, "sites": 0, "files": 0, "pages": 0, "total": 0}
                   for key in ("CorpNet", "HR", "Finance", "IT")}
    for row in sites.values():
        department = departments[row["department"]]
        department["sites"] += 1
        for key in ("files", "pages", "total"):
            department[key] += row[key]
    totals = {key: sum(row[key] for row in sites.values()) for key in ("files", "pages", "total")}
    if (totals != {"files": proof["files"], "pages": proof["pages"], "total": proof["actualExcelRows"]}
            or len(sites) != proof["collections"]
            or source["matchingSources"] != totals["total"]
            or source["documents"] != totals["files"] or source["pages"] != totals["pages"]
            or source["siteCollections"] != len(sites)
            or blueprint["expectedCount"] != totals["total"]
            or blueprint["expectedFiles"] != totals["files"] or blueprint["expectedPages"] != totals["pages"]
            or source["matchesBySiteKey"] != {key: row["total"] for key, row in sites.items()}
            or source["matchesByDepartment"] != {key: row["total"] for key, row in departments.items()}):
        raise ValueError("Coverage breakdown disagrees with verified source/runtime evidence.")
    if (source["newDocuments"] != 400 or source["newRootDocuments"] != 200
            or source["newNestedDocuments"] != 200
            or source["newDocumentsPerSite"] != dict.fromkeys(sites, 40)):
        raise ValueError("Review the new-document folder coverage against changed evidence.")
    indexing = source["indexReadiness"]
    if (indexing["results"]["Body"]["uniqueURLs"] != 400
            or indexing["results"]["Body"]["ready"] is not True
            or indexing["bodyMarkerNotInNamesTitlesOrTags"] is not True
            or indexing["notAnAgentRuntimeTest"] is not True):
        raise ValueError("Review the separately scoped body-content indexing evidence.")
    return {"source": source, "sites": list(sites.values()), "departments": list(departments.values())}


def coverage_rows(rows, include_sites=False):
    rendered = []
    for row in rows:
        numbers = ([row["sites"]] if include_sites else []) + [row["files"], row["pages"], row["total"]]
        cells = "".join(f"<td>{number}</td>" for number in numbers)
        rendered.append(f'<tr><th scope="row">{html.escape(row["label"])}</th>{cells}</tr>')
    return "\n".join(rendered)


def checked_output(output):
    path = Path(output)
    if not path.is_absolute():
        path = ROOT / path
    resolved = path.resolve()
    if (not resolved.is_relative_to(ROOT.resolve()) or resolved == ROOT.resolve()
            or any(part.is_symlink() for part in (path, *path.parents) if part.is_relative_to(ROOT))):
        raise ValueError("Use a dedicated output directory inside this repository.")
    first = resolved.relative_to(ROOT.resolve()).parts[0]
    if first in {"docs", "agent", "solutions", "fixtures", "tools", "scripts", "site", ".git", ".github"}:
        raise ValueError("Output must not overwrite a source or documentation directory.")
    if path.exists() and any(path.iterdir()):
        marker = path / MARKER
        if not marker.is_file():
            raise ValueError("Refuse to overwrite an unmarked nonempty directory.")
        previous = json.loads(marker.read_text(encoding="utf-8"))
        permitted = set(previous["files"]) | {MARKER}
        actual = {p.relative_to(path).as_posix() for p in path.rglob("*") if p.is_file()}
        if actual != permitted or any(p.is_symlink() for p in path.rglob("*")):
            raise ValueError("Unknown files/symlinks in staging; do not upload or delete them automatically.")
    return path


def build(output="_site", write_docs=True):
    staging = checked_output(output)
    docs_html, staged_html = render(False), render(True)
    staging.mkdir(parents=True, exist_ok=True)
    expected = {destination for _, destination in ASSETS.values()} | {"index.html", ".nojekyll"}
    if (staging / MARKER).exists():
        old = json.loads((staging / MARKER).read_text(encoding="utf-8"))["files"]
        for relative in set(old) - expected:
            target = (staging / relative).resolve()
            if not target.is_relative_to(staging.resolve()):
                raise ValueError("Unsafe path in previous staging manifest.")
            target.unlink()
    for source, destination in ASSETS.values():
        target = staging / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path(source), target)
    (staging / "index.html").write_text(staged_html, encoding="utf-8")
    (staging / ".nojekyll").write_text("", encoding="utf-8")
    manifest = {
        "builder": "scripts/build_site.py", "files": sorted(expected),
        "sha256": {name: hashlib.sha256((staging / name).read_bytes()).hexdigest() for name in sorted(expected)},
    }
    (staging / MARKER).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    if write_docs:
        (ROOT / "docs" / "index.html").write_text(docs_html, encoding="utf-8")
        (ROOT / "docs" / "sharepoint-actions.md").write_text(
            sharepoint_reference_markdown(load_sharepoint_reference()), encoding="utf-8")
    return staging


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="_site", help="Dedicated allowlisted build directory, relative to the repository.")
    args = parser.parse_args()
    target = build(args.output)
    print(f"Built docs/index.html and {len(ASSETS) + 3} allowlisted staging files in {target}")


if __name__ == "__main__":
    main()
