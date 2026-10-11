// /pricing: plan buttons stay disabled unless /api/checkout reports Stripe is configured for that plan.
(() => {
  const buttons = Array.from(document.querySelectorAll('button[data-plan]'));
  const note = document.getElementById('checkout-note');
  if (!buttons.length) return;
  const params = new URLSearchParams(location.search);
  const valid = (v) => /^[A-Za-z0-9_-]{24,64}$/.test(v || '');
  const watchlistId = valid(params.get('id')) ? params.get('id') : (window.w351.recall()[0] || {}).id;

  function say(text) {
    note.textContent = text;
    note.hidden = false;
  }

  if (params.get('checkout') === 'cancelled') say('Checkout was cancelled. Nothing was charged.');

  async function enable() {
    let config;
    try {
      const res = await fetch('/api/checkout', { headers: { Accept: 'application/json' } });
      config = await res.json();
    } catch {
      return;
    }
    if (!config || !config.enabled) return;
    for (const button of buttons) {
      const plan = config.plans[button.dataset.plan];
      if (!plan || !plan.enabled) continue;
      button.disabled = false;
      button.classList.remove('ghost');
      button.textContent = `Choose ${plan.name}`;
    }
    document.getElementById('plan-help').textContent = watchlistId
      ? 'The plan applies to your most recent watchlist in this browser. Payment is handled by Stripe.'
      : 'Create a watchlist first; the plan applies to it. Payment is handled by Stripe.';
  }

  for (const button of buttons) {
    button.addEventListener('click', async () => {
      if (!watchlistId) {
        say('Create a watchlist first, then choose a plan from its page.');
        return;
      }
      button.disabled = true;
      try {
        const res = await fetch('/api/checkout', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ plan: button.dataset.plan, watchlist_id: watchlistId }),
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok || !data.url) throw new Error(data.error || 'Checkout is unavailable right now.');
        location.assign(data.url);
      } catch (err) {
        say(err.message);
        button.disabled = false;
      }
    });
  }

  enable();
})();
