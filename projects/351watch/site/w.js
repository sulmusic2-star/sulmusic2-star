// /w/<key> (or /w?id=<key>): one alert list. A private key shows everything, including the
// private and share links, the daily message, edit and delete. A share (read-only) key shows the
// items and feeds only. ?new=1 after creating shows the "save your private link" banner.
(() => {
  const app = document.getElementById('wl-app');
  if (!app) return;
  const $ = (id) => document.getElementById(id);
  const TOPICS = JSON.parse(app.dataset.topics || '{}'); // key: [label, phrase, plural]
  const ORDER = JSON.parse(app.dataset.order || '[]');
  const TAGS = JSON.parse(app.dataset.tags || '{}'); // topic key: label shown on each item
  const MENTION = JSON.parse(app.dataset.mention || '{}'); // topic key: words for "the agenda mentions …"
  const BASE = app.dataset.base || location.origin; // the site's public address, for share links
  const slug = (name) => String(name).toLowerCase().replace(/['’]/g, '').replace(/\s+/g, '-');
  const KINDS = { slack: 'Slack', teams: 'Microsoft Teams', teams_workflow: 'Microsoft Teams', discord: 'Discord', json: 'your webhook' };
  const PLANS = { beta: 'Free' };
  const pathId = (location.pathname.match(/^\/w\/([A-Za-z0-9_-]{24,64})\/?$/) || [])[1];
  const params = new URLSearchParams(location.search);
  const id = pathId || params.get('id') || '';
  const SITE = document.title.split(' | ').pop(); // the product name, from the title build.py wrote
  let homeTown = null; // the alert list's home town, when the API reports it
  let LINES = {}; // /data/lines.json: {lines: {id: [line, quote, note, kind, key, board, rank, number, subject]}, briefs: {id: brief}, new: [id, ...]}
  const BRIEF_RANK = { vote: 10, adopted: 10, hearing: 20, continued: 20, extension: 30, other: 40, discussion: 40, withdrawn: 50 };
  const BRIEF_STAGE = { vote: 'Vote', adopted: 'Final vote', hearing: 'Hearing', continued: 'Postponed', extension: 'Extension', other: '', discussion: 'Discussion', withdrawn: 'Withdrawn' };
  let NEW = new Set();
  const today = new Intl.DateTimeFormat('en-CA', { timeZone: 'America/New_York', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date());

  const el = (tag, attrs = {}, ...children) => {
    const node = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === 'class') node.className = v;
      else if (k === 'text') node.textContent = v;
      else node.setAttribute(k, v);
    }
    node.append(...children.filter((c) => c !== null && c !== undefined && c !== false));
    return node;
  };
  const fmtDate = (iso) => {
    if (!iso) return '';
    const d = new Date(iso.length === 10 ? `${iso}T12:00:00Z` : iso);
    return Number.isNaN(d.getTime()) ? iso : d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', timeZone: iso.length === 10 ? 'UTC' : 'America/New_York' });
  };
  const dayLabel = (iso) => {
    const d = new Date(`${iso.slice(0, 10)}T12:00:00Z`);
    const opts = { weekday: 'short', month: 'short', day: 'numeric', timeZone: 'UTC' };
    if (iso.slice(0, 4) !== today.slice(0, 4)) opts.year = 'numeric';
    return d.toLocaleDateString('en-US', opts).replace(/^(\w{3}),/, '$1'); // "Tue Oct 13", as build.py writes it
  };
  const plural = (n, word) => `${n.toLocaleString('en-US')} ${word}${n === 1 ? '' : 's'}`;
  const joinAnd = (parts) => (parts.length < 3 ? parts.join(' and ') : `${parts.slice(0, -1).join(', ')} and ${parts[parts.length - 1]}`);
  const townPath = (url) => {
    try {
      return new URL(url).pathname;
    } catch {
      return '/towns';
    }
  };

  // Same wording as board_label() in build.py.
  function boardLabel(item) {
    if (item.board_key === 'town_meeting') return 'Town Meeting';
    let b = String(item.board || '').replace(/\s*\([^)]*\)/g, '').replace(/\s+[-–]\s+.*$/, '').replace(/^The\s+/, '').replace(/\s+Meetings?$/, '').trim();
    b = b.replace(/\s*\/.*$/, '').replace(/\s+(?:FY\s?\d{2,4}|Public Hearings?|(?:Meeting\s+)?Agendas?(?:\s*(?:&|and)\s*Minutes)?)$/i, '')
      .replace(/['’]s\s+Office$/, '').replace(/^[\s\-–:]+/, '').replace(/^(\w+), (.+ of)$/, '$2 $1');
    if (b && (b === b.toUpperCase() || b === b.toLowerCase())) b = b.toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase()).replace(/ Of /g, ' of ').replace(/ And /g, ' and ');
    return b.trim() || 'town board';
  }
  function meetingBoard(m) {
    if (m.source === 'massdep_wetlands') return 'Wetlands filing to the state';
    if (m.board_key === 'town_meeting') return 'Town Meeting warrant';
    return m.board.charAt(0).toUpperCase() + m.board.slice(1);
  }
  const HEARING_NOTE = 'Public hearing.';
  const SPEAK_TEXT = 'Yes. Anyone can attend a public hearing and ask to speak. You can also send written comments to the board through the town clerk before the meeting. Ask the clerk about sign-up rules and time limits.';
  const SUBJECT_NOUN = { data_center: 'data centers', battery_storage: 'battery storage', solar: 'solar', clean_energy_siting: 'clean-energy permit rules',
    zoning_amendment: 'zoning', '40b_comprehensive_permit': 'affordable housing', wireless_telecom: 'cell towers', wetlands_filing: 'wetlands' };

  // The plain line for one item (from /data/lines.json, written by item_text() in build.py). An
  // item newer than that file says which topic its agenda mentions, with its own agenda text.
  function lineFor(it) {
    const known = LINES.lines && LINES.lines[it.id];
    const b = LINES.briefs && LINES.briefs[it.id];
    if (b && known) { // a verified written brief, as brief_text() in build.py
      return { say: (b.line || b.what || known[0]).trim(), quote: b.quote || known[1], note: '', kind: 'brief', key: known[4] || '',
        who: known[5] || '', rank: BRIEF_RANK[b.action || 'other'] || 40, no: known[7] || '', subj: known[8] || '', brief: b,
        stage: known[9] || BRIEF_STAGE[b.action || 'other'] || '', facts: [b.where, b.size, b.who].filter(Boolean) };
    }
    if (known) {
      return { say: known[0], quote: known[1], note: known[2] || '', kind: known[3] || 'act', key: known[4] || '', who: known[5] || '',
        rank: Number(known[6] ?? 60), no: known[7] || '', subj: known[8] || '', stage: known[9] || '', facts: known[10] || [] };
    }
    const who = it.board_key === 'town_meeting' ? 'Town Meeting' : `The ${boardLabel(it).replace(/^the /i, '')}`;
    const whose = it.board_key === 'town_meeting' ? 'The Town Meeting warrant' : `${who} agenda`;
    const first = order(it.topics || [])[0];
    return { say: `Mentions ${SUBJECT_NOUN[first] || 'our topics'}.`, quote: String(it.snippet || '').slice(0, 300), note: '',
      kind: 'mention', key: '', who, rank: 70, no: '', subj: first || '', stage: '', facts: [] };
  }
  const order = (topics) => [...new Set(topics)].sort((a, b) => (ORDER.includes(a) ? ORDER.indexOf(a) : 99) - (ORDER.includes(b) ? ORDER.indexOf(b) : 99));
  function tagText(topics) {
    const tags = order(topics).map((t) => TAGS[t] || t.replace(/_/g, ' '));
    return tags.length ? [tags[0], ...tags.slice(1).map((t) => t.toLowerCase())].join(', ') : '';
  }
  const normQ = (q) => String(q || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
  // As overlaps() in build.py: the same passage, or two cuts of one passage.
  const overlaps = (q, quotes) => {
    const a = normQ(q);
    return quotes.some((o) => {
      const b = normQ(o);
      return a.slice(0, 80) === b.slice(0, 80) || (a.length > 40 && b.includes(a.slice(6, 66))) || (b.length > 40 && a.includes(b.slice(6, 66)));
    });
  };

  // Items grouped by meeting (town, board, day), as group_meetings() does in build.py.
  function group(items) {
    const meetings = new Map();
    for (const it of items) {
      const d = (it.meeting_date || '').slice(0, 10);
      const dep = it.source === 'massdep_wetlands';
      const key = `${it.state}:${it.town}|${dep}|${it.board_key || boardLabel(it)}|${d}`;
      if (!meetings.has(key)) {
        const at = (LINES.at && LINES.at[it.source_url]) || ['', ''];
        meetings.set(key, { state: it.state, town: it.town, town_url: it.town_url, board: boardLabel(it), board_key: it.board_key,
          source: it.source, date: d, lines: new Map(), docs: [], found: it.first_seen || '', time: at[0], place: at[1],
          id: `m-${slug(`${it.town}-${boardLabel(it)}-${d || 'warrant'}`)}` });
      }
      const m = meetings.get(key);
      const t = lineFor(it);
      if (!m.lines.has(t.say)) {
        m.lines.set(t.say, { quotes: [], topics: [], isNew: false, note: t.note, kind: t.kind, key: t.key, who: t.who, rank: t.rank,
          no: t.no, subj: t.subj, seen: it.first_seen || '', url: it.source_url, brief: t.brief || null, stage: t.stage || '', facts: t.facts || [] });
      }
      const entry = m.lines.get(t.say);
      const all = [...m.lines.values()].flatMap((v) => v.quotes);
      if (t.quote && !overlaps(t.quote, all)) entry.quotes.push(t.quote);
      for (const x of it.topics || []) if (!entry.topics.includes(x)) entry.topics.push(x);
      entry.isNew = entry.isNew || NEW.has(it.id);
      entry.note = entry.note || t.note;
      if (!m.docs.some((x) => x.url === it.source_url)) {
        m.docs.push({ url: it.source_url, pdf: /\.pdf$/i.test(String(it.source_url).split('?')[0]) || /\(pdf\)/i.test(it.document_title || '') });
      }
      if (it.first_seen && (!m.found || it.first_seen < m.found)) m.found = it.first_seen;
    }
    for (const m of meetings.values()) m.lines = tidy(m.lines);
    return [...meetings.values()];
  }

  // As tidy_lines() in build.py: one line per agenda item (the most important reading wins), a moratorium
  // absorbs other items on its subject, no sentence inside another, a quote shown once, most important first.
  function tidy(lines) {
    const core = (s) => s.toLowerCase().replace(' (continued from an earlier meeting)', '').replace(/\.$/, '')
      .replace(' will vote on ', ' will discuss ').replace('zoning ordinance', 'zoning bylaw');
    const merge = (into, e) => {
      for (const q of e.quotes) if (!overlaps(q, into.quotes)) into.quotes.push(q);
      for (const t of e.topics) if (!into.topics.includes(t)) into.topics.push(t);
      into.isNew = into.isNew || e.isNew;
      into.note = into.note || e.note;
      into.stage = into.stage || e.stage || '';
      if (!(into.facts || []).length) into.facts = e.facts || [];
    };
    const sorted = [...lines.keys()].sort((a, b) => lines.get(a).rank - lines.get(b).rank
      || (lines.get(a).kind !== 'brief') - (lines.get(b).kind !== 'brief')
      || (lines.get(a).kind !== 'act') - (lines.get(b).kind !== 'act') || b.length - a.length);
    const named = new Map();
    const groups = new Map();
    for (const k of sorted) {
      const key = lines.get(k).key;
      if (!key) named.set(k, lines.get(k));
      else {
        if (!groups.has(key)) groups.set(key, []);
        groups.get(key).push(k);
      }
    }
    const ABOUT = /^(.* about )([^“:]+)\.$/;
    for (const keys of groups.values()) {
      const best = lines.get(keys[0]);
      let say = keys[0];
      const lead = best.kind === 'brief' ? null : say.match(ABOUT);
      if (lead) {
        const subjects = [lead[2]];
        for (const k of keys.slice(1)) {
          const mm = k.match(ABOUT);
          if (mm && mm[1] === lead[1] && !subjects.includes(mm[2])) subjects.push(mm[2]);
        }
        say = `${lead[1]}${joinAnd(subjects)}.`;
      }
      for (const k of keys.slice(1)) merge(best, lines.get(k));
      named.set(say, best);
    }
    for (const k of [...named.keys()].sort((a, b) => named.get(a).rank - named.get(b).rank)) {
      if (!named.has(k) || named.get(k).rank >= 10) continue;
      for (const o of [...named.keys()]) {
        const v = named.get(o);
        if (o !== k && v.rank >= 10 && v.subj === named.get(k).subj && v.kind !== 'list' && v.kind !== 'brief') {
          merge(named.get(k), v);
          named.delete(o);
        }
      }
    }
    const acts = [...named.keys()].filter((k) => named.get(k).kind !== 'mention' && named.get(k).kind !== 'brief');
    for (const short of acts.sort((a, b) => core(a).length - core(b).length)) {
      const longer = acts.find((k) => k !== short && named.has(k) && core(k).includes(core(short)));
      if (longer && named.has(short)) {
        merge(named.get(longer), named.get(short));
        named.delete(short);
      }
    }
    const shown = [];
    const out = [];
    for (const k of [...named.keys()].sort((a, b) => (named.get(a).kind === 'mention') - (named.get(b).kind === 'mention') || named.get(a).rank - named.get(b).rank)) {
      const v = named.get(k);
      if (v.kind === 'mention' && v.quotes.length && v.quotes.every((q) => overlaps(q, shown))) continue;
      if (v.kind === 'mention' && !v.quotes.length && named.size > 1) continue;
      shown.push(...v.quotes);
      out.push([k, v]);
    }
    return new Map(out.sort((a, b) => a[1].rank - b[1].rank));
  }

  // As place_text() in build.py.
  const placeText = (p) => (p === 'online' ? 'Online meeting' : p.replace(/ or online$/, ', or join online'));
  const whenText = (m) => (m.date ? dayLabel(m.date) + (m.time ? `, ${m.time}` : '') : '');
  const SPEAK = LINESPEAK();
  function LINESPEAK() { return (LINES && LINES.speak) || 'Public hearing: anyone can speak; written comments go to the town clerk before the meeting.'; }
  const factsText = (e) => {
    const parts = [tagText(e.topics), ...(e.facts || []).map(String)];
    const seen = new Set();
    return parts.filter((x) => x && !seen.has(x.toLowerCase()) && seen.add(x.toLowerCase())).join(' \u00B7 ');
  };

  // One meeting, as meeting_html() renders it in build.py: the meeting line (town \u00B7 board \u00B7 day \u00B7 place), per item
  // one line that starts with the stage, a grey facts line with the stage word, then one source link.
  function meetingNode(m, maxLines) {
    const dep = m.source === 'massdep_wetlands';
    const what = dep ? 'filing' : (m.board_key === 'town_meeting' ? 'warrant' : 'agenda');
    const tid = `${m.state}:${m.town}`;
    const next = homeTown && tid !== homeTown ? ` (next to ${homeTown.split(':').slice(1).join(':')})` : '';
    const when = whenText(m);
    const place = m.place && !dep && !(m.board_key === 'town_meeting' && m.place === 'online') ? placeText(m.place) : '';
    const head = el('p', { class: 'meet-head', 'data-slop-ignore': '' },
      el('span', { class: 'meet-town' }, el('a', { href: townPath(m.town_url), text: m.town + (m.state && m.state !== 'MA' ? `, ${m.state}` : '') }), next),
      el('span', { text: meetingBoard(m) }),
      m.date ? el('span', { class: 'meet-day' }, el('time', { datetime: m.date, text: when }))
        : (m.board_key === 'town_meeting' ? el('span', { class: 'meet-day', text: 'Date not found on the warrant' }) : null),
      place ? el('span', { class: 'meet-place', text: place }) : null);
    const lineNode = ([text, e]) => {
      const b = e.brief;
      const facts = factsText(e);
      const soon = e.stage === 'Hearing' && m.date && (Date.parse(`${m.date}T12:00:00Z`) - Date.parse(`${today}T12:00:00Z`)) / 86400000 <= 2 && m.date >= today;
      return el('li', { class: `line${b ? ' brief' : ''}` },
        el('p', { class: 'line-say' }, e.isNew ? el('span', { class: 'badge-new', text: 'New' }) : null, e.isNew ? ' ' : null, text),
        b && b.what && normQ(b.what) !== normQ(text) ? el('p', { class: 'brief-what', text: b.what }) : null,
        facts || e.stage ? el('p', { class: 'line-facts' }, facts, e.stage ? el('span', { class: `stage${soon ? ' soon' : ''}`, text: e.stage }) : null) : null);
    };
    const where = `${m.town} ${meetingBoard(m)}, ${m.date ? dayLabel(m.date) : 'no date'}`;
    const d = m.docs[0];
    const link = d ? el('a', { class: 'item-link', href: d.url, rel: 'nofollow noopener', target: '_blank' },
      `${what.charAt(0).toUpperCase()}${what.slice(1)}${d.pdf ? ' (PDF)' : ''}`, el('span', { class: 'sr-only', text: `: ${where}` })) : null;
    // The speak line only for a hearing that is still on: not one postponed, canceled or withdrawn.
    const entries = [...m.lines.values()].filter((v) => !/^(Postponed|Canceled|Withdrawn)/.test(v.stage || ''));
    // The brief's own rule from the agenda when the writer found one; otherwise the general line.
    const rules = [];
    for (const v of entries) {
      const b = v.brief || {};
      if (b.can_speak === true && b.how_to_speak && !rules.includes(b.how_to_speak)) rules.push(b.how_to_speak);
    }
    const speakText = rules.length ? rules.slice(0, 2).join(' ') : SPEAK;
    const speak = rules.length > 0 || entries.some((v) => (v.brief && v.brief.can_speak === true) || (v.stage === 'Hearing' && !(v.brief && v.brief.can_speak === false)));
    const all = [...m.lines];
    const shown = maxLines ? all.slice(0, maxLines) : all;
    return el('li', { class: 'meeting', id: m.id }, head,
      el('ul', { class: 'lines' }, ...shown.map(lineNode)),
      shown.length < all.length ? el('p', { class: 'more-items', text: `and ${plural(all.length - shown.length, 'more item')}` }) : null,
      el('p', { class: 'meet-src' }, speak ? el('span', { class: 'speak-line', text: speakText }) : null, link));
  }

  // The first few meetings, the rest behind one "Show more", as meeting_list() does in build.py.
  function meetingList(meetings, shown, more) {
    const nodes = [el('ol', { class: 'meetings' }, ...meetings.slice(0, shown).map(meetingNode))];
    const rest = meetings.slice(shown);
    if (rest.length) {
      nodes.push(el('details', { class: 'more' }, el('summary', { text: `${more} (${rest.length})` }),
        el('ol', { class: 'meetings' }, ...rest.map(meetingNode))));
    }
    return nodes;
  }

  function fail(message, linkText = 'Set up new alerts') {
    $('wl-title').textContent = 'We couldn’t open these alerts';
    document.title = `We couldn’t open these alerts | ${SITE}`;
    const box = $('wl-error');
    box.replaceChildren(document.createTextNode(`${message} `), el('a', { href: '/watch', text: linkText }));
    box.hidden = false;
    $('wl-body').hidden = true;
  }

  async function api(method, url) {
    const res = await fetch(url, { method, cache: 'no-store', headers: { Accept: 'application/json' } });
    const data = await res.json().catch(() => ({}));
    if (!res.ok || data.ok === false) {
      const err = new Error(data.error || 'Something went wrong on our end. Try again in a minute.');
      err.status = res.status;
      throw err;
    }
    return data;
  }

  function copyButton(getText, label) {
    const button = el('button', { type: 'button', class: 'btn small quiet', text: 'Copy' });
    button.setAttribute('aria-label', label);
    button.addEventListener('click', async () => {
      const text = getText();
      try {
        await navigator.clipboard.writeText(text);
      } catch {
        const tmp = el('textarea', { class: 'sr-only' });
        tmp.value = text;
        document.body.append(tmp);
        tmp.select();
        document.execCommand('copy');
        tmp.remove();
      }
      button.textContent = 'Copied';
      setTimeout(() => { button.textContent = 'Copy'; }, 1800);
    });
    return button;
  }

  function linkField(fieldId, url, label) {
    const input = el('input', { id: fieldId, type: 'text', readonly: '', spellcheck: 'false', 'aria-label': label });
    input.value = url;
    input.addEventListener('focus', () => input.select());
    return [input, copyButton(() => url, `Copy ${label.toLowerCase()}`)];
  }

  function renderItems(items) {
    const byDate = (dir) => (a, b) => dir * a.meeting_date.localeCompare(b.meeting_date) || a.town.localeCompare(b.town);
    const up = group(items.filter((i) => i.meeting_date && i.meeting_date >= today).sort(byDate(1)));
    const past = group(items.filter((i) => i.meeting_date && i.meeting_date < today).sort(byDate(-1)));
    const undated = group(items.filter((i) => !i.meeting_date));
    $('items-upcoming').replaceChildren(...(up.length ? meetingList(up, 5, 'More coming up')
      : [el('p', { class: 'empty', text: 'Nothing on these topics in the agendas posted so far.' })]));
    $('items-lead').textContent = '';
    $('items-past').replaceChildren(...meetingList(past, 5, 'Show older'));
    $('past-summary').textContent = `Earlier meetings (${past.length})`;
    $('past-wrap').hidden = !past.length;
    $('items-undated').replaceChildren(...meetingList(undated, 5, 'Show more'));
    $('undated-wrap').hidden = !undated.length;
  }

  function renderFeeds(links) {
    $('webcal-link').href = links.ics.replace(/^https?:/, 'webcal:');
    $('rss-link').href = links.rss;
    $('json-link').href = links.json;
    const rows = [
      ['Calendar', links.ics, 'In Google Calendar or Outlook on the web, add a calendar “from URL” and paste this.'],
      ['RSS', links.rss, 'For news reader apps.'],
    ];
    $('feed-rows').replaceChildren(...rows.map(([label, url, help], n) =>
      el('div', { class: 'feed-row' }, el('label', { for: `feed-${n}`, text: `${label} link` }), ...linkField(`feed-${n}`, url, `${label} link`), el('small', { text: help }))));
  }

  function renderLinks(wl, created) {
    $('private-row').replaceChildren(...linkField(created ? 'private-link-again' : 'private-link', wl.links.page, 'Private link'));
    $('share-row').replaceChildren(...linkField('share-link', wl.links.share, 'Share link'));
    $('links-section').hidden = false;
    if (created) $('created-row').replaceChildren(...linkField('private-link', wl.links.page, 'Private link'));
  }

  // Right after setting up: a short page with how the alerts arrive, one sample, the calendar button and
  // the private link. The full list is one link away.
  function renderCreated(wl, items, emailOn) {
    const mail = wl.email || {};
    const home = homeTown ? homeTown.split(':').slice(1).join(':') : '';
    const others = wl.towns.filter((t) => t !== homeTown).length;
    $('wl-title').textContent = home ? `Alerts on for ${home}${others ? ` and ${others === 1 ? 'the town' : `${others} towns`} next door` : ''}` : `Alerts on: ${wl.name || 'your towns'}`;
    $('wl-summary').textContent = '';
    const how = $('created-how');
    if (mail.configured) {
      how.textContent = `We’ll email ${mail.masked} at most once a day, only when something new is posted.`;
      $('inbox-note').hidden = Boolean(mail.confirmed);
    } else if (emailOn) {
      how.textContent = 'At most one email a day, only when something new is posted. Add your address below to get them by email.';
    } else {
      how.textContent = 'Add these meetings to your calendar; email alerts are coming.';
    }
    const up = group(items.filter((i) => i.meeting_date && i.meeting_date >= today).sort((a, b) => a.meeting_date.localeCompare(b.meeting_date) || a.town.localeCompare(b.town)));
    if (up.length) $('sample').replaceChildren(el('ol', { class: 'meetings' }, meetingNode(up[0], 1)));
    else {
      $('sample-lead').textContent = 'Nothing on these topics is on an agenda yet. You’ll hear from us when something is.';
      $('sample').replaceChildren();
    }
    $('created-cal').href = wl.links.ics.replace(/^https?:/, 'webcal:');
    $('see-all').href = location.pathname;
    $('wl-created').hidden = false;
    $('wl-created').setAttribute('tabindex', '-1');
    $('wl-created').focus();
  }

  // Email (private view only): {configured, available, confirmed, masked, status, resend_available_at}.
  // Offer to add one only when email alerts are on.
  function renderEmail(wl, emailOn) {
    const out = $('email-status');
    const mail = wl.email;
    const edit = el('a', { href: `/watch?edit=${wl.id}` });
    if (mail && mail.configured) {
      edit.textContent = 'Change or remove the address';
      out.replaceChildren(mail.confirmed
        ? `Emails go to ${mail.masked}, at most once a day, only when something new is posted. `
        : `We sent a link to ${mail.masked}. Emails start once you click it. `, edit, '.');
      out.hidden = false;
      const at = mail.resend_available_at ? Date.parse(mail.resend_available_at) : NaN;
      if (!mail.confirmed && !Number.isNaN(at) && at <= Date.now()) {
        const button = el('button', { type: 'button', class: 'btn small quiet', text: 'Send the link again' });
        const said = el('span', { class: 'form-status', role: 'status' });
        button.addEventListener('click', async () => {
          button.disabled = true;
          said.className = 'form-status';
          said.textContent = ' Sending…';
          try {
            await api('POST', `/api/email?action=resend&id=${encodeURIComponent(wl.id)}`);
            said.classList.add('ok');
            said.textContent = ' Sent. Check your inbox and spam folder.';
          } catch (err) {
            said.classList.add('err');
            said.textContent = ` ${err.message}`;
            button.disabled = false;
          }
        });
        out.append(' ', button, said);
      }
    } else if (emailOn || (mail && mail.available)) {
      edit.textContent = 'Add an email address';
      out.replaceChildren('No email address yet. ', edit, '.');
      out.hidden = false;
    }
  }

  function renderWebhook(wl) {
    const status = $('hook-status');
    const hook = wl.webhook;
    $('hook-section').hidden = false;
    if (!hook || !hook.configured) {
      status.replaceChildren('Not posting to a chat app. ', el('a', { href: `/alerts-for-groups?edit=${wl.id}`, text: 'Post to Slack, Teams or Discord' }), '.');
      return;
    }
    const parts = [`New agendas on your topics are posted to ${KINDS[hook.kind] || 'your chat app'} (${hook.masked}) once a day. `];
    const d = wl.last_delivery;
    if (d && d.ok) parts.push(`Last post ${fmtDate(d.at)}: ${plural(d.sent, 'agenda item')}${d.more ? ` and a link to ${d.more} more` : ''}.`);
    else if (d) parts.push(`The last message, on ${fmtDate(d.at)}, failed (${d.error || `HTTP ${d.status}`}). We’ll try again with the next daily run. Check the webhook URL.`);
    else parts.push('Nothing posted yet. We post once a day, only when something new is posted.');
    status.textContent = parts.join('');
    const test = $('hook-test');
    test.hidden = false;
    test.addEventListener('click', async () => {
      const out = $('hook-test-status');
      test.disabled = true;
      out.className = 'form-status';
      out.textContent = 'Sending a test message…';
      try {
        await api('POST', `/api/watchlists?id=${encodeURIComponent(wl.id)}&action=test`);
        out.classList.add('ok');
        out.textContent = 'Test message sent. Check your channel.';
      } catch (err) {
        out.classList.add('err');
        out.textContent = err.message;
      } finally {
        test.disabled = false;
      }
    });
  }

  function renderManage(wl) {
    $('manage-section').hidden = false;
    const plan = PLANS[wl.plan] || wl.plan;
    $('plan-line').replaceChildren(`${plan || 'Free'}. `, el('a', { href: '/pricing', text: 'See what’s included' }), '.');
    $('edit-link').href = `/watch?edit=${wl.id}`;
    const start = $('delete-start');
    const confirmBox = $('delete-confirm');
    start.addEventListener('click', () => {
      confirmBox.hidden = false;
      $('delete-yes').focus();
    });
    $('delete-no').addEventListener('click', () => {
      confirmBox.hidden = true;
      start.focus();
    });
    $('delete-yes').addEventListener('click', async () => {
      const out = $('manage-status');
      $('delete-yes').disabled = true;
      try {
        await api('DELETE', `/api/watchlists?id=${encodeURIComponent(wl.id)}`);
        window.w351.forget(wl.id);
        $('wl-body').hidden = true;
        $('wl-title').textContent = 'Alerts deleted';
        $('wl-summary').textContent = 'Your alerts are deleted. Emails, chat posts and calendar updates have stopped.';
        const box = $('wl-error');
        box.className = 'notice ok';
        box.replaceChildren(el('a', { href: '/watch', text: 'Set up new alerts' }));
        box.hidden = false;
        box.setAttribute('tabindex', '-1');
        box.focus();
      } catch (err) {
        out.className = 'form-status err';
        out.textContent = err.message;
        $('delete-yes').disabled = false;
      }
    });
  }

  async function main() {
    if (!/^[A-Za-z0-9_-]{24,64}$/.test(id)) {
      fail('This link looks cut off. Copy the whole link and try again.');
      return;
    }
    let wl;
    let feed;
    const status = fetch('/api/status', { headers: { Accept: 'application/json' } })
      .then((r) => r.json().catch(() => ({})).then((d) => (r.ok ? d : {}))).catch(() => ({}));
    const linesDoc = fetch('/data/lines.json')
      .then((r) => r.json().catch(() => ({})).then((d) => (r.ok ? d : {}))).catch(() => ({}));
    try {
      [{ watchlist: wl }, feed] = await Promise.all([
        api('GET', `/api/watchlists?id=${encodeURIComponent(id)}`),
        api('GET', `/api/feed?id=${encodeURIComponent(id)}&format=json&fresh=1`),
      ]);
    } catch (err) {
      fail(err.status === 404 ? 'We couldn’t find these alerts. They may have been deleted, or the link may be incomplete.' : err.message);
      return;
    }
    const readonly = wl.readonly === true;
    homeTown = wl.home_town || null;
    const name = wl.name || (readonly ? 'Shared alerts' : 'Your alerts');
    document.title = `${name} | ${SITE}`;
    $('wl-title').textContent = name;
    const townNames = wl.towns.map((t) => t.split(':').slice(1).join(':'));
    const shownTowns = townNames.slice(0, 8).join(', ') + (townNames.length > 8 ? ` and ${townNames.length - 8} more` : '');
    $('wl-summary').textContent = `${plural(wl.towns.length, 'town')}: ${shownTowns}.`;
    window.w351.remember(readonly ? id : wl.id, wl.name, readonly);
    const created = params.get('new') === '1' && !readonly;
    $('wl-body').hidden = created;

    renderFeeds(wl.links);
    LINES = (await linesDoc) || {};
    NEW = new Set(Array.isArray(LINES.new) ? LINES.new : []);
    renderItems(feed.items);
    if (readonly) {
      $('readonly-banner').hidden = false;
      return;
    }
    const emailOn = (await status).email_alerts === true;
    $('settings').hidden = false;
    renderLinks(wl, created);
    renderWebhook(wl);
    renderEmail(wl, emailOn);
    renderManage(wl);
    if (created) {
      renderCreated(wl, feed.items, emailOn);
      return;
    }
    const unconfirmed = params.get('email') === '1' && !(wl.email && wl.email.confirmed);
    if (params.get('email') === '1' && unconfirmed) {
      const banner = $('created-banner');
      banner.replaceChildren(el('b', { text: 'Changes saved.' }), ' Check your inbox and click the link to confirm your address.');
      banner.hidden = false;
      banner.focus();
    }
    if (params.get('email') === 'confirmed') {
      const banner = $('created-banner');
      banner.replaceChildren(el('b', { text: 'Email confirmed.' }),
        ` Alerts will come to ${wl.email && wl.email.masked ? wl.email.masked : 'your inbox'} at most once a day, only when something new is posted.`);
      banner.hidden = false;
      banner.focus();
    }
  }

  main();
})();
