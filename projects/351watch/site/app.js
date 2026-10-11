// Shared behavior on every 351 Watch page: table filters and the corrections form.

function setupFilters() {
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

function setupCoverage() {
  const table = document.querySelector('#coverage-table');
  if (!table) return;
  const rows = Array.from(table.querySelectorAll('tbody tr'));
  const status = document.querySelector('#c-status');
  const search = document.querySelector('#c-search');
  const count = document.querySelector('#c-count');

  function apply() {
    const q = search.value.trim().toLowerCase();
    let shown = 0;
    for (const row of rows) {
      const match = (!status.value || row.dataset.group === status.value) &&
        (!q || row.textContent.toLowerCase().includes(q));
      row.hidden = !match;
      if (match) shown += 1;
    }
    count.textContent = `${shown} of ${rows.length} shown`;
  }

  status.addEventListener('change', apply);
  search.addEventListener('input', apply);
  apply();
}

// <div class="filters" data-filters="G"> with <select data-key="k"> filters rows of every
// table[data-filter-group="G"] by their data-k attribute; [data-search] matches row text.
function setupGenericFilters() {
  for (const bar of document.querySelectorAll('.filters[data-filters]')) {
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
      for (const table of document.querySelectorAll(`table[data-filter-group="${group}"]`)) {
        const section = table.closest('section');
        if (section && !section.contains(bar)) section.hidden = !table.querySelector('tbody tr:not([hidden])');
      }
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
    button.disabled = true;
    const payload = { ...Object.fromEntries(new FormData(form).entries()), page: document.referrer.slice(0, 200) };
    try {
      const res = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok || !data.ok) throw new Error(data.error || 'Something went wrong. Please try again.');
      form.reset();
      status.classList.add('ok');
      status.textContent = 'Thanks, your message was received.';
    } catch (err) {
      status.classList.add('err');
      status.textContent = err.message;
    } finally {
      button.disabled = false;
    }
  });
}

// Watchlist links made or opened in this browser (a per-viewer convenience; may be unavailable).
const LISTS_KEY = '351watch:lists';
window.w351 = {
  recall() {
    try {
      const lists = JSON.parse(localStorage.getItem(LISTS_KEY) || '[]');
      return Array.isArray(lists) ? lists.filter((l) => l && typeof l.id === 'string') : [];
    } catch {
      return [];
    }
  },
  remember(id, name) {
    try {
      const lists = this.recall().filter((l) => l.id !== id);
      lists.unshift({ id, name: name || '', at: new Date().toISOString() });
      localStorage.setItem(LISTS_KEY, JSON.stringify(lists.slice(0, 20)));
    } catch {
      /* storage unavailable */
    }
  },
  forget(id) {
    try {
      localStorage.setItem(LISTS_KEY, JSON.stringify(this.recall().filter((l) => l.id !== id)));
    } catch {
      /* storage unavailable */
    }
  },
};

setupFilters();
setupCoverage();
setupGenericFilters();
setupContactForm();
