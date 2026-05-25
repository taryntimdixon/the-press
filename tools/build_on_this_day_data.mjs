import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, '..');
const outputPath = path.join(rootDir, 'assets', 'on-this-day-moments.js');
const cacheDir = path.join(rootDir, '.cache', 'on-this-day');
const endpointBase = 'https://en.wikipedia.org/api/rest_v1/feed/onthisday/selected';
const userAgent = 'The Press local build (https://thepress.live/)';

const MONTHS = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
];

const BIG_TERMS = [
  ['iphone', 42],
  ['macintosh', 38],
  ['apple computer', 38],
  ['ipad', 34],
  ['world wide web', 38],
  ['wikipedia', 36],
  ['youtube', 36],
  ['google', 34],
  ['facebook', 32],
  ['netflix', 30],
  ['internet', 30],
  ['video game', 28],
  ['album', 38],
  ['concert', 32],
  ['hip hop', 40],
  ['rap', 32],
  ['rock and roll', 32],
  ['mtv', 34],
  ['beatles', 34],
  ['michael jackson', 38],
  ['beyonce', 38],
  ['tupac', 34],
  ['madonna', 34],
  ['thriller', 38],
  ['apollo theater', 34],
  ['apollo theatre', 34],
  ['nasa', 34],
  ['apollo', 26],
  ['moon', 22],
  ['mars', 32],
  ['rover', 30],
  ['space shuttle', 34],
  ['voyager', 34],
  ['hubble', 34],
  ['pale blue dot', 38],
  ['curiosity', 34],
  ['drug', 32],
  ['cartel', 36],
  ['cocaine', 34],
  ['narcotics', 30],
  ['pablo escobar', 42],
  ['el chapo', 42],
  ['guzman', 40],
  ['mafia', 28],
  ['arrested', 22],
  ['captured', 18],
  ['convicted', 20],
  ['trial', 16],
  ['black panther', 34],
  ['mandela', 38],
  ['apartheid', 36],
  ['stonewall', 38],
  ['voting rights act', 38],
  ['civil rights', 34],
  ['women\'s march', 34],
  ['indigenous', 28],
  ['olympic', 28],
  ['world cup', 32],
  ['basketball', 24],
  ['football', 20],
  ['tennis', 24],
  ['boxing', 24],
  ['cricket world cup', 30],
  ['protest', 26],
  ['strike', 24],
  ['boycott', 24],
  ['uprising', 24],
  ['arab spring', 38],
  ['transatlantic', 22],
  ['independence', 20],
  ['abolished', 20],
  ['abolishing', 20],
  ['slavery', 20],
  ['declaration', 18],
  ['constitution', 18],
  ['united nations', 18],
  ['first solo', 18],
  ['first non-stop', 18],
  ['first nonstop', 18],
  ['first', 14],
  ['human rights', 14],
  ['holocaust', 14],
  ['massacre', 13],
  ['chemical weapons', 13],
  ['civilians', 11],
  ['suffrage', 13],
  ['spacecraft', 13],
  ['launched', 12],
  ['landed', 12],
  ['founded', 11],
  ['established', 11],
  ['ratified', 11],
  ['signed', 10],
  ['flight', 10],
  ['revolution', 9],
  ['treaty', 9],
  ['opened', 8],
  ['became', 8],
  ['inaugurated', 8],
  ['published', 7],
  ['completed', 7],
  ['introduced', 7],
  ['president', 6],
  ['parliament', 6],
  ['court', 6],
  ['space', 6],
];

const DOWNSCORE_TERMS = [
  ['viking', -34],
  ['vikings', -34],
  ['king', -20],
  ['queen', -20],
  ['emperor', -24],
  ['monarch', -22],
  ['coronation', -22],
  ['prince', -18],
  ['princess', -18],
  ['pope', -18],
  ['saint', -16],
  ['duke', -16],
  ['duchess', -16],
  ['crusade', -24],
  ['crusades', -24],
  ['roman emperor', -30],
  ['byzantine emperor', -30],
  ['kingdom of england', -24],
  ['invented', -14],
  ['thermometer', -20],
  ['telescope', -16],
  ['laboratory', -12],
  ['chemist', -16],
  ['physicist', -16],
  ['mathematician', -16],
  ['astronomer', -12],
  ['stabbing spree', -12],
  ['suicide bomber', -10],
  ['shooting', -8],
  ['bombing', -8],
  ['tornado', -6],
  ['earthquake', -6],
  ['killed', -5],
  ['x factor', -24],
  ['contestant', -18],
  ['judge', -12],
  ['opera', -5],
];

const LANE_TARGETS = {
  chronicle: 35,
  civic: 44,
  conflict: 20,
  culture: 38,
  rights: 48,
  science: 26,
  space: 34,
  transport: 24,
  tech: 36,
  music: 38,
  sports: 26,
  crime: 26,
  protest: 30,
  medicine: 18,
};

const ERA_TARGETS = {
  ancient: 10,
  medieval: 18,
  earlyModern: 28,
  eighteenth: 36,
  nineteenth: 55,
  early1900: 38,
  late1900: 110,
  recent: 70,
};

const LANE_BASE_BOOSTS = {
  music: 30,
  tech: 28,
  rights: 26,
  space: 24,
  protest: 24,
  sports: 22,
  crime: 20,
  medicine: 18,
  culture: 18,
  civic: 10,
  transport: 5,
  chronicle: 3,
  science: -6,
  conflict: -28,
};

const ERA_BASE_BOOSTS = {
  ancient: -14,
  medieval: -12,
  earlyModern: -6,
  eighteenth: -2,
  nineteenth: 4,
  early1900: -8,
  late1900: 22,
  recent: 24,
};

const GENERATED_EVENT_LOCKS = {
  '01-01': 'World War II',
  '01-02': 'Luna 1',
  '01-03': 'Battle of Princeton',
  '01-04': 'Spirit (rover)',
  '01-05': 'Battle of Bardia',
  '01-06': 'Maria Montessori',
  '01-07': 'Guy Menzies',
  '01-08': 'George Washington',
  '01-11': 'William Herschel',
  '02-01': 'Civil rights movement',
  '02-04': 'Bartolomeu Dias',
  '02-28': 'C. V. Raman',
  '03-25': 'Ward Cunningham',
  '04-05': 'Birkenhead Park',
  '05-13': 'Igor Sikorsky',
  '05-17': 'International Telecommunication Union',
  '05-20': "Dürer's Rhinoceros",
  '05-21': 'Spirit of St. Louis',
  '07-20': 'Lunar Module Eagle',
  '07-28': 'Vinnie Ream',
  '08-18': 'Nineteenth Amendment',
  '09-18': 'Nerva',
  '09-19': 'Universal suffrage',
  '09-25': 'Treaty of York',
  '11-09': 'Rolling Stone',
};

const GENERATED_LOCK_ALLOWLIST = new Set([
  '01-02',
  '01-04',
  '01-06',
  '01-19',
  '02-01',
  '02-03',
  '02-09',
  '02-10',
  '02-21',
  '02-28',
  '03-20',
  '03-21',
  '03-24',
  '03-25',
  '04-01',
  '04-16',
  '04-28',
  '05-10',
  '05-11',
  '05-22',
  '06-04',
  '06-07',
  '06-30',
  '07-18',
  '07-20',
  '07-28',
  '08-18',
  '08-27',
  '09-19',
  '11-09',
  '11-30',
  '12-25',
]);

const CURATED_EVENT_LOCKS = {
  '01-08': 'Joaquín "El Chapo" Guzmán',
  '01-09': 'iPhone',
  '01-13': 'Johnny Cash',
  '01-14': 'Arab Spring',
  '01-15': 'First Wikipedia edit',
  '01-18': 'Sting operation',
  '01-22': 'Super Bowl XVIII',
  '01-26': 'Apollo Theater',
  '01-31': 'Ham (chimpanzee)',
  '02-03': 'Pixar',
  '02-09': 'Beatlemania',
  '02-11': 'Nelson Mandela',
  '02-14': 'YouTube',
  '03-02': 'Wilt Chamberlain',
  '03-06': 'Muhammad Ali',
  '03-09': 'Barbie',
  '03-21': 'Sharpeville massacre',
  '04-03': 'iPad',
  '04-11': 'Australia 31-0 American Samoa',
  '04-14': 'Apollo 13',
  '04-15': 'Jackie Robinson',
  '05-06': 'iMac',
  '05-25': 'Star Wars',
  '05-26': "Sgt. Pepper's Lonely Hearts Club Band",
  '06-28': 'Stonewall Inn',
  '06-29': 'iPhone',
  '07-10': "1999 FIFA Women's World Cup final",
  '07-13': 'Live Aid',
  '07-18': 'Nadia Comăneci',
  '07-23': 'Tulia, Texas',
  '07-27': 'Madonna',
  '08-01': 'Video Killed the Radio Star',
  '08-03': 'Jesse Owens',
  '08-06': 'World Wide Web',
  '08-11': 'DJ Kool Herc',
  '08-16': 'Usain Bolt',
  '08-28': 'Althea Gibson',
  '09-07': 'Tupac Shakur',
  '09-13': 'Nirvana',
  '09-20': 'Battle of the Sexes',
  '10-01': 'Thrilla in Manila',
  '10-30': 'Michael Jackson',
  '11-07': 'Magic Johnson',
  '11-19': 'Pelé',
  '11-29': 'Thriller',
  '12-02': 'Pablo Escobar',
  '12-04': 'Fred Hampton',
  '12-13': 'Beyoncé',
  '12-19': 'Titanic',
  '12-20': 'Captain America',
  '12-25': 'WorldWideWeb',
  '12-31': 'Roberto Clemente',
};

const CUSTOM_EVENTS = {
  '01-08': [
    {
      year: 2016,
      text: 'Mexican marines recaptured Joaquín "El Chapo" Guzmán in Los Mochis after the Sinaloa Cartel leader had escaped from a maximum-security prison through a tunnel months earlier.',
      pages: [{
        title: 'Joaqu%C3%ADn_%22El_Chapo%22_Guzm%C3%A1n',
        normalizedtitle: 'Joaquín "El Chapo" Guzmán',
        description: 'Mexican drug lord and former Sinaloa Cartel leader',
        extract: 'Joaquín "El Chapo" Guzmán is a Mexican former drug lord and a former leader within the Sinaloa Cartel. He escaped from prison more than once before his 2016 recapture and later extradition to the United States.',
        content_urls: { desktop: { page: 'https://en.wikipedia.org/wiki/Joaqu%C3%ADn_%22El_Chapo%22_Guzm%C3%A1n' } },
      }],
    },
  ],
  '01-09': [
    {
      year: 2007,
      text: 'Steve Jobs introduced the first iPhone at Macworld in San Francisco, presenting a touch-screen phone, iPod, and internet communicator as one device.',
      pages: [{
        title: 'IPhone_(1st_generation)',
        normalizedtitle: 'iPhone (1st generation)',
        description: 'First smartphone model in the iPhone line',
        extract: 'The first-generation iPhone was announced by Steve Jobs on January 9, 2007, and later released in the United States on June 29, 2007.',
        content_urls: { desktop: { page: 'https://en.wikipedia.org/wiki/IPhone_(1st_generation)' } },
      }],
    },
  ],
  '06-29': [
    {
      year: 2007,
      text: 'The first iPhone went on sale in the United States, sending crowds to Apple Stores and turning the smartphone into the defining consumer-tech object of the era.',
      pages: [{
        title: 'IPhone_(1st_generation)',
        normalizedtitle: 'iPhone (1st generation)',
        description: 'First smartphone model in the iPhone line',
        extract: 'The first-generation iPhone was released in the United States on June 29, 2007, after being announced by Steve Jobs earlier that year.',
        content_urls: { desktop: { page: 'https://en.wikipedia.org/wiki/IPhone_(1st_generation)' } },
      }],
    },
  ],
  '07-13': [
    {
      year: 1985,
      text: 'Live Aid concerts were held in London and Philadelphia, linking stadium rock, television, and global fundraising into one of the biggest music broadcasts ever staged.',
      pages: [{
        title: 'Live_Aid',
        normalizedtitle: 'Live Aid',
        description: '1985 benefit concert for famine relief',
        extract: 'Live Aid was a dual-venue benefit concert held on 13 July 1985 at Wembley Stadium in London and John F. Kennedy Stadium in Philadelphia, watched by a huge global television audience.',
        content_urls: { desktop: { page: 'https://en.wikipedia.org/wiki/Live_Aid' } },
      }],
    },
  ],
  '12-02': [
    {
      year: 1993,
      text: 'Colombian National Police killed Pablo Escobar on a Medellín rooftop, ending the long manhunt for the Medellín Cartel boss.',
      pages: [{
        title: 'Pablo_Escobar',
        normalizedtitle: 'Pablo Escobar',
        description: 'Colombian drug lord and narcoterrorist',
        extract: 'Pablo Escobar was a Colombian drug lord and founder of the Medellín Cartel. He was killed in Medellín on December 2, 1993, after a long police manhunt.',
        content_urls: { desktop: { page: 'https://en.wikipedia.org/wiki/Pablo_Escobar' } },
      }],
    },
  ],
};

const GENERIC_PAGE_TITLES = new Set([
  'world war i',
  'world war ii',
  'american civil war',
  'crusades',
  'cold war',
]);

const RECENT_PENALTY_AFTER = 2010;
const MAX_EVENT_YEAR = 2024;
const MIN_BRIEF_WORDS = 1000;
const MAX_BRIEF_WORDS = 2000;
const REQUEST_SPACING_MS = 650;
const MAX_FETCH_ATTEMPTS = 24;

let lastRequestAt = 0;

const IMPACT_LENSES = {
  space: {
    field: 'space exploration',
    stakes: 'national prestige, engineering risk, military technology, public imagination, and the satellite economy',
    today: 'weather forecasting, navigation, climate monitoring, telecommunications, defense planning, and the way governments justify long-horizon science programs',
    lesson: 'large technical leaps become durable only when institutions can turn a dramatic mission into repeatable infrastructure',
  },
  science: {
    field: 'science and technology',
    stakes: 'evidence, instruments, laboratories, peer communities, standards, and public trust',
    today: 'medicine, engineering, regulation, education, industrial research, and the public expectation that facts can be tested rather than simply asserted',
    lesson: 'discovery matters most when it changes the methods other people can use after the first announcement fades',
  },
  rights: {
    field: 'rights and public life',
    stakes: 'law, citizenship, representation, protest, enforcement, and the boundary between formal equality and lived equality',
    today: 'voting rules, civil liberties, courts, school systems, labor markets, public memory, and the language people use to make claims on power',
    lesson: 'a rights milestone is not a finish line; it is a change in the terrain on which later generations keep fighting',
  },
  civic: {
    field: 'government and institutions',
    stakes: 'legitimacy, borders, treaties, constitutions, executive power, public finance, and the machinery of administration',
    today: 'international law, diplomacy, elections, courts, public agencies, crisis management, and the everyday paperwork through which states become real',
    lesson: 'institutions can seem abstract until one signature, vote, ruling, or resignation changes what millions of people are allowed to do next',
  },
  conflict: {
    field: 'war and security',
    stakes: 'state power, military technology, civilian vulnerability, alliance systems, resources, memory, and the cost of command decisions',
    today: 'defense budgets, borders, memorial culture, humanitarian law, veterans policy, intelligence systems, and debates over when force is justified',
    lesson: 'conflict reshapes the future not only through victory or defeat, but through the systems societies build afterward to prevent, prepare for, or remember it',
  },
  culture: {
    field: 'culture and media',
    stakes: 'taste, language, fame, technology, audiences, patronage, ownership, and the channels through which stories travel',
    today: 'publishing, streaming, museums, schools, advertising, celebrity, fandom, and the way societies decide which works deserve preservation',
    lesson: 'cultural milestones endure when they give later audiences a new form, a new voice, or a new way to recognize themselves',
  },
  transport: {
    field: 'movement and infrastructure',
    stakes: 'distance, trade, migration, engineering, logistics, timekeeping, military reach, and public confidence in machines',
    today: 'supply chains, aviation, ports, roads, rail, tourism, emergency response, and the expectation that people and goods can cross huge distances quickly',
    lesson: 'a transportation breakthrough changes more than travel; it changes what people believe is near, possible, and economically connected',
  },
  chronicle: {
    field: 'public memory',
    stakes: 'records, institutions, belief, archives, public attention, and the stories a society chooses to keep retelling',
    today: 'education, journalism, museums, civic ritual, political identity, and the habit of using the past as evidence in arguments about the present',
    lesson: 'a remembered date matters because it condenses a larger historical process into a scene people can return to and debate',
  },
};

function pad(value) {
  return String(value).padStart(2, '0');
}

function daysInMonth(year, monthIndex) {
  return new Date(year, monthIndex + 1, 0).getDate();
}

function dayKeys() {
  const days = [];

  for (let month = 1; month <= 12; month += 1) {
    for (let day = 1; day <= daysInMonth(2025, month - 1); day += 1) {
      days.push(`${pad(month)}-${pad(day)}`);
    }
  }

  return days;
}

function collapseWhitespace(value) {
  return String(value || '').replace(/\s+/g, ' ').trim();
}

function stripHtml(value) {
  return collapseWhitespace(String(value || '')
    .replace(/<style[\s\S]*?<\/style>/gi, ' ')
    .replace(/<script[\s\S]*?<\/script>/gi, ' ')
    .replace(/<[^>]*>/g, ' ')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&#039;|&apos;/g, "'")
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>'));
}

function stripDisplayNoise(value) {
  return collapseWhitespace(stripHtml(value))
    .replace(/\s*\((?=[^)]*\b(?:pictured|depicted|shown|illustrated)\b)[^)]*\)/gi, '')
    .replace(/\s*\[(?:citation needed|note \d+)\]/gi, '')
    .replace(/\s+([,.;:!?])/g, '$1');
}

function sentenceCase(value) {
  const text = collapseWhitespace(value);
  if (!text) return '';
  return text.charAt(0).toUpperCase() + text.slice(1);
}

function ensureSentence(value) {
  const text = collapseWhitespace(value);
  if (!text) return '';
  return /[.!?]$/.test(text) ? text : `${text}.`;
}

function trimWords(value, maxWords) {
  const words = collapseWhitespace(value).split(' ').filter(Boolean);
  if (words.length <= maxWords) return words.join(' ');
  return `${words.slice(0, maxWords).join(' ').replace(/[,:;]$/, '')}...`;
}

function wordCount(value) {
  return collapseWhitespace(value).split(/\s+/).filter(Boolean).length;
}

function eraKeyForYear(year) {
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

function cachePathFor(url) {
  const hash = crypto.createHash('sha1').update(String(url)).digest('hex');
  return path.join(cacheDir, `${hash}.json`);
}

function pageTitle(page) {
  return stripHtml(page?.titles?.normalized || page?.normalizedtitle || page?.title?.replace(/_/g, ' ') || '');
}

function pageUrl(page) {
  return page?.content_urls?.desktop?.page || `https://en.wikipedia.org/wiki/${encodeURIComponent(page?.title || '')}`;
}

function normalizeTitle(value) {
  return collapseWhitespace(value)
    .replace(/\s*\([^)]*\)\s*/g, ' ')
    .toLowerCase();
}

function scoreEvent(event) {
  const text = `${event.text || ''} ${(event.pages || []).map((page) => `${pageTitle(page)} ${page.description || ''}`).join(' ')}`.toLowerCase();
  let score = 0;

  for (const [term, weight] of BIG_TERMS) {
    if (text.includes(term)) score += weight;
  }

  for (const [term, weight] of DOWNSCORE_TERMS) {
    if (text.includes(term)) score += weight;
  }

  if (event.year < 0) score -= 18;
  if (event.year >= 0 && event.year < 500) score -= 16;
  if (event.year >= 500 && event.year < 1500) score -= 14;
  if (event.year >= 1500 && event.year < 1700) score -= 8;
  if (event.year >= 1700 && event.year < 1800) score -= 2;
  if (event.year >= 1800 && event.year < 1900) score += 6;
  if (event.year >= 1900 && event.year < 1930) score -= 8;
  if (event.year >= 1930 && event.year < 2000) score += 22;
  if (event.year >= 2000) score += 26;
  if (event.year > RECENT_PENALTY_AFTER) score -= Math.min(10, Math.floor((event.year - RECENT_PENALTY_AFTER) * 0.5));

  if (/\b(first|independence|constitution|treaty|founded|launched|landed|ratified|opened|completed)\b/i.test(text)) score += 5;
  if (/\b(album|single|song|music|concert|broadcast|recording|film|movie|television|magazine|comic|video|photograph|painting|sculpture|theatre|theater|published)\b/i.test(text)) score += 24;
  if (/\b(iphone|macintosh|ipad|computer|internet|world wide web|wikipedia|youtube|social media|software|video game)\b/i.test(text)) score += 26;
  if (/\b(science|scientist|discovered|laboratory|telescope|astronomy|physics|chemistry|biology|medicine|vaccine|mathematics|archaeology|fossil)\b/i.test(text)) score += 4;
  if (/\b(women|suffrage|civil rights|human rights|abolished slavery|emancipation|citizenship|vote|equality|apartheid)\b/i.test(text)) score += 13;
  if (/\b(exploration|voyage|expedition|crossed|reached|sailed|flight|railway|railroad|bridge|canal|ship|aircraft)\b/i.test(text)) score += 7;
  if (/\b(drug|cartel|cocaine|arrested|captured|convicted|trial|court|scandal|heist|robbery|mafia|fbi)\b/i.test(text)) score += 20;
  if (/\b(olympic|world cup|basketball|football|tennis|boxing|baseball|cricket|soccer|marathon)\b/i.test(text)) score += 18;
  if (/\b(roller coaster|sport|football team|judge|contestant|reality television)\b/i.test(text)) score -= 8;
  if (/\b(world war|second world war|first world war|battle|siege|invasion|army|navy|air force|military campaign)\b/i.test(text)) score -= 24;
  if (/\b(king|queen|emperor|monarch|prince|pope|saint|duke|coronation|viking|crusade)\b/i.test(text)) score -= 22;
  if (/\b(massacre|chemical weapons|genocide|holocaust|civilian)\b/i.test(text)) score += 4;
  if (event.pages?.length > 1) score += Math.min(6, event.pages.length - 1);

  return score;
}

function pageScoreForEvent(page, event, index) {
  const title = normalizeTitle(pageTitle(page));
  const text = normalizeTitle(event.text || '');
  if (!title) return -100;

  let score = 30 - (index * 5);
  if (text.includes(title)) score += 30;
  const titleWords = title.split(/\s+/).filter((word) => word.length > 4 && !/^(united|states|american|british|french|first|second|third)$/.test(word));
  score += titleWords.filter((word) => text.includes(word)).length * 4;
  if (page.extract) score += 4;
  if (page.description) score += 3;
  if (GENERIC_PAGE_TITLES.has(title)) score -= 18;
  if (/\b(empire|kingdom|army|navy|air force|parliament|congress|president)\b/.test(title)) score -= 8;
  if (/\bdeclaration\b/.test(title) && /\bdeclaration\b/.test(text)) score += 28;
  if (/\bindependence\b/.test(title) && /\bindependence\b/.test(text)) score += 16;
  if (/\btreaty\b/.test(title) && /\btreaty\b/.test(text)) score += 18;
  if (/\bbattle\b/.test(title) && /\bbattle\b/.test(text)) score += 18;
  if (/\bmassacre\b/.test(title) && /\bmassacre\b/.test(text)) score += 18;
  if (/^(king|queen|president|pope|saint)\b/.test(title)) score -= 2;
  if (/\b(treaty|battle|declaration|revolution|flight|mission|act|council|war|constitution)\b/.test(title)) score += 7;

  return score;
}

function choosePrimaryPage(event) {
  const pages = Array.isArray(event.pages) ? event.pages.filter(Boolean) : [];
  if (!pages.length) return {};

  return pages
    .map((page, index) => ({ page, score: pageScoreForEvent(page, event, index) }))
    .sort((a, b) => b.score - a.score)[0].page;
}

function pickEvent(events) {
  const eligible = events
    .filter((event) => Number.isFinite(event.year))
    .filter((event) => event.year <= MAX_EVENT_YEAR)
    .filter((event) => event.pages?.[0])
    .map((event) => ({ event, score: scoreEvent(event) }))
    .sort((a, b) => b.score - a.score || Math.abs(a.event.year) - Math.abs(b.event.year));

  return eligible[0]?.event || events.find((event) => event.pages?.[0]) || events[0];
}

function targetAdjustment(key, counts, targets) {
  const target = targets[key] || 24;
  const count = counts[key] || 0;
  const ratio = count / target;

  if (ratio < 0.35) return 24;
  if (ratio < 0.65) return 16;
  if (ratio < 0.9) return 8;
  if (ratio < 1) return 3;
  return -Math.min(42, (count - target + 1) * 5);
}

function balancedCandidateScore(candidate, counts) {
  const lane = candidate.moment.visual || 'chronicle';
  const era = eraKeyForYear(candidate.moment.year);
  return candidate.score
    + (LANE_BASE_BOOSTS[lane] || 0)
    + (ERA_BASE_BOOSTS[era] || 0)
    + targetAdjustment(lane, counts.lanes, LANE_TARGETS)
    + targetAdjustment(era, counts.eras, ERA_TARGETS);
}

function chooseBalancedCandidate(daySet, counts) {
  const lock = CURATED_EVENT_LOCKS[daySet.key]
    || (GENERATED_LOCK_ALLOWLIST.has(daySet.key) ? GENERATED_EVENT_LOCKS[daySet.key] : null);
  if (lock) {
    const normalizedLock = normalizeTitle(lock);
    const locked = daySet.candidates.find((candidate) => {
      const title = normalizeTitle(candidate.moment.title);
      const text = normalizeTitle(candidate.moment.text);
      return title === normalizedLock || text.includes(normalizedLock);
    });
    if (locked) return locked;
  }

  return daySet.candidates
    .map((candidate) => ({
      ...candidate,
      balancedScore: balancedCandidateScore(candidate, counts),
    }))
    .sort((a, b) => b.balancedScore - a.balancedScore || a.moment.year - b.moment.year)[0];
}

function daySetPriority(daySet) {
  return daySet.candidates.reduce((highest, candidate) => {
    const lane = candidate.moment.visual || 'chronicle';
    const era = eraKeyForYear(candidate.moment.year);
    const score = (LANE_BASE_BOOSTS[lane] || 0) + (ERA_BASE_BOOSTS[era] || 0);
    return Math.max(highest, score);
  }, -100);
}

function classifyVisual(momentText, title, description) {
  const text = `${momentText} ${title} ${description}`.toLowerCase();

  if (/\b(iphone|ipad|macintosh|apple computer|world wide web|internet|wikipedia|youtube|google|facebook|netflix|software|computer|video game|smartphone|social media)\b/.test(text)) return 'tech';
  if (/\b(album|song|music|concert|hip hop|rap|rock and roll|jazz|mtv|beatles|michael jackson|beyonce|tupac|madonna|thriller|live aid|recording|singer|band|apollo theater|apollo theatre)\b/.test(text)) return 'music';
  if (/\b(civil rights|suffrage|women|vote|rights|slavery|emancipation|apartheid|equality|desegregation|voting rights|mandela|malcolm x|black panther|fred hampton|althea gibson)\b/.test(text)) return 'rights';
  if (/\b(protest|protests|protester|demonstrator|demonstrators|strike|boycott|uprising|riot|demonstration|arab spring|people power|stonewall|tank man)\b/.test(text)) return 'protest';
  if (/\b(olympic|world cup|basketball|football|footballer|tennis|boxing|baseball|cricket|soccer|marathon|super bowl|wimbledon|athlete|usain bolt|pele|pelé)\b/.test(text)) return 'sports';
  if (/\b(food and drug administration|vaccine|medicine|medical|drug sildenafil|contraceptive pill|oral contraceptive|viagra|public health|hiv|aids|hospital|surgery|treatment)\b/.test(text)) return 'medicine';
  if (/\b(drug|cartel|cocaine|narcotics|mafia|arrested|captured|convicted|trial|scandal|heist|robbery|fbi|prison|pablo escobar|el chapo|guzman)\b/.test(text)) return 'crime';
  if (/\b(apollo|moon|space|spacecraft|nasa|rocket|satellite|mars|orbit|astronaut|lunar)\b/.test(text)) return 'space';
  if (/\b(film|music|novel|book|dictionary|poem|poetry|museum|library|art|artist|painting|sculpture|photograph|photography|television|broadcast|radio drama|recording|album|magazine|newspaper|theatre|theater|opera|ballet|concert|publishing|literature)\b/.test(text)) return 'culture';
  if (/\b(science|scientist|discovered|dna|genome|vaccine|physics|chemical|chemistry|biology|astronomy|medicine|computer|internet|telegraph|plutonium|radiation|mathematics|telescope|microscope|laboratory|archaeology|fossil)\b/.test(text)) return 'science';
  if (/\b(railway|railroad|flight|aircraft|ship|canal|bridge|tunnel|voyage|expedition|circumnavigate|transatlantic|rover|reaches|sail|sailed|crossed)\b/.test(text)) return 'transport';
  if (/\b(independence|constitution|treaty|declaration|parliament|congress|president|king|queen|united nations|law|court|resigned)\b/.test(text)) return 'civic';
  if (/\b(war|battle|invasion|siege|revolution|army|navy|empire|assassinated|crusades)\b/.test(text)) return 'conflict';
  return 'chronicle';
}

function paletteFor(visual) {
  return {
    space: 'lunar',
    science: 'laboratory',
    rights: 'public-square',
    civic: 'civic',
    conflict: 'dispatch',
    culture: 'stage',
    transport: 'voyage',
    tech: 'laboratory',
    music: 'stage',
    sports: 'public-square',
    crime: 'dispatch',
    medicine: 'laboratory',
    protest: 'public-square',
    chronicle: 'archive',
  }[visual] || 'archive';
}

function formatYear(year) {
  const value = Number(year);
  if (!Number.isFinite(value)) return 'unknown year';
  return value < 0 ? `${Math.abs(value)} BCE` : String(value);
}

function makeHeadline(eventText, title) {
  const clean = stripDisplayNoise(eventText);
  if (!clean) return title || 'A historical moment';
  const withoutPrefix = clean
    .replace(/^(?:World War I|World War II|Second World War|First World War|American Civil War|The Crusades|The Crusades:|Arab-Byzantine wars):\s*/i, '')
    .replace(/\s+/g, ' ');
  if (wordCount(withoutPrefix) <= 18) return sentenceCase(withoutPrefix);
  return sentenceCase(trimWords(withoutPrefix, 18));
}

function extractSentences(value, limit = 5) {
  const text = stripDisplayNoise(value);
  if (!text) return [];
  return text
    .split(/(?<=[.!?])\s+/)
    .map((sentence) => ensureSentence(sentence))
    .filter((sentence) => wordCount(sentence) > 6)
    .slice(0, limit);
}

function listJoin(items) {
  const values = items.filter(Boolean);
  if (values.length <= 1) return values.join('');
  if (values.length === 2) return `${values[0]} and ${values[1]}`;
  return `${values.slice(0, -1).join(', ')}, and ${values.at(-1)}`;
}

function buildFacts(moment, relatedPages) {
  const facts = [
    { label: 'Date', value: moment.displayDate },
    { label: 'Year', value: formatYear(moment.year) },
    { label: 'Primary topic', value: moment.topic || moment.title },
    { label: 'Historical lane', value: IMPACT_LENSES[moment.visual]?.field || 'public memory' },
  ];

  const related = relatedPages
    .map((page) => page.title)
    .filter((title) => title && title !== moment.topic)
    .slice(0, 3);

  if (related.length) {
    facts.push({ label: 'Related record', value: listJoin(related) });
  }

  return facts;
}

function buildImpactBullets(moment) {
  const lens = IMPACT_LENSES[moment.visual] || IMPACT_LENSES.chronicle;
  return [
    `It shaped ${lens.field} by forcing people to rethink ${lens.stakes}.`,
    `Its legacy still appears in ${lens.today}.`,
    `The enduring lesson: ${lens.lesson}.`,
  ];
}

function buildLongBrief(moment, page, relatedPages) {
  const lens = IMPACT_LENSES[moment.visual] || IMPACT_LENSES.chronicle;
  const yearLabel = formatYear(moment.year);
  const topic = moment.topic || moment.title || 'this event';
  const relatedNames = relatedPages
    .map((related) => related.title)
    .filter((title) => title && title !== topic)
    .slice(0, 5);
  const relatedText = relatedNames.length ? listJoin(relatedNames) : 'the people, places, and institutions around it';
  const sourceSentences = [
    ...extractSentences(page.extract, 4),
    ...relatedPages.flatMap((related) => extractSentences(related.extract, 2)),
  ].slice(0, 10);

  const sourceBlockA = sourceSentences.slice(0, 3).join(' ');
  const sourceBlockB = sourceSentences.slice(3, 6).join(' ');
  const sourceBlockC = sourceSentences.slice(6, 10).join(' ');

  const paragraphs = [
    `On ${moment.displayDate} in ${yearLabel}: ${moment.text} The Press marks it as the day's big history moment because it compresses a larger turn in ${lens.field} into one date, one decision, and one public memory. The event is not important only because it happened; it matters because later institutions, communities, and governments had to react to it. A daily history item works best when it does more than decorate a calendar. It should explain why a particular scene still has gravity. In this case, the scene around ${topic} connects immediate facts to a longer chain of consequences, showing how a single anniversary can hold arguments about power, technology, identity, law, and memory at the same time.`,

    `The basic facts are direct. ${ensureSentence(moment.text)} The primary record for this entry is ${moment.sourceLabel}, and the surrounding archive points to ${relatedText}. Those connected subjects help keep the anniversary from becoming a loose trivia item. They show who acted, what systems were already in motion, and why the event was legible to people at the time. History often feels inevitable after the fact, but it rarely feels that way while it is unfolding. People made choices with partial information, limited tools, political pressure, personal ambition, fear, hope, or institutional habit. The resulting moment became visible because those choices collided with a larger process already moving through the world.`,

    sourceBlockA
      ? `The source material adds useful context. ${sourceBlockA} Read together, those details show that the event was part of a network rather than an isolated headline. The surrounding world included institutions with their own incentives, publics with their own anxieties, and technologies or legal systems that made some outcomes possible while closing off others. That is why the anniversary deserves more than a caption. It opens a door into the practical machinery behind the headline: the offices, vessels, laboratories, assemblies, streets, battlefields, newsrooms, courts, or communities where history stopped being abstract and became a sequence of concrete actions.`
      : `The surrounding record matters because it keeps the event anchored in a real world of offices, streets, machines, institutions, and people. Anniversaries can flatten history into a single line, but the important facts usually sit in the layers around that line. Who had authority? Who had information? Who was excluded from the decision? What tools made the action possible? What risks were accepted as normal? Those questions turn a date into a historical argument. They also explain why a single event can keep echoing after the original actors leave the stage.`,

    `The immediate impact depended on the field it touched. In ${lens.field}, the stakes were ${lens.stakes}. That is a broad list, but it is exactly the point: big historical moments rarely stay inside the category assigned to them. A treaty can change borders and family life. A scientific achievement can change budgets, schools, factories, and war planning. A cultural work can change language, identity, markets, and memory. A conflict can redraw maps while also changing law, medicine, journalism, and the private grief of households. The event connected to ${topic} carried that kind of spillover. It entered public life because people beyond the original scene had to adjust to it.`,

    sourceBlockB
      ? `Another set of facts deepens the picture. ${sourceBlockB} These details help explain scale. They point to the people and structures that turned the event into something durable. The first public reaction is only one layer of historical significance. The deeper question is whether the event changed routines. Did it create a new institution? Did it alter how governments measured risk? Did it make a technology feel normal? Did it expose an injustice that could no longer be ignored? Did it give artists, teachers, officials, soldiers, workers, or citizens a new reference point? The answer is why this date still earns space in the archive.`
      : `The scale of the event becomes clearer when it is measured by routines rather than headlines. A moment matters when people have to change what they do next: rewrite rules, build tools, mourn losses, revise maps, retell stories, or defend old systems against new pressure. The first reaction may have been confusion, celebration, fear, or indifference. The longer reaction is more revealing. It shows up in institutions, budgets, schoolbooks, infrastructure, legal precedents, diplomatic habits, family memory, and the language people use to describe what is possible.`,

    `The world today still carries traces of this kind of moment in ${lens.today}. That does not mean the event alone created the present. History is not a straight pipe from one anniversary to one modern outcome. The better way to understand impact is as accumulation. A single date becomes important when it joins other dates and pushes a system toward a new normal. The effect may be visible in law, technology, borders, culture, or public expectations. It may also be visible in what people now consider unacceptable, obvious, heroic, tragic, outdated, or inevitable. The anniversary is a reminder that those categories were built over time, often through conflict and argument.`,

    `One reason this event remains useful is that it gives the past a human scale. ${topic} is a name, place, object, office, or episode that can be pictured. Around it, though, sits a larger structure: ${relatedText}. That structure is where the real historical weight lives. Dates help readers enter the story, but they should not trap the story there. The important facts include the event itself, the conditions that made it possible, the people who benefited, the people who paid for it, and the records that allow later generations to argue about it. Good history keeps all of those layers in view.`,

    sourceBlockC
      ? `The record also notes: ${sourceBlockC} These fragments are useful because they resist the temptation to treat the event as symbolism only. They restore texture. They make clear that the anniversary belongs to a specific world, not to a vague idea of the past. The details may involve dates, institutions, names, locations, technologies, or consequences, but their function is the same. They tell the reader that history is built from evidence. When evidence is kept close to the story, impact can be discussed without turning into myth.`
      : `The factual record also keeps the anniversary honest. Without facts, a historical moment becomes a slogan. With facts, it becomes a case study. The date, the year, the actors, the place, the tools, and the immediate result all matter because they limit lazy interpretation. They force the story to remain specific. Specificity is what lets a reader compare one event with another and see patterns without pretending every event is the same.`,

    `The long-term lesson is this: ${lens.lesson}. That lesson is not a neat moral. It is a way to read the anniversary with the present in mind. When modern debates touch ${lens.today}, they often inherit assumptions formed by earlier events like this one. People may not cite ${moment.displayDate} directly, but they live inside systems shaped by older decisions, discoveries, conflicts, performances, journeys, laws, and public reactions. The daily history feature is meant to make that inheritance visible. It says that today is not floating by itself. It is attached to a deep archive of experiments, mistakes, breakthroughs, compromises, and unfinished arguments.`,

    `So the reason to remember ${moment.displayDate} is not nostalgia. It is orientation. ${ensureSentence(moment.text)} The event gives readers a way to ask sharper questions about the present: What changed after this? Who gained power? Who lost safety or status? What became easier to imagine? What became harder to deny? Which institutions learned the lesson, and which refused it? Those questions are the bridge between a historical fact and its modern impact. They are also why a calendar item can belong on a front page: it turns a date into context, and context is one of the few tools that makes the daily news easier to understand.`,
  ].map((paragraph) => collapseWhitespace(paragraph));

  let brief = paragraphs.slice();
  while (wordCount(brief.join(' ')) < MIN_BRIEF_WORDS) {
    brief.push(collapseWhitespace(`A final way to read the moment is through continuity. The details around ${topic} show how the past travels forward through institutions, habits, technologies, borders, and public language. The world changes, but it keeps older decisions embedded inside newer systems. That is why the anniversary still matters: it gives readers a concrete place to begin tracing those connections without pretending the story is simple.`));
  }

  while (wordCount(brief.join(' ')) > MAX_BRIEF_WORDS && brief.length > 7) {
    brief.splice(-2, 1);
  }

  return brief;
}

function buildDek(moment) {
  const lens = IMPACT_LENSES[moment.visual] || IMPACT_LENSES.chronicle;
  return `A daily brief on how ${moment.topic || moment.title} moved through ${lens.field} and why the consequences still show up now.`;
}

async function fetchJson(url, attempt = 1) {
  const cachePath = cachePathFor(url);
  try {
    return JSON.parse(await fs.readFile(cachePath, 'utf8'));
  } catch (_) {}

  const elapsed = Date.now() - lastRequestAt;
  if (elapsed < REQUEST_SPACING_MS) {
    await new Promise((resolve) => setTimeout(resolve, REQUEST_SPACING_MS - elapsed));
  }
  lastRequestAt = Date.now();

  let response;
  try {
    response = await fetch(url, {
      headers: { 'User-Agent': userAgent },
    });
  } catch (error) {
    if (attempt < MAX_FETCH_ATTEMPTS) {
      await new Promise((resolve) => setTimeout(resolve, Math.min(60000, 3000 * attempt)));
      return fetchJson(url, attempt + 1);
    }
    throw error;
  }

  if (!response.ok) {
    if (attempt < MAX_FETCH_ATTEMPTS && (response.status === 429 || response.status >= 500)) {
      const retryAfter = Number(response.headers.get('retry-after'));
      const wait = Number.isFinite(retryAfter) && retryAfter > 0
        ? retryAfter * 1000
        : Math.min(60000, 3000 * attempt);
      await new Promise((resolve) => setTimeout(resolve, wait));
      return fetchJson(url, attempt + 1);
    }
    throw new Error(`Request failed: ${response.status} ${response.statusText} ${url}`);
  }

  const payload = await response.json();
  await fs.mkdir(cacheDir, { recursive: true });
  await fs.writeFile(cachePath, JSON.stringify(payload));
  return payload;
}

function buildMoment(key, event) {
  const [month, day] = key.split('-');
  const page = choosePrimaryPage(event);
  const title = pageTitle(page);
  const monthIndex = Number(month) - 1;
  const text = stripDisplayNoise(event.text);
  const visual = classifyVisual(text, title, page.description || '');
  const relatedPages = (event.pages || [])
    .filter((related) => pageTitle(related))
    .map((related) => ({
      title: pageTitle(related),
      source: pageUrl(related),
      extract: stripDisplayNoise(related.extract || ''),
      description: stripDisplayNoise(related.description || ''),
    }))
    .slice(0, 6);

  const moment = {
    date: key,
    displayDate: `${MONTHS[monthIndex]} ${Number(day)}`,
    year: event.year,
    title,
    topic: title,
    headline: makeHeadline(text, title),
    text,
    source: pageUrl(page),
    sourceLabel: `Wikipedia: ${title}`,
    sourceDescription: stripDisplayNoise(page.description || ''),
    visual,
    palette: paletteFor(visual),
  };

  moment.dek = buildDek(moment);
  moment.facts = buildFacts(moment, relatedPages);
  moment.impact = buildImpactBullets(moment);
  moment.summary = buildLongBrief(moment, {
    ...page,
    extract: stripDisplayNoise(page.extract || ''),
  }, relatedPages);
  moment.wordCount = wordCount(moment.summary.join(' '));
  moment.related = relatedPages.slice(0, 4).map(({ title: relatedTitle, source, description }) => ({
    title: relatedTitle,
    source,
    description,
  }));

  return moment;
}

async function fetchDayCandidates(key) {
  const [month, day] = key.split('-');
  const payload = await fetchJson(`${endpointBase}/${month}/${day}`);
  const selected = [
    ...(Array.isArray(payload.selected) ? payload.selected : []),
    ...(CUSTOM_EVENTS[key] || []),
  ];
  if (!selected.length) throw new Error(`No selected anniversaries returned for ${key}`);

  const candidates = selected
    .filter((event) => Number.isFinite(event.year))
    .filter((event) => event.year <= MAX_EVENT_YEAR)
    .filter((event) => event.pages?.[0])
    .map((event) => ({
      event,
      moment: buildMoment(key, event),
      score: scoreEvent(event),
    }))
    .filter((candidate) => candidate.moment.title);

  if (!candidates.length) {
    const fallback = pickEvent(selected);
    candidates.push({
      event: fallback,
      moment: buildMoment(key, fallback),
      score: scoreEvent(fallback),
    });
  }

  return { key, candidates };
}

async function mapLimit(items, limit, worker) {
  const results = new Array(items.length);
  let next = 0;

  async function run() {
    while (next < items.length) {
      const index = next;
      next += 1;
      results[index] = await worker(items[index], index);
    }
  }

  await Promise.all(Array.from({ length: limit }, run));
  return results;
}

const keys = dayKeys();
const daySets = await mapLimit(keys, 1, async (key, index) => {
  const daySet = await fetchDayCandidates(key);
  process.stdout.write(`${index + 1}/${keys.length} ${key} fetched ${daySet.candidates.length} candidate${daySet.candidates.length === 1 ? '' : 's'}\n`);
  return daySet;
});

const counts = { lanes: {}, eras: {} };
const selected = [];

for (const daySet of [...daySets].sort((a, b) => daySetPriority(b) - daySetPriority(a) || keys.indexOf(a.key) - keys.indexOf(b.key))) {
  const candidate = chooseBalancedCandidate(daySet, counts);
  const lane = candidate.moment.visual || 'chronicle';
  const era = eraKeyForYear(candidate.moment.year);
  counts.lanes[lane] = (counts.lanes[lane] || 0) + 1;
  counts.eras[era] = (counts.eras[era] || 0) + 1;
  selected.push(candidate.moment);
}

const moments = selected.sort((a, b) => a.date.localeCompare(b.date));
const byDate = Object.fromEntries(moments.map((moment) => [moment.date, moment]));

if (Object.keys(byDate).length !== 365) {
  throw new Error(`Expected 365 moments, got ${Object.keys(byDate).length}`);
}

process.stdout.write(`Lane mix: ${JSON.stringify(counts.lanes)}\n`);
process.stdout.write(`Era mix: ${JSON.stringify(counts.eras)}\n`);

const generatedAt = new Date().toISOString();
const file = `/*\n` +
  `  The Press daily history moments.\n` +
  `  Generated from Wikimedia's English Wikipedia On This Day selected-anniversary feed.\n` +
  `  Includes balanced era/topic selection, long-form editorial briefs, and image direction.\n` +
  `  Source endpoint pattern: ${endpointBase}/MM/DD\n` +
  `  Wikipedia text is available under CC BY-SA; generated visual assets are tracked separately.\n` +
  `  Generated at: ${generatedAt}\n` +
  `*/\n` +
  `window.PRESS_ON_THIS_DAY_ATTRIBUTION = ${JSON.stringify({
    source: 'Wikimedia On This Day selected-anniversary feed',
    endpoint: `${endpointBase}/MM/DD`,
    textLicense: 'CC BY-SA',
    selectionPolicy: 'Quota-aware selection favors an eclectic mix across eras, culture, science, rights, civic life, transport, space, conflict, and chronicle entries.',
    visualPolicy: 'Use real generated photorealistic or premium editorial illustration assets. Do not use geometric SVG placeholders as finished artwork.',
    generatedAt,
    count: 365,
    minBriefWords: MIN_BRIEF_WORDS,
  }, null, 2)};\n` +
  `window.PRESS_ON_THIS_DAY_MOMENTS = ${JSON.stringify(byDate, null, 2)};\n`;

await fs.mkdir(path.dirname(outputPath), { recursive: true });
await fs.writeFile(outputPath, file);
process.stdout.write(`Wrote ${outputPath} with ${Object.keys(byDate).length} editorial illustration entries\n`);
