/**
 * Parse the active category from a URL query string.
 * @param {string} search - URL search string (e.g. '?cat=tools')
 * @returns {string} category key, defaults to 'all'
 */
export function getActiveCat(search) {
  var params = new URLSearchParams(search || '');
  return params.get('cat') || 'all';
}

/**
 * Build the canonical URL for a category filter.
 * @param {string} cat
 * @returns {string}
 */
export function buildUrl(cat) {
  return cat === 'all' ? '/articles/' : '/articles/?cat=' + cat;
}

/**
 * Apply a category filter: show/hide cards, mark the active button.
 * @param {string} cat
 * @param {Array|NodeList} cards   - elements with dataset.category and style.display
 * @param {Array|NodeList} buttons - elements with dataset.cat and classList.toggle
 */
export function applyFilter(cat, cards, buttons) {
  Array.prototype.forEach.call(cards, function (card) {
    if (cat === 'all' || card.dataset.category === cat) {
      card.style.display = '';
    } else {
      card.style.display = 'none';
    }
  });
  Array.prototype.forEach.call(buttons, function (btn) {
    btn.classList.toggle('active', btn.dataset.cat === cat);
  });
}

/**
 * Wire up the article filter to the page. Reads the initial ?cat= param,
 * applies the filter, then handles click and popstate events.
 *
 * @param {Document} [doc] - injectable for testing (defaults to document)
 * @param {Window}   [win] - injectable for testing (defaults to window)
 */
export function initFilter(doc, win) {
  /* globals document, window */
  doc = doc || document;
  win = win || window;

  var cards = doc.querySelectorAll('#article-list .article-card');
  var buttons = doc.querySelectorAll('.filter-btn');

  // Apply on page load
  applyFilter(getActiveCat(win.location.search), cards, buttons);

  // Intercept filter clicks — update URL and filter without navigation
  Array.prototype.forEach.call(buttons, function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      var cat = btn.dataset.cat || 'all';
      win.history.pushState({}, '', buildUrl(cat));
      applyFilter(cat, cards, buttons);
    });
  });

  // Handle back/forward
  win.addEventListener('popstate', function () {
    applyFilter(getActiveCat(win.location.search), cards, buttons);
  });
}
