import fs from 'node:fs/promises';
import vm from 'node:vm';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, '..');
const momentsPath = path.join(rootDir, 'assets', 'on-this-day-moments.js');

const VISUAL_COPY = {
  space: {
    lane: 'space age',
    scene: 'a hard-lit machine sitting in a place humans were never built to stand',
    texture: 'black sky, bright metal, radio voices, checklists, dust, and the feeling that every bolt mattered',
    stakes: 'a mission where tiny technical details could turn into legend or disaster',
  },
  tech: {
    lane: 'future shock',
    scene: 'a launch stage, computer room, store line, server rack, or demo table where a new tool suddenly feels real',
    texture: 'glowing screens, coiled cables, demo units, press badges, nervous engineers, glass doors, and people realizing the gadget is not just a gadget',
    stakes: 'a technology moment where the object in the room started changing everyday behavior',
  },
  music: {
    lane: 'sound check',
    scene: 'a studio, club, arena, radio booth, record shop, or broadcast room where a sound hits the public all at once',
    texture: 'vinyl sleeves, sweaty stage lights, mic stands, tape reels, crowd noise, headphones, and the tiny pause before the first beat lands',
    stakes: 'a culture moment where a song, concert, album, or broadcast made the room feel bigger than itself',
  },
  sports: {
    lane: 'game day',
    scene: 'a field, court, ring, track, stadium tunnel, broadcast booth, or locker room right before the scoreboard becomes history',
    texture: 'grass stains, floodlights, chalk lines, roaring stands, sweat, flashbulbs, and that strange silence before a record breaks',
    stakes: 'a sports moment where pressure, skill, crowd energy, and myth all showed up at once',
  },
  crime: {
    lane: 'manhunt file',
    scene: 'a courtroom, police command room, evidence table, street corner, prison gate, or news scrum where a case turns',
    texture: 'case files, wire photos, radios, handcuffs, surveillance stills, courtroom wood, and reporters shouting over each other',
    stakes: 'a crime or justice moment where power, evidence, fear, and spectacle collided',
  },
  medicine: {
    lane: 'clinic shift',
    scene: 'a laboratory, clinic, pharmacy counter, hospital corridor, public hearing room, or regulator office where health history changes shape',
    texture: 'white coats, glass bottles, case files, waiting rooms, trial charts, pharmacy shelves, and the nervous quiet before a treatment becomes public',
    stakes: 'a medicine or public-health moment where science, bodies, law, and everyday life collided',
  },
  protest: {
    lane: 'street heat',
    scene: 'a march, square, campus, courthouse, factory gate, or night street where ordinary people make the day impossible to ignore',
    texture: 'placards, chants, megaphones, handmade banners, police lines, newspaper ink, and shoes wearing down pavement',
    stakes: 'a public pressure moment where a crowd forced power to look back',
  },
  science: {
    lane: 'lab bench',
    scene: 'a room full of instruments, notes, prototypes, measurements, and people trying to prove something real',
    texture: 'glassware, chalk marks, cables, notebooks, strange machines, and the pressure of getting the evidence right',
    stakes: 'a discovery moment where one observation could change the whole argument in the room',
  },
  rights: {
    lane: 'public square',
    scene: 'crowded streets, courtrooms, meeting halls, printed notices, raised voices, and people refusing to stay invisible',
    texture: 'placards, formal clothes, police lines, paper petitions, newspaper ink, and the sound of a room turning tense',
    stakes: 'a fight over who counted, who had power, and who was finally being heard',
  },
  civic: {
    lane: 'seat of power',
    scene: 'a chamber, palace, office, treaty table, or government hall where a formal act suddenly became history',
    texture: 'wax seals, flags, stone steps, wood desks, official signatures, and news traveling faster than certainty',
    stakes: 'a political moment where ceremony and raw power were sitting at the same table',
  },
  conflict: {
    lane: 'front line',
    scene: 'a map room, road, encampment, harbor, ruined street, or battlefield where decisions carried real danger',
    texture: 'mud, smoke, uniforms, coded messages, ration tins, cold dawn light, and orders nobody could take back',
    stakes: 'a crisis where fear, command, confusion, and survival were all moving at once',
  },
  culture: {
    lane: 'stage lights',
    scene: 'a theater, studio, print shop, gallery, broadcast room, or public crowd watching culture take shape',
    texture: 'velvet seats, hot lamps, reels, sheet music, handbills, applause, reviews, and the electric feeling of a debut',
    stakes: 'a cultural flashpoint where a new sound, image, story, or performance entered public life',
  },
  transport: {
    lane: 'crossing',
    scene: 'a route, vehicle, station, port, runway, bridge, or open horizon where distance suddenly felt different',
    texture: 'engines, maps, fuel, weather, rivets, timetables, luggage, sea spray, and the nervous quiet before departure',
    stakes: 'a journey where machinery, nerve, and geography all had to cooperate',
  },
  chronicle: {
    lane: 'archive room',
    scene: 'a vivid historical scene caught in records, letters, newsprint, official notes, and eyewitness memory',
    texture: 'paper files, ink, dust, lamps, street noise, handwritten names, and the tiny details that make a date feel alive',
    stakes: 'a moment that still feels worth opening because the details are stranger than a simple calendar line',
  },
};

function collapseWhitespace(value) {
  return String(value || '').replace(/\s+/g, ' ').trim();
}

function ensureSentence(value) {
  const text = collapseWhitespace(value).replace(/\.\.\./g, '.');
  if (!text) return '';
  return /[.!?]$/.test(text) ? text : `${text}.`;
}

function trimWords(value, maxWords) {
  const text = collapseWhitespace(value);
  const words = text.split(/\s+/).filter(Boolean);
  if (words.length <= maxWords) return words.join(' ');
  return firstCompleteSentence(text);
}

function firstCompleteSentence(value) {
  const text = collapseWhitespace(value).replace(/\.\.\./g, '.');
  if (!text) return '';
  const sentence = text.match(/^.{12,420}?[.!?](?:\s|$)/);
  return ensureSentence(sentence ? sentence[0] : text);
}

function wordCount(value) {
  return collapseWhitespace(value).split(/\s+/).filter(Boolean).length;
}

function formatYear(year) {
  const value = Number(year);
  if (!Number.isFinite(value)) return 'unknown year';
  return value < 0 ? `${Math.abs(value)} BCE` : String(value);
}

function listJoin(items) {
  const values = items.filter(Boolean);
  if (values.length <= 1) return values.join('');
  if (values.length === 2) return `${values[0]} and ${values[1]}`;
  return `${values.slice(0, -1).join(', ')}, and ${values.at(-1)}`;
}

function visualCopy(moment) {
  return VISUAL_COPY[moment.visual] || VISUAL_COPY.chronicle;
}

function relatedTitles(moment, limit = 4) {
  return (Array.isArray(moment.related) ? moment.related : [])
    .map((item) => collapseWhitespace(item.title || ''))
    .filter(Boolean)
    .filter((title) => title !== moment.title && title !== moment.topic)
    .slice(0, limit);
}

function relatedDescriptions(moment, limit = 3) {
  return (Array.isArray(moment.related) ? moment.related : [])
    .map((item) => {
      const title = collapseWhitespace(item.title || '');
      const description = collapseWhitespace(item.description || '');
      if (!title || !description) return '';
      return `${title}: ${description}`;
    })
    .filter(Boolean)
    .slice(0, limit);
}

function buildDek(moment) {
  return `Step into ${formatYear(moment.year)}: ${trimWords(moment.headline || moment.text, 24)}`;
}

function buildCoolFacts(moment) {
  const copy = visualCopy(moment);
  const related = relatedTitles(moment, 3);
  const descriptions = relatedDescriptions(moment, 2);
  const facts = [
    `${moment.displayDate} drops you into ${formatYear(moment.year)}, right in the middle of a ${copy.lane} story.`,
    `The main scene: ${ensureSentence(moment.text)}`,
  ];

  if (moment.sourceDescription) {
    facts.push(`Archive tag: ${moment.sourceDescription}.`);
  }

  if (related.length) {
    facts.push(`Names in the margins: ${listJoin(related)}.`);
  }

  descriptions.forEach((description) => {
    facts.push(description.endsWith('.') ? description : `${description}.`);
  });

  facts.push(`What to picture: ${copy.texture}.`);
  return facts.map(ensureSentence).slice(0, 7);
}

function buildFacts(moment) {
  const copy = visualCopy(moment);
  const related = relatedTitles(moment, 3);
  return [
    { label: 'Date', value: moment.displayDate },
    { label: 'Year', value: formatYear(moment.year) },
    { label: 'Time capsule', value: copy.lane },
    { label: 'Main scene', value: trimWords(moment.headline || moment.text, 12) },
    { label: 'In the frame', value: related.length ? listJoin(related) : (moment.sourceDescription || moment.title) },
  ];
}

function buildSummary(moment) {
  const copy = visualCopy(moment);
  const year = formatYear(moment.year);
  const topic = moment.topic || moment.title || 'this moment';
  const related = relatedTitles(moment, 5);
  const descriptions = relatedDescriptions(moment, 4);
  const coolFacts = buildCoolFacts(moment);

  const paragraphs = [
    `Set the dial to ${moment.displayDate}, ${year}. ${ensureSentence(moment.text)} This entry is meant to feel like opening a heavy old archive drawer and finding the day still warm inside: the people, the machines, the weather, the panic, the paperwork, and the strange little details that make the past feel less polished than a textbook paragraph.`,

    `The scene to picture is ${copy.scene}. The texture is all in the small stuff: ${copy.texture}. That is the fun of this kind of history. You do not have to turn it into a sermon. The day already has drama because somebody was making a decision, taking a risk, signing a document, crossing a distance, performing for a crowd, watching an experiment, or trying to survive a situation that had not finished becoming history yet.`,

    `The main hook is ${topic}. In the record, it sits beside ${related.length ? listJoin(related) : 'the people and places around the event'}. ${descriptions.length ? descriptions.map(ensureSentence).join(' ') : `The connected names are part of what gives the event its shape; they turn one date into a room full of objects, voices, routes, uniforms, tools, and witnesses.`} These are the pieces that make the entry worth looking at closely instead of treating it as a one-line calendar fact.`,

    `A few details make the day pop. ${coolFacts.slice(0, 4).join(' ')} ${copy.stakes.charAt(0).toUpperCase() + copy.stakes.slice(1)}. That is the mood this section should carry: not a lecture, not a moral, just the feeling of standing near the moment while it is happening and noticing what everyone else in the frame might have missed.`,

    `For the image, the goal is a real scene, not symbolic geometry: period clothes, believable materials, actual atmosphere, and a strong editorial composition. The art should make ${moment.displayDate} feel cinematic and specific, like a still from a lost feature story. If it is photorealistic, it should look grounded and textured. If it is illustrated, it should feel commissioned and intentional, with the event itself doing the work.`,
  ].map(collapseWhitespace);

  return paragraphs;
}

function buildArtPrompt(moment) {
  const copy = visualCopy(moment);
  return [
    'Use case: historical-scene',
    'Asset type: website editorial image for an "On this day in history" card',
    `Primary request: Create a high-end ${moment.visual === 'culture' || moment.visual === 'rights' ? 'flat editorial illustration or photorealistic editorial scene' : 'photorealistic or premium editorial illustration'} for ${moment.displayDate}, ${formatYear(moment.year)}: ${ensureSentence(moment.text)}`,
    `Scene/backdrop: ${copy.scene}.`,
    `Subject: ${moment.topic || moment.title}, with surrounding details connected to ${relatedTitles(moment, 3).join(', ') || 'the historical record'}.`,
    `Style/medium: Museum-grade photorealistic historical scene, award-winning documentary still or major magazine cover, immersive, researched, cinematic, visually unforgettable, not decorative filler.`,
    `Composition/framing: Landscape 16:9 website feature image, dynamic camera angle, layered depth, strong subject, event-specific environment, motion or consequences visible in the frame.`,
    `Lighting/mood: ${copy.texture}.`,
    'Diversity/variety: Avoid repetitive table scenes, generic handshakes, static portrait shots, and crowds staring at camera. Vary geography, decade, emotional tone, environment, color palette, camera distance, and visual storytelling from adjacent days.',
    'Constraints: no text, no labels, no logo, no watermark, no UI, no cartoon mascot, no simple geometric poster art, no infographic, no generic clipart, no modern anachronisms.',
  ].join('\n');
}

const code = await fs.readFile(momentsPath, 'utf8');
const context = { window: {} };
vm.runInNewContext(code, context);

const moments = context.window.PRESS_ON_THIS_DAY_MOMENTS || {};
const attribution = context.window.PRESS_ON_THIS_DAY_ATTRIBUTION || {};

for (const moment of Object.values(moments)) {
  moment.dek = buildDek(moment);
  moment.facts = buildFacts(moment);
  moment.coolFacts = buildCoolFacts(moment);
  moment.summary = buildSummary(moment);
  moment.artPrompt = buildArtPrompt(moment);
  moment.wordCount = wordCount(moment.summary.join(' '));
  delete moment.impact;
}

const generatedAt = new Date().toISOString();
const updatedAttribution = {
  ...attribution,
  generatedAt,
  copyStyle: 'Time-capsule history briefs focused on the scene, facts, people, objects, and atmosphere of the day.',
  visualPolicy: 'Use real generated photorealistic or premium editorial illustration assets. Do not use geometric SVG placeholders as finished artwork.',
  count: Object.keys(moments).length,
};
delete updatedAttribution.minBriefWords;

const file = `/*\n` +
  `  The Press daily history moments.\n` +
  `  Generated from Wikimedia's English Wikipedia On This Day selected-anniversary feed.\n` +
  `  Rewritten as time-capsule briefs: vivid facts, scene-setting, and image direction.\n` +
  `  Source endpoint pattern: ${updatedAttribution.endpoint || 'https://en.wikipedia.org/api/rest_v1/feed/onthisday/selected/MM/DD'}\n` +
  `  Wikipedia text is available under CC BY-SA; generated visual assets are tracked separately.\n` +
  `  Generated at: ${generatedAt}\n` +
  `*/\n` +
  `window.PRESS_ON_THIS_DAY_ATTRIBUTION = ${JSON.stringify(updatedAttribution, null, 2)};\n` +
  `window.PRESS_ON_THIS_DAY_MOMENTS = ${JSON.stringify(moments, null, 2)};\n`;

await fs.writeFile(momentsPath, file);
process.stdout.write(`Rewrote ${Object.keys(moments).length} on-this-day moments as time capsules.\n`);
