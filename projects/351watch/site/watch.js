// /watch and /alerts-for-groups: set up alerts, or edit them with ?edit=<private key>.
// Screen 1 asks for the town; screen 2 shows what the alerts would have sent lately, one box for all
// the towns next door (and "Choose which towns" for each one), the topics (solar, battery storage and data
// centers to start, or the topic the visitor came from), and an email address (when /api/status says
// email is on). /alerts-for-groups (form data-mode="groups") adds a chat webhook, tested before saving,
// and a name.
// Free alerts cover one home town plus the towns next to it (/data/neighbors.json), every topic.
// Screen 1 also takes a line such as "battery storage in Carver, Plympton and Wareham": the first
// town is the home town, other typed towns narrow the neighbors, typed topics narrow the topics.
// Prefill: ?town=MA:Carver&topic=solar opens screen 2 directly.
(() => {
  const form = document.getElementById('watch-form');
  if (!form) return;
  const $ = (id) => document.getElementById(id);
  const params = new URLSearchParams(location.search);
  let editId = /^[A-Za-z0-9_-]{24,64}$/.test(params.get('edit') || '') ? params.get('edit') : null;

  const title = $('watch-title');
  const home = $('home-town');
  const read = $('home-read');
  const nearList = $('near-list');
  const nearAll = $('near-all');
  const extraList = $('extra-list');
  const topicBoxes = Array.from(form.querySelectorAll('input[name="topics"]'));
  const submit = $('watch-submit');
  const status = $('watch-status');
  const groups = form.dataset.mode === 'groups';
  const testStatus = $('test-status');
  const webhook = $('webhook-url');
  const removeHook = $('webhook-remove');
  const email = $('email');
  const removeEmail = $('email-remove');
  const DEFAULT_READ = read.textContent;
  const PRESET = topicBoxes.filter((t) => t.checked).map((t) => t.value); // as build.py ticks them
  let testedUrl = ''; // the webhook URL that last passed a test message

  let towns = []; // [{id, state, town, county, monitored}]
  const byId = new Map();
  let nameList = []; // [[plain name, regex, [ids]]]
  let neighbors = null; // {"MA:Carver": [...]}, or {} if it could not be loaded
  let lines = null; // /data/lines.json, loaded for the preview
  let homeId = null;
  let topicsFromText = false;
  let lastTyped = ''; // the towns read from screen 1 last time, so a change resets the neighbor boxes
  const plain = (s) => String(s || '').toLowerCase().replace(/[’']/g, '').replace(/[^a-z0-9]+/g, ' ').trim();
  const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const label = (id, ref) => {
    const t = byId.get(id);
    if (!t) return id.split(':').slice(1).join(':');
    const base = typeof ref === 'string' ? ref.split(':')[0] : 'MA';
    return `${t.town}${t.state !== base ? `, ${t.state}` : ''}`;
  };
  const joinAnd = (parts) => (parts.length < 3 ? parts.join(' and ') : `${parts.slice(0, -1).join(', ')} and ${parts[parts.length - 1]}`);
  const plural = (n, word, many) => `${n} ${n === 1 ? word : (many || `${word}s`)}`;
  const el = (tag, cls, text) => {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text != null) node.textContent = text;
    return node;
  };
  const dayLabel = (iso) => new Date(`${iso}T12:00:00`).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }).replace(/,/g, '');
  const readJSON = (url) => fetch(url, { headers: { Accept: 'application/json' } })
    .then((r) => r.json().catch(() => ({})).then((d) => (r.ok ? d : {})))
    .catch(() => ({}));

  function setStatus(node, text, kind) {
    node.className = `form-status${kind ? ` ${kind}` : ''}`;
    node.textContent = text;
  }

  function fieldError(name, message) {
    // A towns problem found after screen 1 (such as the free-area check) shows by the towns on screen 2.
    const id = name === 'towns' && !$('step-send').hidden ? 'near-error' : `${name}-error`;
    if (name === 'towns') for (const other of ['towns-error', 'near-error']) if (other !== id) $(other).hidden = true;
    const node = $(id);
    if (node) {
      node.textContent = message || '';
      node.hidden = !message;
    }
    const target = name === 'towns' ? home : name === 'topics' ? topicBoxes[0] : form.elements[name];
    if (target && target.setAttribute) {
      if (message) target.setAttribute('aria-invalid', 'true');
      else target.removeAttribute('aria-invalid');
    }

  }

  // ---------- screens
  function show(step) {
    $('step-town').hidden = step !== 'town';
    $('step-send').hidden = step !== 'send';
    title.textContent = step === 'town' ? title.dataset.start
      : `${editId ? 'Edit alerts' : 'Alerts'} for ${homeId ? label(homeId) : 'your town'}`;
    if (step === 'send') renderPreview();
  }

  // ---------- data
  const loadTowns = fetch('/data/towns.json').then((r) => (r.ok ? r.json() : Promise.reject(new Error(String(r.status))))).then((doc) => {
    towns = doc.towns || [];
    const multi = new Set(towns.map((t) => t.state)).size > 1;
    $('town-names').replaceChildren(...towns.map((t) => {
      const o = document.createElement('option');
      o.value = `${t.town}${multi ? `, ${t.state}` : ''}`;
      return o;
    }));
    const names = new Map();
    for (const t of towns) {
      byId.set(t.id, t);
      const key = plain(t.town);
      if (!names.has(key)) names.set(key, []);
      names.get(key).push(t.id);
    }
    nameList = [...names.entries()].sort((a, b) => b[0].length - a[0].length)
      .map(([n, ids]) => [n, new RegExp(`(^| )${esc(n)}(?: (ma|mass|massachusetts|ny|new york|ri|rhode island))?(?= |$)`), ids]);
  }).catch(() => {
    fieldError('towns', 'We couldn’t load the town list. Reload the page to try again.');
  });
  const loadNeighbors = readJSON('/data/neighbors.json').then((doc) => { neighbors = doc && typeof doc === 'object' ? doc : {}; });
  let linesPromise = null;
  const loadLines = () => {
    linesPromise = linesPromise || readJSON('/data/lines.json').then((doc) => { lines = doc && doc.recent ? doc : { recent: {}, lines: {} }; });
    return linesPromise;
  };
  readJSON('/api/status').then((s) => {
    const on = !!(s && s.email_alerts === true);
    $('email-option').hidden = !on;
    $('no-email').hidden = on;
    if (!on && !editId) submit.textContent = 'Follow these towns';
  });

  // ---------- reading screen 1
  const TOPIC_WORDS = [
    ['battery_storage', /\b(batter(y|ies)|bess|energy storage|storage)\b/],
    ['solar', /\b(solar|photovoltaics?|pv)\b/],
    ['data_center', /\b(data ?cent(er|re)s?|hyperscale|crypto\w*)\b/],
    ['moratorium', /\b(moratori(um|ums|a))\b/],
    ['clean_energy_siting', /\b(clean energy (permits?|siting)|consolidated (local )?permits?|permit rules)\b/],
    ['zoning_amendment', /\b(zoning (changes?|amendments?)|rezon(e|es|ing))\b/],
    ['40b_comprehensive_permit', /\b(40b|affordable housing|comprehensive permits?)\b/],
    ['wireless_telecom', /\b(cell (towers?|phones?)|wireless|telecom|antennas?)\b/],
    ['wetlands_filing', /\b(wetlands?( filings?)?)\b/],
  ].filter(([k]) => topicBoxes.some((t) => t.value === k));
  const STATES = { ma: 'MA', mass: 'MA', massachusetts: 'MA', ny: 'NY', 'new york': 'NY', ri: 'RI', 'rhode island': 'RI' };
  const FILLER = new Set(['in', 'and', 'or', 'for', 'about', 'the', 'of', 'on', 'to', 'me', 'my', 'any', 'all', 'near',
    'items', 'item', 'news', 'alerts', 'alert', 'town', 'towns', 'city', 'project', 'projects', 'proposals', 'energy',
    'watch', 'tell', 'when', 'comes', 'up', 'with', 'a', 'an', 'ma', 'ny', 'ri', 'massachusetts', 'new', 'york', 'rhode', 'island']);

  function parse(text) {
    let rest = ` ${plain(text)} `;
    const topics = [];
    for (const [key, re] of TOPIC_WORDS) {
      if (re.test(rest)) {
        topics.push(key);
        rest = rest.replace(new RegExp(re.source, 'g'), (x) => ' '.repeat(x.length));
      }
    }
    const found = [];
    for (const [, re, ids] of nameList) {
      const m = rest.match(re);
      if (!m) continue;
      const state = m[2] ? STATES[m[2]] : null;
      const id = (state && ids.find((i) => i.startsWith(`${state}:`))) || ids.find((i) => i.startsWith('MA:')) || ids[0];
      found.push([m.index, id]);
      rest = rest.replace(re, (x) => ' '.repeat(x.length)); // same length, so later positions hold
    }
    found.sort((a, b) => a[0] - b[0]);
    const left = rest.split(/\s+(?:and|or|in|for|about|near)\s+|\s*,\s*|\s{2,}/).map((p) => p.trim())
      .filter((p) => p && !p.split(' ').every((w) => FILLER.has(w) || w.length < 2));
    return { towns: found.map((f) => f[1]), topics, left };
  }

  function checkbox(name, value, text, checked) {
    const li = document.createElement('li');
    const lab = el('label', 'check');
    const box = document.createElement('input');
    box.type = 'checkbox';
    box.name = name;
    box.value = value;
    box.checked = checked;
    lab.append(box, el('span', '', text));
    li.append(lab);
    return li;
  }

  function topicSummary() {
    topicLine();
  }
  function oldTopicSummary() {
    const on = topicBoxes.filter((t) => t.checked);
    const names = on.map((t) => t.closest('label').textContent.trim().toLowerCase());
    $('topics-details').querySelector('summary').textContent = on.length === topicBoxes.length ? 'Topics: all'
      : (on.length ? `Topics: ${names.slice(0, 2).join(', ')}${on.length > 2 ? ` and ${on.length - 2} more` : ''}` : 'Topics: none');
  }

  const area = (id) => (neighbors && !id.startsWith('_') && Array.isArray(neighbors[id]) ? neighbors[id] : []).filter((n) => byId.has(n));
  const notRead = (id) => byId.has(id) && byId.get(id).monitored === false;
  const nearBoxes = () => Array.from(nearList.querySelectorAll('input[name="towns"]'));

  // A home town we can't read yet: say so, and offer to ask for it.
  function showRequest(id) {
    const box = $('home-request');
    if (!id || !notRead(id)) {
      box.hidden = true;
      return;
    }
    $('home-request-text').textContent = `We can’t check ${label(id)}’s agendas yet. You can still follow the towns next to it, and we can ask ${label(id)}’s town hall to let us check its agendas.`;
    $('home-request-btn').textContent = `Ask us to add ${label(id)}`;
    $('home-request-btn').disabled = false;
    $('home-request-status').textContent = '';
    box.hidden = false;
  }
  $('home-request-btn').addEventListener('click', async (event) => {
    const button = event.currentTarget;
    const out = $('home-request-status');
    button.disabled = true;
    setStatus(out, 'Sending…');
    try {
      await window.w351.requestTown(homeId, label(homeId));
      setStatus(out, 'Thanks. We’ve got your request and will ask the town hall.', 'ok');
    } catch (err) {
      setStatus(out, err.message, 'err');
      button.disabled = false;
    }
  });

  // The one "Also watch the towns next to …" box stands for all the neighbor boxes.
  function syncNearAll() {
    const boxes = nearBoxes();
    const on = boxes.filter((b) => b.checked).length;
    nearAll.checked = on > 0;
    nearAll.indeterminate = on > 0 && on < boxes.length;
  }

  function setHome(id, checkedNear) {
    homeId = id;
    if (!id) {
      showRequest(null);
      nearList.replaceChildren();
      return;
    }
    const near = area(id);
    const first = checkbox('home', id, `${label(id)} (your town${notRead(id) ? ', can’t check yet' : ''})`, true);
    first.querySelector('input').disabled = true;
    nearList.replaceChildren(first, ...near.map((n) => checkbox('towns', n,
      `${label(n, id)}${notRead(n) ? ' (can’t check yet)' : ''}`, checkedNear ? checkedNear.includes(n) : true)));
    const cant = [id, ...near].filter(notRead);
    $('cant-note').textContent = notRead(id)
      ? `We can’t check ${label(id)} yet, so for now these alerts come from the towns next to it.` : '';
    $('cant-note').hidden = !notRead(id);
    const chosen = checkedNear ? near.filter((n) => checkedNear.includes(n)) : near;
    const cantNear = near.filter(notRead);
    const shown = groups ? near : chosen;
    $('near-all-text').textContent = `Also the ${shown.length === 1 ? 'town' : `${shown.length} towns`} next door: ${joinAnd(shown.map((n) => label(n, id)))}`
      + (cantNear.length ? ` (${joinAnd(cantNear.map((n) => label(n, id)))} can’t be read yet)` : '');
    $('near-all-row').hidden = !near.length;
    $('near-note').hidden = Boolean(near.length);
    $('near-note').textContent = near.length ? ''
      : (neighbors && Object.keys(neighbors).length
        ? `${label(id)} has no towns next to it, so alerts cover ${label(id)} only.`
        : `We couldn’t load the towns next to ${label(id)}. Alerts will cover ${label(id)} for now.`);
    syncNearAll();
    showRequest(id);
    fieldError('towns', '');
  }

  // "Topics: solar, battery storage, data centers. Change" above the folded options.
  function topicLine() {
    const on = topicBoxes.filter((t) => t.checked).map((t) => t.closest('label').textContent.trim().replace(/\s*\(.*\)$/, '').toLowerCase());
    $('topic-names').textContent = on.length ? joinAnd(on) : 'none chosen';
  }
  $('topics-change').addEventListener('click', () => {
    $('other-ways').open = true;
    (topicBoxes[0] || $('other-ways')).focus();
  });

  function setExtras(ids) {
    extraList.replaceChildren(...ids.map((i) => checkbox('towns', i, label(i), true)));
    $('extra-wrap').hidden = !ids.length;
  }

  function readHome() {
    const text = home.value;
    const exact = towns.find((t) => plain(`${t.town} ${t.state}`) === plain(text) || plain(t.town) === plain(text));
    const { towns: found, topics, left } = exact ? { towns: [exact.id], topics: [], left: [] } : parse(text);
    const first = found[0] || null;
    const others = found.slice(1);
    const typed = found.join();
    if (typed !== lastTyped) setHome(first, others.length ? others : null);
    lastTyped = typed;
    // Typed topics narrow the topics; clearing them brings back all topics.
    if (topics.length) {
      for (const t of topicBoxes) t.checked = topics.includes(t.value);
      topicsFromText = true;
      fieldError('topics', '');
    } else if (topicsFromText) {
      for (const t of topicBoxes) t.checked = PRESET.includes(t.value);
      topicsFromText = false;
    }
    topicSummary();

    if (!text.trim()) {
      read.textContent = DEFAULT_READ;
      return;
    }
    const parts = [];
    const outside = first ? others.filter((o) => !area(first).includes(o)) : [];
    if (first) {
      const t = byId.get(first);
      parts.push(`${label(first)}${t && t.county ? ` (${t.county} County)` : ''}.`);
    } else {
      parts.push('Pick your town from the list.');
    }
    if (outside.length) {
      parts.push(` ${joinAnd(outside.map((x) => label(x)))} ${outside.length === 1 ? 'isn’t' : 'aren’t'} next to ${label(first)}. Free alerts cover one town and its neighbors.`);
    }
    // Half-typed words are not mistakes; the Continue button says so if a name still doesn't match.
    read.textContent = parts.join('');
  }

  function chosenTowns() {
    const near = Array.from(form.querySelectorAll('#near-list input[name="towns"]:checked, #extra-list input[name="towns"]:checked')).map((b) => b.value);
    return homeId ? [homeId, ...near.filter((t) => t !== homeId)] : near;
  }

  // ---------- the preview: what these alerts would have shown lately, from our own data
  function renderPreview() {
    const box = $('preview');
    if (!homeId) {
      box.replaceChildren();
      return;
    }
    if (!lines) {
      box.replaceChildren(el('p', 'form-note', 'Looking up recent agendas…'));
      loadLines().then(renderPreview);
      return;
    }
    const ids = chosenTowns();
    const topics = topicBoxes.filter((t) => t.checked).map((t) => t.value);
    const meetings = new Map();
    for (const tid of ids) {
      for (const [d, board, tps, id] of lines.recent[tid] || []) {
        if (!tps.some((t) => topics.includes(t))) continue;
        const key = `${tid}|${board}|${d}`;
        if (!meetings.has(key)) meetings.set(key, { tid, board, d, ids: [] });
        meetings.get(key).ids.push(id);
      }
    }
    const today = lines.today || new Date().toISOString().slice(0, 10);
    const all = [...meetings.values()];
    const past = all.filter((m) => m.d < today).length;
    const ahead = all.filter((m) => m.d >= today).sort((a, b) => a.d.localeCompare(b.d) || a.tid.localeCompare(b.tid));
    const others = ids.length - 1;
    const where = others ? `${label(homeId)} and ${others === 1 ? 'the town' : `${others} towns`} next to it` : label(homeId);
    const nodes = [];

    if (!past && !ahead.length) {
      nodes.push(el('p', '', `Nothing on these topics in ${where} in the last 30 days. You’ll hear from us when something comes up.`));
    } else {
      const lead = el('p');
      const next = ahead.length ? (ahead.length > 3 ? `${ahead.length} more are coming up. The next 2:` : 'Coming up next:') : 'Nothing else is on an agenda yet.';
      if (past) lead.append(`Over the last 30 days, ${where} had `, el('b', '', plural(past, 'meeting')), ' on these topics, so expect about that many alerts a month. ', next);
      else lead.append(`Nothing on these topics in ${where} in the last 30 days, so alerts will be rare. `, next);
      nodes.push(lead);
      if (ahead.length) {
        const list = el('ul', 'preview-lines');
        for (const m of ahead.slice(0, 2)) {
          const li = el('li');
          const head = el('p', 'meet-head');
          head.append(el('span', '', label(m.tid, homeId)), el('span', '', m.board), el('span', 'meet-day', dayLabel(m.d)));
          // The most specific line first (the lowest rank), as the town page orders them.
          const said = m.ids.map((id) => (lines.lines[id] || [])[0]).filter(Boolean);
          const rank = (id) => Number(((lines.lines[id] || [])[6]) ?? 60);
          const bestId = m.ids.slice().sort((a, b) => rank(a) - rank(b))[0];
          const best = ((lines.lines[bestId] || [])[0] || said[0] || 'Agenda item').replace(/:\s*“.*”$/, '.');
          const others = new Set(said).size - 1;
          li.append(head, el('p', 'line-say', best));
          if (others > 0) li.append(el('p', 'meet-found', `and ${plural(others, 'more item')}`));
          list.append(li);
        }
        nodes.push(list);
      }
    }
    box.replaceChildren(...nodes);
  }

  // ---------- wiring
  home.addEventListener('input', () => Promise.all([loadTowns, loadNeighbors]).then(readHome));
  nearList.addEventListener('change', () => { syncNearAll(); renderPreview(); });
  nearAll.addEventListener('change', () => {
    for (const b of nearBoxes()) b.checked = nearAll.checked;
    nearAll.indeterminate = false;
    renderPreview();
  });
  extraList.addEventListener('change', renderPreview);
  for (const t of topicBoxes) {
    t.addEventListener('change', () => { topicsFromText = false; fieldError('topics', ''); topicSummary(); renderPreview(); });
  }

  async function next() {
    await Promise.all([loadTowns, loadNeighbors]);
    readHome();
    if (!homeId && home.value.trim()) {
      // "Plym" + Continue: the one town that starts that way, as the home page's box does.
      const q = plain(home.value);
      const starts = towns.filter((t) => plain(t.town).startsWith(q));
      if (starts.length === 1 || (starts.length > 1 && starts.every((t) => t.town === starts[0].town))) {
        home.value = starts[0].town;
        readHome();
      }
    }
    if (!homeId) {
      fieldError('towns', home.value.trim() ? 'We don’t know that town. Pick it from the list as you type.' : 'Type your town first.');
      home.focus();
      return;
    }
    loadLines();
    show('send');
    title.focus();
  }
  $('town-next').addEventListener('click', next);
  $('change-town').addEventListener('click', () => {
    show('town');
    home.focus();
  });

  // Residents don't name their alerts: "Carver and the towns next to it".
  function autoName(ids) {
    if (!homeId) return '';
    const others = ids.filter((x) => x !== homeId);
    const near = area(homeId);
    if (!others.length) return label(homeId);
    if (others.length === near.length && others.every((x) => near.includes(x))) return `${label(homeId)} and the towns next to it`;
    return `${label(homeId)} and ${others.length === 1 ? label(others[0], homeId) : `${others.length} nearby towns`}`;
  }

  function payload() {
    const towns = chosenTowns();
    const typedName = form.elements.name ? form.elements.name.value.trim() : '';
    const data = {
      name: typedName || autoName(towns),
      towns,
      topics: topicBoxes.filter((t) => t.checked).map((t) => t.value),
      website: form.elements.website.value,
    };
    if (form.elements.webhook_format) data.webhook_format = form.elements.webhook_format.value;
    if (homeId) data.home_town = homeId;
    const url = webhook ? webhook.value.trim() : '';
    if (webhook && (!editId || url)) data.webhook_url = url;
    else if (removeHook && removeHook.checked) data.webhook_url = '';
    if (!$('email-option').hidden) {
      const address = email.value.trim();
      if (address) data.email = address;
      else if (editId && removeEmail && removeEmail.checked) data.email = '';
    }
    return data;
  }

  function validate(data) {
    let ok = true;
    if (!data.towns.length) {
      fieldError('towns', 'Type your town and pick it from the list.');
      ok = false;
    }
    if (!data.topics.length) {
      fieldError('topics', 'Choose at least one topic.');
      ok = false;
    }
    if (data.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
      fieldError('email', data.email.includes('@') ? 'Check the email address. It should look like name@example.com.' : 'That email is missing an @.');
      ok = false;
    }
    return ok;
  }

  async function send(method, url, body) {
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok || data.ok === false) {
      const err = new Error(data.error || (res.status === 503
        ? 'Alerts can’t be saved right now. Try again in a few minutes.'
        : 'Something went wrong on our end. Try again in a minute.'));
      err.fields = data.fields || {};
      err.code = data.code || '';
      err.status = res.status;
      throw err;
    }
    return data;
  }

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!$('step-town').hidden) {
      next();
      return;
    }
    const data = payload();
    for (const f of ['towns', 'topics', 'webhook_url', 'email']) fieldError(f, '');
    if (!validate(data)) {
      if (!data.towns.length) show('town');
      setStatus(status, 'Check the highlighted field, then try again.', 'err');
      return;
    }
    submit.disabled = true;
    if (data.webhook_url && data.webhook_url !== testedUrl) {
      setStatus(status, 'Checking the webhook with a test message…');
      try {
        await send('POST', '/api/watchlists?action=test', data);
        testedUrl = data.webhook_url;
        setStatus(testStatus, 'Test message sent. Check your channel.', 'ok');
      } catch (err) {
        const why = (err.fields && err.fields.webhook_url) || err.message;
        fieldError('webhook_url', `We couldn’t post to that webhook: ${why} Check the link, or clear it to save without chat posts.`);
        setStatus(status, 'Not saved yet. Fix the webhook link, or clear it, then try again.', 'err');
        submit.disabled = false;
        webhook.focus();
        return;
      }
    }
    setStatus(status, editId ? 'Saving…' : 'Setting up your alerts…');
    try {
      const result = editId
        ? await send('PATCH', `/api/watchlists?id=${encodeURIComponent(editId)}`, data)
        : await send('POST', '/api/watchlists', data);
      const id = editId || result.id;
      if (!id) throw new Error('Something went wrong on our end. Try again in a minute.');
      window.w351.remember(id, data.name);
      if (window.w351.saveAreas) {
        window.w351.saveAreas(data.home_town, data.towns, data.topics.length < topicBoxes.length ? data.topics : null);
      }
      setStatus(status, editId ? 'Changes saved. Opening your alerts…' : 'Alerts set up. Opening them…', 'ok');
      const flags = [editId ? '' : 'new=1', data.email ? 'email=1' : ''].filter(Boolean).join('&');
      location.assign(`/w/${id}${flags ? `?${flags}` : ''}`);
    } catch (err) {
      for (const [field, message] of Object.entries(err.fields || {})) fieldError(field === 'home_town' ? 'towns' : field, message);
      if (err.code === 'free_area' || err.fields.towns || err.fields.home_town) {
        if (!err.fields.towns && !err.fields.home_town) fieldError('towns', err.message);
        if ($('other-ways')) $('other-ways').open = true;
        if ($('near-details')) $('near-details').open = true;
      }
      setStatus(status, err.message, 'err');
      submit.disabled = false;
    }
  });

  if (webhook) webhook.addEventListener('input', () => { fieldError('webhook_url', ''); });
  if ($('send-test')) $('send-test').addEventListener('click', async (event) => {
    const button = event.currentTarget;
    const url = webhook.value.trim();
    fieldError('webhook_url', '');
    if (!url && !editId) {
      setStatus(testStatus, 'Paste a webhook URL first.', 'err');
      webhook.focus();
      return;
    }
    button.disabled = true;
    setStatus(testStatus, 'Sending a test message…');
    try {
      const data = payload();
      if (url) await send('POST', '/api/watchlists?action=test', { ...data, webhook_url: url });
      else await send('POST', `/api/watchlists?id=${encodeURIComponent(editId)}&action=test`, {});
      if (url) testedUrl = url;
      setStatus(testStatus, 'Test message sent. Check your channel.', 'ok');
    } catch (err) {
      if (url) testedUrl = '';
      fieldError('webhook_url', `We couldn’t post to that webhook: ${(err.fields && err.fields.webhook_url) || err.message}`);
      setStatus(testStatus, 'The test message didn’t go through. Check the link and try again.', 'err');
    } finally {
      button.disabled = false;
    }
  });

  function showMyLists() {
    const lists = window.w351.recall().filter((l) => l.id !== editId);
    if (!lists.length) return;
    $('my-lists-items').replaceChildren(...lists.map((l) => {
      const li = document.createElement('li');
      const a = document.createElement('a');
      a.href = `/w/${l.id}`;
      a.textContent = l.name || 'Your alerts';
      li.append(a);
      if (l.readonly) li.append(' (shared with you, view only)');
      return li;
    }));
    $('my-lists').hidden = false;
  }

  function prefill(ids, topicKeys) {
    const valid = ids.filter((i) => byId.has(i));
    if (valid.length) {
      const first = valid[0];
      home.value = label(first);
      const near = area(first);
      const others = valid.slice(1);
      setHome(first, others.length ? others.filter((o) => near.includes(o)) : null);
      setExtras(others.filter((o) => !near.includes(o)));
      lastTyped = first;
    }
    if (topicKeys.length && topicBoxes.some((t) => topicKeys.includes(t.value))) {
      for (const t of topicBoxes) t.checked = topicKeys.includes(t.value);
      if (!valid.length) {
        // Someone arrived from a topic page: the question keeps the promise it came from.
        const names = topicBoxes.filter((t) => t.checked).map((t) => ((t.closest('label') || t.parentElement).textContent || '').trim().split('\n')[0].trim());
        const help = $('town-help');
        if (help && names.length) help.textContent = `You get a private page that updates every morning and a calendar feed about ${names.join(' and ').toLowerCase()} for it and the towns next to it.`;
      }
    }
    topicSummary();
    return valid.length > 0;
  }

  async function loadForEdit() {
    $('edit-banner').hidden = false;
    submit.textContent = 'Save changes';
    submit.disabled = true;
    try {
      const { watchlist: wl } = await send('GET', `/api/watchlists?id=${encodeURIComponent(editId)}`);
      if (wl.readonly) throw new Error('That is a share link, which can’t change alerts. Open your private link to edit them.');
      await Promise.all([loadTowns, loadNeighbors]);
      $('edit-name').textContent = wl.name || 'your alert list';
      document.title = `Edit ${wl.name || 'alerts'} | ${document.title.split(' | ').pop()}`;
      if (wl.webhook && wl.webhook.configured && !groups) {
        location.replace(`/alerts-for-groups?edit=${encodeURIComponent(editId)}`); // that page edits the webhook
        return;
      }
      if (form.elements.name) form.elements.name.value = wl.name || '';
      const first = wl.home_town && wl.towns.includes(wl.home_town) ? wl.home_town : wl.towns[0];
      prefill([first, ...wl.towns.filter((t) => t !== first)], wl.topics);
      for (const t of topicBoxes) t.checked = wl.topics.includes(t.value);
      topicSummary();
      if (wl.webhook && wl.webhook.configured && webhook) {
        webhook.placeholder = `Saved: ${wl.webhook.masked}. Leave blank to keep it.`;
        form.elements.webhook_format.value = wl.webhook.format || 'auto';
        $('webhook-remove-row').hidden = false;
      }
      if (wl.email && wl.email.configured) {
        email.placeholder = `Saved: ${wl.email.masked}. Leave blank to keep it.`;
        $('email-remove-row').hidden = false;
      }
      show('send');
      submit.disabled = false;
    } catch (err) {
      const box = $('watch-error');
      box.textContent = `${err.message} You can set up new alerts below.`;
      box.hidden = false;
      $('edit-banner').hidden = true;
      editId = null;
      submit.textContent = 'Follow these towns';
      submit.disabled = false;
      show('town');
    }
  }

  showMyLists();
  if (editId) loadForEdit();
  else {
    Promise.all([loadTowns, loadNeighbors]).then(() => {
      const ids = params.getAll('town').flatMap((v) => v.split(',')).map((v) => (v.includes(':') ? v : `MA:${v}`));
      if (prefill(ids, params.getAll('topic').flatMap((v) => v.split(',')).filter(Boolean))) show('send');
    });
  }
})();
