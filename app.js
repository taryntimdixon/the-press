const PRESS_SITE_ASSET_BASE = (() => {
  const script = document.currentScript
    || Array.from(document.scripts).reverse().find((item) => /(?:^|\/)app\.js(?:\?|$)/.test(item.getAttribute('src') || ''));
  const scriptSrc = script?.getAttribute('src') || 'app.js';
  return new URL('.', new URL(scriptSrc, window.location.href)).href;
})();

function pressSiteAssetUrl(path) {
  const value = String(path || '').trim();
  if (!value || /^(?:[a-z][a-z0-9+.-]*:|\/|#)/i.test(value)) return value;
  return new URL(value, PRESS_SITE_ASSET_BASE).href;
}

(() => {
  const IMAGE_LINK_SELECTOR = '.drone-article-visual__media[href]';
  let activeLightbox = null;

  function openImageLightbox(link, event) {
    if (!link) return;
    const image = link.querySelector('img');
    if (!image) return;
    event?.preventDefault();

    closeImageLightbox({ restoreHistory: false, restoreFocus: false });

    const overlay = document.createElement('div');
    overlay.className = 'press-image-lightbox';
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.setAttribute('aria-label', image.alt || 'Full image view');
    overlay.tabIndex = -1;

    const backButton = document.createElement('button');
    backButton.type = 'button';
    backButton.className = 'press-image-lightbox__back';
    backButton.textContent = 'Back to article';

    const closeButton = document.createElement('button');
    closeButton.type = 'button';
    closeButton.className = 'press-image-lightbox__close';
    closeButton.setAttribute('aria-label', 'Close full image view');
    closeButton.textContent = 'X';

    const frame = document.createElement('div');
    frame.className = 'press-image-lightbox__frame';

    const fullImage = document.createElement('img');
    fullImage.className = 'press-image-lightbox__image';
    fullImage.src = link.href;
    fullImage.alt = image.alt || '';
    fullImage.decoding = 'async';

    frame.appendChild(fullImage);
    overlay.append(backButton, closeButton, frame);
    document.body.appendChild(overlay);
    document.body.classList.add('press-image-lightbox-open');

    activeLightbox = {
      overlay,
      opener: link,
      historyPushed: false,
    };

    try {
      window.history.pushState({ ...(window.history.state || {}), pressImageLightbox: true }, '', window.location.href);
      activeLightbox.historyPushed = true;
    } catch (_) {
      activeLightbox.historyPushed = false;
    }

    backButton.addEventListener('click', () => closeImageLightbox());
    closeButton.addEventListener('click', () => closeImageLightbox());
    overlay.addEventListener('click', (clickEvent) => {
      if (clickEvent.target === overlay) closeImageLightbox();
    });
    overlay.focus({ preventScroll: true });
  }

  function closeImageLightbox(options = {}) {
    const { restoreHistory = true, restoreFocus = true } = options;
    if (!activeLightbox) return;
    const { overlay, opener, historyPushed } = activeLightbox;
    activeLightbox = null;
    overlay.remove();
    document.body.classList.remove('press-image-lightbox-open');
    if (restoreFocus) opener?.focus?.({ preventScroll: true });
    if (restoreHistory && historyPushed && window.history.state?.pressImageLightbox) {
      window.history.back();
    }
  }

  document.addEventListener('click', (event) => {
    const link = event.target.closest?.(IMAGE_LINK_SELECTOR);
    if (!link) return;
    openImageLightbox(link, event);
  });

  document.addEventListener('keydown', (event) => {
    if (!activeLightbox) return;
    if (event.key === 'Escape') {
      event.preventDefault();
      closeImageLightbox();
    }
  });

  window.addEventListener('popstate', () => {
    if (activeLightbox) closeImageLightbox({ restoreHistory: false });
  });
})();

(() => {
  const CHART_EXPAND_SELECTOR = '[data-chart-expand]';
  let activeChartLightbox = null;

  function openChartLightbox(button, event) {
    const selector = button?.getAttribute('data-chart-expand');
    const figure = selector ? document.querySelector(selector) : null;
    const visual = figure?.querySelector('.drone-data-graphic__visual');
    if (!figure || !visual) return;
    event?.preventDefault();

    closeChartLightbox({ restoreFocus: false });

    const overlay = document.createElement('div');
    overlay.className = 'press-chart-lightbox';
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.setAttribute('aria-label', 'Expanded chart view');
    overlay.tabIndex = -1;

    const backButton = document.createElement('button');
    backButton.type = 'button';
    backButton.className = 'press-chart-lightbox__back';
    backButton.textContent = 'Back to article';

    const closeButton = document.createElement('button');
    closeButton.type = 'button';
    closeButton.className = 'press-chart-lightbox__close';
    closeButton.setAttribute('aria-label', 'Close expanded chart');
    closeButton.textContent = 'X';

    const frame = document.createElement('div');
    frame.className = 'press-chart-lightbox__frame';

    const expandedFigure = document.createElement('figure');
    expandedFigure.className = figure.className;
    expandedFigure.classList.add('press-chart-lightbox__figure');

    const visualClone = visual.cloneNode(true);
    visualClone.classList.add('press-chart-lightbox__visual');
    visualClone.removeAttribute('href');
    visualClone.removeAttribute('target');
    visualClone.removeAttribute('rel');
    visualClone.removeAttribute('aria-label');

    const caption = figure.querySelector('figcaption')?.cloneNode(true);
    caption?.querySelectorAll(CHART_EXPAND_SELECTOR).forEach((node) => node.remove());

    expandedFigure.appendChild(visualClone);
    if (caption) expandedFigure.appendChild(caption);
    frame.appendChild(expandedFigure);
    overlay.append(backButton, closeButton, frame);
    document.body.appendChild(overlay);
    document.body.classList.add('press-image-lightbox-open');

    activeChartLightbox = { overlay, opener: button };

    backButton.addEventListener('click', () => closeChartLightbox());
    closeButton.addEventListener('click', () => closeChartLightbox());
    overlay.addEventListener('click', (clickEvent) => {
      if (clickEvent.target === overlay) closeChartLightbox();
    });
    overlay.focus({ preventScroll: true });
  }

  function closeChartLightbox(options = {}) {
    const { restoreFocus = true } = options;
    if (!activeChartLightbox) return;
    const { overlay, opener } = activeChartLightbox;
    activeChartLightbox = null;
    overlay.remove();
    document.body.classList.remove('press-image-lightbox-open');
    if (restoreFocus) opener?.focus?.({ preventScroll: true });
  }

  document.addEventListener('click', (event) => {
    const button = event.target.closest?.(CHART_EXPAND_SELECTOR);
    if (!button) return;
    openChartLightbox(button, event);
  });

  document.addEventListener('keydown', (event) => {
    if (!activeChartLightbox) return;
    if (event.key === 'Escape') {
      event.preventDefault();
      closeChartLightbox();
    }
  });
})();

(() => {
  const NOTE_LINK_SELECTOR = '.source-notes li[id] > a[href], .source-list li[id] > a[href]';
  const INLINE_SOURCE_SELECTOR = '.source-ref a[href^="#source-"]';
  const DIRECT_SOURCE_SELECTOR = [
    '.drone-source-chips a[href^="#source-"]',
    '.drone-data-graphic__visual[href^="#source-"]',
  ].join(', ');
  const SOURCE_RAIL_LINK_SELECTOR = [
    '.drone-social-feature .press-static-post > a[href]',
    '.article-rail-gallery__card[href]',
  ].join(', ');

  function isExternalSourceHref(href) {
    return /^https?:\/\//i.test(String(href || ''));
  }

  function applyExternalSourceLink(link, source, options = {}) {
    if (!link || !source?.href) return;
    link.setAttribute('href', source.href);
    link.removeAttribute('target');
    link.setAttribute('rel', 'noopener noreferrer');
    link.setAttribute('data-source-external', 'true');
    if (source.label) link.setAttribute('aria-label', `Open source: ${source.label}`);
    if (options.relabel && !link.querySelector('img')) {
      link.textContent = 'Open source site';
    }
  }

  function enhanceArticleSourceLinks() {
    const sourceMap = new Map();

    document.querySelectorAll(NOTE_LINK_SELECTOR).forEach((link, index) => {
      const note = link.closest('li[id]');
      const href = link.getAttribute('href');
      if (!note?.id || !href || href.startsWith('#')) return;

      sourceMap.set(note.id, {
        href,
        label: link.textContent.trim(),
        number: index + 1,
      });

      applyExternalSourceLink(link, sourceMap.get(note.id));
    });

    document.querySelectorAll(INLINE_SOURCE_SELECTOR).forEach((link) => {
      const id = (link.getAttribute('href') || '').slice(1);
      const source = sourceMap.get(id);
      applyExternalSourceLink(link, source);
      if (source?.number) {
        link.textContent = `[${source.number}]`;
        link.dataset.sourceNumber = String(source.number);
        link.title = source.label ? `Source ${source.number}: ${source.label}` : `Source ${source.number}`;
      }
    });

    document.querySelectorAll(DIRECT_SOURCE_SELECTOR).forEach((link) => {
      const id = (link.getAttribute('href') || '').slice(1);
      const source = sourceMap.get(id);
      applyExternalSourceLink(link, source);
    });

    document.querySelectorAll(SOURCE_RAIL_LINK_SELECTOR).forEach((link) => {
      const href = link.getAttribute('href') || '';
      const source = href.startsWith('#source-')
        ? sourceMap.get(href.slice(1))
        : (isExternalSourceHref(href) ? { href, label: link.textContent.trim() } : null);
      applyExternalSourceLink(link, source, { relabel: link.closest('.press-static-post') });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', enhanceArticleSourceLinks, { once: true });
  } else {
    enhanceArticleSourceLinks();
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

    const releaseRestore = () => {

      isRestoring = false;

    };

    if (window.queueMicrotask) {
      window.queueMicrotask(releaseRestore);
    } else {
      window.setTimeout(releaseRestore, 0);
    }

  }

  function queueRestore() {

    if (restoreQueued || isRestoring) return;

    restoreQueued = true;

    const runRestore = () => {

      restoreQueued = false;

      restoreMissingCards();

    };

    if (window.queueMicrotask) {
      window.queueMicrotask(runRestore);
    } else {
      window.requestAnimationFrame(runRestore);
    }

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

    window.setTimeout(restoreMissingCards, 90);

  }

  if (document.readyState === 'loading') {

    document.addEventListener('DOMContentLoaded', bootPreservationGuard, { once: true });

  } else {

    bootPreservationGuard();

  }

})();
(() => {
  const AUTHOR_LABEL = 'By The Press';
  const SEARCH_EMPTY = '<div class="search-empty"><p>Start typing to search the full edition.</p></div>';
  const SEARCH_NONE = '<div class="search-empty"><p>No stories matched that search yet.</p></div>';
  let storyIndexPromise = null;

  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-year]').forEach((node) => {
      node.textContent = new Date().getFullYear();
    });

    ensureHeaderControls();
    ensureMastheadTicker();
    setupMenu();
    setupSearch();
    setupReadingProgress();
    setupLeadPanels();
    setupArchiveFilters();
    setupNewsletterForms();
    normalizeVisibleBylines(document);
    makeCardsClickable();
    makePressSocialCardsClickable(document);
    bindThumbnailFallbacks(document);
    rewriteAuthorsPage();
    relabelUtilityNav();
    injectReadAloudControls();
    prettifySourceLinks(document);
    addInlineSourceMarkers(document);
    setupArticleTrustTools();
    extendSectionNavigation();
    setupDarkMode();
    injectShareButtons();
    bindSourceNoteExternalLinks(document);
    applyDailyCardHover();

    loadStoryIndex().then((stories) => {
      enhanceBreakingStrip(stories);
      renderMastheadTicker(stories);
      injectEditionRadar(stories);
      if (!document.body.classList.contains('page-home')) {
        pressRefreshHomepageStoryBlocks(stories);
      }
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
    fetch(pressSiteAssetUrl(url), { cache: 'no-cache' }).then((response) => {
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

  function ensureHeaderControls() {
    const siteHeader = document.querySelector('[data-site-header]');
    const mastheadRow = siteHeader?.querySelector('.masthead-row');

    if (!siteHeader || !mastheadRow) return;

    let actions = mastheadRow.querySelector('.masthead-actions');
    const utilityNav = mastheadRow.querySelector('.utility-nav') || siteHeader.querySelector('.utility-nav');

    if (!actions) {
      actions = document.createElement('div');
      actions.className = 'masthead-actions';
      mastheadRow.appendChild(actions);
    }

    if (utilityNav && utilityNav.parentElement !== actions) {
      actions.appendChild(utilityNav);
    }

    let controls = actions.querySelector('.header-controls');

    if (!controls) {
      controls = document.createElement('div');
      controls.className = 'header-controls';
      actions.appendChild(controls);
    }

    const themeToggle = siteHeader.querySelector('[data-theme-toggle]') || document.createElement('button');
    themeToggle.classList.add('theme-toggle');
    themeToggle.type = 'button';
    themeToggle.setAttribute('data-theme-toggle', '');
    themeToggle.setAttribute('title', 'Toggle dark/light mode');
    if (!themeToggle.textContent.trim()) themeToggle.textContent = '☀︎';

    const searchButton = siteHeader.querySelector('[data-search-open]') || document.createElement('button');
    searchButton.classList.add('search-trigger');
    searchButton.type = 'button';
    searchButton.setAttribute('data-search-open', '');
    searchButton.textContent = 'Search';

    const menuButton = siteHeader.querySelector('[data-menu-toggle]');

    controls.appendChild(themeToggle);
    controls.appendChild(searchButton);

    if (menuButton && menuButton.parentElement !== controls) {
      controls.appendChild(menuButton);
    }

    siteHeader.querySelectorAll('[data-reader-mode-toggle]').forEach((button) => button.remove());
    siteHeader.querySelector('.topbar')?.remove();
  }

  function ensureMastheadTicker() {
    const siteHeader = document.querySelector('[data-site-header]');
    const mastheadRow = siteHeader?.querySelector('.masthead-row');
    const wrap = mastheadRow?.querySelector('.masthead-wrap');

    if (!siteHeader || !mastheadRow || !wrap) return;

    siteHeader.querySelectorAll('.masthead-tagline').forEach((tagline) => tagline.remove());

    let ticker = mastheadRow.querySelector('.masthead-ticker');

    if (!ticker) {
      ticker = wrap.querySelector('.masthead-ticker') || document.createElement('div');
      ticker.className = 'masthead-ticker';
      ticker.setAttribute('aria-label', 'Latest headlines');
      ticker.innerHTML = '<div class="masthead-ticker__items" data-masthead-ticker></div>';
    }

    if (ticker.parentElement !== mastheadRow) {
      mastheadRow.appendChild(ticker);
    }
  }

  function renderMastheadTicker(stories) {
    const itemsBox = document.querySelector('[data-masthead-ticker]');
    if (!itemsBox || !Array.isArray(stories) || !stories.length) return;

    const seen = new Set();
    const headlines = stories
      .filter((story) => story?.title && story?.url)
      .filter((story) => {
        const key = `${story.title}|${story.url}`;
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
      })
      .slice(0, 14);

    if (!headlines.length) return;

    const links = headlines
      .map((story) => `<a href="${escapeAttribute(story.url)}"><span>${escapeHtml(story.section || 'News')}</span>${escapeHtml(story.title)}</a>`)
      .join('');
    const charBudget = headlines.reduce((sum, story) => sum + Math.min(110, story.title.length), 0);

    itemsBox.style.setProperty('--masthead-ticker-duration', `${Math.max(70, Math.min(150, Math.round(charBudget / 7)))}s`);
    itemsBox.innerHTML = `<div class="masthead-ticker__track">${links}${links}</div>`;
  }

  function normalizeVisibleBylines(root) {
    const replaceHouseByline = (text) =>
      text.replace(/^(?:By\s+)?(?:The Press|The Press Staff|Intelligent AI|Written and Researched by AI)(?=\s*[•·]|\s*$)/i, AUTHOR_LABEL);

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
          if (/^(?:Intelligent AI|Written and Researched by AI|AI)\b/i.test(text)) {
            node.textContent = AUTHOR_LABEL;
          } else if (!/^By\s+/i.test(text)) {
            node.textContent = `By ${text}`;
          }
          return;
        }
        if (/^(?:By\s+)?(?:The Press|Intelligent AI|Written and Researched by AI)\b/i.test(text)) {
          node.textContent = replaceHouseByline(text);
        } else if (/^By\b/i.test(text)) {
          node.textContent = text.replace(/^By\s+.*?(?=\s*[•·]|\s*$)/i, AUTHOR_LABEL);
        } else if (/^The Press Staff|^Intelligent AI|^Written and Researched by AI/i.test(text)) {
          node.textContent = AUTHOR_LABEL;
        }
      });
    });

    root.querySelectorAll('.author-panel').forEach((panel) => {
      panel.innerHTML = '<h2>Masthead</h2><p><strong>The Press</strong>. Source notes, dates, and corrections stay close to the work.</p>';
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

  function makePressSocialCardsClickable(root = document) {
    root.querySelectorAll('.press-static-post').forEach((card) => {
      if (card.dataset.pressSocialClickBound === 'true') return;
      const link = card.querySelector('a[href]');
      if (!link) return;

      card.dataset.pressSocialClickBound = 'true';
      card.classList.add('press-static-post--clickable');
      card.setAttribute('tabindex', '0');
      card.setAttribute('role', 'link');

      const labelParts = [
        card.querySelector('.press-static-post__name')?.textContent,
        card.querySelector('.press-static-post__visual strong')?.textContent,
        link.textContent,
      ].map((text) => collapseWhitespace(text || '')).filter(Boolean);
      if (labelParts.length) {
        card.setAttribute('aria-label', labelParts.join(': '));
      }

      link.setAttribute('rel', 'noopener noreferrer');
      link.removeAttribute('target');

      const openSource = () => {
        window.location.href = link.href;
      };

      card.addEventListener('click', (event) => {
        if (event.target.closest('a, button, input, textarea, select, label')) return;
        openSource();
      });

      card.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          openSource();
        }
      });
    });
  }

  function relabelUtilityNav() {
    document.querySelectorAll('a[href="authors.html"]').forEach((link) => {
      if (/authors/i.test(link.textContent || '')) {
        link.textContent = 'Masthead';
      }
    });
  }

  function injectReadAloudControls() {
    const article = document.querySelector('.article');
    const body = document.querySelector('.article-body');
    const hero = document.querySelector('.article-hero');
    if (!article || !body || !hero || !('speechSynthesis' in window)) return;
    if (document.querySelector('[data-listen-controls]')) return;

    const synth = window.speechSynthesis;
    const VOICE_STORAGE_KEY = 'press.listen.voice';
    const RATE_STORAGE_KEY = 'press.listen.rate';

    const wrapper = document.createElement('div');
    wrapper.className = 'listen-controls';
    wrapper.setAttribute('data-listen-controls', '');
    wrapper.innerHTML = `
      <div class="listen-actions">
        <button class="listen-button" type="button" data-listen-play aria-label="Read this article aloud">🔊 Listen</button>
        <button class="listen-button listen-button--ghost" type="button" data-listen-pause aria-label="Pause reading">Pause</button>
        <button class="listen-button listen-button--ghost" type="button" data-listen-stop aria-label="Stop reading">Stop</button>
      </div>
      <div class="listen-settings" data-listen-settings>
        <label class="listen-field listen-field--voice">
          <span>Voice</span>
          <select class="listen-select" data-listen-voice aria-label="Voice">
            <option value="">System voice</option>
          </select>
        </label>
        <label class="listen-field listen-field--speed">
          <span>Speed</span>
          <input class="listen-range" type="range" min="0.85" max="1.12" step="0.01" value="0.96" data-listen-rate aria-label="Reading speed">
          <strong class="listen-speed-value" data-listen-rate-value>0.96x</strong>
        </label>
      </div>
      <span class="listen-status" data-listen-status>Ready to read aloud</span>
    `;
    const meta = hero.querySelector('.article-meta');
    const figure = hero.querySelector('.hero-figure');
    if (figure) figure.insertAdjacentElement('afterend', wrapper);
    else if (meta) meta.insertAdjacentElement('afterend', wrapper);
    else hero.appendChild(wrapper);

    const play = wrapper.querySelector('[data-listen-play]');
    const pause = wrapper.querySelector('[data-listen-pause]');
    const stop = wrapper.querySelector('[data-listen-stop]');
    const status = wrapper.querySelector('[data-listen-status]');
    const voiceSelect = wrapper.querySelector('[data-listen-voice]');
    const rateInput = wrapper.querySelector('[data-listen-rate]');
    const rateValue = wrapper.querySelector('[data-listen-rate-value]');

    let voices = [];
    let segments = [];
    let segmentIndex = 0;
    let utterance = null;
    let stopRequested = true;
    let activeSpeechRun = 0;

    const setStatus = (message) => {
      if (status) status.textContent = message;
    };

    const readStoredValue = (key) => {
      try {
        return window.localStorage.getItem(key);
      } catch (_) {
        return '';
      }
    };

    const writeStoredValue = (key, value) => {
      try {
        window.localStorage.setItem(key, value);
      } catch (_) {}
    };

    const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

    const formatRate = (value) => {
      const text = Number(value).toFixed(2).replace(/\.00$/, '').replace(/0$/, '');
      return `${text}x`;
    };

    const updateRateLabel = () => {
      const value = clamp(Number(rateInput?.value) || 0.96, 0.85, 1.12);
      if (rateInput) rateInput.value = String(value);
      if (rateValue) rateValue.textContent = formatRate(value);
      return value;
    };

    const getRate = () => updateRateLabel();

    const getVoiceId = (voice) => voice ? (voice.voiceURI || `${voice.name}|${voice.lang}`) : '';

    const scoreVoice = (voice) => {
      if (!voice) return -Infinity;
      const name = `${voice.name || ''} ${voice.voiceURI || ''}`.toLowerCase();
      const lang = String(voice.lang || '').toLowerCase();
      const userLang = String(navigator.language || 'en-US').toLowerCase();
      const userBase = userLang.split('-')[0];
      let score = 0;

      if (lang === userLang) score += 36;
      if (lang === 'en-us') score += 30;
      if (lang.startsWith(`${userBase}-`)) score += 24;
      if (lang.startsWith('en')) score += 18;
      if (voice.default) score += 8;
      if (voice.localService) score += 3;
      if (/samantha|ava|allison|susan|zoe|nicky|siri|google us english|microsoft aria|microsoft jenny|microsoft guy|microsoft davis|microsoft michelle|natural|neural|enhanced|premium/.test(name)) score += 28;
      if (/compact|novelty|whisper|bells|boing|bubbles|cellos|deranged|good news|bad news|hysterical|jester|organ|superstar|trinoids|whisper|zarvox/.test(name)) score -= 80;

      return score;
    };

    const sortVoices = (items) => {
      return Array.from(items || []).sort((a, b) => {
        const scoreDelta = scoreVoice(b) - scoreVoice(a);
        if (scoreDelta) return scoreDelta;
        return String(a.name || '').localeCompare(String(b.name || ''));
      });
    };

    const chooseBestVoice = (items) => sortVoices(items)[0] || null;

    const getSelectedVoice = () => {
      const selectedId = voiceSelect?.value || '';
      return voices.find((voice) => getVoiceId(voice) === selectedId) || chooseBestVoice(voices);
    };

    const populateVoices = () => {
      const available = sortVoices(synth.getVoices());
      const storedVoiceId = readStoredValue(VOICE_STORAGE_KEY);
      const currentVoiceId = voiceSelect?.value || storedVoiceId;
      voices = available;
      if (!voiceSelect) return;

      voiceSelect.replaceChildren();
      if (!voices.length) {
        voiceSelect.appendChild(new Option('System voice', ''));
        voiceSelect.disabled = true;
        return;
      }

      voiceSelect.disabled = false;
      voices.forEach((voice) => {
        const label = `${voice.name}${voice.lang ? ` (${voice.lang})` : ''}`;
        voiceSelect.appendChild(new Option(label, getVoiceId(voice)));
      });

      const nextVoiceId = voices.some((voice) => getVoiceId(voice) === currentVoiceId)
        ? currentVoiceId
        : getVoiceId(chooseBestVoice(voices));
      voiceSelect.value = nextVoiceId || '';
    };

    const splitLongSegment = (text, maxLength = 1200) => {
      const clean = collapseWhitespace(text);
      if (!clean) return [];
      if (clean.length <= maxLength) return [clean];

      const sentences = clean.match(/[^.!?]+[.!?]+["')\]]*|[^.!?]+$/g) || [clean];
      const chunks = [];
      let current = '';

      sentences.forEach((sentence) => {
        const piece = collapseWhitespace(sentence);
        if (!piece) return;

        if (piece.length > maxLength) {
          if (current) {
            chunks.push(current);
            current = '';
          }
          let remainder = piece;
          while (remainder.length > maxLength) {
            const cut = Math.max(remainder.lastIndexOf(' ', maxLength), Math.floor(maxLength * 0.7));
            chunks.push(collapseWhitespace(remainder.slice(0, cut)));
            remainder = collapseWhitespace(remainder.slice(cut));
          }
          if (remainder) current = remainder;
          return;
        }

        const next = current ? `${current} ${piece}` : piece;
        if (next.length > maxLength) {
          if (current) chunks.push(current);
          current = piece;
        } else {
          current = next;
        }
      });

      if (current) chunks.push(current);
      return chunks;
    };

    const getReadableSegments = () => {
      const clone = body.cloneNode(true);
      clone.querySelectorAll([
        'script',
        'style',
        'noscript',
        'aside',
        'figure',
        'nav',
        '[hidden]',
        '[aria-hidden="true"]',
        '.article-jump-strip',
        '.article-rail-gallery',
        '.article-source-drawer',
        '.press-social-side',
        '.press-social-sources',
        '.source-notes',
        '.source-ref',
      ].join(',')).forEach((node) => node.remove());

      const readableNodes = Array.from(clone.querySelectorAll('h2, h3, p, blockquote, li'));
      const textBlocks = readableNodes.length
        ? readableNodes.map((node) => collapseWhitespace(node.textContent || ''))
        : [collapseWhitespace(clone.textContent || '')];

      return textBlocks
        .filter((text) => text && text.length > 2 && !/^(article gallery|open link|source notes)$/i.test(text))
        .flatMap((text) => splitLongSegment(text));
    };

    const setPauseLabel = (label = 'Pause') => {
      if (pause) pause.textContent = label;
    };

    const finishSpeech = () => {
      utterance = null;
      stopRequested = true;
      setPauseLabel();
      setStatus('Finished reading');
    };

    const speakCurrentSegment = () => {
      if (stopRequested) return;
      if (segmentIndex >= segments.length) {
        finishSpeech();
        return;
      }

      const speechToken = ++activeSpeechRun;
      utterance = new SpeechSynthesisUtterance(segments[segmentIndex]);
      const selectedVoice = getSelectedVoice();
      if (selectedVoice) utterance.voice = selectedVoice;
      utterance.rate = getRate();
      utterance.pitch = 1;
      utterance.onstart = () => setStatus('Reading aloud');
      utterance.onend = () => {
        if (stopRequested || speechToken !== activeSpeechRun) return;
        segmentIndex += 1;
        if (segmentIndex >= segments.length) {
          finishSpeech();
        } else {
          window.setTimeout(speakCurrentSegment, 80);
        }
      };
      utterance.onerror = () => {
        if (stopRequested || speechToken !== activeSpeechRun) return;
        utterance = null;
        stopRequested = true;
        setPauseLabel();
        setStatus('Read-aloud unavailable in this browser');
      };
      synth.speak(utterance);
    };

    const startSpeech = () => {
      segments = getReadableSegments();
      segmentIndex = 0;
      if (!segments.length) return;
      stopRequested = false;
      activeSpeechRun += 1;
      synth.cancel();
      window.setTimeout(speakCurrentSegment, 60);
    };

    const stopSpeech = () => {
      stopRequested = true;
      activeSpeechRun += 1;
      synth.cancel();
      utterance = null;
      setPauseLabel();
      setStatus('Stopped');
    };

    const savedRate = clamp(Number(readStoredValue(RATE_STORAGE_KEY)) || 0.96, 0.85, 1.12);
    if (rateInput) rateInput.value = String(savedRate);
    updateRateLabel();
    populateVoices();
    if (typeof synth.addEventListener === 'function') {
      synth.addEventListener('voiceschanged', populateVoices);
    } else if ('onvoiceschanged' in synth) {
      synth.onvoiceschanged = populateVoices;
    }
    window.setTimeout(populateVoices, 250);

    voiceSelect?.addEventListener('change', () => {
      writeStoredValue(VOICE_STORAGE_KEY, voiceSelect.value || '');
      setStatus(synth.speaking ? 'Voice changes on the next paragraph' : 'Voice saved');
    });

    rateInput?.addEventListener('input', () => {
      const rate = updateRateLabel();
      writeStoredValue(RATE_STORAGE_KEY, String(rate));
      if (!synth.speaking) setStatus('Speed saved');
    });

    play.addEventListener('click', () => {
      if (synth.paused) {
        synth.resume();
        setPauseLabel();
        setStatus('Reading aloud');
        return;
      }
      startSpeech();
    });

    pause.addEventListener('click', () => {
      if (!synth.speaking) return;
      if (synth.paused) {
        synth.resume();
        setPauseLabel();
        setStatus('Reading aloud');
      } else {
        synth.pause();
        setPauseLabel('Resume');
        setStatus('Paused');
      }
    });

    stop.addEventListener('click', stopSpeech);
    window.addEventListener('beforeunload', stopSpeech);
  }

  function setupArticleTrustTools() {
    const article = document.querySelector('body.page-article .article, body.page-article .article-shell, .page-article .article, .page-article .article-shell');
    const body = article?.querySelector('.article-body, [data-article-body]');
    if (!article || !body) return;

    injectArticleDisclosure(article);
    setupArticleSourceDrawer(article);
  }

  function injectArticleDisclosure(article) {
    article.querySelectorAll('[data-article-trust-card]').forEach((node) => node.remove());
    return;
    if (article.querySelector('[data-article-trust-card]')) return;

    const disclosure = document.createElement('section');
    disclosure.className = 'article-trust-card';
    disclosure.setAttribute('data-article-trust-card', '');
    disclosure.setAttribute('aria-label', 'Editorial and AI disclosure');
    disclosure.innerHTML = `
      <div class="article-trust-card__copy">
        <p class="article-trust-card__kicker">Editorial note</p>
        <p class="article-trust-card__text">Written and Researched by AI and checked through The Press editorial workflow for sourcing, clarity, and corrections. Inline markers connect claims to the source notes.</p>
        <div class="article-trust-card__badges" aria-label="Story review status">
          <span>AI assisted</span>
          <span>Human reviewed</span>
        </div>
      </div>
      <button class="article-trust-card__button" type="button" data-source-drawer-open>Source drawer</button>
    `;

    const figure = article.querySelector('.article-hero .hero-figure');
    const meta = article.querySelector('.article-meta');
    if (figure) {
      figure.insertAdjacentElement('afterend', disclosure);
    } else if (meta) {
      meta.insertAdjacentElement('afterend', disclosure);
    } else {
      (article.querySelector('.article-hero') || article).appendChild(disclosure);
    }
  }

  function setupArticleSourceDrawer(article) {
    if (document.querySelector('[data-article-source-drawer]')) {
      bindArticleSourceButtons();
      return;
    }

    const sources = collectArticleSources(article);
    const sourceItems = sources.length
      ? sources.map((source, index) => `
          <li${source.href ? ` data-source-drawer-url="${escapeAttribute(source.href)}"` : ''}>
            <span class="article-source-drawer__number">${index + 1}</span>
            <div>
              ${source.href ? `<a href="${escapeAttribute(source.href)}" rel="noopener noreferrer" data-source-drawer-link>${escapeHtml(source.label)}</a>` : `<strong>${escapeHtml(source.label)}</strong>`}
              ${source.detail ? `<p>${escapeHtml(source.detail)}</p>` : ''}
            </div>
          </li>
        `).join('')
      : '<li><span class="article-source-drawer__number">1</span><div><strong>Source notes</strong><p>No source list was found on this story yet.</p></div></li>';

    const drawer = document.createElement('aside');
    drawer.className = 'article-source-drawer';
    drawer.setAttribute('data-article-source-drawer', '');
    drawer.setAttribute('aria-label', 'Article source drawer');
    drawer.setAttribute('aria-modal', 'true');
    drawer.setAttribute('role', 'dialog');
    drawer.hidden = true;
    drawer.innerHTML = `
      <button class="article-source-drawer__scrim" type="button" data-source-drawer-close aria-label="Close source drawer"></button>
      <div class="article-source-drawer__panel" role="document">
        <div class="article-source-drawer__header">
          <div>
            <p class="article-source-drawer__kicker">Source trail</p>
            <h2>How this story is backed up</h2>
          </div>
          <button class="article-source-drawer__close" type="button" data-source-drawer-close aria-label="Close source drawer">Close</button>
        </div>
        <p class="article-source-drawer__intro">These are the source notes attached to the article. The numbered markers in the story point back to this record.</p>
        <ol class="article-source-drawer__list">
          ${sourceItems}
        </ol>
      </div>
    `;

    document.body.appendChild(drawer);
    bindArticleSourceButtons();
  }

  function collectArticleSources(article) {
    const selectors = [
      '#source-notes .source-list li',
      '#source-notes li',
      '.article-sources li',
      '.source-notes li',
      '.source-list li',
    ];
    const seen = new Set();
    const items = [];

    selectors.forEach((selector) => {
      article.querySelectorAll(selector).forEach((item) => {
        if (seen.has(item)) return;
        seen.add(item);

        const primaryLink = Array.from(item.querySelectorAll('a[href]')).find((link) => {
          const href = link.getAttribute('href') || '';
          return /^https?:\/\//i.test(href);
        }) || item.querySelector('a[href]');
        const sourceName = collapseWhitespace(item.querySelector('strong')?.textContent || '');
        const linkText = collapseWhitespace(primaryLink?.textContent || '');
        const fullText = collapseWhitespace(item.textContent || '');
        const label = sourceName || linkText || `Source ${items.length + 1}`;
        let detail = sourceName && linkText ? linkText : fullText;

        if (!detail || detail === label) {
          detail = fullText.replace(label, '');
        }
        detail = collapseWhitespace(detail.replace(/^[,.:;\-\s]+/, '').replace(/\.$/, ''));

        items.push({
          label,
          detail,
          href: primaryLink?.getAttribute('href') || '',
        });
      });
    });

    return items;
  }

  function bindArticleSourceButtons() {
    const drawer = document.querySelector('[data-article-source-drawer]');
    if (!drawer) return;

    let lastSourceDrawerFocus = null;

    const closeDrawer = () => {
      drawer.hidden = true;
      document.documentElement.classList.remove('source-drawer-open');
      if (lastSourceDrawerFocus && typeof lastSourceDrawerFocus.focus === 'function') {
        lastSourceDrawerFocus.focus({ preventScroll: true });
      }
    };

    const openDrawer = () => {
      lastSourceDrawerFocus = document.activeElement;
      drawer.hidden = false;
      document.documentElement.classList.add('source-drawer-open');
      drawer.querySelector('.article-source-drawer__close')?.focus({ preventScroll: true });
    };

    document.querySelectorAll('[data-source-drawer-open]').forEach((button) => {
      if (button.dataset.sourceDrawerBound === 'true') return;
      button.dataset.sourceDrawerBound = 'true';
      button.addEventListener('click', openDrawer);
    });

    drawer.querySelectorAll('[data-source-drawer-close]').forEach((button) => {
      if (button.dataset.sourceDrawerBound === 'true') return;
      button.dataset.sourceDrawerBound = 'true';
      button.addEventListener('click', closeDrawer);
    });

    if (drawer.dataset.sourceLinkBound !== 'true') {
      drawer.dataset.sourceLinkBound = 'true';
      drawer.addEventListener('click', (event) => {
        const target = event.target instanceof Element ? event.target : null;
        const sourceItem = target?.closest('[data-source-drawer-url]');
        const link = target?.closest('[data-source-drawer-link]') || sourceItem?.querySelector('[data-source-drawer-link]');
        if (!link || !drawer.contains(link)) return;

        const href = link.getAttribute('href') || '';
        const plainClick = event.button === 0 && !event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey;
        if (!plainClick || !href || href.startsWith('#') || /^(mailto|tel|javascript):/i.test(href)) return;

        event.preventDefault();
        closeDrawer();
        window.location.href = link.href;
      });
    }

    if (drawer.dataset.escapeBound !== 'true') {
      drawer.dataset.escapeBound = 'true';
      document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && !drawer.hidden) closeDrawer();
      });
    }
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

    const chosenButton = leadButtons.find((button) => button.classList.contains('is-active')) || leadButtons[0];
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

    const grid = document.querySelector('.cards-grid--archive, .cards-grid');
    if (!grid) return;

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
        const response = await fetch(pressSiteAssetUrl(url), { cache: 'force-cache' });
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
    root.querySelectorAll('.source-notes a, .source-list a, .article-sources a, .article-source-notes a, .generated-story .source-notes a').forEach((a) => {
      const raw = collapseWhitespace(a.textContent || '');
      const href = a.getAttribute('href') || '';
      if (!raw || !/^https?:\/\//i.test(raw)) return;
      try {
        const url = new URL(href || raw);
        a.textContent = humanSourceLabel(url.hostname, url.pathname);
      } catch (_) {}
    });
  }

  function bindSourceNoteExternalLinks(root) {
    root.querySelectorAll('#source-notes a[href^="http"], .source-notes a[href^="http"], .article-sources a[href^="http"], .source-list a[href^="http"]').forEach((link) => {
      if (link.dataset.sourceNoteExternalBound === 'true') return;
      link.dataset.sourceNoteExternalBound = 'true';
      link.removeAttribute('target');
      link.setAttribute('rel', 'noopener noreferrer');
    });
  }

  function addInlineSourceMarkers(root) {
    const page = root.body || document.body;
    if (!page?.classList?.contains('page-article')) return;

    const article = root.querySelector('body.page-article .article, body.page-article .article-shell, .page-article .article, .page-article .article-shell');
    const body = article?.querySelector('.article-body, [data-article-body]');
    if (!article || !body || body.querySelector('.source-ref')) return;

    const sources = collectArticleSourcesForMarkers(article);
    if (!sources.length) return;

    const paragraphs = Array.from(body.querySelectorAll('p'))
      .filter((paragraph) => {
        if (paragraph.closest('.article-sources, #source-notes, .source-notes, .related-block, .share-row')) return false;
        if (paragraph.closest('.press-static-visual, .poker-static-visuals, .press-static-post')) return false;
        if (paragraph.querySelector('.source-ref')) return false;
        return collapseWhitespace(paragraph.textContent || '').length >= 90;
      });

    if (!paragraphs.length) return;

    sources.forEach((source, index) => {
      const targetIndex = Math.min(
        paragraphs.length - 1,
        Math.floor((index * paragraphs.length) / Math.max(sources.length, 1))
      );
      const target = paragraphs[targetIndex];
      const sup = document.createElement('sup');
      const link = document.createElement('a');

      sup.className = 'source-ref source-ref--auto';
      link.href = `#${source.id}`;
      link.textContent = `[${index + 1}]`;
      link.setAttribute('aria-label', `Source ${index + 1}`);
      sup.appendChild(link);
      target.appendChild(sup);
    });
  }

  function collectArticleSourcesForMarkers(article) {
    const selectors = [
      '#source-notes .source-list li',
      '#source-notes li',
      '.article-sources li',
      '.source-notes li',
      '.source-list li',
    ];
    const seen = new Set();
    const sources = [];

    selectors.forEach((selector) => {
      article.querySelectorAll(selector).forEach((item) => {
        if (seen.has(item)) return;
        seen.add(item);
        if (!collapseWhitespace(item.textContent || '')) return;

        const index = sources.length + 1;
        if (!item.id) item.id = `source-${index}`;
        sources.push({ id: item.id });
      });
    });

    return sources;
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
    const articleHero = document.querySelector('.article-hero');
    const articleMeta = articleHero?.querySelector('.article-meta');
    const articleBody = document.querySelector('.article-body');
    const homeIntro = document.querySelector('.page-home .home-hero__intro');
    const contextType = articleHero ? 'article' : (homeIntro ? 'site' : '');
    const target = articleMeta || articleBody || homeIntro;
    if (!contextType || !target || document.querySelector('[data-press-share-row]')) return;

    const context = buildShareContext(contextType);
    const shareRow = document.createElement('nav');
    shareRow.className = `share-row share-row--${contextType}`;
    shareRow.setAttribute('aria-label', context.ariaLabel);
    shareRow.setAttribute('data-press-share-row', contextType);
    shareRow.innerHTML = buildShareRowMarkup(context);

    if (articleMeta) {
      articleMeta.insertAdjacentElement('afterend', shareRow);
    } else if (articleBody) {
      articleBody.insertAdjacentElement('afterend', shareRow);
    } else {
      homeIntro.appendChild(shareRow);
    }

    bindShareRow(shareRow, context);
  }

  function buildShareContext(type) {
    const headline = document.querySelector('.article-headline')?.textContent
      || document.querySelector('meta[property="og:title"]')?.content
      || document.title
      || 'The Press';
    const title = collapseWhitespace(headline.replace(/\s+[—-]\s+The Press.*$/i, '')) || 'The Press';
    const description = collapseWhitespace(document.querySelector('meta[name="description"]')?.content || '');
    const url = getCleanShareUrl();
    return {
      type,
      title: type === 'site' ? 'The Press' : title,
      text: description || (type === 'site' ? 'AI powered news from The Press.' : title),
      url,
      imageUrl: getShareImageUrl(),
      externalImageUrl: getShareImageUrl({ preferPublic: true }),
      returnUrl: window.location.href,
      ariaLabel: type === 'site' ? 'Share this page' : 'Share this article',
    };
  }

  function getCleanShareUrl() {
    const canonical = document.querySelector('link[rel="canonical"]')?.href;
    if (canonical) return canonical;
    const ogUrl = document.querySelector('meta[property="og:url"]')?.content
      || document.querySelector('meta[name="twitter:url"]')?.content;
    if (ogUrl) return ogUrl;
    const url = new URL(window.location.href);
    url.hash = '';
    url.search = '';
    return url.href;
  }

  function getShareImageUrl(options = {}) {
    const pageMetadataSelectors = [
      'meta[property="og:image"]',
      'meta[name="twitter:image"]',
    ];
    const visibleImageSelectors = [
      '.article-hero .hero-figure img',
      '.article-hero img',
      '.lead-panel.is-active img',
      '.story-card img',
    ];
    const imageSelectors = options.preferPublic
      ? [...pageMetadataSelectors, ...visibleImageSelectors]
      : [...visibleImageSelectors, ...pageMetadataSelectors];

    for (const selector of imageSelectors) {
      const node = document.querySelector(selector);
      const raw = node?.tagName === 'META'
        ? node.getAttribute('content')
        : node?.currentSrc || node?.getAttribute('src');
      const url = normalizeShareAssetUrl(raw, options);
      if (url) return url;
    }

    return '';
  }

  function normalizeShareAssetUrl(rawUrl, options = {}) {
    if (!rawUrl) return '';
    try {
      const parsed = new URL(rawUrl, window.location.href);
      const isPressLiveAsset = /(^|\.)thepress\.live$/i.test(parsed.hostname);
      const isLocalPreview = /^(localhost|127\.0\.0\.1|\[::1\])$/i.test(window.location.hostname);
      if (isPressLiveAsset && isLocalPreview && !options.preferPublic) {
        return new URL(`${parsed.pathname}${parsed.search}`, window.location.href).href;
      }
      return parsed.href;
    } catch (_) {
      return '';
    }
  }

  function buildShareRowMarkup(context) {
    const intent = buildShareIntents(context);
    return `
      <div class="share-row__buttons">
        <a class="share-btn share-btn--x" href="${escapeAttribute(intent.x)}" target="_blank" rel="noopener noreferrer" data-share-platform="x" data-share-target="${escapeAttribute(intent.x)}" aria-label="Share on X" title="X">${sharePlatformIcon('x')}<span class="sr-only">X</span></a>
        <a class="share-btn share-btn--facebook" href="${escapeAttribute(intent.facebook)}" target="_blank" rel="noopener noreferrer" data-share-platform="facebook" data-share-target="${escapeAttribute(intent.facebook)}" aria-label="Share on Facebook" title="Facebook">${sharePlatformIcon('facebook')}<span class="sr-only">Facebook</span></a>
        <a class="share-btn share-btn--whatsapp" href="${escapeAttribute(intent.whatsapp)}" target="_blank" rel="noopener noreferrer" data-share-platform="whatsapp" data-share-target="${escapeAttribute(intent.whatsapp)}" aria-label="Share on WhatsApp" title="WhatsApp">${sharePlatformIcon('whatsapp')}<span class="sr-only">WhatsApp</span></a>
        <a class="share-btn share-btn--reddit" href="${escapeAttribute(intent.reddit)}" target="_blank" rel="noopener noreferrer" data-share-platform="reddit" data-share-target="${escapeAttribute(intent.reddit)}" aria-label="Share on Reddit" title="Reddit">${sharePlatformIcon('reddit')}<span class="sr-only">Reddit</span></a>
        <a class="share-btn share-btn--discord" href="${escapeAttribute(intent.discord)}" target="_blank" rel="noopener noreferrer" data-share-platform="discord" data-share-target="${escapeAttribute(intent.discord)}" aria-label="Share on Discord" title="Discord">${sharePlatformIcon('discord')}<span class="sr-only">Discord</span></a>
        <button class="share-btn share-btn--copy" type="button" data-share-platform="copy" aria-label="Copy share link" title="Copy link">${sharePlatformIcon('copy')}<span class="sr-only">Copy link</span></button>
      </div>
      <p class="share-row__status" data-share-status aria-live="polite"></p>
    `;
  }

  function sharePlatformIcon(platform) {
    const icons = {
      x: '<svg viewBox="0 0 24 24" focusable="false"><path fill="currentColor" d="M18.24 2.25h3.31l-7.23 8.26 8.51 11.24h-6.66l-5.21-6.82-5.97 6.82H1.68l7.73-8.84L1.25 2.25h6.83l4.71 6.23 5.45-6.23Zm-1.16 17.52h1.84L7.08 4.13H5.12l11.96 15.64Z"/></svg>',
      facebook: '<svg viewBox="0 0 24 24" focusable="false"><path fill="currentColor" d="M14 8h3V4h-3c-3.1 0-5 1.9-5 5v3H6v4h3v6h4v-6h3.1l.9-4h-4V9c0-.6.4-1 1-1Z"/></svg>',
      whatsapp: '<svg viewBox="0 0 24 24" focusable="false"><path d="M20.5 11.8a8.3 8.3 0 0 1-12.3 7.3L4 20.3l1.3-4A8.3 8.3 0 1 1 20.5 11.8Z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path fill="currentColor" d="M8.9 7.6c.3-.3.7-.3 1 0l1 1.4c.2.3.2.6 0 .9l-.5.7c.7 1.4 1.8 2.4 3.2 3.1l.7-.5c.3-.2.7-.2.9 0l1.4 1c.3.2.4.7.1 1-.4.6-1.1 1-1.9.9-3.4-.3-6.4-3.3-6.8-6.7-.1-.8.3-1.5.9-1.8Z"/></svg>',
      reddit: '<svg viewBox="0 0 24 24" focusable="false"><path d="M18.8 10.2c.9 0 1.7.7 1.7 1.7 0 .6-.3 1.1-.8 1.4.1.4.2.7.2 1.1 0 2.8-3.5 5.1-7.9 5.1s-7.9-2.3-7.9-5.1c0-.4.1-.8.2-1.1-.5-.3-.8-.8-.8-1.4 0-.9.8-1.7 1.7-1.7.5 0 .9.2 1.2.5 1.3-.8 3.1-1.3 5-1.4l.9-4.2 3 .7c.2-.6.8-1.1 1.5-1.1.9 0 1.6.7 1.6 1.6S17.7 8 16.8 8c-.6 0-1.1-.3-1.4-.8l-2.1-.5-.6 2.7c1.9.1 3.6.6 4.9 1.4.3-.4.7-.6 1.2-.6Z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><circle cx="9.2" cy="13.8" r="1" fill="currentColor"/><circle cx="14.8" cy="13.8" r="1" fill="currentColor"/><path d="M9.5 16.4c1.3.8 3.7.8 5 0" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>',
      sms: '<svg viewBox="0 0 24 24" focusable="false"><path d="M5 5.5h14a2.5 2.5 0 0 1 2.5 2.5v6.6a2.5 2.5 0 0 1-2.5 2.5h-5.8L8.7 20v-2.9H5a2.5 2.5 0 0 1-2.5-2.5V8A2.5 2.5 0 0 1 5 5.5Z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M7 10h10M7 13.5h6.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
      messenger: '<svg viewBox="0 0 24 24" focusable="false"><path d="M12 4C7.3 4 3.7 7.3 3.7 11.6c0 2.3 1 4.3 2.7 5.7v2.8l2.6-1.4c.9.3 1.9.5 3 .5 4.7 0 8.3-3.3 8.3-7.6S16.7 4 12 4Z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path fill="currentColor" d="m7.6 14 3.3-3.5 2.3 2.2 3.5-3.8-3.3 5.2-2.4-2.2L7.6 14Z"/></svg>',
      discord: '<svg viewBox="0 0 24 24" focusable="false"><path d="M7.4 7.9c2.9-1.1 6.3-1.1 9.2 0l1.1 7.4c-1.7 1.4-3.5 2.1-5.7 2.1s-4-.7-5.7-2.1l1.1-7.4Z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><circle cx="9.9" cy="12.2" r="1.1" fill="currentColor"/><circle cx="14.1" cy="12.2" r="1.1" fill="currentColor"/><path d="M10 15c1.2.6 2.8.6 4 0" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>',
      copy: '<svg viewBox="0 0 24 24" focusable="false"><rect x="8" y="8" width="10" height="10" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M6 16H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v1" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
    };
    return `<span class="share-btn__icon" aria-hidden="true">${icons[platform] || icons.copy}</span>`;
  }

  function buildShareIntents(context) {
    const encodedUrl = encodeURIComponent(context.url);
    const encodedTitle = encodeURIComponent(context.title);
    const encodedText = encodeURIComponent(`${context.title} ${context.url}`);
    return {
      x: `https://twitter.com/intent/tweet?text=${encodedTitle}&url=${encodedUrl}`,
      facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`,
      whatsapp: `https://api.whatsapp.com/send?text=${encodedText}`,
      reddit: `https://www.reddit.com/submit?url=${encodedUrl}&title=${encodedTitle}`,
      discord: 'https://discord.com/channels/@me',
    };
  }

  function bindShareRow(row, context) {
    row.querySelectorAll('[data-share-platform]').forEach((control) => {
      control.addEventListener('click', async (event) => {
        if (event.defaultPrevented || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) return;
        if (control.dataset.sharePlatform === 'copy') {
          event.preventDefault();
          const copied = await copyShareText(context);
          if (copied) {
            clearManualCopyText(row);
            setShareStatus(row, 'Link copied');
          } else {
            showManualCopyText(row, context);
            setShareStatus(row, 'Link selected. Press Ctrl+C or Command+C to copy.');
          }
          return;
        }
        if (control.matches('a[href]')) {
          const platform = control.dataset.sharePlatform;
          const label = getSharePlatformLabel(platform);
          let copiedForDiscord = false;
          if (platform === 'discord') {
            copiedForDiscord = copyShareTextImmediately(context);
          }
          const opened = openShareWindow(control.href);
          if (opened) event.preventDefault();
          if (platform === 'discord') {
            const openingMessage = opened ? 'Discord opened in a new tab' : 'If nothing opened, this browser blocked the new tab.';
            const copiedMessage = copiedForDiscord ? `Link copied. ${openingMessage}` : openingMessage;
            setShareStatus(row, copiedMessage);
            copyShareText(context).then((asyncCopied) => {
              setShareStatus(row, asyncCopied || copiedForDiscord ? `Link copied. ${openingMessage}` : openingMessage);
            });
            return;
          }
          setShareStatus(row, opened ? `Opening ${label} in a new tab` : 'If nothing opened, this browser blocked the new tab.');
        }
      });
    });
  }

  function getSharePlatformLabel(platform) {
    const labels = {
      x: 'X',
      facebook: 'Facebook',
      whatsapp: 'WhatsApp',
      reddit: 'Reddit',
      discord: 'Discord',
    };
    return labels[platform] || 'share';
  }

  function openShareWindow(url) {
    try {
      const shareWindow = window.open('', '_blank');
      if (!shareWindow) return false;
      shareWindow.opener = null;
      shareWindow.location.href = url;
      return true;
    } catch (_) {
      return false;
    }
  }

  async function handleSmsShare(row, control, context) {
    const isPhone = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
    if (isPhone && control.href) {
      window.location.href = control.href;
      return;
    }
    const copied = await copyShareText(context);
    setShareStatus(row, copied ? 'Message text copied' : 'Message text ready to copy');
  }

  async function copyShareText(context) {
    const text = getShareCopyText(context);
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(text);
      } else {
        fallbackCopyText(text);
      }
      return true;
    } catch (_) {
      try {
        fallbackCopyText(text);
        return true;
      } catch (__) {
        // Some browsers block clipboard writes on local pages; the platform still opens.
      }
    }
    return false;
  }

  function copyShareTextImmediately(context) {
    const text = getShareCopyText(context);
    let copied = false;
    try {
      fallbackCopyText(text);
      copied = true;
    } catch (_) {}
    if (navigator.clipboard?.writeText) {
      navigator.clipboard.writeText(text).catch(() => {});
    }
    return copied;
  }

  function getShareCopyText(context) {
    return context.url;
  }

  function setShareStatus(row, message) {
    const status = row.querySelector('[data-share-status]');
    if (!status) return;
    status.textContent = message;
    status.classList.add('is-visible');
    clearTimeout(status._pressTimer);
    status._pressTimer = setTimeout(() => {
      status.classList.remove('is-visible');
      status.textContent = '';
    }, 3200);
  }

  function showManualCopyText(row, context) {
    clearManualCopyText(row);
    const input = document.createElement('input');
    input.className = 'share-row__manual-copy';
    input.type = 'text';
    input.readOnly = true;
    input.value = getShareCopyText(context);
    input.setAttribute('aria-label', 'Selected share text');
    row.appendChild(input);
    input.focus({ preventScroll: true });
    input.select();
    input.setSelectionRange(0, input.value.length);
  }

  function clearManualCopyText(row) {
    row.querySelectorAll('.share-row__manual-copy').forEach((node) => node.remove());
  }

  function fallbackCopyText(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.setAttribute('readonly', '');
    textarea.style.position = 'fixed';
    textarea.style.top = '0';
    textarea.style.left = '-9999px';
    document.body.appendChild(textarea);
    textarea.focus({ preventScroll: true });
    textarea.select();
    textarea.setSelectionRange(0, textarea.value.length);
    const copied = document.execCommand('copy');
    textarea.remove();
    if (!copied) throw new Error('Copy command rejected');
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

function pressNormalizeRotationUrl(value) {
  return String(value || '')
    .trim()
    .replace(/^https?:\/\/[^/]+\//i, '')
    .replace(/^\.\//, '')
    .replace(/[?#].*$/, '');
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
  return AUTHOR_LABEL;
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

    if (window.PressHeroStandard?.layoutLeadNav) {
      window.PressHeroStandard.layoutLeadNav();
    } else {
      pressLayoutLeadNav();
    }
  };

  leadButtons.forEach((btn) => {
    if (btn.dataset.pressLeadBound === 'true') return;
    btn.dataset.pressLeadBound = 'true';
    btn.addEventListener('click', () => setLead(btn.dataset.target));
  });

  const chosenButton = leadButtons.find((button) => button.classList.contains('is-active')) || leadButtons[0];
  if (chosenButton) setLead(chosenButton.dataset.target);
}

function pressLayoutLeadNav(navBox = document.querySelector('.lead-nav')) {
  if (!navBox) return;

  const buttons = Array.from(navBox.querySelectorAll('[data-lead-button]'));
  const sideButtons = buttons.filter((button) => !button.classList.contains('is-active')).slice(0, 6);
  const slots = ['left-1', 'left-2', 'left-3', 'right-1', 'right-2', 'right-3'];

  buttons.forEach((button) => {
    button.removeAttribute('data-side-slot');
  });

  sideButtons.forEach((button, index) => {
    button.setAttribute('data-side-slot', slots[index]);
  });

  navBox.dataset.sideLayout = 'split';
}

function pressShuffleArray(items) {
  return Array.isArray(items) ? items.slice() : [];
}

function pressRotateFromLastHero(source) {
  const candidates = Array.isArray(source) ? source.slice() : [];
  if (candidates.length < 2) return candidates;

  let previousUrl = '';
  try {
    previousUrl = sessionStorage.getItem('press-future-newsroom-hero-url') || '';
  } catch (_) {}

  const previousKey = pressNormalizeRotationUrl(previousUrl);
  const previousIndex = previousKey
    ? candidates.findIndex((story) => pressNormalizeRotationUrl(story && story.url) === previousKey)
    : -1;
  const startIndex = previousIndex >= 0 ? (previousIndex + 1) % candidates.length : 0;

  return candidates.slice(startIndex).concat(candidates.slice(0, startIndex));
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

function pressRenderLeadNavThumb(story) {
  if (story?.image) {
    return `
      <span class="lead-nav__thumb" aria-hidden="true">
        <img src="${pressEscapeAttribute(story.image)}" alt="" loading="lazy" decoding="async" />
      </span>
    `;
  }

  return `
    <span class="lead-nav__thumb lead-nav__thumb--fallback" aria-hidden="true">
      <span>${pressEscapeHtml(story?.section || 'Story')}</span>
    </span>
  `;
}

function pressRenderHomepageLeadStories(stories) {
  const panelBox = document.querySelector('.lead-switcher__panels');
  const navBox = document.querySelector('.lead-nav');

  if (!panelBox || !navBox || !stories.length) return;

  panelBox.innerHTML = stories.map((story, index) => pressRenderLeadPanel(story, index)).join('');
  navBox.innerHTML = stories.map((story, index) => `
    <button class="lead-nav__button${index === 0 ? ' is-active' : ''}" type="button" data-lead-button data-target="lead-${index}" aria-pressed="${String(index === 0)}">
      ${pressRenderLeadNavThumb(story)}
      <span class="lead-nav__kicker">${pressEscapeHtml(story.section || 'Front Page')}</span>
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
  const leadSource = leadPool.length ? leadPool : recent;
  const heroCount = window.PressHeroStandard?.heroSlotCount || 7;
  const leadStories = pressPickStorySet(
    pressRotateFromLastHero(leadSource),
    heroCount,
    used,
    true
  );

  pressRenderHomepageLeadStories(leadStories);

  pressRenderHomepageSecondaryStories(
    pressPickStorySet(recent.filter((story) => !used.has(story.url)), 4, used, true)
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
    if (/^(?:By\s+)?The Press\b/i.test(text) || el.querySelector('a[href*="#the-press"]')) {
      el.textContent = text.replace(/^(?:By\s+)?(?:The Press(?:\s+Staff)?|Intelligent AI|Written and Researched by AI)(?=\s*[•·]|\s*$)/i, "By The Press");
      return;
    }

    if (text.startsWith("By ")) {
      el.textContent = text.replace(/^By\s+[^•]+/, "By The Press");
    } else if (/^(?:Intelligent AI|Written and Researched by AI)\b/i.test(text)) {
      el.textContent = text.replace(/^(?:Intelligent AI|Written and Researched by AI)\b/i, "By The Press");
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

  const PRESS_AUTHOR = 'By The Press';
  const CACHE_PREFIX = 'press-ecosystem-cache:';
  const MODE_KEY = 'press-reader-mode';
  const FRESH_HOURS = 72;
  const LIVE_DAYS = 14;
  const HERO_TARGET = 7;
  const HERO_AUTO_SEED = 2;
  const HERO_ROTATION_KEY = 'press-future-newsroom-hero-url';
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

      window.dispatchEvent(new CustomEvent('press:ecosystem-ready', { detail: state }));
    }).catch((error) => {
      document.documentElement.classList.remove('press-ecosystem-booting');
      console.warn('[The Press] Ecosystem engine could not initialize:', error);
    });
  });

  function loadEcosystem() {
    if (ecosystemPromise) return ecosystemPromise;

    ecosystemPromise = (async () => {
      const [placementsRaw, liveRaw, contentRaw, dailyRaw, editionRaw, searchRaw, embeddedRaw] = await Promise.all([
        fetchOptionalJson(FETCH_TARGETS.placements),
        fetchOptionalJson(FETCH_TARGETS.live),
        fetchOptionalJson(FETCH_TARGETS.content),
        fetchOptionalJson(FETCH_TARGETS.daily),
        fetchOptionalJson(FETCH_TARGETS.edition),
        fetchOptionalJson(FETCH_TARGETS.search),
        Promise.resolve(readEmbeddedSearchJson()),
      ]);

      const sourceStories = mergeStories([
        extractStories(contentRaw, 'content-index'),
        extractStories(liveRaw, 'live-index'),
        extractStories(dailyRaw, 'daily-latest'),
        extractStories(editionRaw, 'edition'),
        extractStories(searchRaw, 'search-index'),
        extractStories(embeddedRaw, 'embedded-search'),
      ]);

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
      const response = await fetch(pressSiteAssetUrl(url), { cache: 'no-store' });
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
    const byline = PRESS_AUTHOR;

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
      byline,
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

    const heroTarget = Math.max(7, Number(placementFile?.home?.hero_slots || placementFile?.home?.heroSlots || HERO_TARGET) || HERO_TARGET);
    const resolvedHero = resolvePlacementList(placementFile?.home?.hero, byId, heroTarget)
      .filter(Boolean);
    const hasManualHero = resolvedHero.length > 0;
    const autoHero = hasManualHero ? [] : pickStories(clusterFresh.filter((story) => story.heroEligible && story.image), Math.min(HERO_AUTO_SEED, heroTarget), {
      usedClusters: new Set(),
      usedUrls: new Set(),
      uniqueSections: false,
    });
    const heroUsedClusters = new Set(autoHero.map((story) => story.clusterId));
    const heroUsedUrls = new Set(autoHero.map((story) => story.url));
    resolvedHero.forEach((story) => remember(story, heroUsedClusters, heroUsedUrls));
    const heroBase = resolvedHero
      .concat(autoHero)
      .concat(pickStories(clusterFresh.filter((story) => story.heroEligible && story.image), heroTarget - autoHero.length - resolvedHero.length, {
        usedClusters: heroUsedClusters,
        usedUrls: heroUsedUrls,
        uniqueSections: true,
      }))
      .concat(pickStories(clusterFresh, heroTarget, {
        usedClusters: heroUsedClusters,
        usedUrls: heroUsedUrls,
        uniqueSections: true,
      }))
      .slice(0, heroTarget);
    const hero = rotateHeroListFromStoredHero(heroBase);

    hero.forEach((story) => remember(story, usedClusters, usedUrls));

    const secondaryTarget = 4;
    const secondary = resolvePlacementList(placementFile?.home?.secondary, byId, secondaryTarget).slice(0, secondaryTarget);
    const secondaryFinal = secondary.slice();

    secondaryFinal.forEach((story) => remember(story, usedClusters, usedUrls));

    if (secondaryFinal.length < secondaryTarget) {
      secondaryFinal.push(...pickStories(clusterFresh, secondaryTarget - secondaryFinal.length, {
          usedClusters,
          usedUrls,
          uniqueSections: true,
        }));
    }

    const latestPool = uniqueByCluster(all);
    const latest = latestPool.slice(0, 15);
    const heroUrls = new Set(hero.map((story) => story.url));
    const recencyTicker = latestPool.filter((story) => !heroUrls.has(story.url)).slice(0, 15);
    const daily = all.filter((story) => story.isDaily).slice(0, 15);
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
      recencyTicker,
      daily: daily.length >= 5 ? daily : latest.slice(0, 15),
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

  function rotateHeroListFromStoredHero(stories) {
    const items = uniqueByUrl(Array.isArray(stories) ? stories : []);
    if (items.length < 2) return items;

    let previousUrl = '';
    try {
      previousUrl = sessionStorage.getItem(HERO_ROTATION_KEY) || '';
    } catch (_) {}

    const previousKey = normalizeUrlKey(previousUrl);
    const previousIndex = previousKey
      ? items.findIndex((story) => normalizeUrlKey(story.url) === previousKey)
      : -1;

    if (previousIndex < 0) return items;

    return items.slice(previousIndex + 1).concat(items.slice(0, previousIndex + 1));
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

    removeHomepagePulsePanels();
    updateHomeIntro(model);
    renderHero(model.hero);
    renderSecondary(model.recencyTicker || model.latest, model.hero);
    renderDailySection(model.daily);
    renderLatestRiver(model.latest);
    renderDeskDirectory(model.all);
  }

  function removeHomepagePulsePanels() {
    if (!document.body.classList.contains('page-home')) return;

    document.querySelectorAll([
      '.press-living-home',
      '[data-living-home-pulse]',
      '.desk-pulse',
      '.press-catchup',
      '.press-future-studio',
      '.press-topic-radar'
    ].join(',')).forEach((node) => {
      node.remove();
    });
  }

  function updateHomeIntro(model) {
    const intro = document.querySelector('.home-hero__intro');
    if (!intro) return;

    intro.querySelectorAll(':scope > .eyebrow, :scope > h1, :scope > .section-copy').forEach((node) => {
      node.remove();
    });
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
    rememberVisibleHero(stories[0]);

    panelBox.innerHTML = stories.map((story, index) => leadPanel(story, index)).join('');

    navBox.innerHTML = stories.map((story, index) => `
      <button aria-pressed="${index === 0}" class="lead-nav__button${index === 0 ? ' is-active' : ''}" data-lead-button data-target="lead-${index}" type="button">
        ${leadNavThumbnail(story)}
        <span class="lead-nav__kicker">${escapeHtml(story.section)}</span>
        <strong>${escapeHtml(story.title)}</strong>
      </button>
    `).join('');

    bindLeadSwitcher(navBox, panelBox);
  }

  function rememberVisibleHero(story) {
    if (!story?.url) return;
    try {
      sessionStorage.setItem(HERO_ROTATION_KEY, story.url);
    } catch (_) {}
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

  function leadNavThumbnail(story) {
    if (story?.image) {
      return `
        <span class="lead-nav__thumb" aria-hidden="true">
          <img src="${escapeAttr(story.image)}" alt="" loading="lazy" decoding="async" />
        </span>
      `;
    }

    return `
      <span class="lead-nav__thumb lead-nav__thumb--fallback" aria-hidden="true">
        <span>${escapeHtml(story?.section || 'Story')}</span>
      </span>
    `;
  }

  function layoutLeadSideSlots(navBox) {
    if (!navBox) return;

    if (window.PressHeroStandard?.layoutLeadNav) {
      window.PressHeroStandard.layoutLeadNav(navBox);
      return;
    }

    const buttons = Array.from(navBox.querySelectorAll('[data-lead-button]'));
    const sideButtons = buttons.filter((button) => !button.classList.contains('is-active')).slice(0, 6);
    const slots = ['left-1', 'left-2', 'left-3', 'right-1', 'right-2', 'right-3'];

    buttons.forEach((button) => {
      button.removeAttribute('data-side-slot');
    });

    sideButtons.forEach((button, index) => {
      button.setAttribute('data-side-slot', slots[index]);
    });
  }

  function bindLeadSwitcher(navBox, panelBox) {
    layoutLeadSideSlots(navBox);

    if (typeof pressLayoutLeadNav === 'function') {
      pressLayoutLeadNav(navBox);
    }

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

        layoutLeadSideSlots(navBox);

        if (typeof pressLayoutLeadNav === 'function') {
          pressLayoutLeadNav(navBox);
        }
      });
    });
  }

  function recencyTickerCard(story, duplicate = false) {
    const tabAttr = duplicate ? ' tabindex="-1"' : '';
    const imageHtml = story.image ? `
      <span class="home-recency-card__media">
        <img alt="${escapeAttr(story.imageAlt || story.title)}" decoding="async" loading="lazy" src="${escapeAttr(story.image)}" />
      </span>
    ` : '<span class="home-recency-card__media home-recency-card__media--empty"></span>';

    return `
      <a class="home-recency-card" href="${escapeAttr(story.url)}" aria-label="${escapeAttr(story.title)}"${tabAttr}>
        ${imageHtml}
        <span class="home-recency-card__body">
          <span class="home-recency-card__kicker">${escapeHtml(story.section)} • ${escapeHtml(story.type)}</span>
          <strong>${escapeHtml(story.title)}</strong>
          <span class="home-recency-card__meta">${escapeHtml(story.published || freshnessLabel(story))}</span>
        </span>
      </a>
    `;
  }

  function removeHeroStories(stories, heroStories, limit = 15) {
    if (!Array.isArray(stories)) return [];
    const heroUrls = new Set((heroStories || []).map((story) => story?.url).filter(Boolean));
    return stories.filter((story) => !heroUrls.has(story.url)).slice(0, limit);
  }

  function renderSecondary(stories, heroStories = []) {
    const ticker = document.querySelector('[data-home-recency-ticker]');
    const latest = removeHeroStories(stories, heroStories);

    if (ticker && latest.length) {
      const duration = Math.max(86, Math.min(150, latest.length * 8));
      ticker.style.setProperty('--home-recency-duration', `${duration}s`);
      ticker.innerHTML = `
        <div class="home-recency-ticker__track">
          <div class="home-recency-ticker__set">
            ${latest.map((story) => recencyTickerCard(story)).join('')}
          </div>
          <div class="home-recency-ticker__set" aria-hidden="true">
            ${latest.map((story) => recencyTickerCard(story, true)).join('')}
          </div>
        </div>
      `;
      bindImageFallbacks(ticker);
      return;
    }

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

    const grid = document.querySelector('.page-section .cards-grid--archive, .page-section .cards-grid');

    if (!grid) return;

    grid.innerHTML = uniqueByCluster(matches)
      .slice(0, 36)
      .map((story) => storyCard(story, {
        archive: true,
        reason: `Newest ${titleForSlug(sectionSlug)} story.`,
      }))
      .join('');
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
    const topbar = document.querySelector('.topbar__actions');

    if (!topbar) {
      setMode('standard');
      try {
        localStorage.removeItem(MODE_KEY);
      } catch (_) {}
      return;
    }

    applyStoredMode();

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
    const parts = [story?.byline || PRESS_AUTHOR];

    if (story.published) parts.push(story.published);

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

  const AUTHOR_LABEL = 'By The Press';

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

    const requestUrl = pressSiteAssetUrl(url);
    const cacheBuster = `${requestUrl}${requestUrl.includes('?') ? '&' : '?'}restore=${Date.now()}`;

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

    window.setTimeout(restoreCategoryArticles, 120);

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
    root.classList.add('press-page-ready');
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
    return;
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

/* PRESS_CATEGORYLESS_START */
(() => {
  const SECTION_HREF = /^section-[^/?#]+\.html(?:[?#].*)?$/i;

  function looksLikeSectionLink(anchor) {
    const raw = (anchor.getAttribute('href') || '').trim();
    if (SECTION_HREF.test(raw)) return true;
    try {
      const url = new URL(anchor.href, window.location.href);
      return SECTION_HREF.test(url.pathname.split('/').pop() || '');
    } catch (_) {
      return false;
    }
  }

  function removeAccidentalOpenGraphText(root = document.documentElement) {
    if (!root || !document.createTreeWalker) return;
    const doomed = [];
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    let node = walker.nextNode();
    while (node) {
      const text = node.nodeValue || '';
      if (/open\s*graph/i.test(text) && /(<!--|&lt;|\\!--)/i.test(text)) {
        doomed.push(node);
      }
      node = walker.nextNode();
    }
    doomed.forEach((nodeToRemove) => nodeToRemove.remove());
  }

  function removeFooterSectionLists() {
    document.querySelectorAll('.site-footer section').forEach((section) => {
      const heading = section.querySelector('.footer-heading');
      if (!heading) return;
      if (/^sections$/i.test((heading.textContent || '').trim())) {
        section.remove();
      }
    });
  }

  function rerouteSectionLinksToArchive() {
    document.querySelectorAll('a[href]').forEach((anchor) => {
      if (!looksLikeSectionLink(anchor)) return;
      anchor.setAttribute('href', 'archive.html');
      if (/^\s*More\s+/i.test(anchor.textContent || '')) {
        anchor.textContent = 'Open archive';
      }
      anchor.removeAttribute('aria-current');
    });
  }

  function removeCategorySurfaces() {
    document.documentElement.classList.add('press-categoryless');
    removeAccidentalOpenGraphText();
    document.querySelectorAll('.section-nav, [data-menu-toggle], .menu-trigger, .desk-directory, .desk-pulse').forEach((node) => node.remove());
    removeFooterSectionLists();
    rerouteSectionLinksToArchive();
  }

  function bootCategorylessMode() {
    removeCategorySurfaces();
    let queued = false;
    const scheduleCleanup = () => {
      if (queued) return;
      queued = true;
      window.requestAnimationFrame(() => {
        queued = false;
        removeCategorySurfaces();
      });
    };
    const target = document.body || document.documentElement;
    if (target && window.MutationObserver) {
      const observer = new MutationObserver(scheduleCleanup);
      observer.observe(target, { childList: true, subtree: true });
    }
    window.requestAnimationFrame(removeCategorySurfaces);
    window.setTimeout(removeCategorySurfaces, 120);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bootCategorylessMode, { once: true });
  } else {
    bootCategorylessMode();
  }
})();
/* PRESS_CATEGORYLESS_END */


/* NEWS_FLOW_UI_IMPROVEMENT_REFRESH_FIX
   Stabilize refresh/render behavior on the home, press, and archive views.
   - Clear stale page-leaving classes after browser bfcache restores.
   - Pick a different active lead panel on reload when the markup includes lead panels.
*/
(function pressNewsFlowUiRefreshFix() {
  const storageKey = 'press:last-active-lead-panel';

  function clearTransitionState() {
    document.documentElement.classList.add('press-page-ready');
    document.documentElement.classList.remove('press-page-leaving');
    document.body.classList.remove('press-page-leaving');
  }

  function syncActiveLeadPanel() {
    const panels = Array.from(document.querySelectorAll('[data-press-lead-panel], .lead-panel, .daily-lead-panel'));
    if (panels.length < 2) return;

    const candidates = panels.map((panel, index) => ({
      panel,
      id: panel.getAttribute('data-slug') || panel.getAttribute('data-panel-id') || panel.id || String(index)
    }));

    const chosen = candidates.find((item) => item.panel.classList.contains('is-active')) || candidates[0];
    if (!chosen) return;

    candidates.forEach((item) => {
      const active = item === chosen;
      item.panel.classList.toggle('is-active', active);
      item.panel.toggleAttribute('hidden', !active && item.panel.hasAttribute('data-press-lead-panel'));
    });

    document.querySelectorAll('[data-press-lead-trigger], .lead-panel-trigger').forEach((button) => {
      const target = button.getAttribute('data-slug') || button.getAttribute('data-panel-id') || button.getAttribute('aria-controls') || '';
      const active = target && target === chosen.id;
      button.classList.toggle('is-active', active);
      button.setAttribute('aria-pressed', active ? 'true' : 'false');
    });

    sessionStorage.setItem(storageKey, chosen.id);
  }

  function run() {
    clearTransitionState();
    syncActiveLeadPanel();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run, { once: true });
  } else {
    run();
  }
  window.addEventListener('pageshow', run);
  window.addEventListener('load', run);
})();

/* PRESS_FUTURE_NEWSROOM_START
   A progressive "living newsroom" layer for the static front page.
   It adds a cinematic live deck, topic radar, and command-palette search.
*/
(function pressFutureNewsroom() {
  'use strict';

  const DATA_URLS = [
    'content-index.json',
    'live-index.json',
    'daily-latest.json',
    'search-index.json',
    'edition.json'
  ];

  const SECTION_COLORS = {
    Politics: '#ff665c',
    Culture: '#f6c85f',
    Technology: '#5dd6ff',
    Economics: '#73e2a7',
    Education: '#b38cff',
    Health: '#ff8fb3',
    Philosophy: '#f4f0e8',
    Science: '#9bf06d',
    World: '#7aa2ff',
    Opinion: '#ffb86b',
    AI: '#68f4d4',
    Film: '#f08cff',
    Geopolitics: '#8fb4ff',
    Niche: '#ffd36e',
    'Pop Culture': '#ff7fbf'
  };

  const HERO_STORAGE_KEY = 'press-future-newsroom-hero-url';

  const STOP_WORDS = new Set([
    'the', 'and', 'for', 'that', 'with', 'from', 'this', 'into', 'over', 'under', 'after', 'before', 'will',
    'have', 'has', 'are', 'was', 'were', 'not', 'now', 'new', 'why', 'how', 'what', 'when', 'where', 'who',
    'its', 'their', 'they', 'them', 'than', 'then', 'still', 'about', 'could', 'would', 'should', 'your',
    'our', 'out', 'off', 'more', 'less', 'again', 'only', 'most', 'just', 'can'
  ]);

  let futureState = null;
  let commandOpen = false;
  let activeFilter = 'All';
  let selectedIndex = 0;
  let currentRefreshHeroUrl = '';

  function ready(callback) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', callback, { once: true });
    } else {
      callback();
    }
  }

  ready(function initFutureNewsroom() {
    document.documentElement.classList.add('press-future-newsroom');
    installCommandPalette();
    bindGlobalCommands();

    hydrate().then(function onHydrated(state) {
      if (!state.stories.length) return;
      futureState = state;
      renderFutureHomepage(state);
      renderCommandResults('');
      document.documentElement.classList.add('press-future-ready');
    }).catch(function onError(error) {
      console.warn('[The Press] Future newsroom layer could not initialize:', error);
    });

    window.addEventListener('press:ecosystem-ready', function onEcosystemReady(event) {
      const stories = event.detail?.model?.all || event.detail?.stories || [];
      if (!Array.isArray(stories) || !stories.length) return;
      futureState = buildState(stories.map(normalizeStory).filter(Boolean));
      renderFutureHomepage(futureState);
      renderCommandResults('');
      document.documentElement.classList.add('press-future-ready');
    });
  });

  async function hydrate() {
    const payloads = await Promise.all(DATA_URLS.map(fetchOptionalJson));
    const embedded = readEmbeddedSearchJson();
    const stories = mergeStories(payloads.concat([embedded]).flatMap(extractStories));
    return buildState(stories);
  }

  async function fetchOptionalJson(url) {
    try {
      const response = await fetch(pressSiteAssetUrl(url), { cache: 'no-store' });
      if (!response.ok) return null;
      return response.json();
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

  function extractStories(payload) {
    if (!payload) return [];
    if (Array.isArray(payload)) return payload.map(normalizeStory).filter(Boolean);
    if (Array.isArray(payload.stories)) return payload.stories.map(normalizeStory).filter(Boolean);
    if (Array.isArray(payload.articles)) return payload.articles.map(normalizeStory).filter(Boolean);
    if (Array.isArray(payload.items)) return payload.items.map(normalizeStory).filter(Boolean);
    return [];
  }

  function normalizeStory(item) {
    if (!item || typeof item !== 'object') return null;

    const title = clean(item.title || item.headline || item.name);
    const url = clean(item.url || item.href || item.link || item.filename || item.permalink);
    if (!title || !url || url === '#') return null;

    const section = titleCase(clean(item.section || item.desk || item.category || inferSection(url) || 'News'));
    const type = clean(item.type || item.kind || item.story_type || (url.includes('/daily/') || url.startsWith('daily/') ? 'Daily Issue' : 'Report'));
    const dek = clean(item.dek || item.summary || item.description || item.excerpt);
    const published = clean(item.published || item.publishedLabel || item.displayDate || item.date);
    const publishedIso = clean(item.publishedIso || item.published_iso || item.publishedAt || item.published_at);
    const image = clean(item.image || item.imageUrl || item.image_url || item.thumbnail || item.photo);
    const imageAlt = clean(item.imageAlt || item.image_alt || item.thumbnail_alt || item.thumbnailAlt || item.alt || title);
    const keywords = Array.isArray(item.keywords) ? item.keywords.filter(Boolean).map(String) : [];
    const sortValue = parseStoryDate(publishedIso || published || url);

    return {
      title,
      url: normalizeUrl(url),
      section,
      sectionSlug: slugify(section),
      type,
      dek,
      published,
      publishedIso,
      image: normalizeUrl(image),
      imageAlt,
      keywords,
      sortValue,
      clusterId: clean(item.cluster_id || item.clusterId || item.story_id || item.storyId || slugify(title)),
      readTime: clean(item.read_time || item.readTime),
      scoreText: [title, section, type, dek, keywords.join(' ')].join(' ').toLowerCase()
    };
  }

  function mergeStories(stories) {
    const byUrl = new Map();
    stories.filter(Boolean).forEach(function remember(story) {
      const key = normalizeUrl(story.url).replace(/^\.\//, '');
      const previous = byUrl.get(key);
      if (!previous) {
        byUrl.set(key, story);
        return;
      }

      byUrl.set(key, {
        ...previous,
        ...story,
        dek: story.dek && story.dek.length > (previous.dek || '').length ? story.dek : previous.dek,
        image: story.image || previous.image,
        imageAlt: story.imageAlt || previous.imageAlt,
        keywords: Array.from(new Set([...(previous.keywords || []), ...(story.keywords || [])])),
        sortValue: Math.max(previous.sortValue || 0, story.sortValue || 0)
      });
    });

    return Array.from(byUrl.values()).sort(function byFreshness(a, b) {
      return (b.sortValue || 0) - (a.sortValue || 0) || a.title.localeCompare(b.title);
    });
  }

  function buildState(stories) {
    const latest = stories.slice(0, 36);
    const hero = pickRefreshHero(latest, stories);
    const bySection = new Map();
    const keywordCounts = new Map();

    stories.forEach(function collect(story) {
      const section = story.section || 'News';
      const bucket = bySection.get(section) || [];
      bucket.push(story);
      bySection.set(section, bucket);

      const terms = story.keywords.length ? story.keywords : extractTerms(story.title + ' ' + story.dek);
      terms.slice(0, 7).forEach(function countKeyword(term) {
        const key = titleCase(term).slice(0, 34);
        if (key.length < 3) return;
        keywordCounts.set(key, (keywordCounts.get(key) || 0) + 1);
      });
    });

    const topics = Array.from(bySection.entries()).map(function toTopic(entry) {
      const section = entry[0];
      const items = entry[1].sort(function byDate(a, b) { return (b.sortValue || 0) - (a.sortValue || 0); });
      return {
        section,
        color: SECTION_COLORS[section] || '#f4f0e8',
        count: items.length,
        latest: items[0],
        signal: topicSignal(items)
      };
    }).sort(function byCount(a, b) {
      return b.count - a.count || a.section.localeCompare(b.section);
    });

    const keywords = Array.from(keywordCounts.entries())
      .map(function toKeyword(entry) { return { label: entry[0], count: entry[1] }; })
      .sort(function byCount(a, b) { return b.count - a.count || a.label.localeCompare(b.label); })
      .slice(0, 12);

    return {
      stories,
      latest,
      hero,
      topics,
      keywords,
      storyCount: stories.length,
      deskCount: topics.length,
      latestLabel: hero ? (hero.published || formatDate(hero.sortValue)) : '',
      imageCount: stories.filter(function hasImage(story) { return story.image; }).length
    };
  }

  function pickRefreshHero(latest, stories) {
    const source = latest.length ? latest : stories;
    const imageCandidates = source.filter(function hasUsableImage(story) {
      return story && story.url && story.image;
    });
    const candidates = (imageCandidates.length >= 2 ? imageCandidates : source)
      .filter(function hasUrl(story) { return story && story.url; });

    if (!candidates.length) return source[0] || null;

    if (currentRefreshHeroUrl) {
      const alreadyChosen = candidates.find(function sameHero(story) {
        return story.url === currentRefreshHeroUrl;
      });
      if (alreadyChosen) return alreadyChosen;
    }

    const previousUrl = readSessionValue(HERO_STORAGE_KEY);
    const previousIndex = candidates.findIndex(function findPrevious(story) {
      return story.url === previousUrl;
    });
    const nextIndex = previousIndex >= 0 ? (previousIndex + 1) % candidates.length : 0;
    const hero = candidates[nextIndex] || candidates[0];

    return hero;
  }

  function readSessionValue(key) {
    try {
      return sessionStorage.getItem(key) || '';
    } catch (_) {
      return '';
    }
  }

  function writeSessionValue(key, value) {
    try {
      sessionStorage.setItem(key, value);
    } catch (_) {}
  }

  function renderFutureHomepage(state) {
    if (!document.body.classList.contains('page-home')) return;

    document.querySelectorAll([
      '.press-living-home',
      '[data-living-home-pulse]',
      '.desk-pulse',
      '.press-catchup',
      '.press-future-studio',
      '.press-topic-radar'
    ].join(',')).forEach(function removePanel(node) {
      node.remove();
    });
  }

  function renderStudioDeck(state) {
    const homeHero = document.querySelector('.home-hero');
    if (!homeHero || !state.hero) return;

    let deck = document.querySelector('.press-future-studio');
    if (!deck) {
      deck = document.createElement('section');
      deck.className = 'press-future-studio';
      deck.setAttribute('aria-label', 'Live newsroom command deck');
      homeHero.insertAdjacentElement('beforebegin', deck);
    }

    const hero = state.hero;
    const hot = state.latest.filter(function different(story) { return story.url !== hero.url; }).slice(0, 6);

    deck.innerHTML = `
      <div class="press-future-studio__inner">
        <article class="press-future-lead" data-story-url="${escapeAttr(hero.url)}">
          <div class="press-future-lead__body">
            <p class="press-future-kicker">Live editorial feature / ${escapeHtml(hero.section)} / ${escapeHtml(freshness(hero))}</p>
            <h2><a href="${escapeAttr(hero.url)}">${escapeHtml(hero.title)}</a></h2>
            <p class="press-future-lead__dek">${escapeHtml(shorten(hero.dek, 260))}</p>
            <div class="press-future-meta-row" aria-label="Edition metrics">
              <span>Rotates on refresh</span>
              <span>Thumbnail lead</span>
              <span>${escapeHtml(freshness(hero))}</span>
            </div>
            <div class="press-future-actions">
              <a class="button press-future-button" href="${escapeAttr(hero.url)}">Read lead</a>
              <button class="press-future-button press-future-button--ghost" type="button" data-future-command-open>Open command center</button>
            </div>
          </div>
          <a class="press-future-lead__media" href="${escapeAttr(hero.url)}">
            ${hero.image ? `<img alt="${escapeAttr(hero.imageAlt || hero.title)}" decoding="async" loading="eager" src="${escapeAttr(hero.image)}">` : `<span>${escapeHtml(hero.section)}</span>`}
          </a>
        </article>

        <aside class="press-signal-board" aria-label="Edition intelligence">
          <div class="press-signal-board__header">
            <p class="press-future-kicker">Edition intelligence</p>
            <h3>More stories in view</h3>
          </div>
          <div class="press-signal-board__visuals">
            ${hot.map(function railCard(story, index) {
              return `
                <a href="${escapeAttr(story.url)}" class="press-rail-card${index === 0 ? ' press-rail-card--feature' : ''}">
                  <span class="press-rail-card__media">
                    ${story.image ? `<img alt="${escapeAttr(story.imageAlt || story.title)}" decoding="async" loading="lazy" src="${escapeAttr(story.image)}">` : `<span>${escapeHtml(story.section)}</span>`}
                  </span>
                  <span class="press-rail-card__body">
                    <em>${escapeHtml(story.section)} / ${escapeHtml(freshness(story))}</em>
                    <strong>${escapeHtml(story.title)}</strong>
                  </span>
                </a>
              `;
            }).join('')}
          </div>
          <div class="press-signal-board__queue">
            <p class="press-signal-board__label">Next in the file</p>
            ${hot.slice(0, 3).map(function queueItem(story, index) {
              return `
                <a href="${escapeAttr(story.url)}" class="press-queue-item">
                  ${story.image ? `<img class="press-queue-item__thumb" alt="${escapeAttr(story.imageAlt || story.title)}" decoding="async" loading="lazy" src="${escapeAttr(story.image)}">` : `<span class="press-queue-item__number">${String(index + 1).padStart(2, '0')}</span>`}
                  <span class="press-queue-item__text">
                    <strong>${escapeHtml(story.title)}</strong>
                    <em>${escapeHtml(story.section)}</em>
                  </span>
                </a>
              `;
            }).join('')}
          </div>
        </aside>
      </div>
    `;
  }

  function renderTopicRadar(state) {
    const homeGrid = document.querySelector('.home-grid');
    const homeHero = document.querySelector('.home-hero');
    if (!homeHero && !homeGrid) return;

    let radar = document.querySelector('.press-topic-radar');
    if (!radar) {
      radar = document.createElement('section');
      radar.className = 'press-topic-radar';
      radar.setAttribute('aria-label', 'Topic radar');
      (homeGrid || homeHero).insertAdjacentElement('beforebegin', radar);
    }

    const topics = state.topics.slice(0, 10);
    const visualStories = state.latest
      .filter(function hasImage(story) { return story.image; })
      .concat(state.latest.filter(function noImage(story) { return !story.image; }))
      .slice(0, 18);

    radar.innerHTML = `
      <div class="press-topic-radar__inner">
        <div class="press-topic-radar__copy">
          <p class="press-future-kicker">Visual edition</p>
          <h2>See the stories, not just the sections.</h2>
          <p>Latest articles now lead with their thumbnails, with quiet desk shortcuts for jumping into the command center.</p>
          <div class="press-radar-keywords">
            ${topics.slice(0, 8).map(function topicButton(topic) {
              return `<button type="button" data-future-topic="${escapeAttr(topic.section)}">${escapeHtml(topic.section)} <span>${escapeHtml(topic.count)}</span></button>`;
            }).join('')}
          </div>
        </div>

        <div class="press-article-wall" aria-label="Latest article thumbnails">
          ${visualStories.map(function articleTile(story) {
            return `
              <article class="press-visual-story" data-section="${escapeAttr(story.section)}">
                <a class="press-visual-story__media" href="${escapeAttr(story.url)}">
                  ${story.image ? `<img alt="${escapeAttr(story.imageAlt || story.title)}" decoding="async" loading="lazy" src="${escapeAttr(story.image)}">` : `<span>${escapeHtml(story.section)}</span>`}
                </a>
                <div class="press-visual-story__body">
                  <p class="press-future-kicker">${escapeHtml(story.section)} / ${escapeHtml(freshness(story))}</p>
                  <h3><a href="${escapeAttr(story.url)}">${escapeHtml(story.title)}</a></h3>
                  <p>${escapeHtml(shorten(story.dek, 118))}</p>
                </div>
              </article>
            `;
          }).join('')}
          <a class="press-visual-archive-link" href="archive.html">Open the full archive</a>
        </div>
      </div>
    `;

    radar.querySelectorAll('[data-future-topic]').forEach(function bindTopic(button) {
      button.addEventListener('click', function onTopicClick() {
        openCommand(button.getAttribute('data-future-topic') || '');
      });
    });

    radar.querySelectorAll('[data-future-keyword]').forEach(function bindKeyword(button) {
      button.addEventListener('click', function onKeywordClick() {
        openCommand(button.getAttribute('data-future-keyword') || '');
      });
    });
  }

  function enhanceLeadPanel() {
    document.querySelectorAll('.lead-panel').forEach(function enhance(panel) {
      if (panel.querySelector('.press-live-badge')) return;
      const body = panel.querySelector('.lead-panel__body > div') || panel.querySelector('.lead-panel__body');
      if (!body) return;
      body.insertAdjacentHTML('afterbegin', '<div class="press-live-badge"><span></span> Live editorial slot</div>');
    });
  }

  function installCommandPalette() {
    if (document.querySelector('.press-command')) return;

    const overlay = document.createElement('div');
    overlay.className = 'press-command';
    overlay.hidden = true;
    overlay.innerHTML = `
      <div class="press-command__scrim" data-command-close></div>
      <section class="press-command__panel" role="dialog" aria-modal="true" aria-labelledby="press-command-title">
        <div class="press-command__top">
          <p class="press-future-kicker" id="press-command-title">Command center</p>
          <button type="button" class="press-command__close" data-command-close aria-label="Close command center">Close</button>
        </div>
        <div class="press-command__search">
          <input data-command-input type="search" autocomplete="off" placeholder="Search the live edition">
        </div>
        <div class="press-command__filters" data-command-filters></div>
        <div class="press-command__body">
          <div class="press-command__results" data-command-results></div>
          <aside class="press-command__preview" data-command-preview></aside>
        </div>
      </section>
    `;

    document.body.appendChild(overlay);

    overlay.querySelectorAll('[data-command-close]').forEach(function bindClose(button) {
      button.addEventListener('click', closeCommand);
    });

    const input = overlay.querySelector('[data-command-input]');
    input.addEventListener('input', function onInput() {
      selectedIndex = 0;
      renderCommandResults(input.value);
    });

    input.addEventListener('keydown', function onKeydown(event) {
      const links = Array.from(overlay.querySelectorAll('[data-command-result]'));
      if (event.key === 'ArrowDown') {
        event.preventDefault();
        selectedIndex = Math.min(selectedIndex + 1, Math.max(links.length - 1, 0));
        syncCommandSelection();
      } else if (event.key === 'ArrowUp') {
        event.preventDefault();
        selectedIndex = Math.max(selectedIndex - 1, 0);
        syncCommandSelection();
      } else if (event.key === 'Enter' && links[selectedIndex]) {
        event.preventDefault();
        links[selectedIndex].click();
      } else if (event.key === 'Escape') {
        closeCommand();
      }
    });
  }

  function bindGlobalCommands() {
    document.addEventListener('click', function interceptSearch(event) {
      const opener = event.target.closest('[data-future-command-open], [data-search-open], .search-trigger');
      if (!opener) return;
      event.preventDefault();
      event.stopPropagation();
      event.stopImmediatePropagation();
      openCommand('');
    }, true);

    document.addEventListener('keydown', function onGlobalKeydown(event) {
      const target = event.target;
      const typing = target && /input|textarea|select/i.test(target.tagName || '');

      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault();
        openCommand('');
        return;
      }

      if (!typing && event.key === '/') {
        event.preventDefault();
        openCommand('');
        return;
      }

      if (event.key === 'Escape' && commandOpen) {
        closeCommand();
      }
    });
  }

  function openCommand(seed) {
    const overlay = document.querySelector('.press-command');
    const input = overlay?.querySelector('[data-command-input]');
    if (!overlay || !input) return;

    commandOpen = true;
    overlay.hidden = false;
    document.documentElement.classList.add('press-command-open');
    buildCommandFilters();

    if (seed) {
      input.value = seed;
      activeFilter = 'All';
    }

    selectedIndex = 0;
    renderCommandResults(input.value);
    window.setTimeout(function focusInput() {
      input.focus();
      input.select();
    }, 20);
  }

  function closeCommand() {
    const overlay = document.querySelector('.press-command');
    if (!overlay) return;
    commandOpen = false;
    overlay.hidden = true;
    document.documentElement.classList.remove('press-command-open');
  }

  function buildCommandFilters() {
    const filters = document.querySelector('[data-command-filters]');
    if (!filters || !futureState) return;

    const sections = ['All'].concat(futureState.topics.slice(0, 8).map(function topicName(topic) { return topic.section; }));
    filters.innerHTML = sections.map(function filter(label) {
      const active = label === activeFilter ? ' is-active' : '';
      return `<button type="button" class="press-command-filter${active}" data-command-filter="${escapeAttr(label)}">${escapeHtml(label)}</button>`;
    }).join('');

    filters.querySelectorAll('[data-command-filter]').forEach(function bind(button) {
      button.addEventListener('click', function onFilterClick() {
        activeFilter = button.getAttribute('data-command-filter') || 'All';
        selectedIndex = 0;
        buildCommandFilters();
        const input = document.querySelector('[data-command-input]');
        renderCommandResults(input?.value || '');
      });
    });
  }

  function renderCommandResults(query) {
    const resultsBox = document.querySelector('[data-command-results]');
    const preview = document.querySelector('[data-command-preview]');
    if (!resultsBox || !preview) return;

    const state = futureState;
    if (!state) {
      resultsBox.innerHTML = '<div class="press-command-empty">Loading the live edition...</div>';
      preview.innerHTML = '';
      return;
    }

    const results = rankStories(state.stories, query || '', activeFilter).slice(0, 12);

    if (!results.length) {
      resultsBox.innerHTML = '<div class="press-command-empty">No matching stories yet.</div>';
      preview.innerHTML = '';
      return;
    }

    resultsBox.innerHTML = results.map(function resultItem(story, index) {
      return `
        <a class="press-command-result${index === selectedIndex ? ' is-selected' : ''}" href="${escapeAttr(story.url)}" data-command-result data-index="${index}">
          <span>${escapeHtml(story.section)}</span>
          <strong>${escapeHtml(story.title)}</strong>
          <em>${escapeHtml(freshness(story))}</em>
        </a>
      `;
    }).join('');

    resultsBox.querySelectorAll('[data-command-result]').forEach(function bindResult(link) {
      link.addEventListener('mouseenter', function onHover() {
        selectedIndex = Number(link.getAttribute('data-index') || 0);
        syncCommandSelection();
      });
    });

    syncCommandSelection();
  }

  function syncCommandSelection() {
    const links = Array.from(document.querySelectorAll('[data-command-result]'));
    const preview = document.querySelector('[data-command-preview]');
    links.forEach(function mark(link, index) {
      link.classList.toggle('is-selected', index === selectedIndex);
    });

    if (!preview || !futureState || !links[selectedIndex]) return;
    const href = links[selectedIndex].getAttribute('href');
    const story = futureState.stories.find(function byHref(item) { return item.url === href; });
    if (!story) return;

    preview.innerHTML = `
      ${story.image ? `<img alt="${escapeAttr(story.imageAlt || story.title)}" src="${escapeAttr(story.image)}" decoding="async" loading="lazy">` : ''}
      <p class="press-future-kicker">${escapeHtml(story.section)} / ${escapeHtml(story.type)}</p>
      <h3>${escapeHtml(story.title)}</h3>
      <p>${escapeHtml(shorten(story.dek, 220))}</p>
      <div class="press-command__meta">
        <span>${escapeHtml(story.published || formatDate(story.sortValue))}</span>
        <span>${escapeHtml(freshness(story))}</span>
      </div>
    `;
  }

  function rankStories(stories, query, filter) {
    const q = clean(query).toLowerCase();
    const terms = q.split(/\s+/).filter(Boolean);

    return stories.map(function score(story) {
      if (filter && filter !== 'All' && story.section !== filter) return null;

      let points = story.sortValue ? story.sortValue / 1e10 : 0;
      if (!terms.length) return { story, points };

      terms.forEach(function scoreTerm(term) {
        if (story.title.toLowerCase().includes(term)) points += 120;
        if (story.section.toLowerCase().includes(term)) points += 80;
        if (story.type.toLowerCase().includes(term)) points += 50;
        if ((story.dek || '').toLowerCase().includes(term)) points += 32;
        if ((story.keywords || []).join(' ').toLowerCase().includes(term)) points += 60;
        if (story.scoreText.includes(term)) points += 10;
      });

      return { story, points };
    }).filter(Boolean).sort(function byScore(a, b) {
      return b.points - a.points;
    }).map(function unwrap(item) {
      return item.story;
    });
  }

  function radarPoint(index, total) {
    const angle = (-90 + (360 / Math.max(total, 1)) * index) * Math.PI / 180;
    return {
      x: Math.round(50 + Math.cos(angle) * 38),
      y: Math.round(50 + Math.sin(angle) * 34)
    };
  }

  function topicSignal(items) {
    if (!items.length) return 'quiet';
    const newest = items[0]?.sortValue || 0;
    const ageHours = newest ? (Date.now() - newest) / 36e5 : 9999;
    if (items.length >= 30 || ageHours < 12) return 'surging';
    if (items.length >= 12 || ageHours < 48) return 'active';
    return 'steady';
  }

  function extractTerms(text) {
    return clean(text).toLowerCase().split(/[^a-z0-9]+/).filter(function term(word) {
      return word.length > 3 && !STOP_WORDS.has(word);
    });
  }

  function inferSection(url) {
    const file = String(url || '').split('/').pop() || '';
    const match = file.match(/^([a-z]+)-/i);
    if (!match) return '';
    const raw = match[1].replace(/ai/i, 'AI');
    return titleCase(raw);
  }

  function parseStoryDate(value) {
    const raw = String(value || '');
    const isoMatch = raw.match(/\d{4}-\d{2}-\d{2}(?:T[^\s]+)?/);
    if (isoMatch) {
      const parsed = Date.parse(isoMatch[0]);
      if (!Number.isNaN(parsed)) return parsed;
    }

    const parsed = Date.parse(raw.replace(/•/g, ' '));
    if (!Number.isNaN(parsed)) return parsed;

    return 0;
  }

  function freshness(story) {
    if (!story?.sortValue) return 'in archive';
    const hours = Math.max(0, (Date.now() - story.sortValue) / 36e5);
    if (hours < 1) return 'just now';
    if (hours < 24) return `${Math.floor(hours)}h ago`;
    if (hours < 72) return `${Math.floor(hours / 24)}d ago`;
    return 'archive';
  }

  function formatDate(value) {
    if (!value) return '';
    try {
      return new Intl.DateTimeFormat('en', { month: 'short', day: 'numeric', year: 'numeric' }).format(new Date(value));
    } catch (_) {
      return '';
    }
  }

  function normalizeUrl(url) {
    const value = clean(url);
    if (!value) return '';
    if (/^(https?:|mailto:|tel:|#)/i.test(value) || value.startsWith('/')) return value;
    return value.replace(/^\.\//, '');
  }

  function clean(value) {
    return String(value || '').replace(/\s+/g, ' ').trim();
  }

  function shorten(value, max) {
    const text = clean(value);
    if (text.length <= max) return text;
    return text.slice(0, Math.max(0, max - 1)).trim().replace(/[,\s]+$/, '') + '...';
  }

  function titleCase(value) {
    const text = clean(value).replace(/[-_]+/g, ' ');
    if (!text) return '';
    if (/^ai$/i.test(text)) return 'AI';
    return text.split(' ').map(function titleWord(word) {
      return /^ai$/i.test(word) ? 'AI' : word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
    }).join(' ');
  }

  function slugify(value) {
    return clean(value).toLowerCase().replace(/&/g, 'and').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  }

  function escapeHtml(value) {
    return String(value || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function escapeAttr(value) {
    return escapeHtml(value).replace(/`/g, '&#96;');
  }
})();
/* PRESS_FUTURE_NEWSROOM_END */

/* PRESS_HOMEPAGE_HERO_STANDARD_START
   One permanent contract for the homepage hero:
   1 center lead, 3 side stories on the left, 3 on the right.
   Any renderer that replaces the hero nav is normalized back to this shape.
*/
(function pressHomepageHeroStandard() {
  'use strict';

  const HERO_SLOT_COUNT = 7;
  const SIDE_SLOTS = ['left-1', 'left-2', 'left-3', 'right-1', 'right-2', 'right-3'];

  function layoutLeadNav(navBox) {
    const nav = navBox || document.querySelector('.lead-nav');
    if (!nav || nav.dataset.pressHeroApplying === 'true') return;

    nav.dataset.pressHeroApplying = 'true';

    try {
      const buttons = Array.from(nav.querySelectorAll('[data-lead-button]'));
      const sideButtons = buttons
        .filter((button) => !button.classList.contains('is-active'))
        .slice(0, SIDE_SLOTS.length);

      buttons.forEach((button) => {
        button.removeAttribute('data-side-slot');
      });

      sideButtons.forEach((button, index) => {
        button.setAttribute('data-side-slot', SIDE_SLOTS[index]);
      });

      nav.dataset.sideLayout = 'split';
      nav.closest('.lead-switcher')?.setAttribute('data-press-hero-layout', 'split-rail');
      nav.closest('.lead-switcher')?.setAttribute('data-press-hero-slots', String(HERO_SLOT_COUNT));
    } finally {
      delete nav.dataset.pressHeroApplying;
    }
  }

  function installObserver(nav) {
    if (!nav || nav.dataset.pressHeroStandardBound === 'true') return;

    nav.dataset.pressHeroStandardBound = 'true';
    let queued = false;

    const schedule = () => {
      if (nav.dataset.pressHeroApplying === 'true' || queued) return;
      queued = true;
      window.requestAnimationFrame(() => {
        queued = false;
        layoutLeadNav(nav);
      });
    };

    const observer = new MutationObserver(schedule);
    observer.observe(nav, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['class', 'aria-pressed'],
    });
  }

  function run() {
    document.querySelectorAll('.lead-nav').forEach((nav) => {
      installObserver(nav);
      layoutLeadNav(nav);
    });
  }

  window.PressHeroStandard = {
    heroSlotCount: HERO_SLOT_COUNT,
    sideSlots: SIDE_SLOTS.slice(),
    layoutLeadNav,
    run,
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run, { once: true });
  } else {
    run();
  }

  window.addEventListener('pageshow', run);
  window.addEventListener('load', run);
  window.addEventListener('press:ecosystem-ready', run);
})();
/* PRESS_HOMEPAGE_HERO_STANDARD_END */

/* PRESS_LIVING_ARTICLE_KIT_START
   Static-first premium layer: place lens, share studio, source constellation,
   entity cards, timelines, reader memory, and homepage pulse. No runtime APIs.
*/
(function pressLivingArticleKit() {
  'use strict';

  const STORAGE = {
    followedTopics: 'press-living-followed-topics',
    readerMode: 'press-living-reader-mode',
    sourceTrail: 'press-living-source-trail',
  };

  const PLACE_LIBRARY = [
    {
      id: 'atla-noho',
      label: 'ATLA NoHo',
      type: 'Restaurant',
      address: '372 Lafayette Street, New York, NY',
      names: ['ATLA NoHo', 'Atla', '372 Lafayette Street', 'Lafayette Street'],
      lat: 40.72717,
      lng: -73.99418,
      note: 'The Lafayette Street room anchors the closing story and the replacement concept that follows it.',
      scene: 'A NoHo restaurant block where food, design, social memory, and real estate all sit in the same room.',
    },
    {
      id: 'noho',
      label: 'NoHo, Manhattan',
      type: 'Neighborhood',
      address: 'NoHo, New York, NY',
      names: ['NoHo', 'NoHo NYC'],
      lat: 40.72755,
      lng: -73.99482,
      note: 'The neighborhood is not a backdrop in the Atla feature; it is part of why the room mattered.',
      scene: 'Cast-iron blocks, downtown dining, foot traffic, and a city that treats restaurant turnover as civic weather.',
    },
    {
      id: 'cosme',
      label: 'Cosme',
      type: 'Restaurant',
      address: '35 E 21st Street, New York, NY',
      names: ['Cosme'],
      lat: 40.74058,
      lng: -73.98913,
      note: 'Cosme is the higher-gloss sibling that helps explain the Casamata New York universe.',
      scene: 'A Flatiron dining room where modern Mexican cooking became part of New York power dining.',
    },
    {
      id: 'pujol',
      label: 'Pujol',
      type: 'Restaurant',
      address: 'Tennyson 133, Polanco, Mexico City',
      names: ['Pujol', 'Mexico City'],
      lat: 19.43071,
      lng: -99.19474,
      note: 'Pujol is the origin point for Enrique Olvera context in several restaurant stories.',
      scene: 'A Mexico City dining institution whose influence travels through cooks, concepts, and city-to-city adaptations.',
    },
    {
      id: 'venice-los-angeles',
      label: 'Venice, Los Angeles',
      type: 'Neighborhood',
      address: 'Venice, Los Angeles, CA',
      names: ['Venice', 'Los Angeles', 'L.A.', 'LA'],
      lat: 33.98505,
      lng: -118.46948,
      note: 'The Los Angeles branch gives the Atla story a second-city echo.',
      scene: 'A beachside restaurant market where Mexico City influence, California dining, and brand expansion meet.',
    },
    {
      id: 'horseshoe-paris-las-vegas',
      label: 'Horseshoe and Paris Las Vegas',
      type: 'Venue',
      address: 'Las Vegas Strip, Las Vegas, NV',
      names: ['Horseshoe', 'Paris Las Vegas', 'Las Vegas', 'WSOP'],
      lat: 36.11289,
      lng: -115.17185,
      note: 'The WSOP Main Event story lives physically inside the Las Vegas casino corridor.',
      scene: 'A televised poker room where tournament scale, camera grammar, and crowd pressure become one product.',
    },
    {
      id: 'espn-bristol',
      label: 'ESPN campus',
      type: 'Media hub',
      address: 'Bristol, CT',
      names: ['ESPN', 'Bristol'],
      lat: 41.64882,
      lng: -72.90078,
      note: 'ESPN matters in sports stories as distribution, memory, and a mainstream viewing room.',
      scene: 'A broadcast hub where sports become schedules, packages, highlight language, and shared national appointment viewing.',
    },
    {
      id: 'pentagon',
      label: 'The Pentagon',
      type: 'Government',
      address: 'Washington, DC area',
      names: ['Pentagon', 'Department of War', 'Department of Defense'],
      lat: 38.87186,
      lng: -77.05627,
      note: 'The classified AI story is about models entering secure defense infrastructure.',
      scene: 'A five-sided bureaucracy where procurement, cloud systems, secrecy, and military judgment converge.',
    },
    {
      id: 'washington-dc',
      label: 'Washington, DC',
      type: 'Capital',
      address: 'Washington, DC',
      names: ['Washington', 'White House', 'Capitol', 'D.C.', 'DC'],
      lat: 38.89768,
      lng: -77.03653,
      note: 'Many politics, courts, culture, and security stories route through Washington power.',
      scene: 'A symbolic city where paperwork, law, ceremony, and crisis often share the same stage.',
    },
    {
      id: 'washington-hilton',
      label: 'Washington Hilton',
      type: 'Hotel and event venue',
      address: '1919 Connecticut Avenue NW, Washington, DC',
      names: ['Washington Hilton', 'Terrace Level', 'Correspondents’ Dinner', 'Correspondents Dinner'],
      lat: 38.91697,
      lng: -77.04522,
      note: 'The ballroom and checkpoint make the security story a question of venue design, memory, and public ritual.',
      scene: 'A Washington hotel whose ballrooms can become a media room, a security perimeter, and a political symbol at once.',
    },
    {
      id: 'oakland-federal-court',
      label: 'Oakland federal courthouse area',
      type: 'Courthouse',
      address: 'Oakland, CA',
      names: ['Oakland'],
      lat: 37.80436,
      lng: -122.27111,
      note: 'The OpenAI trial becomes more concrete when the abstract governance fight has a courtroom on the map.',
      scene: 'A Bay Area courthouse setting where nonprofit promises, capital, and AI power are translated into exhibits and testimony.',
    },
    {
      id: 'nasa-kennedy',
      label: 'Kennedy Space Center',
      type: 'Spaceport',
      address: 'Merritt Island, FL',
      names: ['Kennedy Space Center', 'Artemis', 'Launch Complex 39B', 'NASA'],
      lat: 28.62717,
      lng: -80.62082,
      note: 'Artemis stories need a physical launch site, not just a space-program acronym.',
      scene: 'A coastal launch complex where engineering becomes public spectacle and telemetry becomes evidence.',
    },
    {
      id: 'the-hague',
      label: 'The Hague',
      type: 'Diplomatic city',
      address: 'The Hague, Netherlands',
      names: ['The Hague', 'NATO summit'],
      lat: 52.0705,
      lng: 4.3007,
      note: 'European defense stories often pass through summit language before becoming logistics.',
      scene: 'A diplomatic city where alliance photographs have to become production lines and movement plans.',
    },
    {
      id: 'strait-hormuz',
      label: 'Strait of Hormuz',
      type: 'Maritime chokepoint',
      address: 'Persian Gulf / Gulf of Oman',
      names: ['Strait of Hormuz', 'Hormuz'],
      lat: 26.5667,
      lng: 56.25,
      note: 'Energy and war-risk stories become legible when the chokepoint is visible.',
      scene: 'A narrow waterway where oil, shipping insurance, military signaling, and inflation meet.',
    },
    {
      id: 'el-fasher',
      label: 'El Fasher, Darfur',
      type: 'City',
      address: 'North Darfur, Sudan',
      names: ['El Fasher', 'Darfur', 'Sudan'],
      lat: 13.62793,
      lng: 25.34936,
      note: 'Darfur stories often turn on routes, burn scars, and the geography of food access.',
      scene: 'A city and surrounding region where satellite evidence, roads, markets, and survival are bound together.',
    },
    {
      id: 'nairobi',
      label: 'Nairobi',
      type: 'City',
      address: 'Nairobi, Kenya',
      names: ['Nairobi', 'Kenya'],
      lat: -1.28639,
      lng: 36.81722,
      note: 'Flood and infrastructure stories become sharper when the drainage geography is visible.',
      scene: 'A fast-growing city where roads, rivers, informal settlements, and rainfall all test the urban system.',
    },
    {
      id: 'burbank',
      label: 'Burbank studio district',
      type: 'Media place',
      address: 'Burbank, CA',
      names: ['Burbank', 'Warner Bros.', 'Paramount Skydance'],
      lat: 34.148,
      lng: -118.337,
      note: 'Hollywood consolidation stories become less abstract when tied to lots, gates, and workers.',
      scene: 'A studio city where streaming strategy eventually touches call sheets, back lots, and production labor.',
    },
    {
      id: 'richmond',
      label: 'Richmond',
      type: 'City',
      address: 'Richmond, VA',
      names: ['Richmond'],
      lat: 37.54072,
      lng: -77.43605,
      note: 'Cloud, power, and state-policy stories often land in local ratepayer math.',
      scene: 'A capital city where data-center growth can become a public utility argument.',
    },
    {
      id: 'wichita',
      label: 'Wichita',
      type: 'City',
      address: 'Wichita, KS',
      names: ['Wichita'],
      lat: 37.68718,
      lng: -97.33005,
      note: 'Local governance stories are often clearest when a strange new tool meets a public rulebook.',
      scene: 'A city hall test case where technology policy becomes an ordinary vote.',
    },
    {
      id: 'odesa',
      label: 'Odesa',
      type: 'Port city',
      address: 'Odesa, Ukraine',
      names: ['Odesa', 'Odessa'],
      lat: 46.48253,
      lng: 30.72331,
      note: 'Port stories tie war, food, shipping, and nuclear risk to one coastline.',
      scene: 'A Black Sea port where sirens, grain corridors, and European security overlap.',
    },
    {
      id: 'canary-islands',
      label: 'Canary Islands',
      type: 'Atlantic archipelago',
      address: 'Canary Islands, Spain',
      names: ['Canary Islands', 'Canaries'],
      lat: 28.2916,
      lng: -16.6291,
      note: 'The Arconian seizure made the Atlantic approach visible before the story moved inland.',
      scene: 'An Atlantic waypoint where maritime enforcement, island geography, and European demand intersect.',
    },
    {
      id: 'antwerp',
      label: 'Antwerp',
      type: 'Port city',
      address: 'Antwerp, Belgium',
      names: ['Antwerp', 'Port of Antwerp', 'Port of Antwerp-Bruges'],
      lat: 51.2194,
      lng: 4.4025,
      note: 'Antwerp is one of Europe’s central cocaine-trafficking pressure points.',
      scene: 'A North Sea logistics hub where containers, customs, corruption pressure, and urban violence meet.',
    },
    {
      id: 'rotterdam',
      label: 'Rotterdam',
      type: 'Port city',
      address: 'Rotterdam, Netherlands',
      names: ['Rotterdam', 'Port of Rotterdam'],
      lat: 51.9244,
      lng: 4.4777,
      note: 'Rotterdam keeps the story anchored in the North Sea port system.',
      scene: 'A massive port city where legitimate trade volume creates both prosperity and concealment risk.',
    },
    {
      id: 'algeciras',
      label: 'Algeciras',
      type: 'Port city',
      address: 'Algeciras, Spain',
      names: ['Algeciras'],
      lat: 36.1408,
      lng: -5.4562,
      note: 'The story cites Spain’s earlier 13-tonne banana-shipment seizure at Algeciras.',
      scene: 'A Strait of Gibraltar port where Spanish enforcement and global cargo lanes overlap.',
    },
    {
      id: 'hamburg',
      label: 'Hamburg',
      type: 'Port city',
      address: 'Hamburg, Germany',
      names: ['Hamburg', 'Port of Hamburg'],
      lat: 53.5511,
      lng: 9.9937,
      note: 'Hamburg appears in the story as a previous large European seizure point and a reminder that pressure shifts across ports.',
      scene: 'A major northern port where legitimate cargo volume creates the kind of scale traffickers try to hide inside.',
    },
    {
      id: 'le-havre',
      label: 'Le Havre',
      type: 'Port city',
      address: 'Le Havre, France',
      names: ['Le Havre'],
      lat: 49.4944,
      lng: 0.1079,
      note: 'Le Havre keeps France inside the broader port-pressure map described by the article.',
      scene: 'A Channel port where European logistics, customs pressure, and route displacement can meet.',
    },
    {
      id: 'marseille',
      label: 'Marseille',
      type: 'Port city',
      address: 'Marseille, France',
      names: ['Marseille'],
      lat: 43.2965,
      lng: 5.3698,
      note: 'The article cites Marseille as one of the cities forced to confront cocaine-linked violence and market pressure.',
      scene: 'A Mediterranean port city where trafficking pressure can spill from maritime routes into urban life.',
    },
    {
      id: 'united-kingdom',
      label: 'United Kingdom',
      type: 'Consumer market',
      address: 'United Kingdom',
      names: ['United Kingdom', 'UK', 'Britain', 'British', 'England and Wales'],
      lat: 54.7024,
      lng: -3.2766,
      note: 'The UK is central to the article’s consumer, public-health, wastewater and organised-crime lens.',
      scene: 'A consumer market where the cocaine story leaves ports and becomes mortality data, wastewater signals, street pressure, and ordinary public life.',
    },
    {
      id: 'ecuador',
      label: 'Ecuador',
      type: 'Transit country',
      address: 'Ecuador',
      names: ['Ecuador', 'Ecuadorian'],
      lat: -1.8312,
      lng: -78.1834,
      note: 'Ecuador appears in the story as part of the source and transit pressure connected to European demand.',
      scene: 'An Andean-Pacific pressure point where port violence, gangs, politics, and global cocaine demand intersect.',
    },
    {
      id: 'andean-region',
      label: 'Andean region',
      type: 'Source region',
      address: 'Colombia, Peru, Bolivia and Ecuador',
      names: ['Andean region', 'Andes', 'Colombia', 'Peru', 'Bolivia'],
      lat: -9.19,
      lng: -75.0152,
      note: 'The article connects European demand back to coca cultivation, production pressure, and source-country harm.',
      scene: 'A broad production geography where cultivation, processing, armed groups, rural pressure, and global demand become one supply chain.',
    },
  ];

  const ENTITY_LIBRARY = [
    {
      id: 'arconian',
      name: 'Arconian',
      type: 'Seized vessel',
      aliases: ['Arconian'],
      summary: 'The Comoros-flagged ship Spanish authorities tied to the May 2026 seizure of about 30 tonnes of cocaine near the Canary Islands.',
      why: 'It is the article’s news peg: one vessel that makes a much larger European cocaine market visible.',
    },
    {
      id: 'guardia-civil',
      name: 'Guardia Civil',
      type: 'Law-enforcement agency',
      aliases: ['Guardia Civil'],
      summary: 'Spain’s national police force with military status, central to maritime and drug-trafficking enforcement.',
      why: 'The Arconian case begins with Spanish enforcement and the intelligence that led to the interdiction.',
    },
    {
      id: 'euda',
      name: 'European Union Drugs Agency',
      type: 'Drug-monitoring agency',
      aliases: ['European Union Drugs Agency', 'EUDA', 'European Drug Agency'],
      summary: 'The EU agency that tracks drug use, seizures, wastewater, treatment demand, deaths, and market signals.',
      why: 'Its cocaine and wastewater data make the story more than a single spectacular seizure.',
    },
    {
      id: 'unodc',
      name: 'United Nations Office on Drugs and Crime',
      type: 'UN agency',
      aliases: ['United Nations Office on Drugs and Crime', 'UNODC'],
      summary: 'The UN agency whose global drug reports track cocaine production, trafficking routes, and market expansion.',
      why: 'It connects Europe’s demand to production pressure and source-country violence.',
    },
    {
      id: 'europol',
      name: 'Europol',
      type: 'Law-enforcement agency',
      aliases: ['Europol'],
      summary: 'The EU law-enforcement agency focused on serious and organised crime, including drug trafficking and criminal networks.',
      why: 'Europol frames cocaine as a logistics, corruption, violence, and organised-crime problem.',
    },
    {
      id: 'eurojust',
      name: 'Eurojust',
      type: 'Judicial cooperation agency',
      aliases: ['Eurojust'],
      summary: 'The EU agency that supports cross-border judicial cooperation in major crime cases.',
      why: 'Drug-trafficking investigations do not stop cleanly at national borders; prosecution has to travel too.',
    },
    {
      id: 'european-ports-alliance',
      name: 'European Ports Alliance',
      type: 'Port-security initiative',
      aliases: ['European Ports Alliance', 'Ports Alliance'],
      summary: 'An EU-backed public-private effort to harden ports against drug trafficking and organised-crime infiltration.',
      why: 'It shows that Europe sees ports as systems of economic importance and criminal vulnerability.',
    },
    {
      id: 'national-crime-agency',
      name: 'National Crime Agency',
      type: 'UK law-enforcement agency',
      aliases: ['National Crime Agency', 'NCA'],
      summary: 'The UK agency that assesses and investigates serious and organised crime, including Class A drug markets.',
      why: 'It gives the British angle an enforcement baseline rather than treating the UK as only a consumer market.',
    },
    {
      id: 'office-national-statistics',
      name: 'Office for National Statistics',
      type: 'Statistics agency',
      aliases: ['Office for National Statistics', 'ONS'],
      summary: 'The UK statistics office whose death registrations show cocaine appearing in mortality records.',
      why: 'It makes the consumer-impact side measurable through death-certificate data.',
    },
    {
      id: 'home-office',
      name: 'UK Home Office',
      type: 'Government department',
      aliases: ['Home Office', 'UK Home Office'],
      summary: 'The UK department whose wastewater and drug-misuse statistics help estimate cocaine demand.',
      why: 'Its data helps connect street-level use to city-scale consumption patterns.',
    },
    {
      id: 'port-antwerp-bruges',
      name: 'Port of Antwerp-Bruges',
      type: 'Port authority',
      aliases: ['Port of Antwerp-Bruges', 'Port of Antwerp'],
      summary: 'A major Belgian port authority at the center of Europe’s cocaine-trafficking pressure.',
      why: 'The article uses Antwerp to show how legitimate logistics infrastructure becomes a trafficking target.',
    },
    {
      id: 'port-rotterdam',
      name: 'Port of Rotterdam',
      type: 'Port authority',
      aliases: ['Port of Rotterdam'],
      summary: 'One of Europe’s largest ports and a central node in the North Sea logistics system.',
      why: 'Rotterdam broadens the port story beyond one country and shows the scale of the enforcement problem.',
    },
    {
      id: 'reuters',
      name: 'Reuters',
      type: 'News agency',
      aliases: ['Reuters'],
      summary: 'The news agency whose reporting supplied the central Arconian seizure account used in the article.',
      why: 'It anchors the breaking-news claim in a named reporting source rather than social reaction.',
    },
    {
      id: 'el-pais',
      name: 'El Pais',
      type: 'News organization',
      aliases: ['El Pais', 'El País'],
      summary: 'The Spanish newspaper whose reporting added court, valuation, and destination context around the Arconian case.',
      why: 'It gives the Spanish legal and enforcement story more local texture.',
    },
    {
      id: 'atla',
      name: 'Atla',
      type: 'Restaurant',
      aliases: ['Atla', 'ATLA'],
      summary: 'A NoHo restaurant whose closing turns one room into a story about memory, reinvention, and restaurant culture.',
      why: 'It gives the article a physical object: not just a business closure, but a place people ate, posted about, and remembered.',
    },
    {
      id: 'enrique-olvera',
      name: 'Enrique Olvera',
      type: 'Chef',
      aliases: ['Enrique Olvera', 'Olvera'],
      summary: 'The chef and restaurateur behind Pujol, Cosme, Atla, and the wider Casamata universe.',
      why: 'His reputation connects the local New York closing to a broader city-to-city restaurant system.',
    },
    {
      id: 'casamata',
      name: 'Casamata',
      type: 'Hospitality group',
      aliases: ['Casamata'],
      summary: 'The restaurant group around Olvera projects including Pujol, Cosme, Atla, and later concepts.',
      why: 'The group makes the closing read as conversion and succession, not only disappearance.',
    },
    {
      id: 'cosme',
      name: 'Cosme',
      type: 'Restaurant',
      aliases: ['Cosme'],
      summary: 'A New York restaurant that helps define the higher-end side of the Olvera/Casamata presence.',
      why: 'It gives readers a sibling reference for Atla and the group portfolio.',
    },
    {
      id: 'pujol',
      name: 'Pujol',
      type: 'Restaurant',
      aliases: ['Pujol'],
      summary: 'Olvera’s Mexico City flagship and a central reference point for his cooking reputation.',
      why: 'It explains why a casual downtown restaurant can still carry international culinary gravity.',
    },
    {
      id: 'wsop',
      name: 'World Series of Poker',
      type: 'Sports property',
      aliases: ['World Series of Poker', 'WSOP', 'Main Event'],
      summary: 'Poker’s most recognizable tournament brand and the anchor of the prime-time sports feature.',
      why: 'The story depends on the WSOP as both competition and television product.',
    },
    {
      id: 'espn',
      name: 'ESPN',
      type: 'Broadcaster',
      aliases: ['ESPN'],
      summary: 'The sports network whose distribution can make a poker final table feel mainstream again.',
      why: 'It turns the tournament into a scheduled shared room, not only a niche stream.',
    },
    {
      id: 'openai',
      name: 'OpenAI',
      type: 'AI company',
      aliases: ['OpenAI'],
      summary: 'A frontier AI company central to stories about governance, infrastructure, military use, and trust.',
      why: 'In The Press stories, OpenAI often stands where mission language meets money, power, and deployment.',
    },
    {
      id: 'elon-musk',
      name: 'Elon Musk',
      type: 'Executive',
      aliases: ['Elon Musk', 'Musk'],
      summary: 'A founder, executive, and litigant whose public conflicts often turn private governance disputes into spectacle.',
      why: 'In the OpenAI court story, Musk is both messenger and interested competitor.',
    },
    {
      id: 'sam-altman',
      name: 'Sam Altman',
      type: 'Executive',
      aliases: ['Sam Altman', 'Altman'],
      summary: 'OpenAI’s chief executive and a recurring figure in stories about AI scale, governance, and commercial power.',
      why: 'He personifies the institutional question of whether mission language can survive market scale.',
    },
    {
      id: 'microsoft',
      name: 'Microsoft',
      type: 'Technology company',
      aliases: ['Microsoft'],
      summary: 'A cloud and AI giant whose partnership with OpenAI made compute, capital, and distribution inseparable.',
      why: 'It is the infrastructure and investment layer under several AI stories.',
    },
    {
      id: 'anthropic',
      name: 'Anthropic',
      type: 'AI company',
      aliases: ['Anthropic'],
      summary: 'An AI company often used as a comparison point in safety, enterprise, and defense AI stories.',
      why: 'Its presence or absence can reveal where the guardrail argument is moving.',
    },
    {
      id: 'google',
      name: 'Google',
      type: 'Technology company',
      aliases: ['Google'],
      summary: 'A cloud and AI company that appears in stories about infrastructure, enterprise deployment, and defense contracts.',
      why: 'It broadens the story beyond one AI vendor into a platform race.',
    },
    {
      id: 'oracle',
      name: 'Oracle',
      type: 'Technology company',
      aliases: ['Oracle'],
      summary: 'A cloud and database company that appears where AI deployment meets government infrastructure.',
      why: 'It helps show how AI is becoming a cloud-contract and classified-network story.',
    },
    {
      id: 'pentagon',
      name: 'The Pentagon',
      type: 'Institution',
      aliases: ['Pentagon', 'Department of Defense', 'Department of War'],
      summary: 'The U.S. military bureaucracy where procurement, classified systems, and AI deployment become policy.',
      why: 'It makes AI governance tangible: the model is entering rooms where mistakes are not abstract.',
    },
    {
      id: 'nasa',
      name: 'NASA',
      type: 'Space agency',
      aliases: ['NASA', 'Artemis'],
      summary: 'The U.S. space agency central to Artemis and science-infrastructure stories.',
      why: 'NASA stories let the site show engineering as a public evidence system, not just launch spectacle.',
    },
    {
      id: 'nato',
      name: 'NATO',
      type: 'Alliance',
      aliases: ['NATO'],
      summary: 'The military alliance at the center of European defense, readiness, logistics, and procurement stories.',
      why: 'It turns speeches about security into questions about budgets, factories, roads, and time.',
    },
    {
      id: 'cdc',
      name: 'CDC',
      type: 'Public health agency',
      aliases: ['CDC'],
      summary: 'The U.S. public health agency that appears in outbreak, vaccine, surveillance, and evidence-chain stories.',
      why: 'CDC references usually show whether health information is moving like infrastructure.',
    },
    {
      id: 'white-house',
      name: 'White House',
      type: 'Institution',
      aliases: ['White House'],
      summary: 'The presidential institution that turns ceremony, security, and public communication into national signals.',
      why: 'In Washington stories, it makes the room larger than the room: security choices become political architecture.',
    },
    {
      id: 'secret-service',
      name: 'Secret Service',
      type: 'Federal agency',
      aliases: ['Secret Service'],
      summary: 'The federal protective agency responsible for presidential security and high-risk event protocols.',
      why: 'Its response is the difference between a disrupted event and a much larger constitutional crisis.',
    },
    {
      id: 'department-of-justice',
      name: 'Department of Justice',
      type: 'Federal agency',
      aliases: ['Department of Justice', 'Justice Department', 'DOJ'],
      summary: 'The federal law-enforcement institution that turns alleged political violence into charges, affidavits, and court process.',
      why: 'It gives crisis reporting an official evidence trail beyond the immediate scene.',
    },
    {
      id: 'fbi',
      name: 'FBI',
      type: 'Federal agency',
      aliases: ['FBI'],
      summary: 'The federal investigative agency that appears when threats, affidavits, communications, and motive claims must be sorted into evidence.',
      why: 'It helps separate a fast-moving public narrative from what investigators can actually document.',
    },
    {
      id: 'donald-trump',
      name: 'Donald Trump',
      type: 'Public official',
      aliases: ['Donald Trump', 'President Trump', 'Trump'],
      summary: 'The president at the center of security, politics, courts, and institutional-power stories.',
      why: 'His presence changes an event from local disruption into a national security and political legitimacy story.',
    },
    {
      id: 'iran',
      name: 'Iran',
      type: 'State actor',
      aliases: ['Iran', 'Tehran'],
      summary: 'A state actor central to Gulf security, energy chokepoints, sanctions, and nuclear diplomacy.',
      why: 'In Hormuz stories, Iranian decisions can move from negotiation rooms into oil prices, shipping lanes, and household costs.',
    },
    {
      id: 'international-energy-agency',
      name: 'International Energy Agency',
      type: 'Energy body',
      aliases: ['International Energy Agency', 'IEA'],
      summary: 'An energy-policy organization whose chokepoint data helps turn maritime stress into economic scale.',
      why: 'Its numbers explain why one narrow waterway can become a global price story.',
    },
    {
      id: 'international-maritime-organization',
      name: 'International Maritime Organization',
      type: 'UN agency',
      aliases: ['International Maritime Organization', 'IMO'],
      summary: 'The U.N. maritime agency that frames chokepoint crises through vessel safety, crews, and shipping rules.',
      why: 'It keeps the human labor of seafarers visible inside an oil-market story.',
    },
    {
      id: 'world-food-programme',
      name: 'World Food Programme',
      type: 'Humanitarian agency',
      aliases: ['World Food Programme', 'WFP'],
      summary: 'A U.N. food agency whose market monitors and emergency operations make hunger measurable in war zones.',
      why: 'Its data connects prices, routes, access, and famine warnings to what families can actually eat.',
    },
    {
      id: 'rapid-support-forces',
      name: 'Rapid Support Forces',
      type: 'Armed group',
      aliases: ['Rapid Support Forces', 'RSF'],
      summary: 'A Sudanese paramilitary force central to the Darfur war, siege reporting, displacement, and rights investigations.',
      why: 'The Darfur food-map story depends on who controls roads, burns villages, and constrains civilian movement.',
    },
    {
      id: 'sudanese-armed-forces',
      name: 'Sudanese Armed Forces',
      type: 'Military',
      aliases: ['Sudanese Armed Forces', 'SAF'],
      summary: 'Sudan’s military force and one of the principal parties to the country’s war.',
      why: 'Naming both conflict parties helps the story track responsibility without flattening a complex war into one tactic.',
    },
    {
      id: 'ipc',
      name: 'Integrated Food Security Phase Classification',
      type: 'Food-security system',
      aliases: ['Integrated Food Security Phase Classification', 'IPC'],
      summary: 'The technical system used to classify acute food insecurity, catastrophe, and famine conditions.',
      why: 'It explains why famine warnings can be precise, late, disputed, and still morally urgent.',
    },
  ];

  const SOURCE_CLUSTER_ORDER = [
    'Official',
    'Reporting',
    'Social',
    'Guide',
    'Legal',
    'Public Data',
    'Place',
    'Background',
  ];

  const NUMBER_TOKEN_PATTERN = /(^|[^A-Za-z0-9$€£])((?:[$€£]\s?\d[\d,.]*(?:\.\d+)?(?:\s?(?:million|billion|trillion))?)|(?:\d[\d,.]*(?:\.\d+)?(?:\s|-)?(?:%|percent|million|billion|trillion|barrels?|vessels?|tankers?|ships?|crews?|kilometers?|miles?|tonnes?|tons?|gigawatts?|megawatts?|people|families|children|exports?|imports?|capacity|per day)))(?=$|[^A-Za-z0-9])/gi;
  const SOURCE_NOTE_REF_SELECTOR = '.source-ref a[href^="#source"], a[href^="#source"].source-label, a[data-source-id]:not([data-source-external="true"])';

  let activeArticleContext = null;
  let lastFocusedElement = null;
  let lastSourceClickAt = 0;

  function ready(callback) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', callback, { once: true });
    } else {
      callback();
    }
  }

  ready(function initLivingArticleKit() {
    bindGlobalLivingActions();
    initArticlePage();
    initHomepagePulse();
  });

  function initArticlePage() {
    if (!document.body.classList.contains('page-article')) return;

    const article = document.querySelector('.page-article .article') || document.querySelector('.page-article .article-shell');
    const body = article?.querySelector('.article-body, [data-article-body]') || document.querySelector('.article-body, [data-article-body]');
    const hero = article?.querySelector('.article-hero') || document.querySelector('.article-hero');
    if (!article || !body) return;

    const story = getCurrentStoryData(article, hero, body);
    const text = collectReadableText(body, hero);
    const context = {
      article,
      body,
      hero,
      story,
      text,
      places: detectPlaces(text, story),
      sources: collectArticleSources(article),
      beats: collectTimelineBeats(body),
      entities: detectEntities(text),
      relatedStories: readEmbeddedStories(),
      key: normalizeUrlKey(window.location.pathname || story.url || story.title),
      evidence: [],
      relationships: { nodes: [], links: [] },
    };
    numberInlineSourceRefs(context);
    hydrateRailSourceLinks(context);
    try {
      context.evidence = collectEvidenceMoments(context);
    } catch (_) {
      context.evidence = [];
    }
    try {
      context.relationships = buildRelationshipWeb(context);
    } catch (_) {
      context.relationships = { nodes: context.entities.slice(0, 9), links: [] };
    }

    activeArticleContext = context;
    installArticleDock(context);
    installSocialRailEnhancements(context);
    installArticleAtmosphere(context);
    try {
      installArticleIntelligence(context);
    } catch (_) {}
    try {
      wrapEntityMentions(context);
    } catch (_) {}

    window.PressLivingArticle = {
      openPlaceLens: () => openPlaceLens(context),
      openShareStudio: () => openShareStudio(context),
      openSourceBoard: () => openSourceBoard(context),
      openTimeline: () => openTimeline(context),
      openEntities: () => openEntityDrawer(context),
      openRelationships: () => openRelationshipWeb(context),
      context,
    };
  }

  function initHomepagePulse() {
    if (!document.body.classList.contains('page-home')) return;

    document.querySelectorAll('.press-living-home, [data-living-home-pulse]').forEach((node) => {
      node.remove();
    });
  }

  function installArticleDock(context) {
    document.querySelectorAll('[data-living-article-dock]').forEach((node) => node.remove());
    return;
    const existingDock = document.querySelector('[data-living-article-dock]');
    const dock = existingDock || document.createElement('section');
    dock.className = 'press-living-dock';
    dock.setAttribute('data-living-article-dock', '');
    dock.setAttribute('aria-label', 'Living article tools');
    dock.innerHTML = `
      <div class="press-living-dock__intro">
        <p class="press-living-kicker">Living article kit</p>
        <strong>No API. Static story, live browser tools.</strong>
      </div>
      <div class="press-living-dock__actions">
        <button type="button" data-living-open="places">Place Lens <span>${context.places.length}</span></button>
        <button type="button" data-living-open="share">Share Studio</button>
        <button type="button" data-living-open="sources">Source Board <span>${context.sources.length}</span></button>
        <button type="button" data-living-open="timeline">Timeline <span>${context.beats.length}</span></button>
        <button type="button" data-living-open="entities">Entities <span>${context.entities.length}</span></button>
        <button type="button" data-living-open="relationships">Actor Web <span>${context.relationships.links.length}</span></button>
        <button type="button" data-living-action="source-trail">Source Trail</button>
        <button type="button" data-living-action="listen">Listen</button>
        <button type="button" data-living-action="reader-mode">Focus</button>
        <button type="button" data-living-action="follow-topic">${isFollowingTopic(context.story.section) ? 'Following' : 'Follow Topic'}</button>
      </div>
    `;

    if (!existingDock) {
      const hero = context.hero || context.article;
      const anchor = hero.querySelector('[data-article-trust-card]')
        || hero.querySelector('[data-listen-controls]')
        || hero.querySelector('.hero-figure')
        || hero.querySelector('.article-meta')
        || hero.lastElementChild;

      if (anchor && anchor.parentElement) {
        anchor.insertAdjacentElement('afterend', dock);
      } else {
        hero.appendChild(dock);
      }
    }

    bindLivingControls(dock, context);
    applyStoredSourceTrailMode();
    applyStoredReaderMode();
    updateSourceTrailButton();
    updateReaderButton();
  }

  function bindLivingControls(root, context) {
    root.querySelectorAll('[data-living-open]').forEach((button) => {
      if (button.dataset.livingDirectBound === 'true') return;
      button.dataset.livingDirectBound = 'true';
      button.addEventListener('click', (event) => {
        event.preventDefault();
        event.stopPropagation();
        const target = button.getAttribute('data-living-open');
        if (target === 'places') openPlaceLens(context);
        if (target === 'share') openShareStudio(context);
        if (target === 'sources') openSourceBoard(context);
        if (target === 'timeline') openTimeline(context);
        if (target === 'entities') openEntityDrawer(context);
        if (target === 'relationships') openRelationshipWeb(context);
      });
    });

    root.querySelectorAll('[data-living-action]').forEach((button) => {
      if (button.dataset.livingDirectBound === 'true') return;
      button.dataset.livingDirectBound = 'true';
      button.addEventListener('click', (event) => {
        event.preventDefault();
        event.stopPropagation();
        handleLivingAction(button.getAttribute('data-living-action'));
      });
    });
  }

  function installSocialRailEnhancements(context) {
    document.querySelectorAll('[data-living-sidecar]').forEach((node) => node.remove());
    return;
    if (document.querySelector('.press-social-feature')) return;

    const asideStack = context.article.querySelector('.article-aside .sticky-stack') || context.article.querySelector('.article-aside');
    if (!asideStack || asideStack.querySelector('[data-living-sidecar]')) return;

    const sidecar = document.createElement('section');
    sidecar.className = 'info-box press-living-sidecar';
    sidecar.setAttribute('data-living-sidecar', '');
    sidecar.innerHTML = `
      <h2>Story rail</h2>
      <p>This rail is generated from the article on this page. It does not imitate a social platform.</p>
      <div class="press-living-sidecar__actions">
        <button type="button" data-living-open="sources">Source constellation</button>
        <button type="button" data-living-open="places">Map the places</button>
        <button type="button" data-living-open="relationships">Actor web</button>
        <button type="button" data-living-open="share">Make share card</button>
      </div>
    `;
    asideStack.appendChild(sidecar);
    bindLivingControls(sidecar, context);
  }

  function installArticleAtmosphere(context) {
    let beat = document.querySelector('[data-living-current-beat]');
    if (!beat) {
      beat = document.createElement('div');
      beat.className = 'press-current-beat';
      beat.setAttribute('data-living-current-beat', '');
      document.body.appendChild(beat);
    }

    beat.innerHTML = `
      <button class="press-current-beat__button" type="button" data-living-top aria-label="Back to top">
        <span class="press-current-beat__kicker">Reading</span>
        <strong>Opening</strong>
        <em data-living-progress-text>0%</em>
        <span class="press-current-beat__top" aria-hidden="true"><b>↑</b> Top</span>
      </button>
    `;
    document.body.classList.add('has-living-current-beat');
    bindCurrentBeatTop(beat);

    let queued = false;
    const update = () => {
      queued = false;
      updateCurrentBeat(context);
    };

    window.addEventListener('scroll', () => {
      if (queued) return;
      queued = true;
      window.requestAnimationFrame(update);
    }, { passive: true });

    document.addEventListener('mouseover', (event) => {
      const ref = event.target.closest(SOURCE_NOTE_REF_SELECTOR);
      const id = sourceAnchorId(ref);
      if (!id) return;
      highlightSource(id, { soft: true });
    });

    document.addEventListener('mouseout', (event) => {
      if (!event.target.closest(SOURCE_NOTE_REF_SELECTOR)) return;
      if (Date.now() - lastSourceClickAt < 900) return;
      clearSourceHighlights();
    });

    update();
  }

  function bindCurrentBeatTop(widget) {
    const button = widget.querySelector('[data-living-top]');
    if (!button || button.dataset.livingTopBound === 'true') return;

    button.dataset.livingTopBound = 'true';
    button.addEventListener('click', () => {
      window.scrollTo({
        top: 0,
        behavior: livingPrefersReducedMotion() ? 'auto' : 'smooth',
      });
    });
  }

  function livingPrefersReducedMotion() {
    return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }

  function bindGlobalLivingActions() {
    document.addEventListener('click', function onLivingClick(event) {
      const opener = event.target.closest('[data-living-open]');
      if (opener) {
        event.preventDefault();
        const context = activeArticleContext;
        const target = opener.getAttribute('data-living-open');
        if (!context) return;
        if (target === 'places') openPlaceLens(context);
        if (target === 'share') openShareStudio(context);
        if (target === 'sources') openSourceBoard(context);
        if (target === 'timeline') openTimeline(context);
        if (target === 'entities') openEntityDrawer(context);
        if (target === 'relationships') openRelationshipWeb(context);
        return;
      }

      const number = event.target.closest('[data-living-number-chip]');
      if (number) {
        event.preventDefault();
        if (activeArticleContext) openNumberLens(activeArticleContext, number);
        return;
      }

      const close = event.target.closest('[data-living-close], [data-living-drawer-scrim]');
      if (close) {
        event.preventDefault();
        closeLivingDrawer(close.closest('[data-living-drawer]'));
        return;
      }

      const action = event.target.closest('[data-living-action]');
      if (action) {
        event.preventDefault();
        handleLivingAction(action.getAttribute('data-living-action'));
        return;
      }

      const entity = event.target.closest('[data-living-entity-id]');
      if (entity) {
        event.preventDefault();
        if (activeArticleContext) openEntityDrawer(activeArticleContext, entity.getAttribute('data-living-entity-id'));
        return;
      }

      const inlineSource = event.target.closest(SOURCE_NOTE_REF_SELECTOR);
      const inlineSourceId = sourceAnchorId(inlineSource);
      if (inlineSourceId) {
        event.preventDefault();
        if (history?.replaceState) history.replaceState(null, '', `#${inlineSourceId}`);
        lastSourceClickAt = Date.now();
        highlightSource(inlineSourceId);
        return;
      }

      const source = event.target.closest('[data-living-source-id]');
      if (source) {
        event.preventDefault();
        lastSourceClickAt = Date.now();
        highlightSource(source.getAttribute('data-living-source-id'));
        return;
      }

      const scrollTarget = event.target.closest('[data-living-scroll-target]');
      if (scrollTarget) {
        event.preventDefault();
        scrollToAnchor(scrollTarget.getAttribute('data-living-scroll-target'));
      }
    });

    document.addEventListener('keydown', function onLivingKeydown(event) {
      if (event.key !== 'Escape') return;
      document.querySelectorAll('[data-living-drawer]:not([hidden])').forEach(closeLivingDrawer);
    });
  }

  function handleLivingAction(action) {
    const context = activeArticleContext;
    if (!context) return;

    if (action === 'listen') {
      const play = document.querySelector('[data-listen-play]');
      if (play) play.click();
      return;
    }

    if (action === 'reader-mode') {
      cycleReaderMode();
      return;
    }

    if (action === 'source-trail') {
      toggleSourceTrailMode();
      return;
    }

    if (action === 'follow-topic') {
      toggleFollowTopic(context.story.section);
      const button = document.querySelector('[data-living-action="follow-topic"]');
      if (button) button.textContent = isFollowingTopic(context.story.section) ? 'Following' : 'Follow Topic';
    }
  }

  function installArticleIntelligence(context) {
    installEvidenceAnnotations(context);
    installNumberChips(context);
    applyStoredSourceTrailMode();
    updateSourceTrailButton();
  }

  function collectEvidenceMoments(context) {
    const nodes = collectStoryEvidenceNodes(context.body);

    return nodes.map((node, index) => {
      const id = ensureLivingNodeId(node, 'living-evidence', index + 1);
      const text = cleanText(node.textContent || '');
      const haystack = normalizeText(text);
      const sourceIds = sourceIdsForNode(node);
      const numbers = extractNumberTokens(text);
      const places = context.places.filter((place) => place.names.some((name) => phraseInText(haystack, name))).slice(0, 3);
      const entities = context.entities.filter((entity) => entity.aliases.some((alias) => phraseInText(haystack, alias))).slice(0, 4);
      const quoted = node.matches('blockquote') || /[“”"]/.test(text);
      const score = Math.min(100,
        (sourceIds.length * 26)
        + (numbers.length * 16)
        + (places.length * 13)
        + (entities.length * 8)
        + (quoted ? 10 : 0)
        + Math.min(10, Math.round(text.length / 220))
      );
      const type = primaryEvidenceType({ sourceIds, numbers, places, entities, quoted });

      return {
        id,
        node,
        index,
        score,
        heat: Math.max(.14, Math.min(1, score / 100)),
        type,
        sourceIds,
        numbers,
        places,
        entities,
        quoted,
        summary: shorten(text, 150),
      };
    }).filter((moment) => moment.score >= 18)
      .sort((a, b) => b.score - a.score)
      .slice(0, 12)
      .sort((a, b) => a.index - b.index);
  }

  function installEvidenceAnnotations(context) {
    if (context.body.dataset.livingEvidenceAnnotated === 'true') return;
    context.body.dataset.livingEvidenceAnnotated = 'true';

    context.evidence.forEach((moment) => {
      moment.node.classList.add('press-evidence-node');
      moment.node.setAttribute('data-living-evidence-kind', moment.type.toLowerCase());
      moment.node.style.setProperty('--evidence-heat', moment.heat.toFixed(2));

      if (moment.node.querySelector(':scope > .press-evidence-tags')) return;
      const tags = document.createElement('span');
      tags.className = 'press-evidence-tags';
      tags.setAttribute('aria-label', 'Source trail tags');
      tags.innerHTML = renderEvidenceTags(moment);
      moment.node.appendChild(tags);
    });
  }

  function installNumberChips(context) {
    if (context.body.dataset.livingNumbersWrapped === 'true') return;
    context.body.dataset.livingNumbersWrapped = 'true';

    const walker = document.createTreeWalker(context.body, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        if (!node.nodeValue || !NUMBER_TOKEN_PATTERN.test(node.nodeValue)) {
          NUMBER_TOKEN_PATTERN.lastIndex = 0;
          return NodeFilter.FILTER_REJECT;
        }
        NUMBER_TOKEN_PATTERN.lastIndex = 0;
        const parent = node.parentElement;
        if (!parent) return NodeFilter.FILTER_REJECT;
        if (parent.closest('a, button, sup, script, style, .press-evidence-tags, .press-static-post, .source-list, .source-notes, .article-sources, .related-block, .share-row, [data-living-article-dock], [data-living-drawer]')) {
          return NodeFilter.FILTER_REJECT;
        }
        if (!parent.closest('p, li, blockquote')) return NodeFilter.FILTER_REJECT;
        if (parent.closest('#source-notes, .source-notes, .article-sources, .related-block, [data-living-drawer]')) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      },
    });

    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);

    const state = { total: 0, max: 24 };
    for (const node of nodes) {
      if (state.total >= state.max) break;
      wrapTextNodeWithNumbers(node, context, state);
    }
  }

  function wrapTextNodeWithNumbers(textNode, context, state) {
    const text = textNode.nodeValue;
    const fragment = document.createDocumentFragment();
    let cursor = 0;
    let matched = false;
    let local = 0;
    NUMBER_TOKEN_PATTERN.lastIndex = 0;

    for (const match of text.matchAll(NUMBER_TOKEN_PATTERN)) {
      if (state.total >= state.max || local >= 2) break;
      const prefix = match[1] || '';
      const value = cleanNumberLabel(match[2]);
      if (!value || isDullNumber(value)) continue;

      const start = match.index + prefix.length;
      const end = start + match[2].length;
      if (start < cursor) continue;

      fragment.appendChild(document.createTextNode(text.slice(cursor, start)));
      fragment.appendChild(buildNumberChip(value, text, textNode.parentElement, context, state.total + 1));
      cursor = end;
      matched = true;
      local += 1;
      state.total += 1;
    }

    if (!matched) return false;
    fragment.appendChild(document.createTextNode(text.slice(cursor)));
    textNode.parentNode.replaceChild(fragment, textNode);
    return true;
  }

  function buildNumberChip(value, contextText, parent, context, index) {
    const owner = parent?.closest('p, li, blockquote') || parent;
    const id = ensureLivingNodeId(owner, 'living-number', index);
    const chip = document.createElement('button');
    chip.type = 'button';
    chip.className = 'press-number-chip';
    chip.setAttribute('data-living-number-chip', '');
    chip.setAttribute('data-living-number', value);
    chip.setAttribute('data-living-number-kind', numberKind(value, contextText));
    chip.setAttribute('data-living-number-context', shorten(contextText, 190));
    chip.setAttribute('data-living-number-node', id);
    chip.setAttribute('aria-label', `Open number lens for ${value}`);
    chip.textContent = value;
    return chip;
  }

  function openRelationshipWeb(context) {
    const web = context.relationships?.nodes?.length ? context.relationships : buildRelationshipWeb(context);
    const body = web.nodes.length ? renderRelationshipWeb(web) : `
      <div class="press-empty-state">
        <h3>No actor web yet</h3>
        <p>Add more entity names to the article or the local entity library and this panel will draw relationships from paragraph proximity.</p>
      </div>
    `;

    openLivingDrawer('relationships', 'Actor Relationship Web', 'A static relationship map built from entities that appear near each other in this article.', body);
  }

  function openNumberLens(context, chip) {
    const value = chip.getAttribute('data-living-number') || chip.textContent || '';
    const kind = chip.getAttribute('data-living-number-kind') || 'Signal';
    const nodeId = chip.getAttribute('data-living-number-node') || '';
    const node = nodeId ? document.getElementById(nodeId) : null;
    const sourceIds = node ? sourceIdsForNode(node) : [];
    const nearby = cleanText(chip.getAttribute('data-living-number-context') || node?.textContent || '');
    const body = `
      <div class="press-number-lens">
        <article>
          <p class="press-living-kicker">${escapeHtml(kind)}</p>
          <h3>${escapeHtml(value)}</h3>
          <p>${escapeHtml(numberMeaning(value, kind, nearby))}</p>
        </article>
        <section>
          <h4>Where it appears</h4>
          <p>${escapeHtml(shorten(nearby, 260))}</p>
          <div class="press-number-lens__actions">
            ${nodeId ? `<button type="button" data-living-scroll-target="${escapeAttr(nodeId)}">Jump to paragraph</button>` : ''}
            ${sourceIds.length ? `<button type="button" data-living-source-id="${escapeAttr(sourceIds[0])}">${sourceIds.length === 1 ? 'Open source' : `${sourceIds.length} sources nearby`}</button>` : ''}
          </div>
        </section>
      </div>
    `;

    const drawer = openLivingDrawer('number', 'Number Lens', 'A local stat explainer generated from the sentence around the number.', body);
    drawer.querySelectorAll('[data-living-source-id]').forEach((button) => {
      button.addEventListener('click', (event) => {
        event.preventDefault();
        highlightSource(button.getAttribute('data-living-source-id'));
      });
    });
  }

  function buildRelationshipWeb(context) {
    const nodes = context.entities.slice(0, 9);
    const nodeById = new Map(nodes.map((entity) => [entity.id, entity]));
    const links = new Map();

    collectStoryEvidenceNodes(context.body).forEach((node, index) => {
      const id = ensureLivingNodeId(node, 'living-relationship', index + 1);
      const haystack = normalizeText(node.textContent || '');
      const present = nodes.filter((entity) => entity.aliases.some((alias) => phraseInText(haystack, alias))).slice(0, 5);
      for (let i = 0; i < present.length; i += 1) {
        for (let j = i + 1; j < present.length; j += 1) {
          const pair = [present[i].id, present[j].id].sort();
          const key = pair.join('|');
          const link = links.get(key) || {
            a: nodeById.get(pair[0]),
            b: nodeById.get(pair[1]),
            count: 0,
            ids: [],
            summary: '',
          };
          link.count += 1;
          link.ids.push(id);
          if (!link.summary) link.summary = shorten(cleanText(node.textContent), 155);
          links.set(key, link);
        }
      }
    });

    if (!links.size && nodes.length > 1) {
      nodes.slice(1).forEach((entity, index) => {
        const previous = nodes[index];
        links.set([previous.id, entity.id].sort().join('|'), {
          a: previous,
          b: entity,
          count: 1,
          ids: [],
          summary: 'These actors share the same article frame, even if they do not appear in the same paragraph.',
        });
      });
    }

    return {
      nodes,
      links: Array.from(links.values())
        .filter((link) => link.a && link.b)
        .sort((a, b) => b.count - a.count || a.a.name.localeCompare(b.a.name))
        .slice(0, 12),
    };
  }

  function renderRelationshipWeb(web) {
    const positions = relationshipPositions(web.nodes.length);
    return `
      <div class="press-relationship-web">
        <div class="press-relationship-map" aria-label="Actor relationship map">
          <svg aria-hidden="true" viewBox="0 0 100 100" preserveAspectRatio="none">
            ${web.links.map((link) => {
              const a = positions[web.nodes.findIndex((node) => node.id === link.a.id)];
              const b = positions[web.nodes.findIndex((node) => node.id === link.b.id)];
              if (!a || !b) return '';
              const strength = Math.min(1, .25 + link.count * .18);
              return `<line x1="${a.x}" y1="${a.y}" x2="${b.x}" y2="${b.y}" style="--line-opacity:${strength.toFixed(2)};--stroke-width:${(.6 + (2 * strength)).toFixed(2)}px"></line>`;
            }).join('')}
          </svg>
          ${web.nodes.map((entity, index) => `
            <button type="button" class="press-relationship-node" data-living-entity-id="${escapeAttr(entity.id)}" style="--x:${positions[index].x}%;--y:${positions[index].y}%">
              <span>${escapeHtml(entity.type)}</span>
              <strong>${escapeHtml(entity.name)}</strong>
            </button>
          `).join('')}
        </div>
        <div class="press-relationship-links">
          ${web.links.map((link) => `
            <article>
              <p class="press-living-kicker">${escapeHtml(link.count > 1 ? `${link.count} shared beats` : 'Shared beat')}</p>
              <h3>${escapeHtml(link.a.name)} &harr; ${escapeHtml(link.b.name)}</h3>
              <p>${escapeHtml(link.summary)}</p>
              ${link.ids[0] ? `<button type="button" data-living-scroll-target="${escapeAttr(link.ids[0])}">Jump to evidence</button>` : ''}
            </article>
          `).join('')}
        </div>
      </div>
    `;
  }

  function collectStoryEvidenceNodes(body) {
    return Array.from(body.querySelectorAll('p, li, blockquote')).filter((node) => {
      if (node.closest('#source-notes, .source-notes, .article-sources, .related-block, [data-living-drawer], [data-living-article-dock]')) return false;
      const text = cleanText(node.textContent || '');
      return text.length >= 55;
    });
  }

  function sourceIdsForNode(node) {
    return Array.from(node.querySelectorAll('.source-ref a[href^="#"], a.source-label[href^="#"]'))
      .map((link) => (link.getAttribute('href') || '').replace(/^#/, ''))
      .filter(Boolean);
  }

  function ensureLivingNodeId(node, prefix, index = 1) {
    if (!node) return `${prefix}-${index}`;
    if (node.id) return node.id;

    const base = `${prefix}-${index}`;
    let candidate = base;
    let attempt = 2;
    while (document.getElementById(candidate)) {
      candidate = `${base}-${attempt}`;
      attempt += 1;
    }
    node.id = candidate;
    return candidate;
  }

  function extractNumberTokens(text) {
    const values = [];
    NUMBER_TOKEN_PATTERN.lastIndex = 0;
    for (const match of String(text || '').matchAll(NUMBER_TOKEN_PATTERN)) {
      const value = cleanNumberLabel(match[2]);
      if (value && !isDullNumber(value) && !values.includes(value)) values.push(value);
    }
    NUMBER_TOKEN_PATTERN.lastIndex = 0;
    return values.slice(0, 4);
  }

  function renderEvidenceTags(moment) {
    const tags = [];
    if (moment.sourceIds.length) tags.push(`<button type="button" data-living-source-id="${escapeAttr(moment.sourceIds[0])}">${moment.sourceIds.length} source${moment.sourceIds.length === 1 ? '' : 's'}</button>`);
    if (moment.numbers.length) tags.push(`<button type="button" data-living-scroll-target="${escapeAttr(moment.id)}">${moment.numbers.length} stat${moment.numbers.length === 1 ? '' : 's'}</button>`);
    if (moment.places.length) tags.push(`<button type="button" data-living-open="places">${moment.places.length} place${moment.places.length === 1 ? '' : 's'}</button>`);
    if (moment.entities.length) tags.push(`<button type="button" data-living-open="relationships">${moment.entities.length} actor${moment.entities.length === 1 ? '' : 's'}</button>`);
    if (moment.quoted) tags.push(`<button type="button" data-living-scroll-target="${escapeAttr(moment.id)}">context</button>`);
    return tags.join('');
  }

  function primaryEvidenceType(moment) {
    if (moment.sourceIds.length && moment.numbers.length) return 'Proof';
    if (moment.sourceIds.length) return 'Sources';
    if (moment.numbers.length) return 'Data';
    if (moment.places.length) return 'Places';
    if (moment.entities.length >= 2) return 'Actors';
    if (moment.quoted) return 'Context';
    return 'Signal';
  }

  function relationshipPositions(count) {
    const total = Math.max(1, count);
    return Array.from({ length: total }, (_, index) => {
      const angle = (-90 + (360 / total) * index) * (Math.PI / 180);
      return {
        x: Number((50 + Math.cos(angle) * 37).toFixed(2)),
        y: Number((50 + Math.sin(angle) * 34).toFixed(2)),
      };
    });
  }

  function cleanNumberLabel(value) {
    return cleanText(value).replace(/\s+%/g, '%').replace(/\s+/g, ' ');
  }

  function isDullNumber(value) {
    const text = cleanText(value);
    if (!text) return true;
    if (/^\d{4}$/.test(text)) return true;
    if (/^\d{1,2}$/.test(text) && !/%|[$€£]|percent|million|billion|trillion|barrel|ship|vessel|tank|crew|people|famil|child|export|import|capacity|per day/i.test(text)) return true;
    return false;
  }

  function numberKind(value, contextText) {
    const text = `${value} ${contextText}`.toLowerCase();
    if (/[$€£]|price|cost|barrel|premium|bill/.test(text)) return 'Price signal';
    if (/%|percent|share|exports|imports/.test(text)) return 'Share';
    if (/barrel|tanker|vessel|ship|crew|per day/.test(text)) return 'Flow';
    if (/million|billion|trillion|people|famil|children/.test(text)) return 'Scale';
    if (/capacity|gigawatt|megawatt|kilometer|mile|ton/.test(text)) return 'Capacity';
    return 'Stat';
  }

  function numberMeaning(value, kind, nearby) {
    const lower = `${value} ${nearby}`.toLowerCase();
    if (kind === 'Price signal') return 'This number turns the story into a household or market signal: it shows where a geopolitical or institutional pressure becomes cost.';
    if (kind === 'Share') return 'This share tells you how much of a larger system depends on the fact in this sentence, which is why the paragraph carries extra weight.';
    if (kind === 'Flow') return 'This is a movement number: ships, energy, cargo, or capacity. Flow numbers are where the article becomes logistical instead of abstract.';
    if (kind === 'Scale') return 'This number establishes scale. It helps separate a vivid anecdote from a system large enough to change outcomes.';
    if (kind === 'Capacity') return 'This is a constraint number. It shows how much room the system has before pressure starts showing up somewhere else.';
    if (/days|weeks|months/.test(lower)) return 'This number is a clock. It tells you how long the story can stay unstable before the next consequence arrives.';
    return 'This stat is treated as a signal inside the article: tap back to the paragraph to see what claim it supports.';
  }

  function openPlaceLens(context) {
    const places = context.places;
    const first = places[0];
    const body = places.length ? `
      <div class="press-place-lens">
        <div class="press-place-lens__map">
          <iframe title="OpenStreetMap preview for ${escapeAttr(first.label)}" src="${escapeAttr(osmEmbedUrl(first))}" loading="lazy"></iframe>
        </div>
        <div class="press-place-lens__cards">
          ${places.map(renderPlaceCard).join('')}
        </div>
      </div>
    ` : `
      <div class="press-empty-state">
        <h3>No mapped places found yet</h3>
        <p>This article did not match the local place dictionary. Add a place name and coordinates to the static library to make this lens light up.</p>
      </div>
    `;

    openLivingDrawer('places', 'Place Lens', 'Mapped places mentioned by the article, with no key or API call.', body);
  }

  function openShareStudio(context) {
    const caption = buildShareCaption(context.story);
    const body = `
      <div class="press-share-studio">
        <div class="press-share-studio__canvas-wrap">
          <canvas width="1080" height="1080" data-living-share-canvas></canvas>
        </div>
        <div class="press-share-studio__controls">
          <div class="press-share-studio__formats" role="group" aria-label="Share card format">
            <button type="button" class="is-active" data-share-format="square">Square</button>
            <button type="button" data-share-format="story">Story</button>
            <button type="button" data-share-format="quote">Quote</button>
          </div>
          <label class="press-share-studio__caption">
            Caption
            <textarea data-share-caption rows="8">${escapeHtml(caption)}</textarea>
          </label>
          <div class="press-share-studio__buttons">
            <button type="button" data-share-copy>Copy caption</button>
            <button type="button" data-share-download>Download PNG</button>
          </div>
          <p class="press-share-studio__note">Generated in your browser from local article data. No network rendering service.</p>
        </div>
      </div>
    `;

    const drawer = openLivingDrawer('share', 'Article Share Studio', 'Generate square, story, and quote cards locally in the browser.', body);
    bindShareStudio(context, drawer);
  }

  function openSourceBoard(context) {
    const clusters = clusterSources(context.sources);
    const body = context.sources.length ? `
      <div class="press-source-constellation">
        <div class="press-source-constellation__summary">
          ${SOURCE_CLUSTER_ORDER.filter((name) => clusters[name]?.length).map((name) => `
            <div>
              <span>${escapeHtml(name)}</span>
              <strong>${clusters[name].length}</strong>
            </div>
          `).join('')}
        </div>
        <div class="press-source-constellation__grid">
          ${SOURCE_CLUSTER_ORDER.filter((name) => clusters[name]?.length).map((name) => `
            <section>
              <h3>${escapeHtml(name)}</h3>
              <div class="press-source-constellation__items">
                ${clusters[name].map(renderSourceButton).join('')}
              </div>
            </section>
          `).join('')}
        </div>
      </div>
    ` : `
      <div class="press-empty-state">
        <h3>No source notes found</h3>
        <p>The source board appears once the story has a source list or source notes.</p>
      </div>
    `;

    const drawer = openLivingDrawer('sources', 'Source Constellation', 'A local evidence board grouped from the article source notes.', body);
    drawer.querySelectorAll('[data-living-source-id]').forEach((button) => {
      button.addEventListener('click', (event) => {
        event.preventDefault();
        highlightSource(button.getAttribute('data-living-source-id'));
      });
    });
  }

  function openTimeline(context) {
    const body = context.beats.length ? `
      <div class="press-story-timeline">
        ${context.beats.map((beat, index) => `
          <button type="button" data-living-scroll-target="${escapeAttr(beat.id)}">
            <span>${String(index + 1).padStart(2, '0')}</span>
            <strong>${escapeHtml(beat.title)}</strong>
            <em>${escapeHtml(beat.summary)}</em>
          </button>
        `).join('')}
      </div>
    ` : `
      <div class="press-empty-state">
        <h3>No timeline beats yet</h3>
        <p>Add article section headings and this timeline will turn them into a navigable story path.</p>
      </div>
    `;

    const drawer = openLivingDrawer('timeline', 'Story Timeline', 'A scrollable beat map generated from this article.', body);
    drawer.querySelectorAll('[data-living-scroll-target]').forEach((button) => {
      button.addEventListener('click', (event) => {
        event.preventDefault();
        scrollToAnchor(button.getAttribute('data-living-scroll-target'));
      });
    });
  }

  function openEntityDrawer(context, activeId = '') {
    const body = context.entities.length ? `
      <div class="press-entity-board">
        ${context.entities.map((entity) => {
          const related = relatedStoriesForEntity(entity, context.relatedStories, context.story.url);
          return `
            <article class="press-entity-card${entity.id === activeId ? ' is-active' : ''}" id="entity-card-${escapeAttr(entity.id)}">
              <p class="press-living-kicker">${escapeHtml(entity.type)}</p>
              <h3>${escapeHtml(entity.name)}</h3>
              <p>${escapeHtml(entity.summary)}</p>
              <strong>Why it matters here</strong>
              <p>${escapeHtml(entity.why)}</p>
              ${related.length ? `<div class="press-entity-card__related">${related.map((story) => `<a href="${escapeAttr(story.url)}">${escapeHtml(story.title)}</a>`).join('')}</div>` : ''}
            </article>
          `;
        }).join('')}
      </div>
    ` : `
      <div class="press-empty-state">
        <h3>No entity cards matched</h3>
        <p>Add names to the local entity library and they will appear here with inline article chips.</p>
      </div>
    `;

    const drawer = openLivingDrawer('entities', 'Entity Cards', 'People, places, companies, institutions, and ideas detected from the article.', body);
    if (activeId) {
      const card = drawer.querySelector(`#entity-card-${cssEscape(activeId)}`);
      if (card) card.scrollIntoView({ block: 'center', behavior: 'smooth' });
    }
  }

  function openLivingDrawer(id, title, intro, content) {
    let drawer = document.querySelector(`[data-living-drawer="${id}"]`);
    if (!drawer) {
      drawer = document.createElement('aside');
      drawer.className = 'press-living-drawer';
      drawer.setAttribute('data-living-drawer', id);
      drawer.setAttribute('role', 'dialog');
      drawer.setAttribute('aria-modal', 'true');
      drawer.hidden = true;
      drawer.innerHTML = `
        <button class="press-living-drawer__scrim" type="button" data-living-drawer-scrim aria-label="Close panel"></button>
        <div class="press-living-drawer__panel" role="document">
          <div class="press-living-drawer__header">
            <div>
              <p class="press-living-kicker" data-living-drawer-kicker>Living article</p>
              <h2 data-living-drawer-title></h2>
              <p data-living-drawer-intro></p>
            </div>
            <button class="press-living-drawer__close" type="button" data-living-close>Close</button>
          </div>
          <div class="press-living-drawer__body" data-living-drawer-body></div>
        </div>
      `;
      document.body.appendChild(drawer);
    }

    drawer.querySelector('[data-living-drawer-title]').textContent = title;
    drawer.querySelector('[data-living-drawer-intro]').textContent = intro;
    drawer.querySelector('[data-living-drawer-body]').innerHTML = content;
    drawer.querySelectorAll('[data-living-close], [data-living-drawer-scrim]').forEach((button) => {
      if (button.dataset.livingCloseBound === 'true') return;
      button.dataset.livingCloseBound = 'true';
      button.addEventListener('click', (event) => {
        event.preventDefault();
        closeLivingDrawer(drawer);
      });
    });

    lastFocusedElement = document.activeElement;
    drawer.hidden = false;
    document.documentElement.classList.add('press-living-drawer-open');
    drawer.querySelector('[data-living-close]')?.focus({ preventScroll: true });
    return drawer;
  }

  function closeLivingDrawer(drawer) {
    if (!drawer) return;
    drawer.hidden = true;
    document.documentElement.classList.remove('press-living-drawer-open');
    if (lastFocusedElement && typeof lastFocusedElement.focus === 'function') {
      lastFocusedElement.focus({ preventScroll: true });
    }
  }

  function bindShareStudio(context, drawer) {
    const canvas = drawer.querySelector('[data-living-share-canvas]');
    const caption = drawer.querySelector('[data-share-caption]');
    let currentFormat = 'square';

    drawShareCanvas(context, canvas, currentFormat);

    drawer.querySelectorAll('[data-share-format]').forEach((button) => {
      button.addEventListener('click', () => {
        currentFormat = button.getAttribute('data-share-format') || 'square';
        drawer.querySelectorAll('[data-share-format]').forEach((item) => item.classList.toggle('is-active', item === button));
        drawShareCanvas(context, canvas, currentFormat);
      });
    });

    drawer.querySelector('[data-share-copy]')?.addEventListener('click', async (event) => {
      const button = event.currentTarget;
      try {
        await navigator.clipboard.writeText(caption.value);
        button.textContent = 'Copied';
        window.setTimeout(() => { button.textContent = 'Copy caption'; }, 1500);
      } catch (_) {
        caption.focus();
        caption.select();
        let copied = false;
        try {
          copied = document.execCommand && document.execCommand('copy');
        } catch (__) {
          copied = false;
        }
        button.textContent = copied ? 'Copied' : 'Caption selected';
        window.setTimeout(() => { button.textContent = 'Copy caption'; }, 1800);
      }
    });

    drawer.querySelector('[data-share-download]')?.addEventListener('click', () => {
      const filename = `${slugify(context.story.title || 'the-press-card')}-${currentFormat}.png`;
      if (canvas.toBlob) {
        canvas.toBlob((blob) => {
          if (!blob) return;
          const url = URL.createObjectURL(blob);
          triggerDownload(url, filename);
          window.setTimeout(() => URL.revokeObjectURL(url), 2500);
        }, 'image/png');
      } else {
        triggerDownload(canvas.toDataURL('image/png'), filename);
      }
    });
  }

  async function drawShareCanvas(context, canvas, format) {
    if (!canvas) return;

    const story = context.story;
    const isStory = format === 'story';
    const isQuote = format === 'quote';
    const width = 1080;
    const height = isStory ? 1920 : 1080;
    canvas.width = width;
    canvas.height = height;

    const ctx = canvas.getContext('2d');
    const accent = sectionAccent(story.section);
    const ink = '#1d232d';
    const paper = '#f7f1e5';

    ctx.fillStyle = paper;
    ctx.fillRect(0, 0, width, height);
    drawCardPattern(ctx, width, height, accent);

    const imageSrc = story.image || context.hero?.querySelector('img')?.getAttribute('src') || '';
    if (imageSrc && !isQuote) {
      try {
        const img = await loadImage(new URL(imageSrc, window.location.href).href);
        const imageHeight = isStory ? 760 : 430;
        drawImageCover(ctx, img, 0, 0, width, imageHeight);
        ctx.fillStyle = 'rgba(0,0,0,.34)';
        ctx.fillRect(0, 0, width, imageHeight);
      } catch (_) {
        drawImageFallback(ctx, width, isStory ? 760 : 430, accent);
      }
    }

    const margin = 86;
    const top = isQuote ? 112 : (isStory ? 835 : 500);
    ctx.fillStyle = isQuote ? accent : '#ffffff';
    ctx.font = '900 34px Arial, sans-serif';
    ctx.letterSpacing = '0px';
    ctx.fillText('THE PRESS', margin, isQuote ? 82 : 68);

    ctx.fillStyle = isQuote ? '#596273' : '#f7f1e5';
    ctx.font = '700 30px Arial, sans-serif';
    ctx.fillText(String(story.section || 'News').toUpperCase(), margin, top);

    if (isQuote) {
      const quote = bestQuote(context);
      ctx.fillStyle = ink;
      ctx.font = '900 72px Georgia, serif';
      wrapCanvasText(ctx, quote, margin, 240, width - margin * 2, 84, 8);
      ctx.fillStyle = '#667085';
      ctx.font = '700 30px Arial, sans-serif';
      wrapCanvasText(ctx, story.title, margin, height - 210, width - margin * 2, 38, 3);
    } else {
      ctx.fillStyle = ink;
      ctx.font = isStory ? '900 86px Georgia, serif' : '900 64px Georgia, serif';
      const titleBottom = wrapCanvasText(ctx, story.title, margin, top + 86, width - margin * 2, isStory ? 96 : 74, isStory ? 8 : 5);
      ctx.fillStyle = '#4f5a69';
      ctx.font = isStory ? '400 38px Georgia, serif' : '400 31px Georgia, serif';
      wrapCanvasText(ctx, story.dek || '', margin, titleBottom + 42, width - margin * 2, isStory ? 52 : 43, isStory ? 6 : 4);
    }

    ctx.fillStyle = accent;
    ctx.fillRect(margin, height - 138, 156, 8);
    ctx.fillStyle = '#3a4250';
    ctx.font = '700 28px Arial, sans-serif';
    ctx.fillText('thepress.live', margin, height - 82);
    ctx.textAlign = 'right';
    ctx.fillText(shorten(story.published || story.readTime || 'Static edition', 42), width - margin, height - 82);
    ctx.textAlign = 'left';
  }

  function drawCardPattern(ctx, width, height, accent) {
    ctx.save();
    ctx.globalAlpha = 0.16;
    ctx.fillStyle = accent;
    ctx.beginPath();
    ctx.arc(width - 140, 170, 260, 0, Math.PI * 2);
    ctx.fill();
    ctx.globalAlpha = 0.1;
    ctx.fillStyle = '#24706d';
    ctx.fillRect(0, height - 220, width, 220);
    ctx.globalAlpha = 0.08;
    ctx.strokeStyle = '#1d232d';
    ctx.lineWidth = 3;
    for (let x = -200; x < width + 300; x += 86) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x + 420, height);
      ctx.stroke();
    }
    ctx.restore();
  }

  function drawImageFallback(ctx, width, height, accent) {
    ctx.save();
    const gradient = ctx.createLinearGradient(0, 0, width, height);
    gradient.addColorStop(0, accent);
    gradient.addColorStop(1, '#25314a');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);
    ctx.fillStyle = 'rgba(255,255,255,.16)';
    ctx.fillRect(80, 80, width - 160, height - 160);
    ctx.restore();
  }

  function loadImage(src) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve(img);
      img.onerror = reject;
      img.src = src;
    });
  }

  function drawImageCover(ctx, img, x, y, width, height) {
    const scale = Math.max(width / img.naturalWidth, height / img.naturalHeight);
    const drawWidth = img.naturalWidth * scale;
    const drawHeight = img.naturalHeight * scale;
    ctx.drawImage(img, x + (width - drawWidth) / 2, y + (height - drawHeight) / 2, drawWidth, drawHeight);
  }

  function wrapCanvasText(ctx, text, x, y, maxWidth, lineHeight, maxLines) {
    const words = String(text || '').split(/\s+/).filter(Boolean);
    let line = '';
    let lines = 0;
    let cursor = y;

    words.forEach((word) => {
      const test = line ? `${line} ${word}` : word;
      if (ctx.measureText(test).width > maxWidth && line) {
        if (lines < maxLines) ctx.fillText(line, x, cursor);
        cursor += lineHeight;
        lines += 1;
        line = word;
      } else {
        line = test;
      }
    });

    if (line && lines < maxLines) {
      ctx.fillText(lines === maxLines - 1 && words.length ? shorten(line, 62) : line, x, cursor);
      cursor += lineHeight;
    }

    return cursor;
  }

  function detectPlaces(text, story) {
    const storyText = story.matchedCurrentStory ? `${story.title} ${story.dek} ${(story.keywords || []).join(' ')}` : `${story.title} ${story.dek}`;
    const haystack = normalizeText(`${storyText} ${text}`);
    const seen = new Set();
    return PLACE_LIBRARY.filter((place) => {
      if (seen.has(place.id)) return false;
      const matched = place.names.some((name) => phraseInText(haystack, name));
      if (matched) seen.add(place.id);
      return matched;
    }).slice(0, 8);
  }

  function detectEntities(text) {
    const haystack = normalizeText(text);
    return ENTITY_LIBRARY.filter((entity) => entity.aliases.some((alias) => phraseInText(haystack, alias))).slice(0, 14);
  }

  function wrapEntityMentions(context) {
    if (!context.entities.length || context.body.dataset.livingEntitiesWrapped === 'true') return;
    context.body.dataset.livingEntitiesWrapped = 'true';

    const entityByAlias = [];
    context.entities.forEach((entity) => {
      entity.aliases.forEach((alias) => {
        entityByAlias.push({ entity, alias });
      });
    });
    entityByAlias.sort((a, b) => b.alias.length - a.alias.length);

    const counts = new Map();
    let total = 0;
    const nodes = [];
    const walker = document.createTreeWalker(context.body, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        if (!node.nodeValue || !node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
        const parent = node.parentElement;
        if (!parent) return NodeFilter.FILTER_REJECT;
        if (parent.closest('a, button, sup, script, style, .press-static-post, .source-list, .source-notes, .article-sources, .related-block, .share-row, [data-living-article-dock], [data-living-drawer]')) {
          return NodeFilter.FILTER_REJECT;
        }
        if (!parent.closest('p, li, blockquote')) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      },
    });

    while (walker.nextNode()) nodes.push(walker.currentNode);

    for (const node of nodes) {
      if (total >= 18) break;
      for (const item of entityByAlias) {
        if ((counts.get(item.entity.id) || 0) >= 2) continue;
        if (wrapTextNodeWithEntity(node, item.entity, item.alias)) {
          counts.set(item.entity.id, (counts.get(item.entity.id) || 0) + 1);
          total += 1;
          break;
        }
      }
    }
  }

  function wrapTextNodeWithEntity(textNode, entity, alias) {
    const text = textNode.nodeValue;
    const pattern = new RegExp(`(^|[^A-Za-z0-9])(${escapeRegExp(alias)})(?=$|[^A-Za-z0-9])`, 'i');
    const match = text.match(pattern);
    if (!match) return false;

    const start = match.index + match[1].length;
    const end = start + match[2].length;
    const fragment = document.createDocumentFragment();
    const before = text.slice(0, start);
    const exact = text.slice(start, end);
    const after = text.slice(end);

    if (before) fragment.appendChild(document.createTextNode(before));
    const chip = document.createElement('button');
    chip.type = 'button';
    chip.className = 'press-entity-chip';
    chip.setAttribute('data-living-entity-id', entity.id);
    chip.setAttribute('aria-label', `Open entity card for ${entity.name}`);
    chip.textContent = exact;
    fragment.appendChild(chip);
    if (after) fragment.appendChild(document.createTextNode(after));

    textNode.parentNode.replaceChild(fragment, textNode);
    return true;
  }

  function collectArticleSources(article) {
    const selectors = [
      '#source-notes .source-list li',
      '#source-notes li',
      '.article-sources li',
      '.source-notes li',
      '.source-list li',
    ];
    const seenNodes = new Set();
    const seenKeys = new Set();
    const sources = [];

    selectors.forEach((selector) => {
      article.querySelectorAll(selector).forEach((item) => {
        if (seenNodes.has(item)) return;
        seenNodes.add(item);

        const text = cleanText(item.textContent);
        if (!text) return;
        const link = Array.from(item.querySelectorAll('a[href]')).find((candidate) => /^https?:\/\//i.test(candidate.getAttribute('href') || '')) || item.querySelector('a[href]');
        const href = link?.getAttribute('href') || '';
        const key = `${href}|${text}`.toLowerCase();
        if (seenKeys.has(key)) return;
        seenKeys.add(key);

        if (!item.id) item.id = `source-${sources.length + 1}`;
        const label = cleanText(link?.textContent || item.querySelector('strong')?.textContent || `Source ${sources.length + 1}`);
        sources.push({
          id: item.id,
          label,
          detail: cleanText(text.replace(label, '').replace(/^[,.:;\-\s]+/, '')),
          href,
          host: hostnameFromUrl(href),
          cluster: clusterSource({ href, label, detail: text }),
        });
      });
    });

    return sources;
  }

  function numberInlineSourceRefs(context) {
    if (!context?.body || !context.sources?.length) return;
    const sourceNumbers = new Map();
    context.sources.forEach((source, index) => {
      sourceNumbers.set(source.id, {
        label: source.label,
        number: index + 1,
      });
    });

    context.body.querySelectorAll('.source-ref a[href^="#source"]').forEach((link) => {
      const id = (link.getAttribute('href') || '').slice(1);
      const source = sourceNumbers.get(id);
      if (!source) return;
      link.textContent = `[${source.number}]`;
      link.dataset.sourceNumber = String(source.number);
      link.setAttribute('aria-label', `Source ${source.number}: ${source.label || 'source note'}`);
      link.title = `Source ${source.number}${source.label ? `: ${source.label}` : ''}`;
    });
  }

  function hydrateRailSourceLinks(context) {
    if (!context?.body || !context.sources?.length) return;
    const sourcesById = new Map();
    context.sources.forEach((source) => {
      if (!source?.href || !/^https?:\/\//i.test(source.href)) return;
      sourcesById.set(source.id, source);
      sourcesById.set(source.id.replace(/^source-/, ''), source);
    });

    context.body.querySelectorAll('.press-static-post__source a[data-source-id]').forEach((link) => {
      const sourceKey = link.getAttribute('data-source-id') || '';
      const source = sourcesById.get(sourceKey) || sourcesById.get(`source-${sourceKey}`);
      if (!source?.href) return;
      link.setAttribute('href', source.href);
      link.removeAttribute('target');
      link.setAttribute('rel', 'noopener noreferrer');
      link.setAttribute('data-source-external', 'true');
      link.setAttribute('aria-label', `Open external source: ${source.label || cleanText(link.textContent) || 'source'}`);
      link.title = source.label ? `Open ${source.label}` : 'Open external source';
    });
  }

  function collectTimelineBeats(body) {
    const headings = Array.from(body.querySelectorAll('h2, h3')).filter((heading) => {
      if (heading.closest('#source-notes, .source-notes, .article-sources, .related-block, [data-living-drawer]')) return false;
      return cleanText(heading.textContent).length > 2;
    });

    if (!headings.length) {
      return Array.from(body.querySelectorAll('p')).slice(0, 5).map((paragraph, index) => {
        if (!paragraph.id) paragraph.id = `living-beat-${index + 1}`;
        return {
          id: paragraph.id,
          node: paragraph,
          title: index === 0 ? 'Opening' : `Beat ${index + 1}`,
          summary: shorten(cleanText(paragraph.textContent), 135),
        };
      });
    }

    return headings.slice(0, 12).map((heading, index) => {
      if (!heading.id) heading.id = `living-beat-${index + 1}`;
      return {
        id: heading.id,
        node: heading,
        title: cleanText(heading.textContent),
        summary: shorten(cleanText(findNextParagraphText(heading)), 145),
      };
    });
  }

  function findNextParagraphText(heading) {
    let node = heading.nextElementSibling;
    while (node && !/^H[23]$/i.test(node.tagName || '')) {
      if (node.matches?.('p, blockquote, li')) return node.textContent || '';
      node = node.nextElementSibling;
    }
    return '';
  }

  function clusterSources(sources) {
    return sources.reduce((clusters, source) => {
      const cluster = source.cluster || 'Background';
      if (!clusters[cluster]) clusters[cluster] = [];
      clusters[cluster].push(source);
      return clusters;
    }, {});
  }

  function clusterSource(source) {
    const text = `${source.label || ''} ${source.detail || ''}`.toLowerCase();
    const host = hostnameFromUrl(source.href);
    if (/instagram|tiktok|x\.com|twitter|youtube|threads|facebook/.test(host)) return 'Social';
    if (/court|law|docket|supreme|justice|legal/.test(host + ' ' + text)) return 'Legal';
    if (/\.gov$|nasa\.gov|cdc\.gov|census\.gov|bls\.gov|bea\.gov|noaa\.gov|nih\.gov|imf\.org|worldbank\.org|oecd\.org/.test(host)) return 'Public Data';
    if (/michelin|infatuation|timeout|resy|opentable|50best|traveler|thrillist|grubstreet|guide|review/.test(host + ' ' + text)) return 'Guide';
    if (/official|whitehouse|nato\.int|espn|wsop|casamata|eatatla|company|pressroom/.test(host + ' ' + text)) return 'Official';
    if (/eater|reuters|apnews|latimes|nytimes|washingtonpost|guardian|whatnow|gothamist|bonappetit|newyorker|wired|verge|pokernews|reviewjournal/.test(host)) return 'Reporting';
    if (/map|place|neighborhood|location|address|venue/.test(text)) return 'Place';
    return 'Background';
  }

  function renderPlaceCard(place) {
    return `
      <article class="press-place-card">
        <p class="press-living-kicker">${escapeHtml(place.type)}</p>
        <h3>${escapeHtml(place.label)}</h3>
        <p>${escapeHtml(place.scene)}</p>
        <dl>
          <div><dt>Address</dt><dd>${escapeHtml(place.address)}</dd></div>
          <div><dt>Why here</dt><dd>${escapeHtml(place.note)}</dd></div>
        </dl>
        <div class="press-place-card__links">
          <a href="${escapeAttr(googleMapsUrl(place))}" rel="noopener noreferrer" target="_blank">Map</a>
          <a href="${escapeAttr(streetViewUrl(place))}" rel="noopener noreferrer" target="_blank">Street View</a>
          <a href="${escapeAttr(osmUrl(place))}" rel="noopener noreferrer" target="_blank">OpenStreetMap</a>
        </div>
      </article>
    `;
  }

  function renderSourceButton(source) {
    return `
      <button type="button" data-living-source-id="${escapeAttr(source.id)}">
        <span>${escapeHtml(source.host || source.cluster || 'source')}</span>
        <strong>${escapeHtml(shorten(source.label, 78))}</strong>
        ${source.detail ? `<em>${escapeHtml(shorten(source.detail, 110))}</em>` : ''}
      </button>
    `;
  }

  function renderSectionBar(item) {
    const percent = Math.max(8, Math.min(100, item.count * 8));
    return `
      <a href="${escapeAttr(sectionHref(item.section))}">
        <span>${escapeHtml(item.section)}</span>
        <strong>${item.count}</strong>
        <em style="--bar:${percent}%"></em>
      </a>
    `;
  }

  function highlightSource(id, options = {}) {
    clearSourceHighlights();
    if (!id) return;
    const source = document.getElementById(id);
    const sourceKey = id.replace(/^source-/, '');
    const refs = document.querySelectorAll(`.source-ref a[href="#${cssEscape(id)}"], a.source-label[href="#${cssEscape(id)}"], a[data-source-id="${cssEscape(sourceKey)}"], a[data-source-id="${cssEscape(id)}"]`);
    source?.classList.add('is-living-source-highlight');
    refs.forEach((ref) => ref.classList.add('is-living-source-highlight'));
    if (source && !options.soft) {
      source.scrollIntoView({ behavior: 'smooth', block: 'center' });
      window.setTimeout(clearSourceHighlights, 3600);
    }
  }

  function sourceAnchorId(link) {
    if (!link) return '';
    if (link.matches?.('[data-source-external="true"]')) return '';
    const href = link.getAttribute('href') || '';
    if (href.startsWith('#source')) return href.slice(1);
    if (/^https?:\/\//i.test(href)) return '';
    const sourceId = link.getAttribute('data-source-id') || '';
    if (!sourceId) return '';
    return sourceId.startsWith('source-') ? sourceId : `source-${sourceId}`;
  }

  function clearSourceHighlights() {
    document.querySelectorAll('.is-living-source-highlight').forEach((node) => node.classList.remove('is-living-source-highlight'));
  }

  function updateCurrentBeat(context) {
    const widget = document.querySelector('[data-living-current-beat]');
    if (!widget) return;
    const active = currentBeat(context);
    const progress = buildProgressSnapshot(context, active);
    const title = active?.title || 'Reading';
    const percent = Math.round(progress?.progress || 0);
    widget.querySelector('strong').textContent = title;
    widget.querySelector('em').textContent = `${percent}%`;
    widget.querySelector('[data-living-top]')?.setAttribute('aria-label', `Back to top. ${percent}% read. Current section: ${title}.`);
  }

  function currentBeat(context) {
    const offset = 140;
    let active = context.beats[0] || null;
    context.beats.forEach((beat) => {
      const node = beat.node || document.getElementById(beat.id);
      if (node && node.getBoundingClientRect().top <= offset) active = beat;
    });
    return active;
  }

  function buildProgressSnapshot(context, beat = currentBeat(context)) {
    const rect = context.article.getBoundingClientRect();
    const scrollY = window.scrollY || window.pageYOffset || 0;
    const articleTop = scrollY + rect.top;
    const articleHeight = Math.max(1, context.article.scrollHeight - window.innerHeight * 0.65);
    const progress = Math.max(0, Math.min(100, ((scrollY - articleTop) / articleHeight) * 100));
    return {
      key: context.key,
      title: context.story.title,
      section: context.story.section,
      url: normalizeArticleUrl(context.story.url || window.location.pathname),
      image: context.story.image,
      progress,
      anchor: beat?.id || '',
      updatedAt: Date.now(),
    };
  }

  function cycleReaderMode() {
    const modes = ['standard', 'focus', 'wide'];
    const current = document.documentElement.getAttribute('data-living-reader') || 'standard';
    const next = modes[(modes.indexOf(current) + 1) % modes.length] || 'standard';
    setReaderMode(next);
    updateReaderButton();
  }

  function applyStoredReaderMode() {
    try {
      setReaderMode(localStorage.getItem(STORAGE.readerMode) || 'standard');
    } catch (_) {
      setReaderMode('standard');
    }
  }

  function setReaderMode(mode) {
    document.documentElement.setAttribute('data-living-reader', mode);
    try {
      localStorage.setItem(STORAGE.readerMode, mode);
    } catch (_) {}
  }

  function updateReaderButton() {
    const button = document.querySelector('[data-living-action="reader-mode"]');
    if (!button) return;
    const mode = document.documentElement.getAttribute('data-living-reader') || 'standard';
    button.textContent = mode === 'focus' ? 'Wide' : mode === 'wide' ? 'Standard' : 'Focus';
  }

  function applyStoredSourceTrailMode() {
    try {
      setSourceTrailMode(localStorage.getItem(STORAGE.sourceTrail) === 'on');
    } catch (_) {
      setSourceTrailMode(false);
    }
  }

  function toggleSourceTrailMode() {
    setSourceTrailMode(document.documentElement.getAttribute('data-living-source-trail') !== 'on');
  }

  function setSourceTrailMode(enabled) {
    if (enabled) {
      document.documentElement.setAttribute('data-living-source-trail', 'on');
    } else {
      document.documentElement.removeAttribute('data-living-source-trail');
    }

    try {
      localStorage.setItem(STORAGE.sourceTrail, enabled ? 'on' : 'off');
    } catch (_) {}

    updateSourceTrailButton();
  }

  function updateSourceTrailButton() {
    const enabled = document.documentElement.getAttribute('data-living-source-trail') === 'on';
    document.querySelectorAll('[data-living-action="source-trail"]').forEach((button) => {
      button.textContent = enabled ? 'Trail On' : 'Source Trail';
      button.setAttribute('aria-pressed', enabled ? 'true' : 'false');
    });
  }

  function readFollowedTopics() {
    try {
      const topics = JSON.parse(localStorage.getItem(STORAGE.followedTopics) || '[]');
      return Array.isArray(topics) ? topics : [];
    } catch (_) {
      return [];
    }
  }

  function isFollowingTopic(section) {
    return readFollowedTopics().includes(section || 'News');
  }

  function toggleFollowTopic(section) {
    const label = section || 'News';
    const current = readFollowedTopics();
    const next = current.includes(label) ? current.filter((item) => item !== label) : current.concat(label);
    try {
      localStorage.setItem(STORAGE.followedTopics, JSON.stringify(next));
    } catch (_) {}
  }

  function getCurrentStoryData(article, hero, body) {
    const embedded = readEmbeddedStories();
    const currentKey = normalizeUrlKey(window.location.pathname);
    const match = embedded.find((story) => normalizeUrlKey(story.url) === currentKey || normalizeUrlKey(story.url).endsWith(currentKey));
    const jsonLd = readArticleJsonLd();
    const headline = cleanText(hero?.querySelector('.article-headline, h1')?.textContent || article.querySelector('h1')?.textContent || jsonLd.headline || document.title.replace(/\s+—\s+The Press$/i, ''));
    const dek = cleanText(hero?.querySelector('.article-dek')?.textContent || document.querySelector('meta[name="description"]')?.content || jsonLd.description || match?.dek || '');
    const section = cleanText(match?.section || jsonLd.articleSection || hero?.querySelector('.eyebrow')?.textContent?.split('•')[0] || 'News');
    const image = cleanText(match?.image || hero?.querySelector('img')?.getAttribute('src') || jsonLd.image?.url || '');

    return {
      title: cleanText(match?.title || headline),
      dek: cleanText(match?.dek || dek),
      section,
      type: cleanText(match?.type || hero?.querySelector('.eyebrow')?.textContent?.split('•')[1] || 'Story'),
      url: cleanText(match?.url || window.location.pathname.split('/').pop() || ''),
      image,
      imageAlt: cleanText(match?.imageAlt || match?.image_alt || hero?.querySelector('img')?.alt || headline),
      published: cleanText(match?.published || match?.publishedLabel || jsonLd.datePublished || ''),
      keywords: Array.isArray(match?.keywords) ? match.keywords : [],
      readTime: cleanText(match?.readTime || match?.read_time || ''),
      bodyText: cleanText(body.textContent || ''),
      matchedCurrentStory: Boolean(match),
    };
  }

  function readArticleJsonLd() {
    const scripts = Array.from(document.querySelectorAll('script[type="application/ld+json"]'));
    for (const script of scripts) {
      try {
        const data = JSON.parse(script.textContent || '{}');
        const article = Array.isArray(data) ? data.find((item) => /Article$/i.test(item['@type'] || '')) : data;
        if (article && /Article$/i.test(article['@type'] || '')) return article;
      } catch (_) {}
    }
    return {};
  }

  function readEmbeddedStories() {
    const node = document.getElementById('press-search-data');
    if (!node) return [];
    try {
      const data = JSON.parse(node.textContent || '[]');
      return Array.isArray(data) ? data.map(normalizeStory).filter(Boolean) : [];
    } catch (_) {
      return [];
    }
  }

  function normalizeStory(item) {
    if (!item || typeof item !== 'object') return null;
    const title = cleanText(item.title || item.headline);
    const url = cleanText(item.url || item.href || item.link);
    if (!title || !url) return null;
    return {
      title,
      url: normalizeArticleUrl(url),
      section: cleanText(item.section || item.section_slug || 'News'),
      type: cleanText(item.type || 'Story'),
      dek: cleanText(item.dek || item.description || item.summary || ''),
      image: cleanText(item.image || item.thumbnail || ''),
      imageAlt: cleanText(item.imageAlt || item.image_alt || title),
      published: cleanText(item.published || item.publishedLabel || item.date || ''),
      publishedIso: cleanText(item.publishedIso || item.published_iso || ''),
      keywords: Array.isArray(item.keywords) ? item.keywords.map(String) : [],
      readTime: cleanText(item.readTime || item.read_time || ''),
    };
  }

  function relatedStoriesForEntity(entity, stories, currentUrl) {
    const aliases = entity.aliases.map((alias) => alias.toLowerCase());
    return stories.filter((story) => {
      if (normalizeUrlKey(story.url) === normalizeUrlKey(currentUrl)) return false;
      const haystack = normalizeText(`${story.title} ${story.dek} ${(story.keywords || []).join(' ')}`);
      return aliases.some((alias) => haystack.includes(alias.toLowerCase()));
    }).slice(0, 4);
  }

  function summarizeSections(stories) {
    const counts = new Map();
    stories.forEach((story) => {
      const section = cleanText(story.section || 'News').split('/')[0].trim();
      counts.set(section, (counts.get(section) || 0) + 1);
    });
    return Array.from(counts.entries())
      .map(([section, count]) => ({ section, count }))
      .sort((a, b) => b.count - a.count || a.section.localeCompare(b.section));
  }

  function bestQuote(context) {
    const quote = context.body.querySelector('blockquote')?.textContent;
    if (quote) return cleanText(quote);
    const paragraph = Array.from(context.body.querySelectorAll('p'))
      .map((node) => cleanText(node.textContent))
      .find((text) => text.length > 90 && text.length < 260);
    return paragraph || context.story.dek || context.story.title;
  }

  function buildShareCaption(story) {
    const url = new URL(story.url || window.location.href, window.location.href).href;
    return `${story.title}\n\n${story.dek}\n\nRead it on The Press: ${url}`;
  }

  function collectReadableText(root, hero) {
    const clone = root.cloneNode(true);
    clone.querySelectorAll('script, style, nav, .share-row, [data-living-drawer], .related-block, #related-stories, .story-card--related, .article-sources, #source-notes, .source-notes, .source-list').forEach((node) => node.remove());
    const heroText = hero ? cleanText(hero.textContent || '') : '';
    return cleanText(`${heroText} ${clone.textContent || ''}`);
  }

  function scrollToAnchor(id) {
    if (!id) return;
    const target = document.getElementById(id.replace(/^#/, ''));
    if (!target) return;
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function googleMapsUrl(place) {
    return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${place.lat},${place.lng}`)}`;
  }

  function streetViewUrl(place) {
    return `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${encodeURIComponent(`${place.lat},${place.lng}`)}`;
  }

  function osmUrl(place) {
    return `https://www.openstreetmap.org/?mlat=${place.lat}&mlon=${place.lng}#map=17/${place.lat}/${place.lng}`;
  }

  function osmEmbedUrl(place) {
    const delta = 0.006;
    const bbox = [
      place.lng - delta,
      place.lat - delta,
      place.lng + delta,
      place.lat + delta,
    ].join('%2C');
    return `https://www.openstreetmap.org/export/embed.html?bbox=${bbox}&layer=mapnik&marker=${place.lat}%2C${place.lng}`;
  }

  function hostnameFromUrl(url) {
    try {
      return new URL(url, window.location.href).hostname.replace(/^www\./, '');
    } catch (_) {
      return '';
    }
  }

  function normalizeArticleUrl(url) {
    const value = cleanText(url);
    if (!value) return window.location.pathname.split('/').pop() || 'index.html';
    if (/^https?:\/\//i.test(value) || value.startsWith('/') || value.startsWith('../')) return value;
    return value.replace(/^\.\//, '');
  }

  function normalizeUrlKey(value) {
    let raw = String(value || '')
      .replace(/^https?:\/\/[^/]+/i, '')
      .replace(/^file:\/\/[^/]+/i, '')
      .replace(/^.*\/The-Press\//i, '')
      .replace(/[?#].*$/, '')
      .replace(/^\/+/, '')
      .replace(/^\.\.\//, '')
      .replace(/^\.\//, '');

    if (!raw || raw.endsWith('/')) raw += 'index.html';
    const parts = raw.split('/').filter(Boolean);
    if (parts.length >= 2 && parts[parts.length - 2] === 'daily') return parts.slice(-2).join('/');
    return parts[parts.length - 1] || raw;
  }

  function sectionHref(section) {
    const slug = slugify(section);
    return slug ? `section-${slug}.html` : 'archive.html';
  }

  function sectionAccent(section) {
    const accents = {
      politics: '#b7473f',
      culture: '#2f6f73',
      technology: '#4158b7',
      economics: '#8a6425',
      education: '#5f579f',
      health: '#a23f66',
      philosophy: '#6a4c8f',
      science: '#22766d',
      sports: '#2f5f9e',
      world: '#5c6fb7',
      opinion: '#9f513b',
    };
    return accents[slugify(section)] || '#b7473f';
  }

  function parseStoryTime(story) {
    const parsed = Date.parse(story.publishedIso || story.published || '');
    return Number.isNaN(parsed) ? 0 : parsed;
  }

  function phraseInText(haystack, phrase) {
    const normalizedPhrase = normalizeText(phrase);
    if (!normalizedPhrase) return false;
    const pattern = new RegExp(`(^|[^a-z0-9])${escapeRegExp(normalizedPhrase).replace(/\s+/g, '\\s+')}(?=$|[^a-z0-9])`, 'i');
    return pattern.test(haystack);
  }

  function normalizeText(value) {
    return cleanText(value).toLowerCase();
  }

  function cleanText(value) {
    return String(value || '').replace(/\s+/g, ' ').trim();
  }

  function shorten(value, max) {
    const text = cleanText(value);
    if (text.length <= max) return text;
    return text.slice(0, Math.max(0, max - 1)).trim().replace(/[,\s]+$/, '') + '...';
  }

  function slugify(value) {
    return cleanText(value).toLowerCase().replace(/&/g, 'and').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
  }

  function escapeHtml(value) {
    return String(value ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function escapeAttr(value) {
    return escapeHtml(value).replace(/`/g, '&#96;');
  }

  function escapeRegExp(value) {
    return String(value).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  function cssEscape(value) {
    if (window.CSS && typeof window.CSS.escape === 'function') return window.CSS.escape(value);
    return String(value).replace(/[^a-zA-Z0-9_-]/g, '\\$&');
  }

  function triggerDownload(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
  }
})();
/* PRESS_LIVING_ARTICLE_KIT_END */
