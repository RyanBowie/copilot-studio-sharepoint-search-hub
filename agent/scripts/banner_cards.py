"""Context-only Adaptive Card images; search rows stay in the existing Markdown message."""

import base64
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCOPES = ("All", "CorpNet", "HR", "Finance", "IT")
MAX_CARD_BYTES = 12_000
NODE_ID = "sharePointContextBanner"


class Formula(str):
    pass


def image_asset(name, expected):
    data = (ROOT / "cards" / name).read_bytes()
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError(f"Unreviewed image bytes: {name}")
    return "data:image/png;base64," + base64.b64encode(data).decode()


def inventory():
    manifest = json.loads((ROOT / "cards" / "assets.json").read_text(encoding="utf-8"))
    if set(manifest["themes"]) != set(SCOPES):
        raise ValueError("Exactly the five controlled scope themes are required.")
    themes = {
        scope: {"url": image_asset(value["file"], value["sha256"]), "altText": value["altText"]}
        for scope, value in manifest["themes"].items()
    }
    name = "assets/sharepoint-48.png"
    return themes, image_asset(name, manifest["thirdParty"][name]["sha256"])


def structure(title, banner_url, banner_alt, icon):
    return {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard", "version": "1.5",
        "fallbackText": title,
        "body": [
            {"type": "TextBlock", "text": title, "weight": "bolder", "size": "medium", "wrap": True},
            {"type": "Image", "url": banner_url, "altText": banner_alt, "size": "stretch", "spacing": "small"},
            {"type": "ColumnSet", "spacing": "small", "columns": [
                {"type": "Column", "width": "auto", "verticalContentAlignment": "center", "items": [
                    {"type": "Image", "url": icon, "altText": "Microsoft SharePoint product icon",
                     "width": "24px", "backgroundColor": "#FFFFFF"},
                ]},
                {"type": "Column", "width": "stretch", "items": [
                    {"type": "TextBlock", "text": "Microsoft SharePoint", "wrap": True, "size": "small"},
                    {"type": "TextBlock", "text": "Search uses your selected accounts and approved sites.",
                     "wrap": True, "size": "small", "isSubtle": True, "spacing": "none"},
                ]},
            ]},
        ],
    }


def card(scope):
    if scope not in SCOPES:
        raise ValueError("Unapproved scope; no banner is available.")
    themes, icon = inventory()
    result = structure(f"{scope} SharePoint search", themes[scope]["url"], themes[scope]["altText"], icon)
    if len(json.dumps(result, ensure_ascii=False, separators=(",", ":")).encode("utf-8")) > MAX_CARD_BYTES:
        raise ValueError("Context card exceeds its fixed payload budget.")
    return result


def power_fx(value):
    if isinstance(value, Formula):
        return str(value)
    if isinstance(value, str):
        return '"' + value.replace('"', '""') + '"'
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, list):
        return "[\n" + ",\n".join(power_fx(item) for item in value) + "\n]"
    if isinstance(value, dict):
        return "{\n" + ",\n".join("'" + key + "': " + power_fx(item) for key, item in value.items()) + "\n}"
    raise TypeError(type(value))


def switch(values):
    return Formula("Switch(Topic.Department, " + ", ".join(
        power_fx(scope) + ", " + power_fx(values[scope]) for scope in SCOPES
    ) + ', "")')


def banner_node():
    themes, icon = inventory()
    for scope in SCOPES:
        card(scope)
    content = structure(
        switch({scope: f"{scope} SharePoint search" for scope in SCOPES}),
        switch({scope: themes[scope]["url"] for scope in SCOPES}),
        switch({scope: themes[scope]["altText"] for scope in SCOPES}),
        icon,
    )
    return {
        "kind": "SendActivity", "id": NODE_ID, "disabled": False,
        "activity": {"attachments": [{"kind": "AdaptiveCardTemplate", "cardContent": "=" + power_fx(content)}]},
    }
