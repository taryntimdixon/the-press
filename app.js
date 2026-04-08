
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-year]').forEach((node) => {
    node.textContent = new Date().getFullYear();
  });

  const body = document.body;
  const overlay = document.querySelector('[data-search-overlay]');
  const openButtons = document.querySelectorAll('[data-search-open]');
  const closeButtons = document.querySelectorAll('[data-search-close]');
  const searchInput = document.querySelector('[data-search-input]');
  const resultsBox = document.querySelector('[data-search-results]');
  let searchData = [];

  function openSearch() {
    if (!overlay) return;
    overlay.hidden = false;
    body.style.overflow = 'hidden';
    window.setTimeout(() => searchInput && searchInput.focus(), 30);
  }

  function closeSearch() {
    if (!overlay) return;
    overlay.hidden = true;
    body.style.overflow = '';
    if (searchInput) searchInput.value = '';
    renderSearchResults([]);
  }

  openButtons.forEach((btn) => btn.addEventListener('click', openSearch));
  closeButtons.forEach((btn) => btn.addEventListener('click', closeSearch));
  if (overlay) {
    overlay.addEventListener('click', (event) => {
      if (event.target === overlay) closeSearch();
    });
  }
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeSearch();
  });

  function renderSearchResults(results, query = '') {
    if (!resultsBox) return;
    if (!query) {
      resultsBox.innerHTML = '<div class="search-empty"><p>Start typing to search the full edition.</p></div>';
      return;
    }
    if (!results.length) {
      resultsBox.innerHTML = '<div class="search-empty"><p>No stories matched that search yet.</p></div>';
      return;
    }
    resultsBox.innerHTML = results.map((item) => `
      <article class="search-result">
        <p class="eyebrow eyebrow--tiny">${item.section} • ${item.type}</p>
        <h3><a href="${item.url}">${item.title}</a></h3>
        <p>${item.dek}</p>
        <p class="story-card__meta">By ${item.author} • ${item.published}</p>
      </article>
    `).join('');
  }

  function loadSearchData() {
    const embedded = document.getElementById('press-search-data');
    if (embedded) {
      try {
        searchData = JSON.parse(embedded.textContent);
        return Promise.resolve(searchData);
      } catch (err) {
        // continue to fetch fallback
      }
    }
    return fetch('search-index.json')
      .then((response) => response.ok ? response.json() : [])
      .then((data) => {
        searchData = Array.isArray(data) ? data : [];
        return searchData;
      })
      .catch(() => {
        searchData = [];
        return searchData;
      });
  }

  if (searchInput) {
    loadSearchData().then(() => {
      searchInput.addEventListener('input', () => {
        const query = searchInput.value.trim().toLowerCase();
        if (!query) {
          renderSearchResults([], '');
          return;
        }
        const results = searchData.filter((item) => {
          const haystack = [
            item.title,
            item.section,
            item.type,
            item.dek,
            item.author,
            ...(item.keywords || []),
          ].join(' ').toLowerCase();
          return haystack.includes(query);
        }).slice(0, 12);
        renderSearchResults(results, query);
      });
    });
  }

  const progressBar = document.querySelector('[data-reading-progress]');
  if (progressBar) {
    const updateProgress = () => {
      const article = document.querySelector('.article');
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

  const leadButtons = document.querySelectorAll('[data-lead-button]');
  const leadPanels = document.querySelectorAll('[data-lead-panel]');
  if (leadButtons.length && leadPanels.length) {
    const setLead = (targetId) => {
      leadButtons.forEach((btn) => {
        const active = btn.dataset.target === targetId;
        btn.classList.toggle('is-active', active);
        btn.setAttribute('aria-pressed', String(active));
      });
      leadPanels.forEach((panel) => panel.classList.toggle('is-active', panel.id === targetId));
    };
    leadButtons.forEach((btn) => {
      btn.addEventListener('click', () => setLead(btn.dataset.target));
    });
  }

  const filterButtons = document.querySelectorAll('[data-filter]');
  const archiveCards = document.querySelectorAll('.archive-card');
  if (filterButtons.length && archiveCards.length) {
    filterButtons.forEach((button) => {
      button.addEventListener('click', () => {
        const filterValue = button.dataset.filter;
        filterButtons.forEach((btn) => {
          const active = btn === button;
          btn.classList.toggle('is-active', active);
          btn.setAttribute('aria-pressed', String(active));
        });
        archiveCards.forEach((card) => {
          if (filterValue === 'All') {
            card.hidden = false;
            return;
          }
          const section = card.dataset.section;
          const type = card.dataset.type;
          card.hidden = !(section === filterValue || type === filterValue);
        });
      });
    });
  }

  document.querySelectorAll('[data-newsletter-form]').forEach((form) => {
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      const status = form.querySelector('[data-newsletter-status]');
      if (status) {
        status.textContent = 'Thanks — the signup form is wired as a prototype success state.';
      }
      form.reset();
    });
  });
});
