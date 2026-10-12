// Shared behavior on every page: the town box, list and table filters, the contact form,
// and the list of alert lists made in this browser.

const norm = (s) => String(s || '').toLowerCase().replace(/[’']/g, '').replace(/[^a-z0-9]+/g, ' ').trim();

// Town box: <form data-town-form> with an input tied to <datalist id="town-names">, whose options
// carry data-href. A unique match goes straight to the town's page; anything else falls back to
// the form's own GET to /towns?q=..., which lists matching towns.
function setupTownBox() {
  const list = document.getElementById('town-names');
  for (const form of document.querySelectorAll('form[data-town-form]')) {
    const input = form.querySelector('input');
    const error = form.querySelector('.field-error');
    if (!list || !input) continue;
    const towns = Array.from(list.options).map((o) => {
      const [name, state] = o.value.split(/,\s*/);
      return { name: norm(name), full: norm(o.value), state: norm(state || 'ma'), href: o.dataset.href };
    });
    form.addEventListener('submit', (event) => {
      const q = norm(input.value);
      if (!q) {
        event.preventDefault();
        if (error) {
          error.textContent = 'Type a town name, like Carver.';
          error.hidden = false;
        }
        input.focus();
        return;
      }
      let hits = towns.filter((t) => t.full === q);
      if (!hits.length) hits = towns.filter((t) => t.name === q);
      if (!hits.length) hits = towns.filter((t) => `${t.name} ${t.state}` === q || `${t.name} ${stateName(t.state)}` === q);
      if (hits.length > 1) hits = hits.filter((t) => t.state === 'ma');
      if (hits.length === 1) {
        event.preventDefault();
        location.assign(hits[0].href);
      }
    });
    input.addEventListener('input', () => {
      if (error) error.hidden = true;
    });
  }
}

function stateName(code) {
  return { ma: 'massachusetts', ny: 'new york', ri: 'rhode island' }[code] || code;
}

// /towns: <form data-list-filter> filters every ul[data-filter-list] li by data-search and data-status.
function setupListFilter() {
  const form = document.querySelector('form[data-list-filter]');
  if (!form) return;
  const search = form.querySelector('[data-search]');
  const status = form.querySelector('[data-status]');
  const count = form.querySelector('[data-count]');
  const empty = document.querySelector('[data-empty]');
  const items = Array.from(document.querySelectorAll('[data-filter-list] li'));
  const params = new URLSearchParams(location.search);
  if (params.get('q')) search.value = params.get('q');

  const apply = () => {
    const q = norm(search.value);
    const s = status.value;
    let shown = 0;
    for (const li of items) {
      const ok = (!q || norm(li.dataset.search).includes(q)) &&
        (!s || li.dataset.status === s || (s === 'monitored' && li.dataset.status === 'up'));
      li.hidden = !ok;
      if (ok) shown += 1;
    }
    for (const section of document.querySelectorAll('.state-towns')) {
      section.hidden = !section.querySelector('li:not([hidden])');
    }
    count.textContent = shown === items.length ? `${items.length} towns` : `${shown} of ${items.length} towns`;
    if (empty) empty.hidden = shown > 0;
  };
  form.addEventListener('submit', (event) => event.preventDefault());
  search.addEventListener('input', apply);
  status.addEventListener('change', apply);
  apply();
}

// The local actions table on /attorney-general.
function setupTrackerFilter() {
  const table = document.querySelector('#tracker-table');
  if (!table) return;
  const rows = Array.from(table.querySelectorAll('tbody tr'));
  const status = document.querySelector('#f-status');
  const topic = document.querySelector('#f-topic');
  const county = document.querySelector('#f-county');
  const search = document.querySelector('#f-search');
  const count = document.querySelector('#f-count');

  function apply() {
    const q = search.value.trim().toLowerCase();
    let shown = 0;
    for (const row of rows) {
      const match =
        (!status.value || row.dataset.group === status.value) &&
        (!topic.value || row.dataset.topic.includes(topic.value)) &&
        (!county.value || row.dataset.county === county.value) &&
        (!q || row.textContent.toLowerCase().includes(q));
      row.hidden = !match;
      if (match) shown += 1;
    }
    count.textContent = `${shown} of ${rows.length} shown`;
  }

  for (const el of [status, topic, county]) el.addEventListener('change', apply);
  search.addEventListener('input', apply);
  apply();
}

// <div class="filterbar" data-filters="G"> with <select data-key="k"> filters rows of every
// table[data-filter-group="G"] by their data-k attribute; [data-search] matches row text.
function setupGenericFilters() {
  for (const bar of document.querySelectorAll('[data-filters]')) {
    const group = bar.dataset.filters;
    const rows = Array.from(document.querySelectorAll(`table[data-filter-group="${group}"] tbody tr`));
    const text = rows.map((r) => r.textContent.toLowerCase());
    const selects = Array.from(bar.querySelectorAll('select[data-key]'));
    const search = bar.querySelector('[data-search]');
    const count = bar.querySelector('[data-count]');

    const apply = () => {
      const q = search ? search.value.trim().toLowerCase() : '';
      let shown = 0;
      rows.forEach((row, i) => {
        const match = selects.every((s) => !s.value || row.dataset[s.dataset.key] === s.value) && (!q || text[i].includes(q));
        row.hidden = !match;
        if (match) shown += 1;
      });
      if (count) count.textContent = `${shown} of ${rows.length} shown`;
    };
    for (const s of selects) s.addEventListener('change', apply);
    if (search) search.addEventListener('input', apply);
    apply();
  }
}

function setupContactForm() {
  const form = document.querySelector('#contact-form');
  if (!form) return;
  const status = form.querySelector('.form-status');
  const button = form.querySelector('button[type="submit"]');

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    status.className = 'form-status';
    status.textContent = '';
    if (!form.elements.message.value.trim()) {
      status.classList.add('err');
      status.textContent = 'Write a message first.';
      form.elements.message.focus();
      return;
    }
    button.disabled = true;
    status.textContent = 'Sending…';
    const payload = { ...Object.fromEntries(new FormData(form).entries()), page: document.referrer.slice(0, 200) };
    try {
      const res = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok || !data.ok) throw new Error(data.error || 'The message didn’t go through. Try again in a minute.');
      form.reset();
      status.classList.add('ok');
      status.textContent = 'Message sent. Thank you.';
    } catch (err) {
      status.classList.add('err');
      status.textContent = err.message;
    } finally {
      button.disabled = false;
    }
  });
}

// /search: site/search.js renders li.result items. Split the meta line into separate parts instead
// of dot-joined text, and mark meetings that are still ahead.
// Search excerpts: keep the sentence with the first match (and the next one if that sentence is short).
function trimToSentence(node) {
  const parts = [...node.childNodes].map((n) => ({ text: n.textContent, mark: n.nodeName === 'MARK' }));
  const full = parts.map((p) => p.text).join('');
  let pos = 0;
  let first = -1;
  let last = -1;
  for (const p of parts) {
    if (p.mark && first < 0) first = pos;
    if (p.mark && first >= 0 && pos < first + 160) last = pos + p.text.length;
    pos += p.text.length;
  }
  if (first < 0) return;
  const lead = full.slice(0, first).match(/^[\s\S]*[.;!?]\s+/);
  const start = lead ? lead[0].length : 0;
  const stop = (from) => {
    const i = full.slice(from).search(/[.;!?](?:\s|$)/);
    return i >= 0 ? from + i + 1 : full.length;
  };
  let end = stop(last);
  if (end - start < 60) end = stop(end);
  if (start === 0 && end >= full.length) return;
  const out = [];
  pos = 0;
  for (const p of parts) {
    const a = Math.max(start, pos);
    const b = Math.min(end, pos + p.text.length);
    if (a < b) {
      const t = p.text.slice(a - pos, b - pos);
      if (p.mark) {
        const mark = document.createElement('mark');
        mark.textContent = t;
        out.push(mark);
      } else out.push(document.createTextNode(t));
    }
    pos += p.text.length;
  }
  if (start > 0) out.unshift(document.createTextNode('…'));
  if (end < full.length) out.push(document.createTextNode('…'));
  node.replaceChildren(...out);
}

function setupSearchResults() {
  const list = document.getElementById('search-results');
  if (!list || !window.MutationObserver) return;
  const dress = (li) => {
    if (li.dataset.dressed) return;
    li.dataset.dressed = '1';
    const snippet = li.querySelector('.result-snippet');
    if (snippet) trimToSentence(snippet);
    const meta = li.querySelector('.result-meta');
    if (meta && meta.textContent.includes(' · ')) { // slop-lint: ignore (splits search.js's dot-joined meta)
      meta.replaceChildren(...meta.textContent.split(' · ').map((part) => { // slop-lint: ignore
        const span = document.createElement('span');
        const upcoming = part.endsWith(' (upcoming)');
        span.textContent = upcoming ? part.slice(0, -' (upcoming)'.length) : part;
        if (upcoming) {
          const badge = document.createElement('strong');
          badge.className = 'result-upcoming';
          badge.textContent = 'coming up';
          span.append(' ', badge);
        }
        return span;
      }));
    }
  };
  // "Get these by email" right above the results, carrying the town and topic filters to /watch.
  const alert = document.getElementById('search-alert');
  const form = document.getElementById('search-form');
  const syncAlert = () => {
    if (!alert || !form) return;
    const town = form.elements.town && form.elements.town.value;
    const topic = form.elements.topic && form.elements.topic.value;
    const q = new URLSearchParams();
    if (town) q.set('town', town);
    if (topic) q.set('topic', topic);
    const link = alert.querySelector('a');
    link.href = `/watch${q.toString() ? `?${q}` : ''}`;
    const name = town ? form.elements.town.selectedOptions[0].textContent : '';
    link.textContent = name ? `Get ${name} alerts by email` : 'Get alerts for your town by email';
    alert.hidden = !list.querySelector('li.result');
  };
  if (form) form.addEventListener('change', syncAlert);
  new MutationObserver((changes) => {
    for (const c of changes) for (const n of c.addedNodes) if (n.nodeType === 1 && n.matches('li.result')) dress(n);
    syncAlert();
  }).observe(list, { childList: true });
  syncAlert();
}

// "(starting soon)" notes next to email: hidden once /api/status reports email alerts are on.
function setupEmailNotes() {
  const notes = document.querySelectorAll('[data-email-soon]');
  if (!notes.length) return;
  fetch('/api/status', { headers: { Accept: 'application/json' } })
    .then((r) => r.json().catch(() => ({})).then((d) => (r.ok ? d : {})))
    .then((s) => { if (s && s.email_alerts === true) for (const n of notes) n.hidden = true; })
    .catch(() => {});
}

// "Request this town" for towns we can't read yet: a message through the contact endpoint.
async function requestTown(id, name) {
  const res = await fetch('/api/contact', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ kind: 'message', message: `Please add ${name} (${id}). We can't check its agendas yet.`, page: location.pathname }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok || !data.ok) throw new Error(data.error || 'The request didn’t go through. Try again in a minute.');
}
function setupRequestButtons() {
  for (const box of document.querySelectorAll('[data-request-town]')) {
    const button = box.querySelector('button');
    const out = box.querySelector('.form-status');
    button.addEventListener('click', async () => {
      button.disabled = true;
      out.className = 'form-status';
      out.textContent = 'Sending…';
      try {
        await requestTown(box.dataset.requestTown, box.dataset.townName);
        out.classList.add('ok');
        out.textContent = 'Thanks. We’ve got your request and will ask the town hall.';
      } catch (err) {
        out.classList.add('err');
        out.textContent = err.message;
        button.disabled = false;
      }
    });
  }
}

// Details on demand: a link to something inside a closed <details> opens it, and search filters
// start open when the URL already uses one.
function openTarget() {
  const id = decodeURIComponent(location.hash.slice(1));
  const el = id && document.getElementById(id);
  if (!el) return;
  for (let d = el.closest('details'); d; d = d.parentElement && d.parentElement.closest('details')) d.open = true;
  const next = el.nextElementSibling;
  if (el.matches('h2') && next && next.matches('details') && el.closest('section')) {
    for (const d of el.closest('section').querySelectorAll(':scope > details')) d.open = true;
  }
}
function setupDisclosure() {
  openTarget();
  window.addEventListener('hashchange', openTarget);
  const filters = document.getElementById('search-filters');
  if (filters) {
    const p = new URLSearchParams(location.search);
    if (['state', 'town', 'topic', 'board', 'sort', 'upcoming'].some((k) => p.get(k))) filters.open = true;
  }
}

// Old links to the tracker that used to live on the home page.
function followOldAnchors() {
  if (location.pathname === '/' && location.hash === '#tracker') location.replace('/attorney-general#tracker');
}

// Alert lists made or opened in this browser (a per-viewer convenience; may be unavailable).
// Entries keep the private key when this browser has it, so the owner can find the manage page again.
const LISTS_KEY = '351watch:lists';
const AREAS_KEY = 'agendaahead:areas';
window.w351 = {
  recall() {
    try {
      const lists = JSON.parse(localStorage.getItem(LISTS_KEY) || '[]');
      return Array.isArray(lists) ? lists.filter((l) => l && typeof l.id === 'string') : [];
    } catch {
      return [];
    }
  },
  remember(id, name, readonly = false) {
    try {
      const lists = this.recall().filter((l) => l.id !== id);
      lists.unshift({ id, name: name || '', readonly: Boolean(readonly), at: new Date().toISOString() });
      localStorage.setItem(LISTS_KEY, JSON.stringify(lists.slice(0, 20)));
    } catch {
      /* storage unavailable */
    }
  },
  requestTown,
  // The visitor's own towns (home town first), saved when they set up alerts. Pages may use them to
  // put those towns first; nothing leaves the browser.
  saveAreas(homeTown, towns, topics) {
    try {
      const list = [homeTown, ...(towns || []).filter((t) => t !== homeTown)].filter((t) => typeof t === 'string' && t.includes(':'));
      const doc = { home_town: list[0], towns: list.slice(0, 40) };
      if (Array.isArray(topics) && topics.length) doc.topics = topics.slice(0, 20); // only when some subjects were left out
      if (list.length) localStorage.setItem(AREAS_KEY, JSON.stringify(doc));
    } catch {
      /* storage unavailable */
    }
  },
  areas() {
    try {
      const doc = JSON.parse(localStorage.getItem(AREAS_KEY) || 'null');
      return doc && typeof doc.home_town === 'string' && Array.isArray(doc.towns) ? doc : null;
    } catch {
      return null;
    }
  },
  relDates,
  forget(id) {
    try {
      localStorage.setItem(LISTS_KEY, JSON.stringify(this.recall().filter((l) => l.id !== id)));
    } catch {
      /* storage unavailable */
    }
  },
};

// Meeting days said the way people say them: "Today, Oct 12", "Tomorrow, Oct 13", "Saturday, Oct 17",
// counted in Boston time; a story whose meeting has passed is hidden.
function relDates(root = document) {
  const today = new Intl.DateTimeFormat('en-CA', { timeZone: 'America/New_York', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date());
  for (const t of root.querySelectorAll('time[data-rel]')) {
    const iso = t.getAttribute('datetime') || '';
    const days = Math.round((Date.parse(`${iso}T12:00:00Z`) - Date.parse(`${today}T12:00:00Z`)) / 86400000);
    if (Number.isNaN(days)) continue;
    if (days < 0) {
      const story = t.closest('.story');
      if (story) story.hidden = true;
      continue;
    }
    if (days > 6) continue;
    const d = new Date(`${iso}T12:00:00Z`);
    const md = d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', timeZone: 'UTC' });
    const name = days === 0 ? 'Today' : days === 1 ? 'Tomorrow' : d.toLocaleDateString('en-US', { weekday: 'long', timeZone: 'UTC' });
    t.textContent = `${name}, ${md}`;
  }
}

// "Copy citation" and "Share this meeting": buttons that need JavaScript, so they start hidden.
async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    const tmp = document.createElement('textarea');
    tmp.value = text;
    tmp.setAttribute('readonly', '');
    tmp.className = 'sr-only';
    document.body.append(tmp);
    tmp.select();
    const ok = document.execCommand('copy');
    tmp.remove();
    return ok;
  }
}
function flash(button, text) {
  const was = button.dataset.label || button.textContent;
  button.dataset.label = was;
  button.textContent = text;
  setTimeout(() => { button.textContent = was; }, 2000);
}
function setupCopyAndShare() {
  document.addEventListener('click', async (event) => {
    const copy = event.target.closest('[data-copy]');
    if (copy) {
      flash(copy, (await copyText(copy.dataset.copy)) ? 'Copied' : 'Couldn’t copy');
      return;
    }
    const share = event.target.closest('[data-share]');
    if (!share) return;
    const data = { title: share.dataset.title, text: share.dataset.text, url: share.dataset.url };
    if (navigator.share) {
      try {
        await navigator.share(data);
      } catch {
        /* closed without sharing */
      }
      return;
    }
    flash(share, (await copyText(data.url)) ? 'Link copied' : 'Couldn’t copy the link');
  });
  for (const b of document.querySelectorAll('[data-copy][hidden], [data-share][hidden]')) b.hidden = false;
}

followOldAnchors();
setupTownBox();
setupListFilter();
setupTrackerFilter();
setupGenericFilters();
setupContactForm();
setupSearchResults();
setupEmailNotes();
setupRequestButtons();
setupDisclosure();
setupCopyAndShare();
relDates();
