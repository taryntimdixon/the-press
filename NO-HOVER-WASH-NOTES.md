# No hover wash fix

This removes the colored background/wash that appeared behind article words on hover, while keeping the nice card lift and other dynamic interactions.

Run from the repo root:

```bash
python3 tools/remove_hover_wash.py
```

The script is safe to run more than once. It removes the old article paragraph hover-highlight block when present and appends a final CSS guard that disables colored hover backgrounds on article text and article cards.
