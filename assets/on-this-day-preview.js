(() => {
  const moments = window.PRESS_ON_THIS_DAY_MOMENTS || {};
  const artwork = window.PRESS_ON_THIS_DAY_ARTWORK || {};
  const grid = document.querySelector('[data-history-preview-grid]');
  const search = document.querySelector('[data-history-preview-search]');
  const lane = document.querySelector('[data-history-preview-lane]');
  const era = document.querySelector('[data-history-preview-era]');

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

  function cardMarkup(moment) {
    const art = artwork[moment.date];
    const hasImage = Boolean(art?.src);
    const facts = (moment.coolFacts || []).slice(0, 5);
    const factItems = facts.map((fact) => `<li>${escapeHtml(fact)}</li>`).join('');

    return `
      <article class="history-preview-card" data-preview-card data-search="${escapeHtml(textBlob(moment))}">
        <div class="history-preview-card__media">
          ${hasImage ? `
            <img src="${escapeHtml(assetUrl(historyDisplayImageSrc(art.src)))}" alt="${escapeHtml(art.alt || `${moment.displayDate}: ${moment.title}`)}" loading="lazy" decoding="async">
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
          <p>${escapeHtml(moment.text || '')}</p>
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
    const html = entries
      .filter((moment) => {
        if (laneValue !== 'all' && moment.visual !== laneValue) return false;
        if (eraValue !== 'all' && eraKey(moment.year) !== eraValue) return false;
        if (!query) return true;
        return textBlob(moment).includes(query);
      })
      .map(cardMarkup)
      .join('');

    grid.innerHTML = html || '<p class="history-preview-empty">No history entries matched that filter.</p>';
  }

  search?.addEventListener('input', render);
  lane?.addEventListener('change', render);
  era?.addEventListener('change', render);
  render();
})();
