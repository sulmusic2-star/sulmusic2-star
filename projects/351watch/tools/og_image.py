"""Draw site/og.png, the 1200x630 picture shown when someone shares a link to the site.

usage: python3 tools/og_image.py   (needs Pillow, fontTools and brotli to read the site's own fonts)
Same look as the site: the dot-cluster mark, the product name in Barlow Semi Condensed Bold, one line
in Barlow, on the paper color. Rerun it when SITE_NAME changes.
"""
import io
import sys
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from build import SITE_NAME  # noqa: E402

INK, MUTED, DOT, MARK, PAPER, LAND = "#1f2724", "#545f5a", "#a9b3ac", "#7a2c80", "#ffffff", "#eef1ed"


def font(name, size):
    """A woff2 from site/fonts as a Pillow font."""
    f = TTFont(ROOT / "site" / "fonts" / name)
    f.flavor = None
    buf = io.BytesIO()
    f.save(buf)
    buf.seek(0)
    return ImageFont.truetype(buf, size)


img = Image.new("RGB", (1200, 630), PAPER)
d = ImageDraw.Draw(img)
d.rectangle([0, 560, 1200, 630], fill=LAND)
# the mark: three grey dots and one purple
for x, y, r, c in ((96, 120, 14, DOT), (152, 108, 14, DOT), (160, 176, 14, DOT), (118, 160, 22, MARK)):
    d.ellipse([x - r, y - r, x + r, y + r], fill=c)
d.text((210, 92), SITE_NAME, font=font("barlow-semicondensed-bold.woff2", 96), fill=INK)
d.text((80, 270), "See what’s coming up at", font=font("barlow-semicondensed-bold.woff2", 84), fill=INK)
d.text((80, 365), "your town meetings", font=font("barlow-semicondensed-bold.woff2", 84), fill=INK)
d.text((80, 478), "Solar, batteries and data centers on town agendas, in plain words.",
       font=font("barlow-regular.woff2", 34), fill=MUTED)
img.save(ROOT / "site" / "og.png", optimize=True)
print("wrote site/og.png")
