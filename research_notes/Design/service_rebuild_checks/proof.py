"""The spec's greps over site/**: rows with the banned words, SVG maps, "we" on the content pages, font loading.

usage: python3 -I proof.py SITE_DIR
"""
import glob
import re
import sys

site = sys.argv[1]
pages = glob.glob(f"{site}/**/*.html", recursive=True)
banned = re.compile(r"\bwe\b|\bWe\b|It['’]s a|The town hasn['’]t|so anyone|no vote is listed")
rows_total = rows_bad = 0
bad_examples = []
maps = 0
fonts = 0
for path in pages:
    html = open(path, encoding="utf-8").read()
    for row in re.findall(r'<li class="row[^"]*"[^>]*>.*?</li>', html, flags=re.S):
        rows_total += 1
        text = re.sub(r"<[^>]+>", " ", row)
        if banned.search(text):
            rows_bad += 1
            if len(bad_examples) < 5:
                bad_examples.append((path, banned.search(text).group(0), " ".join(text.split())[:120]))
    if '<svg class="map' in html:
        maps += 1
    if "/fonts/" in html:
        fonts += 1
print(f"pages: {len(pages)}")
print(f"rows: {rows_total}; rows containing we, We, It's a, The town hasn't, so anyone or no vote is listed: {rows_bad}")
for ex in bad_examples:
    print("   ", ex)
print(f'pages with <svg class="map: {maps}')
print(f"pages loading /fonts/: {fonts}")

# "we" on content pages (home, states, towns, meetings, /towns, /upcoming), inside <main>, with the one allowed line
# (the spec's own "We can’t read X’s agendas yet" inset) counted apart.
content = [f"{site}/index.html", f"{site}/towns.html", f"{site}/upcoming.html"] + glob.glob(f"{site}/??.html") \
    + glob.glob(f"{site}/??/*.html") + glob.glob(f"{site}/m/*.html")
we = re.compile(r"\b[Ww]e\b")
allowed = re.compile(r"We can’t read .{1,80}?’s agendas yet")
other = []
insets = 0
for path in content:
    html = open(path, encoding="utf-8").read()
    main = re.search(r"<main.*?</main>", html, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", main.group(0) if main else "")
    insets += len(allowed.findall(text))
    rest = allowed.sub("", text)
    for mt in we.finditer(rest):
        other.append((path, " ".join(rest[max(0, mt.start() - 50):mt.end() + 50].split())))
print(f"content pages checked: {len(content)}; 'We can’t read … yet' insets (the spec's own line): {insets}; other 'we': {len(other)}")
for ex in other[:8]:
    print("   ", ex)
