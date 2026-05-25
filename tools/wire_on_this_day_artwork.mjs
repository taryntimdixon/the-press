#!/usr/bin/env node

import fs from "node:fs";
import vm from "node:vm";

const [dateKey, src, alt, style = "photorealistic editorial historical scene"] = process.argv.slice(2);

if (!dateKey || !src || !alt) {
  console.error("Usage: node tools/wire_on_this_day_artwork.mjs MM-DD path alt [style]");
  process.exit(1);
}

const artworkFile = "assets/on-this-day-artwork.js";
const momentsFile = "assets/on-this-day-moments.js";

function loadWindowFile(file) {
  const ctx = { window: {} };
  vm.runInNewContext(fs.readFileSync(file, "utf8"), ctx);
  return ctx.window;
}

const artWindow = loadWindowFile(artworkFile);
const art = artWindow.PRESS_ON_THIS_DAY_ARTWORK || {};

art[dateKey] = {
  src,
  alt,
  style,
  status: "generated",
};

const sorted = Object.fromEntries(Object.entries(art).sort(([a], [b]) => a.localeCompare(b)));
fs.writeFileSync(
  artworkFile,
  `/*\n  Real artwork assets for The Press daily history moments.\n  Add generated editorial or photorealistic image files here as they are approved.\n*/\nwindow.PRESS_ON_THIS_DAY_ARTWORK = ${JSON.stringify(sorted, null, 2)};\n`,
);

const moments = loadWindowFile(momentsFile).PRESS_ON_THIS_DAY_MOMENTS;
const missing = Object.keys(moments).filter((key) => !sorted[key]);
const missingFiles = Object.values(sorted).filter((item) => !fs.existsSync(item.src));

console.log(
  JSON.stringify(
    {
      artwork: Object.keys(sorted).length,
      missing: missing.length,
      missingFiles: missingFiles.length,
      next: missing.slice(0, 5),
    },
    null,
    2,
  ),
);
