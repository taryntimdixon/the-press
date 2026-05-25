#!/usr/bin/env node

import fs from 'node:fs/promises';
import fsSync from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, '..');
const momentsPath = path.join(rootDir, 'assets', 'on-this-day-moments.js');
const artworkPath = path.join(rootDir, 'assets', 'on-this-day-artwork.js');
const reportingDir = path.join(rootDir, 'reporting');

const startDate = process.argv[2] || '2026-05-24';
const dayCount = Number.parseInt(process.argv[3] || '62', 10);

const REGION_RULES = [
  ['Global / Space', /\b(space|nasa|apollo|mercury|spacex|dragon|international space station|cassini|moon|saturn|astronaut|space shuttle)\b/i],
  ['East Asia', /\b(china|chinese|tiananmen|hong kong|yuen long|korea|north korea|japan)\b/i],
  ['South Asia', /\b(india|pakistan|bangladesh|sri lanka)\b/i],
  ['Southeast Asia', /\b(vietnam|vietnamese|thai|thailand|indonesia|philippines|malaysia|singapore)\b/i],
  ['Middle East / North Africa', /\b(iran|iranian|iraq|israel|yemen|yemenia|egypt|algeria|morocco|tunisia|syria|saudi)\b/i],
  ['Oceania / Indigenous Australia', /\b(australia|australian|new south wales|indigenous australians|myall creek)\b/i],
  ['Sub-Saharan Africa', /\b(comoros|ghana|kenya|nigeria|south africa|ethiopia|congo|sudan)\b/i],
  ['North America', /\b(united states|u\.s\.|american|america|canada|canadian|california|new york|detroit|hoboken|texas|white house|supreme court|apple|iphone|dene|inuit|nunavut)\b/i],
  ['Europe', /\b(england|english|britain|british|london|sweden|eurovision|france|french|germany|german|netherlands|spain|italy|bulgaria|albania|shkoder|ottoman|wimbledon|beatles|bowie)\b/i],
  ['Latin America / Caribbean', /\b(brazil|brazilian|rio de janeiro|mexico|argentina|chile|peru|colombia|cuba|haiti)\b/i],
];

const VISUAL_GUARDS = {
  space: 'Use real spacecraft, mission hardware, Earth or lunar context, and period-specific equipment; avoid repeating control-room foregrounds.',
  tech: 'Use the actual device, computer, screen environment, store line, lab, or launch context; avoid generic glowing monitors.',
  music: 'Anchor the scene in a real release, studio, venue, record shop, broadcast, or crowd moment; vary stage, street, and studio compositions.',
  sports: 'Show the specific match, arena, athlete pressure, crowd geography, or post-event aftermath; avoid generic victory podiums.',
  rights: 'Show the courthouse, law-signing room, street, or public institution tied to the right at stake; keep the people historically grounded.',
  protest: 'Show the specific square, street, station, factory gate, or public pressure point; vary crowd scale and camera distance.',
  crime: 'Show investigation, courtroom, documents, aftermath, or civic setting; do not sensationalize violence.',
  civic: 'Show formal power in a specific place: court, legislature, office, treaty table, or ceremonial room.',
  culture: 'Show publication, theater, museum, gallery, or media context tied to the event; avoid symbolic posters.',
  transport: 'Show the actual vehicle, route, airport, ocean, rescue, or infrastructure; avoid generic crash imagery.',
  chronicle: 'Show the specific recorded place, archive object, civic aftermath, or eyewitness context; avoid generic old-paper still lifes.',
  medicine: 'Show clinics, labs, regulators, treatment rooms, or public-health settings with accurate period details.',
  science: 'Show instruments, evidence, fieldwork, lab bench, or observation; make the discovery visually specific.',
};

const MASTER_VISUAL_STANDARD = [
  'Create a historically accurate but visually unforgettable photorealistic image for the daily "On This Day" feature.',
  'Pull from the real event and its immediate historical setting, across civilizations, eras, and regions of the world.',
  'Avoid repetitive imagery and overused compositions: no repeated table scenes, generic handshakes, or crowds staring at camera.',
  'Every image should differ from adjacent days in subject matter, scale, atmosphere, color palette, geography, decade, emotional tone, camera angle, and visual storytelling.',
  'Prioritize rich environments such as factories, oceans, laboratories, spacecraft, city streets, courts, stadiums, ships, studios, trading floors, temples, ruins, airports, and disaster zones when the event calls for them.',
  'The scene must feel alive, cinematic, immersive, emotionally charged, and grounded in historical authenticity.',
  'Use dynamic composition, layered depth, atmospheric lighting, realistic period clothing/materials/architecture, strong photographic framing, and event-specific props, machinery, vehicles, weather, debris, screens, documents, artifacts, or cultural cues.',
  'Vary photorealistic modes naturally: documentary photography, IMAX historical epic, war journalism, vintage film stock, NASA photography, 1970s newsroom, nightlife realism, aerial perspective, macro close-up, or ultra-wide cinematic scene as appropriate.',
  'The viewer should feel like they are witnessing history itself, not a generic AI recreation.',
].join(' ');

function loadWindowFile(file) {
  const context = { window: {} };
  vm.runInNewContext(fsSync.readFileSync(file, 'utf8'), context);
  return context.window;
}

function collapseWhitespace(value) {
  return String(value || '').replace(/\s+/g, ' ').trim();
}

function stripMarkdownCell(value) {
  return collapseWhitespace(value).replace(/\|/g, '\\|');
}

function words(value, count) {
  const all = collapseWhitespace(value).split(/\s+/).filter(Boolean);
  return all.length > count ? `${all.slice(0, count).join(' ').replace(/[,:;.]$/, '')}...` : all.join(' ');
}

function formatYear(year) {
  const value = Number(year);
  if (!Number.isFinite(value)) return '';
  return value < 0 ? `${Math.abs(value)} BCE` : String(value);
}

function monthDayKey(date) {
  return `${String(date.getUTCMonth() + 1).padStart(2, '0')}-${String(date.getUTCDate()).padStart(2, '0')}`;
}

function isoDate(date) {
  return `${date.getUTCFullYear()}-${String(date.getUTCMonth() + 1).padStart(2, '0')}-${String(date.getUTCDate()).padStart(2, '0')}`;
}

function addDays(date, offset) {
  const next = new Date(date.getTime());
  next.setUTCDate(next.getUTCDate() + offset);
  return next;
}

function inferRegion(moment, art = {}) {
  const haystack = collapseWhitespace([
    moment.title,
    moment.topic,
    moment.text,
    moment.dek,
    Array.isArray(moment.summary) ? moment.summary.join(' ') : '',
    moment.sourceDescription,
    art.alt,
    art.src,
  ].join(' '));
  const match = REGION_RULES.find(([, pattern]) => pattern.test(haystack));
  return match ? match[0] : 'Global / Mixed';
}

function synopsis(moment) {
  const summaryLead = Array.isArray(moment.summary) ? moment.summary[0] : '';
  return words(summaryLead || `${moment.text || ''} ${moment.dek || ''}`, 58);
}

function artPromptExcerpt(moment) {
  const prompt = collapseWhitespace(moment.artPrompt || '');
  if (!prompt) return '';
  return words(prompt.replace(/^Use case: historical-scene\s*/i, ''), 48);
}

function diversityNote(entry, previous) {
  const notes = [VISUAL_GUARDS[entry.visual] || VISUAL_GUARDS.chronicle];
  if (previous?.visual === entry.visual) {
    notes.push(`Previous day also uses ${entry.visual}; change camera distance, setting, and human/object focus.`);
  }
  if (previous?.region === entry.region) {
    notes.push(`Previous day is also ${entry.region}; avoid repeating architecture, crowd type, and color temperature.`);
  }
  return notes.join(' ');
}

function productionPrompt(moment, entry, previous) {
  return [
    `Use case: historical-scene`,
    `Asset type: daily website feature image for "On This Day in History"`,
    `Date/event: ${entry.displayDate}, ${entry.year}: ${entry.event}.`,
    `Core historical fact: ${collapseWhitespace(moment.text || moment.headline || '')}`,
    `Synopsis: ${entry.synopsis}`,
    `Visual standard: ${MASTER_VISUAL_STANDARD}`,
    `Event-specific direction: ${entry.imageBrief || artPromptExcerpt(moment)}`,
    `Diversity and anti-repetition direction: ${diversityNote(entry, previous)}`,
    `Composition: landscape 16:9, cinematic, immersive, layered depth, strong subject, no generic symbolic poster.`,
    `Constraints: no text, no labels, no logo, no watermark, no UI, no fake headlines, no modern anachronisms, no fantasy elements.`,
  ].join('\n');
}

function sortedCounts(entries, key) {
  const counts = new Map();
  entries.forEach((entry) => counts.set(entry[key], (counts.get(entry[key]) || 0) + 1));
  return Object.fromEntries([...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])));
}

const [year, month, day] = startDate.split('-').map(Number);
if (!Number.isFinite(year) || !Number.isFinite(month) || !Number.isFinite(day) || !Number.isFinite(dayCount) || dayCount <= 0) {
  console.error('Usage: node tools/export_on_this_day_synopsis.mjs YYYY-MM-DD [days]');
  process.exit(1);
}

const moments = loadWindowFile(momentsPath).PRESS_ON_THIS_DAY_MOMENTS || {};
const artwork = loadWindowFile(artworkPath).PRESS_ON_THIS_DAY_ARTWORK || {};
const start = new Date(Date.UTC(year, month - 1, day));
const entries = [];

for (let index = 0; index < dayCount; index += 1) {
  const date = addDays(start, index);
  const dateKey = monthDayKey(date);
  const moment = moments[dateKey] || {};
  const art = artwork[dateKey] || {};
  const previous = entries.at(-1);
  const entry = {
    isoDate: isoDate(date),
    dateKey,
    displayDate: moment.displayDate || dateKey,
    year: formatYear(moment.year),
    event: moment.title || moment.topic || 'Unassigned',
    visual: moment.visual || 'chronicle',
    region: inferRegion(moment, art),
    synopsis: synopsis(moment),
    image: art.src || '',
    imageAlt: art.alt || '',
    imageStatus: art.src && fsSync.existsSync(path.join(rootDir, art.src)) ? 'ready' : 'missing',
    imageBrief: art.alt || artPromptExcerpt(moment),
    source: moment.source || '',
    sourceLabel: moment.sourceLabel || '',
  };
  entry.diversityNote = diversityNote(entry, previous);
  entry.productionPrompt = productionPrompt(moment, entry, previous);
  entries.push(entry);
}

const coverage = {
  generatedAt: new Date().toISOString(),
  startDate,
  days: entries.length,
  endDate: entries.at(-1)?.isoDate || startDate,
  readyImages: entries.filter((entry) => entry.imageStatus === 'ready').length,
  missingImages: entries.filter((entry) => entry.imageStatus !== 'ready').map((entry) => entry.dateKey),
  regions: sortedCounts(entries, 'region'),
  visualLanes: sortedCounts(entries, 'visual'),
  standard: 'Choose the biggest durable event available for the date, with global diversity across region, discipline, era, gender, race, class, and institution. Images should depict the real event or its immediate historical setting, not generic symbolism.',
  visualStandard: MASTER_VISUAL_STANDARD,
};

await fs.mkdir(reportingDir, { recursive: true });
const jsonPath = path.join(reportingDir, 'on-this-day-next-two-months-synopsis.json');
const mdPath = path.join(reportingDir, 'on-this-day-next-two-months-synopsis.md');

await fs.writeFile(jsonPath, `${JSON.stringify({ coverage, entries }, null, 2)}\n`, 'utf8');

const md = [
  '# On This Day: Next Two Months',
  '',
  `Range: ${coverage.startDate} through ${coverage.endDate}`,
  '',
  `Coverage: ${coverage.readyImages}/${coverage.days} images ready. Missing image dates: ${coverage.missingImages.length ? coverage.missingImages.join(', ') : 'none'}.`,
  '',
  `Diversity standard: ${coverage.standard}`,
  '',
  `Visual standard: ${coverage.visualStandard}`,
  '',
  `Regions: ${Object.entries(coverage.regions).map(([label, count]) => `${label} (${count})`).join(', ')}.`,
  '',
  `Visual lanes: ${Object.entries(coverage.visualLanes).map(([label, count]) => `${label} (${count})`).join(', ')}.`,
  '',
  '| Date | Year | Event | Region | Visual | Image | Synopsis | Image direction |',
  '| --- | --- | --- | --- | --- | --- | --- | --- |',
  ...entries.map((entry) => [
    entry.displayDate,
    entry.year,
    entry.event,
    entry.region,
    entry.visual,
    entry.imageStatus === 'ready' ? entry.image : 'MISSING',
    entry.synopsis,
    `${entry.imageBrief} ${entry.diversityNote}`,
  ].map(stripMarkdownCell).join(' | ')).map((row) => `| ${row} |`),
  '',
].join('\n');

await fs.writeFile(mdPath, md, 'utf8');
console.log(JSON.stringify({
  json: path.relative(rootDir, jsonPath),
  markdown: path.relative(rootDir, mdPath),
  readyImages: coverage.readyImages,
  days: coverage.days,
  missingImages: coverage.missingImages,
}, null, 2));
