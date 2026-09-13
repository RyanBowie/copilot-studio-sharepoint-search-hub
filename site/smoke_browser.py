"""Optional local headless Edge smoke test; never attaches to an existing browser."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import threading

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
                    page.locator("#screen-" + name + " img").wait_for(state="visible")
                    page.wait_for_function("(id) => document.querySelector(id + ' img').naturalWidth > 0", arg="#screen-" + name)
                page.locator(".wiring summary").click()
                page.locator(".wiring img").wait_for(state="visible")
                page.wait_for_function("() => document.querySelector('.wiring img').naturalWidth > 0")
                results["architectureButtons"] = 6
                results["galleryButtons"] = 4
                results["keyboardTabsPassed"] = True
                results["wiringDisclosurePassed"] = True
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
                for width in (390, 320):
                    page.set_viewport_size({"width": width, "height": 844})
                    page.goto(base + "?scoutTheme=light", wait_until="networkidle")
                    assert page.evaluate("() => document.documentElement.scrollWidth <= window.innerWidth"), f"Overflow at {width}"
                    assert page.get_by_role("heading", level=1).is_visible()
                    if width == 390:
                        page.screenshot(path=str(artifacts / "mobile-light.png"))
                results["noHorizontalOverflowAtWidths"] = [390, 320]
                results["browserUserAgent"] = page.evaluate("() => navigator.userAgent")
                assert not errors, errors
                assert not blocked, blocked
                results.update({"pageErrors": errors, "externalRequests": blocked, "existingBrowserUsed": False,
                                "server": "Loopback only; project-prefixed allowlisted staging tree."})
            finally:
                context.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        shutil.rmtree(profile)
    (artifacts / "smoke-report.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
