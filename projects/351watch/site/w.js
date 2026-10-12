// /w/<key> (or /w?id=<key>): one alert list. A private key shows everything, including the
// private and share links, the daily message, edit and delete. A share (read-only) key shows the
// items and feeds only. ?new=1 after creating shows the "save your private link" banner.
(() => {
  const app = document.getElementById('wl-app');
  if (!app) return;
  const $ = (id) => document.getElementById(id);
  const TOPICS = JSON.parse(app.dataset.topics || '{}'); // key: [label, phrase, plural]
  const ORDER = JSON.parse(app.dataset.order || '[]');
  const KINDS = { slack: 'Slack', teams: 'Microsoft Teams', teams_workflow: 'Microsoft Teams (Workflows)', discord: 'Discord', json: 'a JSON webhook' };
  const PLANS = { beta: 'Founding beta (free)', siting_desk: 'Siting Desk', counsel: 'Counsel', datacenter: 'Data-Center Local Action Feed' };
  const pathId = (location.pathname.match(/^\/w\/([A-Za-z0-9_-]{24,64})\/?$/) || [])[1];
  const params = new URLSearchParams(location.search);
  const id = pathId || params.get('id') || '';
  const SITE = document.title.split(' | ').pop(); // the product name, from the title build.py wrote
  let homeTown = null; // the alert list's home town, when the API reports it
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
  const dayLabel = (iso) => {
    const d = new Date(`${iso.slice(0, 10)}T12:00:00Z`);
    const opts = { weekday: 'long', month: 'long', day: 'numeric', timeZone: 'UTC' };
    if (iso.slice(0, 4) !== today.slice(0, 4)) opts.year = 'numeric';
    return d.toLocaleDateString('en-US', opts);
  };
  const plural = (n, word) => `${n.toLocaleString('en-US')} ${word}${n === 1 ? '' : 's'}`;
  const joinAnd = (parts) => (parts.length < 3 ? parts.join(' and ') : `${parts.slice(0, -1).join(', ')} and ${parts[parts.length - 1]}`);
  const topicLabel = (t) => (TOPICS[t] ? TOPICS[t][0] : t);
  const townPath = (url) => {
    try {
      return new URL(url).pathname;
    } catch {
      return '/towns';
    }
  };

  // Same wording as sentence() in build.py.
  function boardLabel(item) {
    if (item.board_key === 'town_meeting') return 'town meeting';
    let b = String(item.board || '').replace(/\s*\([^)]*\)/g, '').replace(/\s+[-–]\s+.*$/, '').replace(/^The\s+/, '').replace(/\s+Meetings?$/, '').trim();
    if (b && b === b.toUpperCase()) b = b.toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase());
    return b || 'town board';
  }
  function topicPhrase(topics) {
    const idx = (t) => (ORDER.includes(t) ? ORDER.indexOf(t) : 99);
    let ts = [...new Set(topics)].sort((a, b) => idx(a) - idx(b));
    const noWet = ts.filter((t) => t !== 'wetlands_filing');
    if (noWet.length) ts = noWet;
    const phrases = ts.map((t) => (TOPICS[t] ? [TOPICS[t][1], TOPICS[t][2]] : [t.replace(/_/g, ' '), false]));
    let words = phrases.map((p) => p[0]);
    if (words.length > 3) words = [...words.slice(0, 3), 'more'];
    return [joinAnd(words), words.length > 1 || Boolean(phrases[0] && phrases[0][1])];
  }
  function sentence(g, withTown) {
    const [low] = topicPhrase(g.topics);
    let s;
    if (g.source === 'massdep_wetlands') {
      s = `a wetlands filing for ${low} reached MassDEP. The conservation commission must open a hearing within 21 days of filing.`;
    } else {
      const where = g.board_key === 'town_meeting' ? 'the town meeting warrant' : `the ${boardLabel(g)} agenda`;
      s = `${where} mentions ${low}.`;
    }
    if (!withTown) return [s.charAt(0).toUpperCase() + s.slice(1)];
    const town = el('a', { class: 'item-town', href: townPath(g.town_url), text: g.town + (g.state && g.state !== 'MA' ? `, ${g.state}` : '') });
    const id = `${g.state}:${g.town}`;
    const next = homeTown && id !== homeTown ? ` (next to ${homeTown.split(':').slice(1).join(':')})` : '';
    return ['In ', town, `${next}, ${s}`];
  }

  // Group items by agenda document and meeting, as merge_agendas() does in build.py.
  function merge(items) {
    const groups = new Map();
    for (const it of items) {
      const key = `${it.source_url}|${it.meeting_date || ''}|${it.state}:${it.town}`;
      const g = groups.get(key);
      if (!g) groups.set(key, { ...it, topics: [...it.topics], snippets: [it.snippet] });
      else {
        for (const t of it.topics) if (!g.topics.includes(t)) g.topics.push(t);
        if (it.snippet && !g.snippets.includes(it.snippet)) g.snippets.push(it.snippet);
      }
    }
    return [...groups.values()];
  }

  function itemNode(g) {
    const when = fmtDate(g.meeting_date) || 'no date listed';
    const dep = g.source === 'massdep_wetlands';
    const pdf = /\.pdf$/i.test(g.source_url.split('?')[0]) || /\(pdf\)/i.test(g.document_title || '');
    const label = dep ? 'Open the filing' : (pdf ? 'Open the agenda (PDF)' : 'Open the agenda');
    const source = dep ? 'the MassDEP filing' : (g.board_key === 'town_meeting' ? 'the warrant' : 'the agenda');
    const more = g.snippets.length - 3;
    return el('li', { class: 'item' },
      el('p', { class: 'item-say' }, ...sentence(g, true)),
      el('p', { class: 'item-from', text: `Quoted from ${source}:` }),
      ...g.snippets.slice(0, 3).map((s) => el('blockquote', { class: 'item-quote', cite: g.source_url, text: s })),
      more > 0 ? el('p', { class: 'item-more', text: `${plural(more, 'more passage')} on this agenda.` }) : null,
      el('p', { class: 'item-src' }, el('a', { href: g.source_url, rel: 'nofollow noopener', target: '_blank' }, label,
        el('span', { class: 'sr-only', text: ` for ${g.town} ${boardLabel(g)}, ${when}` }))));
  }

  function dayGroups(groups) {
    const order = [];
    const byDay = new Map();
    for (const g of groups) {
      const k = (g.meeting_date || '').slice(0, 10);
      if (!byDay.has(k)) {
        byDay.set(k, []);
        order.push(k);
      }
      byDay.get(k).push(g);
    }
    return order.map((k) => el('section', { class: 'day' },
      el('h4', { class: 'day-head' }, k ? el('time', { datetime: k, text: dayLabel(k) }) : 'No meeting date listed'),
      el('ol', { class: 'items' }, ...byDay.get(k).map(itemNode))));
  }

  function fail(message, linkText = 'Set up new alerts') {
    $('wl-title').textContent = 'Alert list not available';
    document.title = `Alert list not available | ${SITE}`;
    const box = $('wl-error');
    box.replaceChildren(document.createTextNode(`${message} `), el('a', { href: '/watch', text: linkText }));
    box.hidden = false;
    $('wl-body').hidden = true;
  }

  async function api(method, url) {
    const res = await fetch(url, { method, cache: 'no-store', headers: { Accept: 'application/json' } });
    const data = await res.json().catch(() => ({}));
    if (!res.ok || data.ok === false) {
      const err = new Error(data.error || 'The server didn’t answer as expected. Try again in a minute.');
      err.status = res.status;
      throw err;
    }
    return data;
  }

  function copyButton(getText, label) {
    const button = el('button', { type: 'button', class: 'btn small quiet', text: 'Copy' });
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

  function linkField(fieldId, url, label) {
    const input = el('input', { id: fieldId, type: 'text', readonly: '', spellcheck: 'false', 'aria-label': label });
    input.value = url;
    input.addEventListener('focus', () => input.select());
    return [input, copyButton(() => url, `Copy ${label.toLowerCase()}`)];
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
      const up = merge(shown.filter((i) => i.meeting_date && i.meeting_date >= today).sort((a, b) => a.meeting_date.localeCompare(b.meeting_date)));
      const past = merge(shown.filter((i) => i.meeting_date && i.meeting_date < today).sort((a, b) => b.meeting_date.localeCompare(a.meeting_date)));
      const undated = merge(shown.filter((i) => !i.meeting_date));
      const fill = (node, list, empty) => node.replaceChildren(...(list.length ? dayGroups(list) : [el('p', { class: 'empty', text: empty })]));
      fill($('items-upcoming'), up, 'Nothing on upcoming agendas for these towns and topics yet. New items show up here, in the feeds and in the calendar.');
      fill($('items-past'), past, 'No matching items from recent meetings.');
      fill($('items-undated'), undated, '');
      $('undated-wrap').hidden = !undated.length;
      $('i-count').textContent = `${shown.length} of ${items.length} items`;
    };
    for (const c of [town, topic]) c.addEventListener('change', apply);
    search.addEventListener('input', apply);
    apply();
  }

  function renderFeeds(links) {
    $('webcal-link').href = links.ics.replace(/^https?:/, 'webcal:');
    $('rss-link').href = links.rss;
    $('json-link').href = links.json;
    const rows = [
      ['Calendar', links.ics, 'For Google Calendar or Outlook on the web: add a calendar “from URL” and paste this.'],
      ['RSS', links.rss, 'For feed readers such as Feedly, Inoreader or Outlook.'],
    ];
    $('feed-rows').replaceChildren(...rows.map(([label, url, help], n) =>
      el('div', { class: 'feed-row' }, el('label', { for: `feed-${n}`, text: `${label} link` }), ...linkField(`feed-${n}`, url, `${label} link`), el('small', { text: help }))));
  }

  function renderLinks(wl) {
    $('private-row').replaceChildren(...linkField('private-link', wl.links.page, 'Private link'));
    $('share-row').replaceChildren(...linkField('share-link', wl.links.share, 'Share link'));
    $('links-section').hidden = false;
  }

  // Email (private view only): {configured, available, confirmed, masked, status, resend_available_at}.
  // Offer to add one only when email alerts are on.
  function renderEmail(wl, emailOn) {
    const out = $('email-status');
    const mail = wl.email;
    const edit = el('a', { href: `/watch?edit=${wl.id}` });
    if (mail && mail.configured) {
      edit.textContent = 'Change or remove the address';
      out.replaceChildren(mail.confirmed
        ? `Daily email goes to ${mail.masked}, only on days with something new. `
        : `We sent a confirmation link to ${mail.masked}. Emails start once you click it. `, edit, '.');
      out.hidden = false;
      const at = mail.resend_available_at ? Date.parse(mail.resend_available_at) : NaN;
      if (!mail.confirmed && !Number.isNaN(at) && at <= Date.now()) {
        const button = el('button', { type: 'button', class: 'btn small quiet', text: 'Send the confirmation email again' });
        const said = el('span', { class: 'form-status', role: 'status' });
        button.addEventListener('click', async () => {
          button.disabled = true;
          said.className = 'form-status';
          said.textContent = ' Sending…';
          try {
            await api('POST', `/api/email?action=resend&id=${encodeURIComponent(wl.id)}`);
            said.classList.add('ok');
            said.textContent = ' Sent. Check your inbox and spam folder.';
          } catch (err) {
            said.classList.add('err');
            said.textContent = ` ${err.message}`;
            button.disabled = false;
          }
        });
        out.append(' ', button, said);
      }
    } else if (emailOn || (mail && mail.available)) {
      edit.textContent = 'Add an email address';
      out.replaceChildren('No email set up. ', edit, '.');
      out.hidden = false;
    }
  }

  function renderWebhook(wl) {
    const status = $('hook-status');
    const hook = wl.webhook;
    $('hook-section').hidden = false;
    if (!hook || !hook.configured) {
      status.replaceChildren('No daily message set up. ', el('a', { href: `/watch?edit=${wl.id}`, text: 'Add a Slack, Discord or Teams (Workflows) webhook' }), '.');
      return;
    }
    const parts = [`Daily messages go to ${KINDS[hook.kind] || 'a webhook'} at ${hook.masked}. `];
    const d = wl.last_delivery;
    if (d && d.ok) parts.push(`Last sent ${fmtDate(d.at)}: ${plural(d.sent, 'item')}${d.more ? ` plus a link to ${d.more} more` : ''}.`);
    else if (d) parts.push(`The last message, on ${fmtDate(d.at)}, failed (${d.error || `HTTP ${d.status}`}). We’ll try again with the next daily run. Check the webhook URL.`);
    else parts.push('Nothing sent yet. Messages go out once a day when new matching items appear.');
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
    $('manage-section').hidden = false;
    const plan = PLANS[wl.plan] || wl.plan;
    $('plan-line').replaceChildren(`Plan: ${plan}. `, el('a', { href: `/pricing?id=${wl.id}`, text: 'About the beta' }), '.');
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
        $('wl-title').textContent = 'Alert list deleted';
        $('wl-summary').textContent = 'Its page, feeds and daily message have stopped.';
        const box = $('wl-error');
        box.className = 'notice ok';
        box.replaceChildren(el('a', { href: '/watch', text: 'Set up new alerts' }));
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
      fail('This link is missing its key. Check that you copied the whole link.');
      return;
    }
    let wl;
    let feed;
    const status = fetch('/api/status', { headers: { Accept: 'application/json' } })
      .then((r) => r.json().catch(() => ({})).then((d) => (r.ok ? d : {}))).catch(() => ({}));
    try {
      [{ watchlist: wl }, feed] = await Promise.all([
        api('GET', `/api/watchlists?id=${encodeURIComponent(id)}`),
        api('GET', `/api/feed?id=${encodeURIComponent(id)}&format=json&fresh=1`),
      ]);
    } catch (err) {
      fail(err.status === 404 ? 'We couldn’t find these alerts. They may have been deleted, or the link may be incomplete.' : err.message);
      return;
    }
    const readonly = wl.readonly === true;
    homeTown = wl.home_town || null;
    const name = wl.name || (readonly ? 'Shared alerts' : 'Your alerts');
    document.title = `${name} | ${SITE}`;
    $('wl-title').textContent = name;
    const townNames = wl.towns.map((t) => t.split(':').slice(1).join(':'));
    const shownTowns = townNames.slice(0, 8).join(', ') + (townNames.length > 8 ? ` and ${townNames.length - 8} more` : '');
    $('wl-summary').textContent = `${wl.topics.map((t) => topicLabel(t)).join(', ')} in ${plural(wl.towns.length, 'town')}: ${shownTowns}. Made ${fmtDate(wl.created_at)}.`;
    $('items-lead').textContent = `${plural(feed.count, 'item')} match${feed.count === 1 ? 'es' : ''} these alerts in the current data${feed.generated ? `, updated ${fmtDate(feed.generated)}` : ''}.`;
    window.w351.remember(readonly ? id : wl.id, wl.name, readonly);
    $('wl-body').hidden = false;

    renderFeeds(wl.links);
    renderItems(feed.items);
    if (readonly) {
      $('readonly-banner').hidden = false;
      return;
    }
    renderLinks(wl);
    renderWebhook(wl);
    renderEmail(wl, (await status).email_alerts === true);
    renderManage(wl);
    const unconfirmed = params.get('email') === '1' && !(wl.email && wl.email.confirmed);
    if (params.get('new') === '1' || (params.get('email') === '1' && unconfirmed)) {
      const banner = $('created-banner');
      if (params.get('new') !== '1') banner.querySelector('b').textContent = 'Changes saved.';
      $('inbox-note').hidden = !unconfirmed;
      banner.hidden = false;
      banner.focus();
      $('get-title').closest('section').before($('links-section'));
    }
    if (params.get('email') === 'confirmed') {
      const banner = $('created-banner');
      banner.replaceChildren(el('b', { text: 'Email confirmed.' }),
        ` Alerts for this list will come to ${wl.email && wl.email.masked ? wl.email.masked : 'your inbox'} once a day, only when there’s something new.`);
      banner.hidden = false;
      banner.focus();
    }
    if (params.get('checkout') === 'success') {
      const banner = $('created-banner');
      banner.textContent = 'Thanks. Your plan will show here once Stripe confirms the payment.';
      banner.hidden = false;
    }
  }

  main();
})();
