#!/usr/bin/env python3
"""
Hard visible-site fix for The Press.

Run from the repository root:
    python3 apply_visible_hardfix_no_flash.py

What this fixes immediately on the served site:
- Stops the 170ms animated internal-navigation delay that causes the refresh/click flash.
- Adds no-flash CSS overrides to HTML pages and styles.css.
- Adds an inline homepage lead that reads daily-latest.json, chooses a different AI-thumbnail story on refresh,
  and hides the stale April 7 lead cards.
- Adds image hydration for daily cards that have blank/empty image anchors.
- Restores valid GitHub Actions YAML for the newsroom and thumbnail backfill workflows.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path.cwd()
VERSION = "press-hardfix-20260425-2"
BACKUP_DIR = ROOT / f".bak-visible-hardfix-{VERSION}"

CSS_BLOCK = r'''
/* PRESS_HARD_VISIBLE_FIX_CSS_START */
html.press-page-leaving,
html.press-dynamic-page,
html.press-page-ready,
html.press-ecosystem-booting,
html.press-ecosystem-booting body {
  opacity: 1 !important;
  filter: none !important;
  transform: none !important;
}

html,
body {
  scroll-behavior: auto !important;
}

body,
main,
.site-shell,
.site-header,
.page,
.story-card,
.archive-card,
.river-item,
.lead-panel,
.desk-card,
.rail,
.newsletter-block,
.trust-card,
.article-body,
.article-sources,
.daily-home-section,
.daily-archive-section,
.breaking-wire-section,
[data-press-reveal],
[data-press-reveal].is-revealed {
  opacity: 1 !important;
  visibility: visible !important;
  transform: none !important;
  filter: none !important;
  animation: none !important;
  transition: none !important;
}

.press-ink-ripple,
.press-back-to-top {
  display: none !important;
}

#press-live-rotating-lead {
  margin: clamp(1rem, 3vw, 2rem) 0 clamp(1.25rem, 3vw, 2.25rem);
  border: 1px solid color-mix(in srgb, currentColor 16%, transparent);
  border-radius: 22px;
  overflow: hidden;
  background: var(--surface, #ffffff);
  box-shadow: 0 18px 50px rgba(0, 0, 0, 0.10);
}

#press-live-rotating-lead .press-live-lead__link {
  display: grid;
  grid-template-columns: minmax(280px, 1.12fr) minmax(260px, 0.88fr);
  color: inherit;
  text-decoration: none;
}

#press-live-rotating-lead .press-live-lead__media {
  margin: 0;
  min-height: 320px;
  background: color-mix(in srgb, currentColor 9%, transparent);
}

#press-live-rotating-lead img {
  display: block;
  width: 100%;
  height: 100%;
  min-height: 320px;
  max-height: 540px;
  object-fit: cover;
}

#press-live-rotating-lead .press-live-lead__text {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 0.78rem;
  padding: clamp(1.1rem, 3vw, 2.35rem);
}

#press-live-rotating-lead .press-live-lead__kicker {
  margin: 0;
  font-size: 0.78rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--muted, #666);
}

#press-live-rotating-lead .press-live-lead__title {
  margin: 0;
  font-family: var(--serif, Georgia, serif);
  font-size: clamp(2rem, 4.2vw, 4.15rem);
  line-height: 0.96;
  letter-spacing: -0.045em;
}

#press-live-rotating-lead .press-live-lead__summary {
  margin: 0;
  max-width: 62ch;
  font-size: clamp(1rem, 1.4vw, 1.18rem);
  line-height: 1.58;
  color: var(--muted, #555);
}

#press-live-rotating-lead .press-live-lead__meta,
#press-live-rotating-lead .press-live-lead__credit {
  margin: 0;
  font-size: 0.9rem;
  color: var(--muted, #666);
}

#press-live-rotating-lead .press-live-lead__cta {
  margin-top: 0.4rem;
  font-weight: 700;
}

.press-hard-hidden-legacy-lead {
  display: none !important;
}

.press-hard-card-image {
  display: block;
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  border-radius: 16px;
  margin: 0 0 0.85rem;
}

@media (max-width: 760px) {
  #press-live-rotating-lead .press-live-lead__link {
    grid-template-columns: 1fr;
  }
  #press-live-rotating-lead .press-live-lead__media,
  #press-live-rotating-lead img {
    min-height: 230px;
    max-height: 360px;
  }
}
/* PRESS_HARD_VISIBLE_FIX_CSS_END */
'''.strip()

JS_BLOCK = r'''
<script id="press-hard-visible-fix-script">
/* PRESS_HARD_VISIBLE_FIX_JS_START */
(() => {
  const VERSION = 'press-hardfix-20260425-2';
  const CARD_SELECTOR = [
    '.story-card', '.archive-card', '.river-item', '.lead-panel', '.desk-card',
    '.link-list__item', '.related-card', '.daily-card', '.latest-card',
    '#press-live-rotating-lead'
  ].join(', ');
  const LEGACY_HOME_TITLES = [
    'Proof of Citizenship Is Not Just a Voting Rule',
    'Artemis II Proved the Moon',
    'Europe’s Defense Turn Is Now',
    "Europe's Defense Turn Is Now",
    'A Country That Cannot Measure Itself Cannot Govern Itself'
  ];

  const clean = (value) => String(value || '').replace(/\s+/g, ' ').trim();
  const isHome = () => {
    const path = window.location.pathname.replace(/\/+$/, '/');
    return path === '/' || /\/index\.html$/i.test(window.location.pathname);
  };

  function killPageLeavingClass() {
    document.documentElement.classList.remove('press-page-leaving', 'press-ecosystem-booting');
  }

  function installNoFlashNavigationGuard() {
    killPageLeavingClass();
    try {
      new MutationObserver(killPageLeavingClass).observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['class']
      });
    } catch (_) {}

    document.addEventListener('click', (event) => {
      if (event.defaultPrevented) return;
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      const target = event.target instanceof Element ? event.target : null;
      if (!target) return;
      if (target.closest('button, input, textarea, select, label, [contenteditable="true"]')) return;

      const directLink = target.closest('a[href]');
      const card = directLink ? null : target.closest(CARD_SELECTOR);
      const link = directLink || (card && card.querySelector('a[href]'));
      if (!link) return;

      const rawHref = link.getAttribute('href') || '';
      if (!rawHref || rawHref.startsWith('#') || /^(mailto|tel|javascript):/i.test(rawHref)) return;
      if (link.target && link.target !== '_self') return;

      let url;
      try { url = new URL(rawHref, window.location.href); } catch (_) { return; }
      if (url.origin !== window.location.origin) return;
      if (url.pathname === window.location.pathname && url.search === window.location.search && url.hash) return;

      killPageLeavingClass();
      event.stopImmediatePropagation();

      if (!directLink) {
        event.preventDefault();
        window.location.assign(url.href);
      }
      // For real <a> clicks, do not preventDefault. The browser navigates immediately, no 170ms flash delay.
    }, true);
  }

  function normalizeStory(item) {
    if (!item || typeof item !== 'object') return null;
    const title = clean(item.title || item.headline);
    const url = clean(item.url || item.href || item.link);
    if (!title || !url) return null;
    return {
      title,
      url,
      section: clean(item.section || item.category || 'News'),
      summary: clean(item.summary || item.dek || item.description),
      image: clean(item.image || item.thumbnail || item.photo || item.imageUrl),
      imageAlt: clean(item.imageAlt || item.thumbnail_alt || item.alt || title),
      credit: clean(item.image_credit || item.imageCreditPlain || item.credit || 'AI-generated image by The Press.'),
      published: clean(item.published || item.date || '')
    };
  }

  async function loadDailyStories() {
    const response = await fetch(`daily-latest.json?${VERSION}=${Date.now()}`, { cache: 'no-store' });
    if (!response.ok) throw new Error('daily-latest.json did not load');
    const payload = await response.json();
    const raw = Array.isArray(payload) ? payload : (payload.articles || payload.stories || payload.items || []);
    return raw.map(normalizeStory).filter(Boolean);
  }

  function pickDifferentStory(stories) {
    const withImages = stories.filter((story) => story.image);
    const aiFirst = withImages.filter((story) => /assets\/ai-thumbnails\//i.test(story.image));
    const pool = aiFirst.length ? aiFirst : (withImages.length ? withImages : stories);
    if (!pool.length) return null;

    let previous = -1;
    try { previous = Number(sessionStorage.getItem('press:last-random-lead-index') || '-1'); } catch (_) {}
    let index = Math.floor(Math.random() * pool.length);
    if (pool.length > 1 && index === previous) {
      index = (index + 1 + Math.floor(Math.random() * (pool.length - 1))) % pool.length;
    }
    try { sessionStorage.setItem('press:last-random-lead-index', String(index)); } catch (_) {}
    return pool[index];
  }

  function findHomepageInsertionPoint() {
    const main = document.querySelector('main') || document.querySelector('[role="main"]') || document.body;
    const h1 = Array.from(main.querySelectorAll('h1')).find((node) => /today.?s edition/i.test(clean(node.textContent))) || main.querySelector('h1');
    if (!h1) return { parent: main, before: main.firstChild };
    let anchor = h1;
    const next = h1.nextElementSibling;
    if (next && /^(p|div)$/i.test(next.tagName) && clean(next.textContent).length < 260) anchor = next;
    return { parent: anchor.parentNode || main, before: anchor.nextSibling };
  }

  function renderRotatingLead(story) {
    if (!story) return;
    let section = document.getElementById('press-live-rotating-lead');
    if (!section) {
      section = document.createElement('section');
      section.id = 'press-live-rotating-lead';
      section.setAttribute('aria-label', 'Rotating current-issue lead story');
      const spot = findHomepageInsertionPoint();
      spot.parent.insertBefore(section, spot.before);
    }

    const imageHtml = story.image
      ? `<figure class="press-live-lead__media"><img src="${escapeAttr(story.image)}" alt="${escapeAttr(story.imageAlt || story.title)}" loading="eager" decoding="async"></figure>`
      : `<figure class="press-live-lead__media" aria-hidden="true"></figure>`;

    section.innerHTML = `
      <a class="press-live-lead__link" href="${escapeAttr(story.url)}">
        ${imageHtml}
        <div class="press-live-lead__text">
          <p class="press-live-lead__kicker">Current issue • ${escapeHtml(story.section || 'News')}</p>
          <h2 class="press-live-lead__title">${escapeHtml(story.title)}</h2>
          ${story.summary ? `<p class="press-live-lead__summary">${escapeHtml(story.summary)}</p>` : ''}
          ${story.published ? `<p class="press-live-lead__meta">Written by Intelligent AI • ${escapeHtml(story.published)}</p>` : `<p class="press-live-lead__meta">Written by Intelligent AI</p>`}
          ${story.credit ? `<p class="press-live-lead__credit">${escapeHtml(story.credit)}</p>` : ''}
          <span class="press-live-lead__cta">Read story →</span>
        </div>
      </a>`;
  }

  function hideLegacyHomepageLead() {
    if (!isHome()) return;
    const nodes = Array.from(document.querySelectorAll('a, h1, h2, h3'));
    for (const title of LEGACY_HOME_TITLES) {
      const hit = nodes.find((node) => clean(node.textContent).includes(title));
      if (!hit) continue;
      const card = hit.closest('article, .lead-panel, .story-card, .river-item, .feature-card, .front-card, .card, section, div');
      if (card && card.id !== 'press-live-rotating-lead' && !card.closest('#press-live-rotating-lead')) {
        card.classList.add('press-hard-hidden-legacy-lead');
      }
    }
  }

  function hydrateBlankDailyCardImages(stories) {
    const byUrl = new Map();
    stories.forEach((story) => {
      if (story.url && story.image) byUrl.set(normalizeUrl(story.url), story);
    });
    document.querySelectorAll('a[href]').forEach((anchor) => {
      const story = byUrl.get(normalizeUrl(anchor.getAttribute('href') || ''));
      if (!story) return;
      const card = anchor.closest('article, li, .story-card, .archive-card, .river-item, .daily-card, .latest-card, section, div');
      if (!card || card.closest('#press-live-rotating-lead')) return;
      if (card.querySelector('img')) return;
      const img = document.createElement('img');
      img.className = 'press-hard-card-image';
      img.src = story.image;
      img.alt = story.imageAlt || story.title;
      img.loading = 'lazy';
      img.decoding = 'async';
      card.insertBefore(img, card.firstChild);
    });
  }

  function normalizeUrl(url) {
    try {
      const parsed = new URL(url, window.location.href);
      return parsed.pathname.replace(/^\/+/, '').replace(/[?#].*$/, '').toLowerCase();
    } catch (_) {
      return String(url || '').replace(/^\/+/, '').replace(/[?#].*$/, '').toLowerCase();
    }
  }

  function escapeHtml(value) {
    return String(value || '').replace(/[&<>"']/g, (ch) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));
  }
  function escapeAttr(value) { return escapeHtml(value); }

  async function hydrateHomepage() {
    if (!isHome()) return;
    try {
      const stories = await loadDailyStories();
      renderRotatingLead(pickDifferentStory(stories));
      hydrateBlankDailyCardImages(stories);
      hideLegacyHomepageLead();
    } catch (error) {
      console.warn('[The Press] visible homepage hardfix could not hydrate:', error);
      hideLegacyHomepageLead();
    }
  }

  function boot() {
    installNoFlashNavigationGuard();
    hydrateHomepage();
    window.setTimeout(hydrateHomepage, 150);
    window.setTimeout(hydrateHomepage, 600);
    window.setTimeout(hydrateHomepage, 1600);
    window.addEventListener('pageshow', () => {
      killPageLeavingClass();
      hydrateHomepage();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot, { once: true });
  } else {
    boot();
  }
})();
/* PRESS_HARD_VISIBLE_FIX_JS_END */
</script>
'''.strip()

APP_JS_BLOCK = r'''
/* PRESS_HARD_VISIBLE_FIX_APP_GUARD_START */
(() => {
  const kill = () => document.documentElement.classList.remove('press-page-leaving', 'press-ecosystem-booting');
  kill();
  try { new MutationObserver(kill).observe(document.documentElement, { attributes: true, attributeFilter: ['class'] }); } catch (_) {}
})();
/* PRESS_HARD_VISIBLE_FIX_APP_GUARD_END */
'''.strip()

AI_THUMBNAIL_WORKFLOW = r'''name: Backfill Current Issue GPT Image 2 Thumbnails

on:
  workflow_dispatch:
    inputs:
      image_cap:
        description: "Max NEW AI thumbnails this run. 0 = no cap."
        required: true
        default: "0"
      article_cap:
        description: "Max newest/current-issue articles to receive AI thumbnails. 0 = no cap."
        required: true
        default: "0"

jobs:
  ai-thumbnail-backfill:
    runs-on: ubuntu-latest
    timeout-minutes: 180
    permissions:
      contents: write
      pull-requests: write
    steps:
      - name: Check out repo
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install openai beautifulsoup4

      - name: Run GPT Image 2 thumbnail pass for current issue only
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          AI_THUMBNAIL_BACKFILL: "1"
          OPENAI_IMAGE_MODEL: gpt-image-2
          OPENAI_IMAGE_SIZE: 1536x864
          OPENAI_IMAGE_QUALITY: high
          OPENAI_IMAGE_FORMAT: jpeg
          OPENAI_IMAGE_COMPRESSION: "85"
          AI_ART_SCOPE: current_issue
          AI_ART_MAX_ARTICLES: ${{ github.event.inputs.article_cap || '0' }}
          AI_TOTAL_IMAGE_MAX_GENERATIONS: ${{ github.event.inputs.image_cap || '0' }}
          AI_THUMBNAIL_MAX_GENERATIONS: ${{ github.event.inputs.image_cap || '0' }}
          REPLACE_SVG_ARTICLE_THUMBNAILS: "1"
          FORCE_AI_FOR_ALL_ARTICLE_THUMBNAILS: "1"
          FORCE_AI_FOR_DAILY_STORIES: "1"
          STRICT_EDITORIAL_GATES: "0"
          AI_ART_PACKAGE_BACKFILL: "0"
          AI_GALLERY_IMAGES_PER_ARTICLE: "0"
          AI_UPDATE_LINKED_CARDS: "1"
          AI_CARD_UPDATE_SCOPE: front_pages
          AI_ART_PROMPT_MODEL: gpt-5.5
          AI_REGENERATE_AI_THUMBNAILS: "0"
        run: |
          python studio/automation/ai_thumbnail_backfill.py

      - name: Create review PR
        uses: peter-evans/create-pull-request@v6
        with:
          branch: ai-current-issue-thumbnails-${{ github.run_number }}
          delete-branch: true
          title: "Add GPT Image 2 thumbnails to current issue"
          body: |
            This PR targets only the newest/current issue articles from daily-latest.json.

            It should:
            - add one GPT Image 2 thumbnail per selected article
            - reuse existing GPT Image thumbnails on reruns
            - update matching front-page, section, archive, and JSON image references
            - avoid article galleries/photos
            - avoid full-site historical backfill

            Review the generated thumbnails before merging.
          commit-message: "Add current issue GPT Image 2 thumbnails"
'''

DAILY_WORKFLOW = r'''name: Daily AI Newsroom

on:
  workflow_dispatch:
    inputs:
      story_count:
        description: "How many new long-form stories to generate. Default: 15."
        required: true
        default: "15"
      image_cap:
        description: "Max NEW AI thumbnails this run. 0 = no cap."
        required: true
        default: "0"
      article_cap:
        description: "Max newest articles to receive AI thumbnails. 0 = no cap."
        required: true
        default: "0"
  schedule:
    - cron: "5 12 * * *"

jobs:
  preserve-and-append:
    runs-on: ubuntu-latest
    timeout-minutes: 360
    permissions:
      contents: write
      pull-requests: write
    steps:
      - name: Check out repo
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install openai requests beautifulsoup4

      - name: Verify automation scripts exist
        run: |
          ls -la studio/automation
          test -f studio/automation/preserve_old_and_new_issue_v34567.py
          test -f studio/automation/ai_thumbnail_backfill.py

      - name: Generate new issue without wiping old site
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          PEXELS_API_KEY: ${{ secrets.PEXELS_API_KEY }}
          STORY_COUNT: ${{ github.event.inputs.story_count || '15' }}
          SITE_BASE_URL: https://thepress.live
          OPENAI_MODEL: gpt-5.5
          ARTICLE_TARGET_WORDS: "2500"
          MIN_SOURCES: "20"
          MAX_SOURCES: "30"
          MIN_UNIQUE_SOURCE_DOMAINS: "8"
          QUALITY_REPAIR_ATTEMPTS: "2"
          FACT_CHECK_PASSES: "1"
          MAX_OUTPUT_TOKENS: "24000"
          MAX_STORY_COUNT: "30"
          STRICT_QUALITY_GATE: "0"
          STRICT_EDITORIAL_GATES: "0"
          RECENT_TOPIC_LOOKBACK: "120"
          RECENT_TOPIC_SIMILARITY_LIMIT: "0.34"
          ISSUE_TOPIC_SIMILARITY_LIMIT: "0.26"
          VISUAL_CONCEPT_SIMILARITY_LIMIT: "0.32"
          TITLE_RHYTHM_SIMILARITY_LIMIT: "0.64"
          TITLE_STYLE_GATE: "1"
        run: |
          python studio/automation/preserve_old_and_new_issue_v34567.py

      - name: Build GPT Image 2 thumbnails for new stories only
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          AI_THUMBNAIL_BACKFILL: "1"
          OPENAI_IMAGE_MODEL: gpt-image-2
          OPENAI_IMAGE_SIZE: 1536x864
          OPENAI_IMAGE_QUALITY: high
          OPENAI_IMAGE_FORMAT: jpeg
          OPENAI_IMAGE_COMPRESSION: "85"
          AI_ART_SCOPE: current_issue
          AI_ART_MAX_ARTICLES: ${{ github.event.inputs.article_cap || '0' }}
          AI_TOTAL_IMAGE_MAX_GENERATIONS: ${{ github.event.inputs.image_cap || '0' }}
          AI_THUMBNAIL_MAX_GENERATIONS: ${{ github.event.inputs.image_cap || '0' }}
          REPLACE_SVG_ARTICLE_THUMBNAILS: "1"
          FORCE_AI_FOR_ALL_ARTICLE_THUMBNAILS: "1"
          FORCE_AI_FOR_DAILY_STORIES: "1"
          AI_ART_PACKAGE_BACKFILL: "0"
          AI_GALLERY_IMAGES_PER_ARTICLE: "0"
          AI_UPDATE_LINKED_CARDS: "1"
          AI_CARD_UPDATE_SCOPE: front_pages
          AI_ART_PROMPT_MODEL: gpt-5.5
          AI_REGENERATE_AI_THUMBNAILS: "0"
        run: |
          python studio/automation/ai_thumbnail_backfill.py

      - name: Create review PR
        uses: peter-evans/create-pull-request@v6
        with:
          branch: ai-preserve-${{ github.run_number }}
          delete-branch: true
          title: "The Press daily issue — sourced stories with GPT Image 2 thumbnails"
          body: |
            This PR preserves the existing site and appends the newest daily issue.
            It uses GPT-5.5 for writing defaults, keeps strict fatal gates off by default,
            and gives every current issue article a GPT Image 2 thumbnail pass.
          commit-message: "Append daily issue with GPT Image 2 thumbnails"
'''


def backup(path: Path) -> None:
    if not path.exists() or path.is_dir():
        return
    rel = path.relative_to(ROOT)
    dest = BACKUP_DIR / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(path.read_bytes())


def strip_block(text: str, start: str, end: str) -> str:
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    return pattern.sub('', text)


def patch_styles() -> bool:
    path = ROOT / 'styles.css'
    if not path.exists():
        path.write_text('', encoding='utf-8')
    text = path.read_text(encoding='utf-8', errors='ignore')
    original = text
    # The previous patch left this file starting with an unmatched comment closer in some repos.
    text = re.sub(r'^\s*\*/\s*', '', text, count=1)
    text = strip_block(text, '/* PRESS_HARD_VISIBLE_FIX_CSS_START */', '/* PRESS_HARD_VISIBLE_FIX_CSS_END */')
    text = text.rstrip() + '\n' if text.strip() else ''
    text += '\n' + CSS_BLOCK + '\n'
    if text != original:
        backup(path)
        path.write_text(text, encoding='utf-8')
        return True
    return False


def patch_app_js() -> bool:
    path = ROOT / 'app.js'
    if not path.exists():
        return False
    text = path.read_text(encoding='utf-8', errors='ignore')
    original = text
    # Disable the call that adds the 170ms delayed navigation animation.
    text = text.replace('setupSmoothNavigation();', '/* setupSmoothNavigation disabled by visible hardfix */')
    text = strip_block(text, '/* PRESS_HARD_VISIBLE_FIX_APP_GUARD_START */', '/* PRESS_HARD_VISIBLE_FIX_APP_GUARD_END */')
    text = text.rstrip() + '\n' if text.strip() else ''
    text += '\n' + APP_JS_BLOCK + '\n'
    if text != original:
        backup(path)
        path.write_text(text, encoding='utf-8')
        return True
    return False


def patch_html_file(path: Path) -> bool:
    text = path.read_text(encoding='utf-8', errors='ignore')
    original = text

    # Remove old copies of this exact hardfix.
    text = re.sub(r'<style id="press-hard-visible-fix-style">.*?</style>\s*', '', text, flags=re.S)
    text = re.sub(r'<script id="press-hard-visible-fix-script">.*?</script>\s*', '', text, flags=re.S)

    # Cache-bust normal external assets where they exist.
    text = re.sub(r'(href=["\']styles\.css)(?:\?[^"\']*)?(["\'])', rf'\1?v={VERSION}\2', text)
    text = re.sub(r'(src=["\']app\.js)(?:\?[^"\']*)?(["\'])', rf'\1?v={VERSION}\2', text)

    inline_css = '<style id="press-hard-visible-fix-style">\n' + CSS_BLOCK + '\n</style>\n'
    if re.search(r'</head\s*>', text, flags=re.I):
        text = re.sub(r'</head\s*>', lambda _m: inline_css + '</head>', text, count=1, flags=re.I)
    else:
        text = inline_css + text

    if re.search(r'</body\s*>', text, flags=re.I):
        text = re.sub(r'</body\s*>', lambda _m: JS_BLOCK + '\n</body>', text, count=1, flags=re.I)
    else:
        text = text + '\n' + JS_BLOCK + '\n'

    if text != original:
        backup(path)
        path.write_text(text, encoding='utf-8')
        return True
    return False


def patch_html() -> list[Path]:
    changed: list[Path] = []
    # Patch root/front-facing pages and generated daily pages. Skip backups and node/vendor folders.
    skip_parts = {'.git', 'node_modules', '__pycache__'}
    for path in ROOT.rglob('*.html'):
        if any(part in skip_parts or part.startswith('.bak-') for part in path.parts):
            continue
        # These are static site pages; adding a small inline hardfix is intentional.
        if patch_html_file(path):
            changed.append(path)
    return changed


def patch_workflows() -> list[Path]:
    changed = []
    wf = ROOT / '.github' / 'workflows'
    wf.mkdir(parents=True, exist_ok=True)
    targets = {
        wf / 'ai-thumbnail-backfill.yml': AI_THUMBNAIL_WORKFLOW,
        wf / 'daily-ai-newsroom.yml': DAILY_WORKFLOW,
    }
    for path, content in targets.items():
        old = path.read_text(encoding='utf-8', errors='ignore') if path.exists() else ''
        if old != content:
            backup(path)
            path.write_text(content, encoding='utf-8')
            changed.append(path)
    return changed


def main() -> None:
    changed = []
    if patch_styles():
        changed.append(ROOT / 'styles.css')
    if patch_app_js():
        changed.append(ROOT / 'app.js')
    changed.extend(patch_html())
    changed.extend(patch_workflows())

    if changed:
        print('Applied visible hardfix. Changed files:')
        for path in sorted(set(changed)):
            print(' -', path.relative_to(ROOT))
        print('\nBackups are in:', BACKUP_DIR.relative_to(ROOT))
        print('\nNow run:')
        print('  git status --short')
        print('  git add .')
        print('  git commit -m "Apply hard visible homepage and no-flash fix"')
        print('  git push')
    else:
        print('No changes needed. The hardfix is already applied.')


if __name__ == '__main__':
    main()
