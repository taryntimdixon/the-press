(() => {
  const moments = window.PRESS_ON_THIS_DAY_MOMENTS || {};
  const artwork = window.PRESS_ON_THIS_DAY_ARTWORK || {};
  const grid = document.querySelector('[data-history-preview-grid]');
  const search = document.querySelector('[data-history-preview-search]');
  const lane = document.querySelector('[data-history-preview-lane]');
  const era = document.querySelector('[data-history-preview-era]');
  const resultCount = document.querySelector('[data-history-preview-count]');
  const backButton = document.querySelector('[data-history-preview-back]');
  const topButton = document.querySelector('[data-history-preview-top]');
  const todayButton = document.querySelector('[data-history-preview-today]');
  const calendarDays = document.querySelector('[data-history-preview-calendar-days]');
  const calendarMonthLabel = document.querySelector('[data-history-preview-month-label]');
  const calendarPrev = document.querySelector('[data-history-preview-month-prev]');
  const calendarNext = document.querySelector('[data-history-preview-month-next]');

  if (!grid) return;

  const entries = Object.values(moments)
    .filter(Boolean)
    .sort((a, b) => String(a.date || '').localeCompare(String(b.date || '')));

  const laneLabels = {
    chronicle: 'Chronicle',
    civic: 'Civic',
    conflict: 'Conflict',
    culture: 'Culture',
    tech: 'Tech',
    music: 'Music',
    sports: 'Sports',
    crime: 'Crime',
    protest: 'Protest',
    medicine: 'Medicine',
    rights: 'Rights',
    science: 'Science',
    space: 'Space',
    transport: 'Transport',
  };
  const laneCounts = entries.reduce((counts, moment) => {
    const key = moment.visual || 'chronicle';
    counts[key] = (counts[key] || 0) + 1;
    return counts;
  }, {});
  const eraLabels = {
    ancient: 'Ancient',
    medieval: 'Medieval',
    earlyModern: 'Early modern',
    eighteenth: '1700s',
    nineteenth: '1800s',
    early1900: '1900-1929',
    late1900: '1930-1999',
    recent: '2000s',
  };
  const eraOrder = ['ancient', 'medieval', 'earlyModern', 'eighteenth', 'nineteenth', 'early1900', 'late1900', 'recent'];
  const monthLabels = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December',
  ];
  const monthDayCounts = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  const entriesByDate = entries.reduce((map, moment) => {
    if (moment?.date) map.set(moment.date, moment);
    return map;
  }, new Map());
  let visibleMonthIndex = Math.max(0, Math.min(11, Number(todayKey().slice(0, 2)) - 1 || 0));
  let activeDate = todayKey();
  const eraCounts = entries.reduce((counts, moment) => {
    const key = eraKey(moment.year);
    counts[key] = (counts[key] || 0) + 1;
    return counts;
  }, {});

  if (lane) {
    lane.insertAdjacentHTML('beforeend', Object.keys(laneCounts)
      .sort((a, b) => (laneLabels[a] || a).localeCompare(laneLabels[b] || b))
      .map((key) => `<option value="${escapeHtml(key)}">${escapeHtml(laneLabels[key] || key)} (${laneCounts[key]})</option>`)
      .join(''));
  }
  if (era) {
    era.insertAdjacentHTML('beforeend', eraOrder
      .filter((key) => eraCounts[key])
      .map((key) => `<option value="${escapeHtml(key)}">${escapeHtml(eraLabels[key])} (${eraCounts[key]})</option>`)
      .join(''));
  }
  function eraKey(year) {
    const value = Number(year);
    if (!Number.isFinite(value)) return 'recent';
    if (value < 500) return 'ancient';
    if (value < 1500) return 'medieval';
    if (value < 1700) return 'earlyModern';
    if (value < 1800) return 'eighteenth';
    if (value < 1900) return 'nineteenth';
    if (value < 1930) return 'early1900';
    if (value < 2000) return 'late1900';
    return 'recent';
  }

  function assetUrl(path) {
    if (typeof pressSiteAssetUrl === 'function') return pressSiteAssetUrl(path);
    return path;
  }

  function historyDisplayImageSrc(path) {
    const value = String(path || '');
    return value.replace(/assets\/on-this-day-images\/([^?#]+?)\.(?:png|jpe?g)(?=$|[?#])/i, 'assets/on-this-day-display/$1.jpg');
  }

  function escapeHtml(value) {
    return String(value ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function textBlob(moment) {
    return [
      moment.date,
      moment.displayDate,
      moment.year,
      moment.title,
      moment.dek,
      moment.text,
      moment.visual,
      ...(moment.coolFacts || []),
    ].join(' ').toLowerCase();
  }

  function dateId(date) {
    return `history-${String(date || '').replace(/[^a-z0-9]+/gi, '-')}`;
  }

  function todayKey() {
    const now = new Date();
    return `${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
  }

  function setActiveDate(date) {
    activeDate = String(date || '');
    if (activeDate) {
      const monthValue = Number(activeDate.slice(0, 2));
      if (Number.isFinite(monthValue) && monthValue >= 1 && monthValue <= 12) {
        visibleMonthIndex = monthValue - 1;
      }
    }
    renderCalendar();
  }

  function jumpToDate(date) {
    const key = String(date || '');
    if (!key) return;
    let target = document.getElementById(dateId(key));
    if (!target && (search?.value || lane?.value !== 'all' || era?.value !== 'all')) {
      if (search) search.value = '';
      if (lane) lane.value = 'all';
      if (era) era.value = 'all';
      render();
      target = document.getElementById(dateId(key));
    }
    if (!target) return;
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    target.classList.add('is-jump-target');
    window.setTimeout(() => target.classList.remove('is-jump-target'), 1200);
    target.focus({ preventScroll: true });
    setActiveDate(key);
  }

  function changeCalendarMonth(delta) {
    visibleMonthIndex = (visibleMonthIndex + delta + 12) % 12;
    renderCalendar();
  }

  function renderCalendar() {
    if (!calendarDays || !calendarMonthLabel) return;

    const monthNumber = String(visibleMonthIndex + 1).padStart(2, '0');
    const firstWeekday = new Date(2026, visibleMonthIndex, 1).getDay();
    const daysInMonth = monthDayCounts[visibleMonthIndex];
    const cells = [];

    calendarMonthLabel.textContent = monthLabels[visibleMonthIndex] || '';

    for (let index = 0; index < firstWeekday; index += 1) {
      cells.push('<span class="history-preview-calendar__blank" aria-hidden="true"></span>');
    }
    for (let day = 1; day <= daysInMonth; day += 1) {
      const key = `${monthNumber}-${String(day).padStart(2, '0')}`;
      const moment = entriesByDate.get(key);
      const isToday = key === todayKey();
      const isActive = key === activeDate;
      cells.push(`
        <button
          type="button"
          class="${isToday ? 'is-today' : ''} ${isActive ? 'is-active' : ''}"
          data-history-preview-calendar-day="${escapeHtml(key)}"
          ${moment ? `title="${escapeHtml(moment.title || moment.displayDate || key)}"` : 'disabled'}
          aria-label="${escapeHtml(moment ? `${moment.displayDate || key}: ${moment.title || 'Historical moment'}` : key)}"
        >${day}</button>
      `);
    }
    calendarDays.innerHTML = cells.join('');
  }

  function cardMarkup(moment) {
    const art = artwork[moment.date];
    const hasImage = Boolean(art?.src);
    const facts = (moment.coolFacts || []).slice(0, 2);
    const factItems = facts.map((fact) => `<li>${escapeHtml(fact)}</li>`).join('');

    return `
      <article class="history-preview-card" id="${escapeHtml(dateId(moment.date))}" data-preview-card data-date="${escapeHtml(moment.date || '')}" data-search="${escapeHtml(textBlob(moment))}" tabindex="-1">
        <div class="history-preview-card__media">
          ${hasImage ? `
            <img src="${escapeHtml(assetUrl(historyDisplayImageSrc(art.src)))}" alt="${escapeHtml(historyImageAltText(moment, art))}" loading="lazy" decoding="async">
          ` : `
            <div class="history-preview-card__queued">
              <span>Image coming soon</span>
            </div>
          `}
        </div>
        <div class="history-preview-card__body">
          <div class="history-preview-card__kicker">
            <span>${escapeHtml(moment.displayDate || moment.date)}</span>
            <span>${escapeHtml(String(moment.year || ''))}</span>
            <span>${escapeHtml(laneLabels[moment.visual] || moment.visual || 'History')}</span>
          </div>
          <h2>${escapeHtml(moment.title || 'Historical moment')}</h2>
          <p class="history-preview-card__dek">${escapeHtml(moment.dek || '')}</p>
          <p class="history-preview-card__text">${escapeHtml(moment.text || '')}</p>
          <ul class="history-preview-card__facts">${factItems}</ul>
          <a class="history-preview-card__more" href="on-this-day-event.html?date=${escapeHtml(moment.date || '')}">Read more about this</a>
        </div>
      </article>
    `;
  }

  function render() {
    const query = (search?.value || '').trim().toLowerCase();
    const laneValue = lane?.value || 'all';
    const eraValue = era?.value || 'all';
    const filtered = entries
      .filter((moment) => {
        if (laneValue !== 'all' && moment.visual !== laneValue) return false;
        if (eraValue !== 'all' && eraKey(moment.year) !== eraValue) return false;
        if (!query) return true;
        return textBlob(moment).includes(query);
      });
    const html = filtered
      .map(cardMarkup)
      .join('');

    grid.innerHTML = html || '<p class="history-preview-empty">No history entries matched that filter.</p>';
    if (resultCount) {
      const label = filtered.length === entries.length
        ? `Showing all ${entries.length} entries`
        : `Showing ${filtered.length} of ${entries.length} entries`;
      resultCount.textContent = label;
    }
  }

  search?.addEventListener('input', render);
  lane?.addEventListener('change', render);
  era?.addEventListener('change', render);
  backButton?.addEventListener('click', (event) => {
    if (window.history.length <= 1) return;
    event.preventDefault();
    window.history.back();
  });
  todayButton?.addEventListener('click', () => jumpToDate(todayKey()));
  calendarPrev?.addEventListener('click', () => changeCalendarMonth(-1));
  calendarNext?.addEventListener('click', () => changeCalendarMonth(1));
  calendarDays?.addEventListener('click', (event) => {
    const button = event.target.closest('[data-history-preview-calendar-day]');
    if (button) jumpToDate(button.getAttribute('data-history-preview-calendar-day'));
  });
  render();
  renderCalendar();

  if (topButton) {
    const updateTopButton = () => {
      const offset = window.scrollY || document.documentElement.scrollTop || document.body.scrollTop || 0;
      topButton.classList.toggle('is-visible', offset > 700);
    };

    topButton.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
      document.documentElement.scrollTo?.({ top: 0, behavior: 'smooth' });
      document.body.scrollTo?.({ top: 0, behavior: 'smooth' });
      search?.focus({ preventScroll: true });
    });
    window.addEventListener('scroll', updateTopButton, { passive: true });
    document.body.addEventListener('scroll', updateTopButton, { passive: true });
    updateTopButton();
  }

  function historyImageAltText(moment = {}, art = {}) {
    const cleanedArtAlt = cleanHistoryImageText(art.alt || art.caption || '');
    if (cleanedArtAlt) return cleanedArtAlt;

    const year = formatHistoryYear(moment.year);
    const title = cleanHistoryImageText(moment.title || moment.topic || 'Historical moment');
    const summary = firstHistoryImageSentence(moment.text || moment.headline || moment.dek || '');
    const opener = [year, title].filter(Boolean).join(': ');

    if (opener && summary && collapseWhitespace(summary).toLowerCase() !== collapseWhitespace(title).toLowerCase()) {
      return trimHistoryImageText(`${opener}. ${summary}`);
    }
    return trimHistoryImageText(opener || summary || `${moment.displayDate || moment.date || 'Today'}: Historical moment`);
  }

  function formatHistoryYear(yearValue) {
    const value = Number(yearValue);
    if (!Number.isFinite(value)) return '';
    return value < 0 ? `${Math.abs(value)} BCE` : String(value);
  }

  function firstHistoryImageSentence(value) {
    const cleaned = cleanHistoryImageText(value).replace(/\s+The deeper story is\b.*$/i, '');
    const sentence = cleaned.match(/^.{24,260}?[.!?](?:\s|$)/);
    return trimHistoryImageText(sentence ? sentence[0] : cleaned);
  }

  function cleanHistoryImageText(value) {
    let text = collapseWhitespace(value);
    if (!text) return '';

    text = text
      .replace(/^photorealistic\s+/i, '')
      .replace(/^(?:editorial|historical|science|cinematic|wide|dawn|night)\s+(?:scene|artwork|image)\s+(?:of\s+)?/i, '')
      .replace(/^scene\s+of\s+/i, '')
      .replace(/\s*,?\s+with\s+(?:period|historical|era-appropriate|marquee|press|crowd|crowds|cables|instruments|cars|uniforms|documents|machines|smoke|dust|lighting|props|visual|cinematic)\b.*$/i, '.')
      .replace(/\b(?:AI-generated|generated image|artwork prompt|image direction|production note)\b/gi, '')
      .replace(/\s+\./g, '.');

    return collapseWhitespace(text);
  }

  function trimHistoryImageText(value) {
    const text = collapseWhitespace(value);
    if (text.length <= 260) return text;
    return `${text.slice(0, 257).replace(/\s+\S*$/, '')}...`;
  }

  function collapseWhitespace(value) {
    return String(value || '').replace(/\s+/g, ' ').trim();
  }
})();
