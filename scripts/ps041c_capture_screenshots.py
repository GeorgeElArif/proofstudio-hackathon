#!/usr/bin/env python3
"""Browser capture helper invoked by the disposable PS-041C session harness."""
from __future__ import annotations
import os
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

base="http://127.0.0.1:4173"; campaign=os.environ["PS041C_SCREENSHOT_CAMPAIGN_ID"]; run=os.environ["PS041C_SCREENSHOT_RUN_ID"]
cookie=os.environ["PS041C_SCREENSHOT_COOKIE"]; name,value=cookie.split("=",1); out=Path(os.environ["PS041C_SCREENSHOT_OUT"]); out.mkdir(parents=True,exist_ok=True)

def shot(page,path,name,width=1440,height=1000):
    page.set_viewport_size({"width":width,"height":height}); page.goto(base+path,wait_until="networkidle"); page.screenshot(path=out/name,full_page=True)

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    anon=browser.new_context(viewport={"width":1440,"height":1000}); page=anon.new_page()
    shot(page,f"/account/campaigns/{campaign}/proof-room","01-private-proof-room-unauthenticated.png")
    shot(page,"/passport/not-a-public-proof","07-arbitrary-public-passport-not-found.png")
    anon.close()
    context=browser.new_context(viewport={"width":1440,"height":1000})
    context.add_cookies([{"name":name,"value":value,"domain":"127.0.0.1","path":"/","httpOnly":True,"sameSite":"Lax"}]); page=context.new_page()
    shot(page,f"/account/campaigns/{campaign}/proof-room?runId={run}","02-private-proof-room-authorized.png")
    shot(page,"/account/campaigns/unmapped-campaign/proof-room","03-private-proof-room-not-found.png")
    shot(page,f"/account/campaigns/{campaign}/passport/{run}","04-private-passport-authorized.png")
    shot(page,"/account/campaigns/unmapped-campaign/passport/unmapped-run","05-private-passport-denied.png")
    golden=json.loads(Path("docs/evidence/demo/golden-demo-run.json").read_text(encoding="utf-8"))["run_id"]
    shot(page,f"/passport/{golden}","06-exact-golden-public-passport.png")
    shot(page,"/dashboard","08-dashboard-private-launchers.png")
    shot(page,f"/account/campaigns/{campaign}/proof-room?runId={run}","09-mobile-private-proof-room.png",390,844)
    shot(page,f"/account/campaigns/{campaign}/passport/{run}","10-mobile-private-passport.png",390,844)
    context.close(); browser.close()
