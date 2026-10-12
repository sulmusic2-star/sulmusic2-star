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
  let LINES = {}; // /data/lines.json: {lines: {id: [line, quote]}, new: [id, ...]}
  let NEW = new Set();
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
    const opts = { weekday: 'short', month: 'short', day: 'numeric', timeZone: 'UTC' };
    if (iso.slice(0, 4) !== today.slice(0, 4)) opts.year = 'numeric';
    return d.toLocaleDateString('en-US', opts);
  };
  const plural = (n, word) => `${n.toLocaleString('en-US')} ${word}${n === 1 ? '' : 's'}`;
  const joinAnd = (parts) => (parts.length < 3 ? parts.join(' and ') : `${parts.slice(0, -1).join(', ')} and ${parts[parts.length - 1]}`);
  const townPath = (url) => {
    try {
      return new URL(url).pathname;
    } catch {
      return '/towns';
    }
  };

  // Same wording as board_label() and short_topics() in build.py.
  function boardLabel(item) {
    if (item.board_key === 'town_meeting') return 'town meeting';
    let b = String(item.board || '').replace(/\s*\([^)]*\)/g, '').replace(/\s+[-–]\s+.*$/, '').replace(/^The\s+/, '').replace(/\s+Meetings?$/, '').trim();
    if (b && b === b.toUpperCase()) b = b.toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase());
    return b || 'town board';
  }
  function meetingBoard(m) {
    if (m.source === 'massdep_wetlands') return 'Wetlands filing to the state';
    if (m.board_key === 'town_meeting') return 'Town meeting warrant';
    return m.board.charAt(0).toUpperCase() + m.board.slice(1);
  }
  function shortTopics(topics) {
    const idx = (t) => (ORDER.includes(t) ? ORDER.indexOf(t) : 99);
    let ts = [...new Set(topics)].sort((a, b) => idx(a) - idx(b));
    const noWet = ts.filter((t) => t !== 'wetlands_filing');
    if (noWet.length) ts = noWet;
    const words = ts.map((t) => (t === 'moratorium' ? 'moratorium' : (TOPICS[t] ? TOPICS[t][1] : t.replace(/_/g, ' ')))).map((w) => w.replace(/^a /, ''));
    return joinAnd(words.slice(0, 3));
  }

  // The plain line for one item (from /data/lines.json, written by agenda_line() in build.py). An
  // item newer than that file gets "Mentions …" and its own agenda text.
  function lineFor(it) {
    const known = LINES.lines && LINES.lines[it.id];
    if (known) return { line: known[0], quote: known[1] };
    const words = shortTopics(it.topics || []);
    return { line: `Mentions ${words}`, quote: String(it.snippet || '').slice(0, 200) };
  }

  // Items grouped by meeting (town, board, day), as group_meetings() does in build.py: one line per
  // distinct line, the "Mentions …" lines folded into one, one link per agenda document.
  function group(items) {
    const meetings = new Map();
    for (const it of items) {
      const d = (it.meeting_date || '').slice(0, 10);
      const dep = it.source === 'massdep_wetlands';
      const key = `${it.state}:${it.town}|${dep}|${it.board_key || boardLabel(it)}|${d}`;
      if (!meetings.has(key)) {
        meetings.set(key, { state: it.state, town: it.town, town_url: it.town_url, board: boardLabel(it), board_key: it.board_key,
          source: it.source, date: d, lines: new Map(), docs: [], found: it.first_seen || '' });
      }
      const m = meetings.get(key);
      const { line, quote } = lineFor(it);
      if (!m.lines.has(line)) m.lines.set(line, { quotes: [], topics: [], isNew: false });
      const entry = m.lines.get(line);
      if (quote && !entry.quotes.includes(quote)) entry.quotes.push(quote);
      for (const t of it.topics || []) if (!entry.topics.includes(t)) entry.topics.push(t);
      entry.isNew = entry.isNew || NEW.has(it.id);
      if (!m.docs.some((x) => x.url === it.source_url)) {
        m.docs.push({ url: it.source_url, pdf: /\.pdf$/i.test(String(it.source_url).split('?')[0]) || /\(pdf\)/i.test(it.document_title || '') });
      }
      if (it.first_seen && (!m.found || it.first_seen < m.found)) m.found = it.first_seen;
    }
    for (const m of meetings.values()) m.lines = tidy(m.lines);
    return [...meetings.values()];
  }

  function tidy(lines) {
    const core = (s) => s.toLowerCase().replace(' (continued)', '');
    const merge = (into, e) => {
      for (const q of e.quotes) if (!into.quotes.includes(q)) into.quotes.push(q);
      for (const t of e.topics) if (!into.topics.includes(t)) into.topics.push(t);
      into.isNew = into.isNew || e.isNew;
    };
    const named = new Map([...lines].filter(([k]) => !k.startsWith('Mentions ')));
    for (const short of [...named.keys()].sort((a, b) => a.length - b.length)) {
      const longer = [...named.keys()].find((k) => k !== short && k.length > short.length && core(k).includes(core(short)));
      if (longer) {
        merge(named.get(longer), named.get(short));
        named.delete(short);
      }
    }
    const mentions = [...lines].filter(([k]) => k.startsWith('Mentions ')).map(([, v]) => v);
    if (!mentions.length) return named;
    const all = { quotes: [], topics: [], isNew: false };
    for (const v of mentions) merge(all, v);
    const said = [...named.keys()].map(core).join(' ');
    const left = all.topics.filter((t) => !said.includes(shortTopics([t]).toLowerCase().replace(/s$/, '')));
    if (left.length) named.set(`${named.size ? 'Also mentions' : 'Mentions'} ${shortTopics(left)}`, all);
    return named;
  }

  function foundText(m) {
    if (!m.found) return '';
    const found = m.found.slice(0, 10);
    let text = `We found it ${new Date(`${found}T12:00:00Z`).toLocaleDateString('en-US', { month: 'short', day: 'numeric', timeZone: 'UTC' })}`;
    if (m.date && m.date > found) {
      const days = Math.round((Date.parse(`${m.date}T12:00:00Z`) - Date.parse(`${found}T12:00:00Z`)) / 86400000);
      text += `, ${plural(days, 'day')} before the meeting`;
    }
    return `${text}.`;
  }

  // One meeting, as meeting_html() renders it in build.py.
  function meetingNode(m) {
    const dep = m.source === 'massdep_wetlands';
    const source = dep ? 'the state filing' : (m.board_key === 'town_meeting' ? 'the warrant' : 'the agenda');
    const what = dep ? 'filing' : (m.board_key === 'town_meeting' ? 'warrant' : 'agenda');
    const tid = `${m.state}:${m.town}`;
    const next = homeTown && tid !== homeTown ? ` (next to ${homeTown.split(':').slice(1).join(':')})` : '';
    const head = el('h3', { class: 'meet-head', 'data-slop-ignore': '' },
      el('span', { class: 'meet-town' }, el('a', { href: townPath(m.town_url), text: m.town + (m.state && m.state !== 'MA' ? `, ${m.state}` : '') }), next), ' ',
      el('span', { class: 'meet-board', text: meetingBoard(m) }), ' ',
      m.date ? el('span', { class: 'meet-day' }, el('time', { datetime: m.date, text: dayLabel(m.date) })) : null);
    const lineNode = ([text, e]) => el('li', { class: 'line' },
      el('p', { class: 'line-say' }, e.isNew ? el('span', { class: 'badge-new', text: 'New' }) : null, e.isNew ? ' ' : null, text),
      e.quotes.length ? el('details', { class: 'item-words' }, el('summary', { text: 'See the agenda wording' }),
        el('p', { class: 'item-from', text: `Quoted from ${source}:` }),
        ...e.quotes.slice(0, 3).map((q) => el('blockquote', { class: 'item-quote', text: q }))) : null);
    const where = `${m.town} ${meetingBoard(m)}, ${fmtDate(m.date) || 'no date'}`;
    const links = m.docs.map((d, i) => el('a', { class: 'item-link', href: d.url, rel: 'nofollow noopener', target: '_blank' },
      `${i ? `Another version of the ${what}` : `Open the ${what}`}${d.pdf ? ' (PDF)' : ''}`, el('span', { class: 'sr-only', text: `: ${where}` })));
    const found = foundText(m);
    return el('li', { class: 'meeting' }, head,
      el('ul', { class: 'lines' }, ...[...m.lines].map(lineNode)),
      el('p', { class: 'meet-src' }, ...links, found ? el('span', { class: 'meet-found', text: found }) : null));
  }

  // The first few meetings, the rest behind one "Show more", as meeting_list() does in build.py.
  function meetingList(meetings, shown, more) {
    const nodes = [el('ol', { class: 'meetings' }, ...meetings.slice(0, shown).map(meetingNode))];
    const rest = meetings.slice(shown);
    if (rest.length) {
      nodes.push(el('details', { class: 'more' }, el('summary', { text: `${more} (${rest.length})` }),
        el('ol', { class: 'meetings' }, ...rest.map(meetingNode))));
    }
    return nodes;
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
    const byDate = (dir) => (a, b) => dir * a.meeting_date.localeCompare(b.meeting_date) || a.town.localeCompare(b.town);
    const up = group(items.filter((i) => i.meeting_date && i.meeting_date >= today).sort(byDate(1)));
    const past = group(items.filter((i) => i.meeting_date && i.meeting_date < today).sort(byDate(-1)));
    const undated = group(items.filter((i) => !i.meeting_date));
    $('items-upcoming').replaceChildren(...(up.length ? meetingList(up, 5, 'More coming up')
      : [el('p', { class: 'empty', text: 'Nothing on the agenda about these topics right now. New items show up here and in your calendar.' })]));
    $('items-lead').textContent = up.length ? `${plural(up.length, 'meeting')} with items on these topics.` : '';
    $('items-past').replaceChildren(...meetingList(past, 5, 'Show older'));
    $('past-summary').textContent = `Earlier meetings (${past.length})`;
    $('past-wrap').hidden = !past.length;
    $('items-undated').replaceChildren(...meetingList(undated, 5, 'Show more'));
    $('undated-wrap').hidden = !undated.length;
  }

  function renderFeeds(links) {
    $('webcal-link').href = links.ics.replace(/^https?:/, 'webcal:');
    $('rss-link').href = links.rss;
    $('json-link').href = links.json;
    const rows = [
      ['Calendar', links.ics, 'For Google Calendar or Outlook on the web, add a calendar from this URL.'],
      ['RSS', links.rss, 'For feed readers.'],
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
    const linesDoc = fetch('/data/lines.json')
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
    $('wl-summary').textContent = `${plural(wl.towns.length, 'town')}: ${shownTowns}.`;
    window.w351.remember(readonly ? id : wl.id, wl.name, readonly);
    $('wl-body').hidden = false;

    renderFeeds(wl.links);
    LINES = (await linesDoc) || {};
    NEW = new Set(Array.isArray(LINES.new) ? LINES.new : []);
    renderItems(feed.items);
    if (readonly) {
      $('readonly-banner').hidden = false;
      return;
    }
    $('settings').hidden = false;
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
