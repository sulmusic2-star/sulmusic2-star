(() => {
  const consoles = document.querySelectorAll('[data-proof-console]');
  if (!consoles.length) return;

  const states = {
    squad: {
      eyebrow: 'Mobile product system',
      title: 'SquadBrain',
      summary: 'Adaptive practice, matchmaking, and validated results.',
      metric: '25 tests',
      coverage: '98.3% coverage',
      status: 'React Native / TypeScript',
      proof: 'Ranking → adaptive queue → result validation',
      primaryText: 'Open SquadBrain demo',
      primaryHref: 'https://sulmusic2-star.github.io/squadbrain-showcase/',
      codeHref: 'https://github.com/sulmusic2-star/squadbrain-showcase/tree/main/examples',
      log: ['loaded roster state', 'normalized team/player inputs', 'prioritized weak recall', 'validated match result']
    },
    lasting: {
      eyebrow: 'Evidence system',
      title: 'Lasting Ground',
      summary: 'Source lanes, evidence scoring, guarded language, and packet output.',
      metric: '18 tests',
      coverage: '93.29% coverage',
      status: 'Python / packet logic',
      proof: 'Source lanes → support depth → packet sections',
      primaryText: 'Open Lasting Ground demo',
      primaryHref: 'https://sulmusic2-star.github.io/lasting-ground-showcase/',
      codeHref: 'https://github.com/sulmusic2-star/lasting-ground-showcase/tree/main/examples',
      log: ['checked source lanes', 'scored evidence support', 'guarded claim language', 'composed packet output']
    },
    route: {
      eyebrow: 'Evaluator route',
      title: 'Review path',
      summary: 'A reviewer can move from overview to runnable logic to public code fast.',
      metric: '3-page packet',
      coverage: '43 public tests',
      status: 'Packet / lab / repos',
      proof: 'Diligence packet → systems lab → examples',
      primaryText: 'Open diligence packet',
      primaryHref: 'https://sulmusic2-star.github.io/diligence/',
      codeHref: 'https://sulmusic2-star.github.io/lab/',
      log: ['skim packet', 'run systems lab', 'open examples', 'check coverage + ADRs']
    }
  };

  function setText(root, selector, value) {
    const el = root.querySelector(selector);
    if (el) el.textContent = value;
  }

  function render(root, key) {
    const state = states[key] || states.squad;
    root.querySelectorAll('[data-proof-tab]').forEach((button) => {
      const active = button.dataset.proofTab === key;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', active ? 'true' : 'false');
    });

    setText(root, '[data-proof-eyebrow]', state.eyebrow);
    setText(root, '[data-proof-title]', state.title);
    setText(root, '[data-proof-summary]', state.summary);
    setText(root, '[data-proof-metric]', state.metric);
    setText(root, '[data-proof-coverage]', state.coverage);
    setText(root, '[data-proof-status]', state.status);
    setText(root, '[data-proof-route]', state.proof);

    const primary = root.querySelector('[data-proof-primary]');
    if (primary) {
      primary.textContent = state.primaryText;
      primary.href = state.primaryHref;
    }
    const code = root.querySelector('[data-proof-code]');
    if (code) code.href = state.codeHref;

    const log = root.querySelector('[data-proof-log]');
    if (log) {
      log.innerHTML = state.log.map((line, index) => `<li><span>${String(index + 1).padStart(2, '0')}</span>${line}</li>`).join('');
    }
  }

  consoles.forEach((root) => {
    root.querySelectorAll('[data-proof-tab]').forEach((button) => {
      button.addEventListener('click', () => render(root, button.dataset.proofTab));
    });
    render(root, 'squad');
  });
})();

(() => {
  const inspectors = document.querySelectorAll('[data-packet-inspector]');
  if (!inspectors.length) return;

  inspectors.forEach((root) => {
    const image = root.querySelector('[data-packet-image]');
    const title = root.querySelector('[data-packet-title]');
    const note = root.querySelector('[data-packet-note]');

    root.querySelectorAll('[data-packet-page]').forEach((button) => {
      button.addEventListener('click', () => {
        root.querySelectorAll('[data-packet-page]').forEach((tab) => tab.classList.remove('active'));
        button.classList.add('active');
        if (image) image.src = button.dataset.packetPage;
        if (title) title.textContent = button.dataset.packetTitle || button.textContent;
        if (note) note.textContent = button.dataset.packetNote || '';
      });
    });
  });
})();
