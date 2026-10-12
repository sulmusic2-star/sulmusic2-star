#!/usr/bin/env python3
"""slop_lint: flag AI-sounding phrases and patterns in HTML, Markdown, text and CSS files.

    python3 slop_lint.py PATH [PATH ...] [options]

PATH is a file, a directory (searched recursively for .html .htm .md .markdown .txt .css) or a
glob. Each hit prints as `file:line: [rule] message: "matched text"`, then a score line.

Options
  --summary           group hits by rule and by file instead of printing every hit
  --json              machine-readable output
  --ignore R1,R2      skip these rule ids
  --skip-class C      (HTML) skip elements carrying class C; repeatable
  --no-looks          skip the visual checks (CSS rules, middle-dot meta strings, arrows, emoji)
  --max-score N       exit 1 if the total score is above N
  --max-density N     exit 1 if the score per 1,000 words is above N
  --list-rules        print the rules and exit

What is not linted, so quotations, code and data don't count against the copy
  HTML  <script> <style> <code> <pre> <kbd> <samp> <q> <blockquote> <textarea> <svg>, any element
        with a data-slop-ignore attribute or a --skip-class class, everything between
        <!-- slop-lint: off --> and <!-- slop-lint: on -->, and text inside curly quotes.
  MD    front matter, fenced and inline code, link targets, HTML comments, > blockquotes and
        curly-quoted text.
  All   lines containing "slop-lint: ignore"; lines between "slop-lint: off" and "slop-lint: on".

Scoring: each hit adds its rule's weight (1 = weak alone, 2 = usual tell, 3 = near-certain tell).
Density is the score per 1,000 linted words. Verdicts: 0 is clean, under 1.0 per 1,000 words is
near-clean, under 3.0 needs work, anything higher needs a rewrite.

Standard library only (Python 3.8+). The rules are the machine-checkable subset of
references/words.md and references/design.md; reading those still matters, because rhythm,
triads, vague claims and invented facts need a human or model pass.
"""

import argparse
import bisect
import glob
import json
import os
import re
import sys
from html.parser import HTMLParser

# ----------------------------------------------------------------------------- rules
# (id, category, weight, pattern, message). Patterns are case-insensitive and run on text with
# whitespace runs collapsed to one space, one block (paragraph, cell, heading, list item) at a time.
A = r"(?:'|’)"  # straight or curly apostrophe

RULES = [
    # Leftovers from a chat or a draft
    ("chat-residue", "residue", 3,
     r"\b(?:i hope this helps|let me know if|feel free to (?:reach|ask|contact)|great question|happy to help"
     r"|i" + A + r"?d be happy to|as an ai\b|as a(?:n ai)? language model|would you like me to"
     r"|here" + A + r"?s (?:a|an|the) (?:summary|overview|breakdown|rewrite|revised))",
     "chatbot wrapper; delete it and keep the content"),
    ("cutoff-hedge", "residue", 3,
     r"\b(?:as of my (?:last|latest) (?:update|training)|knowledge cutoff|while (?:specific )?details (?:are|remain) "
     r"(?:limited|scarce)|based on (?:the )?available information|not widely (?:documented|available|disclosed|reported))",
     "knowledge-limit hedge; say what the source does not show, or cut it"),
    ("placeholder", "residue", 2,
     r"\[(?:insert|your|describe|add|todo)\b[^\]]{0,60}\]|\blorem ipsum\b|\bTODO:|\bxx-xx\b",
     "unfilled placeholder"),

    # Staging instead of stating
    ("not-x-but-y", "staging", 3,
     r"\bnot (?:just|only|merely|simply) [^.?!;:]{1,80}?\bbut\b",
     "not-just-X-but-Y contrast; state Y directly"),
    ("its-not-x-its-y", "staging", 3,
     r"\b(?:it|this|that)" + A + r"?s not (?:just |only |merely )?[^.?!;]{1,50}?[,;:—–] ?(?:it|this|that)" + A + r"?s\b",
     "it's-not-X-it's-Y reversal; state the point once"),
    ("isnt-just", "staging", 2,
     r"\b(?:is|are|was|were)(?:n" + A + r"t| not) (?:just|only|merely|simply)\b|\bmore than just\b",
     "negative parallelism; say what it is"),
    ("no-x-no-y-just", "staging", 3,
     r"\bno [^,.;!?]{1,30}, no [^,.;!?]{1,30}[,.—–:] ?(?:just|only|simply)\b",
     "'no X, no Y, just Z' formula"),
    ("negative-listing", "staging", 2,
     r"\b(?:not|no) (?:a|an) [^.?!]{1,40}\. (?:not|no) (?:a|an) [^.?!]{1,40}\.",
     "list of what it is not; name what it is"),
    ("throat-clearing", "staging", 2,
     r"\b(?:here" + A + r"?s (?:the thing|the deal|what|why|how|where)|let" + A + r"?s (?:dive|explore|break (?:it|this) down"
     r"|take a (?:closer )?look|be honest|unpack)|without further ado|the (?:truth|reality|bottom line) is|it turns out"
     r"|make no mistake|let that sink in|full stop|at the end of the day|when it comes to|in a world (?:where|of)"
     r"|the real (?:question|problem|issue|story) is|at its core|in a nutshell|it" + A + r"?s no secret)",
     "run-up before the point; start with the point"),
    ("worth-noting", "staging", 2,
     r"\b(?:it" + A + r"?s|it is) (?:worth (?:noting|mentioning|pointing out)|important to (?:note|remember|understand))"
     r"|\bneedless to say\b",
     "announces a point instead of making it"),
    ("rhetorical-cta", "staging", 2,
     r"\b(?:ready to|want to|looking for (?:a way )?to|tired of|struggling to|ever wondered)\b[^.?!]{0,70}\?",
     "rhetorical sales question; say what the product does"),
    ("whether-youre", "staging", 2,
     r"\bwhether you" + A + r"?re (?:a|an)\b",
     "audience-list formula; name one reader"),
    ("ad-cliche", "staging", 2,
     r"\b(?:look no further|say goodbye to|the power of|imagine (?:a|if)\b|introducing\b|we" + A + r"?ve got you covered"
     r"|you" + A + r"?re in the right place)",
     "advertising cliche"),
    ("closer", "staging", 2,
     r"(?:^|[.!?] )(?:that" + A + r"?s (?:it|the (?:point|difference|whole point|real win|key))|and that" + A + r"?s okay"
     r"|that matters|this matters|read that again)[.!]",
     "one-line closer that repeats the point"),
    ("clipped-negatives", "staging", 1,
     r"\bno [a-z]+(?: [a-z]+)?(?:,| and| or) no [a-z]+\b(?! (?:was|were|is|are|has|had|will|can)\b)",
     "paired clipped negatives ('no X, no Y') used as a slogan; say it once, plainly"),
    ("self-reference", "staging", 1,
     r"\b(?:(?:are|is) shown (?:first|below|above)|(?:the|this) (?:table|list|section|page) below"
     r"|below (?:are|is) the|as (?:shown|seen) (?:below|above)|everything below|in this (?:section|page|article))\b",
     "describes the page instead of its subject"),

    # Inflation and borrowed authority
    ("you-care-about", "inflation", 2,
     r"\b(?:you care about|(?:that )?matters? (?:most )?to you|that matter most)\b",
     "template phrase; name the actual thing"),
    ("ai-vocab", "inflation", 2,
     r"\b(?:delv(?:e|es|ed|ing)|tapestr(?:y|ies)|testament|pivotal|underscor(?:e|es|ed|ing)|showcas(?:e|es|ed|ing)"
     r"|interplay|intricac(?:y|ies)|intricate|meticulous(?:ly)?|bolster(?:s|ed|ing)?|garner(?:s|ed|ing)?|vibrant|realm"
     r"|multifaceted|holistic|synerg(?:y|ies|istic)|paradigm|plethora|myriad|embark(?:s|ed|ing)?|enduring|indelible"
     r"|ever-(?:changing|evolving|growing))\b",
     "stock AI vocabulary; use the plain word"),
    ("significance", "inflation", 2,
     r"\b(?:plays? a (?:key|crucial|vital|pivotal|significant|central) role|(?:key|crucial|pivotal|vital|significant) "
     r"(?:moment|turning point|milestone)|marks? a (?:shift|turning point|new era|milestone)|setting the stage"
     r"|reflects? (?:a )?broader|focal point|deeply rooted|the future (?:looks|is) bright|exciting times)",
     "inflated significance; keep the fact, drop the weight"),
    ("landscape", "inflation", 2,
     r"\b(?:today" + A + r"?s|current|regulatory|competitive|business|digital|evolving|shifting|changing|policy|siting) "
     r"landscape\b|\bin today" + A + r"?s\b|\bfast-paced\b",
     "abstract 'landscape' framing"),
    ("hype", "inflation", 2,
     r"\b(?:seamless(?:ly)?|robust|cutting-edge|state-of-the-art|best-in-class|world-class|next-gen(?:eration)?"
     r"|game-?chang(?:er|ers|ing)|revolutioni[sz](?:e|es|ed|ing)|supercharg(?:e|es|ed|ing)|effortless(?:ly)?|hassle-free"
     r"|powerful|unparalleled|unmatched|industry-leading|groundbreaking|innovative|transformative|unlock(?:s|ed|ing)?"
     r"|empower(?:s|ed|ing|ment)?|streamlin(?:e|es|ed|ing)|elevat(?:e|es|ed|ing)|harness(?:es|ed|ing)?"
     r"|leverag(?:e|es|ed|ing)|turbocharg(?:e|ed)|skyrocket(?:s|ed|ing)?)\b",
     "sales language; say what it does, with a number if you have one"),
    ("crucial", "inflation", 2,
     r"\b(?:crucial|vital(?! records| statistics| signs)|invaluable|valuable insights?|actionable(?: insights?)?"
     r"|key (?:insights?|takeaways?|benefits?|features?))\b",
     "importance claimed, not shown"),
    ("marketing", "inflation", 2,
     r"\b(?:stay (?:ahead|informed|in the loop|on top of)|never miss (?:a|an|another|out)|peace of mind|all in one place"
     r"|one-stop|at your fingertips|in (?:just )?(?:seconds|minutes)\b|with ease|like never before|to the next level"
     r"|trusted by|loved by|join (?:thousands|hundreds|millions)|second to none|cut(?:ting)? through the noise"
     r"|single source of truth|first-of-its-kind|no-brainer)",
     "marketing filler"),
    ("vague-declarative", "inflation", 2,
     r"\bthe (?:implications|stakes|consequences|reasons) (?:are|is) (?:significant|high|real|structural|clear)\b",
     "vague declarative; name the specific thing"),
    ("borrowed-authority", "inflation", 2,
     r"\b(?:experts (?:say|agree|argue|believe)|studies show|research shows|observers (?:have )?(?:noted|cited)"
     r"|industry reports|many (?:people|users|customers) (?:say|agree))\b",
     "unnamed authority; cite the source or cut"),
    ("copula-dodge", "inflation", 1,
     r"\b(?:serves as|stands as|functions as|acts as) (?:a|an|the)\b|\bboasts? (?:a|an|over|more)\b",
     "use is, are or has"),
    ("vague-association", "inflation", 1,
     r"\b(?:in connection with|in association with|is associated with)\b",
     "vague link; name the relationship"),
    ("ing-rider", "inflation", 1,
     r", (?:highlighting|underscoring|emphasizing|ensuring|reflecting|symbolizing|showcasing|fostering|cultivating"
     r"|contributing to|paving the way)\b",
     "-ing phrase bolted on for depth"),

    # Filler and hedges
    ("filler-adverb", "filler", 1,
     r"\b(?:simply|really|truly|genuinely|actually|literally|basically|essentially|incredibly|extremely|quietly|deeply"
     r"|fundamentally|inherently|honestly|definitely|absolutely|undoubtedly|surely)\b",
     "filler adverb; cut it"),
    ("just", "filler", 1,
     r"\bjust\b(?! (?:before|after|over|under|outside|inside|north|south|east|west)\b)",
     "'just' as filler"),
    ("very", "filler", 1, r"\bvery\b", "'very' as filler; pick a stronger word or cut"),
    ("essential", "filler", 1, r"\bessential\b", "importance claimed, not shown"),
    ("stacked-hedge", "filler", 2,
     r"\b(?:could potentially|may possibly|might possibly|might arguably|could arguably|it could be argued"
     r"|in some cases,? it may|to some extent)\b",
     "stacked qualifiers"),
    ("transition-opener", "filler", 1,
     r"(?:^|[.!?] )(?:additionally|furthermore|moreover|in conclusion|overall|ultimately|notably|importantly"
     r"|interestingly|crucially|in summary|to summarize),",
     "stock transition; start with the content"),
    ("generic-cta", "filler", 1,
     r"(?:^|(?<=\W))(?:learn more|get started|discover more|find out more|explore (?:now|more)|click here|read more)(?=$|\W)",
     "generic call to action; name what happens"),

    # Punctuation habits
    # A dash alone in a cell ("no data") is not a prose dash, so the pattern needs text on both sides.
    ("em-dash", "punctuation", 2, r"(?<=\S) ?— ?(?=\S)|(?<=\w) -- (?=\w)",
     "em dash; use a comma, colon, period or parentheses"),
    ("spaced-en-dash", "punctuation", 2, r"(?<=\S) – (?=\S)",
     "spaced en dash used as a dash"),
    ("exclamation", "punctuation", 1, r"(?<=[A-Za-z])!(?=\s|$)", "exclamation mark in body copy"),

    # Visual tells that show up in text
    ("arrow", "looks", 1, r"[→⟶➔➜]|(?<=\s)->(?=\s|$)", "decorative arrow in link or button text"),
    ("emoji", "looks", 1, "[\U0001F300-\U0001FAFF✨⭐⚡✅❌]", "emoji as decoration"),
    ("middot-meta", "looks", 1, r"(?<=\S) · (?=\S)", "meta string joined with middle dots"),
]

MD_RULES = [
    ("bold-label-list", "looks", 1, r"^\s*(?:[-*+]|\d+\.)\s+\*\*[^*\n]{1,40}(?::\*\*|\*\*:)",
     "list items with bold labels; turn into prose unless the labels carry information"),
]

CSS_RULES = [
    ("css-uppercase", "looks", 1, r"text-transform\s*:\s*uppercase", "all-caps labels"),
    ("css-default-font", "looks", 1,
     r"(?:font-family|--[\w-]*font[\w-]*)\s*:\s*['\"]?(?:Inter|Roboto|Poppins|Open Sans|Montserrat|Lato|Space Grotesk"
     r"|DM Sans|Plus Jakarta Sans|Geist)\b",
     "default typeface first in the stack"),
    ("css-gradient", "looks", 1, r"(?:linear|radial|conic)-gradient\(", "gradient used as decoration"),
    ("css-glass", "looks", 1, r"backdrop-filter\s*:\s*blur", "frosted-glass effect"),
    ("css-soft-shadow", "looks", 1,
     r"(?:box-shadow|--[\w-]*shadow[\w-]*)\s*:[^;]*rgba\(\s*0\s*,\s*0\s*,\s*0\s*,\s*0?\.(?:0\d*|1\d*)\s*\)",
     "the same soft grey shadow under every box"),
    ("css-entrance", "looks", 1, r"@keyframes\s+(?:fade|slide|reveal|rise)[\w-]*", "scroll-in entrance animation"),
]

ALL_RULES = RULES + MD_RULES + CSS_RULES
SMALL_WORDS = {"a", "an", "and", "as", "at", "but", "by", "for", "from", "in", "into", "nor", "of", "on", "or",
               "per", "the", "to", "up", "via", "vs", "with", "is", "are", "be", "it", "its"}

# ----------------------------------------------------------------------------- extraction

BLOCK_TAGS = {"p", "div", "li", "td", "th", "h1", "h2", "h3", "h4", "h5", "h6", "section", "article", "header",
              "footer", "nav", "tr", "br", "ul", "ol", "dl", "dt", "dd", "form", "label", "button", "option",
              "select", "fieldset", "legend", "table", "main", "aside", "figure", "figcaption", "details",
              "summary", "title", "small", "caption", "hr", "body", "head"}
SKIP_TAGS = {"script", "style", "code", "pre", "kbd", "samp", "q", "blockquote", "textarea", "svg", "template"}
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source",
             "track", "wbr"}
TEXT_ATTRS = {"title", "alt", "placeholder", "aria-label"}
META_NAMES = {"description", "og:description", "og:title", "twitter:title", "twitter:description"}
SEP = " "  # block separator


class Doc:
    """Linted text as a list of pieces (text, line) plus headings for the title-case check."""

    def __init__(self):
        self.pieces = []  # (text, line); SEP pieces split blocks
        self.headings = []  # (text, line, level)

    def add(self, text, line):
        if text:
            self.pieces.append((text, line))

    def block(self):
        if self.pieces and self.pieces[-1][0] != SEP:
            self.pieces.append((SEP, 0))


class HTMLText(HTMLParser):
    def __init__(self, skip_classes):
        super().__init__(convert_charrefs=True)
        self.doc = Doc()
        self.stack = []  # (tag, skipping)
        self.skip_classes = set(skip_classes)
        self.off = False
        self.heading = None  # [level, line, [text]]
        self.eyebrows = []

    def skipping(self):
        return self.off or any(s for _, s in self.stack)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = set((a.get("class") or "").split())
        skip = (tag in SKIP_TAGS or "data-slop-ignore" in a or bool(classes & self.skip_classes))
        line = self.getpos()[0]
        if tag in BLOCK_TAGS:
            self.doc.block()
        if not self.skipping() and any(re.fullmatch(r"eyebrow|kicker|overline|pre-?title|super-?title", c) for c in classes):
            self.eyebrows.append({"line": line, "rule": "eyebrow-class", "category": "looks", "weight": 1,
                                  "message": "eyebrow or kicker label above a heading; cut it or make it a breadcrumb",
                                  "match": f'<{tag} class="{a.get("class")}">'})
        if not self.skipping() and not skip:
            for k in TEXT_ATTRS:
                if a.get(k):
                    self.doc.block()
                    self.doc.add(a[k], line)
                    self.doc.block()
            if tag == "meta" and (a.get("name") or a.get("property") or "").lower() in META_NAMES and a.get("content"):
                self.doc.block()
                self.doc.add(a["content"], line)
                self.doc.block()
        if tag in ("h1", "h2", "h3", "h4") and not self.skipping():
            self.heading = [int(tag[1]), line, []]
        if tag not in VOID_TAGS:
            self.stack.append((tag, skip))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS and self.stack and self.stack[-1][0] == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag in VOID_TAGS:
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break
        if tag in BLOCK_TAGS:
            self.doc.block()
        if tag in ("h1", "h2", "h3", "h4") and self.heading:
            level, line, parts = self.heading
            self.doc.headings.append((" ".join("".join(parts).split()), line, level))
            self.heading = None

    def handle_data(self, data):
        if self.skipping():
            return
        self.doc.add(data, self.getpos()[0])
        if self.heading:
            self.heading[2].append(data)

    def handle_comment(self, data):
        d = data.strip().lower()
        if d.startswith("slop-lint: off"):
            self.off = True
        elif d.startswith("slop-lint: on"):
            self.off = False


def blank(m):
    """Replace a match with spaces, keeping newlines so line numbers survive."""
    return re.sub(r"[^\n]", " ", m.group(0))


def markdown_doc(raw):
    text = raw
    text = re.sub(r"\A---\n.*?\n---\n", blank, text, flags=re.S)
    text = re.sub(r"^(```|~~~).*?^\1[^\n]*$", blank, text, flags=re.S | re.M)
    text = re.sub(r"<!--.*?-->", blank, text, flags=re.S)
    text = re.sub(r"`[^`\n]+`", blank, text)
    text = re.sub(r"\]\([^)\n]*\)", lambda m: "]" + " " * (len(m.group(0)) - 1), text)
    text = re.sub(r"<https?://[^>\s]+>", blank, text)
    text = re.sub(r"^[ \t]*>.*$", blank, text, flags=re.M)  # blockquotes are quotations
    doc = Doc()
    headings = []
    for n, line in enumerate(text.split("\n"), 1):
        if not line.strip():
            doc.block()
            continue
        h = re.match(r"^(#{1,4})\s+(.*)$", line)
        if h:
            headings.append((h.group(2).strip(), n, len(h.group(1))))
            doc.block()
        if re.match(r"^\s*([-*+]|\d+\.|\|)\s", line):
            doc.block()
        doc.add(line + "\n", n)
    doc.headings = headings
    return doc, text


def text_doc(raw):
    doc = Doc()
    for n, line in enumerate(raw.split("\n"), 1):
        if not line.strip():
            doc.block()
        else:
            doc.add(line + "\n", n)
    return doc


# ----------------------------------------------------------------------------- matching

def compile_rules(rules, ignore):
    return [(rid, cat, w, re.compile(p, re.I | re.M), msg) for rid, cat, w, p, msg in rules if rid not in ignore]


def blocks(doc):
    """Yield (normalized_text, [line for each char]) per block."""
    chars, lines = [], []
    for text, line in doc.pieces + [(SEP, 0)]:
        if text == SEP:
            if chars:
                s = "".join(chars)
                yield s, lines
            chars, lines = [], []
            continue
        ln = line
        for ch in text:
            if ch.isspace():
                if chars and chars[-1] != " ":
                    chars.append(" ")
                    lines.append(ln)
            else:
                chars.append(ch)
                lines.append(ln)
            if ch == "\n":
                ln += 1
    return


QUOTE_RE = re.compile(r"“[^“”]{0,800}”")


def lint_blocks(doc, rules, ignored_lines):
    hits, words = [], 0
    for text, lines in blocks(doc):
        text = QUOTE_RE.sub(lambda m: " " * len(m.group(0)), text)
        words += len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’-]*", text))
        for rid, cat, w, rx, msg in rules:
            for m in rx.finditer(text):
                line = lines[min(m.start(), len(lines) - 1)]
                if line in ignored_lines:
                    continue
                hits.append({"line": line, "rule": rid, "category": cat, "weight": w, "message": msg,
                             "match": m.group(0).strip()[:80]})
    return hits, words


HEADING_RULES = [
    ("title-case", "looks", "heading in Title Case; use sentence case"),
    ("heading-question", "staging", "question as a heading; name what the section holds"),
    ("heading-and-why", "staging", "two-part 'X, and why' heading; name what the section holds"),
]


def heading_hits(doc, ignored_lines, ign):
    out = []
    for text, line, level in doc.headings:
        if line in ignored_lines:
            continue
        found = []
        words = re.findall(r"[A-Za-z][A-Za-z'’-]*", text)
        content = [x for x in words if x.lower() not in SMALL_WORDS]
        if len(content) >= 3 and all(x[0].isupper() for x in content) and not all(x.isupper() for x in content):
            found.append("title-case")
        if text.rstrip().endswith("?") or re.search(r"\?\s+\S", text):
            found.append("heading-question")
        if re.search(r",\s+and\s+(?:why|how|what|where|when|who|the)\b|\band why$", text, re.I):
            found.append("heading-and-why")
        for rid, cat, msg in HEADING_RULES:
            if rid in found and rid not in ign:
                out.append({"line": line, "rule": rid, "category": cat, "weight": 1,
                            "message": f"h{level}: {msg}", "match": text[:80]})
    return out


def ignored(raw):
    """Line numbers excluded by slop-lint: ignore / off / on markers."""
    out, off = set(), False
    for n, line in enumerate(raw.split("\n"), 1):
        low = line.lower()
        if "slop-lint: off" in low:
            off = True
        if off or "slop-lint: ignore" in low:
            out.add(n)
        if "slop-lint: on" in low:
            off = False
    return out


def lint_css(raw, rules, ignored_lines):
    text = re.sub(r"/\*.*?\*/", blank, raw, flags=re.S)
    hits = []
    for rid, cat, w, rx, msg in rules:
        for m in rx.finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            if line not in ignored_lines:
                hits.append({"line": line, "rule": rid, "category": cat, "weight": w, "message": msg,
                             "match": m.group(0).strip()[:80]})
    for m in re.finditer(r"(?:background(?:-color)?|--[\w-]*(?:bg|background|paper|page|cream)[\w-]*)\s*:\s*#([0-9a-f]{6})\b",
                         text, re.I):
        r, g, b = (int(m.group(1)[i:i + 2], 16) for i in (0, 2, 4))
        line = text.count("\n", 0, m.start()) + 1
        if r >= 0xF0 and g >= 0xEA and 0xD0 <= b <= 0xF2 and r - b >= 4 and line not in ignored_lines:
            hits.append({"line": line, "rule": "css-cream", "category": "looks", "weight": 1,
                         "message": "warm cream page background, the commonest generated-site palette",
                         "match": m.group(0)[:80]})
    return hits, 0


def lint_file(path, args):
    raw = open(path, encoding="utf-8", errors="replace").read()
    ext = os.path.splitext(path)[1].lower()
    ign = set(args.ignore)
    skip_lines = ignored(raw)
    looks = not args.no_looks
    base = [r for r in RULES if looks or r[1] != "looks"]
    if ext == ".css":
        if not looks:
            return [], 0
        return lint_css(raw, compile_rules(CSS_RULES, ign), skip_lines)
    extra = []
    if ext in (".html", ".htm"):
        parser = HTMLText(args.skip_class)
        parser.feed(raw)
        parser.close()
        doc = parser.doc
        if looks and "eyebrow-class" not in ign:
            extra += [h for h in parser.eyebrows if h["line"] not in skip_lines]
    elif ext in (".md", ".markdown"):
        doc, stripped = markdown_doc(raw)
        if looks:
            for rid, cat, w, rx, msg in compile_rules(MD_RULES, ign):
                for m in rx.finditer(stripped):
                    line = stripped.count("\n", 0, m.start()) + 1
                    if line not in skip_lines:
                        extra.append({"line": line, "rule": rid, "category": cat, "weight": w, "message": msg,
                                      "match": m.group(0).strip()[:80]})
    else:
        doc = text_doc(raw)
    hits, words = lint_blocks(doc, compile_rules(base, ign), skip_lines)
    heads = heading_hits(doc, skip_lines, ign | (set() if looks else {"title-case"}))
    return extra + hits + heads, words


# ----------------------------------------------------------------------------- CLI

EXTS = (".html", ".htm", ".md", ".markdown", ".txt", ".css")


def expand(paths):
    out = []
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs[:] = sorted(d for d in dirs if not d.startswith(".") and d != "node_modules")
                out += [os.path.join(root, f) for f in sorted(files)
                        if f.lower().endswith(EXTS) and not re.search(r"licen[cs]e|copying", f, re.I)]
        elif any(c in p for c in "*?["):
            out += sorted(glob.glob(p, recursive=True))
        elif os.path.exists(p):
            out.append(p)
        else:
            print(f"slop_lint: no such file: {p}", file=sys.stderr)
    seen, uniq = set(), []
    for p in out:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq


def verdict(score, density):
    if score == 0:
        return "clean"
    if density < 1.0:
        return "near-clean"
    if density < 3.0:
        return "needs work"
    return "rewrite"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Flag AI-sounding phrases and patterns in copy.")
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--ignore", default="", help="comma-separated rule ids to skip")
    ap.add_argument("--skip-class", action="append", default=[])
    ap.add_argument("--no-looks", action="store_true")
    ap.add_argument("--max-score", type=float)
    ap.add_argument("--max-density", type=float)
    ap.add_argument("--list-rules", action="store_true")
    args = ap.parse_args(argv)
    args.ignore = [x.strip() for x in args.ignore.split(",") if x.strip()]

    if args.list_rules:
        for rid, cat, w, _, msg in ALL_RULES + [(rid, cat, 1, "", msg) for rid, cat, msg in HEADING_RULES] + [
                ("eyebrow-class", "looks", 1, "", "eyebrow or kicker label above a heading"),
                ("css-cream", "looks", 1, "", "warm cream page background")]:
            print(f"{rid:20} {cat:12} {w}  {msg}")
        return 0
    files = expand(args.paths)
    if not files:
        ap.error("give at least one file, directory or glob")

    results, total_words = [], 0
    for f in files:
        hits, words = lint_file(f, args)
        total_words += words
        for h in sorted(hits, key=lambda h: (h["line"], h["rule"])):
            results.append({"file": f, **h})
    score = sum(h["weight"] for h in results)
    density = score / total_words * 1000 if total_words else float(score)
    summary = {"files": len(files), "words": total_words, "hits": len(results), "score": score,
               "density": round(density, 2), "verdict": verdict(score, density)}

    if args.json:
        print(json.dumps({"summary": summary, "hits": results}, indent=1, ensure_ascii=False))
    elif args.summary:
        by_rule = {}
        for h in results:
            r = by_rule.setdefault(h["rule"], {"n": 0, "score": 0, "message": h["message"], "examples": {}})
            r["n"] += 1
            r["score"] += h["weight"]
            ex = r["examples"].setdefault(h["match"].lower(), [0, f"{h['file']}:{h['line']}"])
            ex[0] += 1
        for rid, r in sorted(by_rule.items(), key=lambda kv: -kv[1]["score"]):
            print(f"{r['score']:5}  {rid} ({r['n']} hits): {r['message']}")
            for text, (n, where) in sorted(r["examples"].items(), key=lambda kv: -kv[1][0])[:4]:
                print(f"         {n:4}x \"{text}\"  e.g. {where}")
        by_file = {}
        for h in results:
            by_file[h["file"]] = by_file.get(h["file"], 0) + h["weight"]
        if by_file:
            print("\nhighest-scoring files:")
            for f, s in sorted(by_file.items(), key=lambda kv: -kv[1])[:10]:
                print(f"{s:5}  {f}")
    else:
        for h in results:
            print(f"{h['file']}:{h['line']}: [{h['rule']}] {h['message']}: \"{h['match']}\"")
    if not args.json:
        print(f"\nslop score {score} ({summary['density']:.2f} per 1,000 words, {total_words:,} words, "
              f"{len(results)} hits, {len(files)} files): {summary['verdict']}")

    if args.max_score is not None and score > args.max_score:
        return 1
    if args.max_density is not None and density > args.max_density:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
