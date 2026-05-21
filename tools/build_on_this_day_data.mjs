import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, '..');
const outputPath = path.join(rootDir, 'assets', 'on-this-day-moments.js');
const endpointBase = 'https://en.wikipedia.org/api/rest_v1/feed/onthisday/selected';
const userAgent = 'The Press local build (https://thepress.live/)';

const MONTHS = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
];

const BIG_TERMS = [
  ['apollo', 22],
  ['moon', 18],
  ['independence', 18],
  ['declaration', 16],
  ['constitution', 15],
  ['united nations', 15],
  ['world war', 14],
  ['first', 11],
  ['founded', 10],
  ['established', 10],
  ['ratified', 10],
  ['signed', 10],
  ['launched', 10],
  ['landed', 10],
  ['discovered', 9],
  ['opened', 8],
  ['revolution', 8],
  ['treaty', 8],
  ['became', 7],
  ['inaugurated', 7],
  ['published', 6],
  ['completed', 6],
  ['introduced', 6],
  ['invented', 6],
  ['spacecraft', 6],
  ['space', 5],
  ['civil rights', 5],
  ['suffrage', 5],
  ['women', 4],
  ['war', 3],
  ['battle', 3],
];

const RECENT_PENALTY_AFTER = 2010;

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

function stripDisplayNoise(value) {
  return collapseWhitespace(value)
    .replace(/\s*\((?=[^)]*\b(?:pictured|depicted|shown|illustrated)\b)[^)]*\)/gi, '')
    .replace(/\s*\[(?:citation needed|note \d+)\]/gi, '')
    .replace(/\s+([,.;:!?])/g, '$1');
}

function pageTitle(page) {
  return page?.titles?.normalized || page?.normalizedtitle || page?.title?.replace(/_/g, ' ') || '';
}

function pageUrl(page) {
  return page?.content_urls?.desktop?.page || `https://en.wikipedia.org/wiki/${encodeURIComponent(page?.title || '')}`;
}

function scoreEvent(event) {
  const page = event.pages?.[0] || {};
  const text = `${event.text || ''} ${pageTitle(page)} ${page.description || ''}`.toLowerCase();
  let score = 0;

  for (const [term, weight] of BIG_TERMS) {
    if (text.includes(term)) score += weight;
  }

  if (event.year < 0) score += 5;
  if (event.year >= 0 && event.year < 1900) score += 6;
  if (event.year >= 1900 && event.year < 2000) score += 4;
  if (event.year > RECENT_PENALTY_AFTER) score -= Math.min(10, Math.floor((event.year - RECENT_PENALTY_AFTER) / 2));

  if (/\b(killed|massacre|bombing|assassinated|suicide attack|shooting)\b/i.test(text)) score -= 4;
  if (/\b(first|independence|constitution|treaty|founded|launched|landed|ratified|opened)\b/i.test(text)) score += 4;
  if (event.pages?.length > 1) score += Math.min(4, event.pages.length - 1);

  return score;
}

function classifyVisual(momentText, title, description) {
  const text = `${momentText} ${title} ${description}`.toLowerCase();

  if (/\b(apollo|moon|space|spacecraft|nasa|rocket|satellite|mars|orbit|astronaut)\b/.test(text)) return 'space';
  if (/\b(science|discovered|dna|genome|vaccine|physics|chemical|astronomy|medicine|computer|internet|radio|telegraph)\b/.test(text)) return 'science';
  if (/\b(civil rights|suffrage|women|vote|rights|slavery|emancipation|apartheid|equality|protest)\b/.test(text)) return 'rights';
  if (/\b(independence|constitution|treaty|declaration|parliament|congress|president|king|queen|united nations|law|court)\b/.test(text)) return 'civic';
  if (/\b(war|battle|invasion|siege|revolution|army|navy|empire|assassinated)\b/.test(text)) return 'conflict';
  if (/\b(film|music|novel|book|museum|art|artist|television|broadcast|olympic|games|theatre|opera)\b/.test(text)) return 'culture';
  if (/\b(railway|railroad|flight|aircraft|ship|canal|bridge|tunnel|voyage|expedition|circumnavigate|reaches)\b/.test(text)) return 'transport';
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
    chronicle: 'archive',
  }[visual] || 'archive';
}

function pickEvent(events) {
  const eligible = events
    .filter((event) => Number.isFinite(event.year))
    .filter((event) => event.pages?.[0])
    .map((event) => ({ event, score: scoreEvent(event) }))
    .sort((a, b) => b.score - a.score || Math.abs(a.event.year) - Math.abs(b.event.year));

  return eligible[0]?.event || events.find((event) => event.pages?.[0]) || events[0];
}

async function fetchDay(key, attempt = 1) {
  const [month, day] = key.split('-');
  const response = await fetch(`${endpointBase}/${month}/${day}`, {
    headers: { 'User-Agent': userAgent },
  });

  if (!response.ok) {
    if (attempt < 3) {
      await new Promise((resolve) => setTimeout(resolve, 500 * attempt));
      return fetchDay(key, attempt + 1);
    }
    throw new Error(`Wikimedia request failed for ${key}: ${response.status} ${response.statusText}`);
  }

  const payload = await response.json();
  const selected = Array.isArray(payload.selected) ? payload.selected : [];
  if (!selected.length) throw new Error(`No selected anniversaries returned for ${key}`);

  const event = pickEvent(selected);
  const page = event.pages?.[0] || {};
  const title = pageTitle(page);
  const monthIndex = Number(month) - 1;
  const visual = classifyVisual(event.text, title, page.description || '');

  return {
    date: key,
    displayDate: `${MONTHS[monthIndex]} ${Number(day)}`,
    year: event.year,
    title,
    text: stripDisplayNoise(event.text),
    source: pageUrl(page),
    sourceLabel: `Wikipedia: ${title}`,
    visual,
    palette: paletteFor(visual),
  };
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
const moments = await mapLimit(keys, 6, async (key, index) => {
  const moment = await fetchDay(key);
  process.stdout.write(`${index + 1}/${keys.length} ${key} ${moment.year} ${moment.title}\n`);
  return moment;
});

const byDate = Object.fromEntries(moments.map((moment) => [moment.date, moment]));

if (Object.keys(byDate).length !== 365) {
  throw new Error(`Expected 365 moments, got ${Object.keys(byDate).length}`);
}

const generatedAt = new Date().toISOString();
const file = `/*\n` +
  `  The Press daily history moments.\n` +
  `  Generated from Wikimedia's English Wikipedia On This Day selected-anniversary feed.\n` +
  `  Source endpoint pattern: ${endpointBase}/MM/DD\n` +
  `  Wikipedia content is available under CC BY-SA; each item keeps a source URL.\n` +
  `  Generated at: ${generatedAt}\n` +
  `*/\n` +
  `window.PRESS_ON_THIS_DAY_ATTRIBUTION = ${JSON.stringify({
    source: 'Wikimedia On This Day selected-anniversary feed',
    endpoint: `${endpointBase}/MM/DD`,
    license: 'CC BY-SA',
    generatedAt,
    count: 365,
  }, null, 2)};\n` +
  `window.PRESS_ON_THIS_DAY_MOMENTS = ${JSON.stringify(byDate, null, 2)};\n`;

await fs.mkdir(path.dirname(outputPath), { recursive: true });
await fs.writeFile(outputPath, file);
process.stdout.write(`Wrote ${outputPath}\n`);
