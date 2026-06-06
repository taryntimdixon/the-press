(() => {
  const moments = window.PRESS_ON_THIS_DAY_MOMENTS || {};
  const artwork = window.PRESS_ON_THIS_DAY_ARTWORK || {};
  const page = document.querySelector('[data-history-detail-page]');

  if (!page) return;

  const laneLabels = {
    chronicle: 'Chronicle',
    civic: 'Civic',
    conflict: 'Conflict',
    culture: 'Culture',
    tech: 'Technology',
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

  const key = selectedDateKey();
  const moment = resolveMoment(key);

  if (!moment) {
    page.classList.remove('history-detail-page--loading');
    page.removeAttribute('aria-busy');
    page.innerHTML = '<p class="history-detail-empty">The history archive is unavailable right now.</p>';
    return;
  }

  renderPage(moment, moment.date || key);
  loadDetailMoment(moment.date || key).then((detailMoment) => {
    if (detailMoment) renderPage(detailMoment, detailMoment.date || moment.date || key);
  });

  function renderPage(moment, resolvedKey) {
  const art = artwork[resolvedKey] || {};
  const imageSrc = art.src ? historyDisplayImageSrc(art.src) : '';
  const imageCaption = historyImageCaption(moment, resolvedKey, art);
  const imageAlt = imageCaption || cleanHistoryImageText(art.alt) || `${moment.displayDate || resolvedKey}: ${moment.title || 'Historical moment'}`;
  const image = art.src
    ? `<img src="${escapeAttribute(assetUrl(imageSrc))}" alt="${escapeAttribute(imageAlt)}" decoding="async" fetchpriority="high">`
    : '<div class="history-detail-image__missing">Image coming soon</div>';
  const summary = Array.isArray(moment.summary) ? moment.summary : [];
  const displayDek = historyDisplayDek(moment);
  const articleBlocks = Array.isArray(moment.article) ? moment.article : summary;
  const facts = Array.isArray(moment.facts) ? moment.facts : [];
  const related = Array.isArray(moment.related) ? moment.related : [];
  const sourceLabel = moment.sourceLabel || 'History source';
  const sourceHref = moment.source || '';
  const laneLabel = laneLabels[moment.visual] || moment.visual || 'History';
  const year = formatHistoryYear(moment.year);
  const sources = collectSources(moment, sourceLabel, sourceHref, related);

  document.title = `${moment.title || 'On This Day History'} — The Press`;
  const description = document.querySelector('meta[name="description"]');
  if (description) description.setAttribute('content', moment.text || moment.dek || 'Read the full On This Day History entry from The Press.');

  page.dataset.historyDateKey = resolvedKey;
  page.classList.remove('history-detail-page--loading');
  page.removeAttribute('aria-busy');
  page.innerHTML = `
    <nav class="history-detail-nav" aria-label="History navigation">
      <a href="index.html#on-this-day">Today</a>
      <a href="on-this-day-preview.html">All 365</a>
    </nav>
    <section class="history-detail-hero">
      <p class="eyebrow">On This Day History</p>
      <h1>${escapeHtml(moment.title || 'Historical moment')}</h1>
      <p class="history-detail-dek">${escapeHtml(displayDek)}</p>
      <div class="history-detail-meta">
        <span>${escapeHtml(moment.displayDate || resolvedKey)}</span>
        <span>${escapeHtml(year)}</span>
        <span>${escapeHtml(laneLabel)}</span>
      </div>
    </section>
    <figure class="history-detail-image">
      ${image}
      ${imageCaption ? `<figcaption>${escapeHtml(imageCaption)}</figcaption>` : ''}
    </figure>
    <div class="history-detail-shell">
      <aside class="history-detail-rail history-detail-rail--left" aria-label="Event quick facts">
        <section class="history-detail-rail-card">
          <h2>At A Glance</h2>
          <dl>
            <div>
              <dt>Date</dt>
              <dd>${escapeHtml(moment.displayDate || resolvedKey)}</dd>
            </div>
            <div>
              <dt>Year</dt>
              <dd>${escapeHtml(year)}</dd>
            </div>
            <div>
              <dt>Lane</dt>
              <dd>${escapeHtml(laneLabel)}</dd>
            </div>
            ${moment.topic ? `
              <div>
                <dt>Topic</dt>
                <dd>${escapeHtml(moment.topic)}</dd>
              </div>
            ` : ''}
          </dl>
        </section>
        <section class="history-detail-rail-card">
          <h2>Key Facts</h2>
          <dl>${facts.map((fact) => `
            <div>
              <dt>${escapeHtml(fact.label || '')}</dt>
              <dd>${escapeHtml(fact.value || '')}</dd>
            </div>
          `).join('')}</dl>
        </section>
      </aside>
      <article class="history-detail-body">
        <p class="history-detail-lead">${escapeHtml(moment.text || '')}</p>
        ${articleBlocks.map((block) => renderArticleBlock(block, sources, moment)).join('')}
        ${renderSourceList(sources)}
      </article>
      <aside class="history-detail-rail history-detail-rail--right" aria-label="Event sources">
        ${sources.length ? `<section class="history-detail-rail-card history-detail-source-rail">
          <h2>Event Sources</h2>
          ${renderSourceRail(sources)}
        </section>` : ''}
        <section class="history-detail-rail-card">
          <h2>Explore</h2>
          <a href="on-this-day-preview.html">Browse all 365 entries</a>
          <a href="index.html#on-this-day">Return to today’s moment</a>
        </section>
      </aside>
    </div>
  `;
  }

  function resolveMoment(key) {
    return moments[key] || moments[monthDayKey(new Date())] || Object.values(moments)[0] || null;
  }

  function loadDetailMoment(key) {
    if (!key || !/^\d{2}-\d{2}$/.test(key)) return Promise.resolve(null);
    const cached = window.PRESS_ON_THIS_DAY_DETAIL?.[key];
    if (cached) return Promise.resolve(cached);

    return new Promise((resolve) => {
      let settled = false;
      const finish = () => {
        if (settled) return;
        settled = true;
        resolve(window.PRESS_ON_THIS_DAY_DETAIL?.[key] || null);
      };
      const previousReady = window.PRESS_ON_THIS_DAY_DETAIL_READY;
      window.PRESS_ON_THIS_DAY_DETAIL_READY = (readyKey) => {
        if (typeof previousReady === 'function') previousReady(readyKey);
        if (readyKey === key) finish();
      };

      const existing = document.querySelector(`script[data-history-detail-payload="${key}"]`);
      if (existing) {
        existing.addEventListener('load', finish, { once: true });
        existing.addEventListener('error', finish, { once: true });
        window.setTimeout(finish, 0);
        return;
      }

      const script = document.createElement('script');
      script.src = assetUrl(`assets/on-this-day-data/${key}.js?v=1780755531`);
      script.async = true;
      script.dataset.historyDetailPayload = key;
      script.addEventListener('load', finish, { once: true });
      script.addEventListener('error', finish, { once: true });
      document.head.appendChild(script);
    });
  }

  function selectedDateKey() {
    const params = new URLSearchParams(window.location.search);
    const raw = params.get('date') || params.get('day') || '';
    const match = String(raw).match(/(?:\d{4}-)?(\d{2})-(\d{2})$/);
    if (match) return `${match[1]}-${match[2]}`;
    return monthDayKey(new Date());
  }

  function monthDayKey(date) {
    return `${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
  }

  function formatHistoryYear(yearValue) {
    const value = Number(yearValue);
    if (!Number.isFinite(value)) return '';
    return value < 0 ? `${Math.abs(value)} BCE` : String(value);
  }

  function historyImageCaption(moment, resolvedKey, art = {}) {
    const directCaption = cleanHistoryImageText(moment.imageCaption || art.caption || '');
    if (directCaption) return trimCaption(directCaption);

    const year = formatHistoryYear(moment.year);
    const title = cleanHistoryImageText(moment.title || moment.topic || 'Historical moment');
    const summary = firstHistorySentence(moment.text || moment.headline || moment.dek || art.alt || '');
    const opener = [year, title].filter(Boolean).join(': ');

    if (opener && summary && !sameText(summary, title)) return trimCaption(`${opener}. ${summary}`);
    return trimCaption(opener || summary || `${moment.displayDate || resolvedKey}: Historical moment`);
  }

  function firstHistorySentence(value) {
    const cleaned = cleanHistoryImageText(value).replace(/\s+The deeper story is\b.*$/i, '');
    return trimCaption(sentenceFromText(cleaned) || cleaned);
  }

  function historyDisplayDek(moment = {}) {
    const event = firstHistorySentence(moment.text || moment.headline || '');
    if (event) return event;
    return firstHistorySentence(stripHistoryDekBoilerplate(moment.dek || '') || moment.title || '');
  }

  function stripHistoryDekBoilerplate(value) {
    return collapseWhitespace(value)
      .replace(/\.\.\./g, '.')
      .replace(/\s+\bThe deeper story is\b.*$/i, '');
  }

  function ensureSentence(value) {
    const text = collapseWhitespace(value);
    if (!text) return '';
    return /[.!?]$/.test(text) ? text : `${text}.`;
  }

  function sentenceFromText(text) {
    for (let index = 0; index < text.length; index += 1) {
      if (!/[.!?]/.test(text[index])) continue;
      if (index < text.length - 1 && !/\s/.test(text[index + 1])) continue;
      if (isProtectedSentencePeriod(text, index)) continue;
      return text.slice(0, index + 1);
    }
    return '';
  }

  function isProtectedSentencePeriod(text, index) {
    const before = text.slice(0, index + 1);
    const token = before.match(/(?:^|\s)(\S+)$/)?.[1] || '';
    const next = text.slice(index + 1).trimStart();
    if (/^(?:[A-Z]\.)+$/.test(token)) return true;
    if (/^(?:Mr|Mrs|Ms|Dr|Prof|St|Sen|Rep|Gov|Gen|Col|Lt|Capt|Sgt|Jr|Sr|No|v|vs)\.$/i.test(token)) return true;
    if (next && /^[a-z]/.test(next)) return true;
    return false;
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

  function trimCaption(value) {
    const text = collapseWhitespace(value);
    if (text.length <= 260) return text;
    return `${text.slice(0, 257).replace(/\s+\S*$/, '')}...`;
  }

  function sameText(a, b) {
    return collapseWhitespace(a).toLowerCase() === collapseWhitespace(b).toLowerCase();
  }

  function assetUrl(path) {
    if (typeof pressSiteAssetUrl === 'function') return pressSiteAssetUrl(path);
    return path;
  }

  function historyDisplayImageSrc(path) {
    const value = String(path || '');
    return value.replace(/assets\/on-this-day-images\/([^?#]+?)\.(?:png|jpe?g)(?=$|[?#])/i, 'assets/on-this-day-display/$1.jpg');
  }

  function collectSources(moment, sourceLabel, sourceHref, related) {
    const collected = [];
    const seen = new Set();
    const minimumSourceCount = 40;
    addSource({
      kind: 'Main record',
      title: sourceLabel,
      href: sourceHref,
      description: moment.sourceDescription || moment.headline || '',
    });

    const extraSources = Array.isArray(moment.sources) ? moment.sources : [];
    extraSources.forEach((source) => {
      addSource({
        kind: source.kind || source.type || 'Source',
        title: source.title || source.label || source.name || '',
        href: source.href || source.url || source.source || '',
        description: source.description || source.note || source.publisher || '',
      });
    });

    related.forEach((item) => {
      addSource({
        kind: 'Related record',
        title: item.title || 'Related source',
        href: item.source || '',
        description: item.description || '',
      });
    });

    buildResearchLeads(moment).forEach(addSource);

    while (collected.length < minimumSourceCount) {
      const number = collected.length + 1;
      addSource({
        kind: 'Search Lead',
        title: `Web research lead ${number}: ${moment.title || moment.topic || 'history'}`,
        href: `https://www.google.com/search?q=${encodeURIComponent(`${moment.title || moment.topic || ''} ${formatHistoryYear(moment.year)} history source ${number}`.trim())}`,
        description: 'Broad web search lead for additional reporting, images, artifacts, books, and background.',
      });
    }

    return collected;

    function addSource(source) {
      const href = String(source.href || '').trim();
      const title = String(source.title || '').trim();
      if (!href && !title) return;
      const key = href || title.toLowerCase();
      if (seen.has(key)) return;
      seen.add(key);
      collected.push({
        kind: source.kind,
        title: title || href,
        href,
        description: String(source.description || '').trim(),
      });
    }
  }

  function buildResearchLeads(moment) {
    const title = moment.title || moment.topic || 'history';
    const topic = moment.topic || moment.title || 'history';
    const year = formatHistoryYear(moment.year);
    const query = encodeURIComponent(`${title} ${year}`.trim());
    const topicQuery = encodeURIComponent(topic);
    const visual = moment.visual || '';
    const common = [
      lead('Image Archive', `Wikimedia Commons search: ${title}`, `https://commons.wikimedia.org/w/index.php?search=${query}&title=Special:MediaSearch&type=image`, 'Images, maps, objects, diagrams, and visual traces connected to the event.'),
      lead('Book/Media Archive', `Internet Archive search: ${title}`, `https://archive.org/search?query=${query}`, 'Digitized books, broadcasts, magazines, public-domain media, and older documentary traces.'),
      lead('Library Archive', `Library of Congress search: ${title}`, `https://www.loc.gov/search/?q=${query}`, 'Photographs, manuscripts, maps, newspapers, recordings, and public-history collection leads.'),
      lead('Museum Archive', `Smithsonian search: ${title}`, `https://www.si.edu/search?edan_q=${query}`, 'Museum objects, images, oral histories, articles, and collection records.'),
      lead('Public Records', `National Archives catalog search: ${title}`, `https://catalog.archives.gov/search?q=${query}`, 'Government records, photographs, declassified files, and public-document leads.'),
      lead('Library Network', `WorldCat search: ${title}`, `https://search.worldcat.org/search?q=${query}`, 'Books, archival catalogs, local histories, and library holdings around the event.'),
      lead('Digitized Books', `HathiTrust search: ${title}`, `https://catalog.hathitrust.org/Search/Home?lookfor=${query}&searchtype=all`, 'Digitized books and research-library catalog records.'),
      lead('Scholarly Search', `JSTOR search: ${title}`, `https://www.jstor.org/action/doBasicSearch?Query=${query}`, 'Academic articles, book chapters, reviews, and historical scholarship leads.'),
      lead('Public Library', `Digital Public Library search: ${title}`, `https://dp.la/search?q=${query}`, 'U.S. cultural-heritage objects, photographs, documents, and partner collection records.'),
      lead('European Archive', `Europeana search: ${title}`, `https://www.europeana.eu/en/search?query=${query}`, 'European museum, archive, newspaper, and image collection leads.'),
      lead('Reference Search', `Britannica search: ${topic}`, `https://www.britannica.com/search?query=${topicQuery}`, 'Reference context for people, places, institutions, and terms around the event.'),
      lead('News Archive', `The New York Times search: ${title}`, `https://www.nytimes.com/search?query=${query}`, 'News, reviews, anniversary coverage, obituaries, and public-memory reporting.'),
      lead('Broadcast Archive', `BBC search: ${title}`, `https://www.bbc.co.uk/search?q=${query}`, 'Broadcast, documentary, interview, and international news coverage leads.'),
      lead('Public Media', `PBS search: ${title}`, `https://www.pbs.org/search/?q=${query}`, 'Documentary, education, interview, and public-media history leads.'),
      lead('Audio/News Archive', `NPR search: ${title}`, `https://www.npr.org/search?query=${query}`, 'Audio stories, interviews, explainers, and public-radio context.'),
      lead('Magazine Archive', `Smithsonian Magazine search: ${title}`, `https://www.smithsonianmag.com/search/?q=${query}`, 'Readable history, science, culture, and artifact-led background.'),
      lead('Photo/Story Archive', `National Geographic search: ${title}`, `https://www.nationalgeographic.com/search?q=${query}`, 'Photography, geography, exploration, science, and culture-story leads.'),
      lead('Press Archive', `Associated Press search: ${title}`, `https://apnews.com/search?q=${query}`, 'Wire-service reporting and later news context.'),
      lead('Global News Archive', `Reuters search: ${title}`, `https://www.reuters.com/site-search/?query=${query}`, 'International news, anniversary coverage, and reporting leads.'),
      lead('Newspaper Archive', `Guardian search: ${title}`, `https://www.theguardian.com/search?q=${query}`, 'News features, criticism, long reads, and public-memory coverage.'),
      lead('Time Archive', `TIME search: ${title}`, `https://time.com/search/?q=${query}`, 'Magazine coverage, profiles, anniversary stories, and cultural-memory leads.'),
      lead('Teaching Archive', `DocsTeach search: ${title}`, `https://www.docsteach.org/search?query=${query}`, 'Classroom-ready primary documents and National Archives teaching materials.'),
      lead('Visual Culture', `Google Arts & Culture search: ${title}`, `https://artsandculture.google.com/search?q=${query}`, 'Museum stories, high-resolution objects, exhibits, and visual-history context.'),
      lead('Book Search', `Google Books search: ${title}`, `https://www.google.com/search?tbm=bks&q=${query}`, 'Book previews, monographs, biographies, and publishing-history leads.'),
      lead('Scholarly Web', `Google Scholar search: ${title}`, `https://scholar.google.com/scholar?q=${query}`, 'Academic articles, citations, and research leads.'),
    ];

    const laneSpecific = [];
    if (visual === 'space') {
      laneSpecific.push(
        lead('NASA Archive', `NASA search: ${title}`, `https://www.nasa.gov/search/?search=${query}`, 'Mission pages, astronaut history, technical background, and NASA features.'),
        lead('NASA Images', `NASA Images search: ${title}`, `https://images.nasa.gov/search-results?q=${query}`, 'NASA photographs, videos, audio, and mission media.'),
        lead('Mission Data', `NASA NSSDC search: ${title}`, `https://nssdc.gsfc.nasa.gov/nmc/`, 'NASA spacecraft catalog and mission-data starting point.'),
      );
    } else if (visual === 'tech') {
      laneSpecific.push(
        lead('Computer History', `Computer History Museum search: ${title}`, `https://www.computerhistory.org/search/?q=${query}`, 'Computing, chip, software, network, and technology-history collection leads.'),
        lead('Engineering Archive', `IEEE History Center search: ${title}`, `https://ethw.org/w/index.php?search=${query}&title=Special%3ASearch`, 'Engineering-history articles, milestone records, and technical background.'),
        lead('Technology News', `Wired search: ${title}`, `https://www.wired.com/search/?q=${query}`, 'Technology reporting, retrospectives, and culture-of-tech context.'),
      );
    } else if (visual === 'medicine') {
      laneSpecific.push(
        lead('Medical Literature', `PubMed search: ${title}`, `https://pubmed.ncbi.nlm.nih.gov/?term=${query}`, 'Medical research, clinical literature, and scientific papers.'),
        lead('Medical Library', `National Library of Medicine search: ${title}`, `https://www.nlm.nih.gov/search/?query=${query}`, 'Medical-history collections, exhibitions, and public-health context.'),
        lead('Public Health', `CDC search: ${title}`, `https://search.cdc.gov/search/?query=${query}`, 'Public-health reports, surveillance history, and health-agency context.'),
      );
    } else if (visual === 'rights' || visual === 'protest') {
      laneSpecific.push(
        lead('Rights Archive', `Library of Congress civil-rights search: ${title}`, `https://www.loc.gov/search/?fa=subject:civil+rights&q=${query}`, 'Civil-rights photographs, manuscripts, law, and movement-history leads.'),
        lead('Human Rights', `Amnesty search: ${title}`, `https://www.amnesty.org/en/search/${query}/`, 'Human-rights reporting, remembrance, and advocacy context.'),
        lead('Law/History', `Oyez search: ${title}`, `https://www.oyez.org/search/${query}`, 'Supreme Court case materials where the event connects to constitutional law.'),
      );
    } else if (visual === 'civic' || visual === 'crime') {
      laneSpecific.push(
        lead('Legal Archive', `Justia search: ${title}`, `https://law.justia.com/search?query=${query}`, 'Legal opinions, statutes, and case-law leads.'),
        lead('Public Records', `FBI Vault search: ${title}`, `https://vault.fbi.gov/search?SearchableText=${query}`, 'Federal investigative files and public-record leads where available.'),
        lead('Government History', `Our Documents search: ${title}`, `https://www.ourdocuments.gov/search.php?query=${query}`, 'Milestone documents and civic-history context.'),
      );
    } else if (visual === 'conflict') {
      laneSpecific.push(
        lead('War Museum', `Imperial War Museums search: ${title}`, `https://www.iwm.org.uk/search/global?query=${query}`, 'Military photographs, objects, oral histories, and war-history collection leads.'),
        lead('Military History', `National WWII Museum search: ${title}`, `https://www.nationalww2museum.org/search?keys=${query}`, 'World War II scholarship, artifacts, education, and campaign context where relevant.'),
        lead('Diplomatic Archive', `Wilson Center search: ${title}`, `https://www.wilsoncenter.org/search?search=${query}`, 'Cold War, diplomatic, and international-history document leads.'),
      );
    } else if (visual === 'culture' || visual === 'music') {
      laneSpecific.push(
        lead('Film/Media Record', `AFI Catalog search: ${title}`, `https://catalog.afi.com/Search?searchField=MovieName&searchText=${query}`, 'Film records, production details, release context, and credits where relevant.'),
        lead('Broadcast/Media', `Paley Center search: ${title}`, `https://www.paleycenter.org/search?q=${query}`, 'Television, radio, and media-history collection leads.'),
        lead('Music Archive', `GRAMMY search: ${title}`, `https://www.grammy.com/search?keys=${query}`, 'Recording history, artists, awards, and music-industry context where relevant.'),
      );
    } else if (visual === 'transport') {
      laneSpecific.push(
        lead('Air & Space', `National Air and Space Museum search: ${title}`, `https://airandspace.si.edu/search?search=${query}`, 'Aircraft, spacecraft, route, aviation, and exploration collection leads.'),
        lead('Infrastructure History', `National Park Service search: ${title}`, `https://www.nps.gov/search/?query=${query}`, 'Historic places, infrastructure, routes, parks, and preservation context.'),
        lead('Engineering Archive', `ASCE search: ${title}`, `https://www.asce.org/search#q=${query}`, 'Civil-engineering and infrastructure-history leads.'),
      );
    } else if (visual === 'science') {
      laneSpecific.push(
        lead('Research Literature', `Nature search: ${title}`, `https://www.nature.com/search?q=${query}`, 'Scientific papers, news, explainers, and research-history context.'),
        lead('Science News', `Science search: ${title}`, `https://www.science.org/action/doSearch?AllField=${query}`, 'Scientific reporting, research papers, and discovery context.'),
        lead('Earth/Science Agency', `USGS search: ${title}`, `https://www.usgs.gov/search?keywords=${query}`, 'Geology, earth-science, hazard, and fieldwork background where relevant.'),
      );
    } else if (visual === 'sports') {
      laneSpecific.push(
        lead('Sports Archive', `Olympics search: ${title}`, `https://olympics.com/en/search?q=${query}`, 'Athlete, tournament, competition, and sports-history leads.'),
        lead('Football Archive', `FIFA search: ${title}`, `https://www.fifa.com/search?q=${query}`, 'World Cup, football, tournament, and match-history leads where relevant.'),
        lead('Sports News', `ESPN search: ${title}`, `https://www.espn.com/search/_/q/${query}`, 'Sports reporting, profiles, and archive leads.'),
      );
    }

    return [...laneSpecific, ...common];

    function lead(kind, title, href, description) {
      return { kind, title, href, description };
    }
  }

  function renderSourceRail(sources) {
    if (!sources.length) return '';

    return `
      <ul class="history-detail-source-list">
        ${sources.map((source, index) => `
          <li>
            ${source.href ? `
              <a class="history-detail-source-link" href="${escapeAttribute(source.href)}">
                <span>${String(index + 1).padStart(2, '0')} / ${escapeHtml(source.kind)}</span>
                <strong>${escapeHtml(source.title)}</strong>
                ${source.description ? `<p>${escapeHtml(source.description)}</p>` : ''}
              </a>
            ` : `
              <div class="history-detail-source-link">
                <span>${String(index + 1).padStart(2, '0')} / ${escapeHtml(source.kind)}</span>
                <strong>${escapeHtml(source.title)}</strong>
                ${source.description ? `<p>${escapeHtml(source.description)}</p>` : ''}
              </div>
            `}
          </li>
        `).join('')}
      </ul>
    `;
  }

  function renderSourceList(sources) {
    if (!sources.length) return '';

    return `
      <section class="history-detail-sources article-sources" aria-label="Sources and further reading">
        <h2>Sources &amp; Further Reading</h2>
        <ol class="source-list">
          ${sources.map((source, index) => `
            <li id="history-source-${index + 1}">
              ${source.href ? `<a href="${escapeAttribute(source.href)}">${escapeHtml(source.title)}</a>` : `<span>${escapeHtml(source.title)}</span>`}
              ${source.description ? `<span class="source-label">${escapeHtml(source.description)}</span>` : ''}
            </li>
          `).join('')}
        </ol>
      </section>
    `;
  }

  function renderArticleBlock(block, sources, moment) {
    if (typeof block === 'string') return `<p>${escapeHtml(cleanHistoryArticleText(block, moment))}</p>`;
    if (!block || typeof block !== 'object') return '';

    const type = String(block.type || '').toLowerCase();
    const text = cleanHistoryArticleText(block.text || block.copy || block.body || '', moment);
    const refs = renderSourceRefs(block.sources || block.sourceRefs || block.refs, sources);

    if (type === 'heading') return `<h2>${escapeHtml(block.text || block.title || '')}</h2>`;
    if (type === 'quote') return `<blockquote>${escapeHtml(text)}${refs}</blockquote>`;
    if (!text) return '';
    return `<p>${escapeHtml(text)}${refs}</p>`;
  }

  function cleanHistoryArticleText(value, moment = {}) {
    const text = collapseWhitespace(value);
    if (!text) return '';
    if (/^The strongest image for this entry\b/i.test(text)) {
      const title = moment.title || moment.topic || 'This moment';
      const setting = moment.scene || 'a real setting where people, institutions, tools, and public pressure met';
      return `${title} was not an abstract headline. It unfolded in ${setting}. That setting matters because historical change does not happen in slogans alone; it happens through rooms, streets, laboratories, courts, stadiums, launch pads, offices, shops, ships, fields, and homes. Those details help the event feel less like trivia and more like a situation people had to navigate in real time.`;
    }
    return text
      .replace(/\bthis entry\b/gi, 'this history')
      .replace(/\bthe strongest image\b/gi, 'the clearest scene');
  }

  function renderSourceRefs(refs, sources) {
    const list = Array.isArray(refs) ? refs : refs ? [refs] : [];
    if (!list.length || !sources.length) return '';

    const links = list.map((ref) => {
      const index = resolveSourceIndex(ref, sources);
      const source = sources[index];
      if (!source) return '';
      const number = index + 1;
      return `<sup class="source-ref"><a href="#history-source-${number}" aria-label="Source ${number}: ${escapeAttribute(source.title)}">${number}</a></sup>`;
    }).filter(Boolean);

    return links.join('');
  }

  function resolveSourceIndex(ref, sources) {
    if (Number.isInteger(ref) && ref >= 1) return ref - 1;
    if (Number.isInteger(ref) && ref === 0) return 0;

    const needle = String(ref || '').trim().toLowerCase();
    if (!needle) return -1;
    return sources.findIndex((source) => (
      source.href.toLowerCase() === needle ||
      source.title.toLowerCase() === needle ||
      source.kind.toLowerCase() === needle
    ));
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

  function collapseWhitespace(value) {
    return String(value || '').replace(/\s+/g, ' ').trim();
  }
})();
