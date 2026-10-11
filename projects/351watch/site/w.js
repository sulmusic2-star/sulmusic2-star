// /w/<id> (or /w?id=<id>): a watchlist's matched items, feed links, webhook status, edit and delete.
(() => {
  const app = document.getElementById('wl-app');
  if (!app) return;
  const $ = (id) => document.getElementById(id);
  const TOPICS = JSON.parse(app.dataset.topics || '{}');
  const KINDS = { slack: 'Slack', teams: 'Microsoft Teams', teams_workflow: 'Teams workflow (Power Automate)', discord: 'Discord', json: 'JSON webhook' };
  const PLANS = { beta: 'Founding beta (free)', siting_desk: 'Siting Desk', counsel: 'Counsel', datacenter: 'Data-Center Local Action Feed' };
  const pathId = (location.pathname.match(/^\/w\/([A-Za-z0-9_-]{24,64})\/?$/) || [])[1];
  const params = new URLSearchParams(location.search);
  const id = pathId || params.get('id') || '';
  const today = new Intl.DateTimeFormat('en-CA', { timeZone: 'America/New_York', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date());

  const el = (tag, attrs = {}, ...children) => {
    const node = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === 'class') node.className = v;
      else if (k === 'text') node.textContent = v;
      else node.setAttribute(k, v);
    }
    node.append(...children.filter((c) => c !== null && c !== undefined && c !== false));
    return node;
  };
  const fmtDate = (iso) => {
    if (!iso) return '';
    const d = new Date(iso.length === 10 ? `${iso}T12:00:00Z` : iso);
    return Number.isNaN(d.getTime()) ? iso : d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', timeZone: iso.length === 10 ? 'UTC' : 'America/New_York' });
  };
  const plural = (n, word) => `${n.toLocaleString('en-US')} ${word}${n === 1 ? '' : 's'}`;
  const topicLabel = (t) => TOPICS[t] || t;
  const townPath = (url) => {
    try {
      return new URL(url).pathname;
    } catch {
      return '/towns';
    }
  };

  function fail(message) {
    $('wl-title').textContent = 'Watchlist not available';
    document.title = 'Watchlist not available | 351 Watch';
    const box = $('wl-error');
    box.replaceChildren(document.createTextNode(`${message} `), el('a', { href: '/watch', text: 'Create a watchlist' }));
    box.hidden = false;
    $('wl-body').hidden = true;
  }

  async function api(method, url) {
    const res = await fetch(url, { method, cache: 'no-store', headers: { Accept: 'application/json' } });
    const data = await res.json().catch(() => ({}));
    if (!res.ok || data.ok === false) {
      const err = new Error(data.error || 'Something went wrong. Please try again.');
      err.status = res.status;
      throw err;
    }
    return data;
  }

  function copyButton(getText, label) {
    const button = el('button', { type: 'button', class: 'btn small ghost', text: 'Copy' });
    button.setAttribute('aria-label', label);
    button.addEventListener('click', async () => {
      const text = getText();
      try {
        await navigator.clipboard.writeText(text);
      } catch {
        const tmp = el('textarea', { class: 'sr-only' });
        tmp.value = text;
        document.body.append(tmp);
        tmp.select();
        document.execCommand('copy');
        tmp.remove();
      }
      button.textContent = 'Copied';
      setTimeout(() => { button.textContent = 'Copy'; }, 1800);
    });
    return button;
  }

  function card(item) {
    const upcoming = item.meeting_date && item.meeting_date >= today;
    const when = fmtDate(item.meeting_date) || 'Date not listed';
    const days = item.days_before_meeting;
    const lead = typeof days === 'number' && days > 0
      ? el('span', { class: 'leadtime', text: days >= 1.5 ? `First seen ${Math.round(days)} days before the meeting` : 'First seen the day before the meeting' })
      : null;
    const agenda = el('a', { href: item.source_url, rel: 'nofollow noopener', target: '_blank' }, 'Agenda',
      el('span', { class: 'sr-only', text: ` for ${item.town} ${item.board}, ${when}` }));
    return el('article', { class: 'hit' },
      el('header', {},
        el('b', {}, el('a', { href: townPath(item.town_url), text: item.town })),
        el('span', { class: 'meta', text: `${item.board} · ${when}` }),
        upcoming ? el('span', { class: 'badge pending', text: 'Upcoming' }) : null),
      el('p', { text: `“${item.snippet}”` }),
      el('div', { class: 'tags' }, ...item.topics.map((t) => el('span', { class: 'tag', text: topicLabel(t) })), lead, agenda));
  }

  function renderItems(items) {
    const town = $('i-town');
    const topic = $('i-topic');
    const search = $('i-search');
    const towns = [...new Set(items.map((i) => i.town))].sort();
    town.append(...towns.map((t) => el('option', { value: t, text: `${t} (${items.filter((i) => i.town === t).length})` })));
    const topics = [...new Set(items.flatMap((i) => i.topics))];
    topic.append(...topics.map((t) => el('option', { value: t, text: topicLabel(t) })));
    const text = items.map((i) => `${i.town} ${i.board} ${i.snippet} ${i.document_title || ''}`.toLowerCase());

    const apply = () => {
      const q = search.value.trim().toLowerCase();
      const shown = items.filter((item, n) =>
        (!town.value || item.town === town.value) && (!topic.value || item.topics.includes(topic.value)) && (!q || text[n].includes(q)));
      const up = shown.filter((i) => i.meeting_date && i.meeting_date >= today).sort((a, b) => a.meeting_date.localeCompare(b.meeting_date));
      const past = shown.filter((i) => i.meeting_date && i.meeting_date < today).sort((a, b) => b.meeting_date.localeCompare(a.meeting_date));
      const undated = shown.filter((i) => !i.meeting_date);
      const fill = (node, list, empty) => node.replaceChildren(...(list.length ? list.map(card) : [el('p', { class: 'empty', text: empty })]));
      fill($('items-upcoming'), up, 'No matching items for meetings still ahead.');
      fill($('items-past'), past, 'No matching items from recent meetings.');
      fill($('items-undated'), undated, '');
      $('undated-wrap').hidden = !undated.length;
      $('i-count').textContent = `${shown.length} of ${items.length} shown`;
    };
    for (const c of [town, topic]) c.addEventListener('change', apply);
    search.addEventListener('input', apply);
    apply();
  }

  function renderFeeds(links) {
    const rows = [
      ['RSS', links.rss, 'For feed readers such as Feedly, Inoreader or Outlook.'],
      ['JSON', links.json, 'For spreadsheets, scripts and your own tools.'],
      ['Calendar (iCal)', links.ics, 'One all-day event per upcoming meeting with matched items.'],
    ];
    $('feed-rows').replaceChildren(...rows.map(([label, url, help], n) => {
      const input = el('input', { id: `feed-${n}`, type: 'text', readonly: '', spellcheck: 'false' });
      input.value = url;
      input.addEventListener('focus', () => input.select());
      return el('div', { class: 'feed-row' }, el('label', { for: `feed-${n}`, text: label }), input,
        copyButton(() => url, `Copy ${label} feed link`), el('small', { text: help }));
    }));
    $('webcal-link').href = links.ics.replace(/^https?:/, 'webcal:');
  }

  function renderWebhook(wl) {
    const status = $('hook-status');
    const hook = wl.webhook;
    if (!hook || !hook.configured) {
      status.replaceChildren('No daily messages set up. ', el('a', { href: `/watch?edit=${wl.id}`, text: 'Add a Slack, Teams or Discord webhook' }), '.');
      return;
    }
    const parts = [`Daily messages go to ${KINDS[hook.kind] || 'a webhook'} at ${hook.masked}. `];
    const d = wl.last_delivery;
    if (d && d.ok) parts.push(`Last delivery ${fmtDate(d.at)}: ${plural(d.sent, 'item')}${d.more ? ` plus a link to ${d.more} more` : ''}.`);
    else if (d) parts.push(`The last delivery on ${fmtDate(d.at)} failed (${d.error || `HTTP ${d.status}`}); we'll retry with the next daily run. Check the webhook URL.`);
    else parts.push('Nothing sent yet: messages go out once a day when new matching items appear.');
    status.textContent = parts.join('');
    const test = $('hook-test');
    test.hidden = false;
    test.addEventListener('click', async () => {
      const out = $('hook-test-status');
      test.disabled = true;
      out.className = 'form-status';
      out.textContent = 'Sending a test message…';
      try {
        await api('POST', `/api/watchlists?id=${encodeURIComponent(wl.id)}&action=test`);
        out.classList.add('ok');
        out.textContent = 'Test message sent. Check your channel.';
      } catch (err) {
        out.classList.add('err');
        out.textContent = err.message;
      } finally {
        test.disabled = false;
      }
    });
  }

  function renderManage(wl) {
    const plan = PLANS[wl.plan] || wl.plan;
    $('plan-line').replaceChildren(`Plan: ${plan}. `, el('a', { href: `/pricing?id=${wl.id}`, text: 'See planned plans' }), '.');
    $('edit-link').href = `/watch?edit=${wl.id}`;
    const start = $('delete-start');
    const confirmBox = $('delete-confirm');
    start.addEventListener('click', () => {
      confirmBox.hidden = false;
      $('delete-yes').focus();
    });
    $('delete-no').addEventListener('click', () => {
      confirmBox.hidden = true;
      start.focus();
    });
    $('delete-yes').addEventListener('click', async () => {
      const out = $('manage-status');
      $('delete-yes').disabled = true;
      try {
        await api('DELETE', `/api/watchlists?id=${encodeURIComponent(wl.id)}`);
        window.w351.forget(wl.id);
        $('wl-body').hidden = true;
        $('wl-title').textContent = 'Watchlist deleted';
        $('wl-summary').textContent = 'Its page and feeds no longer work.';
        const box = $('wl-error');
        box.className = 'notice ok';
        box.replaceChildren('Deleted. ', el('a', { href: '/watch', text: 'Create a new watchlist' }));
        box.hidden = false;
        box.setAttribute('tabindex', '-1');
        box.focus();
      } catch (err) {
        out.className = 'form-status err';
        out.textContent = err.message;
        $('delete-yes').disabled = false;
      }
    });
  }

  async function main() {
    if (!/^[A-Za-z0-9_-]{24,64}$/.test(id)) {
      fail('This link is missing its watchlist ID.');
      return;
    }
    let wl;
    let feed;
    try {
      [{ watchlist: wl }, feed] = await Promise.all([
        api('GET', `/api/watchlists?id=${encodeURIComponent(id)}`),
        api('GET', `/api/feed?id=${encodeURIComponent(id)}&format=json&fresh=1`),
      ]);
    } catch (err) {
      fail(err.status === 404 ? 'We couldn’t find this watchlist. It may have been deleted, or the link may be incomplete.' : err.message);
      return;
    }
    const name = wl.name || 'Your watchlist';
    document.title = `${name} | 351 Watch`;
    $('wl-title').textContent = name;
    const townNames = wl.towns.map((t) => t.split(':').slice(1).join(':'));
    const shownTowns = townNames.slice(0, 8).join(', ') + (townNames.length > 8 ? ` and ${townNames.length - 8} more` : '');
    $('wl-summary').textContent = `${plural(wl.towns.length, 'town')} (${shownTowns}) · ${wl.topics.map(topicLabel).join(', ')}. Created ${fmtDate(wl.created_at)}.`;
    $('items-lead').textContent = `${plural(feed.count, 'item')} match${feed.count === 1 ? 'es' : ''} in the current data${feed.generated ? `, updated ${fmtDate(feed.generated)}` : ''}. Upcoming meetings come first.`;
    window.w351.remember(wl.id, wl.name);
    $('wl-body').hidden = false;

    const copyPage = $('copy-page');
    copyPage.replaceWith(copyButton(() => wl.links.page, 'Copy this watchlist’s link'));
    if (params.get('checkout') === 'success') {
      const banner = $('checkout-banner');
      banner.textContent = 'Thanks. Your plan will show here once Stripe confirms the payment.';
      banner.hidden = false;
    }
    renderItems(feed.items);
    renderFeeds(wl.links);
    renderWebhook(wl);
    renderManage(wl);
  }

  main();
})();
