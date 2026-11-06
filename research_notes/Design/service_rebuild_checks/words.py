"""Visible word counts for the proof: the whole page, and the chrome (everything outside the rows; on a meeting
page also outside the headline, the summary values, the excerpt and the item list).

usage: python3 -I words.py SITE_DIR page.html [page.html ...]
Counts the text a visitor sees: script, style, template, hidden and offscreen elements, option lists and .sr-only
text left out; a token with no letter or digit (a stray comma between links) is not a word.
"""
import re
import sys
from html.parser import HTMLParser


class Visible(HTMLParser):
    SKIP = {"script", "style", "template", "datalist", "noscript", "title", "head"}

    def __init__(self, chrome, meeting):
        super().__init__(convert_charrefs=True)
        self.chrome = chrome
        self.meeting = meeting
        self.stack = []
        self.words = []
        self.rows = 0
        self.hidden_depth = 0
        self.content_depth = 0
        self.in_list = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = (a.get("class") or "").split()
        hidden = ("hidden" in a or "sr-only" in classes or "skip" in classes or tag in self.SKIP or a.get("aria-hidden") == "true")
        content = tag == "li" and "row" in classes
        if self.meeting and (tag in ("h1", "dd", "blockquote") or (tag == "ul" and "list" in classes)):
            content = True
        self.stack.append((tag, hidden, content))
        if hidden:
            self.hidden_depth += 1
        if content:
            self.content_depth += 1
            if "row" in classes:
                self.rows += 1

    def handle_endtag(self, tag):
        while self.stack:
            t, hidden, content = self.stack.pop()
            if hidden:
                self.hidden_depth -= 1
            if content:
                self.content_depth -= 1
            if t == tag:
                break

    def handle_data(self, data):
        if self.hidden_depth or (self.chrome and self.content_depth):
            return
        self.words += [w for w in data.split() if re.search(r"[A-Za-z0-9]", w)]


def count(path, chrome, meeting):
    p = Visible(chrome, meeting)
    p.feed(open(path, encoding="utf-8").read())
    return len(p.words), p.rows, p.words


if __name__ == "__main__":
    site = sys.argv[1]
    for rel in sys.argv[2:]:
        path = f"{site}/{rel}"
        meeting = rel.startswith("m/")
        total, rows, words = count(path, False, meeting)
        chrome, _, cwords = count(path, True, meeting)
        what = "outside the headline, values, excerpt and item list" if meeting else "outside the rows"
        print(f"{rel}: {total} visible words in all, {rows} rows, {chrome} words {what}")
        print("   ", " ".join(cwords))
