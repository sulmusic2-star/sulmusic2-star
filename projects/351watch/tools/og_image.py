"""Draw site/og.png, the 1200x630 picture shown when someone shares a link to the site.

usage: python3 tools/og_image.py   (needs Pillow, fontTools and brotli to read the site's own fonts)
Same look as the site: the agenda-sheet mark, the product name in Public Sans SemiBold, one line
in Public Sans, on the paper color. Rerun it when SITE_NAME changes.
"""
import io
import sys
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from build import SITE_NAME  # noqa: E402

INK, MUTED, DOT, MARK, PAPER, LAND, PIN = "#141414", "#5b5b57", "#c8c8c2", "#b3261e", "#ffffff", "#f3f3ef", "#b3261e"


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
# the mark: the red pin the map uses for a town with a meeting this week
d.ellipse([92, 90, 180, 178], fill=PAPER, outline=PIN, width=6)
d.ellipse([112, 110, 160, 158], fill=PIN)
d.text((210, 92), SITE_NAME, font=font("newsreader-display.woff2", 104), fill=INK)
d.text((80, 250), "Know what your town is about to decide", font=font("newsreader-display.woff2", 68), fill=INK)
d.text((80, 335), "on solar, data centers, zoning and housing", font=font("newsreader-display.woff2", 68), fill=INK)
d.text((80, 450), "We read the agendas towns post and say what each board will decide,",
       font=font("libre-franklin-regular.woff2", 30), fill=MUTED)
d.text((80, 492), "and whether you can speak. Massachusetts, New York and Rhode Island.",
       font=font("libre-franklin-regular.woff2", 30), fill=MUTED)
img.save(ROOT / "site" / "og.png", optimize=True)
print("wrote site/og.png")
