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
    "scale-provenance": ("docs/scale-512-capture-provenance.json", "evidence/scale-512-capture-provenance.json"),
    "hr-proof": ("docs/m365-validation-summary.json", "evidence/m365-validation-summary.json"),
    "it-proof": ("docs/table-polish-validation-summary.json", "evidence/table-polish-validation-summary.json"),
    "workbook-proof": ("docs/workbook-validation-summary.json", "evidence/workbook-validation-summary.json"),
    "package-proof": ("solutions/validation.json", "evidence/solution-validation.json"),
    "notice": ("NOTICE.md", "NOTICE.md"),
    "asset-notice": ("solutions/ASSET-NOTICE.md", "ASSET-NOTICE.md"),
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
    }

    def substitute(match):
        token = match.group(1)
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
    return staging


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="_site", help="Dedicated allowlisted build directory, relative to the repository.")
    args = parser.parse_args()
    target = build(args.output)
    print(f"Built docs/index.html and {len(ASSETS) + 3} allowlisted staging files in {target}")


if __name__ == "__main__":
    main()
