"""Generate original scope banners; optionally fetch pinned Microsoft integration assets."""

import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "cards" / "assets"
THEMES = {
    "All": ("All approved areas", "Connected knowledge", "#075A63", "#17354C", "#51D6C3"),
    "CorpNet": ("CorpNet", "Company knowledge", "#16334D", "#0C5662", "#65DAD0"),
    "HR": ("Human Resources", "People and workplace", "#523279", "#372151", "#C6A6F3"),
    "IT": ("Information Technology", "Services and support", "#125387", "#17354C", "#78CDF0"),
    "Finance": ("Finance", "Financial guidance", "#20664B", "#173D36", "#A2D6AD"),
}
OFFICIAL = {
    "assets/sharepoint-48.png": "https://res.cdn.office.net/files/fabric/assets/brand-icons/product/png/sharepoint_48x1.png",
    "schema/adaptive-card-1.5.json": "https://raw.githubusercontent.com/microsoft/AdaptiveCards/main/schemas/1.5.0/adaptive-card.json",
    "schema/LICENSE": "https://raw.githubusercontent.com/microsoft/AdaptiveCards/main/LICENSE",
}


def banner(scope):
    title, subtitle, background, dark, accent = THEMES[scope]
    image = Image.new("RGB", (640, 96), background)
    draw = ImageDraw.Draw(image)
    draw.polygon([(450, 0), (640, 0), (640, 96), (395, 96)], fill=dark)
    draw.rectangle((0, 0, 5, 95), fill=accent)
    draw.text((23, 21), title, font=ImageFont.load_default(size=26), fill="white")
    draw.text((24, 56), subtitle, font=ImageFont.load_default(size=15), fill="#EBF4F4")
    if scope == "HR":
        for x, y in ((505, 31), (541, 22), (577, 31)):
            draw.ellipse((x, y, x + 17, y + 17), fill=accent)
            draw.rounded_rectangle((x - 4, y + 23, x + 21, y + 44), radius=7, fill=accent)
    elif scope == "IT":
        draw.rounded_rectangle((490, 21, 580, 73), radius=5, outline=accent, width=3)
        for x in (510, 535, 560):
            draw.line((x, 35, x, 60), fill=accent, width=3)
            draw.ellipse((x - 4, 32, x + 4, 40), fill=accent)
        draw.line((520, 80, 550, 80), fill=accent, width=3)
    elif scope == "Finance":
        for x, height in ((499, 23), (530, 39), (561, 57)):
            draw.rounded_rectangle((x, 78 - height, x + 18, 78), radius=3, fill=accent)
        draw.line((490, 82, 588, 82), fill=accent, width=2)
    elif scope == "CorpNet":
        for x, top in ((495, 34), (531, 18), (567, 34)):
            draw.rounded_rectangle((x, top, x + 28, 79), radius=3, outline=accent, width=2)
            for y in range(top + 9, 73, 13):
                draw.rectangle((x + 7, y, x + 11, y + 4), fill=accent)
                draw.rectangle((x + 18, y, x + 22, y + 4), fill=accent)
    else:
        center = (547, 48)
        for x, y in ((500, 25), (501, 72), (591, 24), (592, 72)):
            draw.line((*center, x, y), fill=accent, width=3)
            draw.ellipse((x - 7, y - 7, x + 7, y + 7), fill=accent)
        draw.ellipse((534, 35, 560, 61), fill=accent)
    return image.quantize(colors=16, dither=Image.Dither.NONE)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch-official", action="store_true",
                        help="Fetch the unmodified Microsoft asset/schema; review cards/NOTICE.md first.")
    args = parser.parse_args()
    ASSETS.mkdir(parents=True, exist_ok=True)
    manifest_path = ROOT / "cards" / "assets.json"
    prior = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    if args.fetch_official:
        for name, url in OFFICIAL.items():
            data = urllib.request.urlopen(url, timeout=45).read()
            expected = prior.get("thirdParty", {}).get(name, {}).get("sha256")
            if expected and hashlib.sha256(data).hexdigest() != expected:
                raise ValueError(f"Upstream asset changed: {name}; review rather than silently replace.")
            path = ROOT / "cards" / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    themes = {}
    for scope, (title, subtitle, *_colors) in THEMES.items():
        path = ASSETS / f"{scope}.png"
        banner(scope).save(path, format="PNG", compress_level=9, optimize=False)
        themes[scope] = {"file": f"assets/{scope}.png", "altText": f"{title}: {subtitle}. Original {scope} scope artwork.",
                         "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "width": 640, "height": 96}
    third_party = {}
    for name, url in OFFICIAL.items():
        path = ROOT / "cards" / name
        if not path.exists():
            raise ValueError(f"Missing {name}; review NOTICE.md, then use --fetch-official.")
        third_party[name] = {"source": url, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    manifest = {"bannerGenerator": "Pillow 12.2.0; original geometric artwork, not Microsoft branding",
                "themes": themes, "thirdParty": third_party,
                "imageTransport": "PNG data URI; Adaptive Cards 1.2+, host acceptance must be verified",
                "fabricLicense": "https://aka.ms/fluentui-assets-license"}
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("Generated five original banners; verified local Microsoft asset/schema inventory.")


if __name__ == "__main__":
    main()
