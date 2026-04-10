# View The Press on Your Phone

## Fastest path: publish it once, then open the link on your phone

### Option 1: drag-and-drop publish
1. Unzip the full site package if needed.
2. Upload the **the-press** folder to a static host that accepts direct uploads.
3. Open the generated website link on your phone.

Good fits for this static site:
- **Netlify Drop** for the quickest one-off publish
- **Cloudflare Pages Direct Upload** for a similar direct-upload workflow

## Best path for a permanent site

### Option 2: GitHub Pages
1. Create a new GitHub repository.
2. Upload the contents of the **the-press** folder.
3. Turn on GitHub Pages and publish from your main branch / root folder.
4. Open the GitHub Pages URL on your phone.

## Temporary same-Wi-Fi preview from your computer

If you want to test it before publishing:
1. On your computer, open a terminal in the **the-press** folder.
2. Run:

```bash
python local-preview-on-phone.py
```

3. Make sure your computer and phone are on the same Wi-Fi network.
4. Open the printed local address on your phone.

This is only for previewing. It is not a production host.

## Notes
- This site is now fully bundled with its CSS, JS, and local image assets.
- It is responsive and should read cleanly on mobile screens.
- The build now includes home-screen app icons and manifest metadata.
