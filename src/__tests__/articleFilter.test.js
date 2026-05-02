'use strict';

const { getActiveCat, buildUrl, applyFilter, initFilter } = require('../scripts/articleFilter');

// ─── Helpers ────────────────────────────────────────────────────────────────

/** Minimal card mock: tracks display changes and exposes dataset. */
function makeCard(category) {
  return { dataset: { category }, style: { display: '' } };
}

/** Minimal button mock: tracks classList.toggle calls and click listeners. */
function makeBtn(cat) {
  const listeners = {};
  return {
    dataset: { cat },
    classList: { toggle: jest.fn() },
    addEventListener: jest.fn(function (event, handler) {
      listeners[event] = handler;
    }),
    _fire: function (event, arg) {
      if (listeners[event]) listeners[event](arg);
    },
  };
}

// ─── getActiveCat ───────────────────────────────────────────────────────────

describe('getActiveCat', () => {
  test('returns "all" for empty search string', () => {
    expect(getActiveCat('')).toBe('all');
  });

  test('returns "all" when cat param is absent', () => {
    expect(getActiveCat('?foo=bar')).toBe('all');
  });

  test('returns the cat param value when present', () => {
    expect(getActiveCat('?cat=tools')).toBe('tools');
  });

  test('handles multiple params — picks cat', () => {
    expect(getActiveCat('?page=1&cat=research&q=test')).toBe('research');
  });
});

// ─── buildUrl ───────────────────────────────────────────────────────────────

describe('buildUrl', () => {
  test('returns /articles/ for "all"', () => {
    expect(buildUrl('all')).toBe('/articles/');
  });

  test('returns query string URL for a specific category', () => {
    expect(buildUrl('tools')).toBe('/articles/?cat=tools');
  });

  test('returns query string URL for research category', () => {
    expect(buildUrl('research')).toBe('/articles/?cat=research');
  });
});

// ─── applyFilter ────────────────────────────────────────────────────────────

describe('applyFilter', () => {
  test('"all" shows every card', () => {
    const cards = [makeCard('tools'), makeCard('research'), makeCard('bug-bounty')];
    const btns = [makeBtn('all'), makeBtn('tools')];

    applyFilter('all', cards, btns);

    cards.forEach(c => expect(c.style.display).toBe(''));
  });

  test('hides cards not matching the active category', () => {
    const tools = makeCard('tools');
    const research = makeCard('research');
    const btns = [makeBtn('tools')];

    applyFilter('tools', [tools, research], btns);

    expect(tools.style.display).toBe('');
    expect(research.style.display).toBe('none');
  });

  test('marks the matching button as active', () => {
    const btns = [makeBtn('all'), makeBtn('tools'), makeBtn('research')];
    applyFilter('tools', [], btns);

    expect(btns[0].classList.toggle).toHaveBeenCalledWith('active', false);
    expect(btns[1].classList.toggle).toHaveBeenCalledWith('active', true);
    expect(btns[2].classList.toggle).toHaveBeenCalledWith('active', false);
  });

  test('re-shows a previously hidden card when switching to "all"', () => {
    const card = makeCard('tools');
    card.style.display = 'none'; // simulates a prior filter

    applyFilter('all', [card], []);

    expect(card.style.display).toBe('');
  });

  test('works with an empty card list', () => {
    const btns = [makeBtn('all')];
    expect(() => applyFilter('tools', [], btns)).not.toThrow();
  });
});

// ─── initFilter ─────────────────────────────────────────────────────────────

describe('initFilter', () => {
  function makeDocWin(searchString, cards, btns) {
    const popstateListeners = [];
    return {
      doc: {
        querySelectorAll: jest.fn(function (selector) {
          if (selector === '#article-list .article-card') return cards;
          if (selector === '.filter-btn') return btns;
          return [];
        }),
      },
      win: {
        location: { search: searchString },
        history: { pushState: jest.fn() },
        addEventListener: jest.fn(function (event, handler) {
          if (event === 'popstate') popstateListeners.push(handler);
        }),
        _firePopstate: function () {
          popstateListeners.forEach(fn => fn());
        },
      },
    };
  }

  test('applies filter on init based on location.search', () => {
    const cards = [makeCard('tools'), makeCard('research')];
    const btns = [makeBtn('all'), makeBtn('tools')];
    const { doc, win } = makeDocWin('?cat=tools', cards, btns);

    initFilter(doc, win);

    expect(cards[0].style.display).toBe('');    // tools — shown
    expect(cards[1].style.display).toBe('none'); // research — hidden
  });

  test('clicking a button updates history and re-filters', () => {
    const cards = [makeCard('tools'), makeCard('research')];
    const btns = [makeBtn('all'), makeBtn('research')];
    const { doc, win } = makeDocWin('', cards, btns);

    initFilter(doc, win);

    // Simulate click on "research" button (index 1)
    const researchBtn = btns[1];
    expect(researchBtn.addEventListener).toHaveBeenCalledWith('click', expect.any(Function));
    researchBtn._fire('click', { preventDefault: jest.fn() });

    expect(win.history.pushState).toHaveBeenCalledWith({}, '', '/articles/?cat=research');
    expect(cards[0].style.display).toBe('none'); // tools — hidden
    expect(cards[1].style.display).toBe('');     // research — shown
  });

  test('clicking "all" button navigates to /articles/', () => {
    const btns = [makeBtn('all')];
    const { doc, win } = makeDocWin('?cat=tools', [], btns);

    initFilter(doc, win);

    btns[0]._fire('click', { preventDefault: jest.fn() });

    expect(win.history.pushState).toHaveBeenCalledWith({}, '', '/articles/');
  });

  test('popstate event re-reads location and re-filters', () => {
    const cards = [makeCard('tools'), makeCard('research')];
    const btns = [makeBtn('all'), makeBtn('research')];
    const { doc, win } = makeDocWin('', cards, btns);

    initFilter(doc, win);

    // Simulate browser back — location.search changes to ?cat=research
    win.location.search = '?cat=research';
    win._firePopstate();

    expect(cards[0].style.display).toBe('none'); // tools — hidden
    expect(cards[1].style.display).toBe('');     // research — shown
  });

  test('registers a popstate listener on win', () => {
    const { doc, win } = makeDocWin('', [], []);
    initFilter(doc, win);
    expect(win.addEventListener).toHaveBeenCalledWith('popstate', expect.any(Function));
  });
});
