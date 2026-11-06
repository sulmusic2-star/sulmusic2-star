"""Draw site/og.png, the 1200x630 picture shown when someone shares a link to the site.

usage: python3 tools/og_image.py   (needs Pillow)
The same look as the site: a black bar with the name in white, the home page's question in bold, one line in
the secondary grey, on white, in the Helvetica/Arial stack (Liberation Sans here when neither is installed).
Rerun it when SITE_NAME or the home page's wording changes.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from build import HOME_H1, SITE_NAME  # noqa: E402

TEXT, SECONDARY, BAR, PAGE = "#0b0c0c", "#505a5f", "#0b0c0c", "#ffffff"
BOLD = ["/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf", "C:/Windows/Fonts/arialbd.ttf"]
REGULAR = ["/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
           "/Library/Fonts/Arial.ttf", "C:/Windows/Fonts/arial.ttf"]


def font(faces, size):
    for path in faces:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size)


img = Image.new("RGB", (1200, 630), PAGE)
d = ImageDraw.Draw(img)
d.rectangle([0, 0, 1200, 110], fill=BAR)
d.text((80, 28), SITE_NAME, font=font(BOLD, 52), fill=PAGE)
d.text((80, 200), HOME_H1, font=font(BOLD, 72), fill=TEXT)
d.text((80, 330), "Town and county agendas, read every morning:", font=font(REGULAR, 36), fill=SECONDARY)
d.text((80, 382), "solar, batteries, data centers, zoning, housing.", font=font(REGULAR, 36), fill=SECONDARY)
d.text((80, 540), "Not a government website.", font=font(REGULAR, 28), fill=SECONDARY)
img.save(ROOT / "site" / "og.png", optimize=True)
print("wrote site/og.png")
