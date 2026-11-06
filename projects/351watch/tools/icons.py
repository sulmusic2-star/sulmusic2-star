"""Draw site/favicon.ico and site/apple-touch-icon.png: a plain black square with a white A.

usage: python3 tools/icons.py   (needs Pillow; uses a Helvetica or Arial it can find, else Pillow's own bold face)
The inline SVG favicon in build.py (FAVICON) draws the same.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
BLACK, WHITE = "#0b0c0c", "#ffffff"
FACES = ["/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "/System/Library/Fonts/Helvetica.ttc", "/Library/Fonts/Arial Bold.ttf", "C:/Windows/Fonts/arialbd.ttf"]


def font(size):
    for path in FACES:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size)


def square(px):
    img = Image.new("RGB", (px, px), BLACK)
    d = ImageDraw.Draw(img)
    f = font(int(px * 0.78))
    box = d.textbbox((0, 0), "A", font=f)
    w, h = box[2] - box[0], box[3] - box[1]
    d.text(((px - w) / 2 - box[0], (px - h) / 2 - box[1]), "A", font=f, fill=WHITE)
    return img


if __name__ == "__main__":
    square(180).save(ROOT / "site" / "apple-touch-icon.png", optimize=True)
    square(256).resize((32, 32), Image.LANCZOS).save(ROOT / "site" / "favicon.ico", sizes=[(16, 16), (32, 32)])
    print("wrote site/apple-touch-icon.png and site/favicon.ico")
