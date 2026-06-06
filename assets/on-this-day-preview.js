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
  const extraNotes = {
    '06-06': "More than 150,000 Allied troops crossed the English Channel that day, with airborne landings, naval bombardment, and beach assaults spread across five Normandy landing areas.",
    '01-16': "Carol Channing led the original Broadway cast, and Jerry Herman wrote the music and lyrics for the production.",
    '02-08': "Johnson fell one electoral vote short after Virginia's electors refused to support him, sending the decision to the Senate.",
    '02-14': "Its first video, \"Me at the zoo,\" was uploaded in April 2005, and Google bought the company the next year.",
    '02-19': "Officials later said prison staff had opened doors and helped cartel-linked inmates escape.",
    '02-22': "The game came during the medal round; the United States still had to beat Finland to win gold.",
    '03-02': "Chamberlain also made 28 free throws that night while playing every minute of the game.",
    '03-14': "W. S. Gilbert wrote the libretto, and Arthur Sullivan composed the music for the Savoy Theatre production.",
    '04-02': "The film was developed with Arthur C. Clarke, who also wrote the companion novel released after the premiere.",
    '04-13': "The Island Records release introduced the Wailers to a wider international rock audience.",
    '04-28': "Released in 1973, the record used studio effects, spoken-word fragments, and continuous transitions between tracks.",
    '05-03': "The images helped push the Kennedy administration toward federal civil rights legislation later that year.",
    '05-13': "Salvador Sobral's sister wrote the song, which won with a then-record Eurovision points total.",
    '05-21': "The flight lasted more than 33 hours and ended at Le Bourget, where a huge crowd met Lindbergh.",
    '05-26': "Between May 26 and June 4, Operation Dynamo evacuated more than 338,000 Allied troops from Dunkirk's beaches and harbor.",
    '06-04': "Troops and tanks moved into central Beijing after weeks of student-led demonstrations in Tiananmen Square.",
    '06-11': "Governor George Wallace stood at the schoolhouse door before federalized National Guard troops enforced enrollment.",
    '06-14': "The French government had already left Paris, and the city was declared open to avoid street fighting.",
    '06-16': "Valentina Tereshkova orbited Earth 48 times aboard Vostok 6 over nearly three days.",
    '06-17': "The arrests eventually led to Senate hearings, taped Oval Office evidence, and Richard Nixon's resignation.",
    '06-18': "The battle ended Napoleon's Hundred Days and sent him into final exile on Saint Helena.",
    '06-26': "Bloomsbury printed only about 500 hardback copies in the first United Kingdom run.",
    '07-02': "The law barred discrimination in public accommodations and employment and strengthened federal enforcement of school desegregation.",
    '07-05': "Scientists announced Dolly publicly in February 1997 after keeping the birth quiet for months while confirming the result.",
    '07-08': "Atlantis flew the STS-135 mission, carrying supplies to the International Space Station.",
    '07-12': "France beat Brazil 3-0 at Stade de France, with Zinedine Zidane scoring twice from headers.",
    '07-15': "Nintendo launched the console in Japan with Donkey Kong, Donkey Kong Jr., and Popeye as early cartridges.",
    '07-19': "Cassini photographed Saturn and Earth during an imaging campaign while the spacecraft was in Saturn's shadow.",
    '07-22': "Wiley Post circled the globe alone in the Lockheed Vega Winnie Mae in 7 days, 18 hours, and 49 minutes.",
    '07-29': "Allen & Unwin issued the book in Britain in 1954, followed by The Two Towers and The Return of the King.",
    '08-08': "The cover shoot took only minutes outside EMI Studios, later renamed Abbey Road Studios.",
    '08-10': "His death occurred while he was awaiting trial on federal sex-trafficking charges in New York.",
    '08-12': "Investigators traced the crash to a faulty repair of the aircraft's rear pressure bulkhead years earlier.",
    '08-18': "Tennessee's ratification supplied the final state approval needed for the amendment to become part of the Constitution.",
    '08-27': "Twin brothers Norris and Ross McWhirter compiled the early volumes after being commissioned by Guinness.",
    '09-15': "De Gouges addressed the text to Queen Marie Antoinette and modeled it against the 1789 rights declaration.",
    '10-02': "Before joining the Court, Marshall argued Brown v. Board of Education as NAACP chief counsel.",
    '10-10': "The group's motto was \"Deeds, not words,\" and its tactics brought arrests, hunger strikes, and force-feeding.",
    '10-16': "The book introduced Narnia, Aslan, and the Pevensie children before six more novels expanded the series.",
    '10-17': "The first tournament was a 36-hole event played over three rounds on Prestwick's 12-hole course.",
    '11-06': "The treaty created the Great Sioux Reservation and recognized Native rights to the Black Hills, promises later broken by the United States.",
    '11-09': "Jann Wenner and critic Ralph J. Gleason launched the magazine in San Francisco.",
    '11-16': "Riel's execution deepened divisions between French and English Canada and made him a lasting Metis symbol.",
    '11-25': "The release followed the concert film This Is Us and preceded the Where We Are stadium tour.",
    '12-06': "Georgia's ratification supplied the final state approval, and William H. Seward certified the amendment on December 18, 1865.",
    '12-29': "The killings took place near Wounded Knee Creek on the Pine Ridge Reservation in South Dakota.",
  };

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

  function displayDek(moment = {}) {
    const event = firstCompleteSentence(moment.text || moment.headline || '');
    if (event) return event;
    return firstCompleteSentence(stripHistoryDekBoilerplate(moment.dek || '') || moment.title || '');
  }

  function previewInsights(moment = {}, dek = '') {
    const blockedKeys = new Set([
      comparableText(dek),
      comparableText(moment.text || ''),
      comparableText(moment.headline || ''),
      comparableText(stripHistoryDekBoilerplate(moment.dek || '')),
    ].filter(Boolean));
    const referenceTexts = [
      dek,
      moment.text || '',
    ].filter(Boolean);
    const insights = [];

    addInsight(headlineExtraSentence(moment, dek));
    addInsight(extraNotes[moment.date], true);
    addInsight(sourceDescriptionSentence(moment));
    addInsight(connectedSubjectsSentence(moment));

    (Array.isArray(moment.coolFacts) ? moment.coolFacts : []).forEach((fact) => {
      addInsight(cleanPreviewInsight(fact, moment));
    });
    if (!insights.length) addInsight(stakesSentence(moment));

    return insights.slice(0, 3);

    function addInsight(value, allowNearRepeat = false) {
      const text = ensureSentence(cleanPreviewInsight(value, moment));
      const key = comparableText(text);
      if (!text || !key || blockedKeys.has(key)) return;
      if (!allowNearRepeat && referenceTexts.some((reference) => isRepeatingText(text, reference))) return;
      if (!allowNearRepeat && insights.some((item) => isRepeatingText(text, item))) return;
      insights.push(text);
    }
  }

  function cleanPreviewInsight(value, moment = {}) {
    let text = stripHistoryDekBoilerplate(value);
    if (!text) return '';
    if (/^\w+\s+\d+\s+places the reader\b/i.test(text)) return '';
    if (/^\w+\s+\d{1,2},\s+\d{3,4}:/i.test(text)) return '';
    if (/^A useful starting source is\b/i.test(text)) return '';
    if (/^A calendar entry matters\b/i.test(text)) return '';
    if (/^The lasting meaning sits\b/i.test(text)) return '';
    if (/^(?:The lasting consequence|The practical result|The consequence was)\b/i.test(text)) return '';
    if (/^(?:Why it mattered|The big historical pressure point):/i.test(text)) return '';
    if (/^(?:Context|Source context|Connected subjects|Connected to|Stakes|Main subject):/i.test(text)) return '';
    if (/^Scene:/i.test(text)) return '';
    return ensureSentence(sentenceCase(text));
  }

  function sourceDescriptionSentence(moment = {}) {
    const description = cleanText(moment.sourceDescription || '');
    if (!description) return '';
    const subject = cleanText(moment.topic || moment.title || 'The event');
    if (!subject || comparableText(subject) === comparableText(description)) return '';
    return `${displaySubject(subject)} ${pastSubjectVerb(subject)} ${descriptionPhrase(description)}.`;
  }

  function headlineExtraSentence(moment = {}, dek = '') {
    const headline = stripHistoryDekBoilerplate(moment.headline || '');
    if (!headline || comparableText(headline) === comparableText(dek)) return '';
    const clauses = headline.split(/[,;]\s+/).map((clause) => cleanText(clause)).filter(Boolean);
    for (const clause of clauses.slice(1)) {
      const sentence = clauseToSentence(clause, moment);
      if (sentence && comparableText(sentence) !== comparableText(dek)) return sentence;
    }
    return '';
  }

  function clauseToSentence(value, moment = {}) {
    const clause = cleanText(value).replace(/[.!?]$/, '');
    if (!clause) return '';
    const replacements = {
      opening: 'opened',
      beginning: 'began',
      creating: 'created',
      making: 'made',
      becoming: 'became',
      presenting: 'presented',
      introducing: 'introduced',
      establishing: 'established',
      resulting: 'resulted',
      marking: 'marked',
      giving: 'gave',
      hoping: 'hoped',
      exposing: 'exposed',
      changing: 'changed',
    };
    const match = clause.match(/^([a-z]+ing)\b\s*(.*)$/i);
    if (match) {
      const verb = replacements[match[1].toLowerCase()] || match[1];
      return `${shortSubject(moment)} ${verb} ${match[2]}.`;
    }
    return ensureSentence(sentenceCase(clause));
  }

  function connectedSubjectsSentence(moment = {}) {
    const subjects = connectedSubjects(moment);
    if (!subjects.length) return '';
    return `The surrounding record also points to ${readableList(subjects)}.`;
  }

  function connectedSubjects(moment = {}) {
    const titleKey = comparableText(moment.title || '');
    const topicKey = comparableText(moment.topic || '');
    const descriptionKey = comparableText(moment.sourceDescription || '');
    const items = [];

    (Array.isArray(moment.facts) ? moment.facts : []).forEach((fact) => {
      if (!/^connected to$/i.test(fact.label || '')) return;
      String(fact.value || '').split(',').forEach((item) => add(item));
    });
    (Array.isArray(moment.related) ? moment.related : []).forEach((item) => add(item.title || item.name || ''));

    return items.slice(0, 4);

    function add(value) {
      const text = cleanText(value).replace(/[.!?]$/, '');
      const key = comparableText(text);
      if (!text || !key || key === titleKey || key === topicKey || key === descriptionKey) return;
      if (items.some((item) => comparableText(item) === key)) return;
      items.push(text);
    }
  }

  function stakesSentence(moment = {}) {
    const stakes = cleanText(moment.stakes || '');
    if (!stakes) return '';
    return /^it\b/i.test(stakes) ? ensureSentence(stakes) : `It was ${lowercaseFirst(stakes)}.`;
  }

  function displaySubject(subject) {
    const text = cleanText(subject);
    if (!text || /^(?:a|an|the)\b/i.test(text) || /:/.test(text)) return text;
    if (/\b(?:act|battle|declaration|landings|massacre|revolution|treaty|war)\b/i.test(text)) return `The ${text}`;
    return text;
  }

  function shortSubject(moment = {}) {
    return displaySubject(moment.title || moment.topic || 'The event');
  }

  function subjectVerb(subject) {
    return /\b(?:landings|games|olympics|wars|rights|protests|treaties|forces|people)\b$/i.test(subject) ? 'are' : 'is';
  }

  function pastSubjectVerb(subject) {
    return /\b(?:landings|games|olympics|wars|rights|protests|treaties|forces|people)\b$/i.test(subject) ? 'were' : 'was';
  }

  function descriptionPhrase(value) {
    const text = cleanText(value);
    if (!text) return '';
    if (/^(?:a|an|the)\b/i.test(text)) return text;
    if (/^allied invasion\b/i.test(text)) return `the ${text}`;
    if (/^\d/.test(text)) return `the ${text}`;
    return `${/^[aeiou]/i.test(text) ? 'an' : 'a'} ${text}`;
  }

  function readableList(items) {
    const list = items.map((item) => cleanText(item)).filter(Boolean);
    if (list.length <= 1) return list[0] || '';
    if (list.length === 2) return `${list[0]} and ${list[1]}`;
    return `${list.slice(0, -1).join(', ')}, and ${list[list.length - 1]}`;
  }

  function sentenceCase(value) {
    const text = cleanText(value);
    if (!text || !/^[a-z]/.test(text)) return text;
    return `${text.charAt(0).toUpperCase()}${text.slice(1)}`;
  }

  function lowercaseFirst(value) {
    const text = cleanText(value);
    if (!text || !/^[A-Z]/.test(text)) return text;
    return `${text.charAt(0).toLowerCase()}${text.slice(1)}`;
  }

  function comparableText(value) {
    return cleanText(value)
      .toLowerCase()
      .replace(/&amp;/g, '&')
      .replace(/[^a-z0-9]+/g, ' ')
      .trim();
  }

  function isRepeatingText(value, reference) {
    const valueKey = comparableText(value);
    const referenceKey = comparableText(reference);
    if (!valueKey || !referenceKey) return false;
    if (valueKey === referenceKey) return true;
    if (valueKey.length > 24 && referenceKey.includes(valueKey)) return true;
    if (referenceKey.length > 24 && valueKey.includes(referenceKey)) return true;
    return textOverlap(value, reference) >= 0.62;
  }

  function textOverlap(value, reference) {
    const valueTokens = meaningfulTokens(value);
    const referenceTokens = meaningfulTokens(reference);
    if (valueTokens.length < 4 || referenceTokens.length < 4) return 0;
    const referenceSet = new Set(referenceTokens);
    const shared = valueTokens.filter((token) => referenceSet.has(token)).length;
    return shared / Math.min(valueTokens.length, referenceTokens.length);
  }

  function meaningfulTokens(value) {
    const stopWords = new Set([
      'about', 'above', 'after', 'again', 'against', 'also', 'because', 'before', 'began', 'being',
      'could', 'during', 'each', 'event', 'first', 'from', 'have', 'history', 'into', 'itself',
      'made', 'more', 'most', 'other', 'over', 'same', 'some', 'story', 'than', 'that', 'their',
      'them', 'then', 'there', 'these', 'they', 'this', 'through', 'under', 'very', 'were', 'what',
      'when', 'where', 'which', 'while', 'with', 'world', 'would',
    ]);
    return comparableText(value)
      .split(/\s+/)
      .filter((token) => token.length > 2 && !stopWords.has(token));
  }

  function stripHistoryDekBoilerplate(value) {
    return cleanText(value)
      .replace(/\.\.\./g, '.')
      .replace(/\s+\bThe deeper story is\b.*$/i, '');
  }

  function firstCompleteSentence(value) {
    const text = cleanText(value).replace(/\.\.\./g, '.');
    const sentence = sentenceFromText(text);
    return ensureSentence(sentence || text);
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

  function ensureSentence(value) {
    const text = cleanText(value);
    if (!text) return '';
    return /[.!?]$/.test(text) ? text : `${text}.`;
  }

  function cleanText(value) {
    return String(value || '').replace(/\s+/g, ' ').trim();
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
    const dek = displayDek(moment);
    const insights = previewInsights(moment, dek);
    const supportText = insights[0] || '';
    const factItems = insights.slice(1, 3).map((fact) => `<li>${escapeHtml(fact)}</li>`).join('');

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
          <p class="history-preview-card__dek">${escapeHtml(dek)}</p>
          ${supportText ? `<p class="history-preview-card__text">${escapeHtml(supportText)}</p>` : ''}
          ${factItems ? `<ul class="history-preview-card__facts">${factItems}</ul>` : ''}
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
