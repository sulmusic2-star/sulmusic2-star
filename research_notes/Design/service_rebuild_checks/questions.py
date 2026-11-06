"""Rows whose headline is a question or a sentence addressed to the reader (the clerk's words; listed, not changed).

usage: python3 -I questions.py SITE_DIR
"""
import glob
import html
import re
import sys

site = sys.argv[1]
reader = re.compile(r"\?\s*$|\b(?:you|your|yours|we|us|our|I|I’ll|I'll|please|let’s|let's)\b")
seen = {}
for path in sorted(glob.glob(f"{site}/**/*.html", recursive=True)):
    text = open(path, encoding="utf-8").read()
    for mt in re.finditer(r'<p class="row-head">(?:<span class="row-rank">\d+</span> )?<(?:a|b)[^>]*>([^<]*)</(?:a|b)>', text):
        head = html.unescape(mt.group(1))
        if reader.search(head):
            seen.setdefault(head, []).append(path.replace(site + "/", ""))
print(f"headlines that are a question or speak to the reader: {len(seen)}")
for head, pages in seen.items():
    print(f"  {head!r}: {len(pages)} page(s), e.g. {pages[0]}")
