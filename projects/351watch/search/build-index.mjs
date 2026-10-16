// Build the static full-text search index (Pagefind) from data/search/**/*.jsonl.
//
//   node search/build-index.mjs <data/search dir> <output dir, e.g. .vercel/output/static/pagefind>
//
// Runs at deploy time (site/vercel-build.sh). Every row becomes one Pagefind record; the
// browser (site/search.js) downloads only the index chunks and result fragments a query
// needs, so a search costs nothing on the server. Records carry:
//   meta     title, town, state, board, board_key, date, topics, town_url
//   filters  state ("MA"), town ("MA:Carver"), board (board_key), topic, date (YYYY-MM-DD)
//   sort     date (meeting date; undated documents have none)
// plus words.txt, the spelling vocabulary search.js loads only to correct a misspelled query.
import { createHash } from "node:crypto";
import { readFileSync, readdirSync, rmSync, statSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { close, createIndex } from "pagefind";

const STATE_NAMES = { MA: "Massachusetts", NY: "New York", RI: "Rhode Island", CT: "Connecticut", NH: "New Hampshire",
  VT: "Vermont", ME: "Maine", NJ: "New Jersey", PA: "Pennsylvania" };

const [dataDir, outDir] = process.argv.slice(2);
if (!dataDir || !outDir) {
  console.error("usage: node build-index.mjs <data/search dir> <output dir>");
  process.exit(2);
}

// Same rule as build.py: lowercase, spaces -> "-", apostrophes dropped.
const slugify = (name) => name.toLowerCase().replace(/['’]/g, "").replace(/\s+/g, "-");

function displayTitle(row) {
  const t = (row.title || "").replace(/\s*\(pdf\)\s*$/i, "").replace(/\s+/g, " ").trim();
  // Link text some listings use instead of a title.
  if (!t || /^(copy document link|download|view|click here|pdf|documents?)$/i.test(t)) return `${row.board || "Meeting"} agenda`;
  return t;
}

function* jsonlFiles(dir) {
  for (const name of readdirSync(dir).sort()) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) yield* jsonlFiles(p);
    else if (name.endsWith(".jsonl")) yield p;
  }
}

// One record per distinct document: the same link listed twice, or the same text posted under
// several URLs in one town (re-posts, listing pages), is indexed once, keeping the latest meeting.
const best = new Map();
let rows = 0;
// Agendas a town replaced with a new file (data/search/replaced.json, written by the daily crawl) are not indexed.
let replaced = new Set();
try {
  replaced = new Set(JSON.parse(readFileSync(`${dataDir}/replaced.json`, "utf8")));
} catch (err) {
  replaced = new Set();
}
for (const file of jsonlFiles(dataDir)) {
  for (const line of readFileSync(file, "utf8").split("\n")) {
    if (!line.trim()) continue;
    const row = JSON.parse(line);
    rows++;
    if (!row.text || !(row.source_url || row.url)) continue;
    if (replaced.has(row.url) || replaced.has(row.source_url)) continue;
    const key = `${row.state}|${row.town}|${createHash("sha1").update(row.text).digest("hex")}`;
    const prev = best.get(key);
    if (!prev || (row.meeting_date || "") > (prev.meeting_date || "")) best.set(key, row);
  }
}

// A board's day posted more than once (an agenda, then a revised one, then a cancellation notice): the newest
// posting is the one to find, so the earlier ones go when any title says revised, amended, updated or cancelled.
{
  const byDay = new Map();
  for (const [key, row] of best) {
    if (!row.meeting_date || !row.board_key) continue;
    const day = `${row.state}|${row.town}|${row.board_key}|${row.meeting_date}`;
    if (!byDay.has(day)) byDay.set(day, []);
    byDay.get(day).push([key, row]);
  }
  for (const group of byDay.values()) {
    if (group.length < 2 || !group.some(([, r]) => /cancel|revis|amend|updat/i.test(r.title || ""))) continue;
    group.sort((a, b) => (b[1].first_seen || "").localeCompare(a[1].first_seen || ""));
    for (const [key] of group.slice(1)) best.delete(key);
  }
}

const { index, errors } = await createIndex({ forceLanguage: "en" });
if (!index) throw new Error(`pagefind: ${errors.join("; ")}`);
const seen = new Set();
const docFreq = new Map();
for (const row of best.values()) {
  const link = row.source_url || row.url;
  if (seen.has(link)) continue;
  seen.add(link);
  const title = displayTitle(row);
  const filters = { state: [row.state] };
  if (row.town) filters.town = [`${row.state}:${row.town}`];
  if (row.board_key) filters.board = [row.board_key];
  if (row.topics?.length) filters.topic = row.topics;
  if (row.meeting_date) filters.date = [row.meeting_date];
  const res = await index.addCustomRecord({
    url: link,
    // Title, town and board lead the content, so a town or board name ranks its own documents.
    // "e¢" and "¢" are bullets the OCR misread; they would show up in excerpts.
    content: `${title}. ${row.town}, ${STATE_NAMES[row.state] || row.state}. ${row.board || ""}. ${row.text.replace(/(^|\s)[e€o]?¢\s*/g, "$1")}`,
    language: "en",
    meta: {
      title,
      town: row.town || "",
      state: row.state,
      board: row.board || "",
      board_key: row.board_key || "",
      date: row.meeting_date || "",
      topics: (row.topics || []).join(","),
      town_url: row.town ? `/${row.state.toLowerCase()}/${slugify(row.town)}` : "",
    },
    filters,
    sort: row.meeting_date ? { date: row.meeting_date } : {},
  });
  if (res.errors.length) throw new Error(`pagefind: ${link}: ${res.errors.join("; ")}`);
  for (const w of new Set(row.text.toLowerCase().match(/[a-z]{4,24}/g) || [])) docFreq.set(w, (docFreq.get(w) || 0) + 1);
}
const written = await index.writeFiles({ outputPath: outDir });
if (written.errors.length) throw new Error(`pagefind: ${written.errors.join("; ")}`);
await close();

// Pagefind's prebuilt UI bundles are not used (site/search.js talks to pagefind.js directly).
for (const name of readdirSync(outDir)) {
  if (/^pagefind-(ui|component-ui|modular-ui|highlight)\.(js|css)$/.test(name)) rmSync(join(outDir, name));
}

// Spelling vocabulary for search.js: words in at least 3 documents, most frequent first.
const words = [...docFreq].filter(([, n]) => n >= 3).sort((a, b) => b[1] - a[1] || (a[0] < b[0] ? -1 : 1));
writeFileSync(join(outDir, "words.txt"), words.map(([w]) => w).join("\n") + "\n");
console.log(`search index: ${seen.size} documents from ${rows} rows, ${words.length} vocabulary words -> ${outDir}`);
