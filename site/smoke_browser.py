"""Optional local headless Edge smoke test; never attaches to an existing browser."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import threading
import textwrap

from preview import ROOT, DEFAULT_PREFIX, create_server


def main():
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
                user_data_dir=str(profile), channel="msedge", headless=True,
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
                assert page.locator("#step-1").evaluate("(element) => element === document.activeElement")
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
                page.screenshot(path=str(artifacts / "desktop-light.png"))
                page.get_by_role("button", name="Switch to dark theme").click()
                assert page.locator("html").get_attribute("data-theme") == "dark"
                assert "keep=1" in page.url and "scoutTheme=dark" in page.url
                page.screenshot(path=str(artifacts / "desktop-dark.png"))
                results["themeAndQueryPreservationPassed"] = True
                for width in (1440, 1024, 768, 390, 320):
                    page.set_viewport_size({"width": width, "height": 844})
                    for theme in ("light", "dark"):
                        page.goto(base + "?scoutTheme=" + theme, wait_until="networkidle")
                        assert page.evaluate("() => document.documentElement.scrollWidth <= window.innerWidth"), f"Overflow at {width}"
                        assert page.get_by_role("heading", level=1).is_visible()
                        assert page.locator("#instruction-source code").text_content() == expected
                        if width == 390:
                            page.screenshot(path=str(artifacts / ("mobile-" + theme + ".png")))
                            for section in ("agent-instructions", "sp-Initial_search", "sp-Final_file_acl"):
                                page.locator("#" + section).screenshot(
                                    path=str(artifacts / (section + "-mobile-" + theme + ".png")))
                results["noHorizontalOverflowAtWidthsBothThemes"] = [1440, 1024, 768, 390, 320]
                results["browserUserAgent"] = page.evaluate("() => navigator.userAgent")
                assert not errors, errors
                assert not blocked, blocked
                results.update({"pageErrors": errors, "externalRequests": blocked, "existingBrowserUsed": False,
                                "server": "Loopback only; project-prefixed allowlisted staging tree."})
            finally:
                context.close()
            browser = playwright.chromium.launch(channel="msedge", headless=True)
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
