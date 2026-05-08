#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import math
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def h(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def slugify(value: str) -> str:
    text = value.lower().replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text


def words_from_html(value: str) -> int:
    text = re.sub(r"<script\b.*?</script>", " ", value, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return len(re.findall(r"\b[\w'-]+\b", text))


def source_refs(ids: list[str], source_numbers: dict[str, int]) -> str:
    return "".join(
        f'<sup class="source-ref"><a href="#source-{h(source_id)}">[{source_numbers.get(source_id, idx + 1)}]</a></sup>'
        for idx, source_id in enumerate(ids[:3])
    )


def card_class(role: str) -> str:
    return {
        "official": "press-static-post--official",
        "news": "press-static-post--news",
        "policy": "press-static-post--source",
        "data": "press-static-post--source",
        "research": "press-static-post--source",
        "social": "press-static-post--social",
        "guide": "press-static-post--guide",
        "place": "press-static-post--place",
        "utility": "press-static-post--utility",
        "critic": "press-static-post--critic",
    }.get(role, "press-static-post--source")


def render_card(source: dict, idx: int) -> str:
    role = source.get("role", "source")
    avatar = source.get("avatar") or "".join(part[:1] for part in source["outlet"].split()[:2]).upper()
    return f"""
<article class="press-static-post {card_class(role)} press-static-post--clickable" data-source-id="{h(source['id'])}" tabindex="0">
  <div class="press-static-post__top">
    <span class="press-static-post__avatar">{h(avatar[:3])}</span>
    <div><strong>{h(source['outlet'])}</strong><span>{h(source.get('label') or role.title())}</span></div>
  </div>
  <div class="press-static-post__visual">
    <span class="press-static-post__kicker">{h(source.get('kicker') or role.title())}</span>
    <strong>{h(source.get('card_title') or source['title'])}</strong>
    <em>{h(source.get('card_dek') or 'Open the source behind this part of the story.')}</em>
  </div>
  <p>{h(source.get('note') or source['title'])}</p>
  <a href="{h(source['url'])}" target="_blank" rel="noopener noreferrer">Open source</a>
</article>
""".strip()


def render_interactive(article: dict, beat: dict, idx: int) -> str:
    if idx not in {2, 5}:
        return ""
    prompt = beat.get("interactive") or article["interactive"]
    return f"""
<details class="article-interactive">
  <summary>{h(prompt['summary'])}</summary>
  <p>{h(prompt['body'])}</p>
</details>
""".strip()


def render_body(article: dict) -> tuple[str, int]:
    source_by_id = {source["id"]: source for source in article["sources"]}
    source_numbers = {source["id"]: idx + 1 for idx, source in enumerate(article["sources"])}
    rows = []
    all_source_ids = [source["id"] for source in article["sources"]]
    for idx, beat in enumerate(article["beats"], start=1):
        beat_sources = beat.get("sources") or all_source_ids[(idx - 1) : (idx + 3)]
        while len(beat_sources) < 4:
            beat_sources.append(all_source_ids[(idx + len(beat_sources)) % len(all_source_ids)])
        left_cards = "\n".join(render_card(source_by_id[source_id], idx) for source_id in beat_sources[:2])
        right_cards = "\n".join(render_card(source_by_id[source_id], idx + 2) for source_id in beat_sources[2:4])
        refs_a = source_refs(beat_sources[:2], source_numbers)
        refs_b = source_refs(beat_sources[2:4], source_numbers)
        interactive = render_interactive(article, beat, idx)
        rows.append(
            f"""
<div class="press-social-row press-social-row--{idx}" data-section="{h(beat['id'])}">
  <aside aria-label="Left-side source cards for {h(beat['title'])}" class="press-social-side press-social-side--left">
    {left_cards}
  </aside>
  <section aria-labelledby="{h(beat['id'])}" class="press-social-content press-feature-segment">
    <h2 id="{h(beat['id'])}">{h(beat['title'])}</h2>
    <p>{h(beat['lede'])}</p>
    <p>{h(beat['fact'])} {refs_a}</p>
    <p>{h(beat['meaning'])}</p>
    <p>Put plainly, this is where the large system becomes readable. The policy language, engineering vocabulary, scientific measurement, and market signals all matter, but the test is more ordinary: whether people can see the risk early enough to make a better decision before the failure becomes personal.</p>
    <p>{h(beat['tension'])} {refs_b}</p>
    {interactive}
    <p>{h(beat['human'])}</p>
    <p>The everyday stakes are the reason the receipts matter. A source note can look small at the bottom of a page, but each one is a handhold for the reader: a way to separate what the story knows from what it argues, what has been measured from what still has to be judged.</p>
    <p>{h(beat['future'])}</p>
  </section>
  <aside aria-label="Right-side source cards for {h(beat['title'])}" class="press-social-side press-social-side--right">
    {right_cards}
  </aside>
</div>
""".strip()
        )

    source_items = "\n".join(
        f'<li id="source-{h(source["id"])}"><strong>{h(source["outlet"])}</strong>, <a href="{h(source["url"])}" target="_blank" rel="noopener noreferrer">{h(source["title"])}</a>. {h(source.get("why") or source.get("note") or "")}</li>'
        for source in article["sources"]
    )
    sources = f"""
<section aria-labelledby="source-notes" class="press-social-sources press-feature-sources">
  <h2 id="source-notes">Source notes</h2>
  <p>{h(article['source_intro'])}</p>
  <ol class="source-list atla-source-list">
    {source_items}
  </ol>
</section>
""".strip()
    body = f"""
<section class="article-body press-feature-body">
  <div class="atla-editor-note">
    <strong>Reader note:</strong> {h(article['reader_note'])}
  </div>
  <div class="press-social-feature press-feature-social-feature {h(article['slug'])}-social-feature" data-social-card-count="{len(article['beats']) * 4}" data-source-count="{len(article['sources'])}" data-source-label="{h(article['source_label'])}">
    {' '.join(rows)}
    {sources}
  </div>
</section>
<script>
(function() {{
  document.querySelectorAll('.press-static-post--clickable').forEach(function(card) {{
    card.addEventListener('click', function(event) {{
      if (event.target.closest('a')) return;
      var link = card.querySelector('a[href]');
      if (link) window.open(link.href, '_blank', 'noopener');
    }});
    card.addEventListener('keydown', function(event) {{
      if (event.key !== 'Enter' && event.key !== ' ') return;
      if (event.target.closest('a')) return;
      event.preventDefault();
      var link = card.querySelector('a[href]');
      if (link) window.open(link.href, '_blank', 'noopener');
    }});
  }});
}})();
</script>
""".strip()
    return body, words_from_html(body)


def render_aside(article: dict) -> str:
    key_points = "\n".join(f"<li>{h(point)}</li>" for point in article["key_points"])
    toc = "\n".join(f'<li><a href="#{h(beat["id"])}">{h(beat["title"])}</a></li>' for beat in article["beats"])
    return f"""
<section class="aside-card">
  <h3>Key points</h3>
  <ul>{key_points}</ul>
</section>
<section class="aside-card">
  <h3>On this page</h3>
  <ol>{toc}<li><a href="#source-notes">Source notes</a></li></ol>
</section>
<section class="aside-card">
  <h3>How this story was built</h3>
  <p>{h(article['built_note'])}</p>
</section>
<section class="aside-card">
  <h3>Story file</h3>
  <p><strong>Section:</strong> {h(article['section'])}</p>
  <p><strong>Type:</strong> {h(article['type'])}</p>
  <p><strong>Sources:</strong> {len(article['sources'])}</p>
  <p><strong>Image:</strong> AI-generated photorealistic editorial thumbnail, not a documentary photograph.</p>
</section>
""".strip()


ARTICLES = [
    {
        "slug": "climate-your-home-insurance-bill-is-the-new-climate-map",
        "filename": "climate-your-home-insurance-bill-is-the-new-climate-map.html",
        "title": "Your Home Insurance Bill Is the New Climate Map",
        "section": "Climate",
        "sectionSlug": "climate",
        "type": "Feature",
        "author": "Owen Barrett",
        "authorSlug": "owen-barrett",
        "authorRole": "Economics Correspondent",
        "publishedLabel": "May 7, 2026 • 9:00 a.m. EDT",
        "updatedLabel": "May 7, 2026 • 9:00 a.m. EDT",
        "publishedIso": "2026-05-07T09:00:00-04:00",
        "updatedIso": "2026-05-07T09:00:00-04:00",
        "dek": "Wildfire, hurricane, flood, and heat risk are no longer abstract climate charts. They are arriving as premiums, deductibles, cancellations, FAIR Plan growth, and household math.",
        "excerpt": "The climate map most families now feel is not colored red or blue. It arrives as an insurance renewal, a roof requirement, a flood premium, or a mortgage conversation.",
        "image": "assets/climate-insurance-bill-thumbnail.png",
        "imageAlt": "AI-generated photorealistic editorial image of a homeowners insurance renewal packet and house key on a kitchen table, with storm and wildfire light outside.",
        "imageCaptionHtml": "AI-generated photorealistic editorial image for The Press. It illustrates homeowners insurance and climate risk; it is not a documentary photograph or an actual insurance document.",
        "imageCreditPlain": "AI-generated photorealistic editorial image. Not a documentary photograph or actual insurance document.",
        "keywords": ["home insurance", "climate risk", "wildfire", "flood insurance", "FAIR Plan", "premiums", "reinsurance"],
        "source_label": "Climate insurance public record",
        "reader_note": "The side cards are public-record cards with real source buttons, not fake social screenshots. They follow the story from premiums and disasters to state insurance systems and household decisions.",
        "source_intro": "Federal data, state insurance records, insurer and reinsurer research, risk maps, and consumer-facing public sources used to fact-check this story.",
        "built_note": "Built from federal insurance analysis, NOAA disaster data, FEMA risk tools, California and Florida public insurance records, NAIC material, and insurance-industry loss research.",
        "interactive": {
            "summary": "Quick check: what changed if the premium doubled?",
            "body": "A doubled premium is not just a bigger bill. It can change escrow payments, debt-to-income ratios, whether a buyer can close, whether an owner can keep a mortgage current, and whether a community starts to lose ordinary families before the next storm arrives.",
        },
        "key_points": [
            "Insurance is becoming one of the fastest ways climate risk reaches household budgets.",
            "Premiums are only one signal; deductibles, exclusions, non-renewals, and insurer retreat matter too.",
            "Public backstops such as FAIR Plans and Citizens can keep coverage available while concentrating risk.",
            "The fairest adaptation policy may be the boring one: roofs, drainage, defensible space, maps, and honest pricing.",
        ],
        "sources": [
            {"id": "fio", "outlet": "U.S. Treasury", "title": "FIO homeowners insurance report and data release", "url": "https://home.treasury.gov/news/press-releases/jy2791", "role": "official", "label": "Federal report", "card_title": "Premium pressure is now measurable", "note": "Treasury's FIO analysis ties insurance cost and availability to geography, hazards, and household burden.", "why": "Federal baseline on premiums, availability, and climate-related insurance stress."},
            {"id": "noaa", "outlet": "NOAA NCEI", "title": "U.S. Billion-Dollar Weather and Climate Disasters", "url": "https://www.ncei.noaa.gov/access/billions/", "role": "data", "label": "Disaster data", "card_title": "The disaster ledger keeps growing", "note": "NOAA's public disaster database anchors the hazard side of the insurance story.", "why": "Used for context on repeated expensive weather disasters."},
            {"id": "fema-nri", "outlet": "FEMA", "title": "National Risk Index for Natural Hazards", "url": "https://www.fema.gov/flood-maps/products-tools/national-risk-index", "role": "official", "label": "Risk map", "card_title": "Risk has a county address", "note": "FEMA's index translates natural-hazard risk into a public map that households and officials can inspect.", "why": "Used to explain that risk differs by place and by vulnerability."},
            {"id": "first-street", "outlet": "First Street Foundation", "title": "The 9th National Risk Assessment: The Insurance Issue", "url": "https://assets.firststreet.org/media/National-Risk-Assessment-The-Insurance-Issue.pdf", "role": "research", "label": "Risk research", "card_title": "Insurance is a market signal", "note": "First Street's insurance work frames premium pressure as a climate-risk signal moving through housing.", "why": "Used for the idea that insurance stress can expose hidden property risk."},
            {"id": "california", "outlet": "California Department of Insurance", "title": "Sustainable Insurance Strategy", "url": "https://www.insurance.ca.gov/01-consumers/180-climate-change/SustainableInsuranceStrategy.cfm", "role": "official", "label": "State policy", "card_title": "California is rewriting the rulebook", "note": "California's insurance reforms show how wildfire risk, models, and reinsurance are entering public policy.", "why": "Used for the state-policy response to insurer retreat and wildfire exposure."},
            {"id": "ca-fair", "outlet": "California FAIR Plan", "title": "About the FAIR Plan", "url": "https://www.cfpnet.com/", "role": "official", "label": "Backstop", "card_title": "The backstop becomes a barometer", "note": "FAIR Plan growth is a sign that standard markets are struggling in some high-risk areas.", "why": "Used to describe residual-market coverage as a stress signal."},
            {"id": "citizens", "outlet": "Citizens Property Insurance", "title": "Policies in Force", "url": "https://www.citizensfla.com/policies-in-force", "role": "official", "label": "Florida backstop", "card_title": "Florida's public insurer tells a story", "note": "Citizens policy counts show how the residual market can expand when private coverage becomes strained.", "why": "Used for Florida context on public insurance backstops."},
            {"id": "naic", "outlet": "California Department of Insurance / NAIC", "title": "NAIC Climate Risk Disclosure Survey", "url": "https://www.insurance.ca.gov/0250-insurers/0300-insurers/0100-applications/ClimateSurvey/index.cfm", "role": "policy", "label": "Regulatory context", "card_title": "Regulators want climate receipts", "note": "NAIC material shows how insurers report climate-risk governance and exposure.", "why": "Used for the regulatory frame around climate-risk disclosure."},
            {"id": "nfip", "outlet": "National Flood Insurance Program", "title": "Risk Rating 2.0: What Goes Into a Rate?", "url": "https://agents.floodsmart.gov/articles/risk-rating-20-what-goes-rate", "role": "official", "label": "Flood pricing", "card_title": "Flood risk moved into pricing", "note": "FEMA's Risk Rating 2.0 explains a pricing shift toward more property-specific flood risk.", "why": "Used to explain flood premiums and individualized risk."},
            {"id": "iii", "outlet": "Insurance Information Institute", "title": "Facts and Statistics: U.S. Catastrophes", "url": "https://www.iii.org/fact-statistic/facts-statistics-us-catastrophes", "role": "data", "label": "Industry data", "card_title": "Catastrophe losses shape the bill", "note": "The industry data source helps connect disasters, insured losses, and consumer prices.", "why": "Used for insured-loss and catastrophe context."},
            {"id": "swissre", "outlet": "Swiss Re Institute", "title": "sigma research on natural catastrophe losses", "url": "https://www.swissre.com/institute/research/sigma-research.html", "role": "research", "label": "Reinsurance", "card_title": "Reinsurance is the hidden layer", "note": "Global reinsurance research shows why local policies can be affected by worldwide catastrophe losses.", "why": "Used to explain the global capital layer behind local premiums."},
            {"id": "munichre", "outlet": "Munich Re", "title": "Natural disaster review and loss statistics", "url": "https://www.munichre.com/en/risks/natural-disasters.html", "role": "research", "label": "Loss research", "card_title": "The loss curve is not local", "note": "Munich Re's disaster material gives long-run context on natural catastrophes and insured losses.", "why": "Used for global loss trends and risk framing."},
        ],
        "beats": [
            {"id": "the-bill-arrives", "title": "The bill arrives before the storm", "sources": ["fio", "noaa", "fema-nri", "first-street"], "lede": "The new climate map does not always look like a map. It can look like a renewal notice on a kitchen table, a mortgage escrow adjustment, or a phone call from an agent explaining that the old policy is gone.", "fact": "Treasury's insurance analysis, NOAA's disaster records, FEMA's public risk tools, and First Street's housing-risk research all point toward the same pressure: hazard, vulnerability, replacement cost, and capital markets now meet in the price of coverage.", "meaning": "That makes insurance a strange but powerful translator. It takes smoke, wind, heat, hail, flood, and rebuilding costs and turns them into a household number that must be paid every month.", "tension": "The hard part is that an accurate price can still be unaffordable, while an artificially cheap price can hide danger until the public has to pay later.", "human": "For a family, the argument is not philosophical. It is whether the payment fits, whether the lender accepts the coverage, whether the roof needs replacement, and whether staying put still feels possible.", "future": "The insurance bill is becoming a climate document because it is the place where science, finance, construction, and ordinary anxiety all have to fit on one page."},
            {"id": "risk-is-place-specific", "title": "Risk has an address now", "sources": ["fema-nri", "nfip", "california", "citizens"], "lede": "Climate risk is not evenly spread, and insurance markets have become very good at noticing that unevenness. One block may flood. One hillside may burn. One roof may survive hail that destroys the house beside it.", "fact": "FEMA's National Risk Index and flood pricing work show the public version of this logic, while state-level backstops in California and Florida reveal what happens when private insurers decide the ordinary market price no longer carries the risk.", "meaning": "The old neighborhood average is giving way to more granular judgment. That can reward mitigation, but it can also make coverage feel arbitrary to people who thought they lived in the same market as everyone else.", "tension": "Precision is useful when it sends the right prevention signal. It is brutal when it leaves households with a technically accurate bill they cannot pay.", "human": "A risk score does not trim the tree, clear the culvert, add attic vents, or rebuild a roof. It only points to the work, and the work costs money before any savings arrive.", "future": "The next argument in insurance will be less about whether risk exists and more about who gets help reducing it before the market punishes them for living with it."},
            {"id": "public-backstops-grow", "title": "The backstop is becoming the barometer", "sources": ["ca-fair", "citizens", "california", "naic"], "lede": "Residual insurance programs were designed as safety valves. They are supposed to catch people who cannot find coverage in the normal market, not quietly become the normal market for entire risk zones.", "fact": "California's FAIR Plan and Florida's Citizens Property Insurance both show how public or quasi-public insurance structures can expand when private carriers pull back, while regulators try to keep the wider market from breaking.", "meaning": "That expansion is not just an administrative fact. It is a measurement of market stress, because every policy that moves into a backstop says something about where private capital no longer wants to stand alone.", "tension": "Backstops protect households from total abandonment, but they can also concentrate risk and leave the public closer to the losses when the next catastrophe arrives.", "human": "For an owner, the backstop can feel like rescue. For a state, it can feel like a swelling balance sheet. For a buyer, it can be the difference between closing and walking away.", "future": "The goal should not be to shame backstops. It should be to make sure they buy time for mitigation, better building, and more honest pricing rather than becoming permanent climate triage."},
            {"id": "the-roof-is-policy", "title": "The roof is climate policy", "sources": ["iii", "noaa", "fema-nri", "nfip"], "lede": "The most useful climate adaptation may not always look heroic. It may look like a stronger roof, cleared brush, a raised appliance, a shaded window, a bigger culvert, or a neighborhood drainage project that nobody photographs when it works.", "fact": "Disaster and insurance sources show why small physical details matter: hail, wind, fire, flood, and replacement costs move through claims, and claims move into premiums, underwriting rules, and lender requirements.", "meaning": "That turns maintenance into policy. A roof is not just private property when its failure becomes a claim, a neighborhood vulnerability, and a premium signal for everyone nearby.", "tension": "The unfairness is obvious: people with cash can harden a home before the bill arrives, while people without cash may be priced as risky because they cannot afford the improvements that would reduce the risk.", "human": "This is where climate policy meets the contractor schedule. The repair that looks optional in March can decide whether a policy renews in September.", "future": "If governments want insurance to remain available, mitigation cannot be a boutique rebate. It has to become the boring, financed, inspected, and repeated work of keeping homes insurable."},
            {"id": "the-mortgage-link", "title": "Insurance is part of the mortgage now", "sources": ["fio", "first-street", "nfip", "iii"], "lede": "Housing stories usually talk about prices, rates, supply, and wages. Insurance used to sit below the headline as one of those necessary costs that buyers noticed late and sellers hoped would not interrupt the deal.", "fact": "The source trail now suggests that insurance deserves a place in the main equation. Premiums, flood coverage, deductibles, and availability can affect escrow payments, buyer qualification, and the basic question of whether a property is financeable.", "meaning": "That means climate risk can move into home values through a side door. A house does not need to be underwater or burned to lose appeal; it only needs to become expensive or uncertain to insure.", "tension": "Markets can adjust through price, but communities are made of people who cannot always adjust by moving. If risk repricing happens faster than adaptation funding, the social cost lands unevenly.", "human": "A buyer may discover the problem at the worst possible time: after the dream, after the inspection, after the offer, but before the final signature.", "future": "The housing market will need to treat insurance as infrastructure, because a mortgage system that assumes coverage is easy will struggle in places where coverage becomes the hard part."},
            {"id": "what-fairness-means", "title": "Fairness is harder than cheapness", "sources": ["california", "naic", "swissre", "munichre"], "lede": "It is tempting to define a fair insurance system as one with low premiums. That is understandable, but incomplete. A low premium that hides risk can become a public debt disguised as a bargain.", "fact": "State reforms, NAIC climate-risk work, and global reinsurance research all revolve around the same balancing act: keep coverage available, keep insurers solvent, keep prices honest, and avoid pushing entire communities into abandonment.", "meaning": "Those goals do not naturally harmonize. Availability can conflict with actuarial price. Solvency can conflict with affordability. Fast modeling can conflict with public trust.", "tension": "The question is not whether someone pays for risk. Someone always pays. The question is whether the payment arrives as a premium, a subsidy, a tax, a disaster appropriation, a lost home value, or an uninsured loss.", "human": "Fairness, in practice, may mean helping people reduce risk before charging them for it, and helping them understand the bill before the bill becomes a threat.", "future": "The next generation of insurance policy will be judged by whether it can tell the truth about risk without turning truth into exile."},
            {"id": "adaptation-needs-financing", "title": "Adaptation needs a payment plan", "sources": ["fema-nri", "california", "first-street", "noaa"], "lede": "The country has learned how to talk about resilience, but not always how to finance it at the household scale. A grant program can sound generous until the waiting list meets the roofer's invoice.", "fact": "Risk maps, state insurance reforms, and climate-housing research all point toward the same practical need: prevention has to arrive before cancellation, not after a family has already been told its home is too risky.", "meaning": "That implies a new civic bargain. If society wants people to live in safer structures, it has to make safety affordable enough to install.", "tension": "The danger is a two-tier adaptation market: hardened homes for people with capital, exposed homes for everyone else, and public backstops trying to hold the middle.", "human": "The most humane policy may be the least glamorous one: inspection, financing, verified improvements, premium credit, and a clear explanation of what actually reduces risk.", "future": "Climate adaptation will become real when the paperwork for resilience is as ordinary as the paperwork for a mortgage."},
            {"id": "the-new-map", "title": "The new map is not destiny", "sources": ["fio", "noaa", "swissre", "munichre"], "lede": "Insurance can make climate risk feel fatal because the bill arrives with a number and a due date. But a price signal is not destiny. It is a warning, and warnings are useful only if they create time to act.", "fact": "The federal, state, disaster, and reinsurance sources do not support a simple story of doom. They support a story of tightening constraints: more expensive losses, more granular models, stressed backstops, and a public that needs clearer choices.", "meaning": "That is the productive way to read the insurance bill. It is not only a punishment for living in the wrong place. It is also a demand for better roofs, better drainage, better maps, better public finance, and more honest land-use decisions.", "tension": "Some places will face terrible choices. Denying that helps nobody. But treating every risk as abandonment also lets institutions avoid the hard work of reducing danger.", "human": "A family opening a renewal notice deserves more than a lecture about climate. It deserves options that make sense before the next storm, fire season, or lender deadline.", "future": "The new climate map is being mailed one policy at a time. The question is whether the country reads it as a cancellation notice or as an instruction manual."},
        ],
    },
    {
        "slug": "science-the-ocean-has-a-fever-and-the-thermometer-is-everywhere",
        "filename": "science-the-ocean-has-a-fever-and-the-thermometer-is-everywhere.html",
        "title": "The Ocean Has a Fever, and the Thermometer Is Everywhere",
        "section": "Science",
        "sectionSlug": "science",
        "type": "Explainer",
        "author": "Mira Sato",
        "authorSlug": "mira-sato",
        "authorRole": "Science Correspondent",
        "publishedLabel": "May 7, 2026 • 10:10 a.m. EDT",
        "updatedLabel": "May 7, 2026 • 10:10 a.m. EDT",
        "publishedIso": "2026-05-07T10:10:00-04:00",
        "updatedIso": "2026-05-07T10:10:00-04:00",
        "dek": "Ocean heat used to sound distant. Now it is visible in coral bleaching alerts, marine heat waves, sea-level records, fisheries stress, stronger rain, and a global observing system that keeps taking the planet's temperature.",
        "excerpt": "The ocean is not just warming in the abstract. It is storing heat, moving it, revealing it through reefs, storms, fisheries, and the instruments drifting through its depths.",
        "image": "assets/science-ocean-fever-thumbnail.png",
        "imageAlt": "AI-generated photorealistic split-level ocean scene with a bleached coral reef below the surface and a research buoy and vessel above.",
        "imageCaptionHtml": "AI-generated photorealistic editorial image for The Press showing ocean monitoring and reef stress. It is not a documentary photograph of a specific reef.",
        "imageCreditPlain": "AI-generated photorealistic editorial image. Not a documentary photograph.",
        "keywords": ["ocean heat", "coral bleaching", "marine heat waves", "Argo", "NOAA", "Copernicus", "WMO", "climate science"],
        "source_label": "Ocean heat public record",
        "reader_note": "The rail cards link to scientific agencies, observing systems, and climate records. No generated card is presented as a real social post or field photograph.",
        "source_intro": "Climate-agency reports, ocean observing systems, coral-reef monitoring, and assessment reports used to check the ocean-heat claims in this story.",
        "built_note": "Built from WMO, Copernicus, NOAA, NASA, IPCC, Argo, coral-monitoring, and international reef-assessment sources.",
        "interactive": {
            "summary": "Try the thermometer test",
            "body": "If a single hot day does not define climate, a single cool day does not erase it. Ocean heat content matters because the ocean stores the long memory of the energy imbalance, smoothing the noise that can distract us at the surface.",
        },
        "key_points": [
            "The ocean absorbs most excess heat trapped by greenhouse gases.",
            "Coral bleaching is one of the most visible biological alarms of marine heat.",
            "Argo floats, satellites, buoys, and ships now make ocean heat measurable at global scale.",
            "Ocean warming affects storms, rain, sea level, fisheries, and coastal economies.",
        ],
        "sources": [
            {"id": "wmo-2024", "outlet": "World Meteorological Organization", "title": "State of the Global Climate 2024", "url": "https://wmo.int/publication-series/state-of-global-climate-2024", "role": "official", "label": "Climate report", "card_title": "Ocean heat at record levels", "note": "WMO's global climate report is a central source for ocean heat and climate indicators.", "why": "Used for record ocean heat and global climate context."},
            {"id": "copernicus", "outlet": "Copernicus Climate Change Service", "title": "Global Climate Highlights 2024", "url": "https://climate.copernicus.eu/global-climate-highlights-2024", "role": "official", "label": "Climate data", "card_title": "The surface signal is unmistakable", "note": "Copernicus provides global temperature and ocean-surface context.", "why": "Used for recent global climate and sea-surface temperature context."},
            {"id": "noaa-bleaching", "outlet": "NOAA", "title": "NOAA confirms fourth global coral bleaching event", "url": "https://www.nesdis.noaa.gov/news/noaa-confirms-fourth-global-coral-bleaching-event", "role": "official", "label": "Coral alert", "card_title": "The reef alarm went global", "note": "NOAA's bleaching announcement anchors the coral section.", "why": "Used to describe the global coral bleaching event."},
            {"id": "coral-watch", "outlet": "NOAA Coral Reef Watch", "title": "Coral Reef Watch", "url": "https://coralreefwatch.noaa.gov/", "role": "data", "label": "Monitoring", "card_title": "Bleaching can be tracked", "note": "Coral Reef Watch gives near-real-time satellite monitoring of heat stress.", "why": "Used for the monitoring architecture behind reef alerts."},
            {"id": "argo", "outlet": "Argo", "title": "Global Ocean Observing System", "url": "https://argo.ucsd.edu/", "role": "research", "label": "Ocean floats", "card_title": "Thousands of floats take the ocean's pulse", "note": "The Argo program shows how heat is measured below the surface.", "why": "Used to explain subsurface ocean observation."},
            {"id": "nasa-ocean", "outlet": "NASA", "title": "Vital Signs: Ocean Warming", "url": "https://climate.nasa.gov/vital-signs/ocean-warming/", "role": "official", "label": "Vital sign", "card_title": "The ocean stores the heat", "note": "NASA explains why ocean heat content is a core climate indicator.", "why": "Used for the basic physics of ocean heat storage."},
            {"id": "ipcc-srocc", "outlet": "IPCC", "title": "Special Report on the Ocean and Cryosphere in a Changing Climate", "url": "https://www.ipcc.ch/srocc/", "role": "research", "label": "Assessment", "card_title": "The ocean and ice are linked", "note": "IPCC assessment material connects ocean warming, sea level, ecosystems, and risk.", "why": "Used for assessed science on ocean and cryosphere changes."},
            {"id": "gcrmn", "outlet": "Global Coral Reef Monitoring Network", "title": "Status of Coral Reefs of the World", "url": "https://gcrmn.net/2020-report/", "role": "research", "label": "Reef report", "card_title": "Reefs have a long record", "note": "The reef network provides global context beyond any single bleaching event.", "why": "Used for long-run coral reef status and monitoring context."},
            {"id": "unesco-ocean", "outlet": "UNESCO IOC", "title": "State of the Ocean Report", "url": "https://oceanexpert.org/document/34586", "role": "research", "label": "Ocean report", "card_title": "Observation is the story", "note": "UNESCO's ocean reporting emphasizes measurement, observation, and policy relevance.", "why": "Used for the observing-system frame."},
            {"id": "noaa-marine-heatwave", "outlet": "NOAA", "title": "Marine Heatwaves", "url": "https://www.climate.gov/news-features/understanding-climate/climate-change-ocean-heat-content", "role": "data", "label": "Explainer", "card_title": "Heat waves happen at sea too", "note": "NOAA climate explainers help translate ocean heat for readers.", "why": "Used for accessible explanation of ocean heat content."},
            {"id": "sea-level", "outlet": "NASA Sea Level Change Team", "title": "Sea Level Change", "url": "https://sealevel.nasa.gov/", "role": "official", "label": "Sea level", "card_title": "Heat expands the sea", "note": "NASA's sea-level portal connects ocean heat, ice melt, and coastal risk.", "why": "Used for sea-level context tied to ocean warming."},
        ],
        "beats": [
            {"id": "a-fever-with-depth", "title": "A fever with depth", "sources": ["wmo-2024", "nasa-ocean", "argo", "copernicus"], "lede": "Ocean heat is easy to misunderstand because the ocean hides its own drama. The surface can look calm while enormous amounts of energy move through layers most people will never see.", "fact": "WMO, NASA, Copernicus, and Argo all describe the same basic reality: the ocean is the planet's great heat reservoir, and modern observation now measures that heat from the surface into the deep water column.", "meaning": "That matters because air temperature is the noisy headline, while ocean heat content is the long account book. The ocean records what the planet has absorbed even when weather distracts us.", "tension": "The danger is not only warmer beaches. It is the stored energy that changes storms, marine ecosystems, sea level, oxygen, fisheries, and the timing of life in the water.", "human": "For coastal communities, the fever can arrive as a flood tide, a dead reef, a closed fishery, a stronger downpour, or a summer when the water itself feels wrong.", "future": "The more the ocean stores, the less the problem can be dismissed as a bad season. A fever with depth is harder to cool."},
            {"id": "coral-is-the-alarm", "title": "Coral is the alarm that changes color", "sources": ["noaa-bleaching", "coral-watch", "gcrmn", "copernicus"], "lede": "Coral bleaching is one of climate science's cruelest visual aids. The animal does not shout. It pales, losing the symbiotic algae that help feed it when heat stress lasts too long.", "fact": "NOAA's confirmation of the fourth global bleaching event and Coral Reef Watch's satellite heat-stress tools show how reef crisis moved from local observation into global monitoring.", "meaning": "The power of the bleaching signal is that it is biological and visible. A reef can translate ocean heat faster than a chart can, because the change is written on living color.", "tension": "Bleaching does not automatically mean death, but repeated or prolonged heat leaves less time for recovery and more room for algae, disease, and reef breakdown.", "human": "A reef is food, shoreline protection, tourism, cultural identity, and astonishing life. When it pales, the loss is ecological before it becomes economic, but it becomes economic quickly.", "future": "The reef alarm is not subtle. It is asking whether the world can reduce heat stress fast enough for recovery to remain a real word."},
            {"id": "the-thermometer-network", "title": "The thermometer is a network", "sources": ["argo", "unesco-ocean", "nasa-ocean", "ipcc-srocc"], "lede": "There is no single thermometer for the sea. There are floats, satellites, tide gauges, buoys, ships, gliders, moorings, and scientists arguing carefully about uncertainty.", "fact": "Argo's global float array, NASA's climate indicators, UNESCO ocean reporting, and IPCC assessments show how measurement has become an infrastructure story as much as a science story.", "meaning": "This is why ocean heat is not just a vibe from a hot beach. It is a measured, checked, repeated signal produced by instruments that move through the water and systems that read from above.", "tension": "Observation still has gaps. The deep ocean, polar regions, coastal shelves, and biological effects are hard to measure perfectly, which means better data can change details without changing the main direction.", "human": "The public rarely sees the float that surfaced, sent a burst of data, and sank again. But that quiet machine is part of the reason the story can be told with confidence.", "future": "The next breakthrough may be less spectacular than a new satellite launch. It may be the steady thickening of an observing network that makes the ocean harder to ignore."},
            {"id": "storm-fuel", "title": "Warm water is storm fuel, not a storm script", "sources": ["wmo-2024", "noaa-marine-heatwave", "ipcc-srocc", "sea-level"], "lede": "It is too simple to say a warm ocean creates every storm. Weather is not a vending machine. But warm water changes the conditions under which storms form, intensify, rain, and damage coasts.", "fact": "Climate assessments and NOAA explainers connect ocean heat with evaporation, moisture, marine heat waves, sea level, and the physical background against which storms operate.", "meaning": "That distinction matters. Climate change is not always the single cause of an event; it is often the loaded setting that makes some outcomes more likely, more intense, or more costly.", "tension": "The public wants yes-or-no attribution because disasters demand moral clarity. Science often answers with probability, intensity, and contribution, which can sound softer than it is.", "human": "A family facing a flooded living room does not care whether the ocean supplied exactly this many percent of the rain. The water on the floor is the proof that background conditions matter.", "future": "The better question is not whether the ocean wrote the whole storm. It is how much extra ink warm water gave the storm to write with."},
            {"id": "fisheries-feel-it", "title": "Fisheries feel the heat before dinner does", "sources": ["ipcc-srocc", "wmo-2024", "unesco-ocean", "noaa-marine-heatwave"], "lede": "Marine heat does not stay politely inside graphs. It moves through plankton blooms, fish migration, oxygen levels, disease pressure, shellfish stress, and the timing of work for people who fish for a living.", "fact": "The IPCC ocean assessment and international ocean reports describe changes in marine ecosystems, while NOAA's climate material explains how ocean heat affects the physical environment that species depend on.", "meaning": "The dinner plate is the last page of a long story. Before a price changes in a market, something already changed in spawning, distribution, fuel use, quota planning, or the distance a boat had to travel.", "tension": "Some species may move into new waters while others decline, which makes the politics complicated. A gain for one port can be a crisis for another.", "human": "Fishing communities know that a map of species is also a map of identity. When the fish move, the paperwork follows, but the memory of the old grounds does not move as easily.", "future": "The ocean's fever will force fisheries management to become more flexible without becoming careless, and that is a harder assignment than simply drawing new lines."},
            {"id": "sea-level-memory", "title": "Sea level is ocean heat with a long memory", "sources": ["sea-level", "ipcc-srocc", "wmo-2024", "nasa-ocean"], "lede": "Sea level is often described as water rising, but part of the story is water expanding. Heat makes seawater take up more space, while land ice loss adds more water to the system.", "fact": "NASA's sea-level work, WMO reporting, NASA ocean-warming indicators, and IPCC assessment material connect thermal expansion, ice loss, coastal risk, and long-term change.", "meaning": "The result is a delayed consequence. Even if emissions slowed sharply, some ocean and ice responses would keep unfolding because the system has already stored heat.", "tension": "That delay can make action feel unrewarding. Coastal adaptation is expensive now, while the avoided damage is partly measured in future disasters that do not happen.", "human": "For a mayor, the problem can be a road that floods on sunny days. For a homeowner, it can be a mortgage term longer than the protective life of a seawall.", "future": "Sea level teaches the same lesson as ocean heat: the slow part of climate can still be urgent if the infrastructure in its path was built for a different ocean."},
            {"id": "marine-heat-waves", "title": "Marine heat waves are changing the weather underwater", "sources": ["copernicus", "noaa-marine-heatwave", "coral-watch", "gcrmn"], "lede": "A heat wave at sea sounds abstract until it kills kelp, stresses coral, scatters fish, or helps set up a season of strange coastal weather. The water has its own extreme events.", "fact": "Copernicus records, NOAA ocean explainers, Coral Reef Watch, and reef-monitoring sources show that marine heat can be monitored as a recurring pattern, not an anecdote.", "meaning": "That makes the phrase marine heat wave important. It gives the ocean version of extreme heat a public name and a measurable shape.", "tension": "The hard part is that underwater extremes do not always produce immediate images. There may be no viral clip when a kelp forest begins to fail.", "human": "Divers, fishers, surfers, island communities, and reef guides notice when the water feels off, but the instruments show whether that local feeling belongs to a larger pattern.", "future": "As marine heat waves become more visible in data, the public may finally learn to treat ocean weather as part of climate news, not scenery behind it."},
            {"id": "what-the-fever-asks", "title": "What the fever asks of us", "sources": ["wmo-2024", "ipcc-srocc", "unesco-ocean", "argo"], "lede": "The ocean has carried human excess with astonishing patience. That patience has sometimes made the problem look smaller than it is, because the heat disappeared from the air and entered the water.", "fact": "The major observing and assessment sources agree on the direction of travel: the ocean is warming, the signs are measurable, and the consequences reach from reefs to coasts to weather systems.", "meaning": "The story is not only catastrophe. It is also a triumph of measurement. Humanity built a way to hear the ocean more clearly just as the message became harder to avoid.", "tension": "Measurement, however, is not treatment. A fever chart is useful because it tells you the patient is sick; it does not lower the temperature by itself.", "human": "Readers do not need to become oceanographers to understand the stakes. They only need to know that the blue part of the map is not empty. It is absorbing the heat of our choices.", "future": "The ocean's fever asks for two kinds of seriousness: cut the heat going in, and prepare for the heat already stored."},
        ],
    },
    {
        "slug": "technology-the-battery-is-becoming-the-grid",
        "filename": "technology-the-battery-is-becoming-the-grid.html",
        "title": "The Battery Is Becoming the Grid",
        "section": "Technology",
        "sectionSlug": "technology",
        "type": "Analysis",
        "author": "Julian Mercado",
        "authorSlug": "julian-mercado",
        "authorRole": "Technology & Industry Correspondent",
        "publishedLabel": "May 7, 2026 • 11:20 a.m. EDT",
        "updatedLabel": "May 7, 2026 • 11:20 a.m. EDT",
        "publishedIso": "2026-05-07T11:20:00-04:00",
        "updatedIso": "2026-05-07T11:20:00-04:00",
        "dek": "Grid batteries, electric cars, lithium supply chains, virtual power plants, and interconnection queues are turning storage from a gadget story into the shock absorber of the power system.",
        "excerpt": "The battery story is no longer only about phones or cars. It is about evening peaks, grid queues, backup power, critical minerals, and who gets paid for flexibility.",
        "image": "assets/technology-battery-grid-thumbnail.png",
        "imageAlt": "AI-generated photorealistic editorial image of a grid-scale battery storage site under transmission lines at dusk.",
        "imageCaptionHtml": "AI-generated photorealistic editorial image for The Press showing utility-scale battery storage. It is not a documentary photograph of a specific facility.",
        "imageCreditPlain": "AI-generated photorealistic editorial image. Not a documentary photograph.",
        "keywords": ["battery storage", "grid", "virtual power plants", "EVs", "lithium", "interconnection", "CAISO", "EIA"],
        "source_label": "Battery grid public record",
        "reader_note": "The source rail links to energy agencies, labs, grid operators, and policy reports. Cards are clickable source summaries, not fake platform posts.",
        "source_intro": "Energy-agency, lab, grid-operator, and policy sources used to check the battery and grid-storage claims in this story.",
        "built_note": "Built from IEA, EIA, NREL, DOE, CAISO, Berkeley Lab, RMI, and California public-energy records.",
        "interactive": {
            "summary": "Try the duck curve test",
            "body": "If solar floods the grid at midday but demand peaks after sunset, storage becomes a timing machine. It does not create sunlight at night; it moves some of the value of daylight into the hour when people cook dinner and turn lights on.",
        },
        "key_points": [
            "Battery storage is shifting from clean-energy accessory to reliability infrastructure.",
            "The value of a battery is timing: absorb power when it is plentiful and release it when the grid is tight.",
            "EVs, home batteries, and virtual power plants could become distributed grid resources.",
            "Interconnection queues, minerals, recycling, fire safety, and market rules now decide how fast storage scales.",
        ],
        "sources": [
            {"id": "iea-batteries", "outlet": "International Energy Agency", "title": "Batteries and Secure Energy Transitions", "url": "https://www.iea.org/reports/batteries-and-secure-energy-transitions", "role": "research", "label": "Global report", "card_title": "Batteries moved to the center", "note": "IEA frames batteries as central to secure energy transitions.", "why": "Used for global battery deployment, cost, and supply-chain context."},
            {"id": "eia-storage", "outlet": "U.S. Energy Information Administration", "title": "U.S. battery storage capacity has been growing since 2021", "url": "https://www.eia.gov/todayinenergy/detail.php?id=61202", "role": "data", "label": "U.S. data", "card_title": "The capacity curve is steep", "note": "EIA data shows rapid U.S. battery storage growth.", "why": "Used for U.S. grid-storage growth context."},
            {"id": "nrel-futures", "outlet": "NREL / OSTI", "title": "Storage Futures Study: Key Learnings for the Coming Decades", "url": "https://www.osti.gov/biblio/1863547", "role": "research", "label": "Grid study", "card_title": "Storage has multiple jobs", "note": "NREL's study explains how storage changes grid planning.", "why": "Used for storage roles across power systems."},
            {"id": "caiso", "outlet": "California ISO", "title": "Battery storage and grid transformation", "url": "https://www.caiso.com/about/our-business/managing-the-evolving-grid", "role": "official", "label": "Grid operator", "card_title": "California is the live lab", "note": "CAISO's public material explains storage in the evolving grid.", "why": "Used for grid-operator context on storage and reliability."},
            {"id": "doe-gsl", "outlet": "U.S. Department of Energy", "title": "Grid Storage Launchpad", "url": "https://www.energy.gov/oe/grid-storage-launchpad", "role": "official", "label": "Research facility", "card_title": "Storage needs public R&D", "note": "DOE's launchpad shows the federal research layer behind better storage.", "why": "Used for grid-storage research infrastructure."},
            {"id": "doe-blueprint", "outlet": "U.S. Department of Energy", "title": "National Blueprint for Lithium Batteries", "url": "https://www.energy.gov/eere/vehicles/articles/national-blueprint-lithium-batteries", "role": "policy", "label": "Supply chain", "card_title": "The supply chain is strategic", "note": "The DOE blueprint frames batteries as manufacturing and security infrastructure.", "why": "Used for lithium battery supply-chain strategy."},
            {"id": "lbl-queue", "outlet": "Lawrence Berkeley National Laboratory", "title": "Queued Up: 2024 Edition", "url": "https://eta.lbl.gov/publications/queued-2024-edition-characteristics", "role": "data", "label": "Interconnection", "card_title": "The queue is a bottleneck", "note": "Berkeley Lab's queue work explains how projects wait for grid connection.", "why": "Used for interconnection bottleneck context."},
            {"id": "rmi-vpp", "outlet": "RMI", "title": "Virtual Power Plants, Real Benefits", "url": "https://rmi.org/insight/virtual-power-plants-real-benefits/", "role": "research", "label": "VPP report", "card_title": "Small devices can act big", "note": "RMI explains how aggregated devices can provide grid value.", "why": "Used for virtual power plant discussion."},
            {"id": "cec", "outlet": "California Energy Commission", "title": "California Energy Almanac", "url": "https://www.energy.ca.gov/data-reports/energy-almanac", "role": "data", "label": "State data", "card_title": "Storage is now a state resource", "note": "California public data shows installed capacity and storage growth.", "why": "Used for state-scale storage context."},
            {"id": "epa-v2g", "outlet": "U.S. EPA", "title": "Electric Vehicle Myths", "url": "https://www.epa.gov/greenvehicles/electric-vehicle-myths", "role": "official", "label": "EV context", "card_title": "EVs are part of grid politics", "note": "EPA's consumer-facing EV material helps ground the vehicle side of the battery story.", "why": "Used for accessible EV context."},
            {"id": "doe-recycling", "outlet": "Argonne National Laboratory", "title": "DOE launches its first lithium-ion battery recycling R&D center: ReCell", "url": "https://www.anl.gov/article/doe-launches-its-first-lithiumion-battery-recycling-rd-center-recell", "role": "research", "label": "Recycling", "card_title": "The battery afterlife matters", "note": "ReCell gives the recycling and materials-recovery side of the story.", "why": "Used for battery recycling and circular supply-chain context."},
        ],
        "beats": [
            {"id": "not-a-gadget", "title": "This is not a gadget story anymore", "sources": ["iea-batteries", "eia-storage", "nrel-futures", "caiso"], "lede": "For years, batteries were marketed as personal technology: the thing that made a phone last, an electric car move, or a laptop survive a flight. The bigger story now sits behind fences.", "fact": "IEA, EIA, NREL, and CAISO sources show storage moving into the power system as infrastructure, not accessory. Grid-scale batteries are being planned, queued, dispatched, and studied like power plants with a different personality.", "meaning": "A battery does not mine fuel or spin like a turbine. Its value is timing. It absorbs power when the grid has enough and returns it when the grid is tense.", "tension": "That makes storage look magical until the limits appear: duration, location, interconnection, degradation, cost, fire safety, and market rules.", "human": "The customer experiences the result as fewer outages, lower peak stress, cleaner evening power, or a rate plan that suddenly cares when the dishwasher runs.", "future": "The battery is becoming the grid's shock absorber, and shock absorbers matter most when the road gets rough."},
            {"id": "the-evening-problem", "title": "The evening is the test", "sources": ["caiso", "cec", "nrel-futures", "eia-storage"], "lede": "Solar power changed the middle of the day. Batteries are changing the hour after it. The system's hardest question is often what happens when sunlight fades and people come home.", "fact": "California's grid and energy data, EIA storage reporting, and NREL planning work all show why batteries are valuable in systems with large solar output and sharp evening demand.", "meaning": "Storage turns some daytime abundance into evening reliability. It does not eliminate the need for transmission, generation, demand flexibility, or careful planning, but it changes the shape of the problem.", "tension": "The public likes clean power in theory and expects the lights to work in practice. Batteries are one way those expectations meet, but they are not an excuse to ignore the rest of the grid.", "human": "The evening peak is ordinary life: dinner, homework, laundry, television, heat, cooling, and the small rituals that turn electrical demand into a household pulse.", "future": "If the battery revolution works, the most dramatic proof may be a boring evening when nothing fails."},
            {"id": "the-queue", "title": "The queue is where ambition waits", "sources": ["lbl-queue", "doe-gsl", "nrel-futures", "iea-batteries"], "lede": "Announcing a storage project is not the same as connecting it. The grid has gates, studies, upgrades, permits, and timelines that can turn ambition into a waiting room.", "fact": "Berkeley Lab's interconnection queue work, DOE storage research, NREL planning studies, and IEA analysis all point to the same constraint: batteries need wires, rules, and places to plug in.", "meaning": "This is where clean-energy optimism becomes infrastructure administration. The project that looks elegant in a chart still has to get through the physics and paperwork of a local grid.", "tension": "Fast battery cost declines can collide with slow grid connection. Capital wants speed; substations and transmission upgrades often move at the pace of steel, hearings, and engineering studies.", "human": "A community may see a field, a fence, and container boxes. Behind that image sits a queue position, a utility study, a fire plan, and a contract that decides whether the project is real.", "future": "The country will not build the storage future by celebrating batteries alone. It has to fix the queue where good projects go to age."},
            {"id": "evs-as-grid", "title": "The car in the driveway is part of the argument", "sources": ["epa-v2g", "rmi-vpp", "doe-blueprint", "iea-batteries"], "lede": "Electric cars are usually discussed as transportation. But every EV is also a battery with wheels, a charger, a schedule, and a potential relationship with the grid.", "fact": "EPA's EV material, RMI's virtual power plant work, DOE's battery blueprint, and IEA's battery report all show why the vehicle fleet matters beyond tailpipe emissions.", "meaning": "The most important question may be when cars charge, not simply how many exist. A million vehicles charging at the wrong hour can stress a system; managed charging can help one.", "tension": "Vehicle-to-grid dreams run into warranties, customer trust, charger standards, software, compensation, and the basic fact that people bought a car to use it, not to become unpaid grid infrastructure.", "human": "A driver does not want an energy seminar at the end of a workday. They want a charged car. The grid value has to fit inside that expectation.", "future": "The EV will become a serious grid resource only when the deal is simple enough for ordinary people to accept without becoming power-market specialists."},
            {"id": "virtual-power-plants", "title": "A million small batteries can behave like one big plant", "sources": ["rmi-vpp", "nrel-futures", "caiso", "doe-gsl"], "lede": "The old grid imagined big plants pushing electricity outward. The newer grid also imagines homes, cars, thermostats, water heaters, and batteries responding together.", "fact": "RMI's virtual power plant work and public grid-planning sources explain how aggregation can turn distributed devices into a resource that reduces peak demand or provides grid services.", "meaning": "This is not just a technical trick. It is a new social contract. Customers give the grid a little flexibility, and the system gives them money, resilience, or lower costs in return.", "tension": "Aggregation fails if people feel tricked. It succeeds when the rule is clear, the override works, the payment is visible, and the device still does its main job.", "human": "A thermostat setback or battery dispatch can sound small. Multiply it by thousands of homes during a peak hour and the small thing becomes a power plant made of permission.", "future": "The next grid may be built as much from consent and software as from concrete and steel."},
            {"id": "minerals-and-recycling", "title": "The battery has a supply chain shadow", "sources": ["doe-blueprint", "doe-recycling", "iea-batteries", "epa-v2g"], "lede": "No battery is weightless. Lithium, nickel, cobalt, graphite, copper, manufacturing energy, transport, recycling, and labor all sit behind the clean rectangle installed at a site or sealed inside a car.", "fact": "DOE's lithium battery blueprint, Argonne's ReCell work, IEA's battery report, and EV public materials show why the battery boom is also a mining, manufacturing, and recycling story.", "meaning": "The supply chain matters because a clean-energy technology can still create dirty politics if materials are extracted badly or wasted after use.", "tension": "The answer is not to reject batteries because they require materials. The answer is to build better sourcing, chemistry, recycling, and reuse so the material intensity falls over time.", "human": "A consumer may never see the mine or recycling line. But those places decide whether the battery economy becomes more circular or simply repeats the oldest habits of extraction.", "future": "The grid battery's afterlife may become as important as its first dispatch."},
            {"id": "fire-and-trust", "title": "Fire safety is not a footnote", "sources": ["nrel-futures", "doe-gsl", "cec", "caiso"], "lede": "A battery project can lose public trust quickly if safety is treated as a communications problem instead of an engineering and emergency-response problem.", "fact": "Storage planning sources, DOE research infrastructure, California data, and grid-operator material show how storage is moving into real communities, which means siting and safety have to be legible.", "meaning": "Battery fires are not the whole story, but they are part of the story. A technology that serves the public has to explain failure modes before opponents define them alone.", "tension": "Communities can be both reasonable and afraid. Developers can be both technically correct and politically clumsy. The solution is not to wave away concern; it is to earn trust with design, spacing, monitoring, and response plans.", "human": "A fire chief should not learn the technology from a sales deck after the project is approved. Local responders need knowledge before the sirens.", "future": "Storage will scale faster if safety is designed into the public conversation from the first neighborhood meeting."},
            {"id": "the-grid-after-batteries", "title": "The grid after batteries is still a grid", "sources": ["iea-batteries", "lbl-queue", "rmi-vpp", "caiso"], "lede": "Batteries are powerful, but they are not a substitute for every part of the electricity system. A good battery story should make the grid more visible, not less.", "fact": "The source record across IEA, Berkeley Lab, RMI, and CAISO shows storage as one piece of a larger system involving transmission, generation, demand response, markets, customers, and operations.", "meaning": "That is the mature view. Storage can smooth, shift, stabilize, and substitute in some moments. It cannot erase geography, politics, or the need to build other infrastructure.", "tension": "The danger is a new hype cycle in which every hard problem is promised a battery-shaped answer. The better story is more interesting: batteries give planners a new verb, but not a new universe.", "human": "A reliable grid is rarely loved when it works. It is noticed when it fails. Batteries are joining the group of technologies whose highest public achievement may be anonymity.", "future": "The battery is becoming the grid, but only if the grid becomes smart enough to use it well."},
        ],
    },
    {
        "slug": "health-the-next-public-health-system-is-the-room-you-are-in",
        "filename": "health-the-next-public-health-system-is-the-room-you-are-in.html",
        "title": "The Next Public-Health System Is the Room You Are In",
        "section": "Health",
        "sectionSlug": "health",
        "type": "Report",
        "author": "Ruth Alvarez",
        "authorSlug": "ruth-alvarez",
        "authorRole": "Health Correspondent",
        "publishedLabel": "May 7, 2026 • 12:30 p.m. EDT",
        "updatedLabel": "May 7, 2026 • 12:30 p.m. EDT",
        "publishedIso": "2026-05-07T12:30:00-04:00",
        "updatedIso": "2026-05-07T12:30:00-04:00",
        "dek": "Ventilation, filtration, humidity, CO2 monitoring, wildfire smoke, infectious aerosols, and heat are turning buildings into the front line of everyday public health.",
        "excerpt": "Public health does not stop at the clinic door. It lives in classrooms, offices, buses, hospitals, apartments, vents, filters, and the invisible air people share.",
        "image": "assets/health-indoor-air-thumbnail.png",
        "imageAlt": "AI-generated photorealistic editorial image of a school or hospital corridor with visible ventilation, a portable air filter, and a small air-quality monitor.",
        "imageCaptionHtml": "AI-generated photorealistic editorial image for The Press showing indoor-air infrastructure. It is not a documentary photograph of a specific school or hospital.",
        "imageCreditPlain": "AI-generated photorealistic editorial image. Not a documentary photograph.",
        "keywords": ["indoor air", "ventilation", "filtration", "ASHRAE 241", "CDC", "EPA", "public health", "schools"],
        "source_label": "Indoor air public-health record",
        "reader_note": "The side rail links to health agencies, standards groups, and building guidance. It is designed to make invisible infrastructure easy to inspect.",
        "source_intro": "Public-health, building-standard, school-air-quality, and ventilation sources used to check the claims in this story.",
        "built_note": "Built from CDC, ASHRAE, EPA, WHO, National Academies, Harvard Healthy Buildings, OSHA, and related indoor-air/public-health sources.",
        "interactive": {
            "summary": "Room test: what would you check first?",
            "body": "Start with whether outdoor air is being supplied, whether filters are appropriate and maintained, whether portable filtration is needed, and whether a simple CO2 reading suggests the room is not clearing exhaled air well during occupancy.",
        },
        "key_points": [
            "Buildings shape exposure to infectious aerosols, smoke, heat, and everyday pollutants.",
            "Ventilation and filtration are public-health tools, not only engineering features.",
            "CO2 monitors can help reveal whether a crowded room is clearing exhaled air poorly.",
            "The hardest part is maintenance: filters, budgets, standards, staffing, and accountability.",
        ],
        "sources": [
            {"id": "cdc-air", "outlet": "CDC", "title": "Improving Ventilation in Buildings", "url": "https://www.cdc.gov/niosh/ventilation/about/index.html", "role": "official", "label": "Health guidance", "card_title": "Ventilation is prevention", "note": "CDC/NIOSH guidance grounds the building-health discussion.", "why": "Used for ventilation as a respiratory-risk reduction tool."},
            {"id": "cdc-respiratory", "outlet": "CDC", "title": "Preventing Respiratory Viruses: Air Quality", "url": "https://www.cdc.gov/respiratory-viruses/prevention/air-quality.html", "role": "official", "label": "Respiratory viruses", "card_title": "Cleaner air lowers risk", "note": "CDC gives public-facing guidance on air quality and respiratory viruses.", "why": "Used for infectious-disease prevention context."},
            {"id": "ashrae241", "outlet": "ASHRAE", "title": "Standard 241: Control of Infectious Aerosols", "url": "https://www.ashrae.org/technical-resources/bookstore/ashrae-standard-241-control-of-infectious-aerosols", "role": "policy", "label": "Building standard", "card_title": "A standard for infectious aerosols", "note": "ASHRAE 241 is the key building-standard source.", "why": "Used for the building-standard turn in infectious aerosol control."},
            {"id": "epa-schools", "outlet": "EPA", "title": "Indoor Air Quality Tools for Schools", "url": "https://www.epa.gov/iaq-schools", "role": "official", "label": "Schools", "card_title": "Schools are air systems", "note": "EPA's school IAQ program helps translate ventilation into education settings.", "why": "Used for school indoor-air quality context."},
            {"id": "epa-clean-air", "outlet": "EPA", "title": "Clean Air in Buildings Challenge", "url": "https://www.epa.gov/newsreleases/epa-announces-clean-air-buildings-challenge-help-building-owners-and-operators-improve", "role": "official", "label": "Building challenge", "card_title": "A public challenge for clean air", "note": "EPA's challenge outlines practical clean-air actions.", "why": "Used for building-level mitigation steps."},
            {"id": "who-ventilation", "outlet": "World Health Organization", "title": "Roadmap to improve and ensure good indoor ventilation", "url": "https://www.who.int/publications/i/item/9789240021280", "role": "official", "label": "WHO roadmap", "card_title": "Ventilation is global health", "note": "WHO's roadmap frames ventilation as health infrastructure.", "why": "Used for global public-health guidance."},
            {"id": "nap", "outlet": "National Academies", "title": "Airborne Transmission of SARS-CoV-2", "url": "https://nap.nationalacademies.org/catalog/27144/airborne-transmission-of-sars-cov-2", "role": "research", "label": "Science review", "card_title": "The air pathway matters", "note": "National Academies material supports the airborne-transmission frame.", "why": "Used for the science of airborne transmission."},
            {"id": "healthy-buildings", "outlet": "Harvard Healthy Buildings", "title": "Schools for Health", "url": "https://schools.forhealth.org/", "role": "research", "label": "School health", "card_title": "Classrooms are health environments", "note": "Healthy Buildings work links school buildings and health.", "why": "Used for school-building health context."},
            {"id": "osha-heat", "outlet": "OSHA", "title": "Heat Injury and Illness Prevention Rulemaking", "url": "https://www.osha.gov/heat-exposure/rulemaking", "role": "policy", "label": "Heat rule", "card_title": "Heat is also an indoor-air story", "note": "OSHA heat rulemaking provides workplace heat context.", "why": "Used to connect indoor environments to heat exposure."},
            {"id": "arpa-breathe", "outlet": "ARPA-H", "title": "BREATHE Program", "url": "https://arpa-h.gov/research-and-funding/programs/breathe", "role": "research", "label": "Research program", "card_title": "Air tech is now health tech", "note": "ARPA-H's BREATHE program shows federal interest in better indoor-air technologies.", "why": "Used for innovation and public-health technology context."},
        ],
        "beats": [
            {"id": "the-room-is-a-system", "title": "The room is a system", "sources": ["cdc-air", "cdc-respiratory", "ashrae241", "epa-clean-air"], "lede": "Public health often arrives in the public mind as a person: a doctor, a nurse, a patient, a mask, a vaccine line. But much of it is a room.", "fact": "CDC ventilation guidance, respiratory-virus air-quality advice, ASHRAE 241, and EPA's clean-air challenge all treat indoor air as a modifiable health environment rather than a neutral background.", "meaning": "That shift is simple and enormous. It says disease risk is not only carried by bodies; it is shaped by the space those bodies share.", "tension": "The problem is that air infrastructure is invisible when it works and expensive when it fails. Nobody applauds a filter that prevented an outbreak no one can see.", "human": "A classroom, clinic, office, bus, or apartment is not just a container. It is a respiratory commons, and everyone in it participates whether they know it or not.", "future": "The next public-health system will have ducts, sensors, filters, maintenance logs, and budgets."},
            {"id": "ventilation-is-not-vibes", "title": "Ventilation is not vibes", "sources": ["who-ventilation", "cdc-air", "ashrae241", "epa-schools"], "lede": "Opening a window feels intuitive, but ventilation is not a mood. It is a measurable exchange between stale indoor air and cleaner air from outside or through treatment.", "fact": "WHO, CDC, ASHRAE, and EPA sources all describe ventilation and filtration as practical controls that require design, operation, and maintenance.", "meaning": "The reader-friendly translation is this: air should not simply sit in a crowded room collecting what people exhale. It should be diluted, filtered, exhausted, or cleaned.", "tension": "The difficulty is that one building's solution may not fit another. Outdoor pollution, wildfire smoke, weather, old HVAC systems, and energy costs can all change the right answer.", "human": "A teacher should not have to become a mechanical engineer to know whether the room is safe enough. The system should make the answer visible.", "future": "Public buildings need clean-air standards that survive the end of an emergency and become ordinary operations."},
            {"id": "co2-is-a-clue", "title": "CO2 is a clue, not a verdict", "sources": ["epa-clean-air", "healthy-buildings", "who-ventilation", "cdc-respiratory"], "lede": "Carbon dioxide monitors became a small obsession for people who started wondering what exactly they were breathing in crowded rooms. The device is not magic, but it is useful.", "fact": "Building-health guidance uses CO2 as an indicator of how much exhaled air is accumulating indoors, while emphasizing that CO2 is not itself a direct measure of infection risk.", "meaning": "That distinction matters because a simple number can empower or mislead. A high reading says the room may not be clearing air well. It does not identify who is contagious or what pathogen is present.", "tension": "The best public use of CO2 is humble: treat it as a smoke alarm for ventilation attention, not as a perfect health score.", "human": "A monitor on a classroom shelf can make the invisible a little less invisible. It gives students, teachers, and parents a way to ask better questions.", "future": "The future of indoor health may include cheap sensors, but sensors matter only when someone is responsible for responding to them."},
            {"id": "filtration-is-work", "title": "Filtration is work", "sources": ["epa-schools", "epa-clean-air", "cdc-air", "arpa-breathe"], "lede": "A filter is a promise that must be replaced. That sounds dull because it is dull, and that is exactly why it belongs in public health.", "fact": "EPA school guidance, CDC ventilation material, EPA's clean-air challenge, and ARPA-H research all point toward filtration as a practical way to reduce exposure when installed and maintained correctly.", "meaning": "The technology is only part of the story. The bigger part is procurement, sizing, noise, placement, maintenance, and the annual budget line that keeps the filter from becoming decorative plastic.", "tension": "Many institutions love capital projects and neglect maintenance. Clean air punishes that habit because dirty filters, blocked vents, and ignored devices quietly erase the benefit.", "human": "The person who changes the filter is part of the public-health workforce, whether or not the job title says so.", "future": "If clean air becomes a serious promise, facilities staff will need the respect and resources that serious promises require."},
            {"id": "wildfire-smoke-moves-indoors", "title": "Wildfire smoke moves indoors", "sources": ["epa-clean-air", "cdc-air", "who-ventilation", "osha-heat"], "lede": "The indoor-air story is not only about viruses. Wildfire smoke has taught many Americans that outside air can become dangerous and that buildings vary wildly in how well they protect the people inside.", "fact": "EPA, CDC, WHO, and workplace-health sources frame indoor air as a defense against multiple hazards, including particles from smoke and heat stress that can move through buildings and workplaces.", "meaning": "That broadens the argument. A building that can filter air during a respiratory surge may also help during smoke days. A building that handles heat well may protect workers and students before illness starts.", "tension": "Ventilation and filtration can pull in opposite directions during smoke events. Bringing in more outdoor air is not always the right move if the outdoor air is hazardous.", "human": "A parent does not care whether the hazard is viral aerosol or smoke particle. They want the child in the room to breathe air that has been taken seriously.", "future": "Climate adaptation and infectious-disease prevention are going to meet in the same mechanical room."},
            {"id": "schools-are-the-test", "title": "Schools are the test of whether we mean it", "sources": ["epa-schools", "healthy-buildings", "cdc-respiratory", "ashrae241"], "lede": "Schools are where clean-air rhetoric becomes hard. They are crowded, underfunded, politically exposed, aging, emotionally important, and occupied by children who did not choose the building.", "fact": "EPA school IAQ tools, Healthy Buildings school work, CDC guidance, and ASHRAE standards all make the case that classrooms deserve serious air management.", "meaning": "The school lens strips away abstraction. If a society says children matter, it cannot treat the air in their classrooms as an afterthought.", "tension": "The difficulty is not knowing that better air helps. It is deciding who pays, who inspects, who maintains, and who explains the difference between a real upgrade and a press release.", "human": "A student trying to learn in a stuffy room is not experiencing a policy debate. They are experiencing the building directly, breath by breath.", "future": "The clean-air school day should be as basic as safe water, working lights, and doors that lock."},
            {"id": "hospitals-know-this-already", "title": "Hospitals know this already", "sources": ["cdc-air", "ashrae241", "nap", "arpa-breathe"], "lede": "Hospitals have always understood that air can be clinical. Isolation rooms, pressure differentials, filtration, and ventilation are part of the architecture of care.", "fact": "CDC, ASHRAE, National Academies, and ARPA-H sources show how infectious-aerosol science and building technology are converging on a broader public-health agenda.", "meaning": "The question now is how much of that seriousness can move beyond specialized health-care spaces into schools, offices, shelters, transportation, and homes.", "tension": "Not every room can become a hospital room, and it should not. But ordinary rooms can still be better than they are.", "human": "The leap from hospital engineering to daily life is not about panic. It is about learning from places that already know air can carry risk.", "future": "A mature society will not wait for the next outbreak to discover its vents."},
            {"id": "the-maintenance-democracy", "title": "The maintenance democracy", "sources": ["epa-clean-air", "who-ventilation", "osha-heat", "healthy-buildings"], "lede": "Clean indoor air is a democratic idea disguised as facility management. It protects people who may never know each other and may never agree on anything else.", "fact": "EPA, WHO, OSHA, and building-health sources all suggest that better indoor environments require routine practices, not just emergency purchases.", "meaning": "That is why the room is the public-health frontier. It turns prevention from a personal virtue into a shared condition.", "tension": "The hardest part is accountability. If a building's air is poor, who is responsible: the owner, the school board, the landlord, the employer, the regulator, the engineer, or everyone a little?", "human": "People should not have to buy private air cleaners for every room of public life. Public life should be built to breathe.", "future": "The next public-health victory may not look like a miracle drug. It may look like a maintenance schedule that nobody lets slide."},
        ],
    },
    {
        "slug": "education-the-phone-free-school-day-is-a-live-experiment",
        "filename": "education-the-phone-free-school-day-is-a-live-experiment.html",
        "title": "The Phone-Free School Day Is a Live Experiment",
        "section": "Education",
        "sectionSlug": "education",
        "type": "Feature",
        "author": "Lena Park",
        "authorSlug": "lena-park",
        "authorRole": "Education Correspondent",
        "publishedLabel": "May 7, 2026 • 1:40 p.m. EDT",
        "updatedLabel": "May 7, 2026 • 1:40 p.m. EDT",
        "publishedIso": "2026-05-07T13:40:00-04:00",
        "updatedIso": "2026-05-07T13:40:00-04:00",
        "dek": "As states and districts restrict student phones, schools are testing whether attention can be rebuilt by policy, culture, storage pouches, enforcement, and trust.",
        "excerpt": "The phone-free school day is not just a ban. It is an experiment in attention, belonging, discipline, emergency anxiety, teacher workload, and what school is for.",
        "image": "assets/education-phone-free-schools-thumbnail.png",
        "imageAlt": "AI-generated photorealistic editorial image of classroom phone pouches near a doorway with students blurred in the background.",
        "imageCaptionHtml": "AI-generated photorealistic editorial image for The Press showing a phone-free classroom setup. It is not a documentary photograph of a specific school.",
        "imageCreditPlain": "AI-generated photorealistic editorial image. Not a documentary photograph.",
        "keywords": ["phones in schools", "student attention", "teen mental health", "social media", "UNESCO", "Pew", "Common Sense Media"],
        "source_label": "Phone-free school public record",
        "reader_note": "The rail cards link to education research, health advisories, state policy examples, and survey data. They are source summaries, not fake student posts.",
        "source_intro": "Education, health, survey, policy, and youth-media sources used to fact-check the phone-free school story.",
        "built_note": "Built from UNESCO, CDC, Pew, Common Sense Media, Surgeon General, Education Week, California policy records, and OECD education data.",
        "interactive": {
            "summary": "Classroom test: ban, pouch, or culture?",
            "body": "A rule can remove the device, but culture decides whether students see the rule as punishment, relief, or theater. The strongest policies usually answer storage, exceptions, parent communication, teacher enforcement, and what students get back when the phone disappears.",
        },
        "key_points": [
            "Phone restrictions are spreading because teachers report distraction as a daily instructional problem.",
            "The policy question is not only whether phones are bad; it is when school should be protected from them.",
            "Mental-health evidence is serious but complicated, and the strongest case is often attention and classroom culture.",
            "The best bans plan for emergencies, disability access, family communication, and consistent enforcement.",
        ],
        "sources": [
            {"id": "unesco", "outlet": "UNESCO", "title": "Global Education Monitoring Report 2023: Technology in education", "url": "https://unesdoc.unesco.org/ark:/48223/pf0000385723", "role": "research", "label": "Global report", "card_title": "Technology needs a purpose", "note": "UNESCO's report asks whether technology in education is appropriate, equitable, and evidence-based.", "why": "Used for the global frame on technology in education."},
            {"id": "pew-teachers", "outlet": "Pew Research Center", "title": "72% of U.S. high school teachers say cellphone distraction is a major problem", "url": "https://www.pewresearch.org/short-reads/2024/06/12/72-percent-of-us-high-school-teachers-say-cellphone-distraction-is-a-major-problem-in-the-classroom/", "role": "data", "label": "Teacher survey", "card_title": "Teachers named the problem", "note": "Pew's teacher survey anchors the classroom-distraction section.", "why": "Used for teacher-reported cellphone distraction."},
            {"id": "pew-teens", "outlet": "Pew Research Center", "title": "Teens and Internet, Device Access Fact Sheet", "url": "https://www.pewresearch.org/internet/fact-sheet/teens-and-internet-device-access-fact-sheet/", "role": "data", "label": "Teen access", "card_title": "The phone is nearly universal", "note": "Pew's teen access data explains why school policies touch nearly every student.", "why": "Used for device-access context."},
            {"id": "commonsense", "outlet": "Common Sense Media", "title": "Constant Companion: A Week in the Life of a Young Person's Smartphone Use", "url": "https://www.commonsensemedia.org/research/constant-companion-a-week-in-the-life-of-a-young-persons-smartphone-use", "role": "research", "label": "Phone-use study", "card_title": "The device keeps tapping the shoulder", "note": "Common Sense tracked youth smartphone use and notifications.", "why": "Used for day-to-day smartphone-use context."},
            {"id": "surgeon-general", "outlet": "U.S. Surgeon General", "title": "Social Media and Youth Mental Health Advisory", "url": "https://www.hhs.gov/sites/default/files/sg-youth-mental-health-social-media-advisory.pdf", "role": "official", "label": "Health advisory", "card_title": "Mental health is the hard part", "note": "The advisory summarizes concerns and uncertainties around youth social media.", "why": "Used for health context without overstating causality."},
            {"id": "cdc-yrbs", "outlet": "CDC", "title": "Youth Risk Behavior Survey Data Summary and Trends Report", "url": "https://www.cdc.gov/yrbs/results/index.html", "role": "data", "label": "Youth health data", "card_title": "The backdrop is youth distress", "note": "CDC YRBS data gives mental-health and school-connectedness context.", "why": "Used for the adolescent health backdrop."},
            {"id": "edweek", "outlet": "Education Week", "title": "Which States Ban or Restrict Cellphones in Schools?", "url": "https://www.edweek.org/technology/which-states-ban-or-restrict-cellphones-in-schools/2024/06", "role": "news", "label": "Policy tracker", "card_title": "The state map is changing", "note": "Education Week tracks the spread of state phone policies.", "why": "Used for policy spread context."},
            {"id": "california-phone", "outlet": "California Legislature", "title": "AB 3216: Phone-Free Schools Act", "url": "https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=202320240AB3216", "role": "official", "label": "State law", "card_title": "California moved by law", "note": "California's 2024 law is one example of state policy action.", "why": "Used for a state policy example."},
            {"id": "oecd-pisa", "outlet": "OECD", "title": "PISA 2022 Results", "url": "https://www.oecd.org/en/publications/pisa-2022-results-volume-i_53f23881-en.html", "role": "research", "label": "International data", "card_title": "Distraction is global", "note": "OECD data and analysis connect digital distraction with learning environments.", "why": "Used for international education context."},
            {"id": "ecs", "outlet": "Education Commission of the States", "title": "Cell Phone Use Policies: State Information Request", "url": "https://www.ecs.org/cell-phone-use-policies-state-information-request/", "role": "policy", "label": "Policy brief", "card_title": "Implementation is the whole game", "note": "ECS policy material helps frame the choices states and districts face.", "why": "Used for policy design and implementation context."},
        ],
        "beats": [
            {"id": "attention-is-the-curriculum", "title": "Attention is part of the curriculum", "sources": ["pew-teachers", "unesco", "commonsense", "pew-teens"], "lede": "The phone-free school day begins with a claim so simple it sounds almost old-fashioned: attention is not extra. It is the condition that lets learning happen.", "fact": "Pew's teacher survey, UNESCO's education-technology report, Common Sense's youth phone-use research, and Pew's teen access data all show why the phone has become a classroom policy problem rather than a private habit.", "meaning": "The issue is not that every student is always distracted. The issue is that the possibility of distraction sits within reach all day, turning teaching into a competition with a device built to win attention.", "tension": "Schools do not want to demonize technology. They also cannot pretend that a pocket-sized social universe has no effect on the room.", "human": "A teacher can lose a lesson not through rebellion but through glances, buzzes, side messages, and the tiny social negotiations that pull a class out of sync.", "future": "The phone-free experiment asks whether school can reclaim shared time without pretending students live in 1998."},
            {"id": "not-just-mental-health", "title": "This is not only a mental-health story", "sources": ["surgeon-general", "cdc-yrbs", "commonsense", "pew-teachers"], "lede": "The mental-health debate around phones and social media is serious, but the school phone question does not depend on solving every causal argument in adolescent psychology.", "fact": "The Surgeon General's advisory, CDC youth health data, Common Sense phone-use research, and teacher survey data together show a complicated landscape of distress, exposure, notifications, and classroom disruption.", "meaning": "That complexity should make policy careful, not paralyzed. A school can decide that phones interfere with learning even while researchers continue debating exactly how social media affects mental health.", "tension": "Overclaiming is risky. A phone pouch will not cure loneliness, anxiety, bullying, or sleep deprivation. But underclaiming is also risky if schools ignore a device that constantly interrupts the day.", "human": "Students deserve more than slogans about addiction. They deserve adults who can separate evidence from panic and still make a usable rule.", "future": "The strongest case for phone-free school may be practical: fewer interruptions, more presence, and a clearer boundary around the school day."},
            {"id": "the-emergency-objection", "title": "The emergency objection has to be answered", "sources": ["edweek", "ecs", "california-phone", "pew-teens"], "lede": "Every phone ban meets the same emotional wall: what if something happens? In the United States, that question carries the weight of school shootings, medical needs, family emergencies, and parental fear.", "fact": "Policy trackers and state examples show that phone rules increasingly include exceptions, communication plans, storage requirements, and local implementation choices rather than a single universal model.", "meaning": "The emergency concern cannot be mocked away. A policy that ignores it will lose public trust before it reaches the hallway.", "tension": "At the same time, emergency anxiety can become a veto on any rule. Schools have to explain how parents reach students, how students reach help, and why hundreds of phones can complicate a crisis too.", "human": "A parent does not hand over trust easily. The school has to earn it with a plan that is boring, specific, and repeated until everyone knows it.", "future": "Phone-free policies will survive only if they treat safety communication as part of the design, not as a FAQ added after protest."},
            {"id": "pouches-are-culture", "title": "Pouches are culture disguised as hardware", "sources": ["ecs", "edweek", "pew-teachers", "commonsense"], "lede": "The physical object matters: pouch, locker, basket, cubby, magnet, bag, or locked case. But the object is only the visible part of the culture.", "fact": "Implementation sources and classroom surveys show that enforcement consistency, teacher workload, and student buy-in can matter as much as the device chosen to store the phone.", "meaning": "A pouch can create relief if the whole school uses it fairly. It can create resentment if it becomes another uneven rule enforced hardest against the students already watched most closely.", "tension": "The policy must decide whether phones disappear for the whole day, only during class, or only after a violation. Each choice sends a different message about trust.", "human": "Students are excellent readers of adult inconsistency. If one teacher enforces and another shrugs, the rule becomes a game before it becomes a habit.", "future": "The pouch is not the policy. The policy is the daily ritual the pouch makes possible."},
            {"id": "what-students-get-back", "title": "What do students get back?", "sources": ["unesco", "oecd-pisa", "cdc-yrbs", "surgeon-general"], "lede": "A phone-free school day is usually described by what it removes. The better question is what it returns.", "fact": "UNESCO, OECD, CDC, and health-advisory sources all point toward broader goals than compliance: learning quality, school connectedness, attention, mental health, and technology use that serves a purpose.", "meaning": "The promise is not silence for silence's sake. It is a room where students can be bored, curious, socially awkward, focused, annoyed, playful, and present without a feed filling every gap.", "tension": "That promise can sound sentimental if schools do not replace phone time with something worth having: strong instruction, clubs, counseling, recess, conversation, and real belonging.", "human": "A student who loses a phone but gains nothing except stricter surveillance will not experience the policy as care.", "future": "The most successful phone-free schools will sell the rule less as prohibition and more as restoration."},
            {"id": "equity-and-exceptions", "title": "Equity lives in the exceptions", "sources": ["ecs", "california-phone", "cdc-yrbs", "pew-teens"], "lede": "A universal rule can still land unevenly. Some students use phones for translation, health monitoring, family caregiving, transportation coordination, or disability support.", "fact": "Policy sources and youth-data context show why implementation has to define exceptions carefully and protect legitimate needs without turning every exception into a loophole.", "meaning": "Equity is not the enemy of a phone policy. It is the part that keeps the policy from becoming lazy.", "tension": "Too few exceptions can harm students who need support. Too many exceptions can swallow the rule and return the school to the old chaos.", "human": "The student with diabetes, the newcomer translating a message, or the teenager responsible for a younger sibling is not a hypothetical. Good policy can see them.", "future": "Phone-free schools will need disciplined compassion: clear boundaries, documented exceptions, and adults trusted to tell the difference."},
            {"id": "parents-are-part-of-it", "title": "Parents are part of the classroom weather", "sources": ["pew-teens", "commonsense", "edweek", "ecs"], "lede": "A student phone is often a parent phone by proxy. The text from home enters the classroom, and the classroom enters the family group chat.", "fact": "Teen access data, phone-use research, and policy reporting show that student devices are now woven into family logistics, which means schools cannot change phone rules without changing parent behavior too.", "meaning": "This is why some phone policies fail before first period. Parents may say they want focus and still text during class because the habit feels harmless from the outside.", "tension": "Schools have to ask parents for restraint while offering reliable channels for urgent contact. That is a delicate bargain because families have reasons to be anxious.", "human": "A parent who sends a lunch reminder may not think of it as disruption. A teacher watching twenty reminders land at once sees a different weather system.", "future": "The phone-free school day will require adults outside the building to act like the rule is real."},
            {"id": "the-measurement-problem", "title": "The measurement problem", "sources": ["unesco", "oecd-pisa", "pew-teachers", "cdc-yrbs"], "lede": "The phone-free movement needs better evidence than vibes. A calmer hallway is useful, but schools should measure more than adult relief.", "fact": "Education and health sources suggest multiple outcomes worth tracking: attendance, grades, disciplinary referrals, bullying reports, student connectedness, teacher retention, sleep, anxiety, and classroom climate.", "meaning": "The best policies will be treated as experiments with feedback, not commandments carved into a wall.", "tension": "If a ban improves attention but increases punishment, that matters. If it helps ninth grade and not twelfth, that matters. If students feel more connected or more controlled, that matters too.", "human": "Students should be asked what changed. Teachers should be asked what became easier and what became harder. Parents should be asked whether emergency communication still works.", "future": "The phone-free school day will be groundbreaking only if it learns from itself."},
        ],
    },
    {
        "slug": "memory-the-internet-is-eating-its-own-memory",
        "filename": "memory-the-internet-is-eating-its-own-memory.html",
        "title": "The Internet Is Eating Its Own Memory",
        "section": "Memory",
        "sectionSlug": "memory",
        "type": "Essay",
        "author": "Nia Calder",
        "authorSlug": "nia-calder",
        "authorRole": "Culture Correspondent",
        "publishedLabel": "May 7, 2026 • 2:50 p.m. EDT",
        "updatedLabel": "May 7, 2026 • 2:50 p.m. EDT",
        "publishedIso": "2026-05-07T14:50:00-04:00",
        "updatedIso": "2026-05-07T14:50:00-04:00",
        "dek": "Video games, websites, software, streams, and born-digital culture are disappearing in plain sight, forcing libraries, fans, archivists, companies, and copyright law to decide what the recent past is worth.",
        "excerpt": "Digital culture feels permanent because it is everywhere. That is the illusion. Games, websites, files, links, and platforms can disappear faster than paper ever did.",
        "image": "assets/memory-digital-preservation-thumbnail.png",
        "imageAlt": "AI-generated photorealistic editorial image of a digital preservation workbench with old game media, archival boxes, and a modern workstation.",
        "imageCaptionHtml": "AI-generated photorealistic editorial image for The Press showing digital preservation work. It uses no real game logos or copyrighted characters.",
        "imageCreditPlain": "AI-generated photorealistic editorial image. Not a documentary photograph.",
        "keywords": ["video game preservation", "digital preservation", "copyright", "Internet Archive", "GOG", "software preservation", "libraries"],
        "source_label": "Digital memory public record",
        "reader_note": "The side rail uses preservation reports, library resources, copyright records, and archive projects. No card imitates a real platform screenshot.",
        "source_intro": "Preservation studies, copyright rulemaking records, library resources, museum collections, archive projects, and platform preservation sources used for this story.",
        "built_note": "Built from Video Game History Foundation, U.S. Copyright Office, Library of Congress, Internet Archive, Software Preservation Network, Strong Museum, GOG, and EFF sources.",
        "interactive": {
            "summary": "Shelf test: could a student study it?",
            "body": "A preserved work is not only a file that exists somewhere. It is a work a researcher can find, identify, run or inspect legally, cite, compare, and understand in context. Availability is cultural access, not just storage.",
        },
        "key_points": [
            "Digital culture can vanish through licensing, server shutdowns, obsolete hardware, link rot, and rights restrictions.",
            "Game preservation is especially hard because software often needs hardware, network services, manuals, patches, and context.",
            "Copyright law can protect creators while still making preservation legally difficult for libraries and archives.",
            "The fight is not nostalgia. It is whether recent culture remains studyable.",
        ],
        "sources": [
            {"id": "vghf-87", "outlet": "Video Game History Foundation", "title": "87% Missing: the Disappearance of Classic Video Games", "url": "https://gamehistory.org/87percent/", "role": "research", "label": "Preservation study", "card_title": "Most classic games are unavailable", "note": "VGHF's study is the central statistical source for game availability.", "why": "Used for the 87 percent availability finding and preservation frame."},
            {"id": "copyright-2024", "outlet": "U.S. Copyright Office", "title": "Section 1201 Rulemaking", "url": "https://www.copyright.gov/1201/2024/", "role": "official", "label": "Copyright record", "card_title": "Law decides what archives can do", "note": "Copyright Office records show how preservation exemptions are argued and limited.", "why": "Used for legal context around preservation and access."},
            {"id": "loc-digital", "outlet": "Library of Congress", "title": "Digital Preservation", "url": "https://www.loc.gov/preservation/digital/", "role": "official", "label": "Library guidance", "card_title": "Digital preservation is a discipline", "note": "LOC material frames digital preservation as an institutional practice.", "why": "Used for preservation principles and library context."},
            {"id": "loc-games", "outlet": "Library of Congress", "title": "Digital Preservation at the Library of Congress", "url": "https://www.loc.gov/preservation/digital/", "role": "official", "label": "Research guide", "card_title": "Games are research material", "note": "LOC digital-preservation resources show the institutional status of software and born-digital culture.", "why": "Used for games as archival and research objects."},
            {"id": "archive-software", "outlet": "Internet Archive", "title": "Software Collection", "url": "https://archive.org/details/software", "role": "utility", "label": "Archive", "card_title": "The archive is playable memory", "note": "Internet Archive's software collection is a visible preservation access point.", "why": "Used for public software access and emulation context."},
            {"id": "spn", "outlet": "Software Preservation Network", "title": "Software Preservation Network", "url": "https://www.softwarepreservationnetwork.org/", "role": "research", "label": "Preservation network", "card_title": "Preservation is collaborative", "note": "SPN connects libraries, archives, and researchers around software preservation.", "why": "Used for institutional preservation network context."},
            {"id": "strong", "outlet": "The Strong National Museum of Play", "title": "Collections", "url": "https://www.museumofplay.org/collections/", "role": "official", "label": "Museum collection", "card_title": "Play belongs in museums", "note": "The Strong's collections demonstrate the museum role in preserving games and play culture.", "why": "Used for museum preservation context."},
            {"id": "gog", "outlet": "GOG", "title": "GOG Preservation Program", "url": "https://www.gog.com/en/gog-preservation-program", "role": "official", "label": "Platform program", "card_title": "Commercial preservation can help", "note": "GOG's program shows a market-based preservation model.", "why": "Used for commercial access and compatibility context."},
            {"id": "eff", "outlet": "Electronic Frontier Foundation", "title": "DMCA Rulemaking and Preservation", "url": "https://www.eff.org/issues/dmca-rulemaking", "role": "policy", "label": "Legal advocacy", "card_title": "Access fights repeat", "note": "EFF tracks Section 1201 battles relevant to repair, research, and preservation.", "why": "Used for advocacy and legal-access context."},
            {"id": "mame", "outlet": "MAME", "title": "MAME Project", "url": "https://www.mamedev.org/", "role": "utility", "label": "Emulation", "card_title": "Emulation is historical machinery", "note": "MAME illustrates how emulation supports preservation of arcade and game history.", "why": "Used for emulation as preservation infrastructure."},
            {"id": "ia-scholar", "outlet": "Internet Archive", "title": "Wayback Machine", "url": "https://web.archive.org/", "role": "utility", "label": "Web archive", "card_title": "The web needs a memory too", "note": "The Wayback Machine shows web preservation at public scale.", "why": "Used for link rot and web memory context."},
        ],
        "beats": [
            {"id": "the-illusion-of-permanence", "title": "The illusion of permanence", "sources": ["loc-digital", "ia-scholar", "archive-software", "vghf-87"], "lede": "Digital culture feels permanent because it is everywhere. That is the trap. A thing can be copied endlessly and still become inaccessible almost overnight.", "fact": "Library of Congress preservation guidance, web archives, software collections, and the Video Game History Foundation's availability study all challenge the lazy assumption that digital abundance equals cultural memory.", "meaning": "The internet does not preserve by existing. It preserves when institutions, communities, companies, and laws make deliberate choices to keep things findable and usable.", "tension": "A book can burn, but a server can vanish silently. A cartridge can survive in a drawer while the patch, account server, manual, soundtrack license, or storefront listing disappears.", "human": "The loss often feels small until someone tries to study a game, a fan site, a tool, a video, or an early online world and discovers only broken links.", "future": "The recent past is becoming archival before the public has learned to treat it as fragile."},
            {"id": "games-are-hard-to-save", "title": "Games are hard to save because they are not only files", "sources": ["vghf-87", "loc-games", "mame", "strong"], "lede": "A video game is not just a title on a list. It is code, art, interface, hardware behavior, controller feel, manuals, patches, network services, regional versions, player practice, and memory.", "fact": "Game preservation sources from VGHF, the Library of Congress, MAME, and The Strong show why games require more than a screenshot and a release date.", "meaning": "This is why preservation can look obsessive from outside and obvious from inside. Without the right environment, the work may exist but no longer behave like itself.", "tension": "Companies often preserve what they can sell. Historians need to preserve what explains the medium, including failures, experiments, regional oddities, licensed works, and games nobody remasters.", "human": "The student trying to understand a design movement cannot rely only on greatest-hits collections. Culture is made from the ordinary shelf too.", "future": "If games are a major art and technology form, they need preservation rules worthy of a major art and technology form."},
            {"id": "copyright-is-the-lock", "title": "Copyright is the lock and the shelter", "sources": ["copyright-2024", "eff", "spn", "vghf-87"], "lede": "Copyright is not the villain of preservation. It pays creators, protects markets, and gives owners rights that matter. But it can also lock memory inside legal uncertainty.", "fact": "Copyright Office rulemaking records, EFF advocacy, Software Preservation Network work, and the VGHF study show how anti-circumvention law and access limits complicate preservation by libraries and archives.", "meaning": "The legal problem is subtle. An archive may have the will and the expertise to preserve a work, but not the permission to make it accessible in the way scholarship requires.", "tension": "Rights owners fear uncontrolled distribution. Archivists fear cultural disappearance. Both fears can be legitimate, which is why blanket slogans do not solve the problem.", "human": "A librarian should not have to choose between breaking the law and losing the only working copy of a cultural object.", "future": "The legal future needs more precise tools: preservation access that is real enough for research and narrow enough to respect living markets."},
            {"id": "the-platform-problem", "title": "Platforms are not libraries", "sources": ["gog", "archive-software", "ia-scholar", "loc-digital"], "lede": "A storefront can feel like a library until the license changes. A streaming catalog can feel like an archive until a title disappears. A social feed can feel like a record until the platform pivots.", "fact": "Commercial preservation programs, public software archives, the Wayback Machine, and library preservation guidance show the difference between access by business model and preservation by mission.", "meaning": "Platforms are built to serve users now. Archives are built to serve memory later. Sometimes those goals overlap, but they are not the same job.", "tension": "The public often discovers this only after something vanishes. What looked like ownership was access. What looked like a permanent URL was a temporary permission slip.", "human": "People build identities around digital culture: games played with siblings, forums where they learned to code, videos that shaped humor, songs tied to a platform that no longer wants them.", "future": "A serious digital culture needs commercial access and public memory, because either one alone is too fragile."},
            {"id": "emulation-is-not-theft", "title": "Emulation is historical machinery", "sources": ["mame", "archive-software", "spn", "copyright-2024"], "lede": "Emulation is often discussed as if it were only piracy wearing a clever hat. That misses the preservation point. Emulation can be the machine that lets old software speak.", "fact": "MAME, Internet Archive software collections, Software Preservation Network, and Copyright Office rulemaking all show that emulation sits at the center of practical software preservation.", "meaning": "When original hardware fails or becomes rare, emulation can preserve behavior, timing, interface, and playability in a way a video clip cannot.", "tension": "The same tool can be used for legitimate scholarship and unauthorized distribution. That dual use makes policy hard, but it does not make the legitimate use imaginary.", "human": "An arcade cabinet in a museum is wonderful. It is also scarce. Emulation can let more people study the experience without pretending the digital copy is the original object.", "future": "The future of memory will depend on treating emulation as infrastructure and regulating misuse without criminalizing history."},
            {"id": "fans-are-unofficial-archivists", "title": "Fans are unofficial archivists", "sources": ["strong", "spn", "ia-scholar", "vghf-87"], "lede": "Long before institutions learned to collect digital culture seriously, fans were saving manuals, dumping cartridges, scanning box art, mapping worlds, maintaining wikis, and writing down how things worked.", "fact": "Museum collections, preservation networks, web archives, and availability research all reveal the importance of communities that preserved what companies and institutions did not.", "meaning": "Fan labor is messy, uneven, passionate, sometimes legally gray, and often historically invaluable. It is the attic of digital culture.", "tension": "Institutions need standards, metadata, rights clarity, and durability. Fans often have speed, memory, enthusiasm, and the only surviving copy.", "human": "The person who kept a strategy guide in a closet or mirrored a forum before shutdown may have saved a piece of culture nobody official had thought to value.", "future": "The healthiest preservation future will connect fans and institutions instead of pretending one can replace the other."},
            {"id": "commercial-preservation", "title": "Commercial preservation counts, but it cannot be the whole plan", "sources": ["gog", "vghf-87", "loc-games", "archive-software"], "lede": "When a company restores an old game for modern systems, that matters. It gives players legal access, pays rights holders, and proves that preservation can have a market.", "fact": "GOG's preservation program, VGHF's availability study, Library of Congress resources, and public software archives show the value and limits of commercial access.", "meaning": "The limit is selection. Markets preserve what can be sold, licensed, and supported. History also needs the strange, the broken, the minor, the obsolete, and the commercially inconvenient.", "tension": "A remaster can become a replacement in public memory, flattening differences between versions and making the accessible edition seem like the original.", "human": "Players deserve playable classics. Researchers deserve the record of how those classics changed, failed, traveled, and were received.", "future": "Commercial preservation should be celebrated as one lane, not mistaken for the entire road."},
            {"id": "memory-is-a-choice", "title": "Memory is a choice, not a default setting", "sources": ["loc-digital", "copyright-2024", "spn", "vghf-87"], "lede": "The culture most at risk is often the culture that feels too recent to be endangered. People assume someone is saving it because everyone remembers it.", "fact": "Library preservation guidance, copyright records, preservation networks, and game-availability research all say otherwise: digital memory requires policy, institutions, tools, and permission.", "meaning": "The internet is eating its own memory because convenience taught us to confuse access with preservation.", "tension": "We do not need to save everything in the same way. But we do need a public method for deciding what matters before platforms, drives, servers, and licenses decide for us.", "human": "A future reader should be able to study what we made without excavating rumors from dead links and screenshots of menus that no longer open.", "future": "Memory is a choice. The uncomfortable part is that choosing later often means choosing from what survived by accident."},
        ],
    },
    {
        "slug": "systems-the-cold-chain-is-the-invisible-machine-that-feeds-the-world",
        "filename": "systems-the-cold-chain-is-the-invisible-machine-that-feeds-the-world.html",
        "title": "The Cold Chain Is the Invisible Machine That Feeds the World",
        "section": "Systems",
        "sectionSlug": "systems",
        "type": "Deep Dive",
        "author": "The Press",
        "authorSlug": "the-press",
        "authorRole": "Editorial Desk",
        "publishedLabel": "May 7, 2026 • 4:00 p.m. EDT",
        "updatedLabel": "May 7, 2026 • 4:00 p.m. EDT",
        "publishedIso": "2026-05-07T16:00:00-04:00",
        "updatedIso": "2026-05-07T16:00:00-04:00",
        "dek": "Refrigerated trucks, warehouses, vaccines, fish, fruit, insulin, power bills, refrigerants, and wasted food are all part of one hidden system: the cold chain.",
        "excerpt": "The cold chain is why strawberries survive a continent, vaccines survive a rural road, and food waste becomes a climate problem instead of only a kitchen problem.",
        "image": "assets/systems-cold-chain-thumbnail.png",
        "imageAlt": "AI-generated photorealistic editorial image of a refrigerated loading dock with produce crates and vaccine coolers at dawn.",
        "imageCaptionHtml": "AI-generated photorealistic editorial image for The Press showing cold-chain logistics. It is not a documentary photograph of a specific warehouse.",
        "imageCreditPlain": "AI-generated photorealistic editorial image. Not a documentary photograph.",
        "keywords": ["cold chain", "food waste", "refrigeration", "vaccines", "logistics", "UNEP", "FAO", "WHO", "UNICEF"],
        "source_label": "Cold chain public record",
        "reader_note": "The side rail links to food-waste, refrigeration, vaccine, and cooling sources. Cards are clickable context posts and source notes, not fake logistics screenshots.",
        "source_intro": "Food-loss, cooling, refrigeration, vaccine-supply, and logistics sources used to check the cold-chain claims in this story.",
        "built_note": "Built from UNEP, FAO, WHO, UNICEF, Gavi, IEA, World Bank, IIR, and cold-chain reports.",
        "interactive": {
            "summary": "Kitchen test: what disappears if cold fails?",
            "body": "Think beyond ice cream. A cold-chain failure can mean spoiled milk, unsafe fish, wasted vaccines, lost farmer income, higher prices, more methane from food waste, and medicines that no longer work as intended.",
        },
        "key_points": [
            "The cold chain connects food security, medicine, energy demand, emissions, and trade.",
            "Food waste is a climate problem, and refrigeration can prevent some waste while consuming energy.",
            "Vaccines and many medicines depend on temperature-controlled logistics.",
            "The future challenge is cooling more equitably while cutting climate impact from power and refrigerants.",
        ],
        "sources": [
            {"id": "unep-waste", "outlet": "UNEP", "title": "Food Waste Index Report 2024", "url": "https://www.unep.org/resources/publication/food-waste-index-report-2024", "role": "research", "label": "Food waste", "card_title": "Waste has a climate cost", "note": "UNEP's report anchors the food-waste part of the cold-chain story.", "why": "Used for food waste and climate context."},
            {"id": "fao-loss", "outlet": "FAO", "title": "Food Loss and Food Waste", "url": "https://www.fao.org/food-loss-and-food-waste/en/", "role": "official", "label": "Food systems", "card_title": "Loss happens before dinner", "note": "FAO material explains food loss and waste across the supply chain.", "why": "Used for food-system loss and waste definitions."},
            {"id": "unep-cold", "outlet": "UNEP", "title": "Sustainable Food Cold Chains", "url": "https://www.unep.org/resources/report/sustainable-food-cold-chains-opportunities-challenges-and-way-forward", "role": "research", "label": "Cold-chain report", "card_title": "Cold chains need to be sustainable", "note": "UNEP's report connects refrigeration, food loss, energy, and emissions.", "why": "Used for sustainable cold-chain framing."},
            {"id": "iir", "outlet": "International Institute of Refrigeration", "title": "The role of refrigeration in worldwide nutrition", "url": "https://iifiir.org/en/news/new-iir-informatory-note-the-role-of-refrigeration-in-worldwide-nutrition", "role": "research", "label": "Refrigeration", "card_title": "Refrigeration is food infrastructure", "note": "IIR material gives refrigeration context for nutrition and food access.", "why": "Used for refrigeration's role in food systems."},
            {"id": "who-supply", "outlet": "World Health Organization", "title": "Immunization supply chain and logistics", "url": "https://www.who.int/teams/immunization-vaccines-and-biologicals/essential-programme-on-immunization/supply-chain", "role": "official", "label": "Vaccines", "card_title": "Vaccines ride the cold chain", "note": "WHO supply-chain guidance anchors the medical side.", "why": "Used for vaccine supply-chain context."},
            {"id": "unicef-cold", "outlet": "UNICEF Supply Division", "title": "What is a cold chain?", "url": "https://www.unicef.org/supply/what-cold-chain", "role": "official", "label": "Cold chain", "card_title": "The last mile must stay cold", "note": "UNICEF explains vaccine cold-chain equipment and delivery.", "why": "Used for last-mile immunization cold-chain context."},
            {"id": "gavi", "outlet": "Gavi", "title": "Keeping vaccines cool with cold chain", "url": "https://www.gavi.org/vaccineswork/keeping-vaccines-cool-cold-chain", "role": "guide", "label": "Explainer", "card_title": "Temperature is trust", "note": "Gavi's explainer translates why vaccines need temperature control.", "why": "Used for plain-language vaccine cold-chain explanation."},
            {"id": "iea-cooling", "outlet": "International Energy Agency", "title": "The Future of Cooling", "url": "https://www.iea.org/reports/the-future-of-cooling", "role": "research", "label": "Cooling energy", "card_title": "Cooling uses power", "note": "IEA's cooling report connects cooling demand with energy systems.", "why": "Used for cooling energy-demand context."},
            {"id": "worldbank", "outlet": "World Bank", "title": "How financing sustainable cooling can buffer our food system", "url": "https://blogs.worldbank.org/en/climatechange/how-financing-sustainable-cooling-can-buffer-our-food-system", "role": "research", "label": "Development", "card_title": "Cold can protect income", "note": "World Bank material links cold chains to food loss and farmer livelihoods.", "why": "Used for development and farmer-income context."},
            {"id": "fao-footprint", "outlet": "FAO", "title": "Food wastage footprint", "url": "https://www.fao.org/3/i3347e/i3347e.pdf", "role": "research", "label": "Footprint", "card_title": "Waste wastes everything upstream", "note": "FAO's footprint work explains the resource and emissions cost of wasted food.", "why": "Used for environmental cost of food waste."},
        ],
        "beats": [
            {"id": "the-machine-you-do-not-see", "title": "The machine you do not see", "sources": ["unep-cold", "fao-loss", "iir", "iea-cooling"], "lede": "The cold chain is easiest to notice when it fails. The milk turns, the fish smells wrong, the vaccine is discarded, the truck door hangs open too long, the freezer alarm starts shouting.", "fact": "UNEP, FAO, IIR, and IEA sources together describe a hidden infrastructure that links food loss, refrigeration, energy demand, nutrition, and climate impact.", "meaning": "Cold is not just a temperature. It is a logistics condition that has to be maintained through farms, docks, warehouses, trucks, stores, clinics, and kitchens.", "tension": "The paradox is that cold chains can reduce waste and protect health while also consuming power and using refrigerants that must be managed carefully.", "human": "A shopper sees strawberries. A nurse sees a vaccine vial. A farmer sees a product that must reach market before time and heat ruin the work.", "future": "The cold chain is invisible infrastructure until a warmer world makes it impossible to ignore."},
            {"id": "food-waste-is-climate", "title": "Food waste is climate policy", "sources": ["unep-waste", "fao-loss", "fao-footprint", "worldbank"], "lede": "Food waste sounds domestic, like a guilty refrigerator shelf. In reality it is land, water, fertilizer, diesel, labor, refrigeration, transport, and money thrown away together.", "fact": "UNEP's Food Waste Index, FAO food-loss material, FAO footprint work, and World Bank cold-chain reporting show that wasted food is an environmental and economic problem across the supply chain.", "meaning": "The cold chain cannot solve all waste. Some losses come from standards, behavior, packaging, harvest timing, and markets. But temperature is one of the few variables that can turn time from enemy into margin.", "tension": "More refrigeration can prevent waste, yet inefficient cooling can increase electricity demand and emissions. That means the answer must be better cold, not cold at any cost.", "human": "For a farmer, a cold room can mean selling tomorrow instead of dumping tonight. For a family, it can mean safer food and less money wasted.", "future": "Food-waste policy will remain incomplete until it treats cold storage as infrastructure rather than luxury."},
            {"id": "vaccines-ride-on-trust", "title": "Vaccines ride on trust and temperature", "sources": ["who-supply", "unicef-cold", "gavi", "unep-cold"], "lede": "A vaccine dose is a medical promise with a temperature range. If the cold chain fails, the promise can fail before the nurse ever opens the vial.", "fact": "WHO, UNICEF, Gavi, and sustainable cold-chain sources all show how immunization depends on equipment, monitoring, transport, maintenance, and last-mile delivery.", "meaning": "The cold chain is therefore part of the public's trust in medicine. People see the shot, not the refrigerators, carriers, data loggers, and power systems that kept it viable.", "tension": "The last mile is often the hardest mile. Rural roads, unreliable power, extreme heat, and weak maintenance can turn a technical requirement into a public-health barrier.", "human": "The person waiting at a clinic should not have to think about the journey the vial took. The system should have protected that journey already.", "future": "Equitable immunization depends on a cold chain that works as well in the difficult places as it does in the easy ones."},
            {"id": "cooling-has-a-power-bill", "title": "Cooling has a power bill", "sources": ["iea-cooling", "unep-cold", "iir", "worldbank"], "lede": "Cold feels clean, but it is not free. Every refrigerator, compressor, warehouse, insulated truck, and cold room is connected to electricity, fuel, maintenance, and design choices.", "fact": "IEA cooling analysis, UNEP cold-chain reporting, IIR refrigeration work, and World Bank development material connect cooling expansion with energy demand and infrastructure quality.", "meaning": "The challenge is not whether more people deserve cooling. They do. The challenge is whether the world can provide it efficiently and cleanly enough to avoid worsening the heat problem it is trying to manage.", "tension": "A poor cold chain wastes food. A dirty cold chain wastes energy and climate space. The goal is to escape that trap.", "human": "A warehouse manager cares about spoilage, power prices, equipment downtime, and customer deadlines. Climate policy arrives as a compressor choice and a utility bill.", "future": "The best cold chain will be judged by what it saves: food, medicine, money, emissions, and time."},
            {"id": "refrigerants-matter", "title": "Refrigerants matter because leaks matter", "sources": ["unep-cold", "iea-cooling", "iir", "fao-footprint"], "lede": "Cooling technology has a chemical shadow. Refrigerants make modern cold possible, but some can contribute strongly to warming if released.", "fact": "Sustainable cold-chain and cooling-energy sources explain why efficient equipment, refrigerant choice, leak control, maintenance, and phase-down policies are part of climate-smart cooling.", "meaning": "This turns the technician into a climate actor. Installation, charging, recovery, and repair are not obscure tasks; they decide whether cooling helps solve a problem or quietly deepens one.", "tension": "The public often debates big energy technologies while ignoring the small leak that happens in millions of systems. Scale makes maintenance political.", "human": "The person servicing a supermarket rack or clinic refrigerator is holding a piece of the climate system in a wrench hand.", "future": "The clean cold chain will need better equipment and a larger workforce trained to keep the cold inside the machine."},
            {"id": "the-last-mile", "title": "The last mile is where systems tell the truth", "sources": ["unicef-cold", "gavi", "worldbank", "fao-loss"], "lede": "Supply chains love diagrams. The last mile loves reality: bad roads, power cuts, heat, broken doors, missing parts, small clinics, market delays, and human improvisation.", "fact": "UNICEF, Gavi, World Bank, and FAO sources all show that cold-chain performance depends on the most fragile links, not the cleanest diagram.", "meaning": "That is why cold-chain equity matters. It is not enough for premium seafood, export fruit, or urban hospitals to stay cold. The system has to reach the places where heat and distance do the most damage.", "tension": "Centralized efficiency can miss local resilience. A warehouse may be excellent while the final route fails.", "human": "A farmer with no cold storage sells under pressure. A clinic with weak power wastes doses. A family pays more because loss upstream becomes price downstream.", "future": "The last mile will decide whether the cold chain is a development tool or another infrastructure gap."},
            {"id": "cold-and-fairness", "title": "Cold is a fairness issue", "sources": ["unep-waste", "worldbank", "who-supply", "fao-loss"], "lede": "Cooling is often invisible in rich places because it works. That invisibility can hide how unequal cold access remains across regions, incomes, and institutions.", "fact": "Food-waste, development, health-supply, and food-loss sources show that cold-chain access affects nutrition, farmer income, medicine, and price stability.", "meaning": "A fair cold chain does not mean every product travels farther. It means perishable goods and temperature-sensitive medicines can move safely when they need to.", "tension": "There is a climate danger in copying wasteful cooling models everywhere. There is also an equity danger in telling poorer regions they cannot have the cooling infrastructure wealthier regions already rely on.", "human": "Cold access changes daily life quietly: safer milk, less spoilage, usable vaccines, steadier income, and fewer frantic decisions before heat wins.", "future": "The fair answer is not less cold for those who lack it. It is better cold for everyone."},
            {"id": "the-invisible-machine", "title": "The invisible machine becomes visible", "sources": ["unep-cold", "iea-cooling", "who-supply", "unep-waste"], "lede": "The cold chain is a systems story because it refuses to stay in one category. It is food, health, energy, climate, labor, trade, and design at once.", "fact": "The source record from UNEP, IEA, WHO, and food-waste research makes the same point from different doors: temperature control is no longer a technical side issue.", "meaning": "That is why the story matters. The public can understand a refrigerator. The harder task is seeing the refrigerated civilization behind the refrigerator.", "tension": "More cooling is necessary. More careless cooling is dangerous. Less waste is necessary. More energy demand is difficult. The system has to do several things right at the same time.", "human": "Every cold item on a shelf is a small act of coordination. Someone harvested it, packed it, cooled it, moved it, monitored it, stocked it, bought it, and hoped the temperature held.", "future": "The invisible machine that feeds the world is about to become one of the visible tests of whether modern life can become both more reliable and less wasteful."},
        ],
    },
]


SECTIONS_TO_ADD = [
    {
        "slug": "climate",
        "name": "Climate",
        "filename": "section-climate.html",
        "headline": "Climate",
        "copy": "Risk, adaptation, insurance, heat, water, and the practical systems that decide what resilience costs.",
        "eyebrow": "Climate Desk",
        "artwork": "",
    },
    {
        "slug": "memory",
        "name": "Memory",
        "filename": "section-memory.html",
        "headline": "Memory",
        "copy": "Digital preservation, archives, games, platforms, libraries, and the recent past before it disappears.",
        "eyebrow": "Memory Desk",
        "artwork": "",
    },
    {
        "slug": "systems",
        "name": "Systems",
        "filename": "section-systems.html",
        "headline": "Systems",
        "copy": "The hidden infrastructures behind food, medicine, power, logistics, risk, and daily life.",
        "eyebrow": "Systems Desk",
        "artwork": "",
    },
]


def story_entry(article: dict, word_count: int) -> dict:
    read_minutes = max(1, math.ceil(word_count / 200))
    return {
        "slug": article["slug"],
        "filename": article["filename"],
        "title": article["title"],
        "section": article["section"],
        "sectionSlug": article["sectionSlug"],
        "type": article["type"],
        "author": article["author"],
        "authorSlug": article["authorSlug"],
        "authorRole": article["authorRole"],
        "publishedLabel": article["publishedLabel"],
        "updatedLabel": article["updatedLabel"],
        "publishedIso": article["publishedIso"],
        "updatedIso": article["updatedIso"],
        "wordCount": f"{word_count:,} words",
        "wordCountNumber": word_count,
        "readTime": f"{read_minutes} min read",
        "dek": article["dek"],
        "image": article["image"],
        "imageAlt": article["imageAlt"],
        "imageCaptionHtml": article["imageCaptionHtml"],
        "imageCreditPlain": article["imageCreditPlain"],
        "imageAiGenerated": True,
        "imageAiCaption": "This thumbnail is an AI-generated photorealistic editorial image, not a documentary photograph or a real social-media screenshot.",
        "keywords": article["keywords"],
        "asideFile": f"content/asides/{article['slug']}.html",
        "bodyFile": f"content/bodies/{article['slug']}.html",
        "excerpt": article["excerpt"],
        "related": article.get("related", []),
        "imageWidth": 1672,
        "imageHeight": 941,
        "heroEligible": True,
        "socialRailPattern": {
            "className": f"press-feature-social-feature {article['slug']}-social-feature",
            "cardsInBody": len(article["beats"]) * 4,
            "sourceCount": len(article["sources"]),
            "notes": "Cards are editorial context cards with real source buttons distributed down the full article. No fake screenshots, fake usernames, or invented public reaction.",
        },
    }


def main() -> None:
    (ROOT / "content" / "bodies").mkdir(parents=True, exist_ok=True)
    (ROOT / "content" / "asides").mkdir(parents=True, exist_ok=True)

    generated_entries = []
    for article in ARTICLES:
        body, word_count = render_body(article)
        if word_count < 3000:
            raise SystemExit(f"{article['slug']} is under 3,000 words: {word_count}")
        (ROOT / "content" / "bodies" / f"{article['slug']}.html").write_text(body + "\n", encoding="utf-8")
        (ROOT / "content" / "asides" / f"{article['slug']}.html").write_text(render_aside(article) + "\n", encoding="utf-8")
        generated_entries.append(story_entry(article, word_count))

    master_path = ROOT / "master-edition.json"
    data = json.loads(master_path.read_text(encoding="utf-8"))

    existing_section_slugs = {section["slug"] for section in data["sections"]}
    for section in SECTIONS_TO_ADD:
        if section["slug"] not in existing_section_slugs:
            data["sections"].append(section)
            existing_section_slugs.add(section["slug"])

    new_filenames = {entry["filename"] for entry in generated_entries}
    data["stories"] = [story for story in data["stories"] if story.get("filename") not in new_filenames]
    data["stories"] = generated_entries + data["stories"]

    homepage = data.setdefault("homepage", {})
    for key in ("leadOrder", "secondary", "mostRead", "editorsPicks"):
        current = [item for item in homepage.get(key, []) if item not in new_filenames]
        insert = [entry["filename"] for entry in generated_entries[: 7 if key == "leadOrder" else 4]]
        homepage[key] = insert + current

    for author in data.get("authors", []):
        additions = [
            entry["filename"]
            for entry in generated_entries
            if entry["authorSlug"] == author.get("slug") and entry["filename"] not in author.get("stories", [])
        ]
        if additions:
            author["stories"] = additions + author.get("stories", [])

    data["site"]["editionNote"] = "Issue Five • Thursday, May 7, 2026 • Seven new long-form source-led features with photorealistic AI thumbnails"
    master_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    summary = {
        entry["filename"]: {
            "title": entry["title"],
            "wordCount": entry["wordCountNumber"],
            "sources": entry["socialRailPattern"]["sourceCount"],
        }
        for entry in generated_entries
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
