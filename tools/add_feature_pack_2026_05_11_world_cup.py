#!/usr/bin/env python3
"""Install the May 11, 2026 World Cup feature package."""

from __future__ import annotations

import html
import json
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SLUG = "sports-world-cup-game-day-machine"
FILENAME = f"{SLUG}.html"
BODY_PATH = ROOT / "content" / "bodies" / FILENAME
ASIDE_PATH = ROOT / "content" / "asides" / FILENAME
REPORT_PATH = ROOT / "reporting" / f"{SLUG}-source-stack.md"
MASTER_PATH = ROOT / "master-edition.json"
SEARCH_PATH = ROOT / "search-index.json"

TITLE = "Game Time: The World Cup Is About to Test the World's Matchday Machine"
DEK = (
    "One month before the biggest men's World Cup ever opens, the story is not only soccer. "
    "It is tickets, heat, grass, transit, security, borders, social media, history, and whether "
    "North America can make 104 matches feel like one public event."
)
IMAGE = "assets/article-thumbnails/2026-05-11-world-cup-game-day-machine-thumbnail.jpg"
IMAGE_ALT = (
    "A diverse World Cup crowd moving through a stadium concourse "
    "at dusk, with transit signs, a train, and the pitch beyond."
)


def s(source_id: str, outlet: str, title: str, url: str, note: str) -> dict[str, str]:
    return {"id": source_id, "outlet": outlet, "title": title, "url": url, "note": note}


SOURCES = [
    s("fifa-main", "FIFA", "FIFA World Cup 26 tournament hub", "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026", "Used for the official tournament frame, branding, and current event hub."),
    s("fifa-schedule", "FIFA", "Updated match schedule", "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/updated-fifa-world-cup-2026-match-schedule-now-available", "Used for the June 11 opener, 104-match layout, and July 19 final context."),
    s("fifa-matches", "FIFA", "Matches, fixtures, results and stadiums", "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/match-schedule", "Used for the official match-map reference and city-by-city rhythm."),
    s("fifa-final", "FIFA", "New York New Jersey to host the final", "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/new-york-new-jersey-stadium-host-world-cup-2026-final", "Used for the July 19 final location and the event's end point."),
    s("fifa-hosts-overview", "FIFA", "Hosts, cities and dates overview", "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/fifa-world-cup-2026-hosts-cities-dates-usa-mexico-canada", "Used for the 16-city, three-country geography."),
    s("fifa-host-cities", "FIFA", "Host cities", "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/destination", "Used for the official host-city directory."),
    s("fifa-groups", "FIFA", "Groups, qualification and tie-breakers", "https://www.fifa.com/en/articles/groups-how-teams-qualify-tie-breakers", "Used for the 48-team, 12-group competitive structure."),
    s("fifa-qualified-teams", "FIFA", "Qualified teams", "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/teams", "Used for the expanded field and global participation frame."),
    s("fifa-impact", "Inside FIFA", "Invest in America forum remarks", "https://inside.fifa.com/organisation/president/news/cnbc-invest-in-america-forum-washington-dc-infantino-world-cup-26", "Used for FIFA's public framing of U.S. match load and economic opportunity."),
    s("fifa-tickets", "FIFA", "World Cup ticketing", "https://www.fifa.com/tickets", "Used for official ticketing access and sales-flow context."),
    s("fifa-last-minute", "FIFA", "Last-minute ticket sales phase", "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/last-minute-tickets-sales-phase-to-start-on-1-april", "Used for the current sales phase that opened April 1, 2026."),
    s("fifa-ticket-help", "FIFA Ticketing Help Centre", "World Cup ticketing help centre", "https://gpcustomersupportfwc2026.tickets.fifa.com/hc/en-gb", "Used for ticketing support, exchange, and policy references."),
    s("fifa-resale", "FIFA Ticketing Help Centre", "Do resale exchange prices vary?", "https://gpcustomersupportfwc2026.tickets.fifa.com/hc/en-gb/articles/30547426851613-15-Do-ticket-resale-exchange-prices-vary-on-the-FIFA-Resale-Exchange-Marketplace", "Used for resale-price variation by country, product, and applicable law."),
    s("fifa-resale-market", "FIFA Ticketing Help Centre", "FIFA Resale Exchange Marketplace", "https://gpcustomersupportfwc2026.tickets.fifa.com/hc/en-gb/sections/29894015381533-FIFA-Resale-Exchange-Marketplace", "Used for exchange-market structure and fan resale context."),
    s("fifa-hospitality", "FIFA Hospitality", "FIFA World Cup 26 hospitality", "https://hospitality.fifa.com/en/events/fifa-world-cup-26/", "Used for the premium-access layer and hospitality economy."),
    s("fifa-volunteer", "FIFA Volunteer Platform", "FIFA Volunteer Programme", "https://volunteer.fifa.com/", "Used for the volunteer and public-facing workforce layer."),
    s("fifa-sustainability", "Inside FIFA", "Sustainability", "https://inside.fifa.com/social-impact/sustainability", "Used for FIFA's sustainability posture and host-event responsibility frame."),
    s("fifa-human-rights", "Inside FIFA", "Human rights", "https://inside.fifa.com/social-impact/human-rights", "Used for the human-rights and responsibility frame around mega-events."),
    s("fifa-stadium-guidelines", "FIFA Publications", "Football stadium guidelines", "https://publications.fifa.com/en/football-stadiums-guidelines/", "Used for stadium standards and major-event venue expectations."),
    s("fifa-pitch", "FIFA Publications", "Pitch dimensions and surrounding areas", "https://publications.fifa.com/en/football-stadiums-guidelines/technical-guideline/stadium-guidelines/pitch-dimensions-and-surrounding-areas/", "Used for the technical frame around the field of play."),
    s("fifa-museum-history", "FIFA Museum", "The history of the World Cup", "https://www.fifamuseum.com/en/blog-stories/blog/the-history-of-the-world-cup/", "Used for long-run World Cup history and memory."),
    s("fifa-1930", "FIFA", "Uruguay 1930", "https://www.fifa.com/en/tournaments/mens/worldcup/1930uruguay", "Used for the first World Cup and the tournament's origin story."),
    s("fifa-1994", "FIFA", "USA 1994", "https://www.fifa.com/en/tournaments/mens/worldcup/1994usa", "Used for comparison with the prior U.S.-hosted World Cup."),
    s("fifa-2030", "FIFA", "2030 World Cup host announcement", "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicospainportugalmorocco2030", "Used for the future mega-event calendar and the next century frame."),
    s("fifa-2034", "FIFA", "Saudi Arabia 2034", "https://www.fifa.com/en/tournaments/mens/worldcup/2034saudiarabia", "Used for the future of World Cup scale, climate, and hosting politics."),
    s("fifa-city-mexico-city", "FIFA", "Mexico City host city", "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/destination/mexico/mexico-city", "Used for the opening-city frame."),
    s("fifa-city-guadalajara", "FIFA", "Guadalajara host city", "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/destination/mexico/guadalajara", "Used for Mexico host-city context."),
    s("fifa-city-monterrey", "FIFA", "Monterrey host city", "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/destination/mexico/monterrey", "Used for northern Mexico host-city context."),
    s("fifa-city-toronto", "FIFA", "Toronto host city", "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/destination/canada/toronto", "Used for Toronto host-city context."),
    s("fifa-city-vancouver", "FIFA", "Vancouver host city", "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/destination/canada/vancouver", "Used for Vancouver host-city context."),
    s("fifa-city-atlanta", "FIFA", "Atlanta host city", "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/destination/usa/atlanta", "Used for Atlanta host-city context."),
    s("fifa-city-boston", "FIFA", "Boston host city", "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/destination/usa/boston", "Used for Boston host-city context."),
    s("fifa-city-dallas", "FIFA", "Dallas host city", "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/destination/usa/dallas", "Used for Dallas host-city context."),
    s("fifa-city-houston", "FIFA", "Houston host city", "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/destination/usa/houston", "Used for Houston host-city context."),
    s("fifa-city-kansas-city", "FIFA", "Kansas City host city", "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/destination/usa/kansas-city", "Used for Kansas City host-city context."),
    s("fifa-city-los-angeles", "FIFA", "Los Angeles host city", "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/destination/usa/los-angeles", "Used for Los Angeles host-city context."),
    s("fifa-city-miami", "FIFA", "Miami host city", "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/destination/usa/miami", "Used for Miami host-city context."),
    s("fifa-city-nynj", "FIFA", "New York New Jersey host city", "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/destination/usa/new-york-new-jersey", "Used for the final-region host-city context."),
    s("fifa-city-philadelphia", "FIFA", "Philadelphia host city", "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/destination/usa/philadelphia", "Used for Philadelphia host-city context."),
    s("fifa-city-bay-area", "FIFA", "San Francisco Bay Area host city", "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/destination/usa/san-francisco-bay-area", "Used for Bay Area host-city context."),
    s("fifa-city-seattle", "FIFA", "Seattle host city", "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/destination/usa/seattle", "Used for Seattle host-city context."),
    s("atlanta-host", "Atlanta FIFA World Cup 26", "Atlanta host committee", "https://www.atlfwc26.com/", "Used for local host-committee programming and civic preparation."),
    s("boston-host", "Boston FIFA World Cup 26", "Boston host committee", "https://www.bostonfwc26.org/", "Used for local host-committee programming and civic preparation."),
    s("dallas-host", "Dallas FIFA World Cup 26", "Dallas host committee", "https://www.dallasfwc26.com/", "Used for local host-committee programming and civic preparation."),
    s("houston-host", "Houston FIFA World Cup 26", "Houston host committee", "https://www.houstonfwc26.com/", "Used for local host-committee programming and civic preparation."),
    s("kc-host", "Kansas City FIFA World Cup 26", "Kansas City host committee", "https://www.kansascityfwc26.com/", "Used for local host-committee programming and civic preparation."),
    s("la-host", "Los Angeles World Cup 26", "Los Angeles host committee", "https://www.laworldcup26.com/", "Used for local host-committee programming and civic preparation."),
    s("miami-host", "Miami FIFA World Cup 26", "Miami host committee", "https://www.miamifwc26.com/", "Used for local host-committee programming and civic preparation."),
    s("nynj-host", "New York New Jersey FIFA World Cup 26", "NYNJ host committee", "https://www.nynjfwc26.com/", "Used for final-region host-committee programming."),
    s("philly-host", "Philadelphia Soccer 2026", "Philadelphia host committee", "https://www.phlworldcup26.com/", "Used for local host-committee programming and civic preparation."),
    s("seattle-host", "Seattle FIFA World Cup 26", "Seattle host committee", "https://fwc26seattle.com/", "Used for local host-committee programming and civic preparation."),
    s("toronto-host", "City of Toronto", "FIFA World Cup 26 Toronto", "https://www.toronto.ca/explore-enjoy/festivals-events/fifa-world-cup-26/", "Used for Toronto municipal planning and public-information context."),
    s("vancouver-host", "Vancouver FIFA World Cup 26", "Vancouver host city", "https://vancouverfwc26.ca/", "Used for Vancouver host-city planning and public-information context."),
    s("bay-area-host", "Bay Area Host Committee", "Bay Area World Cup host committee", "https://www.bayareahostcommittee.com/", "Used for Bay Area civic and sports-event preparation."),
    s("dot-transit", "U.S. Department of Transportation", "World Cup public-transit funding", "https://www.transportation.gov/briefing-room/trumps-transportation-secretary-announces-100-million-funding-enhance-public", "Used for the $100.3 million transit-funding announcement for U.S. host cities."),
    s("fta-transit", "Federal Transit Administration", "Transit funding for World Cup host cities", "https://www.transit.dot.gov/", "Used for federal transit context and U.S. host-city operating support."),
    s("nj-transit-plan", "NJ TRANSIT", "NYNJ regional stadium mobility plan", "https://www.njtransit.com/press-releases/fifa-world-cup-2026tm-new-york-new-jersey-host-committee-and-nj-transit-announce", "Used for the NYNJ stadium mobility plan and first ticketing details."),
    s("nj-transit-reduced", "NBC New York", "NJ Transit lowers World Cup train fare", "https://www.nbcnewyork.com/world-cup/nj-transit-lowers-price-train-tickets-world-cup-games-metlife-stadium/6499439/", "Used for the May 2026 reduction from $150 to $105 for special MetLife roundtrip rail tickets."),
    s("port-authority", "Port Authority of New York and New Jersey", "Regional transportation agency", "https://www.panynj.gov/", "Used for the final-region transportation context."),
    s("mta", "MTA", "New York metropolitan transit", "https://new.mta.info/", "Used for regional movement around the NYNJ host area."),
    s("amtrak", "Amtrak", "Intercity rail", "https://www.amtrak.com/", "Used for regional intercity rail context."),
    s("marta", "MARTA", "Atlanta transit", "https://www.itsmarta.com/", "Used for host-city transit context."),
    s("septa", "SEPTA", "Philadelphia transit", "https://www.septa.org/", "Used for host-city transit context."),
    s("mbta", "MBTA", "Boston-area transit", "https://www.mbta.com/", "Used for host-city transit context."),
    s("dart", "Dallas Area Rapid Transit", "DART", "https://www.dart.org/", "Used for Dallas-area transit context."),
    s("houston-metro", "Houston METRO", "Houston transit", "https://www.ridemetro.org/", "Used for Houston transit context."),
    s("la-metro", "LA Metro", "Los Angeles transit", "https://www.metro.net/", "Used for Los Angeles transit context."),
    s("sound-transit", "Sound Transit", "Seattle regional transit", "https://www.soundtransit.org/", "Used for Seattle transit context."),
    s("king-county-metro", "King County Metro", "Seattle local transit", "https://kingcounty.gov/en/dept/metro", "Used for Seattle local transit context."),
    s("kcata", "RideKC", "Kansas City transit", "https://ridekc.org/", "Used for Kansas City transit context."),
    s("bart", "BART", "Bay Area rapid transit", "https://www.bart.gov/", "Used for Bay Area transit context."),
    s("caltrain", "Caltrain", "Bay Area rail", "https://www.caltrain.com/", "Used for Bay Area rail context."),
    s("translink", "TransLink", "Vancouver regional transit", "https://www.translink.ca/", "Used for Vancouver transit context."),
    s("ttc", "TTC", "Toronto transit", "https://www.ttc.ca/", "Used for Toronto transit context."),
    s("go-transit", "GO Transit", "Greater Toronto regional rail", "https://www.gotransit.com/", "Used for regional movement around Toronto."),
    s("cdmx-metro", "Sistema de Transporte Colectivo Metro", "Mexico City Metro", "https://www.metro.cdmx.gob.mx/", "Used for Mexico City movement context."),
    s("ap-final-ticket", "Associated Press", "Top World Cup final ticket price rises to $10,990", "https://apnews.com/article/world-cup-tickets-sale-e4bb8a9eb9aa285f55caa4b9405fb182", "Used for the top final price, dynamic-pricing context, and April sales reopening."),
    s("ap-ticket-general", "Associated Press", "World Cup tickets remain on sale at high prices", "https://apnews.com/article/world-cup-tickets-9a5a713fabdd0ec3743222e5b6c8a384", "Used for group-stage availability, entry-price examples, and public access context."),
    s("ap-heat", "Associated Press", "Extreme heat could threaten World Cup players and fans", "https://apnews.com/article/world-cup-climate-change-extreme-heat-safety-soccer-481b018c2a0bc6fd3187ba6505402ee9", "Used for heat-risk framing and wet-bulb globe temperature examples."),
    s("ap-iran", "Associated Press", "Iran seeks World Cup assurances", "https://apnews.com/article/iran-world-cup-soccer-federation-fifa-13a50d2be82ac00875f33f5d770306f2", "Used for visa, security, and geopolitical participation context."),
    s("reuters-grass", "Reuters Connect", "Pitch installation at MetLife Stadium", "https://www.reutersconnect.com/item/pitch-installation-at-metlife-stadium/dGFnOnJldXRlcnMuY29tLDIwMjY6bmV3c21sX1JDMks0TEFGSkJBTw", "Used for the May 7, 2026 real-grass pitch installation detail."),
    s("guardian-security", "The Guardian", "World Cup terrorism-risk report", "https://www.theguardian.com/football/2026/may/10/fifa-world-cup-terrorism-risk-iran-war", "Used for soft-target and security-risk context around U.S. matches."),
    s("canada-security", "Public Safety Canada", "World Cup public-safety funding", "https://www.canada.ca/en/public-safety-canada/news/2026/04/government-of-canada-announces-up-to-145-million-to-support-public-safety-and-security-for-the-fifa-world-cup-2026.html", "Used for Canada's up-to-C$145-million public-safety support."),
    s("dhs-sear", "U.S. Department of Homeland Security", "Special Event Assessment Rating", "https://www.dhs.gov/special-event-assessment-rating", "Used for U.S. major-event security framework context."),
    s("secret-service-nsse", "U.S. Secret Service", "National Special Security Events", "https://www.secretservice.gov/protection/events", "Used for National Special Security Event context."),
    s("cisa-events", "CISA", "Securing major public events", "https://www.cisa.gov/topics/physical-security/security-major-public-events", "Used for soft-target and major-event protection context."),
    s("state-visas", "U.S. Department of State", "U.S. visas", "https://travel.state.gov/content/travel/en/us-visas.html", "Used for international travel and visa context."),
    s("cbp-travel", "U.S. Customs and Border Protection", "Travel", "https://www.cbp.gov/travel", "Used for border-entry and arrival context."),
    s("tsa-screening", "Transportation Security Administration", "Security screening", "https://www.tsa.gov/travel/security-screening", "Used for travel-screening and airport-flow context."),
    s("nws-heat", "National Weather Service", "Heat safety", "https://www.weather.gov/safety/heat", "Used for public heat-safety context."),
    s("cdc-heat", "CDC", "Heat and health", "https://www.cdc.gov/heat-health/", "Used for health-risk context around outdoor queues and fan festivals."),
    s("osha-heat", "OSHA", "Heat exposure", "https://www.osha.gov/heat-exposure", "Used for worker heat-risk context."),
    s("noaa-climate", "NOAA", "Climate information", "https://www.noaa.gov/climate", "Used for climate and weather-risk context."),
    s("nasa-climate", "NASA", "Global climate change", "https://climate.nasa.gov/", "Used for the broader climate-risk frame."),
    s("who-mass-gatherings", "World Health Organization", "Mass gatherings", "https://www.who.int/health-topics/mass-gatherings", "Used for public-health planning around large events."),
    s("ohchr-guiding", "OHCHR", "UN Guiding Principles on Business and Human Rights", "https://www.ohchr.org/en/business-and-human-rights/un-guiding-principles-business-and-human-rights", "Used for the rights-and-responsibility frame around mega-events."),
    s("hrw-sport", "Human Rights Watch", "Sport and human rights", "https://www.hrw.org/topic/sport-and-human-rights", "Used for civil-society scrutiny around sports mega-events."),
    s("amnesty-sport", "Amnesty International", "Sport and human rights", "https://www.amnesty.org/en/search/?q=sport%20human%20rights", "Used for civil-society context on sports and rights."),
    s("fifa-x", "FIFA World Cup", "Official X account", "https://x.com/FIFAWorldCup", "Used for the live social-media pulse and official tournament messaging."),
    s("fifa-instagram", "FIFA World Cup", "Official Instagram", "https://www.instagram.com/fifaworldcup/", "Used for the visual social-media layer of the tournament."),
    s("fifa-tiktok", "FIFA World Cup", "Official TikTok", "https://www.tiktok.com/@fifaworldcup", "Used for short-video tournament culture."),
    s("fifa-youtube", "FIFA", "Official YouTube channel", "https://www.youtube.com/fifa", "Used for highlights, explainers, and global video distribution."),
    s("fifa-facebook", "FIFA World Cup", "Official Facebook", "https://www.facebook.com/fifaworldcup/", "Used for broad social distribution."),
    s("fifa-threads", "FIFA World Cup", "Official Threads", "https://www.threads.net/@fifaworldcup", "Used for the platform-spread of official tournament communication."),
    s("ussoccer", "U.S. Soccer", "U.S. Soccer", "https://www.ussoccer.com/", "Used for U.S. national-team context."),
    s("canada-soccer", "Canada Soccer", "Canada Soccer", "https://canadasoccer.com/", "Used for Canada national-team and host-country context."),
    s("miseleccion", "Mexican National Team", "Mi Seleccion", "https://miseleccion.mx/", "Used for Mexico national-team and host-country context."),
    s("fox-sports", "FOX Sports", "FIFA World Cup coverage", "https://www.foxsports.com/soccer/fifa-world-cup-men", "Used for U.S. English-language broadcast context."),
    s("telemundo", "Telemundo Deportes", "FIFA World Cup coverage", "https://www.telemundodeportes.com/futbol/copa-mundial-de-la-fifa-2026", "Used for U.S. Spanish-language broadcast context."),
    s("tsn", "TSN", "Soccer", "https://www.tsn.ca/soccer", "Used for Canadian sports-media context."),
    s("cbc-sports", "CBC Sports", "Soccer", "https://www.cbc.ca/sports/soccer", "Used for Canadian sports and civic coverage context."),
    s("bbc-world-cup", "BBC Sport", "World Cup", "https://www.bbc.com/sport/football/world-cup", "Used for global English-language context."),
    s("marca-world-cup", "Marca", "Mundial 2026", "https://www.marca.com/futbol/mundial.html", "Used for Spanish-language global football context."),
    s("espn-world-cup", "ESPN", "FIFA World Cup", "https://www.espn.com/soccer/league/_/name/fifa.world", "Used for U.S. sports-news and competition context."),
    s("the-athletic-world-cup", "The Athletic", "World Cup", "https://www.nytimes.com/athletic/football/world-cup/", "Used for sports-analysis context."),
    s("soccerway", "Soccerway", "World Cup", "https://int.soccerway.com/international/world/world-cup/", "Used for match-data and historical competition context."),
    s("rsssf", "RSSSF", "World Cup archive", "https://www.rsssf.org/tablesw/worldcup.html", "Used for independent historical record context."),
]


SOURCE_BY_ID = {item["id"]: item for item in SOURCES}


def source_link(source_id: str) -> str:
    source = SOURCE_BY_ID[source_id]
    return source["url"]


def inline_source(source_id: str, label: str = "source note") -> str:
    return f'<span class="source-ref"><a href="#source-{source_id}">{html.escape(label)}</a></span>'


def img(path: str, alt: str, caption: str, link_source: str) -> dict[str, str]:
    return {
        "path": path,
        "alt": alt,
        "caption": caption,
        "link": source_link(link_source),
    }


GALLERY_IMAGES = [
    img(
        "assets/social/photoreal/world-cup-2026-ticketing-entry.jpg",
        "Diverse World Cup fans moving through a ticketing and entry checkpoint.",
        "Ticketing and entry",
        "ap-final-ticket",
    ),
    img(
        "assets/social/photoreal/world-cup-2026-transit-hub.jpg",
        "A packed World Cup transit hub with multilingual signs and diverse supporters.",
        "Transit and crowd flow",
        "nj-transit-reduced",
    ),
    img(
        "assets/social/photoreal/world-cup-2026-heat-cooling.jpg",
        "World Cup fans and workers using shade, water, and cooling stations in summer heat.",
        "Heat and public safety",
        "ap-heat",
    ),
    img(
        "assets/social/photoreal/world-cup-2026-grass-pitch.jpg",
        "Grounds crews preparing a natural-grass World Cup pitch inside a large stadium.",
        "Grass and stadium conversion",
        "reuters-grass",
    ),
    img(
        "assets/social/photoreal/world-cup-2026-watch-party.jpg",
        "A diverse outdoor World Cup watch party at night with flags, screens, and phones.",
        "Social media and watch parties",
        "fifa-tiktok",
    ),
    img(
        "assets/social/photoreal/world-cup-2026-history-future.jpg",
        "A World Cup timeline display linking older tournament memories with future host cities.",
        "History and future",
        "fifa-museum-history",
    ),
]


RAIL_IMAGE_PATHS = [
    "assets/social/photoreal/world-cup-2026-rail/01-schedule-map.jpg",
    "assets/social/photoreal/world-cup-2026-rail/02-format-board.jpg",
    "assets/social/photoreal/world-cup-2026-rail/03-ticket-access.jpg",
    "assets/social/photoreal/world-cup-2026-rail/04-resale-policy.jpg",
    "assets/social/photoreal/world-cup-2026-rail/05-final-rail-route.jpg",
    "assets/social/photoreal/world-cup-2026-rail/06-transit-funding.jpg",
    "assets/social/photoreal/world-cup-2026-rail/07-heat-risk.jpg",
    "assets/social/photoreal/world-cup-2026-rail/08-cooling-tent.jpg",
    "assets/social/photoreal/world-cup-2026-rail/09-grass-installation.jpg",
    "assets/social/photoreal/world-cup-2026-rail/10-pitch-guidelines.jpg",
    "assets/social/photoreal/world-cup-2026-rail/11-canada-security.jpg",
    "assets/social/photoreal/world-cup-2026-rail/12-visas-border.jpg",
    "assets/social/photoreal/world-cup-2026-rail/13-short-video-watch-party.jpg",
    "assets/social/photoreal/world-cup-2026-rail/14-visual-feed-editors.jpg",
    "assets/social/photoreal/world-cup-2026-rail/15-us-host-pressure.jpg",
    "assets/social/photoreal/world-cup-2026-rail/16-mexico-opening-memory.jpg",
    "assets/social/photoreal/world-cup-2026-rail/17-world-cup-history.jpg",
    "assets/social/photoreal/world-cup-2026-rail/18-future-hosts.jpg",
    "assets/social/photoreal/world-cup-2026-rail/19-atlanta-local-stage.jpg",
    "assets/social/photoreal/world-cup-2026-rail/20-seattle-civic-plan.jpg",
    "assets/social/photoreal/world-cup-2026-rail/21-mass-gatherings.jpg",
    "assets/social/photoreal/world-cup-2026-rail/22-event-security.jpg",
    "assets/social/photoreal/world-cup-2026-rail/23-broadcast-camera-platform.jpg",
    "assets/social/photoreal/world-cup-2026-rail/24-spanish-language-booth.jpg",
    "assets/social/photoreal/world-cup-2026-rail/25-mixed-zone-live-wire.jpg",
    "assets/social/photoreal/world-cup-2026-rail/26-community-replay.jpg",
    "assets/social/photoreal/world-cup-2026-rail/27-multigenerational-watch-party.jpg",
    "assets/social/photoreal/world-cup-2026-rail/28-barbershop-conversation.jpg",
    "assets/social/photoreal/world-cup-2026-rail/29-canada-host-team.jpg",
    "assets/social/photoreal/world-cup-2026-rail/30-canada-public-square.jpg",
    "assets/social/photoreal/world-cup-2026-rail/31-community-hall-coverage.jpg",
    "assets/social/photoreal/world-cup-2026-rail/32-global-travel-view.jpg",
    "assets/social/photoreal/world-cup-2026-rail/33-spanish-sports-bar.jpg",
    "assets/social/photoreal/world-cup-2026-rail/34-sidewalk-tactics-debate.jpg",
    "assets/social/photoreal/world-cup-2026-rail/35-late-night-press-tribune.jpg",
    "assets/social/photoreal/world-cup-2026-rail/36-records-room.jpg",
    "assets/social/photoreal/world-cup-2026-rail/37-working-archive.jpg",
    "assets/social/photoreal/world-cup-2026-rail/38-boston-tavern-kitchen.jpg",
    "assets/social/photoreal/world-cup-2026-rail/39-dallas-concession-prep.jpg",
    "assets/social/photoreal/world-cup-2026-rail/40-houston-cooling-kitchen.jpg",
    "assets/social/photoreal/world-cup-2026-rail/41-kansas-city-park.jpg",
    "assets/social/photoreal/world-cup-2026-rail/42-los-angeles-street-food.jpg",
    "assets/social/photoreal/world-cup-2026-rail/43-miami-waterfront-fan-zone.jpg",
    "assets/social/photoreal/world-cup-2026-rail/44-ny-nj-diner.jpg",
    "assets/social/photoreal/world-cup-2026-rail/45-philadelphia-history-street.jpg",
    "assets/social/photoreal/world-cup-2026-rail/46-toronto-waterfront-park.jpg",
    "assets/social/photoreal/world-cup-2026-rail/47-vancouver-seawall.jpg",
    "assets/social/photoreal/world-cup-2026-rail/48-bay-area-backyard.jpg",
    "assets/social/photoreal/world-cup-2026-rail/49-ny-subway-after-match.jpg",
    "assets/social/photoreal/world-cup-2026-rail/50-la-light-rail-interior.jpg",
    "assets/social/photoreal/world-cup-2026-rail/51-vancouver-rain-bus.jpg",
    "assets/social/photoreal/world-cup-2026-rail/52-mexico-city-metro-car.jpg",
]


CARDS = [
    {"class": "official", "avatar": "FIFA", "outlet": "FIFA", "sub": "Schedule", "kicker": "Tournament map", "headline": "104 matches, 16 host cities, three countries.", "deck": "The schedule is the continent's operating plan.", "body": "The official schedule sets the June 11 opener and July 19 final.", "source": "fifa-schedule"},
    {"class": "source", "avatar": "48", "outlet": "FIFA", "sub": "Format", "kicker": "New field", "headline": "48 teams. 12 groups. 32 knockout places.", "deck": "Expansion changes the bracket and the public square.", "body": "The new field increases inclusion, inventory, travel, and expectation.", "source": "fifa-groups"},
    {"class": "news", "avatar": "AP", "outlet": "Associated Press", "sub": "Tickets", "kicker": "Access", "headline": "The final's top listed ticket reached $10,990.", "deck": "Dynamic pricing moved affordability into the main story.", "body": "AP tracked the April price jump as sales reopened.", "source": "ap-final-ticket", "image": GALLERY_IMAGES[0]},
    {"class": "official", "avatar": "$", "outlet": "FIFA Ticketing", "sub": "Resale", "kicker": "Policy", "headline": "Resale rules differ by country and law.", "deck": "The same tournament carries different market rules.", "body": "FIFA's help centre lays out variation across Mexico, Ontario, and other markets.", "source": "fifa-resale"},
    {"class": "place", "avatar": "NYNJ", "outlet": "NJ TRANSIT", "sub": "Mobility", "kicker": "Final route", "headline": "The ride to MetLife became its own ticketed system.", "deck": "The special roundtrip fare was reduced after backlash.", "body": "Local reporting shows a May reduction from $150 to $105.", "source": "nj-transit-reduced", "image": GALLERY_IMAGES[1]},
    {"class": "official", "avatar": "DOT", "outlet": "U.S. DOT", "sub": "Transit", "kicker": "Federal boost", "headline": "$100.3 million for U.S. host-city transit.", "deck": "Moving fans is now federal event infrastructure.", "body": "The funding supports planning, capital, and operating expenses tied to matches.", "source": "dot-transit"},
    {"class": "news", "avatar": "AP", "outlet": "Associated Press", "sub": "Heat", "kicker": "Climate", "headline": "Summer heat is part of the bracket.", "deck": "Cooling is a competitive and public-safety issue.", "body": "AP reported on wet-bulb globe temperature risks for players, fans, and workers.", "source": "ap-heat", "image": GALLERY_IMAGES[2]},
    {"class": "utility", "avatar": "NWS", "outlet": "National Weather Service", "sub": "Safety", "kicker": "Public health", "headline": "Water, shade, and timing are not side details.", "deck": "Heat planning follows fans outside the stadium bowl.", "body": "Federal heat-safety guidance helps frame the fan and worker risk.", "source": "nws-heat"},
    {"class": "source", "avatar": "REU", "outlet": "Reuters", "sub": "Pitch", "kicker": "Surface", "headline": "Real grass is being installed at MetLife.", "deck": "Even the ground has to be converted for the world's game.", "body": "Reuters documented sprinklers watering the newly installed pitch on May 7.", "source": "reuters-grass", "image": GALLERY_IMAGES[3]},
    {"class": "guide", "avatar": "PITCH", "outlet": "FIFA", "sub": "Guidelines", "kicker": "Field of play", "headline": "The pitch is rules, safety, rhythm, and trust.", "deck": "A temporary field has to play like a permanent promise.", "body": "FIFA's stadium guidance treats the pitch as technical infrastructure.", "source": "fifa-pitch"},
    {"class": "official", "avatar": "CAN", "outlet": "Public Safety Canada", "sub": "Security", "kicker": "Safety", "headline": "Canada pledged up to C$145 million for World Cup safety.", "deck": "Public safety is a national promise and a host-city cost.", "body": "The money supports Toronto and Vancouver operations.", "source": "canada-security"},
    {"class": "news", "avatar": "AP", "outlet": "Associated Press", "sub": "Visas", "kicker": "Border test", "headline": "Iran says it will play, but wants assurances.", "deck": "The bracket arrives with geopolitics attached.", "body": "AP reported Iranian federation concerns about visas, security, and treatment.", "source": "ap-iran"},
    {"class": "social", "avatar": "TOK", "outlet": "FIFA World Cup", "sub": "TikTok", "kicker": "Short video", "headline": "The World Cup will be watched, clipped, remixed, and argued in real time.", "deck": "The crowd now lives in the stadium and in the feed.", "body": "Official short-video channels shape the tournament's global social rhythm.", "source": "fifa-tiktok", "image": GALLERY_IMAGES[4]},
    {"class": "social", "avatar": "IG", "outlet": "FIFA World Cup", "sub": "Instagram", "kicker": "Visual feed", "headline": "The official image stream is part of the event itself.", "deck": "Culture travels through photos before the whistle stops echoing.", "body": "Instagram becomes a live gallery of teams, supporters, cities, and moments.", "source": "fifa-instagram"},
    {"class": "official", "avatar": "US", "outlet": "U.S. Soccer", "sub": "Host team", "kicker": "Home pressure", "headline": "The U.S. hosts most of the event and carries a different kind of expectation.", "deck": "The tournament is a test of soccer's American ceiling.", "body": "U.S. Soccer's public channels anchor the host-team frame.", "source": "ussoccer"},
    {"class": "official", "avatar": "MEX", "outlet": "Mi Seleccion", "sub": "Opening host", "kicker": "Mexico", "headline": "Mexico links 2026 to 1970 and 1986.", "deck": "History will be present before the opening whistle.", "body": "The Mexican national-team record and Mexico City opener give the tournament deep memory.", "source": "miseleccion"},
    {"class": "source", "avatar": "HIS", "outlet": "FIFA Museum", "sub": "History", "kicker": "World memory", "headline": "Every World Cup borrows from the ones before it.", "deck": "The first tournament and the 1994 U.S. boom both live inside 2026.", "body": "Historical sources frame the event as a century-long civic and sporting project.", "source": "fifa-museum-history", "image": GALLERY_IMAGES[5]},
    {"class": "official", "avatar": "2030", "outlet": "FIFA", "sub": "Future hosts", "kicker": "Next century", "headline": "The future of the World Cup is already on the calendar.", "deck": "2026 is a preview of how big the event can become.", "body": "The 2030 and 2034 host cycles show the World Cup's expanding geography.", "source": "fifa-2030"},
    {"class": "place", "avatar": "ATL", "outlet": "Atlanta FWC26", "sub": "Host city", "kicker": "Local stage", "headline": "Host committees turn the tournament into street-level work.", "deck": "The event is planned one city at a time.", "body": "Local committees connect stadium plans to fan festivals, volunteers, and residents.", "source": "atlanta-host"},
    {"class": "place", "avatar": "SEA", "outlet": "Seattle FWC26", "sub": "Host city", "kicker": "Civic plan", "headline": "The host map is continental, but the work is local.", "deck": "Every city inherits the same brand and a different set of problems.", "body": "Seattle's host committee is one of the public windows into that local layer.", "source": "seattle-host"},
    {"class": "official", "avatar": "WHO", "outlet": "WHO", "sub": "Mass gatherings", "kicker": "Public health", "headline": "A crowd is a living system.", "deck": "Large events need health planning beyond emergency rooms.", "body": "Mass-gathering guidance helps frame the health side of fan movement.", "source": "who-mass-gatherings"},
    {"class": "official", "avatar": "DHS", "outlet": "DHS", "sub": "Events", "kicker": "Security frame", "headline": "Mega-event security is layered, not theatrical.", "deck": "The obvious gate is only one part of the risk map.", "body": "DHS event-rating materials help explain the federal security architecture.", "source": "dhs-sear"},
    {"class": "news", "avatar": "FOX", "outlet": "FOX Sports", "sub": "Broadcast", "kicker": "Screens", "headline": "The tournament will be a TV event, a streaming event, and a phone event.", "deck": "Broadcast rights meet the social-media public square.", "body": "U.S. broadcast coverage turns the tournament into a national habit for five weeks.", "source": "fox-sports"},
    {"class": "news", "avatar": "TEL", "outlet": "Telemundo Deportes", "sub": "Broadcast", "kicker": "Language", "headline": "Spanish-language coverage is central, not secondary.", "deck": "The host continent already speaks the game's biggest languages.", "body": "Telemundo's World Cup coverage is part of the tournament's U.S. cultural reach.", "source": "telemundo"},
    {"class": "social", "avatar": "X", "outlet": "FIFA World Cup", "sub": "X", "kicker": "Live wire", "headline": "The fastest official pulse will live in the scrolling feed.", "deck": "News, clips, lineups, and reaction will move at match speed.", "body": "The official X account is one of the tournament's real-time distribution channels.", "source": "fifa-x"},
    {"class": "social", "avatar": "YT", "outlet": "FIFA", "sub": "YouTube", "kicker": "Video shelf", "headline": "Highlights will become the tournament's global second language.", "deck": "YouTube gives fans a way back into the match after the whistle.", "body": "FIFA's channel anchors highlights, archive video, explainers, and long-tail viewing.", "source": "fifa-youtube"},
    {"class": "social", "avatar": "FB", "outlet": "FIFA World Cup", "sub": "Facebook", "kicker": "Broad reach", "headline": "Older platforms still matter when the whole world is watching.", "deck": "The World Cup audience is not confined to one feed.", "body": "Facebook remains part of official global distribution for tournament moments.", "source": "fifa-facebook"},
    {"class": "social", "avatar": "TH", "outlet": "FIFA World Cup", "sub": "Threads", "kicker": "Platform spread", "headline": "The same match will become different conversations on different apps.", "deck": "Fragmented media is now a matchday condition.", "body": "Threads adds another official lane for quick tournament updates and reaction.", "source": "fifa-threads"},
    {"class": "official", "avatar": "CAN", "outlet": "Canada Soccer", "sub": "Host team", "kicker": "First men's host run", "headline": "Canada's home tournament has a different national weight.", "deck": "The host-country story is also a program-building story.", "body": "Canada Soccer's public channels frame the national-team side of the event.", "source": "canada-soccer"},
    {"class": "news", "avatar": "TSN", "outlet": "TSN", "sub": "Canada media", "kicker": "North screen", "headline": "Canadian coverage will make the tournament local every day.", "deck": "A host nation becomes real through daily repetition.", "body": "TSN's soccer coverage is one part of Canada's World Cup media layer.", "source": "tsn"},
    {"class": "news", "avatar": "CBC", "outlet": "CBC Sports", "sub": "Canada media", "kicker": "Public signal", "headline": "Public sports coverage helps turn matches into civic conversation.", "deck": "The story lives beyond kickoff windows.", "body": "CBC Sports is part of the broader Canadian sports-media environment around the event.", "source": "cbc-sports"},
    {"class": "news", "avatar": "BBC", "outlet": "BBC Sport", "sub": "Global media", "kicker": "Outside view", "headline": "The world will also watch the hosts watching themselves.", "deck": "International coverage is a mirror for North America.", "body": "BBC's World Cup coverage supplies a global English-language reference point.", "source": "bbc-world-cup"},
    {"class": "news", "avatar": "MAR", "outlet": "Marca", "sub": "Spanish media", "kicker": "Spanish lens", "headline": "Spanish-language football culture will be central to the tournament's sound.", "deck": "Mexico, the U.S. and global fans make that unavoidable.", "body": "Marca's Mundial coverage is part of the Spanish-language global football record.", "source": "marca-world-cup"},
    {"class": "news", "avatar": "ESPN", "outlet": "ESPN", "sub": "Sports desk", "kicker": "Daily debate", "headline": "The World Cup becomes a month-long argument machine.", "deck": "Sports networks will turn every matchday into a national conversation.", "body": "ESPN's World Cup page sits in the daily U.S. sports-news layer.", "source": "espn-world-cup"},
    {"class": "source", "avatar": "ATH", "outlet": "The Athletic", "sub": "Analysis", "kicker": "Deep bench", "headline": "Tactics, travel, labor, and money need room for longer reads.", "deck": "The tournament deserves analysis beyond the final score.", "body": "The Athletic's World Cup desk adds another layer of match and business analysis.", "source": "the-athletic-world-cup"},
    {"class": "source", "avatar": "DATA", "outlet": "Soccerway", "sub": "Data", "kicker": "Match record", "headline": "Scores become history only when they are findable.", "deck": "The data layer is part of the public memory.", "body": "Soccerway provides match and competition records that help track the field.", "source": "soccerway"},
    {"class": "source", "avatar": "RSS", "outlet": "RSSSF", "sub": "Archive", "kicker": "Long record", "headline": "The World Cup's past is a working archive, not decoration.", "deck": "A century of results gives 2026 its scale.", "body": "RSSSF's World Cup archive helps anchor the historical record outside official channels.", "source": "rsssf"},
    {"class": "place", "avatar": "BOS", "outlet": "Boston FWC26", "sub": "Host city", "kicker": "New England", "headline": "Boston's World Cup is a regional transportation and culture test.", "deck": "Gillette turns one matchday into a metro problem.", "body": "Boston's host committee is a public doorway into the local plan.", "source": "boston-host"},
    {"class": "place", "avatar": "DAL", "outlet": "Dallas FWC26", "sub": "Host city", "kicker": "Texas scale", "headline": "Dallas has stadium power and summer stakes.", "deck": "The local challenge is access, heat, and massive-event flow.", "body": "Dallas host materials frame one of the largest U.S. World Cup stages.", "source": "dallas-host"},
    {"class": "place", "avatar": "HOU", "outlet": "Houston FWC26", "sub": "Host city", "kicker": "Gulf heat", "headline": "Houston's test starts before fans reach the gate.", "deck": "Heat, travel, and visitor movement sit under the matchday story.", "body": "Houston's host committee gives the local event infrastructure a public face.", "source": "houston-host"},
    {"class": "place", "avatar": "KC", "outlet": "Kansas City FWC26", "sub": "Host city", "kicker": "Midwest stage", "headline": "Kansas City gets to prove what soccer culture looks like away from the coasts.", "deck": "A smaller market can still make a huge sound.", "body": "Kansas City's host committee tracks the civic layer around its matches.", "source": "kc-host"},
    {"class": "place", "avatar": "LA", "outlet": "Los Angeles World Cup 26", "sub": "Host city", "kicker": "Entertainment capital", "headline": "Los Angeles can sell spectacle; the harder part is movement.", "deck": "The tournament arrives in a city that already knows mega-events.", "body": "Los Angeles host materials frame the local stage before 2028's Olympics follow.", "source": "la-host"},
    {"class": "place", "avatar": "MIA", "outlet": "Miami FWC26", "sub": "Host city", "kicker": "Americas hub", "headline": "Miami makes the World Cup feel hemispheric.", "deck": "Language, migration, and football culture already meet there.", "body": "Miami's host committee connects the event to one of the sport's natural U.S. gateways.", "source": "miami-host"},
    {"class": "place", "avatar": "NYNJ", "outlet": "NYNJ FWC26", "sub": "Host city", "kicker": "Final stage", "headline": "The final region is not one city; it is a whole operating area.", "deck": "That makes coordination the real venue.", "body": "The NYNJ host committee anchors the final-region planning story.", "source": "nynj-host"},
    {"class": "place", "avatar": "PHL", "outlet": "Philadelphia Soccer 2026", "sub": "Host city", "kicker": "Semiquincentennial", "headline": "Philadelphia hosts soccer inside a bigger national anniversary year.", "deck": "The city will carry history and event traffic at once.", "body": "Philadelphia's committee frames the matchday plan in a loaded civic calendar.", "source": "philly-host"},
    {"class": "place", "avatar": "TOR", "outlet": "City of Toronto", "sub": "Host city", "kicker": "Canada stage", "headline": "Toronto's World Cup is a city-service test as much as a sports event.", "deck": "Public information becomes part of the fan experience.", "body": "Toronto's municipal page is a public reference for local planning.", "source": "toronto-host"},
    {"class": "place", "avatar": "VAN", "outlet": "Vancouver FWC26", "sub": "Host city", "kicker": "Pacific stage", "headline": "Vancouver brings transit bones and international visitor pressure.", "deck": "A beautiful setting still needs a working matchday.", "body": "Vancouver's host page tracks the city-facing side of the tournament.", "source": "vancouver-host"},
    {"class": "place", "avatar": "BAY", "outlet": "Bay Area Host Committee", "sub": "Host city", "kicker": "Regional event", "headline": "The Bay Area's venue sits inside a regional transport puzzle.", "deck": "The match is local, but the arrival pattern is regional.", "body": "The Bay Area Host Committee frames the local sports and civic buildout.", "source": "bay-area-host"},
    {"class": "utility", "avatar": "MTA", "outlet": "MTA", "sub": "Regional transit", "kicker": "NY movement", "headline": "The final region depends on more than the stadium rail spur.", "deck": "New York movement is a system of systems.", "body": "MTA service is part of the broader regional movement around the NYNJ host area.", "source": "mta"},
    {"class": "utility", "avatar": "LA", "outlet": "LA Metro", "sub": "Transit", "kicker": "Car city test", "headline": "Los Angeles has to make visitor movement legible.", "deck": "Mega-event ambition runs through the transit map.", "body": "LA Metro is one of the core public references for moving through the host region.", "source": "la-metro"},
    {"class": "utility", "avatar": "TL", "outlet": "TransLink", "sub": "Transit", "kicker": "Vancouver flow", "headline": "A compact host city still needs regional rhythm.", "deck": "Transit quality can turn matchday into welcome.", "body": "TransLink anchors Vancouver's everyday public-transport context.", "source": "translink"},
    {"class": "utility", "avatar": "CDMX", "outlet": "Mexico City Metro", "sub": "Transit", "kicker": "Opening city", "headline": "Mexico City's opening day will move through a deep transit culture.", "deck": "The first match begins long before the first whistle.", "body": "The Metro is part of the civic setting around the tournament opener.", "source": "cdmx-metro"},
]

if len(RAIL_IMAGE_PATHS) != len(CARDS):
    raise ValueError("Rail image count must match side-rail card count")

RAIL_IMAGE_BY_SOURCE = {
    str(card["source"]): path for card, path in zip(CARDS, RAIL_IMAGE_PATHS)
}


SECTIONS = [
    {
        "id": "one-month-out",
        "heading": None,
        "paragraphs": [
            '<p class="lede">There is a moment before a World Cup when the posters are still bright but the romance has to become a functioning public system. The countdown clock keeps glowing, the sponsors keep promising joy, the hosts keep saying the world is welcome, and then the practical questions arrive with their elbows out. Where will people sleep? Which train gets them to the stadium? What happens when a heat index turns a queue into a health risk? Who can afford the ticket? Who gets a visa? How does a football pitch behave inside a building designed for a different sport? In May 2026, one month before the first ball, those questions are no longer background noise. They are the event.</p>',
            f'<p>The 2026 men\'s World Cup opens on June 11 in Mexico City and is scheduled to end on July 19 at New York New Jersey Stadium. For the first time, the tournament has 48 teams, 12 groups, 104 matches, three host countries, and 16 host cities. It stretches from Vancouver and Toronto through Mexico City, Guadalajara, and Monterrey, then across a U.S. map that includes Seattle, Los Angeles, the Bay Area, Dallas, Houston, Kansas City, Atlanta, Miami, Boston, Philadelphia, and New York New Jersey. That is a sports schedule, yes. It is also a transit problem, a security plan, a labor plan, a climate plan, a broadcast calendar, a hotel economy, a border question, and a mass experiment in whether scale can still feel human. {inline_source("fifa-schedule", "FIFA schedule")}</p>',
            '<div class="article-jump-strip"><a href="#article-gallery" data-open-gallery>Article Gallery</a><a href="#source-notes">100+ Source Notes</a><a href="#what-it-means-for-the-world">What It Means</a></div>',
            '<p>That is the central drama of this World Cup before the drama of the matches begins. The tournament is selling itself as a continental celebration of football, a North American coming-out party for the global game, and a glimpse of the sport\'s expanded future. It may become all of that. But first it has to work. The 2026 World Cup is not just asking cities to host matches. It is asking them to turn ordinary civic systems into international services for five weeks and to do it without making the public feel like an afterthought.</p>',
            '<p>The easy version of the story is that game time is almost here. The harder and more interesting version is that game time has already started. It began in ticket queues, train plans, grass trays, heat maps, social feeds, police briefings, hotel blocks, volunteer calls, and the thousand small decisions that decide whether a great sporting event feels like welcome or like friction.</p>',
        ],
    },
    {
        "id": "scale-is-the-first-opponent",
        "heading": "Scale is the first opponent",
        "paragraphs": [
            '<p>The old American comparison for any giant sports event is the Super Bowl. That comparison is useful only because it collapses so quickly. A Super Bowl is a week of corporate gravity around one game. The World Cup is 104 games scattered through 16 host cities across three countries, with supporters moving in several languages, through different currencies, laws, transit systems, police practices, stadium designs, broadcast windows, and climates. A Super Bowl asks one city to absorb a spotlight. This World Cup asks a continent to become a usable interface.</p>',
            f'<p>The expansion to 48 teams is the tournament\'s clearest statement of ambition. More countries get the stage. More supporters see themselves in the bracket. More styles of football reach the group phase. The emotional argument for expansion is strong because the World Cup should belong to more of the world than the old field allowed. But the operating cost is real. Twelve groups mean more matches, more travel, more training bases, more ticket inventory, more security deployments, more television windows, and more chances for a small miscue to become a defining memory. Inclusion by scale is still inclusion, but only if the scale does not swallow the people it claims to invite. {inline_source("fifa-groups", "format source")}</p>',
            '<p>That is why the first opponent in 2026 is not Argentina, France, Brazil, Spain, England, Mexico, the United States, Canada, or any team that arrives with a song behind it. The first opponent is size. Size can thrill. It lets a child in Kansas City, a family in Monterrey, a visitor in Vancouver, and a first-time fan in Philadelphia all feel the same global story brushing past their lives. Size can also flatten. It can turn a game into a queue, a city into a perimeter, a supporter into a customer record, and a public celebration into a platform.</p>',
            '<p>The best World Cups have always been bigger than the field, but not in the same way. They were bigger because a match rearranged a national mood, because a street exploded after a goal, because an underdog made strangers remember where they were. The 2026 version will be bigger in the physical and administrative sense before it becomes bigger in the emotional one. It has to move people before it can move them.</p>',
            '<p>There is beauty in that, if the hosts take it seriously. Logistics are often treated as the dull backstage of sport. Here they are part of the moral texture. A tournament that says the world is welcome has to make welcome legible in the most ordinary places: the sign at the station, the water refill point, the gate map, the price page, the text alert, the volunteer who knows where to send a family that has missed a connection. The measure of scale is not how impressive it looks from above. The measure is whether it still makes sense at ground level.</p>',
        ],
    },
    {
        "id": "the-map-is-the-story",
        "heading": "The map is the story",
        "paragraphs": [
            '<p>The 2026 host map is a thesis. Mexico brings the tournament back to a country that already gave the World Cup two of its most mythic editions, 1970 and 1986. Canada hosts its first men\'s World Cup matches after years of building its national team and soccer infrastructure. The United States hosts most of the schedule and tries again to convert a massive sports economy into something closer to a football country. The map is not just where games happen. It is the argument the tournament is making about the sport\'s future.</p>',
            f'<p>FIFA has leaned into that continental story, and the public numbers explain why. The United States hosts 78 of 104 matches. Canada and Mexico host 13 apiece. That distribution gives the U.S. the heaviest operating load, but it also gives Mexico and Canada symbolic weight that cannot be measured only by match count. Mexico City opens the tournament in a stadium tied to Pele, Maradona, and decades of World Cup memory. Toronto and Vancouver make Canada a men\'s World Cup host at a moment when the sport has already claimed more space in the country\'s imagination. {inline_source("fifa-impact", "FIFA impact frame")}</p>',
            '<p>The city list also reveals the strange personality of North American soccer. Some venues sit in places with dense transit and old urban bones. Others sit in regions shaped by highways, parking lots, suburbs, and stadium districts built for a different kind of arrival. Some cities have immigrant communities that have treated the World Cup as a civic holiday for generations. Some are still learning what it means when two visiting fan bases turn a station, plaza, or neighborhood into a temporary home country.</p>',
            '<p>That variation could be the tournament\'s strength. A World Cup should not feel identical in every city. It should sound different in Mexico City than in Seattle, in Miami than in Vancouver, in Kansas City than in Toronto. The event will be richer if it lets each place bring its own weather, food, music, transport habits, immigrant histories, and football cultures into the frame. But variation becomes confusion if the common basics fail. A fan should not need a local Ph.D. in parking policy to reach a match. A visitor should not have to guess whether a shuttle exists, whether a ticket works, or whether the last train has already left.</p>',
            '<p>The host map is therefore both celebration and warning. It says the World Cup is big enough to touch a continent. It also says no single organizing story will be enough. Each city must solve the tournament in its own way without making the tournament feel fragmented. The great challenge is to make a scattered event feel coherent without sanding away the local life that makes it worth scattering in the first place.</p>',
        ],
    },
    {
        "id": "ticket-becomes-the-story",
        "heading": "The ticket becomes the story",
        "paragraphs": [
            '<p>Every World Cup has an access problem because every World Cup has more desire than seats. The 2026 version has turned that old scarcity into a sharper argument about market logic. FIFA opened its last-minute sales phase on April 1, and more inventory is scheduled to be released through the tournament. That sounds like opportunity. It is also the point at which the public could see the real price of being present.</p>',
            f'<p>Associated Press reporting put the tension in plain numbers: the top listed price for the July 19 final rose to $10,990 during the April sales reopening, up from $8,680 after the draw. AP also reported that many group-stage tickets remained available in early May, but at prices that made the word available feel complicated. The cheapest tickets then listed were $380 for a handful of games, while some high-demand fixtures stretched into the thousands. For a tournament that calls itself the world\'s game, the ticket page has become one of its most revealing texts. {inline_source("ap-final-ticket", "AP ticket report")}</p>',
            '<p>This is not just a complaint about expensive seats. It is a question about what kind of public event the World Cup wants to be. Dynamic pricing can be defended as a way to reflect demand and capture value that would otherwise move through secondary markets. But football is not a concert tour without memory. The World Cup sells belonging. It sells the idea that the world can gather around a common game. When the price of that belonging rises too far, the tournament risks staging universality while practicing exclusion.</p>',
            '<p>The resale rules deepen the point because they change by country and law. FIFA\'s own help materials say price limits differ across places, with Mexico and Ontario treated differently from many other resale environments. That means the market is not a single clean machine. It is a patchwork of national and provincial rules, platform decisions, currencies, demand curves, and fan expectations. A supporter in one city may see a constrained resale system while another faces a much more elastic price environment. The same tournament produces different meanings of fairness depending on where the seat is located.</p>',
            '<p>The ticket is the smallest object in the World Cup and one of the largest symbols. It tells a fan whether the event has room for them. It tells a city whether local residents can join the celebration or merely host the disruption. It tells FIFA whether the global game is being monetized as a luxury product at the exact moment it is being marketed as a mass gathering. Stadiums can be full and still leave a civic question hanging over the night: who got to be there, and who was priced into watching from somewhere else?</p>',
        ],
    },
    {
        "id": "getting-there-is-not-a-side-quest",
        "heading": "Getting there is not a side quest",
        "paragraphs": [
            '<p>The most ordinary question may be the most decisive one: how do people get to the match? North American stadiums were often built around cars, tailgates, highways, controlled parking lots, and one-time event pulses. World Cup crowds are not ordinary home crowds. They include international visitors who may not drive, supporters moving in large groups, families carrying flags and children, residents trying to commute through the event, workers arriving before fans, media with gear, and visitors whose first language may not be English, Spanish, or French.</p>',
            f'<p>The U.S. Department of Transportation announced $100.3 million in Federal Transit Administration funding for public transit systems serving World Cup host cities. The money is intended for planning, capital, and operating expenses tied to matches and public events. That sentence sounds bureaucratic because the work is bureaucratic. It is also one of the most important parts of the tournament. A clean transit plan will not make a highlight reel. A broken one can define a matchday for thousands of people who only wanted to arrive with enough time to hear the anthem. {inline_source("dot-transit", "DOT funding")}</p>',
            '<p>The New York New Jersey final region shows how quickly transportation becomes a political story. NJ TRANSIT and the host committee announced a regional stadium mobility plan in April, including special match-specific rail tickets to the Meadowlands. The initial roundtrip price of $150 drew outrage. In early May, NBC New York reported that the price was reduced to $105. That correction matters not only because of the dollars, but because it showed how visible the ride itself had become. The route to the final is not a neutral detail. It is part of the price of participation.</p>',
            '<p>Every host city has its own version of the same problem. Los Angeles has to translate a car-heavy region into visitor-friendly movement. Dallas and Houston have to manage heat, distance, and stadium access in sprawling metros. Seattle, Vancouver, Toronto, Boston, Philadelphia, and the Bay Area have more rail bones but still have to absorb irregular crowds and late-night return flows. Mexico City has deep transit culture and enormous demand. Kansas City and Atlanta have their own station, shuttle, rideshare, and roadway puzzles. A continental World Cup will be experienced locally as a set of very specific directions.</p>',
            '<p>Transportation is where the event either honors the public or exposes it. Good movement makes a city feel generous. Bad movement turns enthusiasm into resentment. The host that gets this right will not simply publish a map. It will speak clearly, price honestly, run enough service, protect people from heat while they wait, and remember that visitors do not know the shortcuts locals know. The World Cup starts before the gate. In 2026, it may start on the platform.</p>',
        ],
    },
    {
        "id": "heat-is-part-of-the-bracket",
        "heading": "Heat is part of the bracket",
        "paragraphs": [
            '<p>Soccer likes to imagine the field as neutral. The ball is round, the laws are shared, the better team should win. Summer keeps interrupting that idea. The 2026 World Cup will be played across June and July in cities where heat is not a backdrop but an active condition. Covered stadiums help, and several venues have roofs or climate-control advantages. But the World Cup is not only what happens under the roof. It is also the fan festival, the shuttle queue, the security line, the sidewalk, the parking lot, the work shift, and the walk back after stoppage time.</p>',
            f'<p>AP reported that extreme heat could threaten players, fans, officials, and workers during the tournament, citing research that wet-bulb globe temperatures could reach dangerous levels in several host markets. That measurement matters because it captures more than the air temperature. It accounts for humidity, wind, sun angle, and other factors that shape what the human body can tolerate. A 3 p.m. matchday is not just a scheduling choice. It can become a public-health decision. {inline_source("ap-heat", "AP heat report")}</p>',
            '<p>Heat changes the sport. It can slow pressing, alter substitutions, punish teams that chase, and reward patience. But the larger issue is fairness off the field. Wealth can buy shade, air-conditioning, shorter waits, private transport, and better timing. The cheapest path to participation often asks people to stand longer, walk farther, queue earlier, and accept more exposure. A World Cup that wants to feel global cannot let the least protected fans and workers absorb the harshest weather.</p>',
            '<p>The worker question deserves its own place in the story. Security staff, concessions workers, cleaners, volunteers, broadcasters, drivers, medical teams, police officers, and stadium crews will experience the tournament as labor before spectacle. They may be outside before fans arrive and after fans leave. OSHA and public-health guidance on heat exposure is not an abstraction for them. It is the difference between a safe shift and a dangerous one. If the event is serious about welcome, it has to include the people making welcome possible.</p>',
            '<p>The best heat plan will be visible in small mercies. Water that is easy to find. Shade where people actually wait. Clear refill rules. Cooling spaces before distress sets in. Multilingual alerts that do not arrive too late. Staff empowered to pause a line before it becomes a medical scene. Matchday schedules that treat climate as a factor, not an inconvenience. The World Cup cannot control the weather. It can decide whether people feel cared for inside it.</p>',
        ],
    },
    {
        "id": "grass-tells-the-truth",
        "heading": "Grass tells the truth",
        "paragraphs": [
            '<p>The field is the quietest confession in the whole event. Several U.S. World Cup venues are NFL buildings, designed first for American football, concerts, corporate suites, and the economics of multipurpose entertainment. The World Cup arrives and asks them to become something more specific. It asks the building to speak football in the global sense, not just host soccer as another event line on a calendar.</p>',
            f'<p>That is why the grass story matters. Reuters documented sprinklers watering the newly installed real-grass pitch at MetLife Stadium on May 7. The image is almost plain if you miss the meaning: the final is not simply being staged in East Rutherford. The ground itself is being converted. Beneath every camera angle and sponsor board sits a technical promise that elite players will be asked to trust with their footing, timing, and bodies. {inline_source("reuters-grass", "Reuters pitch record")}</p>',
            '<p>Grass is not nostalgia. It is performance infrastructure. It affects ball speed, bounce, traction, fatigue, injury risk, drainage, irrigation, sunlight, airflow, and how a temporary surface holds together under repeated training and match stress. A great pitch disappears into the game because it lets the game explain itself. A bad one becomes a character, and almost never in a good way. Players notice first. Then coaches. Then everyone.</p>',
            '<p>The pitch also carries a symbolic charge in 2026. North America has enough stadium size, broadcast skill, hospitality inventory, and security experience to stage enormous spectacles. The harder task is adaptation. Football is not improved by every feature of the American sports machine. It does not always need more noise, more premium layers, more interruptions, more price segmentation, more screens telling fans how to feel. Sometimes the most important act of hosting is humility: changing the venue to fit the game instead of changing the game to fit the venue.</p>',
            '<p>That is why grass tells the truth. It shows whether the World Cup is being treated as a visiting tenant or as the central event. It reminds the hosts that the spectacle rests on a rectangle of living material that has to be watered, protected, measured, and trusted. Beneath the global branding, the tournament still begins with a ball on a field. If that part fails, all the rest of the machine looks foolish.</p>',
        ],
    },
    {
        "id": "security-and-borders",
        "heading": "Security and borders move onto the sports page",
        "paragraphs": [
            '<p>The World Cup is a soft-power event until it is not. It asks countries to show openness, then forces governments to manage every risk that openness creates. The 2026 tournament arrives in a politically tense moment, and the closer kickoff gets, the more visible that tension becomes. Security is no longer a background promise. It is part of the story fans, teams, governments, and host cities are already reading.</p>',
            f'<p>Canada announced up to C$145 million in federal support for public safety and security around matches in Toronto and Vancouver. In the United States, recent reporting has focused on heightened risk around U.S. matches, soft targets, hotels, transit hubs, and public gatherings, with the final carrying National Special Security Event weight. That does not mean fear should become the tournament\'s mood. It means the event\'s public joy depends on careful, quiet, layered work. {inline_source("canada-security", "Canada security source")}</p>',
            '<p>The border story is just as complicated. AP reported that Iran\'s soccer federation said it would participate but wanted assurances around visas, security, and treatment, including for team members who had completed mandatory military service in the Revolutionary Guard. That is a sports item only if sports is defined too narrowly. The bracket brings governments into contact. Players and fans move through consular systems, airports, interviews, watchlists, sanctions, media scrutiny, protest politics, and public suspicion. A fixture can become a diplomatic test before it becomes a match.</p>',
            '<p>Security planning has to walk a narrow line. Too little security is a failure of duty. Too much visible force can make a city feel occupied rather than welcoming. The best posture is not the loudest one. It is the one that protects without turning ordinary supporters into suspects, guards protest rights without inviting chaos, moves people calmly, and understands that fan culture is not automatically disorder. A crowd singing in the street can be a risk-management problem and a civic gift at the same time.</p>',
            '<p>This is where the World Cup exposes the real condition of the world it claims to gather. Borders are not neutral. Policing is not neutral. Visas are not neutral. Press access, protest zones, hotel security, intelligence sharing, and airport treatment all shape whether the event feels genuinely international or only commercially global. There is no way to remove politics from the World Cup. There is only the choice to manage it honestly or pretend it will wait outside the gate.</p>',
        ],
    },
    {
        "id": "first-of-its-kind-happenings",
        "heading": "The first-of-its-kind layer",
        "paragraphs": [
            '<p>The phrase "first of its kind" is often abused around sports, but 2026 earns it in several concrete ways. It is the first 48-team men\'s World Cup. It is the first with 104 matches. It is the first jointly hosted across three countries. It is the first men\'s World Cup in Canada. It is the first time Mexico hosts matches in a third men\'s World Cup. It is the first time the United States hosts after the modern streaming and social-video economy has swallowed the old broadcast monoculture. It is also the first World Cup staged in North America under this level of climate, security, and affordability scrutiny.</p>',
            '<p>Those firsts do not all point in the same direction. Some are exhilarating. More teams means more countries get a national memory. More host cities means the event can reach people who would never travel across the continent for a single final. More social distribution means moments can move instantly from a stadium seat to a group chat in another hemisphere. A tournament built across three countries can show how football travels through diaspora, migration, language, and family histories rather than pretending a host nation is a sealed container.</p>',
            '<p>Other firsts are tests. A 104-match tournament asks whether the World Cup can grow without diluting itself. Three host countries ask whether border systems and local laws can support a single event. A richer ticket platform asks whether demand pricing can coexist with football\'s mass identity. A social-media World Cup asks whether the shared public square can survive algorithmic fragmentation. A hotter summer asks whether host planning has caught up to climate reality. The newness is not automatically progress. It is an audition.</p>',
            '<p>There will be small firsts too, the ones that matter more to people than to press releases. A child in Toronto may attend a men\'s World Cup match at home for the first time. A family in Mexico City may connect 2026 to stories told about 1986. A supporter from a debuting nation may see their flag in a stadium they never expected to enter. A U.S. city that has always treated soccer as a niche may discover that the niche was actually a crowd waiting for permission to become visible.</p>',
            '<p>The danger is that the tournament talks about firsts as trophies instead of responsibilities. Being first means nobody can fully rely on old habits. It means every assumption deserves pressure: how tickets are priced, how streets are closed, how shade is placed, how volunteers are trained, how teams travel, how fans are spoken to, how social platforms are used, and how host cities measure success after the circus leaves. The 2026 World Cup will make history because it must. Whether that history is admired depends on what the firsts feel like to people living through them.</p>',
        ],
    },
    {
        "id": "history-is-not-a-museum-piece",
        "heading": "History is not a museum piece",
        "paragraphs": [
            '<p>The World Cup is never only the present tournament. It arrives carrying ghosts. Uruguay 1930 is in it, the beginning of a competition that was smaller, slower, and less certain of its future. Mexico 1970 is in it, all color and myth and altitude and Pele. Mexico 1986 is in it, Maradona bending the event around himself. USA 1994 is in it, the summer when American soccer learned that borrowed attention could become infrastructure. Every edition leaves something behind: a goal, a scandal, a song, a tactical shift, a stadium, a warning.</p>',
            f'<p>That history matters in 2026 because the tournament is returning to places that already changed it. Mexico is not simply another host. It is a World Cup memory palace. The United States is not simply another market. It is where FIFA once proved that the sport could fill giant American stadiums even before Major League Soccer existed. Canada is not simply the new piece. It is a country that has watched the women\'s game, immigrant communities, and the men\'s national team widen the meaning of football at home. {inline_source("fifa-museum-history", "history source")}</p>',
            '<p>The comparison with 1994 will be unavoidable and imperfect. That tournament was a commercial success and a soccer conversion story, but it took place before smartphones, before streaming, before current immigration politics, before climate risk was so hard to dodge, before ticket platforms trained fans to expect prices to move like airline seats. The 1994 lesson was that the United States could host and that American crowds could show up. The 2026 question is different: can a continent host at much greater scale without letting the machinery become the main character?</p>',
            '<p>History also protects the tournament from becoming pure product. The World Cup is valuable because people remember it across generations. A match can become a family story, a national wound, a neighborhood ritual, or a private timestamp. That is why the event should be careful with its own commercialization. The future value of a World Cup is created by memories that feel real, not by frictionless content output. If every moment is priced, packaged, and optimized, the event may make money while thinning the very memory that gives it power.</p>',
            '<p>The best version of 2026 will know that it is joining a long conversation. It will honor Mexico\'s past, Canada\'s arrival, the United States\' unfinished soccer project, and the supporters who have carried the sport in bars, parks, Sunday leagues, family rooms, and immigrant neighborhoods long before the official countdown began. A World Cup is not made global by branding. It is made global by memory moving from one person to another.</p>',
        ],
    },
    {
        "id": "the-feed-and-the-street",
        "heading": "The feed and the street",
        "paragraphs": [
            '<p>The 2026 World Cup will be watched in stadiums, bars, living rooms, outdoor watch parties, office Slack channels, school cafeterias, airport gates, and phones held above crowds. The event will exist in the street and in the feed at the same time, and neither version will be secondary. A fan may experience a goal first as a roar, then as a replay, then as a meme, then as an argument, then as a family text from another country. The World Cup has always traveled through conversation. In 2026, the conversation travels instantly and everywhere.</p>',
            f'<p>That social layer is not cosmetic. FIFA\'s official accounts on X, Instagram, TikTok, YouTube, Facebook, and Threads will distribute highlights, behind-the-scenes clips, city imagery, player moments, tactical explainers, and brand-safe emotions. Broadcasters will push their own clips and shoulder programming. Supporters will publish the unauthorized version: the train chant, the bad queue, the perfect street scene, the overpriced meal, the child seeing a star, the protest sign, the goalkeeper warmup, the confusion outside Gate C. The official World Cup and the lived World Cup will compete in real time. {inline_source("fifa-tiktok", "official social source")}</p>',
            '<p>This is good for the event when it makes the tournament feel shared. A watch party can become a stadium for people without tickets. A clip can give a small nation a global audience. A fan account can translate local emotion better than any campaign. A phone can preserve the tiny scenes that broadcast cameras miss. Social media can turn the World Cup back into a public square when ticket prices and travel costs make the stadium feel distant.</p>',
            '<p>It can also punish failure quickly. A transportation meltdown does not need a newspaper deadline. A heat line can become a viral image before officials have finished a statement. A security overreaction can travel farther than the match result. A pricing screenshot can define the mood of a week. Host cities should not treat social media as a decoration around the event. It is now one of the main accountability systems.</p>',
            '<p>The street still matters more than the feed because the street is where bodies are. But the feed shapes what the street means to everyone else. That is the new World Cup loop. The match produces emotion. The crowd performs it. The phone transmits it. The world responds. The response changes the next crowd. In 2026, the event will not wait for the final whistle to become memory. It will become memory minute by minute, post by post, chant by chant, complaint by complaint, joy by joy.</p>',
        ],
    },
    {
        "id": "what-it-means-for-the-world",
        "heading": "What it means for the world",
        "paragraphs": [
            '<p>The World Cup matters because it is one of the few events that still asks billions of people to look in the same direction without asking them to agree. That is rare in a fractured media age. The tournament does not heal the world. It does not erase war, borders, inequality, climate stress, or authoritarian politics. It does not make FIFA innocent of criticism or hosts immune from scrutiny. But it still creates a temporary grammar that people almost everywhere can read. A goal is understood before it is translated. A penalty miss requires no passport. A national anthem can make a stranger understand, for ninety seconds, how much a game can carry.</p>',
            '<p>That is why 2026 feels larger than its operational checklist. The logistics matter precisely because the emotion matters. If the tournament were only a corporate product, a bad train would be a customer-service issue. If it is a global civic ritual, a bad train is a broken promise. If the World Cup is only content, heat is a scheduling inconvenience. If it is a public gathering, heat is a matter of care. If football is only entertainment, ticket prices are whatever the market bears. If it is a shared language, pricing determines who gets to speak it in person.</p>',
            '<p>The world will read North America through this event. It will see whether the United States can host without turning every experience into a premium tier. It will see whether Mexico can fuse memory and modern pressure. It will see whether Canada can make its first men\'s World Cup feel confident, inclusive, and serious. It will see whether three countries can share a stage at a time when borders and nationalism keep hardening. It will see whether the global game can expand without losing the intimacy that made it global in the first place.</p>',
            '<p>The future of the World Cup is already moving toward larger hosts, larger budgets, larger political consequences, and hotter questions. The 2030 and 2034 cycles are not distant abstractions. They are the next chapters in a story 2026 is helping to write. If this tournament works, it will strengthen the argument that expansion can broaden belonging. If it fails in public ways, it will feed the suspicion that football\'s greatest event is becoming too large, too expensive, and too insulated from the people who give it meaning.</p>',
            '<p>So the stakes are not only who lifts the trophy. The stakes are whether the World Cup can remain the world\'s most generous sporting idea while becoming one of its most complicated logistical products. That balance is fragile. It depends on planners who sweat small details, fans who bring the event to life, workers whose labor is treated with respect, cities willing to learn quickly, and organizers honest enough to admit that scale is not the same thing as welcome.</p>',
        ],
    },
    {
        "id": "what-success-looks-like",
        "heading": "What success will look like",
        "paragraphs": [
            '<p>The successful version of this World Cup is easy to imagine because it is made of ordinary things done well. The opening match feels historic without feeling overproduced. The trains are findable. The shuttle signs are clear. Water is available before people are desperate. Security is serious without becoming theater. Ticket buyers understand what they purchased. Workers get shade, breaks, and respect. The pitch holds. A visitor who speaks little English can still navigate the day. The stadium is loud because supporters are there, not because the event has been engineered into a generic entertainment product.</p>',
            '<p>The best version also allows the sport to surprise the machinery. A debutant nation steals a point. A favorite survives a scare. A goalkeeper becomes a national myth. A host city expected to be quiet turns into a street party. A fan without a ticket finds a watch party that feels like belonging. A child learns a player\'s name and keeps it. The World Cup needs planning so that unplanned magic has room to happen.</p>',
            '<p>The failed version is just as visible. A price story overwhelms an access story. A heat plan breaks at the first long queue. A transit surcharge becomes a symbol of civic resentment. A security scare away from the stadium redefines a week. A temporary pitch draws player anger. A border dispute turns a fixture into a diplomatic test. A fan festival becomes a crowd-management lesson. The tournament still happens, the money still moves, the final still gets played, but the memory gathers around everything that made the game harder to reach.</p>',
            '<p>For years, the 2026 World Cup sounded like the future. Then it sounded like a schedule. Now it sounds like a checklist. That is not a demotion. It is the moment serious hosts should want, because a checklist is how a promise becomes real. The ball will soon return the tournament to uncertainty, which is where football is happiest. Until then, the story belongs to the system around the match: tickets, trains, heat, grass, security, borders, workers, fans, cities, screens, memory, and the public square.</p>',
            '<p>Game time is almost here. The host continent is already playing.</p>',
        ],
    },
]


def image_index_for_card(card: dict[str, object]) -> int:
    text = " ".join(
        str(card.get(key, ""))
        for key in ("class", "outlet", "sub", "kicker", "headline", "deck", "body")
    ).lower()
    keyword_groups = [
        ("heat climate public health weather water shade cooling osha cdc nws", 2),
        ("transit train metro mobility route movement rail shuttle transport station", 1),
        ("pitch grass stadium field surface venue", 3),
        ("social tiktok instagram youtube facebook threads broadcast screen feed media watch", 4),
        ("history archive future 2030 2034 museum record memory", 5),
        ("ticket resale price access hospitality", 0),
    ]
    for keywords, index in keyword_groups:
        if any(word in text for word in keywords.split()):
            return index
    seed = sum((index + 1) * ord(char) for index, char in enumerate(str(card["source"])))
    return seed % len(GALLERY_IMAGES)


def image_for_card(card: dict[str, object]) -> dict[str, str]:
    source = SOURCE_BY_ID[str(card["source"])]
    rail_image_path = RAIL_IMAGE_BY_SOURCE.get(str(card["source"]))
    if rail_image_path:
        image = {
            "path": rail_image_path,
            "alt": f'{str(card["kicker"])}: {str(card["headline"])}',
            "caption": f'{str(card["kicker"])} / {str(card["sub"])}',
        }
    elif "image" in card:
        image = dict(card["image"])
    else:
        image = dict(GALLERY_IMAGES[image_index_for_card(card)])
        image["caption"] = f'{str(card["kicker"])} / {str(card["sub"])}'
    image["link"] = source["url"]
    return image


def render_gallery() -> str:
    cards = []
    seen_paths = set()
    for card in CARDS:
        item = image_for_card(card)
        if item["path"] in seen_paths:
            continue
        seen_paths.add(item["path"])
        source = SOURCE_BY_ID[str(card["source"])]
        cards.append(
            '<a class="article-rail-gallery__card" href="{link}" data-source-id="{source_id}">'
            '<img src="{src}" alt="{alt}" loading="lazy" decoding="async" />'
            "</a>".format(
                link=html.escape(item["link"]),
                source_id=html.escape(source["id"]),
                src=html.escape(item["path"]),
                alt=html.escape(item["alt"]),
            )
        )
    return "\n".join(cards)


def render_gallery_block() -> str:
    return (
        '<details class="article-rail-gallery article-rail-gallery--top" id="article-gallery">'
        '<summary>Article Gallery</summary>'
        f'<div class="article-rail-gallery__grid">{render_gallery()}</div>'
        '</details>'
    )


def render_card(card: dict[str, object]) -> str:
    source = SOURCE_BY_ID[str(card["source"])]
    class_name = f'press-static-post press-static-post--{card["class"]} press-static-post--clickable press-static-post--with-illustration world-cup-rail-card--with-image'
    if "image" not in card:
        class_name += " world-cup-rail-card--gallery-sourced"
    image = image_for_card(card)
    media = (
        '<figure class="press-static-post__media--illustration">'
        '<a href="{link}">'
        '<img src="{src}" alt="{alt}" loading="eager" decoding="async" />'
        "</a>"
        "</figure>"
    ).format(
        link=html.escape(image["link"]),
        src=html.escape(image["path"]),
        alt=html.escape(image["alt"]),
    )

    source_url = html.escape(source["url"])
    return f"""
      <article class="{class_name}" data-source-id="{html.escape(source["id"])}" data-source-url="{source_url}" role="link" tabindex="0">
        <div class="press-static-post__top"><span class="press-static-post__avatar">{html.escape(str(card["avatar"]))}</span><div><strong>{html.escape(str(card["outlet"]))}</strong><span>{html.escape(str(card["sub"]))}</span></div></div>
        {media}
        <div class="press-static-post__visual"><span class="press-static-post__kicker">{html.escape(str(card["kicker"]))}</span><strong>{html.escape(str(card["headline"]))}</strong><em>{html.escape(str(card["deck"]))}</em></div>
        <p>{html.escape(str(card["body"]))}</p>
        <a href="{source_url}">Open link</a>
      </article>"""


def render_section(section: dict[str, object]) -> str:
    heading = ""
    if section["heading"]:
        heading = f'<h2>{html.escape(str(section["heading"]))}</h2>\n'
    paragraphs = "\n      ".join(str(p) for p in section["paragraphs"])
    return f"""<section class="press-social-content" id="{html.escape(str(section["id"]))}">
      {heading}{paragraphs}
    </section>"""


def render_body() -> str:
    rows = []
    for index, section in enumerate(SECTIONS):
        start = index * 4
        left_cards = [CARDS[(start + offset) % len(CARDS)] for offset in (0, 1)]
        right_cards = [CARDS[(start + offset) % len(CARDS)] for offset in (2, 3)]
        left_html = "\n".join(render_card(card) for card in left_cards)
        right_html = "\n".join(render_card(card) for card in right_cards)
        rows.append(
            f"""  <div class="press-social-row press-social-row--{index + 1}">
    <aside class="press-social-side press-social-side--left">
{left_html}
    </aside>
{render_section(section)}
    <aside class="press-social-side press-social-side--right">
{right_html}
    </aside>
  </div>"""
        )
    sources = []
    for item in SOURCES:
        sources.append(
            '<li id="source-{id}"><strong>{outlet}</strong>, <a href="{url}">{title}</a>. {note}</li>'.format(
                id=html.escape(item["id"]),
                outlet=html.escape(item["outlet"]),
                url=html.escape(item["url"]),
                title=html.escape(item["title"]),
                note=html.escape(item["note"]),
            )
        )

    return f"""<section class="press-social-feature world-cup-game-day-feature" data-social-card-count="{len(CARDS)}" data-source-count="{len(SOURCES)}" data-source-label="World Cup public record">
{render_gallery_block()}
{chr(10).join(rows)}
</section>

<section class="press-social-sources press-feature-sources world-cup-source-notes" id="source-notes">
  <h2>Source notes</h2>
  <p>This article is built from official tournament materials, host-city pages, transit agencies, public-safety sources, health and climate guidance, sports-media links, and current reporting. The list below includes the working public record behind the article and the side-rail links.</p>
  <ol class="source-list">
    {chr(10).join(sources)}
  </ol>
</section>
<script>
(function() {{
  document.querySelectorAll('.press-static-post--clickable').forEach(function(card) {{
    var sourceUrl = card.getAttribute('data-source-url');
    card.addEventListener('click', function(event) {{
      if (event.target.closest('a')) return;
      var destination = sourceUrl || (card.querySelector('a[href]') || {{}}).href;
      if (!destination) return;
      event.preventDefault();
      event.stopPropagation();
      window.location.assign(destination);
    }}, true);
    card.addEventListener('keydown', function(event) {{
      if (event.key !== 'Enter' && event.key !== ' ') return;
      if (event.target.closest('a')) return;
      event.preventDefault();
      var destination = sourceUrl || (card.querySelector('a[href]') || {{}}).href;
      if (destination) window.location.assign(destination);
    }});
  }});
  document.querySelectorAll('[data-open-gallery]').forEach(function(link) {{
    link.addEventListener('click', function() {{
      var gallery = document.getElementById('article-gallery');
      if (gallery) gallery.open = true;
    }});
  }});
}})();
</script>
"""


def clean_words(markup: str) -> int:
    text = re.sub(r"<script[\s\S]*?</script>", " ", markup)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return len(re.findall(r"\b[\w'-]+\b", text))


def render_aside() -> str:
    return f"""<section class="aside-card">
  <h3>Key points</h3>
  <ul>
    <li>The 2026 World Cup opens on June 11 and runs through the July 19 final in New York New Jersey.</li>
    <li>The expanded tournament puts 48 teams, 104 matches, 16 host cities, and three countries into one shared North American operating system.</li>
    <li>The biggest tests include ticket prices, transit, heat, grass installation, public safety, borders, labor, broadcast reach, and social-media accountability.</li>
    <li>This feature now includes {len(SOURCES)} source notes, {len(CARDS)} image rail cards, and a reader-opened Article Gallery tied to the same side-rail links.</li>
  </ul>
</section>
<section class="aside-card">
  <h3>On this page</h3>
  <ol>
    <li><a href="#one-month-out">One month out</a></li>
    <li><a href="#article-gallery">Article Gallery</a></li>
    <li><a href="#scale-is-the-first-opponent">Scale</a></li>
    <li><a href="#ticket-becomes-the-story">Tickets</a></li>
    <li><a href="#getting-there-is-not-a-side-quest">Transit</a></li>
    <li><a href="#heat-is-part-of-the-bracket">Heat</a></li>
    <li><a href="#grass-tells-the-truth">Grass</a></li>
    <li><a href="#security-and-borders">Security and borders</a></li>
    <li><a href="#first-of-its-kind-happenings">Firsts</a></li>
    <li><a href="#history-is-not-a-museum-piece">History</a></li>
    <li><a href="#the-feed-and-the-street">The feed and the street</a></li>
    <li><a href="#what-it-means-for-the-world">What it means</a></li>
    <li><a href="#source-notes">100+ source notes</a></li>
  </ol>
</section>
<section class="aside-card">
  <h3>Source mix</h3>
  <p>Official FIFA and host-city pages; transit and security agencies; AP, Reuters and Guardian reporting; health, heat and labor guidance; broadcasters; national federations; and official World Cup social links.</p>
</section>
"""


def render_report(word_count: int) -> str:
    return f"""# Source Stack: {TITLE}

- Story date: May 11, 2026.
- Body word count after generation: {word_count:,}.
- Source notes in article: {len(SOURCES)}.
- Side-rail cards: {len(CARDS)}.
- Gallery tiles: {len(CARDS)}.
- Distinct generated rail images: {len(RAIL_IMAGE_PATHS)}.
- Gallery default state: closed until the reader opens it.
- Thumbnail: `{IMAGE}`.

## Source families

- FIFA schedule, host-city, team, ticketing, resale, hospitality, sustainability, human-rights, stadium and history references.
- Official or public host-city and host-committee pages for U.S., Canada and Mexico markets.
- Transit sources for federal funding, New York New Jersey mobility, regional rail, and local host-city agencies.
- Current reporting from AP, Reuters and The Guardian on tickets, heat, pitch installation, visas and security.
- Public-safety, visa, border, airport, heat, labor and mass-gathering guidance.
- Official social and broadcast links for the live media layer around the tournament.
"""


def update_master(word_count: int) -> dict[str, object]:
    master = json.loads(MASTER_PATH.read_text())
    read_minutes = max(1, math.ceil(word_count / 200))
    story = None
    for item in master.get("stories", []):
        if item.get("filename") == FILENAME:
            story = item
            break
    if story is None:
        story = {}
        master.setdefault("stories", []).insert(0, story)

    story.update(
        {
            "slug": SLUG,
            "filename": FILENAME,
            "title": TITLE,
            "section": "Sports",
            "sectionSlug": "sports",
            "type": "Feature",
            "author": "The Press",
            "authorSlug": "the-press",
            "authorRole": "Editorial Desk",
            "publishedLabel": "May 11, 2026 • 9:00 a.m. EDT",
            "updatedLabel": "May 11, 2026 • 9:00 a.m. EDT",
            "publishedIso": "2026-05-11T09:00:00-04:00",
            "updatedIso": "2026-05-11T09:00:00-04:00",
            "wordCount": f"{word_count:,} words",
            "wordCountNumber": word_count,
            "readTime": f"{read_minutes} min read",
            "dek": DEK,
            "image": IMAGE,
            "heroImage": IMAGE,
            "heroImageWidth": 1672,
            "heroImageHeight": 941,
            "imageAlt": IMAGE_ALT,
            "imageCaptionHtml": "",
            "imageCreditPlain": "",
            "imageAiGenerated": True,
            "imageAiCaption": "",
            "imageCaption": "The 2026 World Cup is becoming a test of tickets, transit, heat, security, media, memory and the matchday system around the game.",
            "keywords": [
                "FIFA World Cup 2026",
                "World Cup",
                "soccer",
                "sports media",
                "sports business",
                "transit",
                "ticket prices",
                "extreme heat",
                "MetLife Stadium",
                "North America",
            ],
            "asideFile": f"content/asides/{FILENAME}",
            "bodyFile": f"content/bodies/{FILENAME}",
            "excerpt": "The 2026 World Cup is one month away, and the real test is the machine around the match: tickets, transit, heat, grass, security, borders, social media, history and whether a continental event can still feel human.",
            "related": [
                "sports-texas-holdem-prime-time-moment-back.html",
                "world-americas-military-year-is-a-map-of-force.html",
                "climate-your-home-insurance-bill-is-the-new-climate-map.html",
            ],
            "heroEligible": True,
            "imageWidth": 1672,
            "imageHeight": 941,
            "socialRailPattern": {
                "className": "press-social-feature world-cup-game-day-feature",
                "cardsInBody": len(CARDS),
                "sourceCount": len(SOURCES),
                "notes": "Every side-rail card now carries its own distinct thumbnail linked to its public source or official social/site destination. The Article Gallery stays closed until the reader opens it and renders one image-only tile per unique image path. Source-note, gallery, and rail links navigate directly in the current tab.",
            },
        }
    )

    homepage = master.setdefault("homepage", {})
    for key in ("leadOrder", "secondary", "mostRead", "editorsPicks"):
        items = homepage.setdefault(key, [])
        items[:] = [item for item in items if item != FILENAME]
        items.insert(0, FILENAME)
    master["site"]["editionNote"] = "Issue Six • Monday, May 11, 2026 • Game Time World Cup special"

    for author in master.get("authors", []):
        if author.get("slug") == "the-press":
            stories = author.setdefault("stories", [])
            if FILENAME not in stories:
                stories.insert(0, FILENAME)

    MASTER_PATH.write_text(json.dumps(master, indent=2, ensure_ascii=False) + "\n")
    return story


def update_search_index(story: dict[str, object]) -> None:
    if SEARCH_PATH.exists():
        payload = json.loads(SEARCH_PATH.read_text())
    else:
        payload = []

    rows = payload.setdefault("stories", []) if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        rows = []

    row = {
        "title": story["title"],
        "section": story["section"],
        "type": story["type"],
        "dek": story["dek"],
        "url": story["filename"],
        "author": story["author"],
        "published": story["publishedLabel"],
        "publishedIso": story["publishedIso"],
        "updatedIso": story["updatedIso"],
        "image": story["image"],
        "imageAlt": story["imageAlt"],
        "imageWidth": story["imageWidth"],
        "imageHeight": story["imageHeight"],
        "keywords": story["keywords"],
        "publishedLabel": story["publishedLabel"],
        "updatedLabel": story["updatedLabel"],
        "wordCount": story["wordCount"],
        "readTime": story["readTime"],
        "imageCredit": story["imageCreditPlain"],
        "story_id": story["slug"],
        "cluster_id": "sports-world-cup-game-time-matchday-machine",
        "section_slug": story["sectionSlug"],
        "published_iso": "2026-05-11T13:00:00+00:00",
        "updated": story["updatedLabel"],
        "updated_iso": "2026-05-11T13:00:00+00:00",
        "image_alt": story["imageAlt"],
        "read_time": story["readTime"],
        "word_count": story["wordCount"],
        "status": "published",
        "priority": 20,
        "hero_eligible": True,
        "source": "master-edition",
        "is_daily": False,
    }

    rows[:] = [item for item in rows if item.get("url") != story["filename"]]
    rows.insert(0, row)
    SEARCH_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def main() -> None:
    body = render_body()
    word_count = clean_words(body)
    BODY_PATH.write_text(body)
    ASIDE_PATH.write_text(render_aside())
    REPORT_PATH.write_text(render_report(word_count))
    story = update_master(word_count)
    update_search_index(story)
    print(f"Installed {FILENAME}: {word_count:,} words, {len(SOURCES)} sources, {len(CARDS)} image side cards, {len(CARDS)} gallery tiles")


if __name__ == "__main__":
    main()
