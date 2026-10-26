// Shared behavior on every page: the town box, list and table filters, the contact form,
// and the list of alert lists made in this browser.

const norm = (s) => String(s || '').toLowerCase().replace(/[’']/g, '').replace(/[^a-z0-9]+/g, ' ').trim();

// Town box: <form data-town-form> with an input tied to <datalist id="town-names">, whose options
// carry data-href and data-up (meetings coming up). With a <ul class="suggest"> beside the input,
// the browser's own popup is replaced by a visible list of up to eight towns, each a full tap row,
// with arrow keys, Enter and Escape (the GOV.UK accessible-autocomplete pattern). A unique match
// goes straight to the town's page; a name shared by two states asks which; anything else falls
// back to the form's own GET to /towns?q=..., which lists matching towns.
function setupTownBox() {
  const list = document.getElementById('town-names');
  // A form goes to the town's page; a box with data-town-box="pick" (the alerts page) fills its input instead.
  for (const form of document.querySelectorAll('form[data-town-form], [data-town-box]')) {
    const input = form.querySelector('input');
    const error = form.querySelector('.field-error');
    const box = form.querySelector('.suggest');
    const status = form.querySelector('[aria-live]');
    if (!list || !input) continue;
    const pick = form.dataset.townBox === 'pick';
    // The alerts page fills the list after loading its towns, so read it when needed, not once at start.
    let towns = [];
    let read = -1;
    const allTowns = () => {
      if (list.options.length !== read) {
        read = list.options.length;
        towns = Array.from(list.options).map((o) => {
          const [name, state] = o.value.split(/,\s*/);
          return { label: name, name: norm(name), full: norm(o.value), state: (state || 'MA').toUpperCase(), st: norm(state || 'ma'),
            href: o.dataset.href, up: Number(o.dataset.up || 0) };
        });
      }
      return towns;
    };
    // Choosing a town: go to its page, or (on the alerts page) put its name in the box and let the page read it.
    const choose = (t) => {
      if (!pick) return location.assign(t.href);
      const twin = allTowns().some((o) => o !== t && o.name === t.name);
      input.value = twin ? `${t.label} ${t.state}` : t.label;
      close();
      input.dispatchEvent(new Event('input', { bubbles: true }));
      input.focus();
    };
    const say = (text) => { if (status) status.textContent = text; };
    const fail = (text) => {
      if (error) { error.textContent = text; error.hidden = false; }
    };
    // Exact name first, then names that start with the typed text, then names that contain it.
    const find = (q) => {
      const rank = (t) => (t.full === q || t.name === q ? 0 : t.name.startsWith(q) ? 1 : t.full.startsWith(q) ? 2 : t.name.includes(q) ? 3 : 9);
      return allTowns().map((t) => [rank(t), t]).filter(([r]) => r < 9)
        .sort((a, b) => a[0] - b[0] || a[1].name.localeCompare(b[1].name)).slice(0, 8).map(([, t]) => t);
    };
    let shown = [];
    let active = -1;
    const close = () => {
      if (!box) return;
      box.hidden = true;
      box.replaceChildren();
      input.setAttribute('aria-expanded', 'false');
      input.removeAttribute('aria-activedescendant');
      shown = [];
      active = -1;
    };
    const setActive = (i) => {
      active = i;
      Array.from(box.children).forEach((li, n) => li.setAttribute('aria-selected', String(n === i)));
      if (i >= 0) {
        input.setAttribute('aria-activedescendant', box.children[i].id);
        box.children[i].scrollIntoView({ block: 'nearest' });
      } else input.removeAttribute('aria-activedescendant');
    };
    const open = (matches) => {
      if (!box) return;
      shown = matches;
      box.replaceChildren(...matches.map((t, i) => {
        const li = document.createElement('li');
        li.id = `${input.id}-opt-${i}`;
        li.setAttribute('role', 'option');
        li.setAttribute('aria-selected', 'false');
        li.dataset.href = t.href || '';
        li.dataset.i = String(i);
        const name = document.createElement('span');
        name.className = 'name';
        name.textContent = t.label;
        const st = document.createElement('span');
        st.className = 'st';
        st.textContent = t.up ? `${t.state} · ${t.up} ${t.up === 1 ? 'meeting' : 'meetings'} coming up` : t.state;
        li.append(name, st);
        return li;
      }));
      box.hidden = false;
      input.setAttribute('aria-expanded', 'true');
      setActive(-1);
      say(`${matches.length} ${matches.length === 1 ? 'town matches' : 'towns match'}. Use the arrow keys, then Enter.`);
    };
    if (box) {
      input.removeAttribute('list');
      input.setAttribute('role', 'combobox');
      input.setAttribute('aria-autocomplete', 'list');
      input.setAttribute('aria-expanded', 'false');
      input.setAttribute('aria-controls', box.id);
      input.addEventListener('keydown', (event) => {
        if (box.hidden) return;
        if (event.key === 'ArrowDown') { event.preventDefault(); setActive(Math.min(active + 1, shown.length - 1)); }
        else if (event.key === 'ArrowUp') { event.preventDefault(); setActive(Math.max(active - 1, 0)); }
        else if (event.key === 'Escape') close();
        else if (event.key === 'Enter' && active >= 0) { event.preventDefault(); choose(shown[active]); }
      });
      input.addEventListener('blur', () => setTimeout(close, 150));
      box.addEventListener('mousedown', (event) => event.preventDefault());  // keep the input focused while tapping a row
      box.addEventListener('click', (event) => {
        const li = event.target.closest('li[data-i]');
        if (li && shown[Number(li.dataset.i)]) choose(shown[Number(li.dataset.i)]);
      });
    }
    if (pick) {
      input.addEventListener('input', () => {
        const q = norm(input.value);
        if (!q) return close();
        const matches = find(q);
        if (matches.length) open(matches);
        else close();
      });
      continue;
    }
    form.addEventListener('submit', (event) => {
      const q = norm(input.value);
      if (!q) {
        event.preventDefault();
        fail('Type a town name, like Carver.');
        input.focus();
        return;
      }
      let hits = allTowns().filter((t) => t.full === q);
      if (!hits.length) hits = allTowns().filter((t) => `${t.name} ${t.st}` === q || `${t.name} ${stateName(t.st)}` === q);
      if (!hits.length) hits = allTowns().filter((t) => t.name === q);
      if (hits.length > 1) {
        // The same name in two states: ask, rather than guess.
        event.preventDefault();
        const states = hits.map((t) => stateName(t.st).replace(/\b\w/g, (c) => c.toUpperCase()));
        fail(`${hits[0].label} is in ${states.slice(0, -1).join(', ')} and ${states[states.length - 1]}. Which one?`);
        open(hits);
        input.focus();
        return;
      }
      if (!hits.length) {
        const near = find(q);
        if (near.length === 1 || (near.length && near[0].name.startsWith(q) && !near[1].name.startsWith(q))) hits = [near[0]];
      }
      if (hits.length === 1) {
        event.preventDefault();
        location.assign(hits[0].href);
      }
    });
    input.addEventListener('input', () => {
      if (error) error.hidden = true;
      const q = norm(input.value);
      if (!q) return close();
      const matches = find(q);
      if (matches.length) open(matches);
      else {
        close();
        say('No town matches yet.');
      }
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
  const count = form.querySelector('[data-count]');
  const empty = document.querySelector('[data-empty]');
  const status = form.querySelector('[data-status]');
  const noun = form.dataset.noun || 'towns';
  const items = Array.from(document.querySelectorAll('[data-filter-list] li, [data-filter-list] tr[data-search]'));
  const groups = Array.from(document.querySelectorAll('details.state-towns, details.county'));
  const sections = Array.from(document.querySelectorAll('.rec-group'));
  const params = new URLSearchParams(location.search);
  if (params.get('q')) search.value = params.get('q');
  if (status && params.get('status') && [...status.options].some((o) => o.value === params.get('status'))) status.value = params.get('status');
  const keep = () => {
    const p = new URLSearchParams(location.search);
    if (search.value.trim()) p.set('q', search.value.trim()); else p.delete('q');
    if (status && status.value) p.set('status', status.value); else p.delete('status');
    const qs = p.toString();
    history.replaceState(null, '', location.pathname + (qs ? `?${qs}` : '') + location.hash);
  };

  const apply = () => {
    const q = norm(search.value);
    const want = status ? status.value : '';
    let shown = 0;
    for (const li of items) {
      const ok = (!q || norm(li.dataset.search).includes(q)) && (!want || li.dataset.status === want);
      li.hidden = !ok;
      if (ok) shown += 1;
    }
    // Typing opens every state and county with a match and hides the rest; with the box empty, states
    // are open on a wide screen and folded on a phone, counties folded until tapped.
    for (const group of groups) {
      const has = Boolean(group.querySelector('li:not([hidden])'));
      group.hidden = q ? !has : false;
      group.open = q ? has : false; // a state opens when someone taps it
    }
    for (const sec of sections) sec.hidden = !sec.querySelector('li:not([hidden])');
    count.textContent = (q || want) ? `${shown} of ${items.length} ${noun}` : '';
    if (empty) empty.hidden = shown > 0;
    keep();
  };
  form.addEventListener('submit', (event) => event.preventDefault());
  search.addEventListener('input', apply);
  if (status) status.addEventListener('change', apply);
  apply();
}

// The local actions table on /attorney-general.
function setupTrackerFilter() {
  const table = document.querySelector('#tracker-table');
  if (!table) return;
  const rows = Array.from(table.querySelectorAll('.rec'));
  const status = document.querySelector('#f-status');
  const topic = document.querySelector('#f-topic');
  const county = document.querySelector('#f-county');
  const search = document.querySelector('#f-search');
  const count = document.querySelector('#f-count');

  function apply() {
    const words = search.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
    let shown = 0;
    for (const row of rows) {
      const text = row.textContent.toLowerCase();
      const match =
        (!status.value || row.dataset.group === status.value) &&
        (!topic.value || row.dataset.topic.includes(topic.value)) &&
        (!county.value || row.dataset.county === county.value) &&
        words.every((w) => text.includes(w));
      row.hidden = !match;
      if (match) shown += 1;
    }
    const on = status.value || topic.value || county.value || words.length;
    count.textContent = on ? (shown ? `${shown} of ${rows.length} shown` : `None of the ${rows.length} match. Try fewer words or another filter.`) : '';
  }

  for (const el of [status, topic, county]) el.addEventListener('change', apply);
  search.addEventListener('input', apply);
  apply();
}

// <div class="filterbar" data-filters="G"> with <select data-key="k"> filters rows of every
// table[data-filter-group="G"] by their data-k attribute; [data-search] matches row text.
// a CSV file as its records (a quoted field may hold a comma, a quote or a line break), each kept as written
function csvRecords(text) {
  const out = [];
  let start = 0;
  let quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const c = text[i];
    if (c === '"') quoted = !quoted;
    else if (!quoted && (c === '\n' || c === '\r')) {
      if (i > start) out.push(text.slice(start, i));
      if (c === '\r' && text[i + 1] === '\n') i += 1;
      start = i + 1;
    }
  }
  if (start < text.length) out.push(text.slice(start));
  return out;
}

function setupGenericFilters() {
  for (const bar of document.querySelectorAll('[data-filters]')) {
    const group = bar.dataset.filters;
    const rows = Array.from(document.querySelectorAll(`[data-filter-group="${group}"] .rec`));
    const years = Array.from(document.querySelectorAll(`[data-filter-group="${group}"] [data-year-group]`));
    const text = rows.map((r) => r.textContent.toLowerCase());
    const selects = Array.from(bar.querySelectorAll('select[data-key]'));
    const search = bar.querySelector('[data-search]');
    const count = bar.querySelector('[data-count]');
    const params = new URLSearchParams(location.search);
    for (const s of selects) {
      const v = params.get(s.dataset.key);
      if (v && [...s.options].some((o) => o.value === v)) s.value = v;
    }
    if (search && params.get('q')) search.value = params.get('q');
    const head = document.querySelector(`[data-count-for="${group}"]`);
    const home = document.getElementById(group);
    const csv = document.querySelector(`a[data-csv-for="${group}"]`);
    if (csv) {
      // with a filter on, the download is the rows shown: the full file, cut to the rows' line numbers
      csv.addEventListener('click', async (ev) => {
        const keep = rows.filter((r) => !r.hidden && r.dataset.csv).map((r) => Number(r.dataset.csv));
        if (keep.length === rows.filter((r) => r.dataset.csv).length) return;
        ev.preventDefault();
        try {
          const all = await (await fetch(csv.getAttribute('href'))).text();
          const lines = csvRecords(all);
          const out = [lines[0], ...keep.sort((a, b) => a - b).map((i) => lines[i + 1])].join('\r\n') + '\r\n';
          const a = document.createElement('a');
          a.href = URL.createObjectURL(new Blob([out], { type: 'text/csv' }));
          a.download = 'rulings-filtered.csv';
          document.body.appendChild(a);
          a.click();
          a.remove();
        } catch (e) {
          location.href = csv.getAttribute('href');
        }
      });
    }
    const box = bar.closest('details');
    if (box && (selects.some((s) => s.value) || (search && search.value))) box.open = true;

    const apply = () => {
      const words = search ? search.value.trim().toLowerCase().split(/\s+/).filter(Boolean) : [];
      let shown = 0;
      rows.forEach((row, i) => {
        const match = selects.every((s) => !s.value || row.dataset[s.dataset.key] === s.value) && words.every((w) => text[i].includes(w));
        row.hidden = !match;
        if (match) shown += 1;
      });
      const on = selects.some((s) => s.value) || (search && search.value.trim());
      // the count is for the main list (the Attorney General's rulings), not the court rulings filtered with it
      const own = rows.filter((r) => (!home || home.contains(r)) && !r.dataset.nocount);
      const ownShown = own.filter((r) => !r.hidden).length;
      const said = on ? (ownShown ? `${ownShown} of ${own.length} shown` : `None of the ${own.length} match. Try fewer words or another filter.`) : '';
      if (count) count.textContent = said;
      if (head) head.textContent = said;
      // a year with no ruling left under it goes; the others count what is left
      for (const y of years) {
        const left = y.querySelectorAll('.rec:not([hidden])').length;
        y.hidden = !left;
        const sub = y.querySelector('.sub-count');
        if (sub) {
          sub.dataset.all = sub.dataset.all || sub.textContent;
          sub.textContent = on ? `${left} of ${y.querySelectorAll('.rec').length} rulings` : sub.dataset.all;
        }
      }
      if (csv) {
        csv.dataset.all = csv.dataset.all || csv.textContent;
        csv.textContent = on && ownShown ? 'Download what’s shown (CSV)' : csv.dataset.all;
      }
      const p = new URLSearchParams(location.search);
      for (const s of selects) { if (s.value) p.set(s.dataset.key, s.value); else p.delete(s.dataset.key); }
      if (search && search.value.trim()) p.set('q', search.value.trim()); else if (search) p.delete('q');
      const qs = p.toString();
      history.replaceState(null, '', location.pathname + (qs ? `?${qs}` : '') + location.hash);
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
  const about = new URLSearchParams(location.search).get('about');
  if (about) {
    form.elements.kind.value = 'correction';
    form.elements.message.value = `About: ${about.slice(0, 300)}\n\nWhat’s wrong: `;
    const details = form.closest('details');
    if (details) details.open = true;
  }

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
      status.textContent = `Message sent. Thank you.${data && data.ref ? ` Reference ${data.ref}, if you write again about it.` : ''}`;
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

// Search results in the site's item format (town, board, "Mon Oct 26") with the town as the link, the
// item's own line as the heading when the agenda has one (from /data/lines.json), one excerpt line with
// no file names or URLs in it, and no repeats.
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
function dayLabel(d) {
  const m = d.match(/^([A-Z][a-z]{2}) (\d{1,2}), (\d{4})$/);
  if (!m) return d;
  const iso = `${m[3]}-${String(MONTHS.indexOf(m[1]) + 1).padStart(2, '0')}-${m[2].padStart(2, '0')}`;
  const dt = new Date(`${iso}T12:00:00Z`);
  const thisYear = new Date().getFullYear() === +m[3];
  return `${dt.toLocaleDateString('en-US', { weekday: 'short', timeZone: 'UTC' })} ${m[1]} ${+m[2]}${thisYear ? '' : `, ${m[3]}`}`;
}
function cleanExcerpt(node) {
  for (const n of [...node.childNodes]) {
    if (n.nodeType !== 3) continue;
    n.textContent = n.textContent
      .replace(/https?:\/\/\S+/g, ' ')
      .replace(/\S*\.(?:pdf|docx?|xlsx?)\b[^\s]*/gi, ' ')
      .replace(/\b(?:FWD?|RE|FW)_[^\s]*/g, ' ')
      .replace(/\b(?:[A-Z0-9_&-]{3,}\s+){3,}[A-Z0-9_&-]{3,}\b/g, ' ')
      .replace(/\s{2,}/g, ' ');
  }
}
function setupSearchResults() {
  const list = document.getElementById('search-results');
  if (!list || !window.MutationObserver) return;
  const form = document.getElementById('search-form');
  // search.js renders each result; the excerpt loses its OCR noise and ends on a sentence here.
  const dress = (li) => {
    if (li.dataset.dressed) return;
    li.dataset.dressed = '1';
    const snippet = li.querySelector('.result-snippet');
    if (snippet) {
      cleanExcerpt(snippet);
      trimToSentence(snippet);
    }
  };

  // Towns: chips with hidden name="town" inputs. search.js keeps one value per name when it reads the
  // form, so this page sends the query itself (several town= params) and lets search.js run it.
  const pick = document.getElementById('town-pick');
  const chips = document.getElementById('town-chips');
  const add = document.getElementById('town-add');
  const addError = document.getElementById('town-add-error');
  const options = pick ? Array.from(pick.querySelectorAll('#search-towns option')) : [];
  const nameOf = (id) => {
    const o = options.find((x) => x.dataset.id === id);
    return o ? o.value : id.split(':').slice(1).join(':');
  };
  const chosen = () => (chips ? Array.from(chips.querySelectorAll('input[name="town"]')).map((i) => i.value) : []);
  const chip = (id) => {
    const li = document.createElement('li');
    const box = document.createElement('input');
    box.type = 'hidden';
    box.name = 'town';
    box.value = id;
    const x = document.createElement('button');
    x.type = 'button';
    x.className = 'chip-x';
    x.textContent = '×';
    x.setAttribute('aria-label', `Remove ${nameOf(id)}`);
    x.addEventListener('click', () => {
      li.remove();
      submit();
      add.focus();
    });
    li.append(document.createTextNode(nameOf(id)), box, x);
    return li;
  };
  const setTowns = (ids) => {
    if (!chips) return;
    chips.replaceChildren(...[...new Set(ids)].filter(Boolean).map(chip));
    try { localStorage.setItem('agendaahead:search-towns', JSON.stringify(chosen())); } catch { /* private window */ }
  };
  function params() {
    const p = new URLSearchParams();
    for (const [k, v] of new FormData(form)) {
      const value = String(v).trim();
      if (!value) continue;
      if (k === 'town') p.append(k, value);
      else p.set(k, value);
    }
    for (const field of form.elements) if (field.type === 'checkbox' && field.defaultChecked && !field.checked) p.set(field.name, '0');
    return p;
  }
  function submit() {
    const qs = params().toString();
    if (qs !== location.search.slice(1)) history.pushState(null, '', location.pathname + (qs ? `?${qs}` : ''));
    window.dispatchEvent(new PopStateEvent('popstate')); // search.js runs the query in the address bar
    syncAlert();
  }
  function addTyped() {
    const want = norm(add.value);
    if (!want) return false;
    const o = options.find((x) => norm(x.value) === want) || options.find((x) => norm(x.value.split(',')[0]) === want);
    if (!o) {
      addError.textContent = 'We don’t know that town. Pick it from the list as you type.';
      addError.hidden = false;
      return false;
    }
    addError.hidden = true;
    if (!chosen().includes(o.dataset.id)) chips.append(chip(o.dataset.id));
    add.value = '';
    return true;
  }
  if (pick && form) {
    const fromUrl = new URLSearchParams(location.search).getAll('town').flatMap((v) => v.split(','));
    let remembered = [];
    try { remembered = JSON.parse(localStorage.getItem('agendaahead:search-towns') || '[]'); } catch { /* private window */ }
    // the towns added last time stay until removed; a link with its own towns wins
    setTowns(fromUrl.length ? fromUrl : remembered.filter((id) => options.some((x) => x.dataset.id === id)));
    if (!fromUrl.length && chosen().length) submit();  // the summary says how many filters are on; results stay first
    document.getElementById('town-add-btn').addEventListener('click', () => { if (addTyped()) submit(); });
    add.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' && add.value.trim()) {
        event.preventDefault();
        if (addTyped()) submit();
      }
    });
    add.addEventListener('change', () => { if (options.some((x) => x.value === add.value) && addTyped()) submit(); });
    // Runs before search.js's own submit handler (capture on document) and stops it.
    document.addEventListener('submit', (event) => {
      if (event.target !== form) return;
      event.preventDefault();
      event.stopPropagation();
      if (add.value.trim()) addTyped();
      submit();
    }, true);
    window.addEventListener('popstate', () => setTowns(new URLSearchParams(location.search).getAll('town')));
    const mine = window.w351 && window.w351.areas ? window.w351.areas() : null;
    const mineBtn = document.getElementById('my-towns-btn');
    if (mine && mine.towns.length && mineBtn) {
      mineBtn.textContent = `Search my towns (${mine.towns.slice(0, 3).map(nameOf).join(', ')}${mine.towns.length > 3 ? ` and ${mine.towns.length - 3} more` : ''})`;
      mineBtn.hidden = false;
      mineBtn.addEventListener('click', () => {
        setTowns(mine.towns);
        submit();
      });
    }
  }

  // "Get these by email" right above the results, carrying the town and topic filters to /watch.
  const alert = document.getElementById('search-alert');
  function syncAlert() {
    if (!alert || !form) return;
    const towns = chosen();
    const topic = form.elements.topic && form.elements.topic.value;
    const q = new URLSearchParams();
    if (towns.length) q.set('town', towns.join(','));
    if (topic) q.set('topic', topic);
    const link = alert.querySelector('a');
    link.href = `/watch${q.toString() ? `?${q}` : ''}`;
    const names = towns.map((t) => nameOf(t).split(',')[0]);
    link.textContent = names.length ? `Follow ${names.length > 2 ? `${names[0]} and ${names.length - 1} more towns` : names.join(' or ')}`
      : 'Follow your town';
    alert.hidden = !list.querySelector('li.result:not([hidden])');
  }

  // A name of two or more words with no exact match in the results: say so, and offer the quoted search.
  const exact = document.getElementById('search-exact');
  const input = document.getElementById('search-q');
  function checkExact() {
    if (!exact || !input) return;
    const q = input.value.trim();
    const words = q.split(/\s+/).filter((w) => w.length > 1);
    const results = Array.from(list.querySelectorAll('li.result:not([hidden])'));
    if (/["“”]/.test(q) || words.length < 2 || !results.length) {
      exact.hidden = true;
      return;
    }
    const phrase = norm(q);
    const found = results.some((li) => norm(li.textContent).includes(phrase));
    if (found) {
      exact.hidden = true;
      return;
    }
    const again = document.createElement('button');
    again.type = 'button';
    again.className = 'link-btn';
    again.textContent = `Search for "${q}" as an exact phrase`;
    again.addEventListener('click', () => {
      input.value = `"${q}"`;
      submit();
    });
    exact.replaceChildren(`No exact match for “${q}”. The results below have these words, but not together. `, again, '.');
    exact.hidden = false;
  }

  if (form) form.addEventListener('change', syncAlert);
  let pending = 0;
  new MutationObserver((changes) => {
    for (const c of changes) for (const n of c.addedNodes) if (n.nodeType === 1 && n.matches('li.result')) dress(n);
    syncAlert();
    clearTimeout(pending);
    pending = setTimeout(checkExact, 150);
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
async function requestTown(id, name, email) {
  const reply = email ? ` Tell me when it's added: ${email}` : '';
  const res = await fetch('/api/contact', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ kind: 'message', message: `Please add ${name} (${id}). We can't get its agendas yet.${reply}`, page: location.pathname }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok || !data.ok) throw new Error(data.error || 'The request didn’t go through. Try again in a minute.');
}
function setupRequestButtons() {
  for (const box of document.querySelectorAll('[data-request-town]')) {
    const button = box.querySelector('button');
    const out = box.querySelector('.form-status');
    const email = box.querySelector('input[type="email"]');
    button.addEventListener('click', async () => {
      const address = email ? email.value.trim() : '';
      if (address && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(address)) {
        out.className = 'form-status err';
        out.textContent = 'Check the email address. It should look like name@example.com, or leave it empty.';
        email.focus();
        return;
      }
      button.disabled = true;
      out.className = 'form-status';
      out.textContent = 'Sending…';
      try {
        await requestTown(box.dataset.requestTown, box.dataset.townName, address);
        out.classList.add('ok');
        out.textContent = address ? 'Thanks. We’ll ask the town hall, and email you when the town is added.'
          : 'Thanks. We’ve got your request and will ask the town hall.';
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
  // Search keeps its results first: the folded filters say how many are on instead of opening.
  const filters = document.getElementById('search-filters');
  if (filters) {
    const summary = filters.querySelector(':scope > summary');
    const say = () => {
      const on = ['state', 'topic', 'board'].filter((k) => (filters.querySelector(`select[name=${k}]`) || {}).value).length
        + (document.querySelector('#town-chips li') ? 1 : 0);
      summary.textContent = on ? `Filters (${on} on)` : 'Filters';
    };
    new MutationObserver(say).observe(document.getElementById('town-chips') || filters, { childList: true });
    say();
    window.addEventListener('popstate', say);
    document.addEventListener('change', (ev) => { if (filters.contains(ev.target)) setTimeout(say, 0); });
  }
}

// Old links to the tracker that used to live on the home page.
function followOldAnchors() {
  if (location.pathname === '/' && location.hash === '#tracker') location.replace('/attorney-general/town-actions');
  if (location.pathname === '/attorney-general' && location.hash === '#tracker') location.replace('/attorney-general/town-actions');
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
  saveAreas(homeTown, towns, topics, merge = true) {
    try {
      // a new alert adds its towns to the ones this device already has (merge); removing a town replaces the list
      const before = merge && this.areas() ? this.areas().towns : [];
      const list = [...new Set([homeTown, ...(towns || []), ...before])].filter((t) => typeof t === 'string' && t.includes(':'));
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
  // "My towns" from a town page: added to the same saved towns (the first one stays the home town).
  addTown(id) {
    const doc = this.areas();
    const towns = doc ? doc.towns : [];
    if (!towns.includes(id)) this.saveAreas(doc ? doc.home_town : id, [...towns, id], doc && doc.topics, false);
  },
  removeTown(id) {
    const doc = this.areas();
    if (!doc) return;
    const towns = doc.towns.filter((t) => t !== id);
    try {
      if (!towns.length) localStorage.removeItem(AREAS_KEY);
      else this.saveAreas(towns[0], towns, doc.topics, false);
    } catch {
      /* storage unavailable */
    }
  },
  // Every town this device follows: the alerts' towns and the towns added in Search.
  myTowns() {
    const doc = this.areas();
    const read = (key) => { try { const v = JSON.parse(localStorage.getItem(key) || '[]'); return Array.isArray(v) ? v : []; } catch { return []; } };
    return [...new Set([...(doc ? doc.towns : []), ...read('agendaahead:search-towns'), ...read('agendaahead:story-towns')])]
      .filter((t) => typeof t === 'string' && t.includes(':'));
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

// A story or row whose meeting has passed (in Boston time) is hidden. Dates stay as written: "Tue Oct 13".
function relDates(root = document) {
  const today = new Intl.DateTimeFormat('en-CA', { timeZone: 'America/New_York', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date());
  for (const t of root.querySelectorAll('.row time, .story time')) {
    const iso = t.getAttribute('datetime') || '';
    if (iso && iso < today) {
      const item = t.closest('.row, .story');
      if (item) item.hidden = true;
    }
  }
}

// "Copy citation" and "Share this meeting": buttons that need JavaScript, so they start hidden. Share
// opens the phone's share sheet, or copies the text and link (ready to paste into Facebook).
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
    const post = data.text ? `${data.text}\n${data.url}` : data.url;
    flash(share, (await copyText(post)) ? 'Copied, ready to paste' : 'Couldn’t copy');
  });
  for (const b of document.querySelectorAll('[data-copy][hidden], [data-share][hidden]')) b.hidden = false;
}

followOldAnchors();
setupTownBox();
// Topic pages: <div data-meeting-filter> with a county select hides the meetings from other counties.
function setupMeetingFilter() {
  const bar = document.querySelector('[data-meeting-filter]');
  if (!bar) return;
  const select = bar.querySelector('select[data-key="county"]');
  const town = bar.querySelector('input[data-key="town"]');
  const mineBtn = bar.querySelector('[data-my-towns]');
  const mineNote = bar.querySelector('[data-cant-mine]');
  if (!select && !town) return;
  const count = bar.querySelector('[data-count]');
  const clearBtn = bar.querySelector('[data-clear-filters]');
  // the meetings still ahead: not a day that has passed since the page was built, not an "Earlier meetings" fold
  const meetings = Array.from(document.querySelectorAll('.meeting[data-county]'))
    .filter((m) => !m.closest('.day-group.past') && !m.closest('details.disclose'));
  const days = Array.from(document.querySelectorAll('.day-group:not(.past)'));
  const sections = Array.from(document.querySelectorAll('[data-meet-section]'));
  // "Only my towns": every town this device follows (alerts, Search and Biggest stories)
  const mineIds = window.w351 && window.w351.myTowns ? window.w351.myTowns() : [];
  const mineNames = mineIds.map((id) => id.split(':').slice(1).join(':'));
  const params = new URLSearchParams(location.search);
  let onlyMine = params.get('mine') === '1' && mineNames.length > 0;
  if (select && params.get('county')) {
    const v = params.get('county');
    // an older link says county=Worcester; the list now names counties within their state (MA:Worcester)
    const opt = [...select.options].find((o) => o.value === v) || [...select.options].find((o) => o.value === `MA:${v}`)
      || [...select.options].find((o) => o.value.endsWith(`:${v}`));
    if (opt) select.value = opt.value;
  }
  if (town && params.get('town')) town.value = params.get('town');
  const joinAnd = (xs) => (xs.length < 3 ? xs.join(' and ') : `${xs.slice(0, -1).join(', ')} and ${xs[xs.length - 1]}`);
  const mineLabel = () => `Only my towns (${mineNames.slice(0, 3).join(', ')}${mineNames.length > 3 ? ` and ${mineNames.length - 3} more` : ''})`;
  // the towns this device follows that we can't read yet, so a quiet list isn't taken for a quiet town
  let unread = null;
  const sayUnread = () => {
    if (!mineNote) return;
    if (!onlyMine || !unread || !unread.length) { mineNote.hidden = true; return; }
    const groups = {};
    for (const t of unread) (groups[t.why] = groups[t.why] || []).push(t.town);
    mineNote.textContent = `Your towns: ${joinAnd(mineNames)}. We can’t read ${Object.entries(groups)
      .map(([why, ts]) => `${joinAnd(ts)} (${why})`).join('; ')} yet, so nothing from ${unread.length === 1 ? 'it' : 'them'} shows here.`;
    mineNote.hidden = false;
  };
  const apply = () => {
    const wants = town ? town.value.split(',').map((w) => norm(w)).filter(Boolean) : [];
    const county = select ? select.value : '';
    let shown = 0;
    for (const m of meetings) {
      const name = norm(m.dataset.town || '');
      const ok = (!county || m.dataset.county === county)
        && (!wants.length || wants.some((w) => name.startsWith(w) || name.includes(` ${w}`)))
        && (!onlyMine || mineNames.includes(m.dataset.town || ''));
      m.hidden = !ok;
      if (ok) shown += 1;
    }
    const narrowed = county || wants.length || onlyMine;
    // a day heading with nothing left under it goes too, and so does a "Next 7 days" or "Later" with nothing in it
    for (const d of days) d.hidden = !d.querySelector('.meeting:not([hidden])');
    for (const sec of sections) {
      const has = sec.querySelector('.meeting');
      sec.hidden = Boolean(narrowed && has && !sec.querySelector('.meeting:not([hidden])'));
    }
    // "Show meetings more than 30 days out (8)" counts what the filter leaves, and goes at none
    for (const det of document.querySelectorAll('details.more')) {
      const summary = det.querySelector(':scope > summary');
      const n = det.querySelectorAll('.meeting:not([hidden])').length;
      if (summary && /\(\d+\)/.test(summary.textContent)) summary.textContent = summary.textContent.replace(/\(\d+\)/, `(${n})`);
      det.hidden = n === 0;
    }
    // a week's fold says what the filter leaves in it, opens when something does, and goes at none
    for (const det of document.querySelectorAll('details.week')) {
      const left = Array.from(det.querySelectorAll('.meeting:not([hidden])'));
      const items = left.reduce((n, m) => n + m.querySelectorAll('.line').length, 0);
      const label = det.querySelector('[data-week-count]');
      if (label) label.textContent = `${items} ${items === 1 ? 'item' : 'items'} at ${left.length} ${left.length === 1 ? 'meeting' : 'meetings'}`;
      det.hidden = left.length === 0;
      if (narrowed && left.length) det.open = true;
      else if (!narrowed) det.open = false;
    }
    if (clearBtn) clearBtn.hidden = !narrowed;
    // under a chosen county, the towns there we can't read
    for (const p of bar.querySelectorAll('[data-cant-county]')) p.hidden = p.dataset.cantCounty !== county;
    count.textContent = narrowed ? (shown ? `${shown} of ${meetings.length} meetings` : 'Nothing coming up for that choice.') : '';
    sayUnread();
    // the address bar carries the choice, so the page can be shared or bookmarked
    const p = new URLSearchParams(location.search);
    if (county) p.set('county', county); else p.delete('county');
    if (town && town.value.trim()) p.set('town', town.value.trim()); else p.delete('town');
    if (onlyMine) p.set('mine', '1'); else p.delete('mine');
    const qs = p.toString();
    history.replaceState(null, '', location.pathname + (qs ? `?${qs}` : '') + location.hash);
  };
  if (select) select.addEventListener('change', apply);
  if (town) town.addEventListener('input', apply);
  if (clearBtn) clearBtn.addEventListener('click', () => {
    if (select) select.value = '';
    if (town) town.value = '';
    onlyMine = false;
    if (mineBtn) {
      mineBtn.setAttribute('aria-pressed', 'false');
      if (mineNames.length) mineBtn.textContent = mineLabel();
    }
    apply();
  });
  if (mineBtn && mineNames.length) {
    mineBtn.hidden = false;
    const label = () => {
      mineBtn.setAttribute('aria-pressed', String(onlyMine));
      mineBtn.textContent = onlyMine ? 'All towns' : mineLabel();
    };
    label();
    mineBtn.addEventListener('click', () => {
      onlyMine = !onlyMine;
      label();
      apply();
    });
    fetch('/data/towns.json').then((r) => (r.ok ? r.json() : null)).then((d) => {
      if (!d) return;
      const ids = new Set(mineIds);
      unread = (d.towns || []).filter((t) => ids.has(t.id) && !t.monitored).map((t) => ({ town: t.town, why: t.why || 'not worked out yet' }));
      sayUnread();
    }).catch(() => {});
  }
  apply();
}

// A day heading whose date has passed (the page was built this morning; it may be read after midnight) goes,
// with its meetings.
function markPastDays() {
  const today = new Intl.DateTimeFormat('en-CA', { timeZone: 'America/New_York', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date());
  for (const g of document.querySelectorAll('.day-group')) {
    const t = g.querySelector('.day time[datetime]');
    if (t && t.getAttribute('datetime') < today && !g.closest('details.disclose')) {
      g.classList.add('past');
      g.hidden = true;
    }
  }
}

// /upcoming: "Titles only" hides the write-ups so a reporter can scan six towns on one screen. The page comes
// built that way (body.compact); a remembered "With details" takes the class off.
function setupViewSwitch() {
  const bar = document.querySelector('[data-view-switch]');
  if (!bar) return;
  const buttons = Array.from(bar.querySelectorAll('[data-view]'));
  const set = (view) => {
    document.body.classList.toggle('compact', view === 'lines');
    for (const b of buttons) b.setAttribute('aria-pressed', String(b.dataset.view === view));
  };
  let view = new URLSearchParams(location.search).get('view');
  if (!view) { try { view = localStorage.getItem('agendaahead:view2'); } catch { /* private window */ } }
  set(view === 'full' ? 'full' : 'lines');
  for (const b of buttons) b.addEventListener('click', () => {
    set(b.dataset.view);
    try { localStorage.setItem('agendaahead:view2', b.dataset.view); } catch { /* private window */ }
  });
}

setupListFilter();
setupTrackerFilter();
setupGenericFilters();
markPastDays();
setupMeetingFilter();
(() => {
  const id = decodeURIComponent(location.hash.slice(1));
  const rec = id ? document.getElementById(id) : null;
  const box = rec && rec.matches('.rec') ? rec.querySelector('details') : (rec && rec.tagName === 'DETAILS' ? rec : null);
  if (box) { box.open = true; rec.scrollIntoView({ block: 'start' }); }
})();
setupViewSwitch();
setupContactForm();
setupSearchResults();
setupEmailNotes();
setupRequestButtons();
setupDisclosure();
setupCopyAndShare();
relDates();
