# Topic Radar upgrade for The Press

This bundle starts the workflow change you asked for: topic selection happens before article generation, with a broader radar of world news, AI, uprisings, science, food/life/culture, and a bunch of other high-interest lanes.

## What it adds

1. `studio/automation/topic_radar.py`
   - Builds a daily assignment plan with web search before the article writer runs.
   - Saves reviewable files:
     - `daily/topic-candidates-YYYY-MM-DD.json`
     - `daily/topic-plan-latest.json`
   - Uses broader editorial buckets without forcing the public site nav to change.

2. Patch to `studio/automation/preserve_old_and_new_issue_v34567.py`
   - Calls Topic Radar after recent archive memory loads.
   - Sends each article writer a locked assignment.
   - Keeps the old section-rotation flow as fallback if radar is disabled or fails.

3. Patch to `.github/workflows/daily-ai-newsroom.yml`
   - Adds workflow knobs for issue mix, variety, headline humility, and reader-friendly density.

4. Reader-friendly editorial voice layer
   - Adds a reusable `READER_VOICE_GUIDE` to the article prompt.
   - Pushes headlines away from all-knowing frames like “this proves,” “the real truth,” or “everything changed.”
   - Adds a density gate for long, specialist-heavy sentence patterns so articles stay approachable without getting thin.

## New topic buckets

Existing radar buckets include world heat, uprisings, AI, science, food culture/life, culture/platforms, money systems, weird-but-real, and local-to-global.

This upgrade adds these extra reader-interest buckets:

- `CLIMATE_EXTREMES`
- `CYBER_SECURITY`
- `MIGRATION_BORDERS`
- `CITIES_HOUSING_TRANSIT`
- `SPORTS_POWER`
- `RELIGION_IDENTITY`
- `JUSTICE_PUBLIC_SAFETY`
- `ENERGY_INFRASTRUCTURE`
- `CONSUMER_LIFE`
- `HEALTH_SYSTEM_SHOCK`
- `EDUCATION_YOUTH`
- `SPACE_OCEAN_FRONTIER`
- `NATURE_ANIMALS`

That is more than seven on purpose. The paper should have range.

## Reader-friendly writing upgrade

This addition is meant to make the articles feel fun, useful, and open to everybody without dumbing anything down. The generator now gets these principles before it writes:

- Write for curious people from age 10 to 99.
- Use plain language first, then add depth.
- Explain specialized terms the first time they appear.
- Be creative with structure, examples, and analogies — not with facts.
- Stay unbiased by separating evidence, interpretation, and uncertainty.
- Avoid headlines that sound like The Press has solved the whole subject.

The patch also makes those headline-humility and density warnings repair-triggering, so the generator gets another chance to rewrite before the story is accepted.

## How to apply

From the repo root:

```bash
cp /path/to/topic_radar.py ./topic_radar.py
cp /path/to/apply_topic_radar_upgrade.py ./apply_topic_radar_upgrade.py
python apply_topic_radar_upgrade.py
python -m py_compile studio/automation/topic_radar.py studio/automation/preserve_old_and_new_issue_v34567.py
git diff -- studio/automation .github/workflows/daily-ai-newsroom.yml
```

Then test manually from GitHub Actions:

```bash
gh workflow run daily-ai-newsroom.yml -f story_count=15 -f image_cap=0 -f article_cap=0
```

## Important knobs

```yaml
TOPIC_SELECTION_MODE: "radar"
TOPIC_RADAR_MODEL: gpt-5.5
TREND_LOOKBACK_HOURS: "48"
HEADLINE_CERTAINTY_GATE: "1"
MAX_AVG_SENTENCE_WORDS: "24"
MAX_LONG_SENTENCE_SHARE: "0.22"
MIN_WORLD_HEAT_STORIES: "3"
MIN_AI_OR_SCIENCE_STORIES: "2"
MIN_FOOD_CULTURE_LIFE_STORIES: "1"
MIN_WEIRD_OR_NICHE_STORIES: "1"
MIN_NON_US_STORIES: "4"
MAX_US_INSTITUTIONAL_PROCESS_STORIES: "2"
MAX_SAME_COUNTRY_STORIES: "2"
MAX_SAME_BUCKET_STORIES: "3"
WILDCARD_RATE: "0.20"
```

To fall back to the old process without deleting the new code:

```yaml
TOPIC_SELECTION_MODE: "rotation"
```

## What to check in the first run

Open `daily/topic-plan-latest.json` before merging the generated PR. You should see a front-page mix with giant world stories, AI/science, food/life/culture, and a weird or niche assignment. If the plan looks good, the articles should follow.
