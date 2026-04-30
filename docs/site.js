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

(() => {
  const inspectors = document.querySelectorAll('[data-outcome-inspector]');
  if (!inspectors.length) return;

  const states = {
    product: {
      eyebrow: 'Product UX',
      claim: 'Claim',
      title: 'Usable surfaces for complex workflows.',
      summary: 'SquadBrain turns recall into a replayable mobile loop; Lasting Ground turns scattered public context into a readable packet route.',
      metric: '2 surfaces',
      check: 'Mobile + packet',
      metricLabel: 'Public demos',
      checkLabel: 'UX evidence',
      steps: ['Open the demo surface.', 'Trace the state the user sees.', 'Verify the linked implementation examples.'],
      primary: ['Open SquadBrain demo', 'https://sulmusic2-star.github.io/squadbrain-showcase/'],
      secondary: ['Open Lasting Ground demo', 'https://sulmusic2-star.github.io/lasting-ground-showcase/']
    },
    logic: {
      eyebrow: 'Systems logic',
      claim: 'Mechanism',
      title: 'Rules turn messy work into repeatable behavior.',
      summary: 'Adaptive priority, matchmaking, source lanes, evidence scoring, and support-depth gates make the systems inspectable instead of vague.',
      metric: '43 tests',
      check: 'Examples folders',
      metricLabel: 'Public checks',
      checkLabel: 'Executable logic',
      steps: ['Open the examples folders.', 'Read the scoring or validation path.', 'Compare behavior against the live surface.'],
      primary: ['Open SquadBrain examples', 'https://github.com/sulmusic2-star/squadbrain-showcase/tree/main/examples'],
      secondary: ['Open Lasting Ground examples', 'https://github.com/sulmusic2-star/lasting-ground-showcase/tree/main/examples']
    },
    evidence: {
      eyebrow: 'Evidence discipline',
      claim: 'Boundary',
      title: 'Claims stay tied to visible support.',
      summary: 'Lasting Ground shows source gaps and cautious language; SquadBrain recomputes competitive results before changing rank state.',
      metric: 'Guardrails',
      check: 'ADRs',
      metricLabel: 'Review states',
      checkLabel: 'Decision records',
      steps: ['Find the risky input.', 'Check the guardrail that handles it.', 'Open the ADR explaining the tradeoff.'],
      primary: ['Open evidence scoring', 'https://github.com/sulmusic2-star/lasting-ground-showcase/blob/main/examples/evidence_scoring.py'],
      secondary: ['Open result validation', 'https://github.com/sulmusic2-star/squadbrain-showcase/blob/main/examples/result-validation.ts']
    },
    delivery: {
      eyebrow: 'Delivery proof',
      claim: 'Verification',
      title: 'The work can be reviewed without a private walkthrough.',
      summary: 'The public trail includes demos, examples, tests, coverage summaries, ADRs, generated outputs, and a portable diligence packet.',
      metric: 'CI',
      check: '3-page packet',
      metricLabel: 'Repeatable checks',
      checkLabel: 'Portable review',
      steps: ['Open the diligence packet.', 'Run the systems lab.', 'Check coverage and decision records.'],
      primary: ['Open diligence packet', 'https://sulmusic2-star.github.io/diligence/'],
      secondary: ['Run systems lab', 'https://sulmusic2-star.github.io/lab/']
    }
  };

  function set(root, selector, value) {
    const el = root.querySelector(selector);
    if (el) el.textContent = value;
  }

  function render(root, key) {
    const state = states[key] || states.product;
    root.querySelectorAll('[data-outcome-key]').forEach((button) => button.classList.toggle('active', button.dataset.outcomeKey === key));
    set(root, '[data-outcome-eyebrow]', state.eyebrow);
    set(root, '[data-outcome-claim]', state.claim);
    set(root, '[data-outcome-title]', state.title);
    set(root, '[data-outcome-summary]', state.summary);
    set(root, '[data-outcome-metric]', state.metric);
    set(root, '[data-outcome-check]', state.check);
    const side = root.querySelectorAll('.outcome-proof-side small');
    if (side[0]) side[0].textContent = state.metricLabel;
    if (side[1]) side[1].textContent = state.checkLabel;
    const steps = root.querySelector('[data-outcome-steps]');
    if (steps) steps.innerHTML = state.steps.map((step, index) => `<li><span>${String(index + 1).padStart(2, '0')}</span>${step}</li>`).join('');
    const primary = root.querySelector('[data-outcome-primary]');
    const secondary = root.querySelector('[data-outcome-secondary]');
    if (primary) { primary.textContent = state.primary[0]; primary.href = state.primary[1]; }
    if (secondary) { secondary.textContent = state.secondary[0]; secondary.href = state.secondary[1]; }
  }

  inspectors.forEach((root) => {
    root.querySelectorAll('[data-outcome-key]').forEach((button) => button.addEventListener('click', () => render(root, button.dataset.outcomeKey)));
    render(root, 'product');
  });
})();

(() => {
  const traces = document.querySelectorAll('[data-atlas-trace]');
  if (!traces.length) return;

  const states = {
    squad: {
      label: 'SquadBrain trace',
      title: 'Competitive practice flow with validation boundary.',
      summary: 'Roster input becomes normalized practice state, adaptive priority, match result, recomputed score, and reviewable rank movement.',
      flow: [['01', 'Input', 'Roster + session state'], ['02', 'Rules', 'Priority + match constraints'], ['03', 'Guardrail', 'Recompute results'], ['04', 'Output', 'Progress + proof']],
      risk: 'Risk handled: untrusted competitive submissions.',
      proof: 'Proof: result-validation.ts + ADR-01',
      primary: ['Open proof file', 'https://github.com/sulmusic2-star/squadbrain-showcase/blob/main/examples/result-validation.ts'],
      secondary: ['Open decision records', 'https://github.com/sulmusic2-star/squadbrain-showcase/tree/main/docs/adr']
    },
    lasting: {
      label: 'Lasting Ground trace',
      title: 'Source-bounded packet flow with uncertainty visible.',
      summary: 'Public source lanes become support depth, evidence score, cautious language, and packet sections that show what the sources can and cannot support.',
      flow: [['01', 'Input', 'Public source lanes'], ['02', 'Rules', 'Authority + freshness'], ['03', 'Guardrail', 'Missing lane states'], ['04', 'Output', 'Packet sections']],
      risk: 'Risk handled: overconfident conclusions from incomplete sources.',
      proof: 'Proof: evidence_scoring.py + packet_composer.py',
      primary: ['Open evidence scoring', 'https://github.com/sulmusic2-star/lasting-ground-showcase/blob/main/examples/evidence_scoring.py'],
      secondary: ['Open packet composer', 'https://github.com/sulmusic2-star/lasting-ground-showcase/blob/main/examples/packet_composer.py']
    },
    review: {
      label: 'Review system trace',
      title: 'Public portfolio flow designed for fast evaluation.',
      summary: 'A reviewer can move from outcome board to systems lab, examples, coverage, decision records, and the portable packet without needing a private walkthrough.',
      flow: [['01', 'Route', 'Outcome board'], ['02', 'Run', 'Systems lab'], ['03', 'Inspect', 'Code + ADRs'], ['04', 'Carry', 'PDF packet']],
      risk: 'Risk handled: portfolio claims with no fast proof path.',
      proof: 'Proof: diligence packet + live lab + public repos',
      primary: ['Open diligence packet', 'https://sulmusic2-star.github.io/diligence/'],
      secondary: ['Run systems lab', 'https://sulmusic2-star.github.io/lab/']
    }
  };

  function set(root, selector, value) {
    const el = root.querySelector(selector);
    if (el) el.textContent = value;
  }

  function render(root, key) {
    const state = states[key] || states.squad;
    root.querySelectorAll('[data-trace-key]').forEach((button) => button.classList.toggle('active', button.dataset.traceKey === key));
    set(root, '[data-trace-label]', state.label);
    set(root, '[data-trace-title]', state.title);
    set(root, '[data-trace-summary]', state.summary);
    set(root, '[data-trace-risk]', state.risk);
    set(root, '[data-trace-proof]', state.proof);
    const flow = root.querySelector('[data-trace-flow]');
    if (flow) flow.innerHTML = state.flow.map(([n, title, body]) => `<div><span>${n}</span><b>${title}</b><small>${body}</small></div>`).join('');
    const primary = root.querySelector('[data-trace-primary]');
    const secondary = root.querySelector('[data-trace-secondary]');
    if (primary) { primary.textContent = state.primary[0]; primary.href = state.primary[1]; }
    if (secondary) { secondary.textContent = state.secondary[0]; secondary.href = state.secondary[1]; }
  }

  traces.forEach((root) => {
    root.querySelectorAll('[data-trace-key]').forEach((button) => button.addEventListener('click', () => render(root, button.dataset.traceKey)));
    render(root, 'squad');
  });
})();
