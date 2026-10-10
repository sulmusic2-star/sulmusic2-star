// Table filtering and form submission for the 351 Watch tracker page.

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

function setupForm(form, endpoint, successText) {
  if (!form) return;
  const status = form.querySelector('.form-status');
  const button = form.querySelector('button[type="submit"]');

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    status.className = 'form-status';
    status.textContent = '';
    button.disabled = true;

    const payload = Object.fromEntries(new FormData(form).entries());
    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok || !data.ok) throw new Error(data.error || 'Something went wrong. Please try again.');
      form.reset();
      status.classList.add('ok');
      status.textContent = successText;
    } catch (err) {
      status.classList.add('err');
      status.textContent = err.message;
    } finally {
      button.disabled = false;
    }
  });
}

setupFilters();
setupForm(document.querySelector('#signup-form'), '/api/waitlist', "You're on the list. We'll email you when alerts open for your towns.");
setupForm(document.querySelector('#contact-form'), '/api/contact', 'Thanks — your message was received.');
