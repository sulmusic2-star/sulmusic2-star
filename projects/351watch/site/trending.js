// /trending: the biggest stories coming up. build.py renders the top 20 for everyone ("Everywhere").
// When this browser has the visitor's towns (saved by alert setup, or by "See stories near your town
// first" here), "For you" re-ranks /data/trending.json toward them, as trending.personalize() does:
//   personal = score × (1 + 2·in my towns + 1·in a town next to mine) × (1 + 0.5·topic match)
(() => {
  const all = document.getElementById('trend-all');
  if (!all) return;
  const $ = (id) => document.getElementById(id);
  const mine = $('trend-mine');
  const views = $('trend-views');
  const chooser = $('near-me');
  const input = $('near-town');
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

  // As story_html() in build.py: a row with day · town · board, the item's line and the stage word.
  function storyNode(st) {
    const li = el('li', 'row');
    li.dataset.date = st.meeting_date || '';
    li.dataset.topics = (st.topics || []).join(' ');
    const a = el('a');
    a.href = st.href;
    const day = el('span', 'row-day');
    if (st.meeting_date) {
      const t = el('time', '', dayLabel(st.meeting_date));
      t.dateTime = st.meeting_date;
      day.append(t);
    } else day.append('Date not set');
    const when = el('span', 'row-when');
    when.append(el('span', 'row-town', `${st.town}${st.state !== 'MA' ? `, ${st.state}` : ''}`));
    if (st.board) when.append(el('span', '', st.board));
    const line = el('span', 'row-line');
    if (st.new) line.append(el('span', 'badge-new', 'New'), ' ');
    const words = (st.line || st.headline || '').replace(' (no vote listed)', '').replace('; no vote listed)', ')');
    line.append(/[a-z0-9)]\.$/.test(words) && !/\b(St|Rd|Ave|Dr|Ln|Blvd|Mt|No|Art|Sec|Inc|Corp|LLC|Co)\.$/.test(words) ? words.slice(0, -1) : words);
    a.append(day, when, line);
    if (st.stage) {
      // the same dot as the page: filled when the board acts (a vote or hearing), hollow otherwise
      const act = /^(Vote|Hearing|Final vote|Possible vote|Decided)/.test(st.stage);
      a.append(el('span', `stage${act ? ' act' : ''}`, st.stage));
    }
    li.append(a);
    return li;
  }

  function show(which) {
    const showMine = which === 'mine';
    mine.hidden = !showMine;
    all.hidden = showMine;
    $('view-mine').setAttribute('aria-pressed', String(showMine));
    $('view-all').setAttribute('aria-pressed', String(!showMine));
  }

  async function renderMine(areas) {
    const [doc, neighbors, townDoc] = await data;
    const stories = Array.isArray(doc.stories) ? doc.stories : [];
    if (!stories.length) return;
    const w = doc.personalize || { in_my_towns: 2, in_neighbor_towns: 1, topic_match: 0.5 };
    const chosen = new Set(areas.towns);
    const near = new Set();
    for (const t of chosen) for (const n of (Array.isArray(neighbors[t]) ? neighbors[t] : [])) if (!chosen.has(n)) near.add(n);
    const topics = new Set(Array.isArray(areas.topics) ? areas.topics : []);
    const ranked = stories.map((st, i) => {
      const mineHit = st.towns.some((t) => chosen.has(t)) ? 1 : 0;
      const nearHit = st.towns.some((t) => near.has(t)) ? 1 : 0;
      const topicHit = topics.size && st.topics.some((t) => topics.has(t)) ? 1 : 0;
      return { st, i, personal: st.score * (1 + w.in_my_towns * mineHit + w.in_neighbor_towns * nearHit) * (1 + w.topic_match * topicHit) };
    }).sort((a, b) => b.personal - a.personal || a.i - b.i).slice(0, 20);
    mine.replaceChildren(...ranked.map((r) => storyNode(r.st)));
    if (window.w351 && window.w351.relDates) window.w351.relDates(mine);
    const byId = new Map((townDoc.towns || []).map((t) => [t.id, t]));
    const home = byId.get(areas.home_town);
    const name = home ? home.town : areas.home_town.split(':').slice(1).join(':');
    const note = $('mine-note');
    note.replaceChildren(`Stories in ${name} and the towns next to it come first. `);
    const change = el('button', 'link-btn', 'Change town');
    change.type = 'button';
    change.addEventListener('click', () => {
      chooser.hidden = false;
      input.focus();
    });
    note.append(change);
    views.hidden = false;
    chooser.hidden = true;
    show('mine');
    applyFilters();
  }

  // Narrow the list by date and by one or more topics; both lists ("Everywhere" and "Near me") follow.
  const filters = $('trend-filters');
  const staticRows = [...all.children];  // the top 20 build.py rendered
  async function applyFilters() {
    if (!filters) return;
    const when = new FormData(filters).get('when') || 'year';
    const topics = [...filters.querySelectorAll('input[name=topic]:checked')].map((i) => i.value);
    // Calendar ranges, in local time: this week ends Sunday, this month on its last day; "this year"
    // means the next twelve months, so nothing coming up is ever hidden by the default.
    const now = new Date();
    const end = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    if (when === 'week') end.setDate(end.getDate() + ((7 - end.getDay()) % 7));
    else if (when === 'month') end.setMonth(end.getMonth() + 1, 0);
    else end.setFullYear(end.getFullYear() + 1);
    const until = `${end.getFullYear()}-${String(end.getMonth() + 1).padStart(2, '0')}-${String(end.getDate()).padStart(2, '0')}`;
    const keep = (date, has) => (!date || date <= until) && (!topics.length || topics.some((t) => has.includes(t)));
    const active = when !== 'year' || topics.length > 0;
    // "Everywhere" with a filter on draws from every ranked story (/data/trending.json holds 100), not just
    // the 20 on the page, so a topic shows all of its stories; without a filter the page's own rows return.
    const [doc] = await data;
    const stories = Array.isArray(doc.stories) ? doc.stories : [];
    let shown = 0;
    let total = 0;
    if (active && stories.length) {
      const matches = stories.filter((st) => keep(st.meeting_date || '', st.topics || []));
      all.replaceChildren(...matches.map(storyNode));
      if (window.w351 && window.w351.relDates) window.w351.relDates(all);
      if (!all.hidden) {
        shown = matches.length;
        total = stories.length;
      }
    } else if (all.children.length !== staticRows.length || all.firstChild !== staticRows[0]) {
      all.replaceChildren(...staticRows);
    }
    for (const li of mine.children) {
      const ok = keep(li.dataset.date || '', (li.dataset.topics || '').split(' '));
      li.hidden = !ok;
      if (!mine.hidden) {
        total += 1;
        if (ok) shown += 1;
      }
    }
    const count = $('trend-count');
    if (count) count.textContent = active ? `${shown} of ${total} stories` : '';
  }
  if (filters) filters.addEventListener('change', applyFilters);

  $('view-mine').addEventListener('click', () => show('mine'));
  $('view-all').addEventListener('click', () => show('all'));

  data.then(([, , townDoc]) => {
    const towns = townDoc.towns || [];
    const multi = new Set(towns.map((t) => t.state)).size > 1;
    $('near-towns').replaceChildren(...towns.map((t) => {
      const o = document.createElement('option');
      o.value = `${t.town}${multi ? `, ${t.state}` : ''}`;
      return o;
    }));
  });
  chooser.addEventListener('submit', async (event) => {
    event.preventDefault();
    const [, , townDoc] = await data;
    const want = plain(input.value);
    const match = (townDoc.towns || []).find((t) => plain(`${t.town} ${t.state}`) === want || plain(t.town) === want);
    const error = $('near-town-error');
    if (!match) {
      error.textContent = want ? 'We don’t know that town. Pick it from the list as you type.' : 'Type your town first.';
      error.hidden = false;
      return;
    }
    error.hidden = true;
    const areas = { home_town: match.id, towns: [match.id] };
    if (window.w351) window.w351.saveAreas(match.id, [match.id]);
    renderMine(areas);
  });

  const saved = window.w351 && window.w351.areas ? window.w351.areas() : null;
  chooser.hidden = Boolean(saved);
  if (saved) renderMine(saved);
})();
