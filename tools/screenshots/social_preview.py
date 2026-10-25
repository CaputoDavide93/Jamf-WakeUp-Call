"""Draw docs/assets/social-preview.png (1280x640) from the brand icon.

The owner uploads it by hand under Settings, Social preview. Metadata is stripped.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
ICON = (ROOT / "docs/assets/brand/icon.svg").read_text()
OUT = ROOT / "docs/assets/social-preview.png"

CHIPS = ["Dry run first", "Group, serial or file", "Jamf Pro API"]

HTML = f"""<!doctype html><meta charset="utf-8"><style>
body{{margin:0;width:1280px;height:640px;font-family:-apple-system,"Helvetica Neue",Helvetica,Arial,sans-serif;
 background:radial-gradient(circle at 20% 35%,#1d2f52 0,#14233F 45%,#0b1427 100%);color:#F6F1E7;
 display:flex;align-items:center;position:relative;overflow:hidden}}
.icon{{width:300px;height:300px;margin-left:98px;filter:drop-shadow(0 18px 30px rgba(0,0,0,.45))}}
.icon svg{{width:100%;height:100%}}
.txt{{margin-left:82px;width:720px}}
h1{{margin:0;white-space:nowrap;font-size:76px;line-height:1;font-weight:800;letter-spacing:-2px}}
h1 b{{background:linear-gradient(#FFC94D,#FF7A2F);-webkit-background-clip:text;color:transparent}}
p{{margin:26px 0 30px;font-size:34px;line-height:1.28;font-weight:600;color:#d8d3c8}}
.chips{{display:flex;gap:12px;flex-wrap:wrap}}
.c{{padding:9px 20px;border:2px solid rgba(246,241,231,.28);border-radius:30px;font-size:22px;font-weight:700}}
.c:first-child{{background:linear-gradient(#FFC94D,#FF7A2F);color:#14233F;border-color:transparent}}
.bar{{position:absolute;left:0;right:0;bottom:0;height:10px;background:linear-gradient(90deg,#FFC94D,#FF7A2F)}}
</style><div class="icon">{ICON}</div><div class="txt">
<h1>Jamf <b>WakeUp</b> Call</h1>
<p>Wake the Macs that stopped checking in to Jamf Pro, by group, serial or file</p>
<div class="chips">{''.join(f'<span class="c">{c}</span>' for c in CHIPS)}</div></div><div class="bar"></div>"""


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 640})
        page.set_content(HTML)
        page.screenshot(path=str(OUT))
        browser.close()
    with Image.open(OUT) as im:
        clean = Image.frombytes(im.mode, im.size, im.tobytes())
        clean.save(OUT, optimize=True)
    print("wrote", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
