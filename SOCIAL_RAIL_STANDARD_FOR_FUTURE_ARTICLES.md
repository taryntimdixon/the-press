# The Press social-rail standard for future long-form articles

## Purpose

The social rail is a companion layer for long feature stories. It should make the article feel alive as the reader scrolls: public conversation, official posts, source cards, critic notes, guide context, neighborhood signals, and reader mood travel beside the main story.

## Core layout

Use repeated rows instead of one giant sidebar:

```html
<section class="press-social-feature">
  <div class="press-social-row">
    <aside class="press-social-side press-social-side--left">
      <!-- social/source cards -->
    </aside>

    <section class="press-social-content">
      <!-- article section -->
    </section>

    <aside class="press-social-side press-social-side--right">
      <!-- social/source cards -->
    </aside>
  </div>
</section>
```

## Card types

Use these recurring card roles:

- official restaurant/company/source post
- reporter/news-break post
- creator/Reel/TikTok slot, if a real public post exists
- critic/review card
- guide/rating card
- neighborhood/context card
- transparent composite reader-mood card
- menu/object card
- timeline card

## Image rule

Do not create fake social screenshots.

Allowed:
- A real screenshot manually uploaded by the editor.
- A real source-page screenshot, where rights and editorial policy allow.
- Text-only cards with a click-through link.
- AI-generated editorial illustrations that summarize the source context, if clearly labeled and not styled like platform screenshots.
- AI-generated editorial thumbnails/heroes, if clearly labeled as AI-generated and not documentary photographs.

Not allowed:
- Fake usernames.
- Fake Instagram/TikTok/X screenshots.
- Fake comments presented as real public reaction.
- Generated source screenshots.
- Generated art that imitates Instagram, TikTok, X, Substack, or another live platform UI.
- “Image goes here” boxes in published pages.

## Screenshot fallback behavior

Cards that may show screenshots should be written so missing images do not break layout. If the local file does not exist, the card remains text-only and keeps its source link.

## Illustration fallback behavior

When a real screenshot is unavailable, a rail card may use the reusable illustrated-summary treatment in `.press-static-post__visual`. The illustration should be editorial art generated from the card's source context or summary, not a fake post. Keep the original click-through link visible.

For larger feature packages, prefer local generated illustration assets over generic placeholders. The Atla package uses one contextual SVG per rail card under `assets/social/illustrations/`, loaded only when a real screenshot is not present.

## Placement rule

Side cards should run from the top of the article until the source section. Do not cluster all cards near the first paragraph.

## Mobile rule

On small screens, stack the article copy and cards. The main article should remain easy to read. Social cards can appear between sections or below each section.

## Source notes

Visible source notes belong after the final social row. They should not be interrupted by side rails.
