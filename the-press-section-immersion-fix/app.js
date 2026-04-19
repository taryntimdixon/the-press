(() => {
  const DAILY_GRID_SCOPE = '.daily-section-feed, .daily-home-section, [data-daily-section-feed], [data-daily-feed], [data-live-feed]';
  const SECTION_GRID_SELECTOR = [
    '.page-section main .cards-section .cards-grid--archive',
    '.page-section main .cards-grid--archive',
    '.page-section .cards-section .cards-grid--archive',
    '.page-section .cards-grid--archive',
    '.page-section main .cards-section .cards-grid',
    '.page-section main .cards-grid'
  ].join(', ');

  function isSectionPage() {
    return Boolean(document.body && document.body.classList.contains('page-section'));
  }

  function removeOpenGraphGhost(root = document) {
    const scope = root.body || root.documentElement || root;
    if (!scope || !document.createTreeWalker) return;

    const ghostPattern = /<\\?!?--\s*Open Graph(?:\s*\/\s*social sharing)?\s*-->/gi;
    const walker = document.createTreeWalker(scope, NodeFilter.SHOW_TEXT);
    const emptyNodes = [];

    while (walker.nextNode()) {
      const node = walker.currentNode;
      if (!ghostPattern.test(node.nodeValue || '')) continue;
      ghostPattern.lastIndex = 0;
      node.nodeValue = (node.nodeValue || '').replace(ghostPattern, '').replace(/^\s+$/, '');
      if (!node.nodeValue) emptyNodes.push(node);
    }

    emptyNodes.forEach((node) => node.parentNode && node.parentNode.removeChild(node));
  }

  function findSectionArchiveGrid() {
    const grids = Array.from(document.querySelectorAll(SECTION_GRID_SELECTOR));
    return grids.find((grid) => !grid.closest(DAILY_GRID_SCOPE)) || null;
  }

  function markSectionArchiveReady() {
    if (!isSectionPage()) return;
    document.body.classList.add('press-section-grid-ready');
    document.body.classList.remove('press-section-grid-loading');
  }

  function bootSectionImmersionGuard() {
    removeOpenGraphGhost();
    if (!isSectionPage()) return;

    document.body.classList.add('press-section-grid-loading');

    const grid = findSectionArchiveGrid();
    if (!grid) {
      markSectionArchiveReady();
      return;
    }

    const initialCount = grid.querySelectorAll('.story-card, .archive-card').length;

    const readyIfHydrated = () => {
      removeOpenGraphGhost();
      const currentGrid = findSectionArchiveGrid();
      const currentCount = currentGrid ? currentGrid.querySelectorAll('.story-card, .archive-card').length : 0;
      if (currentGrid && (currentGrid.dataset.pressSectionHydrated === 'true' || currentCount !== initialCount || currentCount > 2)) {
        markSectionArchiveReady();
      }
    };

    const observer = new MutationObserver(readyIfHydrated);
    observer.observe(grid, { childList: true, subtree: true });

    window.setTimeout(readyIfHydrated, 80);
    window.setTimeout(readyIfHydrated, 450);
    window.setTimeout(() => {
      markSectionArchiveReady();
      observer.disconnect();
    }, 3600);
  }

  window.pressFindSectionArchiveGrid = findSectionArchiveGrid;
  window.pressMarkSectionArchiveReady = markSectionArchiveReady;
  window.pressRemoveOpenGraphGhost = removeOpenGraphGhost;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bootSectionImmersionGuard, { once: true });
  } else {
    bootSectionImmersionGuard();
  }
})();

(() => {

  const BODY_CLASS = 'page-section';

  const GRID_SELECTOR = [

    '.page-section .cards-grid--archive',

    '.page-section .cards-grid',

    '.cards-grid--archive',

    '.cards-grid'

  ].join(', ');

  const CARD_SELECTOR = '.story-card, .archive-card';

  const DAILY_SECTION_SELECTOR = [

    '.daily-section-feed',

    '.daily-home-section',

    '[data-daily-section-feed]',

    '[data-daily-feed]',

    '[data-live-feed]'

  ].join(', ');

  let preservedCards = [];

  let preservedKeys = new Set();

  let observer = null;

  let restoreQueued = false;

  let isRestoring = false;

  function isSectionPage() {

    return document.body && document.body.classList.contains(BODY_CLASS);

  }

  function normalizeHref(href) {

    return String(href || '')

      .trim()

      .replace(/^https?:\/\/[^/]+\//i, '')

      .replace(/^\/+/, '')

      .replace(/[?#].*$/, '')

      .toLowerCase();

  }

  function normalizeText(text) {

    return String(text || '')

      .trim()

      .replace(/\s+/g, ' ')

      .toLowerCase();

  }

  function cardKey(card) {

    if (!card) return '';

    const link = card.querySelector('a[href]');

    const href = normalizeHref(link && link.getAttribute('href'));

    if (href) return `url:${href}`;

    const heading = card.querySelector('h1, h2, h3, .story-card__title, .archive-card__title');

    const title = normalizeText(heading ? heading.textContent : card.textContent);

    return title ? `title:${title}` : '';

  }

  function isDailyGrid(grid) {

    return Boolean(grid && grid.closest(DAILY_SECTION_SELECTOR));

  }

  function findBestCategoryGrid() {

    const grids = Array.from(document.querySelectorAll(GRID_SELECTOR));

    if (!grids.length) return null;

    const nonDailyWithCards = grids.find((grid) => {

      return !isDailyGrid(grid) && grid.querySelector(CARD_SELECTOR);

    });

    if (nonDailyWithCards) return nonDailyWithCards;

    const archiveGrid = grids.find((grid) => {

      return !isDailyGrid(grid) && grid.classList.contains('cards-grid--archive');

    });

    if (archiveGrid) return archiveGrid;

    return grids.find((grid) => !isDailyGrid(grid)) || null;

  }

  function saveOriginalCards() {

    if (!isSectionPage()) return;

    const grid = findBestCategoryGrid();

    if (!grid) return;

    const cards = Array.from(grid.querySelectorAll(CARD_SELECTOR));

    if (!cards.length) return;

    preservedCards = cards.map((card) => card.cloneNode(true));

    preservedKeys = new Set(

      preservedCards

        .map(cardKey)

        .filter(Boolean)

    );

    grid.setAttribute('data-press-preserved-category-grid', 'true');

  }

  function makeCardsClickableAgain(scope) {

    if (!scope) return;

    scope.querySelectorAll('.link-list__item, .related-card, .story-card, .archive-card, .river-item, .lead-panel').forEach((card) => {

      if (card.dataset.pressPreserveClickBound === 'true') return;

      const link = card.querySelector('a[href]');

      if (!link) return;

      card.dataset.pressPreserveClickBound = 'true';

      card.classList.add('is-clickable');

      card.setAttribute('tabindex', '0');

      card.setAttribute('role', 'link');

      card.addEventListener('click', (event) => {

        if (event.target.closest('a, button, input, textarea, select, label')) return;

        window.location.href = link.href;

      });

      card.addEventListener('keydown', (event) => {

        if (event.key === 'Enter' || event.key === ' ') {

          event.preventDefault();

          link.click();

        }

      });

    });

  }

  function bindImageFallbacksAgain(scope) {

    if (!scope) return;

    scope.querySelectorAll('img').forEach((img) => {

      if (img.dataset.pressPreserveFallbackBound === 'true') return;

      img.dataset.pressPreserveFallbackBound = 'true';

      img.addEventListener('error', () => {

        const holder = img.closest(

          '.story-card__image, .lead-panel__media, .river-item__media, .archive-card__image, figure, .card-media'

        );

        if (holder) {

          holder.classList.add('is-hidden');

        } else {

          img.style.display = 'none';

        }

      });

    });

  }

  function restoreMissingCards() {

    if (!isSectionPage()) return;

    if (!preservedCards.length) return;

    const grid = findBestCategoryGrid();

    if (!grid) return;

    isRestoring = true;

    const currentCards = Array.from(grid.querySelectorAll(CARD_SELECTOR));

    const currentKeys = new Set(

      currentCards

        .map(cardKey)

        .filter(Boolean)

    );

    const missingCards = preservedCards.filter((card) => {

      const key = cardKey(card);

      return key && !currentKeys.has(key);

    });

    if (missingCards.length) {

      const fragment = document.createDocumentFragment();

      missingCards.forEach((card) => {

        const clone = card.cloneNode(true);

        clone.setAttribute('data-press-restored-old-article', 'true');

        fragment.appendChild(clone);

      });

      grid.appendChild(fragment);

    }

    grid.setAttribute('data-press-preserved-category-grid', 'true');

    makeCardsClickableAgain(grid);

    bindImageFallbacksAgain(grid);

    window.setTimeout(() => {

      isRestoring = false;

    }, 0);

  }

  function queueRestore() {

    if (restoreQueued || isRestoring) return;

    restoreQueued = true;

    window.requestAnimationFrame(() => {

      restoreQueued = false;

      restoreMissingCards();

    });

  }

  function startObserver() {

    if (!isSectionPage()) return;

    if (observer) return;

    const grid = findBestCategoryGrid();

    if (!grid) return;

    observer = new MutationObserver(() => {

      if (!isRestoring) queueRestore();

    });

    observer.observe(grid, {

      childList: true,

      subtree: true

    });

  }

  function bootPreservationGuard() {

    if (!isSectionPage()) return;

    saveOriginalCards();

    restoreMissingCards();

    startObserver();

    window.setTimeout(restoreMissingCards, 50);

    window.setTimeout(restoreMissingCards, 300);

    window.setTimeout(restoreMissingCards, 900);

    window.setTimeout(restoreMissingCards, 1500);

    window.setTimeout(restoreMissingCards, 3000);

  }

  if (document.readyState === 'loading') {

    document.addEventListener('DOMContentLoaded', bootPreservationGuard, { once: true });

  } else {

    bootPreservationGuard();

  }

})();
(() => {
  const AUTHOR_LABEL = 'Written by Intelligent AI';
  const SEARCH_EMPTY = '<div class="search-empty"><p>Start typing to search the full edition.</p></div>';
  const SEARCH_NONE = '<div class="search-empty"><p>No stories matched that search yet.</p></div>';
  let storyIndexPromise = null;

  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-year]').forEach((node) => {
      node.textContent = new Date().getFullYear();
    });

    setupMenu();
    setupSearch();
    setupReadingProgress();
    setupLeadPanels();
    setupArchiveFilters();
    setupNewsletterForms();
    normalizeVisibleBylines(document);
    makeCardsClickable();
    bindThumbnailFallbacks(document);
    rewriteAuthorsPage();
    relabelUtilityNav();
    injectReadAloudControls();
    prettifySourceLinks(document);
    extendSectionNavigation();
    setupDarkMode();
    injectShareButtons();
    applyDailyCardHover();
    injectReadingTime();

    loadStoryIndex().then((stories) => {
      enhanceBreakingStrip(stories);
      injectEditionRadar(stories);
      pressRefreshHomepageStoryBlocks(stories);
      renderSectionPage(stories);
      renderDynamicCategoryPages(stories);
      const hasHomepageTargets =
  document.querySelector('.lead-switcher__panels') ||
  document.querySelector('.home-grid__main .cards-grid.cards-grid--three') ||
  document.querySelector('.latest-section .river');

if (!hasHomepageTargets) {
  hydrateMissingCardImages();
}
    });
  });

  function loadStoryIndex() {
  if (storyIndexPromise) return storyIndexPromise;

  const normalizePayload = (data) => {
    if (Array.isArray(data)) return normalizeStoryArray(data);
    if (data && Array.isArray(data.stories)) return normalizeStoryArray(data.stories);
    if (data && Array.isArray(data.articles)) return normalizeStoryArray(data.articles);
    if (data && Array.isArray(data.items)) return normalizeStoryArray(data.items);
    return [];
  };

  const fetchJson = (url) =>
    fetch(url, { cache: 'default' }).then((response) => {
      if (!response.ok) throw new Error(`Could not load ${url}`);
      return response.json();
    });

  storyIndexPromise = fetchJson('live-index.json')
    .catch(() => fetchJson('content-index.json'))
    .catch(() => fetchJson('search-index.json'))
    .then(normalizePayload)
    .catch(() => {
      const embedded = document.getElementById('press-search-data');

      if (embedded) {
        try {
          return normalizePayload(JSON.parse(embedded.textContent));
        } catch (_) {
          return [];
        }
      }

      return [];
    });

  return storyIndexPromise;
}

  function normalizeStoryArray(data) {
    const items = Array.isArray(data) ? data.slice() : [];
    return items.map((item) => ({
      title: item.title || '',
      section: normalizeSectionLabel(item.section || ''),
      type: item.type || 'Report',
      dek: item.dek || item.summary || '',
      summary: item.summary || item.dek || '',
      url: item.url || '#',
      published: item.published || '',
      keywords: Array.isArray(item.keywords) ? item.keywords : [],
      image: item.image || item.thumbnail || item.photo || '',
      imageAlt: item.imageAlt || item.alt || item.photoAlt || '',
      sourceLabel: item.sourceLabel || '',
      sortValue: parsePublished(item.published || ''),
    })).sort((a, b) => b.sortValue - a.sortValue);
  }

  function parsePublished(value) {
    const text = String(value || '').replace(/•/g, ' ').replace(/\ba\.m\./gi, 'AM').replace(/\bp\.m\./gi, 'PM').replace(/\bEDT\b|\bEST\b|\bUTC\b/gi, '').trim();
    const time = Date.parse(text);
    return Number.isFinite(time) ? time : 0;
  }

  function setupMenu() {
    const siteHeader = document.querySelector('[data-site-header]');
    const menuToggle = document.querySelector('[data-menu-toggle]');
    function setMenu(open) {
      if (!siteHeader || !menuToggle) return;
      siteHeader.classList.toggle('is-menu-open', open);
      menuToggle.setAttribute('aria-expanded', String(open));
      menuToggle.textContent = open ? 'Close' : 'Menu';
    }
    if (!menuToggle || !siteHeader) return;
    menuToggle.addEventListener('click', () => {
      setMenu(!siteHeader.classList.contains('is-menu-open'));
    });
    siteHeader.querySelectorAll('.utility-nav a, .section-nav a').forEach((link) => {
      link.addEventListener('click', () => setMenu(false));
    });
    window.addEventListener('resize', () => {
      if (window.innerWidth > 700) setMenu(false);
    });
  }

  function normalizeVisibleBylines(root) {
    const selectors = [
      '.article-meta span:first-child',
      '.article-meta-row span:first-child',
      '.lead-panel__meta',
      '.story-card__meta',
      '.river-item__meta',
      '.link-list__meta',
      '.archive-card__meta',
      '.search-result__meta',
      '.latest-card__meta',
      '.story-meta',
      '.generated-story .byline',
    ];

    selectors.forEach((selector) => {
      root.querySelectorAll(selector).forEach((node) => {
        const text = collapseWhitespace(node.textContent || '');
        if (!text) return;
        if (selector.endsWith('span:first-child')) {
          node.textContent = AUTHOR_LABEL;
          return;
        }
        if (/^By\b/i.test(text)) {
          node.textContent = text.replace(/^By\s+.*?(?=\s*[•·]|\s*$)/i, AUTHOR_LABEL);
        } else if (/^The Press Staff/i.test(text)) {
          node.textContent = AUTHOR_LABEL;
        }
      });
    });

    root.querySelectorAll('.author-panel').forEach((panel) => {
      panel.innerHTML = '<h2>AI newsroom</h2><p><strong>' + AUTHOR_LABEL + '</strong>. This edition does not use named human bylines. Stories are generated by Intelligent AI and reviewed before publication.</p>';
    });

    root.querySelectorAll('.figure-credit a').forEach((a) => {
      a.setAttribute('target', '_blank');
      a.setAttribute('rel', 'noopener noreferrer');
    });
  }

  function rewriteAuthorsPage() {
    if (!document.body.classList.contains('page-authors')) return;
    document.querySelectorAll('.staff-card').forEach((card) => card.remove());
  }

  function makeCardsClickable() {
    document.querySelectorAll('.link-list__item, .related-card, .story-card, .archive-card, .river-item, .lead-panel').forEach((card) => {
      const link = card.querySelector('a[href]');
      if (!link) return;
      card.classList.add('is-clickable');
      card.setAttribute('tabindex', '0');
      card.setAttribute('role', 'link');
      card.addEventListener('click', (event) => {
        if (event.target.closest('a, button, input, textarea, select, label')) return;
        window.location.href = link.href;
      });
      card.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          link.click();
        }
      });
    });
  }

  function relabelUtilityNav() {
    document.querySelectorAll('a[href="authors.html"]').forEach((link) => {
      if (/authors/i.test(link.textContent || '')) {
        link.textContent = 'AI Newsroom';
      }
    });
  }

  function injectReadAloudControls() {
    const article = document.querySelector('.article');
    const body = document.querySelector('.article-body');
    const hero = document.querySelector('.article-hero');
    if (!article || !body || !hero || !('speechSynthesis' in window)) return;
    if (document.querySelector('[data-listen-controls]')) return;

    const wrapper = document.createElement('div');
    wrapper.className = 'listen-controls';
    wrapper.setAttribute('data-listen-controls', '');
    wrapper.innerHTML = `
      <button class="listen-button" type="button" data-listen-play aria-label="Read this article aloud">🔊 Listen</button>
      <button class="listen-button listen-button--ghost" type="button" data-listen-pause aria-label="Pause reading">Pause</button>
      <button class="listen-button listen-button--ghost" type="button" data-listen-stop aria-label="Stop reading">Stop</button>
      <span class="listen-status" data-listen-status>Ready to read aloud</span>
    `;
    const meta = hero.querySelector('.article-meta');
    if (meta) meta.insertAdjacentElement('afterend', wrapper); else hero.appendChild(wrapper);

    const play = wrapper.querySelector('[data-listen-play]');
    const pause = wrapper.querySelector('[data-listen-pause]');
    const stop = wrapper.querySelector('[data-listen-stop]');
    const status = wrapper.querySelector('[data-listen-status]');

    let utterance = null;
    const getText = () => collapseWhitespace(body.innerText || body.textContent || '');

    const stopSpeech = () => {
      window.speechSynthesis.cancel();
      utterance = null;
      if (status) status.textContent = 'Stopped';
    };

    play.addEventListener('click', () => {
      const text = getText();
      if (!text) return;
      if (window.speechSynthesis.paused) {
        window.speechSynthesis.resume();
        if (status) status.textContent = 'Reading aloud';
        return;
      }
      window.speechSynthesis.cancel();
      utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1;
      utterance.pitch = 1;
      utterance.onstart = () => { if (status) status.textContent = 'Reading aloud'; };
      utterance.onend = () => { if (status) status.textContent = 'Finished reading'; utterance = null; };
      utterance.onerror = () => { if (status) status.textContent = 'Read-aloud unavailable in this browser'; utterance = null; };
      window.speechSynthesis.speak(utterance);
    });

    pause.addEventListener('click', () => {
      if (!window.speechSynthesis.speaking) return;
      if (window.speechSynthesis.paused) {
        window.speechSynthesis.resume();
        if (status) status.textContent = 'Reading aloud';
      } else {
        window.speechSynthesis.pause();
        if (status) status.textContent = 'Paused';
      }
    });

    stop.addEventListener('click', stopSpeech);
    window.addEventListener('beforeunload', stopSpeech);
  }

  function bindThumbnailFallbacks(root) {
    root.querySelectorAll('img').forEach((img) => {
      if (img.dataset.pressFallbackBound === 'true') return;
      img.dataset.pressFallbackBound = 'true';
      img.addEventListener('error', () => hideBrokenImage(img));
      if (img.complete && img.naturalWidth === 0) hideBrokenImage(img);
    });
  }

  function hideBrokenImage(img) {
    const holder = img.closest('.story-card__image, .lead-panel__media, .river-item__media, .archive-card__image, figure, .card-media');
    if (holder) holder.classList.add('is-hidden'); else img.style.display = 'none';
  }

  function setupSearch() {
    const body = document.body;
    const overlay = document.querySelector('[data-search-overlay]');
    const openButtons = document.querySelectorAll('[data-search-open], [data-open-search]');
    const closeButtons = document.querySelectorAll('[data-search-close], [data-close-search]');
    const searchInput = document.querySelector('[data-search-input]');
    const resultsBox = document.querySelector('[data-search-results]');
    let searchData = [];

    function showOverlay(show) {
      if (!overlay) return;
      if ('hidden' in overlay) overlay.hidden = !show;
      overlay.classList.toggle('is-hidden', !show);
      overlay.setAttribute('aria-hidden', String(!show));
      body.style.overflow = show ? 'hidden' : '';
    }

    function openSearch() {
      showOverlay(true);
      window.setTimeout(() => searchInput && searchInput.focus(), 30);
    }

    function closeSearch() {
      showOverlay(false);
      if (searchInput) searchInput.value = '';
      renderSearchResults([], '');
    }

    openButtons.forEach((btn) => btn.addEventListener('click', openSearch));
    closeButtons.forEach((btn) => btn.addEventListener('click', closeSearch));
    if (overlay) overlay.addEventListener('click', (event) => { if (event.target === overlay) closeSearch(); });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') closeSearch();
    });

    function renderSearchResults(results, query = '') {
      if (!resultsBox) return;
      if (!query) {
        resultsBox.innerHTML = SEARCH_EMPTY;
        return;
      }
      if (!results.length) {
        resultsBox.innerHTML = SEARCH_NONE;
        return;
      }
      resultsBox.innerHTML = results.map((item) => `
        <article class="search-result">
          <p class="eyebrow eyebrow--tiny">${escapeHtml(item.section || '')} • ${escapeHtml(item.type || '')}</p>
          <h3><a href="${escapeAttribute(item.url || '#')}">${escapeHtml(item.title || '')}</a></h3>
          <p>${escapeHtml(item.dek || item.summary || '')}</p>
          <p class="search-result__meta">${AUTHOR_LABEL} • ${escapeHtml(item.published || '')}</p>
        </article>
      `).join('');
    }

    if (!searchInput) return;
    loadStoryIndex().then((stories) => {
      searchData = stories;
      searchInput.addEventListener('input', () => {
        const query = searchInput.value.trim().toLowerCase();
        if (!query) return renderSearchResults([], '');
        const results = searchData.filter((item) => {
          const haystack = [item.title, item.section, item.type, item.dek, item.summary, ...(item.keywords || [])].join(' ').toLowerCase();
          return haystack.includes(query);
        }).slice(0, 12);
        renderSearchResults(results, query);
      });
    });
  }

  function setupReadingProgress() {
    const progressBar = document.querySelector('[data-reading-progress], [data-progress]');
    if (!progressBar) return;
    const updateProgress = () => {
      const article = document.querySelector('.article, .article-body, [data-article-body]');
      if (!article) return;
      const rect = article.getBoundingClientRect();
      const scrollTop = window.scrollY || window.pageYOffset;
      const articleTop = scrollTop + rect.top;
      const articleHeight = article.offsetHeight - window.innerHeight;
      const progress = Math.min(1, Math.max(0, (scrollTop - articleTop) / Math.max(articleHeight, 1)));
      progressBar.style.width = `${progress * 100}%`;
    };
    updateProgress();
    document.addEventListener('scroll', updateProgress, { passive: true });
    window.addEventListener('resize', updateProgress);
  }

  function setupLeadPanels() {
    const leadButtons = Array.from(document.querySelectorAll('[data-lead-button]'));
    const leadPanels = Array.from(document.querySelectorAll('[data-lead-panel]'));
    if (!leadButtons.length || !leadPanels.length) return;
    const setLead = (targetId) => {
      leadButtons.forEach((btn) => {
        const active = btn.dataset.target === targetId;
        btn.classList.toggle('is-active', active);
        btn.setAttribute('aria-pressed', String(active));
      });
      leadPanels.forEach((panel) => panel.classList.toggle('is-active', panel.id === targetId));
    };
    leadButtons.forEach((btn) => btn.addEventListener('click', () => setLead(btn.dataset.target)));

    const weightedOrder = [0, 0, 0, 1, 1, 2, 3];
    const key = new Date().toISOString().slice(0, 10).split('-').join('');
    let hash = 0;
    for (const char of key) hash = ((hash * 31) + char.charCodeAt(0)) >>> 0;
    const chosen = weightedOrder[hash % weightedOrder.length];
    const chosenButton = leadButtons[chosen];
    if (chosenButton) setLead(chosenButton.dataset.target);
  }

  function setupArchiveFilters() {
    const filterButtons = document.querySelectorAll('[data-filter]');
    const archiveCards = document.querySelectorAll('.archive-card');
    if (!filterButtons.length || !archiveCards.length) return;
    filterButtons.forEach((button) => {
      button.addEventListener('click', () => {
        const filterValue = button.dataset.filter;
        filterButtons.forEach((btn) => {
          const active = btn === button;
          btn.classList.toggle('is-active', active);
          btn.setAttribute('aria-pressed', String(active));
        });
        archiveCards.forEach((card) => {
          if (filterValue === 'All') return card.hidden = false;
          const section = normalizeSectionLabel(card.dataset.section);
          const type = card.dataset.type;
          card.hidden = !(section === filterValue || type === filterValue);
        });
      });
    });
  }

  function setupNewsletterForms() {
    document.querySelectorAll('[data-newsletter-form]').forEach((form) => {
      form.addEventListener('submit', (event) => {
        event.preventDefault();
        const status = form.querySelector('[data-newsletter-status]');
        if (status) status.textContent = 'Thanks — the signup form is wired as a prototype success state.';
        form.reset();
      });
    });
  }

  function extendSectionNavigation() {
    const extra = [
      { label: 'AI', href: 'section-ai.html' },
      { label: 'Geopolitics', href: 'section-geopolitics.html' },
      { label: 'Film', href: 'section-film.html' },
      { label: 'Pop Culture', href: 'section-pop-culture.html' },
      { label: 'Niche', href: 'section-niche.html' },
    ];
    document.querySelectorAll('.section-nav__inner').forEach((nav) => {
      extra.forEach((item) => {
        if (nav.querySelector(`a[href="${item.href}"]`)) return;
        const a = document.createElement('a');
        a.className = 'nav-link';
        a.href = item.href;
        a.textContent = item.label;
        nav.appendChild(a);
      });
    });
    document.querySelectorAll('.footer-list').forEach((list) => {
      if (!list.closest('section')?.querySelector('.footer-heading')?.textContent?.match(/Sections/i)) return;
      extra.forEach((item) => {
        if (list.querySelector(`a[href="${item.href}"]`)) return;
        const li = document.createElement('li');
        li.innerHTML = `<a href="${item.href}">${item.label}</a>`;
        list.appendChild(li);
      });
    });
  }


function enhanceBreakingStrip(stories) {
  const strip = document.querySelector('.breaking-strip');
  const itemsBox = strip?.querySelector('.breaking-strip__items');
  if (!strip || !itemsBox) return;
  const existing = Array.from(itemsBox.querySelectorAll('a')).map((a) => ({ title: collapseWhitespace(a.textContent), url: a.getAttribute('href') }));
  const extra = stories.slice(0, 12).map((story) => ({ title: story.title, url: story.url }));
  const seen = new Set();
  const merged = [...existing, ...extra].filter((item) => {
    const key = `${item.title}|${item.url}`;
    if (!item.title || seen.has(key)) return false;
    seen.add(key);
    return true;
  }).slice(0, 14);
  if (!merged.length) return;
  const markup = merged.map((item) => `<a href="${escapeAttribute(item.url)}">${escapeHtml(item.title)}</a>`).join('');
  const charBudget = merged.reduce((sum, item) => sum + Math.min(96, (item.title || '').length), 0);
  const duration = Math.max(78, Math.min(138, Math.round(charBudget / 8)));
  itemsBox.style.setProperty('--press-ticker-duration', `${duration}s`);
  itemsBox.innerHTML = `<div class="breaking-strip__track">${markup}${markup}</div>`;
}

  function injectEditionRadar(stories) {
    if (!document.body.classList.contains('page-home')) return;
    const main = document.querySelector('.home-grid__main');
    const anchor = document.querySelector('.home-grid__main .cards-grid');
    if (!main || !anchor || document.querySelector('.edition-radar')) return;

    const used = new Set(Array.from(document.querySelectorAll('.home-grid a[href]')).map((a) => a.getAttribute('href')));
    const picks = stories.filter((story) => !used.has(story.url)).slice(0, 3);
    const desks = [...new Set(stories.slice(0, 10).map((story) => story.section))];
    const updated = stories[0]?.published || 'Updated recently';

    const block = document.createElement('section');
    block.className = 'edition-radar';
    block.innerHTML = `
      <div class="section-heading-row">
        <div>
          <p class="eyebrow eyebrow--tiny">Edition Radar</p>
          <h2 class="section-heading">More from the edition</h2>
        </div>
        <a class="section-link" href="ai-edition.html">Open latest issue</a>
      </div>
      <div class="edition-radar__grid">
        <div class="edition-radar__stack">
          ${(picks.length ? picks : stories.slice(0, 3)).map((story) => `
            <article class="edition-radar__item">
              <p class="eyebrow eyebrow--tiny">${escapeHtml(story.section)} • ${escapeHtml(story.type)}</p>
              <h3><a href="${escapeAttribute(story.url)}">${escapeHtml(story.title)}</a></h3>
              <p>${escapeHtml(story.dek || story.summary || '')}</p>
            </article>
          `).join('')}
        </div>
        <aside class="edition-radar__aside">
          <div class="edition-radar__stat"><span>Updated</span><strong>${escapeHtml(updated)}</strong></div>
          <div class="edition-radar__stat"><span>Stories tracked</span><strong>${stories.length}</strong></div>
          <div class="edition-radar__stat"><span>Desks in play</span><strong>${desks.length}</strong></div>
          <div class="edition-radar__desks">${desks.slice(0, 8).map((desk) => `<span>${escapeHtml(desk)}</span>`).join('')}</div>
        </aside>
      </div>
    `;
    anchor.insertAdjacentElement('afterend', block);
    normalizeVisibleBylines(block);
    makeCardsClickable();
  }

  function renderSectionPage(stories) {
    if (!document.body.classList.contains('page-section')) return;
    const heading = document.querySelector('.section-landing h1, .page-hero h1');
    const sectionName = normalizeSectionLabel(heading?.textContent || '');
    if (!sectionName) return;

    const grid = (window.pressFindSectionArchiveGrid && window.pressFindSectionArchiveGrid()) || document.querySelector('.page-section main .cards-section .cards-grid--archive, .page-section main .cards-grid--archive, .page-section .cards-grid--archive');
    if (!grid) {
      window.pressMarkSectionArchiveReady?.();
      return;
    }

    const aliases = sectionAliases(sectionName);
    const existingCards = Array.from(grid.querySelectorAll('.story-card, .archive-card'));
    const imageMap = new Map();
    existingCards.forEach((card) => {
      const link = card.querySelector('a[href]');
      const img = card.querySelector('img');
      if (!link || !img) return;
      imageMap.set(link.getAttribute('href'), { src: img.getAttribute('src'), alt: img.getAttribute('alt') || '' });
    });

    const matches = stories.filter((story) => aliases.includes(normalizeSectionLabel(story.section)));
    if (!matches.length) return;

    const deduped = [];
    const seen = new Set();
    matches.forEach((story) => {
      if (seen.has(story.url)) return;
      seen.add(story.url);
      deduped.push(story);
    });

    grid.innerHTML = deduped.map((story) => renderSectionCard(story, imageMap.get(story.url))).join('');
    grid.dataset.pressSectionHydrated = 'true';
    window.pressMarkSectionArchiveReady?.();
    normalizeVisibleBylines(grid);
    makeCardsClickable();
    bindThumbnailFallbacks(grid);
    hydrateMissingCardImages(grid);
  }

  function renderDynamicCategoryPages(stories) {
    const main = document.querySelector('.page-home .desk-directory .desk-grid');
    if (!main) return;
    const cards = Array.from(main.querySelectorAll('.desk-card'));
    const allSections = new Map();
    stories.forEach((story) => {
      const key = normalizeSectionLabel(story.section);
      if (!allSections.has(key)) allSections.set(key, []);
      allSections.get(key).push(story);
    });
    cards.forEach((card) => {
      const heading = card.querySelector('h3 a');
      if (!heading) return;
      const section = normalizeSectionLabel(heading.textContent);
      const pool = allSections.get(sectionAliases(section)[0]) || allSections.get(section) || [];
      const link = card.querySelector('.desk-card__story');
      if (pool.length && link) {
        link.textContent = pool[0].title;
        link.href = pool[0].url;
      }
    });
  }

  function renderSectionCard(story, existingImage) {
    const image = story.image || existingImage?.src || '';
    const imageAlt = story.imageAlt || existingImage?.alt || story.title;
    const imageHtml = image ? `
      <a class="story-card__image" href="${escapeAttribute(story.url)}" data-card-image-wrap>
        <img src="${escapeAttribute(image)}" alt="${escapeAttribute(imageAlt)}" loading="lazy" decoding="async" />
      </a>` : '';
    return `
      <article class="story-card archive-card" data-section="${escapeAttribute(story.section)}" data-type="${escapeAttribute(story.type)}" data-story-url="${escapeAttribute(story.url)}">
        ${imageHtml}
        <div class="story-card__body">
          <p class="eyebrow eyebrow--compact">${escapeHtml(story.section)} • ${escapeHtml(story.type)}</p>
          <h3 class="story-card__title"><a href="${escapeAttribute(story.url)}">${escapeHtml(story.title)}</a></h3>
          <p class="story-card__dek">${escapeHtml(story.dek || story.summary || '')}</p>
          <p class="story-card__meta">${AUTHOR_LABEL} • ${escapeHtml(story.published || '')}</p>
        </div>
      </article>
    `;
  }

  async function hydrateMissingCardImages(scope = document) {
    const cards = Array.from(scope.querySelectorAll('[data-story-url]')).filter((card) => !card.querySelector('img'));
    for (const card of cards.slice(0, 18)) {
      const url = card.getAttribute('data-story-url');
      if (!url || url === '#') continue;
      try {
        const response = await fetch(url, { cache: 'force-cache' });
        if (!response.ok) continue;
        const html = await response.text();
        const doc = new DOMParser().parseFromString(html, 'text/html');
        const img = doc.querySelector('.article-hero img, .generated-story img, main img');
        if (!img) continue;
        const src = img.getAttribute('src') || '';
        const alt = collapseWhitespace(img.getAttribute('alt') || '');
        if (!src || isBadImageCandidate(src, alt)) continue;
        const wrap = document.createElement('a');
        wrap.className = 'story-card__image';
        wrap.href = url;
        wrap.setAttribute('data-card-image-wrap', '');
        wrap.innerHTML = `<img src="${escapeAttribute(src)}" alt="${escapeAttribute(alt || card.querySelector('h3 a')?.textContent || 'Story image')}" loading="lazy" decoding="async" />`;
        card.insertBefore(wrap, card.firstChild);
        bindThumbnailFallbacks(card);
      } catch (_) {}
    }
  }

  function isBadImageCandidate(src, alt) {
    const joined = `${src} ${alt}`.toLowerCase();
    return ['no image', 'placeholder', 'fallback', 'default', 'blank.svg', 'no_image_available'].some((needle) => joined.includes(needle));
  }

  function prettifySourceLinks(root) {
    root.querySelectorAll('.source-notes a, .source-list a, .article-source-notes a, .generated-story .source-notes a').forEach((a) => {
      const raw = collapseWhitespace(a.textContent || '');
      const href = a.getAttribute('href') || '';
      if (!raw || !/^https?:\/\//i.test(raw)) return;
      try {
        const url = new URL(href || raw);
        a.textContent = humanSourceLabel(url.hostname, url.pathname);
      } catch (_) {}
    });
  }

  function humanSourceLabel(hostname, pathname) {
    const host = hostname.replace(/^www\./, '').toLowerCase();
    const nice = {
      'reuters.com': 'Reuters',
      'apnews.com': 'AP News',
      'nasa.gov': 'NASA',
      'census.gov': 'U.S. Census Bureau',
      'bls.gov': 'U.S. Bureau of Labor Statistics',
      'bea.gov': 'U.S. Bureau of Economic Analysis',
      'cdc.gov': 'CDC',
      'whitehouse.gov': 'The White House',
      'commons.wikimedia.org': 'Wikimedia Commons',
      'loc.gov': 'Library of Congress',
      'worldbank.org': 'World Bank',
      'imf.org': 'IMF',
      'oecd.org': 'OECD',
      'unesco.org': 'UNESCO',
      'nato.int': 'NATO',
      'europarl.europa.eu': 'European Parliament',
      'ec.europa.eu': 'European Commission',
    };
    if (nice[host]) return nice[host];
    const parts = host.split('.');
    const brand = parts.length >= 2 ? parts[parts.length - 2] : host;
    return brand.charAt(0).toUpperCase() + brand.slice(1).replace(/-/g, ' ');
  }

  function sectionAliases(sectionName) {
    const section = normalizeSectionLabel(sectionName);
    const aliases = {
      'Politics': ['Politics'],
      'Culture': ['Culture', 'Pop Culture', 'Film'],
      'Technology': ['Technology', 'AI'],
      'Economics': ['Economics'],
      'Education': ['Education'],
      'Health': ['Health'],
      'Philosophy': ['Philosophy'],
      'Science': ['Science'],
      'World': ['World', 'Geopolitics'],
      'Opinion': ['Opinion'],
      'AI': ['AI', 'Technology'],
      'Geopolitics': ['Geopolitics', 'World'],
      'Film': ['Film', 'Culture', 'Pop Culture'],
      'Pop Culture': ['Pop Culture', 'Culture', 'Film'],
      'Niche': ['Niche'],
    };
    return aliases[section] || [section];
  }

  function normalizeSectionLabel(section) {
    return collapseWhitespace(String(section || ''));
  }

  function collapseWhitespace(value) {
    return String(value || '').replace(/\s+/g, ' ').trim();
  }

  function escapeHtml(value) {
    return String(value ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function escapeAttribute(value) {
    return escapeHtml(value).replace(/`/g, '&#96;');
  }

  /* ── Dark-mode toggle ──────────────────────────────────────────────── */
  function setupDarkMode() {
    const STORAGE_KEY = 'press-theme';
    const root = document.documentElement;

    // Restore saved preference immediately (before paint)
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved === 'dark' || saved === 'light') root.setAttribute('data-theme', saved);

    const toggle = document.querySelector('[data-theme-toggle]');
    if (!toggle) return;

    function updateIcon() {
      const isDark = root.getAttribute('data-theme') === 'dark' ||
        (!root.getAttribute('data-theme') && window.matchMedia('(prefers-color-scheme: dark)').matches);
      toggle.textContent = isDark ? '☽' : '☀︎';
      toggle.setAttribute('aria-label', isDark ? 'Switch to light mode' : 'Switch to dark mode');
    }

    toggle.addEventListener('click', () => {
      const isDark = root.getAttribute('data-theme') === 'dark' ||
        (!root.getAttribute('data-theme') && window.matchMedia('(prefers-color-scheme: dark)').matches);
      const next = isDark ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      localStorage.setItem(STORAGE_KEY, next);
      updateIcon();
    });

    updateIcon();
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', updateIcon);
  }

  /* ── Share buttons ────────────────────────────────────────────────── */
  function injectShareButtons() {
    const article = document.querySelector('.article, .article-shell');
    const body = document.querySelector('.article-body');
    if (!article || !body) return;
    if (document.querySelector('.share-row')) return;

    const title = encodeURIComponent(document.title.replace(' — The Press', '').trim());
    const url = encodeURIComponent(window.location.href);
    const tweetUrl = `https://twitter.com/intent/tweet?text=${title}&url=${url}&via=thepress`;
    const linkedInUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${url}`;

    const shareRow = document.createElement('div');
    shareRow.className = 'share-row';
    shareRow.innerHTML = `
      <span class="share-row__label">Share this story</span>
      <a class="share-btn" href="${tweetUrl}" target="_blank" rel="noopener noreferrer" aria-label="Share on X (Twitter)">
        𝕏&nbsp;Post
      </a>
      <a class="share-btn" href="${linkedInUrl}" target="_blank" rel="noopener noreferrer" aria-label="Share on LinkedIn">
        in&nbsp;LinkedIn
      </a>
      <button class="share-btn share-btn--copy" type="button" data-copy-link aria-label="Copy link to article">
        🔗&nbsp;Copy link
      </button>
      ${navigator.share ? '<button class="share-btn share-btn--native" type="button" data-native-share aria-label="Share via system menu">↗ Share</button>' : ''}
    `;
    body.insertAdjacentElement('afterend', shareRow);

    // Copy link
    const copyBtn = shareRow.querySelector('[data-copy-link]');
    if (copyBtn) {
      copyBtn.addEventListener('click', async () => {
        try {
          await navigator.clipboard.writeText(window.location.href);
          copyBtn.textContent = '✓ Copied!';
          copyBtn.classList.add('copied');
          setTimeout(() => {
            copyBtn.innerHTML = '🔗&nbsp;Copy link';
            copyBtn.classList.remove('copied');
          }, 2200);
        } catch (_) {
          copyBtn.textContent = 'Copy failed';
        }
      });
    }

    // Native share
    const nativeBtn = shareRow.querySelector('[data-native-share]');
    if (nativeBtn && navigator.share) {
      nativeBtn.addEventListener('click', () => {
        navigator.share({
          title: document.title.replace(' — The Press', '').trim(),
          text: document.querySelector('meta[name="description"]')?.content || '',
          url: window.location.href,
        }).catch(() => {});
      });
    }
  }

  /* ── Hover micro-animation for daily cards ────────────────────────── */
  function applyDailyCardHover() {
    document.querySelectorAll('.daily-card, .story-card--daily').forEach((card) => {
      const link = card.querySelector('a[href]');
      if (!link) return;
      card.style.cursor = 'pointer';
      card.addEventListener('click', (e) => {
        if (e.target.closest('a')) return;
        window.location.href = link.href;
      });
    });
  }

  /* ── Inject "min read" reading-time badge on article pages ─────────  */
  function injectReadingTime() {
    const body = document.querySelector('.article-body, [data-article-body]');
    const meta = document.querySelector('.article-meta');
    if (!body || !meta) return;
    if (meta.querySelector('[data-reading-time]')) return;
    const words = (body.textContent || '').trim().split(/\s+/).length;
    const mins = Math.max(1, Math.round(words / 230));
    const badge = document.createElement('span');
    badge.setAttribute('data-reading-time', '');
    badge.textContent = `${mins} min read`;
    meta.appendChild(badge);
  }
/* =========================
   HOMEPAGE ROTATION PATCH
   ========================= */

function pressEscapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function pressEscapeAttribute(value) {
  return pressEscapeHtml(value);
}

function pressSectionHref(sectionName) {
  const slug = String(sectionName || '')
    .toLowerCase()
    .replace(/&/g, ' and ')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');

  return slug ? `section-${slug}.html` : 'archive.html';
}

function pressNormalizeSectionLabel(value) {
  return String(value || 'front page')
    .toLowerCase()
    .replace(/&/g, ' and ')
    .replace(/[^a-z0-9]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function pressSortValue(story) {
  const direct = Number(story && story.sortValue);
  if (Number.isFinite(direct)) return direct;

  const maybeDates = [
    story && story.publishedAt,
    story && story.published,
    story && story.publishDate,
    story && story.date,
    story && story.updatedAt,
    story && story.timestamp
  ];

  for (const value of maybeDates) {
    if (!value) continue;
    const parsed = Date.parse(value);
    if (!Number.isNaN(parsed)) return parsed;
  }

  return 0;
}

function pressNormalizeStory(story) {
  if (!story) return null;

  const url = story.url || story.href || story.link || story.permalink || '';
  const title = story.title || story.headline || story.name || '';
  if (!url || !title) return null;

  const summary = story.dek || story.summary || story.description || story.excerpt || '';
  const image = story.image || story.imageUrl || story.thumbnail || story.photo || '';

  return {
    ...story,
    url,
    title,
    image,
    imageAlt: story.imageAlt || story.alt || title,
    section: story.section || story.desk || story.category || 'News',
    type: story.type || story.kind || 'Story',
    dek: summary,
    summary,
    published: story.published || story.displayDate || story.date || '',
    byline: story.byline || story.author || story.authors || '',
    sortValue: pressSortValue(story),
  };
}

function pressMetaLabel(story) {
  return story && story.byline ? story.byline : 'The Press';
}

function pressMetaLine(story) {
  const author = pressMetaLabel(story);
  const published = String((story && story.published) || '').trim();
  return published ? `${author} • ${published}` : author;
}

function pressBindThumbnailFallbacks(root = document) {
  const scope = root && root.querySelectorAll ? root : document;

  scope.querySelectorAll('img').forEach((img) => {
    if (img.dataset.pressFallbackBound === 'true') return;
    img.dataset.pressFallbackBound = 'true';

    img.addEventListener('error', () => {
      const wrapper = img.closest('.story-card__image, .river-item__thumb, .lead-panel__media');
      if (wrapper) {
        wrapper.style.display = 'none';
      } else {
        img.style.display = 'none';
      }
    });
  });
}

function pressNormalizeVisibleBylines(root = document) {
  const scope = root && root.querySelectorAll ? root : document;

  scope.querySelectorAll('.story-card__meta, .river-item__meta, .lead-panel__meta').forEach((el) => {
    const text = String(el.textContent || '').replace(/\s+/g, ' ').trim();
    if (!text || text === '•') el.remove();
  });
}

function pressHydrateMissingCardImages(root = document) {
  try {
    if (typeof hydrateMissingCardImages === 'function') {
      hydrateMissingCardImages(root);
    }
  } catch (error) {
    /* noop */
  }
}

function pressSetupLeadPanels() {
  const leadButtons = Array.from(document.querySelectorAll('[data-lead-button]'));
  const leadPanels = Array.from(document.querySelectorAll('[data-lead-panel]'));
  if (!leadButtons.length || !leadPanels.length) return;

  const setLead = (targetId) => {
    leadButtons.forEach((btn) => {
      const active = btn.dataset.target === targetId;
      btn.classList.toggle('is-active', active);
      btn.setAttribute('aria-pressed', String(active));
    });

    leadPanels.forEach((panel) => {
      panel.classList.toggle('is-active', panel.id === targetId);
    });
  };

  leadButtons.forEach((btn) => {
    if (btn.dataset.pressLeadBound === 'true') return;
    btn.dataset.pressLeadBound = 'true';
    btn.addEventListener('click', () => setLead(btn.dataset.target));
  });

  const previous = Number(sessionStorage.getItem('press-last-lead-index') ?? -1);
  let chosen = Math.floor(Math.random() * leadButtons.length);
  if (leadButtons.length > 1 && chosen === previous) {
    chosen = (chosen + 1) % leadButtons.length;
  }
  sessionStorage.setItem('press-last-lead-index', String(chosen));

  const chosenButton = leadButtons[chosen];
  if (chosenButton) setLead(chosenButton.dataset.target);
}

function pressShuffleArray(items) {
  const copy = Array.isArray(items) ? items.slice() : [];

  for (let i = copy.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }

  return copy;
}

function pressPickStorySet(source, count, used, uniqueSections = false) {
  const picked = [];
  const seenSections = new Set();
  const candidates = pressShuffleArray(Array.isArray(source) ? source : []);

  const tryTake = (story, enforceUniqueSections) => {
    if (!story || !story.url || used.has(story.url)) return false;

    const sectionKey = pressNormalizeSectionLabel(story.section);
    if (enforceUniqueSections && seenSections.has(sectionKey)) return false;

    used.add(story.url);
    seenSections.add(sectionKey);
    picked.push(story);

    return picked.length >= count;
  };

  for (const story of candidates) {
    if (tryTake(story, uniqueSections)) return picked;
  }

  for (const story of candidates) {
    if (tryTake(story, false)) return picked;
  }

  return picked;
}

function pressRenderLeadPanel(story, index) {
  const imageHtml = story.image
    ? `<img src="${pressEscapeAttribute(story.image)}" alt="${pressEscapeAttribute(story.imageAlt || story.title || '')}" loading="eager" decoding="async" />`
    : '';

  return `
    <div class="lead-panel${index === 0 ? ' is-active' : ''}" data-lead-panel id="lead-${index}">
      <div class="lead-panel__media">
        ${imageHtml}
      </div>
      <div class="lead-panel__body">
        <div>
          <p class="eyebrow">Front Page • ${pressEscapeHtml(story.section || 'News')} • ${pressEscapeHtml(story.type || 'Story')}</p>
          <h2><a href="${pressEscapeAttribute(story.url)}">${pressEscapeHtml(story.title || '')}</a></h2>
          <p class="lead-panel__dek">${pressEscapeHtml(story.dek || story.summary || '')}</p>
          <p class="lead-panel__meta">${pressEscapeHtml(pressMetaLine(story))}</p>
        </div>
        <div class="button-row">
          <a class="button" href="${pressEscapeAttribute(story.url)}">Read story</a>
          <a class="button button--ghost" href="${pressEscapeAttribute(pressSectionHref(story.section))}">More ${pressEscapeHtml(String(story.section || 'news').toLowerCase())}</a>
        </div>
      </div>
    </div>
  `;
}

function pressRenderHomepageLeadStories(stories) {
  const panelBox = document.querySelector('.lead-switcher__panels');
  const navBox = document.querySelector('.lead-nav');

  if (!panelBox || !navBox || !stories.length) return;

  panelBox.innerHTML = stories.map((story, index) => pressRenderLeadPanel(story, index)).join('');
  navBox.innerHTML = stories.map((story, index) => `
    <button class="lead-nav__button${index === 0 ? ' is-active' : ''}" type="button" data-lead-button data-target="lead-${index}" aria-pressed="${String(index === 0)}">
      <span>${pressEscapeHtml(story.section || 'Front Page')}</span>
      <strong>${pressEscapeHtml(story.title || '')}</strong>
    </button>
  `).join('');

  pressBindThumbnailFallbacks(panelBox);
  pressSetupLeadPanels();
}

function pressRenderHomeStoryCard(story) {
  const imageHtml = story.image ? `
    <a class="story-card__image" href="${pressEscapeAttribute(story.url)}">
      <img alt="${pressEscapeAttribute(story.imageAlt || story.title || '')}" decoding="async" loading="lazy" src="${pressEscapeAttribute(story.image)}" />
    </a>
  ` : '';

  return `
    <article class="story-card" data-section="${pressEscapeAttribute(story.section || '')}" data-type="${pressEscapeAttribute(story.type || '')}" data-story-url="${pressEscapeAttribute(story.url)}">
      ${imageHtml}
      <div class="story-card__body">
        <p class="eyebrow eyebrow--compact">${pressEscapeHtml(story.section || '')} • ${pressEscapeHtml(story.type || '')}</p>
        <h3 class="story-card__title"><a href="${pressEscapeAttribute(story.url)}">${pressEscapeHtml(story.title || '')}</a></h3>
        <p class="story-card__dek">${pressEscapeHtml(story.dek || story.summary || '')}</p>
        <p class="story-card__meta">${pressEscapeHtml(pressMetaLine(story))}</p>
      </div>
    </article>
  `;
}

function pressRenderHomepageSecondaryStories(stories) {
  const grid = document.querySelector('.home-grid__main .cards-grid.cards-grid--three');
  if (!grid || !stories.length) return;

  grid.innerHTML = stories.map((story) => pressRenderHomeStoryCard(story)).join('');
  pressNormalizeVisibleBylines(grid);
  pressBindThumbnailFallbacks(grid);
  pressHydrateMissingCardImages(grid);
}

function pressRenderRiverStory(story) {
  const imageHtml = story.image ? `
    <a class="river-item__thumb" href="${pressEscapeAttribute(story.url)}">
      <img alt="${pressEscapeAttribute(story.imageAlt || story.title || '')}" decoding="async" loading="lazy" src="${pressEscapeAttribute(story.image)}" />
    </a>
  ` : '';

  return `
    <article class="river-item" data-story-url="${pressEscapeAttribute(story.url)}">
      ${imageHtml}
      <div class="river-item__body">
        <p class="eyebrow eyebrow--tiny">${pressEscapeHtml(story.section || '')} • ${pressEscapeHtml(story.type || '')}</p>
        <h3><a href="${pressEscapeAttribute(story.url)}">${pressEscapeHtml(story.title || '')}</a></h3>
        <p>${pressEscapeHtml(story.dek || story.summary || '')}</p>
        <p class="river-item__meta">${pressEscapeHtml(pressMetaLine(story))}</p>
      </div>
    </article>
  `;
}

function pressRenderHomepageRiverStories(stories) {
  const river = document.querySelector('.latest-section .river');
  if (!river || !stories.length) return;

  river.innerHTML = stories.map((story) => pressRenderRiverStory(story)).join('');
  pressNormalizeVisibleBylines(river);
  pressBindThumbnailFallbacks(river);
  pressHydrateMissingCardImages(river);
}

function pressMakeCardsClickable() {
  document.querySelectorAll('.link-list__item, .related-card, .story-card, .archive-card, .river-item, .lead-panel').forEach((card) => {
    if (card.dataset.pressClickableBound === 'true') return;
    card.dataset.pressClickableBound = 'true';

    const link = card.querySelector('a[href]');
    if (!link) return;

    card.classList.add('is-clickable');
    card.setAttribute('tabindex', '0');
    card.setAttribute('role', 'link');

    card.addEventListener('click', (event) => {
      if (event.target.closest('a, button, input, textarea, select, label')) return;
      window.location.href = link.href;
    });

    card.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        link.click();
      }
    });
  });
}

function pressRefreshHomepageStoryBlocks(stories) {
  const hasHomepageTargets =
    document.querySelector('.lead-switcher__panels') ||
    document.querySelector('.home-grid__main .cards-grid.cards-grid--three') ||
    document.querySelector('.latest-section .river');

  if (!hasHomepageTargets) return;

  const pool = Array.isArray(stories)
    ? stories.map(pressNormalizeStory).filter((story) => story && story.url && story.title)
    : [];

  if (!pool.length) return;

  const recent = pool.slice().sort((a, b) => b.sortValue - a.sortValue);
  const used = new Set();

  const leadPool = recent.filter((story) => story.image);

  pressRenderHomepageLeadStories(
    pressPickStorySet(leadPool.length ? leadPool : recent, 4, used, true)
  );

  pressRenderHomepageSecondaryStories(
    pressPickStorySet(recent.filter((story) => !used.has(story.url)), 3, used, true)
  );

  pressRenderHomepageRiverStories(
    pressPickStorySet(recent.filter((story) => !used.has(story.url)), 8, used, false)
  );

  pressMakeCardsClickable();
}
})();

/* PRESS_AI_BYLINE_PATCH_START */
document.addEventListener("DOMContentLoaded", () => {
  const selectors = [
    ".byline",
    ".story-card__meta",
    ".lead-panel__meta",
    ".link-list__meta",
    ".article-meta"
  ];

  document.querySelectorAll(selectors.join(",")).forEach((el) => {
    const text = (el.textContent || "").trim();
    if (!text) return;

    if (text.startsWith("By ")) {
      el.textContent = text.replace(/^By\s+[^•]+/, "Written by Intelligent AI");
    }
  });
});
/* PRESS_AI_BYLINE_PATCH_END */
/* PRESS_ECOSYSTEM_ENGINE_START
   Drop this entire block at the very bottom of app.js.
   It turns the homepage, section pages, archive, freshness chips, desk pulse,
   catch-up cards, and reading modes into a cleaner live article ecosystem.
*/
(() => {
  'use strict';

  const PRESS_AUTHOR = 'Written by Intelligent AI';
  const CACHE_PREFIX = 'press-ecosystem-cache:';
  const MODE_KEY = 'press-reader-mode';
  const FRESH_HOURS = 72;
  const LIVE_DAYS = 14;
  const FETCH_TARGETS = {
    placements: 'placements.json',
    live: 'live-index.json',
    content: 'content-index.json',
    daily: 'daily-latest.json',
    edition: 'edition.json',
    search: 'search-index.json',
  };

  const SECTION_COPY = {
    ai: 'Model labs, compute, safety, infrastructure, and the business systems underneath artificial intelligence.',
    culture: 'Institutions, labor, audiences, and the economics under the room.',
    economics: 'Indicators translated back into rent, wages, spending, and shelter.',
    education: 'Schools, campuses, attendance, learning, and public-system capacity.',
    film: 'Festivals, studios, directors, box office, and the machinery of screen culture.',
    geopolitics: 'War, diplomacy, alliances, borders, and the logistics behind power.',
    health: 'Public health, vaccination, surveillance, and the line between fear and evidence.',
    niche: 'Internet microcultures, collector obsessions, odd markets, and the small trends that explain big moods.',
    opinion: 'Arguments anchored in public facts, not hot air.',
    philosophy: 'Essays on judgment, ethics, institutions, and the words societies use to think.',
    politics: 'Power, administration, elections, and the law of democratic procedure.',
    popculture: 'Pop music, fandom, celebrity systems, festivals, and the internet’s cultural weather.',
    science: 'Research, engineering, and the physical systems required to turn ambition into evidence.',
    technology: 'Infrastructure, industry, and the machinery behind digital life.',
    world: 'Alliances, borders, defense industry, and how geopolitical language becomes logistics.',
  };

  const SECTION_ALIAS = {
    ai: ['ai', 'artificial intelligence', 'technology'],
    artificialintelligence: ['ai', 'artificial intelligence', 'technology'],
    film: ['film', 'culture'],
    geopolitics: ['geopolitics', 'world'],
    popculture: ['pop culture', 'popculture', 'culture'],
    niche: ['niche', 'culture'],
    world: ['world', 'geopolitics'],
    technology: ['technology', 'ai'],
    culture: ['culture', 'film', 'pop culture', 'niche'],
  };

  const STOP_WORDS = new Set([
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'but', 'by', 'can', 'could', 'for', 'from', 'has', 'have', 'how', 'in', 'into', 'is',
    'it', 'its', 'new', 'not', 'now', 'of', 'on', 'or', 'over', 'that', 'the', 'their', 'this', 'to', 'with', 'without', 'why', 'will',
    'after', 'before', 'still', 'about', 'what', 'when', 'where', 'who', 'than', 'then', 'there', 'they', 'was', 'were', 'been', 'being',
  ]);

  let ecosystemState = null;
  let ecosystemPromise = null;

  function ready(callback) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', callback, { once: true });
    } else {
      callback();
    }
  }

  ready(() => {
    document.documentElement.classList.add('press-ecosystem-booting');
    installReadingModes();
    installWhyTooltips();
    installSmartSearchHook();

    loadEcosystem().then((state) => {
      ecosystemState = state;
      document.documentElement.classList.remove('press-ecosystem-booting');
      document.documentElement.classList.add('press-ecosystem-ready');

      renderEverything(state);

      // Existing app.js also refreshes some slots asynchronously.
      // These passes make this engine the final source of truth.
      window.setTimeout(() => renderEverything(state), 300);
      window.setTimeout(() => renderEverything(state), 1200);

      window.dispatchEvent(new CustomEvent('press:ecosystem-ready', { detail: state }));
    }).catch((error) => {
      document.documentElement.classList.remove('press-ecosystem-booting');
      console.warn('[The Press] Ecosystem engine could not initialize:', error);
    });
  });

  function loadEcosystem() {
    if (ecosystemPromise) return ecosystemPromise;

    ecosystemPromise = (async () => {
      const [placementsRaw, liveRaw, contentRaw] = await Promise.all([
        fetchOptionalJson(FETCH_TARGETS.placements),
        fetchOptionalJson(FETCH_TARGETS.live),
        fetchOptionalJson(FETCH_TARGETS.content),
      ]);

      let sourceStories = mergeStories([
        extractStories(contentRaw, 'content-index'),
        extractStories(liveRaw, 'live-index'),
      ]);

      if (sourceStories.length < 8) {
        const [dailyRaw, editionRaw, searchRaw, embeddedRaw] = await Promise.all([
          fetchOptionalJson(FETCH_TARGETS.daily),
          fetchOptionalJson(FETCH_TARGETS.edition),
          fetchOptionalJson(FETCH_TARGETS.search),
          Promise.resolve(readEmbeddedSearchJson()),
        ]);

        sourceStories = mergeStories([
          sourceStories,
          extractStories(dailyRaw, 'daily-latest'),
          extractStories(editionRaw, 'edition'),
          extractStories(searchRaw, 'search-index'),
          extractStories(embeddedRaw, 'embedded-search'),
        ]);
      }

      const stories = sourceStories
        .filter((story) => story.title && story.url)
        .sort((a, b) => b.sortValue - a.sortValue || a.title.localeCompare(b.title));

      const model = buildPlacementModel(stories, normalizePlacementFile(placementsRaw));

      return {
        stories,
        model,
        generatedAt: new Date().toISOString(),
      };
    })();

    return ecosystemPromise;
  }

  async function fetchOptionalJson(url) {
    try {
      const response = await fetch(url, { cache: 'default' });
      if (!response.ok) return readCachedJson(url);

      const json = await response.json();
      writeCachedJson(url, json);
      return json;
    } catch (_) {
      return readCachedJson(url);
    }
  }

  function writeCachedJson(url, data) {
    try {
      localStorage.setItem(CACHE_PREFIX + url, JSON.stringify({
        savedAt: Date.now(),
        data,
      }));
    } catch (_) {}
  }

  function readCachedJson(url) {
    try {
      const raw = localStorage.getItem(CACHE_PREFIX + url);
      if (!raw) return null;

      const parsed = JSON.parse(raw);
      return parsed && parsed.data ? parsed.data : null;
    } catch (_) {
      return null;
    }
  }

  function readEmbeddedSearchJson() {
    const node = document.getElementById('press-search-data');
    if (!node) return null;

    try {
      return JSON.parse(node.textContent || '[]');
    } catch (_) {
      return null;
    }
  }

  function extractStories(payload, sourceName) {
    if (!payload) return [];

    if (Array.isArray(payload)) {
      return payload.map((item) => normalizeStory(item, sourceName)).filter(Boolean);
    }

    if (Array.isArray(payload.stories)) {
      return payload.stories.map((item) => normalizeStory(item, sourceName)).filter(Boolean);
    }

    if (Array.isArray(payload.articles)) {
      return payload.articles.map((item) => normalizeStory(item, sourceName)).filter(Boolean);
    }

    if (Array.isArray(payload.items)) {
      return payload.items.map((item) => normalizeStory(item, sourceName)).filter(Boolean);
    }

    return [];
  }

  function normalizeStory(item, sourceName) {
    if (!item || typeof item !== 'object') return null;

    const title = clean(item.title || item.headline || item.name || '');
    const url = clean(item.url || item.href || item.link || item.filename || item.permalink || '');

    if (!title || !url || url === '#') return null;

    const section = titleCaseSection(item.section || item.desk || item.category || inferSectionFromUrl(url) || 'News');
    const type = clean(item.type || item.kind || item.story_type || (url.startsWith('daily/') ? 'Daily Issue' : 'Report'));
    const summary = clean(item.dek || item.summary || item.description || item.excerpt || '');
    const publishedLabel = clean(item.published || item.publishedLabel || item.published_label || item.displayDate || item.date || '');
    const updatedLabel = clean(item.updated || item.updatedLabel || item.updated_label || item.updatedAt || '');
    const publishedIso = clean(item.publishedIso || item.published_iso || item.publishedAt || item.published_at || '');
    const updatedIso = clean(item.updatedIso || item.updated_iso || item.updatedAt || item.updated_at || '');
    const sortValue = parsePressDate(publishedIso || publishedLabel || item.date || urlDateHint(url));
    const image = clean(item.image || item.imageUrl || item.image_url || item.thumbnail || item.photo || '');
    const imageAlt = clean(item.imageAlt || item.image_alt || item.alt || item.photoAlt || item.photo_alt || title);
    const keywords = Array.isArray(item.keywords) ? item.keywords.filter(Boolean).map(String) : [];
    const storyId = clean(item.story_id || item.storyId || item.id || slugFromUrl(url));
    const clusterId = clean(item.cluster_id || item.clusterId || makeClusterId(title, keywords, section));
    const readTime = clean(item.readTime || item.read_time || '');
    const wordCount = clean(item.wordCount || item.word_count || '');
    const author = clean(item.author || item.byline || item.authors || PRESS_AUTHOR).replace(/^By\s+/i, '');

    return {
      raw: item,
      sourceName,
      storyId,
      clusterId,
      title,
      section,
      sectionSlug: slugify(section),
      type,
      dek: summary,
      summary,
      url,
      image,
      imageAlt,
      author: author || PRESS_AUTHOR,
      byline: PRESS_AUTHOR,
      published: publishedLabel || formatDateLabel(sortValue),
      publishedIso: publishedIso || (sortValue ? new Date(sortValue).toISOString() : ''),
      updated: updatedLabel,
      updatedIso,
      sortValue,
      ageHours: sortValue ? Math.max(0, (Date.now() - sortValue) / 36e5) : 999999,
      keywords,
      readTime,
      wordCount,
      priority: Number(item.priority || item.editorial_priority || 0) || 0,
      heroEligible: item.hero_eligible !== false,
      status: clean(item.status || 'published'),
      isDaily: /daily\//i.test(url) || /daily/i.test(type),
    };
  }

  function mergeStories(groups) {
    const byUrl = new Map();
    const flat = groups.flat().filter(Boolean);

    flat.forEach((story) => {
      const key = normalizeUrlKey(story.url);
      const previous = byUrl.get(key);

      if (!previous) {
        byUrl.set(key, story);
        return;
      }

      byUrl.set(key, mergeStoryPair(previous, story));
    });

    return Array.from(byUrl.values())
      .filter((story) => !/draft|private|trash/i.test(story.status || ''));
  }

  function mergeStoryPair(a, b) {
    const newer = (b.sortValue || 0) >= (a.sortValue || 0) ? b : a;
    const older = newer === b ? a : b;

    return {
      ...older,
      ...newer,
      image: newer.image || older.image,
      imageAlt: newer.imageAlt || older.imageAlt,
      dek: longer(newer.dek, older.dek),
      summary: longer(newer.summary, older.summary),
      keywords: Array.from(new Set([...(older.keywords || []), ...(newer.keywords || [])])),
      readTime: newer.readTime || older.readTime,
      wordCount: newer.wordCount || older.wordCount,
      clusterId: newer.clusterId || older.clusterId,
      priority: Math.max(Number(older.priority || 0), Number(newer.priority || 0)),
    };
  }

  function longer(a, b) {
    return String(a || '').length >= String(b || '').length ? (a || b || '') : (b || a || '');
  }

  function buildPlacementModel(stories, placementFile) {
    const all = stories.slice().sort((a, b) => b.sortValue - a.sortValue);

    const byId = new Map();
    all.forEach((story) => {
      byId.set(story.storyId, story);
      byId.set(story.url, story);
      byId.set(normalizeUrlKey(story.url), story);
    });

    const liveCutoff = Date.now() - LIVE_DAYS * 24 * 36e5;
    const recentEnough = all.filter((story) => !story.sortValue || story.sortValue >= liveCutoff);
    const livePool = recentEnough.length >= 12 ? recentEnough : all.slice(0, Math.max(24, Math.min(all.length, 60)));
    const clusterFresh = freshestPerCluster(livePool);

    const usedClusters = new Set();
    const usedUrls = new Set();

    const resolvedHero = resolvePlacementList(placementFile?.home?.hero, byId, 4);
    const hero = resolvedHero.length
      ? resolvedHero
      : pickStories(clusterFresh.filter((story) => story.heroEligible && story.image), 4, {
          usedClusters,
          usedUrls,
          uniqueSections: true,
        })
          .concat(pickStories(clusterFresh, 4, {
            usedClusters,
            usedUrls,
            uniqueSections: true,
          }))
          .slice(0, 4);

    hero.forEach((story) => remember(story, usedClusters, usedUrls));

    const secondary = resolvePlacementList(placementFile?.home?.secondary, byId, 3);
    const secondaryFinal = secondary.length
      ? secondary
      : pickStories(clusterFresh, 3, {
          usedClusters,
          usedUrls,
          uniqueSections: true,
        });

    secondaryFinal.forEach((story) => remember(story, usedClusters, usedUrls));

    const latest = uniqueByCluster(all).slice(0, 12);
    const daily = all.filter((story) => story.isDaily).slice(0, 10);
    const railUsed = new Set([...hero, ...secondaryFinal].map((story) => story.clusterId));
    const railPool = clusterFresh.filter((story) => !railUsed.has(story.clusterId));

    const mostRead = resolvePlacementList(placementFile?.home?.most_read || placementFile?.home?.mostRead, byId, 5);
    const mostReadFinal = mostRead.length ? mostRead : scoreSort(railPool, 'mostRead').slice(0, 5);

    const pickUsed = new Set([...railUsed, ...mostReadFinal.map((story) => story.clusterId)]);
    const editorsPicks = resolvePlacementList(placementFile?.home?.editors_picks || placementFile?.home?.editorsPicks, byId, 4);
    const editorsFinal = editorsPicks.length
      ? editorsPicks
      : scoreSort(clusterFresh.filter((story) => !pickUsed.has(story.clusterId)), 'editors').slice(0, 4);

    const breaking = uniqueByCluster(all).slice(0, 14);
    const deskPulse = buildDeskPulse(livePool);

    return {
      all,
      livePool,
      hero,
      secondary: secondaryFinal,
      mostRead: mostReadFinal,
      editorsPicks: editorsFinal,
      latest,
      daily: daily.length >= 5 ? daily : latest.slice(0, 10),
      breaking,
      deskPulse,
      updatedLabel: latest[0]?.published || 'Updated recently',
      storyCount: all.length,
      liveCount: livePool.length,
    };
  }

  function normalizePlacementFile(payload) {
    if (!payload || typeof payload !== 'object') return null;
    if (payload.slots) return { home: payload.slots.home || payload.home || {} };
    if (payload.home) return payload;
    return null;
  }

  function resolvePlacementList(value, byId, limit) {
    const values = Array.isArray(value) ? value : value ? [value] : [];

    return values.map((entry) => {
      const key = typeof entry === 'string'
        ? entry
        : entry?.story_id || entry?.storyId || entry?.url || entry?.id;

      return byId.get(key) || byId.get(normalizeUrlKey(key || ''));
    }).filter(Boolean).slice(0, limit);
  }

  function freshestPerCluster(stories) {
    const map = new Map();

    stories.forEach((story) => {
      const key = story.clusterId || story.url;
      const previous = map.get(key);

      if (!previous || story.sortValue > previous.sortValue || (story.image && !previous.image)) {
        map.set(key, story);
      }
    });

    return Array.from(map.values()).sort((a, b) => b.sortValue - a.sortValue);
  }

  function uniqueByCluster(stories) {
    const seen = new Set();

    return stories.filter((story) => {
      const key = story.clusterId || story.url;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }

  function pickStories(source, count, options = {}) {
    const picked = [];
    const sectionSeen = new Set();
    const candidates = scoreSort(source, 'placement');

    for (const story of candidates) {
      if (!story || picked.length >= count) break;
      if (options.usedUrls?.has(story.url)) continue;
      if (options.usedClusters?.has(story.clusterId)) continue;

      const sectionKey = slugify(story.section);
      if (options.uniqueSections && sectionSeen.has(sectionKey)) continue;

      picked.push(story);
      sectionSeen.add(sectionKey);
      remember(story, options.usedClusters, options.usedUrls);
    }

    if (picked.length < count && options.uniqueSections) {
      picked.push(...pickStories(source, count - picked.length, {
        ...options,
        uniqueSections: false,
      }));
    }

    return uniqueByUrl(picked).slice(0, count);
  }

  function remember(story, usedClusters, usedUrls) {
    if (!story) return;
    usedClusters?.add(story.clusterId);
    usedUrls?.add(story.url);
  }

  function uniqueByUrl(stories) {
    const seen = new Set();

    return stories.filter((story) => {
      const key = normalizeUrlKey(story.url);
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }

  function scoreSort(stories, mode = 'placement') {
    return stories.slice().sort((a, b) => storyScore(b, mode) - storyScore(a, mode));
  }

  function storyScore(story, mode) {
    const recency = story.sortValue ? story.sortValue / 1e10 : 0;
    const freshBoost = story.ageHours <= FRESH_HOURS ? 24 : story.ageHours <= 168 ? 8 : 0;
    const imageBoost = story.image ? 6 : 0;
    const dailyBoost = story.isDaily ? 4 : 0;
    const priorityBoost = Number(story.priority || 0) * 20;
    const summaryBoost = story.dek && story.dek.length > 90 ? 2 : 0;
    const modeBoost = mode === 'editors' && /analysis|essay|feature/i.test(story.type) ? 6 : 0;

    return recency + freshBoost + imageBoost + dailyBoost + priorityBoost + summaryBoost + modeBoost;
  }

  function buildDeskPulse(stories) {
    const map = new Map();

    stories.forEach((story) => {
      const slug = slugify(story.section);
      const current = map.get(slug) || {
        section: story.section,
        slug,
        count: 0,
        latest: story.sortValue,
        story,
      };

      current.count += 1;

      if (story.sortValue > current.latest) {
        current.latest = story.sortValue;
        current.story = story;
      }

      map.set(slug, current);
    });

    return Array.from(map.values())
      .sort((a, b) => b.latest - a.latest || b.count - a.count)
      .slice(0, 10);
  }

  function renderEverything(state) {
    if (!state?.model?.all?.length) return;

    renderGlobalFreshness(state.model);
    renderBreakingStrip(state.model.breaking);
    renderHomepage(state.model);
    renderSectionPage(state.model.all);
    renderArchivePage(state.model.all);
    renderSearchResultsFromState(state.model.all);
    bindCardInteractions();
    bindImageFallbacks(document);
  }

  function renderGlobalFreshness(model) {
    const note = document.querySelector('.edition-note');

    if (note) {
      note.textContent = `Live edition • ${model.liveCount} active stories • ${model.deskPulse.length} desks • Latest ${model.updatedLabel}`;
    }

    const banner = document.querySelector('.ai-edition-banner .section-copy');

    if (banner) {
      banner.textContent = 'New stories now replenish the live homepage slots automatically. Older pieces move into the archive instead of haunting the front page.';
    }
  }

  function renderBreakingStrip(stories) {
    const box = document.querySelector('.breaking-strip__items');
    if (!box || !stories.length) return;

    const links = stories.slice(0, 12)
      .map((story) => `<a href="${escapeAttr(story.url)}">${escapeHtml(story.title)}</a>`)
      .join('');

    box.innerHTML = `<div class="breaking-strip__track">${links}${links}</div>`;
    box.style.setProperty('--press-ticker-duration', `${Math.max(72, Math.min(140, stories.length * 12))}s`);
  }

  function renderHomepage(model) {
    if (!document.body.classList.contains('page-home')) return;

    updateHomeIntro(model);
    renderDeskPulse(model);
    renderCatchUp(model);
    renderHero(model.hero);
    renderSecondary(model.secondary);
    renderRail('.rail--most-read .link-list', model.mostRead, {
      ranked: true,
      reason: 'Trending because it is fresh, prominent, and part of an active topic cluster.',
    });
    renderRail('.rail--editors .link-list', model.editorsPicks, {
      ranked: false,
      reason: 'Chosen as a section-diverse editor-style pick with lasting context.',
    });
    renderDailySection(model.daily);
    renderLatestRiver(model.latest);
    renderDeskDirectory(model.all);
  }

  function updateHomeIntro(model) {
    const h1 = document.querySelector('.home-hero__intro h1');

    if (h1) {
      h1.textContent = 'Live Front Page';
    }

    const copy = document.querySelector('.home-hero__intro .section-copy');

    if (copy) {
      copy.textContent = `A cleaner live edition: ${model.liveCount} active stories, ${model.deskPulse.length} desks in motion, and automatic article replenishment across the homepage.`;
    }
  }

  function renderDeskPulse(model) {
    const hero = document.querySelector('.home-hero');

    if (!hero || document.querySelector('.desk-pulse')) return;

    const pulse = document.createElement('section');
    pulse.className = 'desk-pulse';

    pulse.innerHTML = `
      <div class="desk-pulse__head">
        <p class="eyebrow eyebrow--tiny">Desk Pulse</p>
        <h2>What’s active right now</h2>
      </div>

      <div class="desk-pulse__rail">
        ${model.deskPulse.map((desk) => `
          <a class="desk-pulse__chip" href="${escapeAttr(sectionHref(desk.section))}">
            <span>${escapeHtml(desk.section)}</span>
            <strong>${desk.count}</strong>
          </a>
        `).join('')}
      </div>

      <button class="desk-pulse__catchup" type="button" data-press-catchup-toggle>Catch me up</button>
    `;

    hero.insertAdjacentElement('beforebegin', pulse);

    pulse.querySelector('[data-press-catchup-toggle]')?.addEventListener('click', () => {
      document.querySelector('.press-catchup')?.classList.toggle('is-open');
    });
  }

  function renderCatchUp(model) {
    const hero = document.querySelector('.home-hero');

    if (!hero || document.querySelector('.press-catchup')) return;

    const panel = document.createElement('section');
    panel.className = 'press-catchup';

    panel.innerHTML = `
      <div class="section-heading-row">
        <div>
          <p class="eyebrow eyebrow--tiny">Catch Me Up</p>
          <h2 class="section-heading">Five stories to understand the edition</h2>
        </div>
        <a class="section-link" href="archive.html">Full archive</a>
      </div>

      <div class="press-catchup__grid">
        ${model.latest.slice(0, 5).map((story, index) => `
          <article class="press-catchup__item">
            <span>${index + 1}</span>
            <div>
              <p class="eyebrow eyebrow--tiny">${escapeHtml(story.section)} • ${freshnessLabel(story)}</p>
              <h3><a href="${escapeAttr(story.url)}">${escapeHtml(story.title)}</a></h3>
              <p>${escapeHtml(shorten(story.dek || story.summary, 145))}</p>
            </div>
          </article>
        `).join('')}
      </div>
    `;

    hero.insertAdjacentElement('beforebegin', panel);
  }

  function renderHero(stories) {
    const panelBox = document.querySelector('.lead-switcher__panels');
    const navBox = document.querySelector('.lead-nav');

    if (!panelBox || !navBox || !stories?.length) return;

    panelBox.innerHTML = stories.map((story, index) => leadPanel(story, index)).join('');

    navBox.innerHTML = stories.map((story, index) => `
      <button aria-pressed="${index === 0}" class="lead-nav__button${index === 0 ? ' is-active' : ''}" data-lead-button data-target="lead-${index}" type="button">
        <span>${escapeHtml(story.section)}</span>
        <strong>${escapeHtml(story.title)}</strong>
      </button>
    `).join('');

    bindLeadSwitcher(navBox, panelBox);
  }

  function leadPanel(story, index) {
    const imageHtml = story.image
      ? `<img alt="${escapeAttr(story.imageAlt || story.title)}" decoding="async" loading="${index === 0 ? 'eager' : 'lazy'}" src="${escapeAttr(story.image)}" />`
      : `<div class="press-image-fallback"><span>${escapeHtml(story.section)}</span></div>`;

    return `
      <div class="lead-panel${index === 0 ? ' is-active' : ''}" data-lead-panel id="lead-${index}">
        <div class="lead-panel__media">
          ${imageHtml}
          <div class="lead-panel__media-note">
            <p class="eyebrow eyebrow--tiny">${escapeHtml(freshnessLabel(story))}</p>
            <p class="lead-panel__media-copy">${escapeHtml(shorten(story.dek || story.summary, 150))}</p>
            <p class="lead-panel__media-source">Live slot • Replenishes automatically</p>
          </div>
        </div>

        <div class="lead-panel__body">
          <div>
            <p class="eyebrow">Front Page • ${escapeHtml(story.section)} • ${escapeHtml(story.type)}</p>
            <h2><a href="${escapeAttr(story.url)}">${escapeHtml(story.title)}</a></h2>
            <p class="lead-panel__dek">${escapeHtml(story.dek || story.summary)}</p>
            <p class="lead-panel__meta">${escapeHtml(metaLine(story))}</p>
            ${whyDetail('Hero slot', story, 'Selected for freshness, image readiness, and section variety.')}
          </div>

          <div class="button-row">
            <a class="button" href="${escapeAttr(story.url)}">Read story</a>
            <a class="button button--ghost" href="${escapeAttr(sectionHref(story.section))}">More ${escapeHtml(story.section.toLowerCase())}</a>
          </div>
        </div>
      </div>
    `;
  }

  function bindLeadSwitcher(navBox, panelBox) {
    navBox.querySelectorAll('[data-lead-button]').forEach((button) => {
      button.addEventListener('click', () => {
        const target = button.dataset.target;

        navBox.querySelectorAll('[data-lead-button]').forEach((btn) => {
          const active = btn === button;
          btn.classList.toggle('is-active', active);
          btn.setAttribute('aria-pressed', String(active));
        });

        panelBox.querySelectorAll('[data-lead-panel]').forEach((panel) => {
          panel.classList.toggle('is-active', panel.id === target);
        });
      });
    });
  }

  function renderSecondary(stories) {
    const grid = document.querySelector('.home-grid__main .cards-grid.cards-grid--three');

    if (!grid || !stories?.length) return;

    grid.innerHTML = stories.map((story) => storyCard(story, {
      reason: 'Fresh section-diverse secondary story.',
    })).join('');
  }

  function renderRail(selector, stories, options = {}) {
    const list = document.querySelector(selector);

    if (!list || !stories?.length) return;

    list.innerHTML = stories.map((story, index) => `
      <li class="link-list__item" data-story-url="${escapeAttr(story.url)}">
        ${options.ranked ? `<span class="rank-number">${index + 1}</span>` : ''}
        <div>
          <p class="eyebrow eyebrow--tiny">${escapeHtml(story.section)} • ${escapeHtml(story.type)}</p>
          <a href="${escapeAttr(story.url)}">${escapeHtml(story.title)}</a>
          <p class="link-list__meta">${escapeHtml(metaLine(story))}</p>
          ${whyDetail(options.ranked ? `Rank ${index + 1}` : 'Editor pick', story, options.reason)}
        </div>
      </li>
    `).join('');
  }

  function renderDailySection(stories) {
    const section = document.querySelector('.daily-home-section');

    if (!section || !stories?.length) return;

    const heading = section.querySelector('.section-heading');

    if (heading) {
      heading.textContent = `${stories.length} newest live stories`;
    }

    const standfirst = section.querySelector('.section-standfirst');

    if (standfirst) {
      standfirst.textContent = 'This row is now replenished by the article ecosystem. Old daily stories age into archive instead of staying pinned.';
    }

    const grid = section.querySelector('.cards-grid--daily, .cards-grid');

    if (grid) {
      grid.innerHTML = stories.map((story) => storyCard(story, {
        daily: true,
        reason: 'Part of the newest generated daily batch.',
      })).join('');
    }
  }

  function renderLatestRiver(stories) {
    const river = document.querySelector('.latest-section .river');

    if (!river || !stories?.length) return;

    river.innerHTML = stories.slice(0, 8).map((story) => `
      <article class="river-item" data-story-url="${escapeAttr(story.url)}">
        ${story.image ? `<a class="river-item__thumb" href="${escapeAttr(story.url)}"><img alt="${escapeAttr(story.imageAlt || story.title)}" decoding="async" loading="lazy" src="${escapeAttr(story.image)}" /></a>` : ''}

        <div class="river-item__body">
          <p class="eyebrow eyebrow--tiny">${escapeHtml(story.section)} • ${escapeHtml(story.type)} <span class="freshness-chip">${escapeHtml(freshnessLabel(story))}</span></p>
          <h3><a href="${escapeAttr(story.url)}">${escapeHtml(story.title)}</a></h3>
          <p>${escapeHtml(shorten(story.dek || story.summary, 180))}</p>
          <p class="river-item__meta">${escapeHtml(metaLine(story))}</p>
        </div>
      </article>
    `).join('');
  }

  function renderDeskDirectory(stories) {
    const cards = document.querySelectorAll('.page-home .desk-card');

    if (!cards.length) return;

    const bySection = new Map();

    stories.forEach((story) => {
      const slug = slugify(story.section);
      if (!bySection.has(slug)) bySection.set(slug, story);
    });

    cards.forEach((card) => {
      const heading = card.querySelector('h3 a');
      const link = card.querySelector('.desk-card__story');

      if (!heading || !link) return;

      const slug = slugify(heading.textContent || '');
      const story = bySection.get(slug) || findBySectionAlias(stories, slug);

      if (!story) return;

      link.textContent = story.title;
      link.href = story.url;
    });
  }

  function renderSectionPage(stories) {
    if (!document.body.classList.contains('page-section')) return;

    const sectionSlug = currentSectionSlug();

    if (!sectionSlug) return;

    const matches = stories.filter((story) => sectionMatches(story.section, sectionSlug));

    if (!matches.length) return;

    const h1 = document.querySelector('.section-landing h1, .page-hero h1');

    if (h1) {
      h1.textContent = titleForSlug(sectionSlug);
    }

    const copy = document.querySelector('.section-landing .section-copy, .page-hero .section-copy');

    if (copy) {
      copy.textContent = SECTION_COPY[sectionSlug] || `The latest ${titleForSlug(sectionSlug).toLowerCase()} stories from The Press.`;
    }

    const grid = (window.pressFindSectionArchiveGrid && window.pressFindSectionArchiveGrid()) || document.querySelector('.page-section main .cards-section .cards-grid--archive, .page-section main .cards-grid--archive, .page-section .cards-grid--archive');

    if (!grid) {
      window.pressMarkSectionArchiveReady?.();
      return;
    }

    grid.innerHTML = uniqueByCluster(matches)
      .slice(0, 36)
      .map((story) => storyCard(story, {
        archive: true,
        reason: `Newest ${titleForSlug(sectionSlug)} story.`,
      }))
      .join('');
    grid.dataset.pressSectionHydrated = 'true';
    window.pressMarkSectionArchiveReady?.();
  }

  function renderArchivePage(stories) {
    if (!document.body.classList.contains('page-archive')) return;

    const grid = document.querySelector('.page-archive .cards-grid--archive, .page-archive .cards-grid');

    if (!grid) return;

    grid.innerHTML = stories.map((story) => storyCard(story, {
      archive: true,
      reason: 'Archive card sorted by publication date.',
    })).join('');

    const toolbar = document.querySelector('.filter-toolbar');

    if (toolbar && !toolbar.dataset.pressEcosystemBound) {
      toolbar.dataset.pressEcosystemBound = 'true';

      toolbar.addEventListener('click', (event) => {
        const button = event.target.closest('[data-filter]');
        if (!button) return;

        const value = button.dataset.filter || 'All';

        toolbar.querySelectorAll('[data-filter]').forEach((btn) => {
          btn.classList.toggle('is-active', btn === button);
        });

        grid.querySelectorAll('[data-section]').forEach((card) => {
          const show = value === 'All' || card.dataset.section === value || card.dataset.type === value;
          card.hidden = !show;
        });
      });
    }
  }

  function storyCard(story, options = {}) {
    const imageHtml = story.image ? `
      <a class="story-card__image" href="${escapeAttr(story.url)}">
        <img alt="${escapeAttr(story.imageAlt || story.title)}" decoding="async" loading="lazy" src="${escapeAttr(story.image)}" />
      </a>
    ` : '';

    const classes = ['story-card'];

    if (options.archive) classes.push('archive-card');
    if (options.daily) classes.push('story-card--daily');

    return `
      <article class="${classes.join(' ')}" data-section="${escapeAttr(story.section)}" data-type="${escapeAttr(story.type)}" data-story-url="${escapeAttr(story.url)}">
        ${imageHtml}

        <div class="story-card__body">
          <p class="eyebrow eyebrow--compact">${escapeHtml(story.section)} • ${escapeHtml(story.type)} <span class="freshness-chip">${escapeHtml(freshnessLabel(story))}</span></p>
          <h3 class="story-card__title"><a href="${escapeAttr(story.url)}">${escapeHtml(story.title)}</a></h3>
          <p class="story-card__dek">${escapeHtml(shorten(story.dek || story.summary, 170))}</p>
          <p class="story-card__meta">${escapeHtml(metaLine(story))}</p>
          ${whyDetail('Placement', story, options.reason || 'Selected by the live article ecosystem.')}
          ${options.daily ? `<a class="story-card__cta" href="${escapeAttr(story.url)}">Read story</a>` : ''}
        </div>
      </article>
    `;
  }

  function whyDetail(label, story, reason) {
    return `
      <details class="press-why">
        <summary>${escapeHtml(label)} info</summary>
        <p>${escapeHtml(reason)} ${escapeHtml(freshnessLabel(story))}. Cluster: ${escapeHtml(story.clusterId || 'single story')}.</p>
      </details>
    `;
  }

  function installReadingModes() {
    applyStoredMode();

    const topbar = document.querySelector('.topbar__actions');

    if (!topbar || document.querySelector('[data-reader-mode-toggle]')) return;

    const button = document.createElement('button');
    button.className = 'reader-mode-toggle';
    button.type = 'button';
    button.setAttribute('data-reader-mode-toggle', '');
    button.textContent = modeButtonLabel(currentMode());

    button.addEventListener('click', () => {
      const next = nextMode(currentMode());
      setMode(next);
      button.textContent = modeButtonLabel(next);
    });

    topbar.insertBefore(button, topbar.firstChild);
  }

  function currentMode() {
    try {
      return localStorage.getItem(MODE_KEY) || 'standard';
    } catch (_) {
      return 'standard';
    }
  }

  function setMode(mode) {
    try {
      localStorage.setItem(MODE_KEY, mode);
    } catch (_) {}

    document.documentElement.dataset.readerMode = mode;
  }

  function applyStoredMode() {
    setMode(currentMode());
  }

  function nextMode(mode) {
    return mode === 'standard' ? 'quiet' : mode === 'quiet' ? 'edition' : 'standard';
  }

  function modeButtonLabel(mode) {
    return mode === 'quiet'
      ? 'Edition mode'
      : mode === 'edition'
        ? 'Standard mode'
        : 'Quiet mode';
  }

  function installWhyTooltips() {
    document.addEventListener('toggle', (event) => {
      const target = event.target;

      if (!target?.matches?.('.press-why') || !target.open) return;

      document.querySelectorAll('.press-why[open]').forEach((detail) => {
        if (detail !== target) detail.removeAttribute('open');
      });
    }, true);
  }

  function installSmartSearchHook() {
    document.addEventListener('input', (event) => {
      if (!event.target.matches('[data-search-input]')) return;
      if (!ecosystemState?.model?.all?.length) return;

      renderSearchResultsFromState(ecosystemState.model.all, event.target.value || '');
    }, true);
  }

  function renderSearchResultsFromState(stories, queryOverride) {
    const input = document.querySelector('[data-search-input]');
    const box = document.querySelector('[data-search-results]');

    if (!input || !box) return;

    const query = typeof queryOverride === 'string'
      ? queryOverride.trim().toLowerCase()
      : input.value.trim().toLowerCase();

    if (!query) return;

    const results = stories.filter((story) => {
      const haystack = [
        story.title,
        story.section,
        story.type,
        story.dek,
        story.summary,
        ...(story.keywords || []),
      ].join(' ').toLowerCase();

      return haystack.includes(query);
    }).slice(0, 12);

    if (!results.length) {
      box.innerHTML = '<div class="search-empty"><p>No stories matched that search yet.</p></div>';
      return;
    }

    box.innerHTML = results.map((story) => `
      <article class="search-result">
        <p class="eyebrow eyebrow--tiny">${escapeHtml(story.section)} • ${escapeHtml(story.type)} • ${escapeHtml(freshnessLabel(story))}</p>
        <h3><a href="${escapeAttr(story.url)}">${escapeHtml(story.title)}</a></h3>
        <p>${escapeHtml(shorten(story.dek || story.summary, 180))}</p>
        <p class="search-result__meta">${escapeHtml(metaLine(story))}</p>
      </article>
    `).join('');
  }

  function bindCardInteractions() {
    document.querySelectorAll('.story-card, .archive-card, .river-item, .link-list__item, .lead-panel, .press-catchup__item').forEach((card) => {
      if (card.dataset.ecosystemClickable === 'true') return;

      const link = card.querySelector('a[href]');
      if (!link) return;

      card.dataset.ecosystemClickable = 'true';
      card.classList.add('is-clickable');

      card.addEventListener('click', (event) => {
        if (event.target.closest('a, button, summary, details, input, textarea, select, label')) return;
        window.location.href = link.href;
      });
    });
  }

  function bindImageFallbacks(root = document) {
    root.querySelectorAll('img').forEach((img) => {
      if (img.dataset.ecosystemFallbackBound === 'true') return;

      img.dataset.ecosystemFallbackBound = 'true';

      img.addEventListener('error', () => {
        const holder = img.closest('.story-card__image, .lead-panel__media, .river-item__thumb');

        if (holder) {
          holder.classList.add('is-hidden');
        } else {
          img.hidden = true;
        }
      });
    });
  }

  function sectionMatches(sectionName, wantedSlug) {
    const storySlug = slugify(sectionName);

    if (storySlug === wantedSlug) return true;

    const aliases = SECTION_ALIAS[wantedSlug] || [wantedSlug];

    return aliases.map(slugify).includes(storySlug);
  }

  function findBySectionAlias(stories, slug) {
    return stories.find((story) => sectionMatches(story.section, slug));
  }

  function currentSectionSlug() {
    const file = location.pathname.split('/').pop() || '';
    const match = file.match(/^section-(.+)\.html$/i);

    if (match) return slugify(match[1]);

    const heading = document.querySelector('.section-landing h1, .page-hero h1');

    return heading ? slugify(heading.textContent || '') : '';
  }

  function titleForSlug(slug) {
    const nice = {
      ai: 'AI',
      popculture: 'Pop Culture',
    };

    return nice[slug] || slug.replace(/-/g, ' ').replace(/\b\w/g, (m) => m.toUpperCase());
  }

  function titleCaseSection(value) {
    const text = clean(value).replace(/[-_]+/g, ' ');
    const key = slugify(text);

    if (key === 'ai') return 'AI';
    if (key === 'popculture') return 'Pop Culture';

    return text.replace(/\b\w/g, (m) => m.toUpperCase());
  }

  function sectionHref(sectionName) {
    const slug = slugify(sectionName);

    if (!slug) return 'archive.html';
    if (slug === 'popculture') return 'section-pop-culture.html';

    return `section-${slug}.html`;
  }

  function metaLine(story) {
    const parts = [PRESS_AUTHOR];

    if (story.published) parts.push(story.published);

    if (story.readTime) {
      parts.push(story.readTime);
    } else if (story.wordCount) {
      parts.push(story.wordCount);
    }

    return parts.join(' • ');
  }

  function freshnessLabel(story) {
    if (!story?.sortValue) return 'Archive';

    const hours = Math.max(0, (Date.now() - story.sortValue) / 36e5);

    if (hours < 1) return 'Just now';
    if (hours < 24) return `${Math.floor(hours)}h ago`;
    if (hours < 48) return 'Yesterday';
    if (hours <= FRESH_HOURS) return `${Math.floor(hours / 24)}d ago`;
    if (hours < 168) return 'This week';

    return 'Archive';
  }

  function formatDateLabel(timestamp) {
    if (!timestamp) return '';

    try {
      return new Intl.DateTimeFormat('en-US', {
        month: 'long',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
      }).format(new Date(timestamp));
    } catch (_) {
      return '';
    }
  }

  function parsePressDate(value) {
    const raw = clean(value);

    if (!raw) return 0;

    let text = raw
      .replace(/•/g, ' ')
      .replace(/\ba\.m\./gi, 'AM')
      .replace(/\bp\.m\./gi, 'PM')
      .replace(/\bEDT\b|\bEST\b|\bUTC\b/gi, '')
      .replace(/\s+/g, ' ')
      .trim();

    let parsed = Date.parse(text);

    if (Number.isFinite(parsed)) return parsed;

    parsed = Date.parse(text.replace(/(\d{4})-(\d{2})-(\d{2}).*/, '$1-$2-$3T12:00:00'));

    return Number.isFinite(parsed) ? parsed : 0;
  }

  function urlDateHint(url) {
    const match = String(url || '').match(/(20\d{2})[-/](\d{2})[-/](\d{2})/);

    return match ? `${match[1]}-${match[2]}-${match[3]}T12:00:00` : '';
  }

  function inferSectionFromUrl(url) {
    const file = String(url || '').split('/').pop() || '';
    const first = file.split('-')[0];

    return first && !/^20\d{2}$/.test(first) ? first : '';
  }

  function makeClusterId(title, keywords = [], section = '') {
    const words = `${title} ${keywords.slice(0, 5).join(' ')}`
      .toLowerCase()
      .normalize('NFKD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-z0-9\s]/g, ' ')
      .split(/\s+/)
      .filter((word) => word.length > 2 && !STOP_WORDS.has(word));

    const core = Array.from(new Set(words)).slice(0, 6).join('-');

    return `${slugify(section)}-${core || slugify(title).slice(0, 48)}`;
  }

  function slugFromUrl(url) {
    const last = String(url || '').split('/').pop() || '';

    return last.replace(/\.html?$/i, '') || slugify(url);
  }

  function slugify(value) {
    return clean(value)
      .toLowerCase()
      .normalize('NFKD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/&/g, ' and ')
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '')
      .replace(/^pop-culture$/, 'popculture');
  }

  function normalizeUrlKey(url) {
    return clean(url)
      .replace(/^https?:\/\/[^/]+\//i, '')
      .replace(/^\.\//, '')
      .replace(/\?.*$/, '')
      .replace(/#.*$/, '');
  }

  function shorten(value, max = 160) {
    const text = clean(value);

    if (text.length <= max) return text;

    const clipped = text.slice(0, max - 1);
    const lastSpace = clipped.lastIndexOf(' ');

    return `${clipped.slice(0, lastSpace > 80 ? lastSpace : clipped.length)}…`;
  }

  function clean(value) {
    return String(value ?? '').replace(/\s+/g, ' ').trim();
  }

  function escapeHtml(value) {
    return clean(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function escapeAttr(value) {
    return escapeHtml(value);
  }
})();
/* PRESS_ECOSYSTEM_ENGINE_END */
(() => {

  'use strict';

  const AUTHOR_LABEL = 'Written by Intelligent AI';

  const SECTION_ALIASES = {

    ai: ['ai', 'artificialintelligence', 'technology'],

    artificialintelligence: ['ai', 'artificialintelligence', 'technology'],

    technology: ['technology', 'ai', 'artificialintelligence'],

    culture: ['culture', 'film', 'popculture', 'pop-culture', 'niche'],

    film: ['film', 'culture'],

    popculture: ['popculture', 'pop-culture', 'culture'],

    'pop-culture': ['popculture', 'pop-culture', 'culture'],

    niche: ['niche', 'culture'],

    world: ['world', 'geopolitics'],

    geopolitics: ['geopolitics', 'world'],

    politics: ['politics'],

    economics: ['economics'],

    education: ['education'],

    health: ['health'],

    philosophy: ['philosophy'],

    science: ['science'],

    opinion: ['opinion']

  };

  function ready(fn) {

    if (document.readyState === 'loading') {

      document.addEventListener('DOMContentLoaded', fn, { once: true });

    } else {

      fn();

    }

  }

  function slugify(value) {

    return String(value || '')

      .toLowerCase()

      .replace(/&/g, 'and')

      .replace(/[^a-z0-9]+/g, '-')

      .replace(/^-+|-+$/g, '');

  }

  function compactSlug(value) {

    return slugify(value).replace(/-/g, '');

  }

  function escapeHtml(value) {

    return String(value || '')

      .replace(/&/g, '&amp;')

      .replace(/</g, '&lt;')

      .replace(/>/g, '&gt;')

      .replace(/"/g, '&quot;')

      .replace(/'/g, '&#039;');

  }

  function storyUrl(story) {

    return String(story.url || story.href || story.link || story.filename || '#').trim();

  }

  function normalizeStory(story) {

    if (!story) return null;

    const title = story.title || story.headline || story.name || '';

    const url = storyUrl(story);

    if (!title || !url || url === '#') return null;

    const section =

      story.section ||

      story.section_name ||

      story.desk ||

      story.category ||

      story.section_slug ||

      'News';

    const image =

      story.image ||

      story.imageUrl ||

      story.thumbnail ||

      story.photo ||

      '';

    const imageAlt =

      story.imageAlt ||

      story.image_alt ||

      story.alt ||

      title;

    const published =

      story.published ||

      story.publishedLabel ||

      story.displayDate ||

      story.date ||

      story.published_iso ||

      '';

    const sortValue = Date.parse(

      story.published_iso ||

      story.publishedIso ||

      story.updated_iso ||

      story.updatedIso ||

      published ||

      ''

    );

    return {

      title,

      url,

      section,

      sectionSlug: story.section_slug || story.sectionSlug || slugify(section),

      type: story.type || story.kind || 'Story',

      dek: story.dek || story.summary || story.description || story.excerpt || '',

      image,

      imageAlt,

      published,

      readTime: story.read_time || story.readTime || '',

      isDaily: Boolean(story.is_daily || story.isDaily || url.startsWith('daily/')),

      sortValue: Number.isFinite(sortValue) ? sortValue : 0

    };

  }

  function getCurrentSectionSlug() {

    const fromUrl = location.pathname.match(/section-([a-z0-9-]+)\.html/i);

    if (fromUrl && fromUrl[1]) return slugify(fromUrl[1]);

    const heading = document.querySelector('.section-landing h1, .page-hero h1, h1');

    if (heading) return slugify(heading.textContent);

    return '';

  }

  function sectionMatches(story, pageSlug) {

    const pageCompact = compactSlug(pageSlug);

    const storySlug = slugify(story.sectionSlug || story.section);

    const storyCompact = compactSlug(storySlug);

    if (storyCompact === pageCompact) return true;

    const aliases = SECTION_ALIASES[pageSlug] || SECTION_ALIASES[pageCompact] || [];

    const compactAliases = aliases.map(compactSlug);

    return compactAliases.includes(storyCompact);

  }

  function getEmbeddedSearchStories() {

    const node = document.getElementById('press-search-data');

    if (!node) return [];

    try {

      const parsed = JSON.parse(node.textContent || '[]');

      return Array.isArray(parsed) ? parsed : [];

    } catch (_) {

      return [];

    }

  }

  async function fetchJson(url) {

    const cacheBuster = `${url}${url.includes('?') ? '&' : '?'}restore=${Date.now()}`;

    const response = await fetch(cacheBuster, { cache: 'no-store' });

    if (!response.ok) {

      throw new Error(`Could not load ${url}`);

    }

    return response.json();

  }

  async function loadAllKnownStories() {

    const buckets = [];

    buckets.push(getEmbeddedSearchStories());

    const files = [

      'content-index.json',

      'search-index.json',

      'live-index.json',

      'archive-index.json',

      'daily-latest.json'

    ];

    for (const file of files) {

      try {

        const data = await fetchJson(file);

        if (Array.isArray(data)) {

          buckets.push(data);

        } else if (data && Array.isArray(data.stories)) {

          buckets.push(data.stories);

        } else if (data && Array.isArray(data.articles)) {

          buckets.push(data.articles);

        } else if (data && Array.isArray(data.items)) {

          buckets.push(data.items);

        }

      } catch (_) {

        /* Keep going. Some pages may not have every file available. */

      }

    }

    const seen = new Set();

    const stories = [];

    buckets

      .flat()

      .map(normalizeStory)

      .filter(Boolean)

      .forEach((story) => {

        const key = story.url.replace(/^\/+/, '').toLowerCase();

        if (seen.has(key)) return;

        seen.add(key);

        stories.push(story);

      });

    return stories.sort((a, b) => b.sortValue - a.sortValue);

  }

  function findOrCreateArchiveGrid() {

    let grid = document.querySelector('main .cards-section .cards-grid--archive');

    if (grid) return grid;

    let main = document.querySelector('main.page') || document.querySelector('main');

    if (!main) {

      main = document.createElement('main');

      main.className = 'page';

      document.body.insertBefore(main, document.querySelector('.site-footer') || null);

    }

    let section = main.querySelector('.cards-section');

    if (!section) {

      section = document.createElement('section');

      section.className = 'cards-section';

      main.appendChild(section);

    }

    grid = document.createElement('div');

    grid.className = 'cards-grid cards-grid--archive';

    section.appendChild(grid);

    return grid;

  }

  function urlsAlreadyShownInDailyFeed() {

    const urls = new Set();

    document.querySelectorAll('.daily-section-feed a[href], .daily-home-section a[href]').forEach((link) => {

      const href = link.getAttribute('href');

      if (href) urls.add(href.replace(/^\/+/, '').toLowerCase());

    });

    return urls;

  }

  function renderCard(story) {

    const imageHtml = story.image

      ? `

        <a class="story-card__image" href="${escapeHtml(story.url)}">

          <img

            alt="${escapeHtml(story.imageAlt || story.title)}"

            decoding="async"

            loading="lazy"

            src="${escapeHtml(story.image)}"

          />

        </a>`

      : '';

    const metaParts = [AUTHOR_LABEL];

    if (story.published) metaParts.push(story.published);

    if (story.readTime) metaParts.push(story.readTime);

    return `

      <article

        class="story-card archive-card"

        data-section="${escapeHtml(story.section)}"

        data-type="${escapeHtml(story.type)}"

        data-story-url="${escapeHtml(story.url)}"

      >

        ${imageHtml}

        <div class="story-card__body">

          <p class="eyebrow eyebrow--compact">${escapeHtml(story.section)} • ${escapeHtml(story.type)}</p>

          <h3 class="story-card__title">

            <a href="${escapeHtml(story.url)}">${escapeHtml(story.title)}</a>

          </h3>

          ${story.dek ? `<p class="story-card__dek">${escapeHtml(story.dek)}</p>` : ''}

          <p class="story-card__meta">${escapeHtml(metaParts.join(' • '))}</p>

        </div>

      </article>

    `;

  }

  function makeCardsClickable(scope) {

    scope.querySelectorAll('.story-card, .archive-card').forEach((card) => {

      if (card.dataset.restoreClickBound === 'true') return;

      const link = card.querySelector('a[href]');

      if (!link) return;

      card.dataset.restoreClickBound = 'true';

      card.classList.add('is-clickable');

      card.setAttribute('tabindex', '0');

      card.setAttribute('role', 'link');

      card.addEventListener('click', (event) => {

        if (event.target.closest('a, button, input, textarea, select, label')) return;

        window.location.href = link.href;

      });

      card.addEventListener('keydown', (event) => {

        if (event.key === 'Enter' || event.key === ' ') {

          event.preventDefault();

          link.click();

        }

      });

    });

  }

  function clearOldAppCaches() {

    try {

      Object.keys(localStorage)

        .filter((key) => key.startsWith('press-ecosystem-cache:'))

        .forEach((key) => localStorage.removeItem(key));

    } catch (_) {

      /* localStorage may be blocked. Ignore safely. */

    }

  }

  async function restoreCategoryArticles() {

    if (!document.body.classList.contains('page-section')) return;

    const pageSlug = getCurrentSectionSlug();

    if (!pageSlug) return;

    clearOldAppCaches();

    const allStories = await loadAllKnownStories();

    const dailyUrls = urlsAlreadyShownInDailyFeed();

    let sectionStories = allStories.filter((story) => sectionMatches(story, pageSlug));

    sectionStories = sectionStories.filter((story) => {

      const cleanUrl = story.url.replace(/^\/+/, '').toLowerCase();

      return !dailyUrls.has(cleanUrl);

    });

    if (!sectionStories.length) {

      sectionStories = allStories.filter((story) => sectionMatches(story, pageSlug));

    }

    if (!sectionStories.length) return;

    const grid = findOrCreateArchiveGrid();

    grid.innerHTML = sectionStories.map(renderCard).join('');

    grid.setAttribute('data-restored-old-category-articles', 'true');

    makeCardsClickable(grid);

    grid.querySelectorAll('img').forEach((img) => {

      img.addEventListener('error', () => {

        const wrap = img.closest('.story-card__image');

        if (wrap) wrap.style.display = 'none';

      });

    });

  }

  function runRestoreSeveralTimes() {

    restoreCategoryArticles();

    window.setTimeout(restoreCategoryArticles, 250);

    window.setTimeout(restoreCategoryArticles, 900);

    window.setTimeout(restoreCategoryArticles, 1800);

    window.setTimeout(restoreCategoryArticles, 3500);

  }

  ready(runRestoreSeveralTimes);

})();

/* PRESS_DYNAMIC_INTERACTIONS_START
   Progressive dynamic UI layer: subtle tilt/lift, reveal-on-scroll, tactile ripples,
   smooth internal navigation, and a small back-to-top helper. Respects reduced motion.
*/
(() => {

  const root = document.documentElement;
  const CARD_SELECTOR = [
    '.story-card',
    '.archive-card',
    '.river-item',
    '.lead-panel',
    '.desk-card',
    '.link-list__item',
    '.related-card',
    '.edition-radar__item',
    '.press-catchup__item',
    '.daily-card'
  ].join(', ');

  const REVEAL_SELECTOR = [
    '.story-card',
    '.archive-card',
    '.river-item',
    '.lead-panel',
    '.desk-card',
    '.rail',
    '.newsletter-block',
    '.trust-card',
    '.article-body',
    '.article-sources',
    '.edition-radar',
    '.desk-pulse',
    '.press-catchup',
    '.daily-home-section',
    '.daily-archive-section',
    '.breaking-wire-section'
  ].join(', ');

  const RIPPLE_SELECTOR = [
    'button',
    '.button',
    '.theme-toggle',
    '.reader-mode-toggle',
    '.lead-nav__button',
    '.desk-pulse__catchup',
    '.press-micro-card',
    '.story-card__cta'
  ].join(', ');

  const reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
  const finePointerQuery = window.matchMedia('(hover: hover) and (pointer: fine)');

  root.classList.add('press-dynamic-page');

  const ready = (callback) => {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', callback, { once: true });
    } else {
      callback();
    }
  };

  const prefersReducedMotion = () => reducedMotionQuery.matches;

  function markPageReady() {
    window.requestAnimationFrame(() => root.classList.add('press-page-ready'));
    window.addEventListener('pageshow', () => root.classList.remove('press-page-leaving'));
  }

  function isModifiedClick(event) {
    return event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0;
  }

  function findInternalNavigationTarget(event) {
    if (event.defaultPrevented || isModifiedClick(event)) return null;
    const target = event.target instanceof Element ? event.target : null;
    if (!target) return null;
    if (target.closest('button, input, textarea, select, label, [contenteditable="true"]')) return null;

    const directLink = target.closest('a[href]');
    const cardLink = directLink ? null : target.closest(CARD_SELECTOR)?.querySelector('a[href]');
    const link = directLink || cardLink;
    if (!link) return null;

    const rawHref = link.getAttribute('href') || '';
    if (!rawHref || rawHref.startsWith('#') || /^(mailto|tel|javascript):/i.test(rawHref)) return null;
    if (link.hasAttribute('download')) return null;
    if (link.target && link.target !== '_self') return null;

    let url;
    try {
      url = new URL(rawHref, window.location.href);
    } catch (_) {
      return null;
    }

    if (url.origin !== window.location.origin) return null;
    const sameDocument = url.pathname === window.location.pathname &&
      url.search === window.location.search &&
      Boolean(url.hash);
    if (sameDocument) return null;

    return { url: url.href, host: directLink || target.closest(CARD_SELECTOR) || link };
  }

  function setupSmoothNavigation() {
    document.addEventListener('click', (event) => {
      const navigation = findInternalNavigationTarget(event);
      if (!navigation || prefersReducedMotion()) return;

      event.preventDefault();
      event.stopImmediatePropagation();
      createRipple(navigation.host, event);
      root.classList.add('press-page-leaving');
      window.setTimeout(() => {
        window.location.href = navigation.url;
      }, 170);
    }, true);
  }

  function enhanceCard(card) {
    if (!(card instanceof HTMLElement)) return;
    if (card.dataset.pressDynamicCard === 'true') return;
    card.dataset.pressDynamicCard = 'true';
    card.classList.add('press-micro-card');

    if (!finePointerQuery.matches || prefersReducedMotion()) return;

    card.addEventListener('pointermove', (event) => {
      const rect = card.getBoundingClientRect();
      if (!rect.width || !rect.height) return;
      const x = Math.min(Math.max((event.clientX - rect.left) / rect.width, 0), 1);
      const y = Math.min(Math.max((event.clientY - rect.top) / rect.height, 0), 1);
      const tiltX = (0.5 - y) * 2.4;
      const tiltY = (x - 0.5) * 2.4;
      card.style.setProperty('--press-mouse-x', `${(x * 100).toFixed(2)}%`);
      card.style.setProperty('--press-mouse-y', `${(y * 100).toFixed(2)}%`);
      card.style.setProperty('--press-tilt-x', `${tiltX.toFixed(2)}deg`);
      card.style.setProperty('--press-tilt-y', `${tiltY.toFixed(2)}deg`);
    });

    card.addEventListener('pointerleave', () => {
      card.style.removeProperty('--press-tilt-x');
      card.style.removeProperty('--press-tilt-y');
      card.style.setProperty('--press-mouse-x', '50%');
      card.style.setProperty('--press-mouse-y', '50%');
    });
  }

  function setupMicroInteractions(scope = document) {
    const nodes = [];
    if (scope instanceof Element && scope.matches(CARD_SELECTOR)) nodes.push(scope);
    nodes.push(...scope.querySelectorAll(CARD_SELECTOR));
    nodes.forEach(enhanceCard);
  }

  function setupRevealOnScroll(scope = document, observer) {
    const nodes = [];
    if (scope instanceof Element && scope.matches(REVEAL_SELECTOR)) nodes.push(scope);
    nodes.push(...scope.querySelectorAll(REVEAL_SELECTOR));

    nodes.forEach((node, index) => {
      if (!(node instanceof HTMLElement)) return;
      if (node.dataset.pressRevealBound === 'true') return;
      node.dataset.pressRevealBound = 'true';
      node.setAttribute('data-press-reveal', '');
      node.style.setProperty('--press-reveal-delay', `${Math.min(index % 6, 5) * 45}ms`);

      if (!observer || prefersReducedMotion()) {
        node.classList.add('is-revealed');
        return;
      }

      observer.observe(node);
    });
  }

  function buildRevealObserver() {
    if (!('IntersectionObserver' in window) || prefersReducedMotion()) return null;
    return new IntersectionObserver((entries, observer) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-revealed');
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -8% 0px' });
  }

  function createRipple(host, event) {
    if (!(host instanceof HTMLElement) || prefersReducedMotion()) return;
    if (host.matches('input, textarea, select')) return;

    const rect = host.getBoundingClientRect();
    if (!rect.width || !rect.height) return;

    host.classList.add('press-ripple-host');
    const ripple = document.createElement('span');
    ripple.className = 'press-ink-ripple';
    const size = Math.max(rect.width, rect.height) * 2.15;
    const x = event.clientX ? event.clientX - rect.left : rect.width / 2;
    const y = event.clientY ? event.clientY - rect.top : rect.height / 2;

    ripple.style.setProperty('--press-ripple-size', `${size}px`);
    ripple.style.setProperty('--press-ripple-x', `${x}px`);
    ripple.style.setProperty('--press-ripple-y', `${y}px`);
    host.appendChild(ripple);
    ripple.addEventListener('animationend', () => ripple.remove(), { once: true });
  }

  function setupRipples() {
    document.addEventListener('pointerdown', (event) => {
      if (!(event.target instanceof Element)) return;
      if (event.target.closest('input, textarea, select, label, [contenteditable="true"]')) return;
      const host = event.target.closest(RIPPLE_SELECTOR);
      if (!host) return;
      createRipple(host, event);
    });
  }

  function setupBackToTop() {
    if (document.querySelector('[data-press-back-to-top]')) return;

    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'press-back-to-top';
    button.setAttribute('data-press-back-to-top', '');
    button.setAttribute('aria-label', 'Back to top');
    button.innerHTML = '<span aria-hidden="true">↑</span> Top';
    document.body.appendChild(button);

    button.addEventListener('click', () => {
      window.scrollTo({
        top: 0,
        behavior: prefersReducedMotion() ? 'auto' : 'smooth'
      });
    });

    let ticking = false;
    const update = () => {
      ticking = false;
      button.classList.toggle('is-visible', window.scrollY > 640);
    };

    update();
    window.addEventListener('scroll', () => {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(update);
    }, { passive: true });
  }

  function watchDynamicContent(revealObserver) {
    if (!('MutationObserver' in window) || !document.body) return;
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (!(node instanceof Element)) return;
          setupMicroInteractions(node);
          setupRevealOnScroll(node, revealObserver);
        });
      });
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }

  ready(() => {
    markPageReady();
    const revealObserver = buildRevealObserver();
    setupMicroInteractions();
    setupRevealOnScroll(document, revealObserver);
    setupSmoothNavigation();
    setupRipples();
    setupBackToTop();
    watchDynamicContent(revealObserver);
  });

})();
/* PRESS_DYNAMIC_INTERACTIONS_END */
