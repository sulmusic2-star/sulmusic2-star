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

  // A brief's facts, labeled from trending.json's brief_labels (as brief_facts_html() in build.py).
  function factsNode(b, labels, speak) {
    const dl = el('dl', 'brief-facts');
    for (const [key, label] of Object.entries(labels || {})) {
      if (key === 'quote' || !label) continue;
      let v = b[key];
      if (key === 'can_speak') v = v === true ? (speak || {}).true : v === false ? (speak || {}).false : null;
      if (v === null || v === undefined || v === '' || v === false) continue;
      dl.append(el('div', 'fact'), el('dt', '', label), el('dd', '', String(v)));
    }
    return dl.childElementCount ? dl : null;
  }

  // As story_html() in build.py.
  function storyNode(st, doc) {
    const b = st.brief || null;
    const headline = b && b.line ? b.line : st.headline;
    const dek = b && b.what ? b.what : st.dek;
    const li = el('li', `story${b ? ' brief' : ''}`);
    const when = el('p', 'story-when');
    if (st.meeting_date) {
      const t = el('time', '', dayLabel(st.meeting_date));
      t.dateTime = st.meeting_date;
      t.dataset.rel = '';
      when.append(t);
    } else when.append(el('span', '', 'Date not set yet'));
    when.append(el('span', 'story-town', `${st.town}${st.state !== 'MA' ? `, ${st.state}` : ''}`));
    const head = el('h2', 'story-head');
    const a = el('a');
    a.href = st.href;
    if (st.new) a.append(el('span', 'badge-new', 'New'), ' ');
    a.append(headline);
    head.append(a);
    li.append(when, head, el('p', 'story-dek', dek));
    const facts = b ? factsNode(b, (doc || {}).brief_labels, (doc || {}).brief_speak) : null;
    if (facts) li.append(facts);
    if (st.reasons.length) {
      const why = el('p', 'story-why');
      why.append(...st.reasons.map((r) => el('span', '', r)));
      li.append(why);
    }
    const tools = el('div', 'line-tools');
    const quoteText = b ? (b.quote || '') : st.quote;
    if (quoteText) {
      const d = el('details', 'item-words');
      const q = el('blockquote', 'item-quote', quoteText);
      d.append(el('summary', '', b ? (((doc || {}).brief_labels || {}).quote || 'Exact agenda wording') : 'Show the agenda text'),
        el('p', 'item-from', `Quoted from the ${st.warrant ? 'warrant' : 'agenda'}:`), q);
      tools.append(d);
    }
    if (st.source_url) {
      const link = el('a', 'item-link', st.warrant ? 'Open the warrant' : 'Open the agenda');
      link.href = st.source_url;
      link.rel = 'nofollow noopener';
      link.target = '_blank';
      tools.append(link);
    }
    // Share: the day, the headline and the summary, ready to paste (app.js handles the click).
    const share = el('button', 'link-btn', 'Share');
    share.type = 'button';
    share.dataset.share = '';
    share.dataset.url = new URL(st.href, location.origin).href;
    share.dataset.title = headline;
    share.dataset.text = `${st.meeting_date ? `${dayLabel(st.meeting_date)}: ` : ''}${headline}. ${dek}`;
    tools.append(share);
    li.append(tools);
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
    mine.replaceChildren(...ranked.map((r) => storyNode(r.st, doc)));
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
  }

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
