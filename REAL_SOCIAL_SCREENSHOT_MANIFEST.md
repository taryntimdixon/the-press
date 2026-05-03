# Social screenshot manifest — no generated images included

This version does **not** ship generated social screenshots. The rail cards are link-only by default and may use clearly labeled AI editorial illustrations as visual summaries. If you want a card to show an actual post image, manually capture a real public post/source screenshot and save it to the matching path below.

## Screenshot-ready filenames

- `assets/social/atla-official-announcement.jpg`
- `assets/social/creator-atla-noho-reel.jpg`
- `assets/social/eater-ny-atla-closing-post.jpg`
- `assets/social/latimes-san-damian-x-post.jpg`
- `assets/social/public-atla-food-post.jpg`
- `assets/social/public-atla-quesadilla-post.jpg`
- `assets/social/public-repost-atla-announcement.jpg`

The small script in the article tries to load these files. If a file exists, the image appears. If it does not exist, the card remains clean with its illustrated/text summary — no broken image box and no fake social screenshot.

## Illustration fallback

The Atla rail also includes 52 contextual AI editorial SVG illustrations in `assets/social/illustrations/`. They are not screenshots and should be replaced by real manually captured screenshots only when those real screenshots are available.
