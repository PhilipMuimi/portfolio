"""Browser regression checks for the portfolio using an isolated Chrome instance."""

import asyncio
import base64
import json
import os
import urllib.request
from pathlib import Path
import websockets

OUT = Path(__file__).resolve().parents[1] / "qa"
BASE_URL = os.environ.get("PORTFOLIO_URL", "http://127.0.0.1:8765")
DEBUG_URL = os.environ.get("BROWSER_DEBUG_URL", "http://127.0.0.1:9224")


async def main():
    OUT.mkdir(exist_ok=True)
    pages = json.load(urllib.request.urlopen(DEBUG_URL + "/json", timeout=10))
    page = next((p for p in pages if p["type"] == "page"))
    async with websockets.connect(
        page["webSocketDebuggerUrl"], max_size=20000000
    ) as ws:
        sequence = 0
        errors = []
        failures = []

        async def call(method, params=None):
            nonlocal sequence
            sequence += 1
            ident = sequence
            await ws.send(
                json.dumps({"id": ident, "method": method, "params": params or {}})
            )
            while True:
                result = json.loads(await ws.recv())
                if result.get("method") == "Runtime.exceptionThrown":
                    errors.append(result["params"]["exceptionDetails"])
                if (
                    result.get("method") == "Network.responseReceived"
                    and result["params"]["response"]["status"] >= 400
                ):
                    failures.append(result["params"]["response"]["url"])
                if result.get("id") == ident:
                    if "error" in result:
                        raise RuntimeError(result["error"])
                    return result.get("result", {})

        async def js(expression):
            r = await call(
                "Runtime.evaluate",
                {"expression": expression, "returnByValue": True, "awaitPromise": True},
            )
            if "exceptionDetails" in r:
                raise RuntimeError(r["exceptionDetails"])
            return r.get("result", {}).get("value")

        async def settle():
            await js(
                "new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))"
            )

        async def screenshot(name):
            r = await call(
                "Page.captureScreenshot",
                {"format": "png", "captureBeyondViewport": False},
            )
            (OUT / name).write_bytes(base64.b64decode(r["data"]))

        await call("Page.enable")
        await call("Runtime.enable")
        await call("Network.enable")
        await call(
            "Emulation.setDeviceMetricsOverride",
            {"width": 1440, "height": 1000, "deviceScaleFactor": 1, "mobile": False},
        )
        await call("Page.navigate", {"url": BASE_URL})
        await js(
            "new Promise(resolve=>document.readyState==='complete'?resolve():window.addEventListener('load',resolve,{once:true}))"
        )
        await settle()
        assert await js('document.title.includes("Philip Muimi")')
        await js(
            "document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager')"
        )
        await js(
            "Promise.all([...document.images].map(i=>i.decode().catch(()=>false)))"
        )
        assert await js(
            "[...document.images].every(i=>i.complete&&i.naturalWidth>0)"
        ), "Images failed"
        await js(
            "document.documentElement.dataset.theme='light';localStorage.setItem('portfolio-theme','light')"
        )
        await screenshot("desktop-light.png")
        results = []
        for width in [320, 375, 390, 680, 681, 768, 1024, 1440]:
            await call(
                "Emulation.setDeviceMetricsOverride",
                {
                    "width": width,
                    "height": 900,
                    "deviceScaleFactor": 1,
                    "mobile": width < 681,
                },
            )
            await settle()
            dims = await js(
                "({width:innerWidth,scroll:document.documentElement.scrollWidth})"
            )
            assert dims["scroll"] <= dims["width"], f"Horizontal overflow: {dims}"
            results.append(f"No horizontal overflow at {width}px")
        await call(
            "Emulation.setDeviceMetricsOverride",
            {"width": 390, "height": 844, "deviceScaleFactor": 1, "mobile": True},
        )
        await settle()
        await screenshot("mobile-light.png")
        await js("document.querySelector('.menu-toggle').click()")
        assert await js(
            "document.querySelector('.menu-toggle').getAttribute('aria-expanded')==='true' && getComputedStyle(document.querySelector('.nav-links')).display==='flex'"
        )
        await call(
            "Input.dispatchKeyEvent",
            {
                "type": "keyDown",
                "key": "Escape",
                "code": "Escape",
                "windowsVirtualKeyCode": 27,
            },
        )
        assert await js(
            "document.querySelector('.menu-toggle').getAttribute('aria-expanded')==='false' && document.activeElement===document.querySelector('.menu-toggle')"
        )
        await js(
            "document.querySelector('.menu-toggle').click();document.querySelector('.nav-links a').click()"
        )
        assert await js(
            "document.querySelector('.menu-toggle').getAttribute('aria-expanded')==='false'"
        )
        await js("document.querySelector('[data-filter=data]').click()")
        assert (
            await js("document.querySelectorAll('.skill-item:not([hidden])').length")
            == 3
        )
        await js(
            "document.querySelector('#skill-search').value='SQL';document.querySelector('#skill-search').dispatchEvent(new Event('input'))"
        )
        assert (
            await js("document.querySelectorAll('.skill-item:not([hidden])').length")
            == 1
        )
        await js(
            "document.querySelector('#skill-search').value='nonexistent skill';document.querySelector('#skill-search').dispatchEvent(new Event('input'))"
        )
        assert await js("!document.querySelector('.empty-state').hidden")
        await js(
            "document.querySelector('#skill-search').value='';document.querySelector('[data-filter=all]').click()"
        )
        assert (
            await js("document.querySelectorAll('.skill-item:not([hidden])').length")
            == 6
        )
        await js("document.querySelector('.earlier-education summary').click()")
        assert await js("document.querySelector('.earlier-education').open")
        assert (
            await js("document.querySelector('#contact-form').checkValidity()") == False
        )
        await js(
            "(()=>{const f=document.querySelector('#contact-form');f.elements.name.value='Test & Name';f.elements.email.value='test@example.com';f.elements.subject.value='Role & opportunity';f.elements.message.value='Hello, Philip!';window.composedURL='';HTMLAnchorElement.prototype.click=function(){window.composedURL=this.href};f.requestSubmit()})()"
        )
        composed = await js("window.composedURL")
        assert (
            "subject=Role%20%26%20opportunity" in composed
            and "test%40example.com" in composed
        ), composed
        assert await js(
            "document.querySelector('#form-status').textContent.includes('review and send')"
        )
        await js(
            "document.documentElement.dataset.theme='light';document.querySelector('.theme-toggle').click()"
        )
        assert await js(
            "document.documentElement.dataset.theme==='dark' && localStorage.getItem('portfolio-theme')==='dark'"
        )
        await call("Page.reload")
        await js(
            "new Promise(resolve=>document.readyState==='complete'?resolve():window.addEventListener('load',resolve,{once:true}))"
        )
        await settle()
        assert await js("document.documentElement.dataset.theme==='dark'")
        await screenshot("mobile-dark.png")
        await call(
            "Emulation.setDeviceMetricsOverride",
            {"width": 1440, "height": 1000, "deviceScaleFactor": 1, "mobile": False},
        )
        await js("window.scrollTo(0,0)")
        await settle()
        await screenshot("desktop-dark.png")
        await js(
            "document.documentElement.style.scrollBehavior='auto';document.querySelector('#contact').scrollIntoView()"
        )
        await settle()
        assert await js(
            "document.querySelector('.nav-links a[href=\"#contact\"]').getAttribute('aria-current')==='location'"
        )
        await js("window.scrollTo(0,0)")
        await settle()
        assert await js(
            "document.querySelectorAll('.nav-links [aria-current]').length===0"
        )
        await call("Emulation.setScriptExecutionDisabled", {"value": True})
        await call("Page.reload")
        await asyncio.sleep(0.5)
        await call("Emulation.setScriptExecutionDisabled", {"value": False})
        assert (
            await js("document.querySelectorAll('.skill-item:not([hidden])').length")
            == 6
        )
        assert await js(
            "getComputedStyle(document.querySelector('.nav-links')).display!=='none'"
        )
        await call(
            "Emulation.setDeviceMetricsOverride",
            {"width": 390, "height": 844, "deviceScaleFactor": 1, "mobile": True},
        )
        await settle()
        assert await js(
            "getComputedStyle(document.querySelector('.nav-links')).display!=='none'"
        )
        assert not errors, errors
        assert not failures, failures
        results += [
            "All seven page images loaded",
            "Mobile menu: open, Escape/focus return, close on navigation",
            "Skill category, search, empty state, and reset",
            "Earlier education disclosure",
            "Contact validation and correctly encoded email draft",
            "Dark theme persistence after reload",
            "Active navigation updates and clears at the home section",
            "Content and mobile links available with JavaScript disabled",
            "No JavaScript exceptions or HTTP errors",
        ]
        (OUT / "browser-checks.txt").write_text("\n".join(results) + "\n")
        print("\n".join(results))


if __name__ == "__main__":
    asyncio.run(asyncio.wait_for(main(), timeout=60))
