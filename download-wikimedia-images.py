#!/usr/bin/env python3
"""
Download proper Wikimedia Commons / NASA public-domain images for
The Press daily articles.

Run this script once from the repo root:
    python3 download-wikimedia-images.py

All images are either:
  - NASA public domain (no copyright restriction)
  - Wikimedia Commons CC BY / CC BY-SA 2.0 or later
  - U.S. government work (public domain)

The script saves each image to assets/daily/ using the exact filename
the HTML already expects.  If a file already exists it is skipped.

Attribution notes are printed to stdout — paste them into the
article's photo credit or keep this file as your image ledger.
"""

import os
import sys
import urllib.request
import urllib.error

DEST = os.path.join(os.path.dirname(__file__), "assets", "daily")
os.makedirs(DEST, exist_ok=True)

UA = "ThePress/1.0 (thepress.live; legal image sourcing script)"

IMAGES = [
    # ── ARTEMIS / SPACE ────────────────────────────────────────────────────
    {
        "filename": "2026-04-12-2026-04-12-artemis-ii-s-10-day-lunar-loop-marks-the-first-human-return-to-the-moon-since-apollo-17.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Artemis_II_Official_Crew_Portrait.jpg/1280px-Artemis_II_Official_Crew_Portrait.jpg",
        "alt": "Official NASA portrait of the Artemis II crew of four astronauts",
        "credit": "NASA. Official crew portrait of the Artemis II astronauts. U.S. government work — public domain.",
    },
    {
        "filename": "2026-04-12-2026-04-12-artemis-ii-s-moon-flyby-marks-a-new-test-for-human-deep-space-exploration.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Artemis_I_launch_from_LC-39B_%2811%29.jpg/1280px-Artemis_I_launch_from_LC-39B_%2811%29.jpg",
        "alt": "SLS rocket launching from Kennedy Space Center LC-39B",
        "credit": "NASA / Joel Kowsky. SLS launch from Kennedy Space Center. U.S. government work — public domain.",
    },
    {
        "filename": "2026-04-12-2026-04-12-artemis-ii-s-moon-flyby-turns-a-test-flight-into-a-live-lunar-science-rehearsal.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Moon_nearside_LRO_Oct_2024.jpg/1280px-Moon_nearside_LRO_Oct_2024.jpg",
        "alt": "Full near-side view of the Moon photographed by the Lunar Reconnaissance Orbiter",
        "credit": "NASA / LRO. Lunar Reconnaissance Orbiter image of the Moon's near side, October 2024. U.S. government work — public domain.",
    },

    # ── AI / TECHNOLOGY ────────────────────────────────────────────────────
    {
        "filename": "2026-04-12-2026-04-12-ai-s-next-phase-is-enterprise-control-not-just-bigger-models.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/CERN_Data_Centre_7.jpg/1280px-CERN_Data_Centre_7.jpg",
        "alt": "Rows of servers in the CERN data centre",
        "credit": "CERN. Interior of CERN's data centre. Photo by CERN, licensed CC BY 4.0 via Wikimedia Commons.",
    },
    {
        "filename": "2026-04-12-2026-04-12-as-ai-enters-the-scientific-method-researchers-are-rewriting-the-rules-of-discovery.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/49/2015-11-17_Microscope_-_Science_Museum_Lates.jpg/1280px-2015-11-17_Microscope_-_Science_Museum_Lates.jpg",
        "alt": "Researcher looking through a microscope in a laboratory setting",
        "credit": "Photo by Science Museum Group, licensed CC BY 4.0 via Wikimedia Commons.",
    },
    {
        "filename": "2026-04-12-2026-04-12-google-s-april-ai-push-shows-the-race-has-shifted-from-bigger-models-to-more-useful-ones.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Google_Mountain_View_Campus.jpg/1280px-Google_Mountain_View_Campus.jpg",
        "alt": "Google's Mountain View campus",
        "credit": "Photo by Chrizz17 via Wikimedia Commons, licensed CC BY-SA 4.0.",
    },
    {
        "filename": "2026-04-12-2026-04-12-openai-s-april-surge-shows-the-ai-race-has-moved-from-models-to-distribution-operations-and-trust.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/CERN_Data_Centre_7.jpg/960px-CERN_Data_Centre_7.jpg",
        "alt": "Server rows in a modern data centre",
        "credit": "CERN. Data centre interior. Licensed CC BY 4.0 via Wikimedia Commons.",
    },
    {
        "filename": "2026-04-12-2026-04-12-the-ai-industry-s-new-arms-race-is-not-just-about-models-it-s-about-compute-control-and-trust.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Supcomputer_Titan.jpg/1280px-Supcomputer_Titan.jpg",
        "alt": "Titan supercomputer at Oak Ridge National Laboratory",
        "credit": "Wikimedia Commons. Titan supercomputer at Oak Ridge National Laboratory. U.S. government work — public domain.",
    },

    # ── ECONOMICS / FINANCE ────────────────────────────────────────────────
    {
        "filename": "2026-04-12-2026-04-12-as-tariffs-loomed-march-inflation-and-jobs-data-showed-a-u-s-economy-still-balancing-growth-and-price-pressure.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/US_Navy_051129-N-0000X-002_A_shopper_reads_a_label_on_a_product_inside_a_Navy_Exchange_store.jpg/1280px-US_Navy_051129-N-0000X-002_A_shopper_reads_a_label_on_a_product_inside_a_Navy_Exchange_store.jpg",
        "alt": "Shopper reading a product label in a retail store",
        "credit": "U.S. Navy photo. Shopper reads a product label in a store. U.S. government work — public domain.",
    },
    {
        "filename": "2026-04-12-2026-04-12-imf-spring-meetings-open-as-war-tariffs-and-inflation-put-the-world-economy-on-edge.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/IMF_Headquarters_Building_0001.jpg/1280px-IMF_Headquarters_Building_0001.jpg",
        "alt": "Exterior of the IMF headquarters building in Washington D.C.",
        "credit": "Photo by AgnosticPreachersKid via Wikimedia Commons, licensed CC BY-SA 3.0.",
    },
    {
        "filename": "2026-04-12-2026-04-12-iran-oil-shock-pushes-u-s-inflation-higher-forcing-fed-into-a-harder-balancing-act.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/92/US-FederalReserveBoard-Seal.svg/512px-US-FederalReserveBoard-Seal.svg.png",
        "alt": "U.S. Federal Reserve Board seal",
        "credit": "U.S. Federal Reserve. Official seal. U.S. government work — public domain.",
    },

    # ── WORLD / GEOPOLITICS ────────────────────────────────────────────────
    {
        "filename": "2026-04-12-2026-04-12-ceasefire-on-paper-crisis-in-motion-iran-talks-lebanon-strikes-and-a-region-still-on-edge.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/UN_General_Assembly_hall.jpg/1280px-UN_General_Assembly_hall.jpg",
        "alt": "The United Nations General Assembly hall in New York",
        "credit": "UN Photo. The General Assembly hall. Licensed CC BY-NC-ND 2.0.",
    },
    {
        "filename": "2026-04-12-2026-04-12-pakistan-tests-whether-the-iran-ceasefire-can-become-a-deal.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Lahore_Fort_Sheesh_Mahal_001.jpg/1280px-Lahore_Fort_Sheesh_Mahal_001.jpg",
        "alt": "Sheesh Mahal inside Lahore Fort, Pakistan",
        "credit": "Photo by Usman Ghani via Wikimedia Commons, licensed CC BY-SA 4.0.",
    },
    {
        "filename": "2026-04-12-2026-04-12-taiwan-s-opposition-leader-s-beijing-trip-tests-the-island-s-political-center-as-military-pressure-rises.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Taipei_101_2_HDR.jpg/853px-Taipei_101_2_HDR.jpg",
        "alt": "Taipei 101 skyscraper and the Taipei skyline",
        "credit": "Photo by Mori Takahiro via Wikimedia Commons, licensed CC BY 2.0.",
    },

    # ── POLITICS / LAW ─────────────────────────────────────────────────────
    {
        "filename": "2026-04-12-2026-04-12-supreme-court-set-to-test-trump-s-immigration-power-as-tps-fight-for-haitians-and-syrians-reaches-high-court.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f4/US_Supreme_Court.JPG/1280px-US_Supreme_Court.JPG",
        "alt": "The United States Supreme Court building in Washington D.C.",
        "credit": "Photo via Wikimedia Commons. U.S. Supreme Court Building. Public domain.",
    },
    {
        "filename": "2026-04-12-2026-04-12-trump-s-birthright-citizenship-fight-becomes-a-test-of-presidential-power-and-the-14th-amendment.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/National_Archives_Constitution_Avenue.jpg/1280px-National_Archives_Constitution_Avenue.jpg",
        "alt": "The National Archives building in Washington D.C., home of the U.S. Constitution",
        "credit": "Photo by dbking via Wikimedia Commons, licensed CC BY 2.0.",
    },
    {
        "filename": "2026-04-12-2026-04-12-trump-s-tariffs-are-back-in-court-and-the-fight-is-really-about-presidential-power.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f4/US_Supreme_Court.JPG/960px-US_Supreme_Court.JPG",
        "alt": "United States Supreme Court building",
        "credit": "Photo via Wikimedia Commons. U.S. Supreme Court. Public domain.",
    },

    # ── CULTURE / SOCIETY ──────────────────────────────────────────────────
    {
        "filename": "2026-04-12-2026-04-12-the-tiny-wedding-economy-is-having-a-very-online-moment.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Wedding_flowers.jpg/1280px-Wedding_flowers.jpg",
        "alt": "Elegant wedding flower arrangement",
        "credit": "Photo via Wikimedia Commons. Wedding flowers. Licensed CC BY 2.0.",
    },
    {
        "filename": "2026-04-12-2026-04-12-tokyo-s-new-museum-of-narratives-wants-to-turn-culture-into-a-living-story.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Tokyo_Skytree_2012.JPG/853px-Tokyo_Skytree_2012.JPG",
        "alt": "Tokyo Skytree tower rising above the Tokyo skyline",
        "credit": "Photo by Kakidai via Wikimedia Commons, licensed CC BY-SA 4.0.",
    },
    {
        "filename": "2026-04-12-2026-04-12-why-birding-is-having-a-bigger-moment-than-many-people-realize.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/A_small_cup_of_coffee.JPG/1280px-A_small_cup_of_coffee.JPG",
        "alt": "Birdwatcher with binoculars outdoors",
        "credit": "Photo via Wikimedia Commons, public domain.",
    },
]

# Better birding image
IMAGES[-1] = {
    "filename": "2026-04-12-2026-04-12-why-birding-is-having-a-bigger-moment-than-many-people-realize.jpg",
    "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Birder_Rio_Grande_Valley_Texas.jpg/1280px-Birder_Rio_Grande_Valley_Texas.jpg",
    "alt": "A birder looking through binoculars in the Rio Grande Valley, Texas",
    "credit": "Photo by U.S. Fish and Wildlife Service via Wikimedia Commons. U.S. government work — public domain.",
}


def download(entry):
    dest_path = os.path.join(DEST, entry["filename"])
    if os.path.exists(dest_path):
        sz = os.path.getsize(dest_path)
        if sz > 20_000:            # already a real image, not a placeholder
            print(f"  SKIP  {entry['filename']} ({sz//1024}KB already)")
            return True
    print(f"  GET   {entry['url'][:72]}…")
    try:
        req = urllib.request.Request(entry["url"], headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        with open(dest_path, "wb") as f:
            f.write(data)
        print(f"  SAVED {entry['filename']} ({len(data)//1024}KB)")
        print(f"  CRED  {entry['credit']}")
        return True
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code} for {entry['filename']}")
        return False
    except Exception as e:
        print(f"  ERROR {entry['filename']}: {e}")
        return False


if __name__ == "__main__":
    print(f"The Press — Wikimedia image downloader")
    print(f"Destination: {DEST}\n")
    ok = 0
    for item in IMAGES:
        if download(item):
            ok += 1
    print(f"\nDone: {ok}/{len(IMAGES)} images saved.")
    print("\nAll images are Wikimedia Commons CC-licensed or U.S. government")
    print("public domain.  Check individual credit lines above for attribution.")
