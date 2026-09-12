"""Render the publication-safe architecture as SVG and editable Excalidraw."""

import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "images"
WIDTH, HEIGHT = 1420, 1030
COLORS = {
    "blue": ("#0078D4", "#CFE4FA"),
    "green": ("#107C10", "#DFF6DD"),
    "purple": ("#5C2D91", "#E8DAEF"),
    "orange": ("#A84800", "#FFF4CE"),
    "neutral": ("#605E5C", "#F3F2F1"),
}
NODES = [
    ("user", 40, 150, "Authenticated user", ["Starts Search SharePoint", "Chooses scope and keywords"], "blue"),
    ("topic", 390, 150, "Guided topic", ["Validates plain input", "Invokes the registered tool"], "blue"),
    ("flow", 740, 150, "Native Power Automate flow", ["Caller-provided connectors", "No provisioning fallback"], "purple"),
    ("identity", 1090, 150, "Identity alignment", ["Profile + source + destination", "Verified mailbox, not chat input"], "purple"),
    ("scope", 1090, 380, "Approved inventory", ["Known collection IDs + hub", "Department is a relevance filter"], "green"),
    ("search", 740, 380, "SharePoint Search", ["Files, pages and folder content", "Bounded candidates and paging"], "green"),
    ("verify", 390, 380, "Current source checks", ["Recheck access per result", "Read actual stored metadata"], "green"),
    ("chat", 40, 660, "Chat preview", ["Up to 5 real links + stored tags", "Initial status is not completion"], "blue"),
    ("continue", 740, 660, "Same-run continuation", ["Continue bounded verification", "Record caps and partial results"], "purple"),
    ("excel", 1090, 660, "Private Excel workbook", ["Filterable table + source links", "Verify rows and private access"], "purple"),
    ("email", 1090, 870, "Verified-account email", ["Private workbook link", "Actual delivery action evidence"], "blue"),
]
EDGES = [
    ("user-topic", [(330, 220), (390, 220)]),
    ("topic-flow", [(680, 220), (740, 220)]),
    ("flow-identity", [(1030, 220), (1090, 220)]),
    ("identity-scope", [(1235, 290), (1235, 380)]),
    ("scope-search", [(1090, 450), (1030, 450)]),
    ("search-verify", [(740, 450), (680, 450)]),
    ("verify-chat", [(440, 520), (440, 605), (185, 605), (185, 660)]),
    ("verify-continue", [(535, 520), (535, 575), (885, 575), (885, 660)]),
    ("continue-excel", [(1030, 730), (1090, 730)]),
    ("excel-email", [(1235, 800), (1235, 870)]),
]


def base(element_id, kind, x, y, width, height):
    return {
        "id": element_id, "type": kind, "x": x, "y": y,
        "width": width, "height": height, "angle": 0,
        "strokeWidth": 1.5, "strokeStyle": "solid", "roughness": 0,
        "opacity": 100, "groupIds": [], "frameId": None,
        "seed": 1, "version": 1, "versionNonce": 1, "isDeleted": False,
        "updated": 1, "link": None, "locked": False,
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    elements = []
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title description">',
        "<title id=\"title\">SharePoint Search Hub architecture</title>",
        "<desc id=\"description\">A guided Copilot Studio topic calls a native caller-authenticated flow. The flow aligns identities, searches approved SharePoint collections, rechecks source access and metadata, returns up to five linked rows, then continues to a verified private workbook and email.</desc>",
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#605E5C"/></marker></defs>',
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="#ffffff"/>',
    ]

    def text(element_id, x, y, lines, size, width, bold=False):
        value = "\n".join(lines)
        element = base(element_id, "text", x, y, width, size * 2.5 * len(lines))
        element.update({
            "text": value, "originalText": value, "fontSize": size, "fontFamily": 2,
            "strokeColor": "#000000", "backgroundColor": "transparent",
            "fillStyle": "solid", "textAlign": "left", "verticalAlign": "top",
            "containerId": None, "lineHeight": 1.25, "autoResize": True,
        })
        elements.append(element)
        weight = "700" if bold else "400"
        for index, line in enumerate(lines):
            svg.append(
                f'<text x="{x}" y="{y + size + index * (size + 10)}" fill="#000000" '
                f'font-family="Arial, Helvetica, sans-serif" font-size="{size}" font-weight="{weight}">{html.escape(line)}</text>'
            )

    text("title", 40, 24, ["SharePoint Search Hub"], 34, 1100, True)
    text("subtitle", 40, 76, ["Permission-aware retrieval  |  Small chat preview  |  Private, bounded export"], 20, 1300)

    for element_id, points in EDGES:
        x, y = points[0]
        element = base(element_id, "arrow", x, y,
                       max(point[0] for point in points) - min(point[0] for point in points),
                       max(point[1] for point in points) - min(point[1] for point in points))
        element.update({
            "points": [[px - x, py - y] for px, py in points],
            "strokeColor": "#605E5C", "backgroundColor": "transparent",
            "fillStyle": "solid", "startArrowhead": None, "endArrowhead": "arrow",
            "startBinding": None, "endBinding": None,
        })
        elements.append(element)
        svg.append(
            '<polyline points="' + " ".join(f"{px},{py}" for px, py in points)
            + '" fill="none" stroke="#605E5C" stroke-width="2" marker-end="url(#arrow)"/>'
        )

    for element_id, x, y, title, lines, color in NODES:
        stroke, fill = COLORS[color]
        box = base(element_id, "rectangle", x, y, 290, 140)
        box.update({"strokeColor": stroke, "backgroundColor": fill,
                    "fillStyle": "solid", "roundness": {"type": 3}})
        elements.append(box)
        svg.append(f'<rect x="{x}" y="{y}" width="290" height="140" rx="12" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
        text(element_id + "-title", x + 15, y + 18, [title], 18, 260, True)
        text(element_id + "-detail", x + 15, y + 59, lines, 15, 265)

    text("boundary-title", 40, 385, ["Trust boundary"], 20, 300, True)
    text("boundary-detail", 40, 429, [
        "The index is not a live inventory.",
        "The hub does not grant access.",
        "No row is invented or inferred.",
    ], 15, 310)
    text("limits-title", 40, 850, ["Explicit bounds, honest status"], 20, 700, True)
    text("limits-detail", 40, 895, [
        "1,000 exported rows  |  2,000 candidates  |  40 search pages",
        "12 batches of up to 20 approved collections",
        "Owner-only demo evidence is not production or permission-denial proof.",
    ], 16, 930)
    svg.append("</svg>")
    (OUT / "architecture.svg").write_text("\n".join(svg) + "\n", encoding="utf-8")
    drawing = {
        "type": "excalidraw", "version": 2, "source": "SharePoint Search Hub",
        "elements": elements, "appState": {"viewBackgroundColor": "#ffffff", "gridSize": 20},
        "files": {},
    }
    (OUT / "architecture.excalidraw").write_text(json.dumps(drawing, indent=2) + "\n", encoding="utf-8")
    print("Rendered docs\\images\\architecture.svg and architecture.excalidraw")


if __name__ == "__main__":
    main()
