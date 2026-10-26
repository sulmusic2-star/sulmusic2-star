// /trending: the biggest stories coming up. build.py renders the top 20 for everyone. A visitor can add any
// number of towns; the list then shows the stories in those towns (and, when ticked, the towns next to them),
// their own towns first, then by size. The towns stay in this browser.
// One status vocabulary (build.py stage_class / stage_word)
function stageClass(s) {
  if (/^(Postponed|Asks to postpone|Moved|Asked to move)/.test(s)) return 'stage moved';
  if (/^(Canceled|Withdrawn)/.test(s)) return 'stage off';
  if (/^Possible vote/.test(s)) return 'stage maybe';
  if (/^(Vote|Hearing|Final vote|Decided)/.test(s)) return 'stage act';
  return 'stage';
}
function stageWord(s) {
  return s.replace(/^Postponed to /, 'Moved to ').replace(/^Postponed$/, 'Moved').replace(/^Asks to postpone/, 'Asked to move');
}

(() => {
  const all = document.getElementById('trend-all');
  if (!all) return;
  const $ = (id) => document.getElementById(id);
  const mine = $('trend-mine');
  const form = $('story-towns');
  const input = $('story-town');
  const chips = $('story-chips');
  const near = $('story-near');
  const nearRow = $('story-near-row');
  const error = $('story-town-error');
  const filters = $('trend-filters');
  const count = $('trend-count');
  const KEY = 'agendaahead:story-towns';
  const readJSON = (url) => fetch(url).then((r) => r.json().catch(() => ({})).then((d) => (r.ok ? d : {}))).catch(() => ({}));
  const data = Promise.all([readJSON('/data/trending.json'), readJSON('/data/neighbors.json'), readJSON('/data/towns.json')]);
  const plain = (s) => String(s || '').toLowerCase().replace(/[’']/g, '').replace(/[^a-z0-9]+/g, ' ').trim();
  const el = (tag, cls, text) => {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text != null) node.textContent = text;
    return node;
  };
  const dayLabel = (iso) => new Date(`${iso}T12:00:00Z`).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', timeZone: 'UTC' }).replace(/^(\w{3}),/, '$1');
  const relDates = (root) => { if (window.w351 && window.w351.relDates) window.w351.relDates(root); };

  // As story_html() in build.py: a box with the day, town and board, the item's line and the status.
  function storyNode(st, i) {
    const li = el('li', 'row');
    li.dataset.date = st.meeting_date || '';
    li.dataset.topics = (st.topics || []).join(' ');
    const a = el('a');
    a.href = st.href;
    const rank = el('span', 'row-rank', String((Number.isInteger(i) ? i : 0) + 1));
    const when = el('span', 'row-when');
    when.append(el('span', 'row-town', `${st.town}${st.state !== 'MA' ? `, ${st.state}` : ''}`));
    if (st.board) when.append(el('span', '', st.board));
    if (st.meeting_date) {
      const t = el('time', '', dayLabel(st.meeting_date));
      t.dateTime = st.meeting_date;
      const d = el('span'); d.append(t); when.append(d);
    } else when.append(el('span', '', 'Date not set'));
    if (st.new) when.append(el('span', 'is-new', 'New on an agenda'));
    const line = el('span', 'row-line');
    const words = (st.line || st.headline || '').replace(' (no vote listed)', '').replace('; no vote listed)', ')');
    line.append(/[a-z0-9)]\.$/.test(words) && !/\b(St|Rd|Ave|Dr|Ln|Blvd|Mt|No|Art|Sec|Inc|Corp|LLC|Co)\.$/.test(words) ? words.slice(0, -1) : words);
    a.append(rank, when, line);
    const chips = (st.reasons || []).filter((c) => c && !c.startsWith('Also next door'));
    const wave = (st.reasons || []).filter((c) => c && c.startsWith('Also next door'));
    const reasons = (chips.length >= 2 ? chips.slice(0, 2) : chips.concat(wave.slice(0, 1))).slice(0, 2);
    if (reasons.length) {
      const why = el('span', 'row-why');
      reasons.forEach((r) => why.append(el('span', '', r)));
      a.append(why);
    }
    if (st.stage) {
      // the same dot as the page: filled when the board acts (a vote or hearing), hollow otherwise
      a.append(el('span', stageClass(st.stage), stageWord(st.stage)));
    }
    li.append(a);
    return li;
  }

  const staticRows = [...all.children]; // the top 20 build.py rendered
  let chosen = null;
  try { chosen = JSON.parse(localStorage.getItem(KEY) || 'null'); } catch { chosen = null; }
  if (!Array.isArray(chosen)) chosen = window.w351 && window.w351.myTowns ? window.w351.myTowns() : [];
  // a link with ?towns=MA:Carver,MA:Plymouth shows those towns (and can be shared)
  const fromUrl = (new URLSearchParams(location.search).get('towns') || '').split(',').filter((t) => /^[A-Z]{2}:/.test(t));
  if (fromUrl.length) chosen = fromUrl;
  // the rest of the choice travels in the link too: ?towns=…&near=1&when=month&topics=solar,battery
  const start = new URLSearchParams(location.search);
  if (start.get('near') === '1') near.checked = true;
  if (filters && start.get('when')) {
    const w = filters.querySelector(`input[name=when][value="${CSS.escape(start.get('when'))}"]`);
    if (w) w.checked = true;
  }
  if (filters && start.get('topics')) {
    const want = start.get('topics').split(',');
    for (const box of filters.querySelectorAll('input[name=topic]')) box.checked = want.includes(box.value);
  }
  const save = () => {
    try { localStorage.setItem(KEY, JSON.stringify(chosen)); } catch { /* private window */ }
    const p = new URLSearchParams(location.search);
    if (chosen.length) p.set('towns', chosen.join(',')); else p.delete('towns');
    if (chosen.length && near.checked) p.set('near', '1'); else p.delete('near');
    const when = filters ? (new FormData(filters).get('when') || 'year') : 'year';
    if (when !== 'year') p.set('when', when); else p.delete('when');
    const topics = filters ? [...filters.querySelectorAll('input[name=topic]:checked')].map((i) => i.value) : [];
    if (topics.length) p.set('topics', topics.join(',')); else p.delete('topics');
    const qs = p.toString();
    history.replaceState(null, '', location.pathname + (qs ? `?${qs}` : '') + location.hash);
  };
  let names = new Map();
  const nameOf = (id) => names.get(id) || id.split(':').slice(1).join(':');
  const listNames = (ids) => {
    const n = ids.map(nameOf);
    return n.length <= 2 ? n.join(' and ') : `${n.slice(0, -1).join(', ')} and ${n[n.length - 1]}`;
  };

  function renderChips() {
    chips.replaceChildren(...chosen.map((id) => {
      const li = document.createElement('li');
      const x = el('button', 'chip-x', '×');
      x.type = 'button';
      x.setAttribute('aria-label', `Remove ${nameOf(id)}`);
      x.addEventListener('click', () => {
        chosen = chosen.filter((t) => t !== id);
        save();
        renderChips();
        render();
        input.focus();
      });
      li.append(document.createTextNode(nameOf(id)), x);
      return li;
    }));
    nearRow.hidden = !chosen.length;
  }

  // Date and topic filters: calendar ranges in local time; "this year" means the next twelve months.
  function filterState() {
    const when = filters ? (new FormData(filters).get('when') || 'year') : 'year';
    const topics = filters ? [...filters.querySelectorAll('input[name=topic]:checked')].map((i) => i.value) : [];
    const now = new Date();
    const end = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    if (when === 'week') end.setDate(end.getDate() + ((7 - end.getDay()) % 7));
    else if (when === 'month') end.setMonth(end.getMonth() + 1, 0);
    else end.setFullYear(end.getFullYear() + 1);
    const until = `${end.getFullYear()}-${String(end.getMonth() + 1).padStart(2, '0')}-${String(end.getDate()).padStart(2, '0')}`;
    return {
      keep: (date, has) => (!date || date <= until) && (!topics.length || topics.some((t) => has.includes(t))),
      active: when !== 'year' || topics.length > 0,
    };
  }

  const say = (text, link) => {
    count.replaceChildren(text);
    if (link) {
      count.append(' ');
      const a = el('a', '', link[0]);
      a.href = link[1];
      count.append(a);
    }
  };

  async function render() {
    const [doc, neighbors] = await data;
    const stories = Array.isArray(doc.stories) ? doc.stories : [];
    const { keep, active } = filterState();
    if (!chosen.length) {
      mine.hidden = true;
      all.hidden = false;
      if (active && stories.length) {
        const matches = stories.filter((st) => keep(st.meeting_date || '', st.topics || []));
        all.replaceChildren(...matches.map((st, i) => storyNode(st, i)));
        relDates(all);
        say(`${matches.length} ${matches.length === 1 ? 'story' : 'stories'}`);
      } else {
        if (all.firstChild !== staticRows[0] || all.children.length !== staticRows.length) all.replaceChildren(...staticRows);
        say('');
      }
      return;
    }
    const own = new Set(chosen);
    const nextDoor = new Set();
    if (near.checked) for (const t of chosen) for (const n of (Array.isArray(neighbors[t]) ? neighbors[t] : [])) if (!own.has(n)) nextDoor.add(n);
    const picked = stories
      .map((st, i) => ({ st, i, mine: (st.towns || []).some((t) => own.has(t)), next: (st.towns || []).some((t) => nextDoor.has(t)) }))
      .filter((x) => (x.mine || x.next) && keep(x.st.meeting_date || '', x.st.topics || []))
      // still ranked: your own towns' stories first, then by what is at stake
      .sort((a, b) => Number(b.mine) - Number(a.mine) || b.st.score - a.st.score || (a.st.meeting_date || '9999').localeCompare(b.st.meeting_date || '9999'))
      .map((x) => x.st);
    mine.replaceChildren(...picked.map((st, i) => storyNode(st, i)));
    relDates(mine);
    mine.hidden = false;
    all.hidden = true;
    const shown = [...mine.children].filter((li) => !li.hidden).length;
    const where = near.checked ? `${chosen.map(nameOf).join(', ')} and the towns next to them` : listNames(chosen);
    if (shown) say(`${shown} ${shown === 1 ? 'story' : 'stories'} in ${where}, biggest first`);
    else say(`Nothing big coming up in ${where} right now.`, ['See everything coming up', '/upcoming']);
  }

  data.then(([, , townDoc]) => {
    const towns = townDoc.towns || [];
    const multi = new Set(towns.map((t) => t.state)).size > 1;
    names = new Map(towns.map((t) => [t.id, t.state === 'MA' || !multi ? t.town : `${t.town}, ${t.state}`]));
    $('story-town-list').replaceChildren(...towns.map((t) => {
      const o = document.createElement('option');
      o.value = `${t.town}${multi ? `, ${t.state}` : ''}`;
      return o;
    }));
    renderChips();
  });

  // value is read when the visitor acts, so a pick from the list and a press of Add can't race each other
  async function add(value) {
    const want = plain(value);
    const [, , townDoc] = await data;
    if (!want) {
      // Add pressed after a pick from the list already added the town: nothing to say
      error.textContent = 'Type a town first.';
      error.hidden = Boolean(chosen.length);
      return;
    }
    const towns = townDoc.towns || [];
    const match = towns.find((t) => plain(`${t.town} ${t.state}`) === want) || towns.find((t) => plain(t.town) === want);
    if (!match) {
      error.textContent = 'We don’t know that town. Pick it from the list as you type.';
      error.hidden = false;
      return;
    }
    error.hidden = true;
    if (!chosen.includes(match.id)) chosen.push(match.id);
    if (plain(input.value) === want) input.value = '';
    save();
    renderChips();
    render();
  }
  form.addEventListener('submit', (event) => { event.preventDefault(); add(input.value); });
  // a pick from the suggestions adds the town at once
  input.addEventListener('input', async (event) => {
    const value = input.value;
    const [, , townDoc] = await data;
    const want = plain(value);
    const picked = event.inputType === 'insertReplacementText' || !event.inputType;
    if (want && picked && (townDoc.towns || []).some((t) => plain(`${t.town} ${t.state}`) === want)) add(value);
  });
  near.addEventListener('change', () => { save(); render(); });
  if (filters) filters.addEventListener('change', () => { save(); render(); });
  if (chosen.length) save();
  renderChips();
  render();
})();
