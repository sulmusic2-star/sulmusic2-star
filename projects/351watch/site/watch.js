// /watch: set up alerts (an "alert list"), or edit one with ?edit=<private key>.
// Free alerts cover one home town plus the towns next to it (/data/neighbors.json), every topic.
// Step 1 takes a town name, or a line such as "battery storage in Carver, Plympton and Wareham":
// the first town is the home town, other typed towns narrow the neighbors, typed topics narrow
// the topics. The ticked boxes are what gets saved. Prefill: ?town=MA:Carver&topic=solar.
(() => {
  const form = document.getElementById('watch-form');
  if (!form) return;
  const $ = (id) => document.getElementById(id);
  const params = new URLSearchParams(location.search);
  let editId = /^[A-Za-z0-9_-]{24,64}$/.test(params.get('edit') || '') ? params.get('edit') : null;

  const home = $('home-town');
  const read = $('home-read');
  const nearList = $('near-list');
  const nearNote = $('near-note');
  const extraList = $('extra-list');
  const topicBoxes = Array.from(form.querySelectorAll('input[name="topics"]'));
  const submit = $('watch-submit');
  const status = $('watch-status');
  const testStatus = $('test-status');
  const webhook = $('webhook-url');
  const removeHook = $('webhook-remove');
  const email = $('email');
  const removeEmail = $('email-remove');
  const DEFAULT_READ = read.textContent;

  let towns = []; // [{id, state, town, county, monitored}]
  const byId = new Map();
  let nameList = []; // [[plain name, regex, [ids]]]
  let neighbors = null; // {"MA:Carver": [...]}, or {} if it could not be loaded
  let homeId = null;
  let topicsFromText = false;
  const plain = (s) => String(s || '').toLowerCase().replace(/[’']/g, '').replace(/[^a-z0-9]+/g, ' ').trim();
  const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const label = (id) => {
    const t = byId.get(id);
    return t ? `${t.town}${t.state !== 'MA' ? `, ${t.state}` : ''}` : id.split(':').slice(1).join(':');
  };
  const joinAnd = (parts) => (parts.length < 3 ? parts.join(' and ') : `${parts.slice(0, -1).join(', ')} and ${parts[parts.length - 1]}`);

  function setStatus(el, text, kind) {
    el.className = `form-status${kind ? ` ${kind}` : ''}`;
    el.textContent = text;
  }

  function fieldError(name, message) {
    const el = $(`${name}-error`);
    if (el) {
      el.textContent = message || '';
      el.hidden = !message;
    }
    const target = name === 'towns' ? home : name === 'topics' ? topicBoxes[0] : form.elements[name];
    if (target && target.setAttribute) {
      if (message) target.setAttribute('aria-invalid', 'true');
      else target.removeAttribute('aria-invalid');
    }
    if (message && name === 'webhook_url') $('hook-details').open = true;
  }

  // ---------- data
  const loadTowns = fetch('/data/towns.json').then((r) => r.json()).then((doc) => {
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
  });
  const loadNeighbors = fetch('/data/neighbors.json')
    .then((r) => r.json().catch(() => ({})).then((d) => (r.ok ? d : {})))
    .catch(() => ({}))
    .then((doc) => { neighbors = doc && typeof doc === 'object' ? doc : {}; });
  fetch('/api/status', { headers: { Accept: 'application/json' } })
    .then((r) => r.json().catch(() => ({})).then((d) => (r.ok ? d : {})))
    .catch(() => ({}))
    .then((s) => { $('email-option').hidden = !(s && s.email_alerts === true); });

  // ---------- reading step 1
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
    const lab = document.createElement('label');
    lab.className = 'check';
    const box = document.createElement('input');
    box.type = 'checkbox';
    box.name = name;
    box.value = value;
    box.checked = checked;
    const span = document.createElement('span');
    span.textContent = text;
    lab.append(box, span);
    li.append(lab);
    return li;
  }

  const area = (id) => (neighbors && neighbors[id]) || [];
  const notRead = (id) => byId.has(id) && byId.get(id).monitored === false;

  // A home town we can't read yet: say so, and offer to ask for it.
  function showRequest(id) {
    const box = $('home-request');
    if (!id || !notRead(id)) {
      box.hidden = true;
      return;
    }
    $('home-request-text').textContent = `We can’t read ${label(id)}’s agendas yet. Its alerts start once we can; items from the towns next to it still come. Want ${label(id)} covered?`;
    $('home-request-btn').textContent = `Request ${label(id)}`;
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
      setStatus(out, 'Request sent. Thank you.', 'ok');
    } catch (err) {
      setStatus(out, err.message, 'err');
      button.disabled = false;
    }
  });

  function setHome(id, checkedNear) {
    homeId = id;
    $('home-name').textContent = id ? label(id) : 'your town';
    if (!id) {
      showRequest(null);
      nearList.replaceChildren();
      nearNote.textContent = 'Pick your town first. Its neighbors show up here, all included.';
      return;
    }
    const near = area(id);
    const first = checkbox('home', id, `${label(id)} (your town${notRead(id) ? ', not read yet' : ''})`, true);
    first.querySelector('input').disabled = true;
    nearList.replaceChildren(first, ...near.map((n) => checkbox('towns', n,
      `${label(n)} (next to ${label(id)}${notRead(n) ? ', not read yet' : ''})`, checkedNear ? checkedNear.includes(n) : true)));
    showRequest(id);
    nearNote.textContent = near.length
      ? `${label(id)} and the ${near.length === 1 ? 'town' : `${near.length} towns`} next to it are included. Untick any you don’t want.`
      : (neighbors && Object.keys(neighbors).length
        ? `We don’t have neighbors listed for ${label(id)}, so these alerts cover ${label(id)} only.`
        : `We couldn’t load the towns next to ${label(id)} right now. These alerts will cover ${label(id)}; you can add its neighbors later by editing them.`);
    fieldError('towns', '');
  }

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
    if (first !== homeId || others.length) setHome(first, others.length ? others : null);
    // Typed topics narrow the topics; clearing them brings back all topics.
    if (topics.length) {
      for (const t of topicBoxes) t.checked = topics.includes(t.value);
      topicsFromText = true;
      fieldError('topics', '');
    } else if (topicsFromText) {
      for (const t of topicBoxes) t.checked = true;
      topicsFromText = false;
    }

    if (!text.trim()) {
      read.textContent = DEFAULT_READ;
      return;
    }
    const parts = [];
    const b = (s) => {
      const el = document.createElement('b');
      el.textContent = s;
      return el;
    };
    const outside = first ? others.filter((o) => !area(first).includes(o)) : [];
    if (first) {
      const chosenTopics = topicBoxes.filter((t) => t.checked);
      const what = chosenTopics.length === topicBoxes.length ? 'every topic'
        : joinAnd(chosenTopics.map((t) => t.closest('label').querySelector('span').firstChild.textContent.trim().toLowerCase()));
      const near = Array.from(nearList.querySelectorAll('input[name="towns"]:checked')).map((x) => x.value);
      const where = others.length
        ? joinAnd([first, ...others.filter((o) => near.includes(o))].map(label))
        : (near.length ? `${label(first)} and the ${near.length === 1 ? 'town' : `${near.length} towns`} next to it` : label(first));
      parts.push('Alerts for ', b(what), ' in ', b(where), '.');
    } else {
      parts.push('Pick your town from the list.');
    }
    if (outside.length) {
      parts.push(` ${joinAnd(outside.map(label))} ${outside.length === 1 ? 'isn’t' : 'aren’t'} next to ${label(first)}. Free alerts cover one town and the towns next to it.`);
    }
    if (left.length) parts.push(` We didn’t find a town or topic called “${left.slice(0, 3).join('”, “')}”. Check the spelling.`);
    read.replaceChildren(...parts.map((p) => (typeof p === 'string' ? document.createTextNode(p) : p)));
  }

  // ---------- wiring
  home.addEventListener('input', () => Promise.all([loadTowns, loadNeighbors]).then(readHome));
  nearList.addEventListener('change', () => { if (home.value.trim()) readHome(); });
  for (const t of topicBoxes) t.addEventListener('change', () => { topicsFromText = false; fieldError('topics', ''); });

  function payload() {
    const chosen = Array.from(form.querySelectorAll('#near-list input[name="towns"]:checked, #extra-list input[name="towns"]:checked')).map((b) => b.value);
    const data = {
      name: form.elements.name.value,
      towns: homeId ? [homeId, ...chosen.filter((t) => t !== homeId)] : chosen,
      topics: topicBoxes.filter((t) => t.checked).map((t) => t.value),
      webhook_format: form.elements.webhook_format.value,
      website: form.elements.website.value,
    };
    if (homeId) data.home_town = homeId;
    const url = webhook.value.trim();
    if (!editId || url) data.webhook_url = url;
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
      fieldError('email', 'Check the email address. It should look like name@example.com.');
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
      const err = new Error(data.error || 'The server didn’t answer as expected. Try again in a minute.');
      err.fields = data.fields || {};
      throw err;
    }
    return data;
  }

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    await Promise.all([loadTowns, loadNeighbors]);
    if (home.value.trim() && !homeId) readHome();
    const data = payload();
    for (const f of ['towns', 'topics', 'webhook_url', 'email']) fieldError(f, '');
    if (!validate(data)) {
      setStatus(status, 'Check the highlighted steps, then try again.', 'err');
      return;
    }
    submit.disabled = true;
    setStatus(status, editId ? 'Saving…' : 'Creating your alerts…');
    try {
      const result = editId
        ? await send('PATCH', `/api/watchlists?id=${encodeURIComponent(editId)}`, data)
        : await send('POST', '/api/watchlists', data);
      const id = editId || result.id;
      if (!id) throw new Error('The server didn’t answer as expected. Try again in a minute.');
      window.w351.remember(id, data.name);
      setStatus(status, editId ? 'Changes saved. Opening your alerts…' : 'Alerts created. Opening them…', 'ok');
      const flags = [editId ? '' : 'new=1', data.email ? 'email=1' : ''].filter(Boolean).join('&');
      location.assign(`/w/${id}${flags ? `?${flags}` : ''}`);
    } catch (err) {
      for (const [field, message] of Object.entries(err.fields || {})) fieldError(field === 'home_town' ? 'towns' : field, message);
      setStatus(status, err.message, 'err');
      submit.disabled = false;
    }
  });

  $('send-test').addEventListener('click', async (event) => {
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
      setStatus(testStatus, 'Test message sent. Check your channel.', 'ok');
    } catch (err) {
      if (err.fields && err.fields.webhook_url) fieldError('webhook_url', err.fields.webhook_url);
      setStatus(testStatus, err.message, 'err');
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
      a.textContent = l.name || 'Untitled alert list';
      li.append(a);
      if (l.readonly) li.append(' (shared with you, read-only)');
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
    }
    if (topicKeys.length && topicBoxes.some((t) => topicKeys.includes(t.value))) {
      for (const t of topicBoxes) t.checked = topicKeys.includes(t.value);
    }
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
      form.elements.name.value = wl.name || '';
      const first = wl.home_town && wl.towns.includes(wl.home_town) ? wl.home_town : wl.towns[0];
      prefill([first, ...wl.towns.filter((t) => t !== first)], wl.topics);
      for (const t of topicBoxes) t.checked = wl.topics.includes(t.value);
      if (wl.webhook && wl.webhook.configured) {
        webhook.placeholder = `Saved: ${wl.webhook.masked}. Leave blank to keep it.`;
        form.elements.webhook_format.value = wl.webhook.format || 'auto';
        $('webhook-remove-row').hidden = false;
        $('hook-details').open = true;
      }
      if (wl.email && wl.email.configured) {
        email.placeholder = `Saved: ${wl.email.masked}. Leave blank to keep it.`;
        $('email-remove-row').hidden = false;
      }
      submit.disabled = false;
    } catch (err) {
      const box = $('watch-error');
      box.textContent = `${err.message} You can set up new alerts below.`;
      box.hidden = false;
      $('edit-banner').hidden = true;
      editId = null;
      submit.textContent = 'Create alerts';
      submit.disabled = false;
    }
  }

  showMyLists();
  if (editId) loadForEdit();
  else {
    Promise.all([loadTowns, loadNeighbors]).then(() => {
      const ids = params.getAll('town').flatMap((v) => v.split(',')).map((v) => (v.includes(':') ? v : `MA:${v}`));
      prefill(ids, params.getAll('topic').flatMap((v) => v.split(',')).filter(Boolean));
    });
  }
})();
