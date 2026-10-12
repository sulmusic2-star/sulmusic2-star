// /w/<key> (or /w?id=<key>): one alert list. A private key shows everything, including the
// private and share links, the daily message, edit and delete. A share (read-only) key shows the
// items and feeds only. ?new=1 after creating shows the "save your private link" banner.
(() => {
  const app = document.getElementById('wl-app');
  if (!app) return;
  const $ = (id) => document.getElementById(id);
  const TOPICS = JSON.parse(app.dataset.topics || '{}'); // key: [label, phrase, plural]
  const ORDER = JSON.parse(app.dataset.order || '[]');
  const TAGS = JSON.parse(app.dataset.tags || '{}'); // topic key: label shown on each item
  const MENTION = JSON.parse(app.dataset.mention || '{}'); // topic key: words for "the agenda mentions …"
  const BASE = app.dataset.base || location.origin; // the site's public address, for share links
  const slug = (name) => String(name).toLowerCase().replace(/['’]/g, '').replace(/\s+/g, '-');
  const KINDS = { slack: 'Slack', teams: 'Microsoft Teams', teams_workflow: 'Microsoft Teams', discord: 'Discord', json: 'your webhook' };
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
    return d.toLocaleDateString('en-US', opts).replace(/^(\w{3}),/, '$1'); // "Tue Oct 13", as build.py writes it
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

  // Same wording as board_label() in build.py.
  function boardLabel(item) {
    if (item.board_key === 'town_meeting') return 'town meeting';
    let b = String(item.board || '').replace(/\s*\([^)]*\)/g, '').replace(/\s+[-–]\s+.*$/, '').replace(/^The\s+/, '').replace(/\s+Meetings?$/, '').trim();
    b = b.replace(/\s*\/.*$/, '').replace(/\s+(?:FY\s?\d{2,4}|Public Hearings?|Agendas?)$/i, '').replace(/^(\w+), (.+ of)$/, '$2 $1');
    if (b && b === b.toUpperCase()) b = b.toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase());
    return b || 'town board';
  }
  function meetingBoard(m) {
    if (m.source === 'massdep_wetlands') return 'Wetlands filing to the state';
    if (m.board_key === 'town_meeting') return 'Town meeting warrant';
    return m.board.charAt(0).toUpperCase() + m.board.slice(1);
  }


  // The plain line for one item (from /data/lines.json, written by agenda_line() in build.py). An
  // item newer than that file gets "Mentions …" and its own agenda text.
  function lineFor(it) {
    const known = LINES.lines && LINES.lines[it.id];
    if (known) return { say: known[0], quote: known[1], note: known[2] || '', kind: known[3] || 'act', key: known[4] || '', who: known[5] || '' };
    // An item newer than /data/lines.json: say which subjects its agenda mentions.
    const who = it.board_key === 'town_meeting' ? 'Town meeting' : `The ${boardLabel(it).replace(/^the /i, '')}`;
    const whose = it.board_key === 'town_meeting' ? 'The town meeting warrant' : `${who} agenda`;
    return { say: `${whose} mentions ${mentionText(it.topics || [])}.`, quote: String(it.snippet || '').slice(0, 200), note: '', kind: 'mention', key: '', who };
  }
  const order = (topics) => [...new Set(topics)].sort((a, b) => (ORDER.includes(a) ? ORDER.indexOf(a) : 99) - (ORDER.includes(b) ? ORDER.indexOf(b) : 99));
  const mentionText = (topics) => joinAnd(order(topics).map((t) => MENTION[t] || t.replace(/_/g, ' ')).slice(0, 3));
  function tagText(topics) {
    const tags = order(topics).map((t) => TAGS[t] || t.replace(/_/g, ' '));
    return tags.length ? [tags[0], ...tags.slice(1).map((t) => t.toLowerCase())].join(', ') : '';
  }

  // Items grouped by meeting (town, board, day), as group_meetings() does in build.py.
  function group(items) {
    const meetings = new Map();
    for (const it of items) {
      const d = (it.meeting_date || '').slice(0, 10);
      const dep = it.source === 'massdep_wetlands';
      const key = `${it.state}:${it.town}|${dep}|${it.board_key || boardLabel(it)}|${d}`;
      if (!meetings.has(key)) {
        const at = (LINES.at && LINES.at[it.source_url]) || ['', ''];
        meetings.set(key, { state: it.state, town: it.town, town_url: it.town_url, board: boardLabel(it), board_key: it.board_key,
          source: it.source, date: d, lines: new Map(), docs: [], found: it.first_seen || '', time: at[0], place: at[1],
          id: `m-${slug(`${it.town}-${boardLabel(it)}-${d || 'warrant'}`)}` });
      }
      const m = meetings.get(key);
      const t = lineFor(it);
      if (!m.lines.has(t.say)) m.lines.set(t.say, { quotes: [], topics: [], isNew: false, note: t.note, kind: t.kind, key: t.key, who: t.who });
      const entry = m.lines.get(t.say);
      if (t.quote && !entry.quotes.includes(t.quote)) entry.quotes.push(t.quote);
      for (const x of it.topics || []) if (!entry.topics.includes(x)) entry.topics.push(x);
      entry.isNew = entry.isNew || NEW.has(it.id);
      entry.note = entry.note || t.note;
      if (!m.docs.some((x) => x.url === it.source_url)) {
        m.docs.push({ url: it.source_url, pdf: /\.pdf$/i.test(String(it.source_url).split('?')[0]) || /\(pdf\)/i.test(it.document_title || '') });
      }
      if (it.first_seen && (!m.found || it.first_seen < m.found)) m.found = it.first_seen;
    }
    for (const m of meetings.values()) m.lines = tidy(m.lines, m.board_key === 'town_meeting');
    return [...meetings.values()];
  }

  // As tidy_lines() in build.py: one sentence per project, no sentence inside another, the
  // "mentions" sentences folded into one at the end.
  function tidy(lines, townMeeting) {
    const core = (s) => s.toLowerCase().replace(' (continued from an earlier meeting)', '').replace(/\.$/, '')
      .replace(' will vote on ', ' will discuss ').replace('zoning ordinance', 'zoning bylaw');
    const merge = (into, e) => {
      for (const q of e.quotes) if (!into.quotes.includes(q)) into.quotes.push(q);
      for (const t of e.topics) if (!into.topics.includes(t)) into.topics.push(t);
      into.isNew = into.isNew || e.isNew;
      into.note = into.note || e.note;
    };
    const named = new Map([...lines].filter(([, v]) => v.kind !== 'mention'));
    const seen = new Map();
    for (const k of [...named.keys()].sort((a, b) => (named.get(a).kind !== 'act') - (named.get(b).kind !== 'act') || b.length - a.length)) {
      const key = named.get(k).key;
      if (key && seen.has(key)) {
        merge(named.get(seen.get(key)), named.get(k));
        named.delete(k);
      } else if (key) seen.set(key, k);
    }
    for (const short of [...named.keys()].sort((a, b) => core(a).length - core(b).length)) {
      const longer = [...named.keys()].find((k) => k !== short && core(k).includes(core(short)));
      if (longer) {
        merge(named.get(longer), named.get(short));
        named.delete(short);
      }
    }
    const mentions = [...lines.values()].filter((v) => v.kind === 'mention');
    if (!mentions.length) return named;
    const all = { quotes: [], topics: [], isNew: false, note: '', kind: 'mention', key: '', who: mentions[0].who };
    for (const v of mentions) merge(all, v);
    const said = [...named.keys()].map(core).join(' ');
    const left = order(all.topics).filter((t) => !said.includes((MENTION[t] || t).toLowerCase().replace(/s$/, '')));
    if (left.length) {
      all.topics = left;
      const whose = townMeeting ? 'The town meeting warrant' : `${all.who} agenda`;
      named.set(`${whose} ${named.size ? 'also ' : ''}mentions ${mentionText(left)}.`, all);
    }
    return named;
  }

  const shortDay = (iso) => new Date(`${iso.slice(0, 10)}T12:00:00Z`).toLocaleDateString('en-US', { month: 'short', day: 'numeric', timeZone: 'UTC' });
  function postedText(m) {
    if (!m.found) return '';
    const what = m.source === 'massdep_wetlands' ? 'Filed' : (m.board_key === 'town_meeting' ? 'Warrant posted' : 'Agenda posted');
    return `${what} by ${shortDay(m.found)}`;
  }
  // As place_text() in build.py.
  const placeText = (p) => (p === 'online' ? 'Online meeting' : p.replace(/ or online$/, ', or join online'));
  const whenText = (m) => (m.date ? dayLabel(m.date) + (m.time ? `, ${m.time}` : '') : '');

  // One meeting, as meeting_html() renders it in build.py.
  function meetingNode(m) {
    const dep = m.source === 'massdep_wetlands';
    const source = dep ? 'the state filing' : (m.board_key === 'town_meeting' ? 'the warrant' : 'the agenda');
    const what = dep ? 'filing' : (m.board_key === 'town_meeting' ? 'warrant' : 'agenda');
    const tid = `${m.state}:${m.town}`;
    const next = homeTown && tid !== homeTown ? ` (next to ${homeTown.split(':').slice(1).join(':')})` : '';
    const when = whenText(m);
    const head = el('h3', { class: 'meet-head', 'data-slop-ignore': '' },
      el('span', { class: 'meet-town' }, el('a', { href: townPath(m.town_url), text: m.town + (m.state && m.state !== 'MA' ? `, ${m.state}` : '') }), next), ' ',
      m.date ? el('span', { class: 'meet-day' }, el('time', { datetime: m.date, text: when })) : null, ' ',
      m.place && !dep ? el('span', { class: 'meet-place', text: placeText(m.place) }) : null);
    const posted = m.found ? `, posted by ${fmtDate(m.found.slice(0, 10))}` : '';
    const cite = `${m.town}, ${m.state}, ${meetingBoard(m)}. Agenda for the meeting of ${m.date ? fmtDate(m.date) : 'no meeting date'}${posted}. ${m.docs[0] ? m.docs[0].url : ''}`;
    const copy = (text) => {
      const b = el('button', { type: 'button', class: 'link-btn', 'data-copy': text, text: 'Copy citation' });
      return b;
    };
    const lineNode = ([text, e]) => el('li', { class: 'line' },
      tagText(e.topics) ? el('p', { class: 'item-tags', text: tagText(e.topics) }) : null,
      el('p', { class: 'line-say' }, e.isNew ? el('span', { class: 'badge-new', text: 'New' }) : null, e.isNew ? ' ' : null, text),
      e.note ? el('p', { class: 'line-note', text: e.note }) : null,
      el('div', { class: 'line-tools' },
        e.quotes.length ? el('details', { class: 'item-words' }, el('summary', { text: 'Show the agenda text' }),
          el('p', { class: 'item-from', text: `Quoted from ${source}:` }),
          ...e.quotes.slice(0, 3).map((q) => el('blockquote', { class: 'item-quote', text: q }))) : null,
        copy(cite)));
    const where = `${m.town} ${meetingBoard(m)}, ${fmtDate(m.date) || 'no date'}`;
    const links = m.docs.map((d, i) => el('a', { class: 'item-link', href: d.url, rel: 'nofollow noopener', target: '_blank' },
      `${i ? `Another version of the ${what}` : `Open the ${what}`}${d.pdf ? ' (PDF)' : ''}`, el('span', { class: 'sr-only', text: `: ${where}` })));
    const first = [...m.lines.keys()][0] || '';
    const share = el('button', { type: 'button', class: 'link-btn', 'data-share': '', 'data-url': `${BASE}${townPath(m.town_url)}#${m.id}`,
      'data-title': `${m.town} ${meetingBoard(m)}${when ? `, ${when}` : ''}`, 'data-text': first, text: 'Share this meeting' });
    const postedLine = postedText(m);
    return el('li', { class: 'meeting', id: m.id }, head,
      el('ul', { class: 'lines' }, ...[...m.lines].map(lineNode)),
      el('p', { class: 'meet-src' }, ...links, postedLine ? el('span', { class: 'meet-found', text: postedLine }) : null, ' ', share));
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
    $('wl-title').textContent = 'We couldn’t open these alerts';
    document.title = `We couldn’t open these alerts | ${SITE}`;
    const box = $('wl-error');
    box.replaceChildren(document.createTextNode(`${message} `), el('a', { href: '/watch', text: linkText }));
    box.hidden = false;
    $('wl-body').hidden = true;
  }

  async function api(method, url) {
    const res = await fetch(url, { method, cache: 'no-store', headers: { Accept: 'application/json' } });
    const data = await res.json().catch(() => ({}));
    if (!res.ok || data.ok === false) {
      const err = new Error(data.error || 'Something went wrong on our end. Try again in a minute.');
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
      : [el('p', { class: 'empty', text: 'Nothing about these subjects on the agendas posted so far. We check new agendas every morning.' })]));
    $('items-lead').textContent = '';
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
      ['Calendar', links.ics, 'In Google Calendar or Outlook on the web, add a calendar “from URL” and paste this.'],
      ['RSS', links.rss, 'For news reader apps.'],
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
        ? `Emails go to ${mail.masked}, at most once a day, only when something new is posted. `
        : `We sent a link to ${mail.masked}. Emails start once you click it. `, edit, '.');
      out.hidden = false;
      const at = mail.resend_available_at ? Date.parse(mail.resend_available_at) : NaN;
      if (!mail.confirmed && !Number.isNaN(at) && at <= Date.now()) {
        const button = el('button', { type: 'button', class: 'btn small quiet', text: 'Send the link again' });
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
      out.replaceChildren('No email address yet. ', edit, '.');
      out.hidden = false;
    }
  }

  function renderWebhook(wl) {
    const status = $('hook-status');
    const hook = wl.webhook;
    $('hook-section').hidden = false;
    if (!hook || !hook.configured) {
      status.replaceChildren('Not posting to a chat app. ', el('a', { href: `/alerts-for-groups?edit=${wl.id}`, text: 'Post to Slack, Teams or Discord' }), '.');
      return;
    }
    const parts = [`New items are posted to ${KINDS[hook.kind] || 'your chat app'} (${hook.masked}) once a day. `];
    const d = wl.last_delivery;
    if (d && d.ok) parts.push(`Last post ${fmtDate(d.at)}: ${plural(d.sent, 'item')}${d.more ? ` and a link to ${d.more} more` : ''}.`);
    else if (d) parts.push(`The last message, on ${fmtDate(d.at)}, failed (${d.error || `HTTP ${d.status}`}). We’ll try again with the next daily run. Check the webhook URL.`);
    else parts.push('Nothing posted yet. We post once a day, only when something new is posted.');
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
    $('plan-line').replaceChildren(`${plan === PLANS.beta ? 'Free' : plan}. `, el('a', { href: '/pricing', text: 'Is it free?' }));
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
        $('wl-title').textContent = 'Alerts deleted';
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
        ` Alerts will come to ${wl.email && wl.email.masked ? wl.email.masked : 'your inbox'} at most once a day, only when something new is posted.`);
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
