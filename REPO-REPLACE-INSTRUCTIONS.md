# Replace your GitHub site with the repaired build

This build fixes the issues you reported:
- restores the missing `assets/` folder and `styles.css`
- makes the right-rail story rows clickable
- changes visible bylines to **Written by Intelligent AI**
- replaces the old Authors page with an **AI Newsroom** page
- keeps article images from disappearing by restoring the image files and fallback artwork
- adds a visible **Latest AI Edition** link on the homepage and archive page
- makes lead/article images show more of the full photo instead of cropping hard

## Simplest way to update GitHub

1. Download the repaired ZIP.
2. Unzip it on your computer.
3. Open your GitHub repo.
4. Click **Code**.
5. Click **Add file** → **Upload files**.
6. Drag **everything inside** the unzipped `the-press-repaired` folder into GitHub.
7. If GitHub says files with the same name already exist, let it replace them.
8. Click **Commit changes**.
9. Wait about 30–60 seconds.
10. Hard refresh your live site.

## Important

Do **not** delete your `.github/` folder if you want to keep the AI workflow. This repaired site bundle does not include that hidden folder, so just upload the site files on top of your existing repo.
