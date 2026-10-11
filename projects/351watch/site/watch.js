// /watch: create a watchlist (or edit one with ?edit=<id>). Prefill with ?town=MA:Amherst&topic=data_center.
(() => {
  const form = document.getElementById('watch-form');
  if (!form) return;
  const MAX_TOWNS = 200;
  const CHIP_LIMIT = 40;
  const $ = (id) => document.getElementById(id);
  const params = new URLSearchParams(location.search);
  let editId = /^[A-Za-z0-9_-]{24,64}$/.test(params.get('edit') || '') ? params.get('edit') : null;

  const list = $('town-list');
  const boxes = Array.from(list.querySelectorAll('input[name="towns"]'));
  const rows = boxes.map((b) => b.closest('li'));
  const topicBoxes = Array.from(form.querySelectorAll('input[name="topics"]'));
  const search = $('town-search');
  const show = $('town-show');
  const count = $('town-count');
  const chips = $('town-chips');
  const empty = $('town-empty');
  const submit = $('watch-submit');
  const status = $('watch-status');
  const testStatus = $('test-status');
  const webhook = $('webhook-url');
  const removeHook = $('webhook-remove');
  const byLower = new Map(boxes.map((b) => [b.value.toLowerCase(), b]));

  const selected = () => boxes.filter((b) => b.checked);

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
    const target = name === 'towns' ? search : name === 'topics' ? topicBoxes[0] : form.elements[name];
    if (target && target.setAttribute) {
      if (message) target.setAttribute('aria-invalid', 'true');
      else target.removeAttribute('aria-invalid');
    }
  }

  function renderSelection() {
    const chosen = selected();
    const n = chosen.length;
    count.textContent = n
      ? `${n} town${n === 1 ? '' : 's'} selected${n > MAX_TOWNS ? ` (the limit is ${MAX_TOWNS})` : ''}`
      : 'No towns selected';
    const nodes = chosen.slice(0, CHIP_LIMIT).map((b) => {
      const chip = document.createElement('button');
      chip.type = 'button';
      chip.className = 'chip';
      chip.textContent = `${b.dataset.label} ×`;
      chip.setAttribute('aria-label', `Remove ${b.dataset.label}`);
      chip.addEventListener('click', () => {
        b.checked = false;
        renderSelection();
        if (show.value === 'selected') applyFilter();
        (chips.querySelector('.chip') || search).focus();
      });
      return chip;
    });
    if (n > CHIP_LIMIT) {
      const more = document.createElement('span');
      more.className = 'chip more';
      more.textContent = `+${n - CHIP_LIMIT} more`;
      nodes.push(more);
    }
    chips.replaceChildren(...nodes);
    if (n) fieldError('towns', '');
  }

  function applyFilter() {
    const q = search.value.trim().toLowerCase();
    const mode = show.value;
    let shown = 0;
    rows.forEach((li, i) => {
      const ok = (!q || li.dataset.search.includes(q)) &&
        (mode !== 'monitored' || li.dataset.monitored === '1') &&
        (mode !== 'selected' || boxes[i].checked);
      li.hidden = !ok;
      if (ok) shown += 1;
    });
    for (const group of list.querySelectorAll('.state-group')) group.hidden = !group.querySelector('li:not([hidden])');
    empty.hidden = shown > 0;
  }

  function setTowns(values) {
    const wanted = new Set();
    for (const raw of values) {
      const v = raw.trim().toLowerCase();
      if (!v) continue;
      const box = byLower.get(v.includes(':') ? v : `ma:${v}`);
      if (box) wanted.add(box);
    }
    if (!wanted.size) return false;
    for (const b of boxes) b.checked = wanted.has(b);
    return true;
  }

  function setTopics(values) {
    const wanted = new Set(values.map((v) => v.trim()).filter(Boolean));
    if (!topicBoxes.some((t) => wanted.has(t.value))) return;
    for (const t of topicBoxes) t.checked = wanted.has(t.value);
  }

  list.addEventListener('change', (event) => {
    if (event.target.name === 'towns') renderSelection();
  });
  search.addEventListener('input', applyFilter);
  show.addEventListener('change', applyFilter);
  $('select-shown').addEventListener('click', () => {
    let n = selected().length;
    for (const [i, li] of rows.entries()) {
      if (li.hidden || boxes[i].checked) continue;
      if (n >= MAX_TOWNS) break;
      boxes[i].checked = true;
      n += 1;
    }
    renderSelection();
  });
  $('clear-towns').addEventListener('click', () => {
    for (const b of boxes) b.checked = false;
    renderSelection();
    applyFilter();
  });
  for (const t of topicBoxes) t.addEventListener('change', () => fieldError('topics', ''));

  function payload() {
    const data = {
      name: form.elements.name.value,
      towns: selected().map((b) => b.value),
      topics: topicBoxes.filter((t) => t.checked).map((t) => t.value),
      webhook_format: form.elements.webhook_format.value,
      website: form.elements.website.value,
    };
    const url = webhook.value.trim();
    if (!editId || url) data.webhook_url = url;
    else if (removeHook && removeHook.checked) data.webhook_url = '';
    return data;
  }

  function validate(data) {
    let ok = true;
    if (!data.towns.length) {
      fieldError('towns', 'Choose at least one town.');
      ok = false;
    } else if (data.towns.length > MAX_TOWNS) {
      fieldError('towns', `Choose up to ${MAX_TOWNS} towns.`);
      ok = false;
    }
    if (!data.topics.length) {
      fieldError('topics', 'Choose at least one topic.');
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
      const err = new Error(data.error || 'Something went wrong. Please try again.');
      err.fields = data.fields || {};
      throw err;
    }
    return data;
  }

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const data = payload();
    for (const f of ['towns', 'topics', 'webhook_url']) fieldError(f, '');
    if (!validate(data)) {
      setStatus(status, 'Please fix the highlighted fields.', 'err');
      return;
    }
    submit.disabled = true;
    setStatus(status, editId ? 'Saving…' : 'Creating your watchlist…');
    try {
      const result = editId
        ? await send('PATCH', `/api/watchlists?id=${encodeURIComponent(editId)}`, data)
        : await send('POST', '/api/watchlists', data);
      const id = editId || result.id;
      if (!id) throw new Error('Something went wrong. Please try again.');
      window.w351.remember(id, data.name);
      setStatus(status, editId ? 'Saved. Opening your watchlist…' : 'Created. Opening your watchlist…', 'ok');
      location.assign(`/w/${id}`);
    } catch (err) {
      for (const [field, message] of Object.entries(err.fields || {})) fieldError(field, message);
      setStatus(status, err.message, 'err');
      submit.disabled = false;
    }
  });

  $('send-test').addEventListener('click', async (event) => {
    const button = event.currentTarget;
    const url = webhook.value.trim();
    fieldError('webhook_url', '');
    if (!url && !editId) {
      setStatus(testStatus, 'Enter a webhook URL first.', 'err');
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
    const ul = $('my-lists-items');
    ul.replaceChildren(...lists.map((l) => {
      const li = document.createElement('li');
      const a = document.createElement('a');
      a.href = `/w/${l.id}`;
      a.textContent = l.name || 'Untitled watchlist';
      li.append(a);
      return li;
    }));
    $('my-lists').hidden = false;
  }

  async function loadForEdit() {
    $('edit-banner').hidden = false;
    submit.textContent = 'Save changes';
    submit.disabled = true;
    try {
      const { watchlist: wl } = await send('GET', `/api/watchlists?id=${encodeURIComponent(editId)}`);
      $('edit-name').textContent = wl.name || 'your watchlist';
      document.title = `Edit ${wl.name || 'watchlist'} | 351 Watch`;
      form.elements.name.value = wl.name || '';
      setTowns(wl.towns);
      for (const t of topicBoxes) t.checked = wl.topics.includes(t.value);
      renderSelection();
      applyFilter();
      if (wl.webhook && wl.webhook.configured) {
        webhook.placeholder = `Saved: ${wl.webhook.masked}. Leave blank to keep it.`;
        form.elements.webhook_format.value = wl.webhook.format || 'auto';
        $('webhook-remove-row').hidden = false;
      }
      submit.disabled = false;
    } catch (err) {
      const box = $('watch-error');
      box.textContent = `${err.message} You can create a new watchlist below.`;
      box.hidden = false;
      $('edit-banner').hidden = true;
      editId = null;
      submit.textContent = 'Create watchlist';
      submit.disabled = false;
    }
  }

  setTopics(params.getAll('topic').flatMap((v) => v.split(',')));
  setTowns(params.getAll('town').flatMap((v) => v.split(',')));
  renderSelection();
  applyFilter();
  showMyLists();
  if (editId) loadForEdit();
})();
