/* Progressive enhancement: every destination is already a real link in HTML. */
(() => {
  'use strict';
  const grid = document.getElementById('app-grid');
  const cards = Array.from(grid.querySelectorAll('.app-card'));
  const search = document.getElementById('app-search');
  const sort = document.getElementById('sort-order');
  const filters = Array.from(document.querySelectorAll('button[data-category]'));
  const views = Array.from(document.querySelectorAll('button[data-view]'));
  const count = document.getElementById('result-count');
  const empty = document.getElementById('empty-state');
  const categories = new Set(filters.map(button => button.dataset.category));
  let category = 'all';
  let view = 'grid';
  const normalize = text => text.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase();

  function updateUrl() {
    const url = new URL(window.location.href);
    for (const [key, value, baseline] of [['q', search.value.trim(), ''], ['category', category, 'all'], ['sort', sort.value, 'collection'], ['view', view, 'grid']]) {
      if (value === baseline) url.searchParams.delete(key);
      else url.searchParams.set(key, value);
    }
    // file:// previews and restrictive browser contexts still retain all controls.
    try { window.history.replaceState(null, '', url); } catch (_) { /* optional URL state */ }
  }

  function apply(syncUrl = true) {
    const tokens = normalize(search.value.trim()).split(/\s+/).filter(Boolean);
    let visible = 0;
    for (const card of cards) {
      const match = (category === 'all' || card.dataset.category === category) && tokens.every(token => normalize(card.dataset.search).includes(token));
      card.hidden = !match;
      if (match) visible++;
    }
    const ordered = [...cards].sort(sort.value === 'name'
      ? (a, b) => a.dataset.name.localeCompare(b.dataset.name) || Number(a.dataset.order) - Number(b.dataset.order)
      : (a, b) => Number(a.dataset.order) - Number(b.dataset.order));
    for (const card of ordered) grid.appendChild(card);
    for (const button of filters) button.setAttribute('aria-pressed', String(button.dataset.category === category));
    for (const button of views) button.setAttribute('aria-pressed', String(button.dataset.view === view));
    grid.dataset.view = view;
    count.textContent = visible === cards.length ? `${visible} instruments` : `${visible} of ${cards.length} instruments`;
    empty.hidden = visible !== 0;
    grid.hidden = visible === 0;
    if (syncUrl) updateUrl();
  }

  function readUrl() {
    const params = new URLSearchParams(window.location.search);
    search.value = params.get('q') || '';
    category = categories.has(params.get('category')) ? params.get('category') : 'all';
    sort.value = params.get('sort') === 'name' ? 'name' : 'collection';
    view = params.get('view') === 'list' ? 'list' : 'grid';
    apply(false);
  }

  search.addEventListener('input', () => apply());
  search.addEventListener('keydown', event => {
    if (event.key === 'Escape') { search.value = ''; apply(); }
  });
  sort.addEventListener('change', () => apply());
  filters.forEach(button => button.addEventListener('click', () => { category = button.dataset.category; apply(); }));
  views.forEach(button => button.addEventListener('click', () => { view = button.dataset.view; apply(); }));
  document.getElementById('reset-filters').addEventListener('click', () => {
    search.value = ''; category = 'all'; apply(); search.focus();
  });
  document.addEventListener('keydown', event => {
    if (event.key === '/' && !event.metaKey && !event.ctrlKey && !event.altKey && !event.target.closest('input, textarea, select, [contenteditable]')) {
      event.preventDefault(); search.focus();
    }
  });
  window.addEventListener('popstate', readUrl);
  readUrl();
  document.querySelector('.enhanced-controls').hidden = false;
})();
