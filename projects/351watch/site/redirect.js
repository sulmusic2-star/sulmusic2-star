// Old URLs (/proof, /privacy, /bot) are small pages that send visitors to their new home and keep
// the section they asked for: <script src="/redirect.js" data-to="/how-it-works" data-default="#privacy"
// data-map='{"#contact":"#contact"}'>. A <meta http-equiv="refresh"> on the same page covers no-JS.
(() => {
  const s = document.currentScript;
  if (!s) return;
  let map = {};
  try {
    map = JSON.parse(s.dataset.map || '{}');
  } catch {
    map = {};
  }
  const mapped = map[location.hash];
  const dest = mapped && mapped.startsWith('/') ? mapped : s.dataset.to + (mapped || s.dataset.default || '');
  location.replace(dest);
})();
