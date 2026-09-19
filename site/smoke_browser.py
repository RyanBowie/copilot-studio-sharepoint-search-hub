"""Optional isolated headless browser smoke test; never attaches to an existing browser."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import threading
import textwrap

from preview import ROOT, DEFAULT_PREFIX, create_server


LIGHT_PALETTE = {
    "bg": "#f2f2f8", "bg-elevated": "#f8f7fc", "surface": "#ffffff",
    "surface-soft": "#f2f2f8", "border": "#e3dfed", "border-strong": "#9285aa",
    "text": "#102631", "text-muted": "#52637a", "text-soft": "#667287",
    "accent": "#7653ae", "accent-hover": "#58378b", "accent-soft": "#eee8f7",
    "accent-fg": "#ffffff", "link": "#066bc7", "success": "#207346",
    "danger": "#b4233e", "warning": "#8c6208", "chart-blue": "#0877dd",
    "chart-indigo": "#5364ba", "chart-purple": "#7653ae", "chart-violet": "#9651bb",
    "chart-magenta": "#b535c3", "chart-track": "#e8e3f0", "transparent": "transparent",
    "highlight": "rgba(118, 83, 174, 0.12)",
}
DARK_PALETTE = LIGHT_PALETTE | {
    "bg": "#171717", "bg-elevated": "#222222", "surface": "#1f1f1f",
    "surface-soft": "#262626", "border": "#3b3b3b", "border-strong": "#858585",
    "text": "#f2f2f2", "text-muted": "#bdbdbd", "text-soft": "#aaaaaa",
    "accent": "#c3a0ef", "accent-hover": "#debeff", "accent-soft": "#2b2b2b",
    "accent-fg": "#181818", "link": "#80baff", "success": "#4ade80",
    "danger": "#f87171", "warning": "#fbbf24", "chart-blue": "#69aeff",
    "chart-indigo": "#98a5ff", "chart-purple": "#bc98ed", "chart-violet": "#d097ee",
    "chart-magenta": "#ed8fea", "chart-track": "#3b3b3b",
    "highlight": "rgba(195, 160, 239, 0.12)",
}


def rgb(hex_color):
    return "rgb(" + ", ".join(str(int(hex_color[i:i + 2], 16)) for i in (1, 3, 5)) + ")"


def check_theme(page, theme):
    expected = LIGHT_PALETTE if theme == "light" else DARK_PALETTE
    actual = page.evaluate("""keys => {
        const style = getComputedStyle(document.documentElement);
        return Object.fromEntries(keys.map(key => [key, style.getPropertyValue('--cp-' + key).trim()]));
    }""", list(expected))
    assert actual == expected, (theme, actual)
    styles = page.evaluate("""() => {
        const read = (selector, properties) => {
            const style = getComputedStyle(document.querySelector(selector));
            return Object.fromEntries(properties.map(property => [property, style[property]]));
        };
        return {
            body: read('body', ['backgroundColor', 'color', 'fontSize', 'lineHeight', 'fontFamily']),
            title: read('h1', ['fontWeight', 'fontSize', 'lineHeight', 'letterSpacing', 'backgroundImage', 'backgroundClip']),
            heading: read('h2', ['fontWeight']),
            header: read('.topbar', ['backgroundColor', 'borderBottomWidth', 'borderBottomColor']),
            card: read('.shot-card', ['backgroundColor', 'borderRadius', 'borderTopWidth', 'borderTopColor']),
            button: read('.button.primary', ['backgroundColor', 'color', 'borderRadius']),
            link: read('.guide-jumps a', ['color']),
            image: read('#showcase img', ['filter', 'opacity', 'mixBlendMode'])
        };
    }""")
    assert styles["body"]["backgroundColor"] == rgb(expected["bg"])
    assert styles["body"]["color"] == rgb(expected["text"])
    assert styles["body"]["fontSize"] == "16px"
    assert styles["body"]["lineHeight"] == "26.4px"
    assert styles["body"]["fontFamily"].startswith('"Segoe UI", Aptos, Calibri')
    title = styles["title"]
    assert title["fontWeight"] == "450"
    size = float(title["fontSize"].removesuffix("px"))
    assert 36 <= size <= 64, size
    assert abs(float(title["lineHeight"].removesuffix("px")) - size * 1.12) < .01
    assert abs(float(title["letterSpacing"].removesuffix("px")) + size * .035) < .01
    assert title["backgroundClip"] == "text"
    gradient = f'linear-gradient(105deg, {rgb(expected["chart-blue"])}, {rgb(expected["chart-purple"])} 56%, {rgb(expected["chart-magenta"])})'
    assert title["backgroundImage"] == gradient, title
    assert styles["heading"]["fontWeight"] == "600"
    assert styles["header"] == {"backgroundColor": rgb(expected["surface"]), "borderBottomWidth": "1px",
                                "borderBottomColor": rgb(expected["border"])}
    assert styles["card"] == {"backgroundColor": rgb(expected["surface"]), "borderRadius": "16px",
                              "borderTopWidth": "1px", "borderTopColor": rgb(expected["border"])}
    assert styles["button"] == {"backgroundColor": rgb(expected["accent"]),
                                "color": rgb(expected["accent-fg"]), "borderRadius": "10px"}
    assert styles["link"]["color"] == rgb(expected["link"])
    assert styles["image"] == {"filter": "none", "opacity": "1", "mixBlendMode": "normal"}
    assert page.evaluate("() => document.documentElement.scrollWidth <= window.innerWidth")
    return {"theme": theme, "titleSize": size, "variables": actual}


def check_keyboard_focus(page, selector, theme):
    element = page.locator(selector)
    assert element.evaluate("(element) => element === document.activeElement")
    focus = element.evaluate("""element => {
        const style = getComputedStyle(element);
        return {visible: element.matches(':focus-visible'), width: style.outlineWidth,
                color: style.outlineColor, offset: style.outlineOffset, style: style.outlineStyle};
    }""")
    palette = LIGHT_PALETTE if theme == "light" else DARK_PALETTE
    assert focus == {"visible": True, "width": "3px", "color": rgb(palette["accent"]),
                     "offset": "5px", "style": "solid"}, focus


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser-channel", choices=("msedge", "chrome", "chromium"), default="msedge")
    args = parser.parse_args()
    channel = None if args.browser_channel == "chromium" else args.browser_channel
    profile = ROOT / ".site-browser-profile"
    artifacts = ROOT / ".site-browser-artifacts"
    if profile.exists():
        raise ValueError("Refuse to reuse an existing browser profile; close/review that directory first.")
    if artifacts.is_symlink():
        raise ValueError("Browser artifacts must be local to the repository.")
    artifacts.mkdir(exist_ok=True)
    profile.mkdir()
    for key in ("TEMP", "TMP", "TMPDIR"):
        os.environ[key] = str(artifacts)
    from playwright.sync_api import sync_playwright

    server = create_server()
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_address[1]}{DEFAULT_PREFIX}"
    errors, blocked = [], []
    results = {}
    try:
        with sync_playwright() as playwright:
            context = playwright.chromium.launch_persistent_context(
                user_data_dir=str(profile), channel=channel, headless=True,
                viewport={"width": 1440, "height": 1000}, accept_downloads=False,
                downloads_path=str(artifacts), traces_dir=str(artifacts),
                args=["--no-first-run", "--no-default-browser-check", "--disable-background-networking",
                      "--disable-sync", "--disable-component-update"])
            try:
                def route_request(route):
                    if route.request.url.startswith(base):
                        route.continue_()
                    else:
                        blocked.append(route.request.url)
                        route.abort()
                context.route("**/*", route_request)
                page = context.pages[0]
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.on("console", lambda message: errors.append(message.text) if message.type == "error" else None)
                response = page.goto(base + "?scoutTheme=light&keep=1", wait_until="networkidle")
                assert response.status == 200
                assert page.locator("html").get_attribute("data-theme") == "light"
                assert page.locator("main > section").first.get_attribute("id") == "showcase"
                assert page.locator("#primary-actions a").all_text_contents() == [
                    "Download solution ZIP", "Import and configure", "View repository"]
                for image in page.locator("#showcase img").all():
                    image.evaluate("(image) => image.decode()")
                page.screenshot(path=str(artifacts / "showcase-desktop.png"))
                for i in range(1, 7):
                    page.locator(f"#step-{i}").click()
                    assert page.locator(f"#stage-{i}").is_visible()
                    assert page.locator(f"#step-{i}").get_attribute("aria-selected") == "true"
                page.locator("#step-6").focus()
                page.keyboard.press("Home")
                check_keyboard_focus(page, "#step-1", "light")
                page.keyboard.press("ArrowDown")
                assert page.locator("#stage-2").is_visible()
                for name in ("all", "hr", "it", "excel"):
                    page.locator("#gallery-" + name).click()
                    assert page.locator("#screen-" + name).is_visible()
                    for image in page.locator("#screen-" + name + " img").all():
                        image.scroll_into_view_if_needed()
                        image.evaluate("(image) => image.decode()")
                page.locator(".wiring summary").click()
                assert page.locator(".wiring pre").is_visible()
                source = (ROOT / "agent" / "agent.mcs.yml").read_text(encoding="utf-8")
                expected = textwrap.dedent(source.split("instructions: |-\n", 1)[1]
                                           .split("\ngptCapabilities:", 1)[0]).rstrip("\n")
                assert page.locator("#instruction-source code").text_content() == expected
                for image in page.locator("#agent img, #agent-flow img").all():
                    image.scroll_into_view_if_needed()
                    image.evaluate("(image) => image.decode()")
                    assert image.get_attribute("src") == image.locator("..").get_attribute("href")
                    full = page.request.get(base + image.get_attribute("src"))
                    assert full.status == 200 and full.body().startswith(b"\x89PNG\r\n\x1a\n")
                for section in ("agent-instructions", "tools", "flow-search", "flow-paging",
                                "sp-Initial_search", "sp-Read_current_items", "sp-Final_file_acl"):
                    page.locator("#" + section).screenshot(path=str(artifacts / (section + "-desktop.png")))
                assert page.locator(".sp-action").count() == 12
                assert page.locator("#tenant-customization tbody tr").count() == 9
                expected_parameters = {"Initial_search": "_api/search/postquery",
                                       "SharePoint_profile": "_api/SP.UserProfiles.PeopleManager/GetMyProperties?$select=PersonalUrl,AccountName"}
                for action, uri in expected_parameters.items():
                    data = json.loads(page.locator("#sp-config-" + action + " code").text_content())
                    assert data["parameters/uri"] == uri
                page.locator("#sp-Final_file_acl .sp-definition summary").click()
                assert page.locator("#sp-Final_file_acl .sp-definition pre").is_visible()
                results["sharePointActionsWithExactRequests"] = 12
                results["newTenantCustomizationRows"] = 9
                results["showcaseAndThreePrimaryActionsPassed"] = True
                results["displayedInstructionsMatchSource"] = True
                results["inlineNativeFlowScreenshots"] = page.locator("#agent-flow img").count()
                results["uniqueEmbeddedProductScreenshots"] = page.locator("img").evaluate_all(
                    "(images) => new Set(images.map(image => image.getAttribute('src'))).size")
                results["architectureButtons"] = 6
                results["galleryButtons"] = 4
                results["keyboardTabsPassed"] = True
                results["settingsDisclosurePassed"] = True
                package = page.request.get(base + "downloads/CorpNetSearchHubReference_1_0_0_0_unmanaged.zip")
                assert package.status == 200
                digest = hashlib.sha256(package.body()).hexdigest()
                assert digest == "525136e9e96afaf5a90594cc14cf502555b16eb31680a9c64dc3b109ec925272"
                results["httpSolutionSha256"] = digest
                assert len(package.body()) == 64159
                page.goto(base + "?scoutTheme=light&keep=1", wait_until="networkidle")
                check_theme(page, "light")
                page.screenshot(path=str(artifacts / "desktop-light.png"))
                page.get_by_role("navigation", name="Main navigation").get_by_role("link", name="Coverage", exact=True).click()
                assert page.url.endswith("#coverage")
                page.get_by_role("button", name="Switch to dark theme").focus()
                page.keyboard.press("Enter")
                assert page.locator("html").get_attribute("data-theme") == "dark"
                assert "keep=1" in page.url and "scoutTheme=dark" in page.url and page.url.endswith("#coverage")
                check_keyboard_focus(page, "#theme-toggle", "dark")
                check_theme(page, "dark")
                page.evaluate("() => window.scrollTo(0, 0)")
                page.screenshot(path=str(artifacts / "desktop-dark.png"))
                results["themeAndQueryPreservationPassed"] = True
                results["computedThemes"] = []
                for width in (1440, 1024, 768, 390, 320):
                    page.set_viewport_size({"width": width, "height": 844})
                    for theme in ("light", "dark"):
                        page.emulate_media(color_scheme="dark" if theme == "light" else "light")
                        page.goto(base + "?scoutTheme=" + theme, wait_until="networkidle")
                        assert page.locator("html").get_attribute("data-theme") == theme
                        results["computedThemes"].append({"width": width, **check_theme(page, theme)})
                        assert page.get_by_role("heading", level=1).is_visible()
                        assert page.locator("#instruction-source code").text_content() == expected
                        page.keyboard.press("Tab")
                        check_keyboard_focus(page, ".skip", theme)
                        page.keyboard.press("Enter")
                        assert page.locator("#main").evaluate("(element) => element === document.activeElement")
                        page.get_by_role("button", name="Switch to " + ("dark" if theme == "light" else "light") + " theme").focus()
                        page.keyboard.press("Enter")
                        check_theme(page, "dark" if theme == "light" else "light")
                        page.keyboard.press("Enter")
                        check_theme(page, theme)
                        page.locator("#gallery-hr").focus()
                        page.keyboard.press("End")
                        check_keyboard_focus(page, "#gallery-excel", theme)
                        assert page.locator("#screen-excel").is_visible()
                        page.evaluate("() => window.scrollTo(0, 0)")
                        if width == 390:
                            page.screenshot(path=str(artifacts / ("mobile-" + theme + ".png")))
                            for section in ("agent-instructions", "sp-Initial_search", "sp-Final_file_acl"):
                                page.locator("#" + section).screenshot(
                                    path=str(artifacts / (section + "-mobile-" + theme + ".png")))
                results["noHorizontalOverflowAtWidthsBothThemes"] = [1440, 1024, 768, 390, 320]
                for theme in ("light", "dark"):
                    page.emulate_media(color_scheme=theme)
                    for query in ("", "?scoutTheme=invalid"):
                        page.goto(base + query, wait_until="networkidle")
                        assert page.locator("html").get_attribute("data-theme") == theme
                        check_theme(page, theme)
                    for media in ({"forced_colors": "active"}, {"media": "print"}):
                        page.emulate_media(**media)
                        fallback = page.locator("h1").evaluate("""element => {
                            const style = getComputedStyle(element);
                            return {background: style.backgroundImage, color: style.color};
                        }""")
                        assert fallback["background"] == "none"
                        assert fallback["color"] != "rgba(0, 0, 0, 0)"
                        page.emulate_media(forced_colors="none", media="screen")
                results["systemPreferenceAndInvalidParameterFallbackPassed"] = True
                results["forcedColorsAndPrintTitleFallbackPassed"] = True
                results["keyboardNavigationFocusAndToggleBothThemesPassed"] = True
                results["browserUserAgent"] = page.evaluate("() => navigator.userAgent")
                assert not errors, errors
                assert not blocked, blocked
                results.update({"pageErrors": errors, "externalRequests": blocked, "existingBrowserUsed": False,
                                "server": "Loopback only; project-prefixed allowlisted staging tree."})
            finally:
                context.close()
            browser = playwright.chromium.launch(channel=channel, headless=True)
            try:
                nojs = browser.new_context(java_script_enabled=False, viewport={"width": 390, "height": 844})
                nojs.route("**/*", route_request)
                page = nojs.new_page()
                assert page.goto(base).status == 200
                assert page.locator("#instruction-source code").text_content() == expected
                assert page.locator("#agent-flow img").count() == 9
                assert page.locator(".sp-action").count() == 12
                assert page.locator("#setup .setup > li").count() == 10
                assert page.locator('[role="tabpanel"]:visible').count() == 10
                assert page.evaluate("() => document.documentElement.scrollWidth <= window.innerWidth")
                assert not blocked, blocked
                results["noJavaScriptWalkthroughPassed"] = True
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        shutil.rmtree(profile)
    (artifacts / "smoke-report.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
