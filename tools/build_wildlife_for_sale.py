#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD_SLUG = "science-animals-around-the-world-are-sending-one-message"
OLD_FILE = f"{OLD_SLUG}.html"
SLUG = "science-wildlife-for-sale"
FILENAME = f"{SLUG}.html"
BODY_FILE = f"content/bodies/{SLUG}.html"
ASIDE_FILE = f"content/asides/{SLUG}.html"
METADATA_FILE = f"metadata/{SLUG}-master-edition-entry.json"
SOURCE_STACK_FILE = f"reporting/{SLUG}-source-stack.json"
TITLE = "Wildlife for Sale"
DEK = (
    "The trade begins with capture and ends with desire. In between are airports, ports, "
    "forged permits, encrypted chats, online listings, weak laws, and animals treated as "
    "cargo with a heartbeat."
)
HERO = "assets/wildlife-for-sale/wildlife-for-sale-thumbnail-v5.jpg"
HERO_ALT = (
    "Wildlife and customs officers inspecting freight, permits and animal transport crates "
    "at a rain-slick seaport and airport cargo checkpoint at sunrise"
)
RAIL_IMAGE_DIR = "assets/wildlife-for-sale/rails"

IMAGE_BY_CATEGORY = {
    "law": "assets/wildlife-for-sale/rail-forged-permits.png",
    "enforcement": "assets/wildlife-for-sale/rail-airport-reptiles.png",
    "port": "assets/wildlife-for-sale/rail-seaport-marine-products.png",
    "online": "assets/wildlife-for-sale/rail-online-listings.png",
    "forensics": "assets/wildlife-for-sale/rail-forensic-lab.png",
    "birds": "assets/wildlife-for-sale/rail-songbird-rescue.png",
    "rescue": "assets/wildlife-for-sale/rail-rescue-intake.png",
    "mail": "assets/wildlife-for-sale/rail-mail-center.png",
    "market": "assets/wildlife-for-sale/rail-market-pressure.png",
    "community": "assets/wildlife-for-sale/rail-community-rangers.png",
    "marine": "assets/wildlife-for-sale/rail-seaport-marine-products.png",
    "research": "assets/wildlife-for-sale/rail-forensic-lab.png",
}

SOURCES = [
    {"id": "interpol-thunder-2025", "org": "INTERPOL", "title": "Operation Thunder 2025", "url": "https://www.interpol.int/en/News-and-Events/News/2025/30-000-live-animals-seized-in-global-operation-against-wildlife-and-forestry-crime", "category": "enforcement", "note": "Global wildlife and forestry crime operation with live-animal seizure figures."},
    {"id": "interpol-wildlife-crime", "org": "INTERPOL", "title": "Wildlife crime", "url": "https://www.interpol.int/en/Crimes/Environmental-crime/Wildlife-crime", "category": "enforcement", "note": "Defines wildlife crime as a transnational enforcement problem."},
    {"id": "interpol-environmental-crime", "org": "INTERPOL", "title": "Environmental crime", "url": "https://www.interpol.int/en/Crimes/Environmental-crime", "category": "enforcement", "note": "Frames wildlife trafficking inside broader environmental crime."},
    {"id": "unodc-wwcr-2024", "org": "UNODC", "title": "World Wildlife Crime Report 2024", "url": "https://www.unodc.org/documents/data-and-analysis/wildlife/2024/Wildlife2024_Final.pdf", "category": "law", "note": "Core global report on species, commodities, seizures and criminal markets."},
    {"id": "unodc-wildlife-portal", "org": "UNODC", "title": "Wildlife crime data and analysis", "url": "https://www.unodc.org/unodc/en/data-and-analysis/wildlife.html", "category": "research", "note": "UNODC hub for wildlife-crime reporting and analysis."},
    {"id": "unodc-wwcr-2020", "org": "UNODC", "title": "World Wildlife Crime Report 2020", "url": "https://www.unodc.org/documents/data-and-analysis/wildlife/2020/World_Wildlife_Report_2020_9July.pdf", "category": "law", "note": "Prior global baseline on illegal wildlife markets and seizure data."},
    {"id": "cites-what", "org": "CITES", "title": "What is CITES?", "url": "https://cites.org/eng/disc/what.php", "category": "law", "note": "Explains the treaty system that governs international trade in listed species."},
    {"id": "cites-appendices", "org": "CITES", "title": "CITES Appendices", "url": "https://cites.org/eng/app/appendices.php", "category": "law", "note": "Used to explain Appendix I, II and III trade restrictions."},
    {"id": "cites-trade-db", "org": "CITES", "title": "CITES Trade Database", "url": "https://trade.cites.org/", "category": "law", "note": "Official database for reported legal CITES trade records."},
    {"id": "tradeview", "org": "CITES / UNEP-WCMC", "title": "Wildlife TradeView", "url": "https://tradeview.cites.org/", "category": "law", "note": "Public interface for CITES-listed wildlife trade data."},
    {"id": "tradeview-faq", "org": "CITES / UNEP-WCMC", "title": "Wildlife TradeView FAQ", "url": "https://tradeview.cites.org/en/faqs", "category": "law", "note": "Caveats on what CITES trade data can and cannot show."},
    {"id": "speciesplus", "org": "UNEP-WCMC", "title": "Species+", "url": "https://speciesplus.net/", "category": "law", "note": "Legal listing and nomenclature reference for CITES and CMS species."},
    {"id": "cites-illegal-trade-reports", "org": "CITES", "title": "Annual illegal trade reports", "url": "https://cites.org/eng/resources/reports/Illegal_trade_reports", "category": "law", "note": "Parties' annual reporting channel for illegal trade."},
    {"id": "cites-wwtr-2022", "org": "CITES", "title": "World Wildlife Trade Report 2022", "url": "https://cites.org/eng/news/cites-launches-first-world-wildlife-trade-report-2022", "category": "law", "note": "Pilot report on legal wildlife trade and its documentation limits."},
    {"id": "iccwc", "org": "ICCWC", "title": "International Consortium on Combating Wildlife Crime", "url": "https://cites.org/eng/prog/iccwc", "category": "law", "note": "Explains the multi-agency enforcement consortium."},
    {"id": "iccwc-toolkit", "org": "ICCWC", "title": "Wildlife and forest crime analytic toolkit", "url": "https://cites.org/eng/prog/iccwc/analytical_toolkit", "category": "law", "note": "Assessment toolkit for national wildlife-crime response."},
    {"id": "fatf-iwt", "org": "FATF", "title": "Money laundering and the illegal wildlife trade", "url": "https://www.fatf-gafi.org/en/publications/Methodsandtrends/Money-laundering-wildlife-trade.html", "category": "law", "note": "Financial-crime frame for trafficking networks."},
    {"id": "fincen-wildlife-threat", "org": "FinCEN", "title": "Illicit finance threat involving wildlife trafficking", "url": "https://www.fincen.gov/news/news-releases/fincen-financial-threat-analysis-illicit-finance-threat-involving-wildlife", "category": "law", "note": "U.S. financial-threat analysis using Bank Secrecy Act data."},
    {"id": "fincen-environmental-crimes", "org": "FinCEN", "title": "Environmental crimes vigilance reminder", "url": "https://www.fincen.gov/index.php/news/news-releases/fincen-reminds-financial-institutions-remain-vigilant-environmental-crimes", "category": "law", "note": "Connects wildlife trafficking to financial reporting obligations."},
    {"id": "ec-wildlife-trade", "org": "European Commission", "title": "Wildlife trade", "url": "https://environment.ec.europa.eu/topics/nature-and-biodiversity/wildlife-trade_en", "category": "law", "note": "EU policy context for wildlife trade regulation."},
    {"id": "ec-action-plan", "org": "European Commission", "title": "EU Action Plan against Wildlife Trafficking", "url": "https://ec.europa.eu/commission/presscorner/detail/en/ip_22_6581", "category": "law", "note": "EU action-plan announcement and enforcement priorities."},
    {"id": "europol-environmental-crime", "org": "Europol", "title": "Environmental crime", "url": "https://www.europol.europa.eu/crime-areas-and-statistics/crime-areas/environmental-crime", "category": "enforcement", "note": "European organized-crime frame for environmental crime."},
    {"id": "wco-environment", "org": "World Customs Organization", "title": "Environment programme", "url": "https://www.wcoomd.org/en/topics/enforcement-and-compliance/activities-and-programmes/environment-programme.aspx", "category": "port", "note": "Customs role in environmental and wildlife crime enforcement."},
    {"id": "oecd-seasia", "org": "OECD", "title": "The Illegal Wildlife Trade in Southeast Asia", "url": "https://www.oecd.org/en/publications/the-illegal-wildlife-trade-in-southeast-asia_14fe3297-en.html", "category": "law", "note": "Regional governance and enforcement-capacity report."},
    {"id": "world-bank-wildlife-trade", "org": "World Bank", "title": "Illegal logging, fishing, and wildlife trade", "url": "https://www.worldbank.org/en/topic/environment/brief/illegal-logging-fishing-and-wildlife-trade", "category": "law", "note": "Economic-development frame for illicit natural-resource trade."},
    {"id": "iucn-red-list", "org": "IUCN", "title": "IUCN Red List", "url": "https://nrl.iucnredlist.org/", "category": "research", "note": "Extinction-risk baseline for species named in the story."},
    {"id": "iucn-summary", "org": "IUCN", "title": "Red List Summary Statistics", "url": "https://nrl.iucnredlist.org/resources/summary-statistics", "category": "research", "note": "Threatened-share estimates by assessed taxonomic group."},
    {"id": "ipbes-global", "org": "IPBES / UNEP", "title": "Global Assessment press release", "url": "https://www.unep.org/news-and-stories/press-release/natures-dangerous-decline-unprecedented-species-extinction-rates", "category": "research", "note": "Global biodiversity-loss drivers and extinction-risk frame."},
    {"id": "ipbes-invasive", "org": "IPBES / UNEP", "title": "Invasive Alien Species Report", "url": "https://www.unep.org/resources/report/invasive-alien-species-report", "category": "research", "note": "Invasive-species context tied to live wildlife movement."},
    {"id": "protected-planet-2024", "org": "UNEP-WCMC / IUCN", "title": "Protected Planet Report 2024", "url": "https://www.unep.org/news-and-stories/press-release/world-must-act-faster-protect-30-planet-2030", "category": "community", "note": "Protected-area coverage and 30 by 30 progress."},
    {"id": "fao-fish-stocks-2025", "org": "FAO", "title": "Review of world marine fishery resources 2025", "url": "https://www.fao.org/newsroom/detail/fao-releases-the-most-detailed-global-assessment-of-marine-fish-stocks-to-date/en", "category": "marine", "note": "Fish-stock status for marine-exploitation context."},
    {"id": "noaa-coral-bleaching", "org": "NOAA", "title": "Fourth global coral bleaching event", "url": "https://www.nesdis.noaa.gov/news/noaa-confirms-fourth-global-coral-bleaching-event", "category": "marine", "note": "Coral and reef-animal climate pressure background."},
    {"id": "cms-migratory", "org": "Convention on Migratory Species", "title": "State of the World's Migratory Species", "url": "https://www.cms.int/en/publication/state-worlds-migratory-species", "category": "research", "note": "Migration and cross-border animal conservation context."},
    {"id": "usfws-ole", "org": "U.S. Fish and Wildlife Service", "title": "Office of Law Enforcement", "url": "https://www.fws.gov/program/office-of-law-enforcement", "category": "enforcement", "note": "U.S. wildlife-law enforcement and inspection context."},
    {"id": "usfws-wildlife-trafficking", "org": "U.S. Fish and Wildlife Service", "title": "Combating Wildlife Trafficking", "url": "https://www.fws.gov/initiative/combating-wildlife-trafficking", "category": "enforcement", "note": "U.S. public explainer on wildlife trafficking."},
    {"id": "usfws-inspection", "org": "U.S. Fish and Wildlife Service", "title": "Office of Law Enforcement: What We Do", "url": "https://www.fws.gov/rivers/program/office-of-law-enforcement/what-we-do", "category": "port", "note": "Port inspection role for imported and exported wildlife."},
    {"id": "usfws-cites", "org": "U.S. Fish and Wildlife Service", "title": "CITES", "url": "https://www.fws.gov/international-affairs/cites", "category": "law", "note": "U.S. implementation of CITES."},
    {"id": "usfws-lacey", "org": "U.S. Fish and Wildlife Service", "title": "Lacey Act", "url": "https://www.fws.gov/law/lacey-act", "category": "law", "note": "U.S. law against illegal wildlife trafficking and false labeling."},
    {"id": "usfws-esa", "org": "U.S. Fish and Wildlife Service", "title": "Endangered Species Act", "url": "https://www.fws.gov/law/endangered-species-act", "category": "law", "note": "U.S. endangered-species legal context."},
    {"id": "doj-enrd-wildlife", "org": "U.S. Department of Justice", "title": "Wildlife trafficking", "url": "https://www.justice.gov/enrd/wildlife-trafficking", "category": "enforcement", "note": "Federal prosecution frame for wildlife trafficking."},
    {"id": "state-wildlife-trafficking", "org": "U.S. State Department", "title": "Wildlife trafficking", "url": "https://www.state.gov/wildlife-trafficking/", "category": "law", "note": "Diplomatic and transnational response framing."},
    {"id": "noaa-ole", "org": "NOAA Fisheries", "title": "Office of Law Enforcement", "url": "https://www.fisheries.noaa.gov/topic/enforcement", "category": "marine", "note": "Marine-resource enforcement and illegal fishing context."},
    {"id": "uk-cites", "org": "UK Government", "title": "CITES imports and exports", "url": "https://www.gov.uk/guidance/cites-imports-and-exports", "category": "law", "note": "UK permit and border rules for listed species."},
    {"id": "uk-nwcu", "org": "National Wildlife Crime Unit", "title": "UK National Wildlife Crime Unit", "url": "https://www.nwcu.police.uk/", "category": "enforcement", "note": "UK wildlife-crime policing context."},
    {"id": "eu-twix", "org": "EU-TWIX", "title": "EU Trade in Wildlife Information Exchange", "url": "https://www.eu-twix.org/", "category": "enforcement", "note": "European information exchange for illegal wildlife trade."},
    {"id": "australia-cites", "org": "Australian Government", "title": "Wildlife trade and CITES", "url": "https://www.dcceew.gov.au/environment/wildlife-trade/cites", "category": "law", "note": "Australian CITES and wildlife-trade controls."},
    {"id": "canada-cites", "org": "Government of Canada", "title": "CITES in Canada", "url": "https://www.canada.ca/en/environment-climate-change/services/convention-international-trade-endangered-species.html", "category": "law", "note": "Canadian CITES implementation."},
    {"id": "nz-cites", "org": "New Zealand Department of Conservation", "title": "CITES", "url": "https://www.doc.govt.nz/about-us/international-agreements/cites/", "category": "law", "note": "New Zealand CITES implementation."},
    {"id": "singapore-nparks-cites", "org": "NParks Singapore", "title": "About CITES", "url": "https://avs.nparks.gov.sg/wildlife/wildlife-trade/cites/about/", "category": "law", "note": "Singapore permitting and species-protection system."},
    {"id": "singapore-wildlife-trade", "org": "NParks Singapore", "title": "Importing or exporting wildlife and endangered species", "url": "https://avs.nparks.gov.sg/businesses/commercial-importers-exporters/animals/wildlife-endangered-species/", "category": "enforcement", "note": "Singapore wildlife-trade enforcement and public guidance."},
    {"id": "hongkong-afcd", "org": "Hong Kong AFCD", "title": "Protection of Endangered Species", "url": "https://www.afcd.gov.hk/english/conservation/con_end/con_end.html", "category": "law", "note": "Hong Kong endangered-species protection context."},
    {"id": "hongkong-customs", "org": "Hong Kong Customs", "title": "Customs press releases", "url": "https://www.customs.gov.hk/en/customs-announcement/press-release/index.html", "category": "port", "note": "Customs release archive used for seizure context."},
    {"id": "india-wccb", "org": "Wildlife Crime Control Bureau", "title": "Wildlife Crime Control Bureau", "url": "https://wccb.gov.in/", "category": "enforcement", "note": "Indian wildlife-crime enforcement agency."},
    {"id": "south-africa-rhino", "org": "South African DFFE", "title": "Rhino poaching statistics", "url": "https://www.dffe.gov.za/mediarelease/rhinopoaching_statistics_2024", "category": "enforcement", "note": "Rhino poaching and enforcement context."},
    {"id": "kenya-wildlife-service", "org": "Kenya Wildlife Service", "title": "Kenya Wildlife Service", "url": "https://www.kws.go.ke/", "category": "community", "note": "East African wildlife-management and anti-poaching context."},
    {"id": "malaysia-wildlife", "org": "PERHILITAN Malaysia", "title": "Department of Wildlife and National Parks", "url": "https://www.wildlife.gov.my/", "category": "enforcement", "note": "Malaysian wildlife enforcement and conservation context."},
    {"id": "traffic-iwt", "org": "TRAFFIC", "title": "Wildlife crime", "url": "https://www.traffic.org/what-we-do/thematic-issues/wildlife-crime/", "category": "research", "note": "TRAFFIC overview of illegal wildlife trade."},
    {"id": "traffic-publications", "org": "TRAFFIC", "title": "Publications", "url": "https://www.traffic.org/publications/", "category": "research", "note": "Report library used for commodity and market checks."},
    {"id": "traffic-portal", "org": "TRAFFIC", "title": "Wildlife Trade Portal", "url": "https://www.wildlifetradeportal.org/", "category": "research", "note": "Open seizure-report portal for wildlife trade incidents."},
    {"id": "traffic-pangolin", "org": "TRAFFIC", "title": "The global trafficking of pangolins", "url": "https://www.traffic.org/publications/reports/the-global-trafficking-of-pangolins/", "category": "market", "note": "Pangolin commodity and trafficking context."},
    {"id": "traffic-glass-eel", "org": "TRAFFIC", "title": "European eel trafficking surge", "url": "https://www.traffic.org/news/traffic-warns-of-european-eel-trafficking-surge/", "category": "marine", "note": "Glass eel trafficking and enforcement context."},
    {"id": "traffic-songbirds", "org": "TRAFFIC", "title": "Asian Songbirds", "url": "https://www.traffic.org/what-we-do/species/asian-songbirds/", "category": "birds", "note": "Songbird trade and market-pressure background."},
    {"id": "traffic-reptiles-japan", "org": "TRAFFIC", "title": "Reptiles and amphibians endemic to Japan's Nansei Islands", "url": "https://www.traffic.org/vn/publications/reports/reptiles-and-amphibians-endemic-to-japans-nansei-islands-japanese/", "category": "online", "note": "Reptile and amphibian pet-trade case source."},
    {"id": "traffic-sharks-rays", "org": "TRAFFIC", "title": "SharkTrace", "url": "https://www.traffic.org/sharktrace/", "category": "marine", "note": "Shark and ray trade pressure source."},
    {"id": "wwf-iwt", "org": "WWF", "title": "Illegal wildlife trade", "url": "https://www.worldwildlife.org/threats/illegal-wildlife-trade", "category": "research", "note": "Accessible overview of illegal wildlife trade threats."},
    {"id": "wwf-uk-iwt", "org": "WWF", "title": "The latest trends in the illegal wildlife trade", "url": "https://www.worldwildlife.org/news/stories/the-latest-trends-in-the-illegal-wildlife-trade/", "category": "research", "note": "Demand and enforcement frame from WWF."},
    {"id": "wwf-coalition", "org": "WWF", "title": "Coalition to End Wildlife Trafficking Online", "url": "https://www.worldwildlife.org/initiatives/coalition-to-end-wildlife-trafficking-online", "category": "online", "note": "Platform coalition source for online trade."},
    {"id": "coalition-online", "org": "Coalition to End Wildlife Trafficking Online", "title": "Coalition homepage", "url": "https://www.endwildlifetraffickingonline.org/", "category": "online", "note": "Online platform response and member context."},
    {"id": "ifaw-cybercrime", "org": "IFAW", "title": "Disrupting Wildlife Cybercrime", "url": "https://www.ifaw.org/projects/wildlife-cybercrime-prevention-global", "category": "online", "note": "Online wildlife-trafficking campaign and evidence."},
    {"id": "ifaw-offline", "org": "IFAW", "title": "Wildlife cybercrime factsheet", "url": "https://www.ifaw.org/ca-en/resources/wildlife-cybercrime-factsheet", "category": "online", "note": "Online listings and illegal wildlife trade report."},
    {"id": "ifaw-disrupt", "org": "IFAW", "title": "Disrupt: Wildlife Cybercrime", "url": "https://www.ifaw.org/resources/disrupt-wildlife-cybercrime", "category": "online", "note": "Cybercrime and platform enforcement source."},
    {"id": "wjc-home", "org": "Wildlife Justice Commission", "title": "Our work", "url": "https://wildlifejustice.org/our-work/", "category": "enforcement", "note": "Intelligence-led investigation model."},
    {"id": "wjc-rhino", "org": "Wildlife Justice Commission", "title": "Rhino horn trafficking report", "url": "https://wildlifejustice.org/rhino-horn-trafficking-report/", "category": "market", "note": "Transnational rhino-horn trafficking report."},
    {"id": "wjc-disruption-disarray", "org": "Wildlife Justice Commission", "title": "Disruption and Disarray", "url": "https://wildlifejustice.org/wildlife-justice-commission-report-reveals-major-disruption-in-pangolin-scale-and-ivory-trafficking/", "category": "market", "note": "Pangolin scale and ivory trafficking analysis through 2024."},
    {"id": "wjc-convergence", "org": "Wildlife Justice Commission", "title": "Convergence of wildlife crime with other organised crime", "url": "https://wildlifejustice.org/convergence-wildlife-crime-organised-crime/", "category": "law", "note": "Crime convergence with drugs, seafood, tax and corruption."},
    {"id": "wjc-corruption", "org": "Wildlife Justice Commission", "title": "Dirty Money: corruption and wildlife crime", "url": "https://wildlifejustice.org/new-report-sheds-light-on-the-key-role-of-corruption-in-enabling-wildlife-crime/", "category": "law", "note": "Corruption risk in wildlife-crime supply chains."},
    {"id": "eia-wildlife", "org": "Environmental Investigation Agency", "title": "Wildlife", "url": "https://eia-international.org/wildlife/", "category": "research", "note": "Investigative source on wildlife trafficking."},
    {"id": "eia-tipping-scales", "org": "Environmental Investigation Agency", "title": "Smoke and Mirrors", "url": "https://eia-international.org/report/chinas-complicity-in-the-global-illegal-pangolin-trade-smoke-and-mirrors/", "category": "market", "note": "Pangolin trafficking and market-pressure report."},
    {"id": "eia-out-of-africa", "org": "Environmental Investigation Agency", "title": "Out of Africa", "url": "https://reports.eia-international.org/out-of-africa/", "category": "market", "note": "Ivory trafficking investigation source."},
    {"id": "eia-totoaba", "org": "Environmental Investigation Agency", "title": "On Borrowed Time", "url": "https://eia-international.org/report/on-borrowed-time/", "category": "marine", "note": "Totoaba swim-bladder trade and vaquita pressure."},
    {"id": "wildaid-sharks", "org": "WildAid", "title": "Sharks", "url": "https://wildaid.org/programs/sharks/", "category": "marine", "note": "Demand-reduction and shark-fin trade context."},
    {"id": "wcs-wildlife-trade", "org": "Wildlife Conservation Society", "title": "Wildlife trade", "url": "https://programs.wcs.org/wildlifetrade/", "category": "research", "note": "Conservation and public-health frame for wildlife trade."},
    {"id": "panthera-trade", "org": "Panthera", "title": "The Illegal Wildlife Trade", "url": "https://panthera.org/threat-illegal-wildlife-trade", "category": "market", "note": "Big-cat and jaguar trafficking context."},
    {"id": "irf-rhino", "org": "International Rhino Foundation", "title": "State of the Rhino", "url": "https://rhinos.org/about-rhinos/state-of-the-rhino/", "category": "market", "note": "Rhino conservation and trafficking context."},
    {"id": "save-elephants-etis", "org": "CITES / TRAFFIC", "title": "Elephant Trade Information System", "url": "https://cites.org/eng/prog/etis", "category": "market", "note": "Ivory seizure monitoring context."},
    {"id": "shark-trust", "org": "Shark Trust", "title": "Position Statement: UK Shark Fin Ban", "url": "https://www.sharktrust.org/banning-the-import-of-shark-fins-to-uk", "category": "marine", "note": "Public explainer on shark-fin demand and regulation."},
    {"id": "nature-reptile-trade", "org": "Nature Communications", "title": "Thousands of reptile species threatened by under-regulated global trade", "url": "https://www.nature.com/articles/s41467-020-18523-4", "category": "research", "note": "Peer-reviewed analysis of web-based reptile trade gaps."},
    {"id": "nature-trade-impact", "org": "Nature Ecology & Evolution", "title": "Impacts of wildlife trade on terrestrial biodiversity", "url": "https://www.nature.com/articles/s41559-021-01399-y", "category": "research", "note": "Meta-analysis of trade-driven population declines."},
    {"id": "nature-cites-gaps", "org": "Nature Ecology & Evolution", "title": "Species likely threatened by international trade", "url": "https://www.nature.com/articles/s41559-023-02115-8", "category": "research", "note": "Research on CITES gaps for trade-threatened species."},
    {"id": "nature-alien-vertebrates", "org": "Nature Communications", "title": "Alien vertebrates from wildlife trade", "url": "https://www.nature.com/articles/s41467-023-43754-6", "category": "research", "note": "Live wildlife trade and invasive vertebrate risk."},
    {"id": "sci-reports-snake", "org": "Scientific Reports", "title": "Slow life history leaves endangered snake vulnerable to illegal collecting", "url": "https://www.nature.com/articles/s41598-021-84745-1", "category": "research", "note": "Example of rare reptile demand and population vulnerability."},
    {"id": "frontiers-primates", "org": "Frontiers in Conservation Science", "title": "Primate trade and conservation crisis", "url": "https://www.frontiersin.org/journals/conservation-science/articles/10.3389/fcosc.2024.1400613/full", "category": "research", "note": "Nonhuman primate trade, pet demand and online market source."},
    {"id": "plos-iwt-value-usa", "org": "PLOS ONE", "title": "Economic value of illegal wildlife trade entering the USA", "url": "https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0258523", "category": "research", "note": "Open-method valuation and LEMIS-related seizure context."},
    {"id": "plos-pangolin-detection", "org": "PLOS ONE", "title": "Where are you hiding the pangolins?", "url": "https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0299152", "category": "forensics", "note": "Detection tools and inspection-method review for wildlife contraband."},
    {"id": "springer-songbirds", "org": "Biodiversity and Conservation", "title": "Songbirds on sale across online and physical markets in Indonesia", "url": "https://link.springer.com/article/10.1007/s10531-024-02825-w", "category": "birds", "note": "Online and physical market comparison for songbirds."},
    {"id": "springer-pangolins-india", "org": "European Journal of Wildlife Research", "title": "Illegal trade of pangolins in India", "url": "https://link.springer.com/article/10.1007/s10344-023-01708-9", "category": "research", "note": "Pangolin seizure analysis and prosecution context."},
    {"id": "stoten-glass-eels", "org": "Science of the Total Environment", "title": "Health of smuggled European glass eels", "url": "https://www.sciencedirect.com/science/article/pii/S0048969724085048", "category": "marine", "note": "Physiological impact of glass eel trafficking."},
    {"id": "marine-policy-eels", "org": "Marine Policy", "title": "Crime script analysis of European eel trafficking", "url": "https://www.sciencedirect.com/science/article/pii/S0308597X24005694", "category": "marine", "note": "Illegal eel trade process and source-to-market script."},
    {"id": "sharks-plane", "org": "Forensic Science International: Animals and Environments", "title": "Sharks on a plane", "url": "https://www.sciencedirect.com/science/article/pii/S2666937422000154", "category": "marine", "note": "Shark-fin seizure and CITES-listed species identification source."},
    {"id": "plos-youtube-exotic", "org": "PLOS ONE", "title": "Is YouTube promoting the exotic pet trade?", "url": "https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0235451", "category": "online", "note": "Online content and exotic-pet demand source."},
    {"id": "plos-spillover-regulation", "org": "PLOS ONE", "title": "Preventing zoonotic spillover and wildlife trade regulation", "url": "https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0312012", "category": "research", "note": "Regulatory approaches and zoonotic-risk framing."},
    {"id": "nature-food-risky", "org": "Nature Food", "title": "Risky business", "url": "https://www.nature.com/articles/s43016-021-00330-9", "category": "research", "note": "Wildlife trade and zoonotic-risk assessment context."},
    {"id": "plos-rarity-value", "org": "PLOS Biology", "title": "Rarity value and species extinction", "url": "https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.0040415", "category": "research", "note": "Anthropogenic Allee effect and rare-species market logic."},
    {"id": "rusi-illicit-finance", "org": "RUSI", "title": "Illegal wildlife trade and illicit finance in the UK", "url": "https://static.rusi.org/314_WHR_G7_IWT_UK.pdf", "category": "law", "note": "UK illicit-finance and wildlife-trafficking source."},
    {"id": "global-initiative-iwt", "org": "Global Initiative Against Transnational Organized Crime", "title": "Illegal wildlife trade analysis", "url": "https://globalinitiative.net/analysis/illegal-wildlife-trade/", "category": "law", "note": "Organized-crime analysis of illegal wildlife trade."},
    {"id": "tnrc-crime-convergence", "org": "WWF TNRC", "title": "Crime convergence and natural resources", "url": "https://www.worldwildlife.org/projects/crime-convergence-natural-resource-exploitation-and-transnational-organized-crime", "category": "law", "note": "Natural-resource crime convergence and corruption context."},
]

SECTION_SOURCE_IDS = [
    ["interpol-thunder-2025", "unodc-wwcr-2024", "cites-what", "fws-placeholder"],
]

SECTIONS = [
    {
        "id": "customs-opens-the-box",
        "title": "Customs opens the box",
        "source_ids": ["interpol-thunder-2025", "interpol-wildlife-crime", "usfws-ole", "usfws-inspection", "wco-environment", "hongkong-customs", "singapore-wildlife-trade", "plos-pangolin-detection"],
        "paragraphs": [
            "At the border, wildlife trafficking rarely announces itself as a crime against nature. It arrives as freight. It arrives as a checked bag, a padded envelope, an aquarium shipment, a crate with bad paperwork, a parcel with air holes, a container whose manifest describes something legal, or a phone message that tells a buyer where to meet. Customs officers do not open a myth. They open packaging.",
            "The shock of the trade is not only that animals are captured. It is that the capture is converted so quickly into logistics. A forest animal becomes a shipment. A reef animal becomes a line item. A bird becomes a voice in a cage, a reptile becomes a private collection, a shark becomes fins, a pangolin becomes scales, and the whole transaction can move through routes built for ordinary commerce.",
            "INTERPOL's Operation Thunder 2025 gives the article its first hard edge: authorities in 134 countries reported 4,640 seizures, identified 1,100 suspects, and seized nearly 30,000 live animals during a one-month global operation against wildlife and forestry crime. The same operation reported more than 245 tonnes of protected marine wildlife seized, including thousands of shark-fin pieces. [[interpol-thunder-2025]]",
            "That does not mean enforcement has counted the whole market. Seizures are evidence of detection, not a census of hidden trade. A bigger operation can mean stronger enforcement, larger flows, better intelligence, or all three at once. But the source trail still tells us something specific: this is not a single animal story and not a single smuggling route. It is a system with many entrances.",
            "The phrase 'wildlife trafficking' can sound abstract, so it helps to slow the definition down. The trade covers protected animals, animal parts and derivatives moved or sold in violation of international or domestic law. It includes poaching, capture, purchase, storage, laundering, transport, sale, finance and concealment. It can be organized, opportunistic, local, transnational, online, physical, violent, bureaucratic, small-scale or industrial. [[interpol-wildlife-crime]][[unodc-wwcr-2024]]",
            "The first pattern in the source review is simple: the illegal wildlife trade does not behave like a narrow black market. It behaves like a set of shadow supply chains plugged into legal systems. It uses the same roads, airports, ports, parcel networks, banking channels, messaging apps, breeders, exporters, importers and paperwork habits that make the legitimate economy work.",
            "That matters because a supply-chain crime is harder to fight than a single act of poaching. The animal may be taken in one country, held in another, mislabeled in a third, shipped through a fourth and sold to a buyer who never sees the place where the capture happened. Each handoff creates distance. Distance is useful to the trafficker because it turns responsibility blurry.",
            "Start at a checkpoint because that is where the fantasy of separation collapses. What looks like a conservation problem in a forest becomes a customs problem in a terminal, a platform problem on a phone and a banking problem in a suspicious transaction report. By the time it becomes a veterinary problem in a quarantine room or a courtroom problem in a prosecution file, the animal has already paid the price."
        ],
    },
    {
        "id": "desire-is-the-demand-side",
        "title": "Desire is the demand side",
        "source_ids": ["wwf-iwt", "wwf-uk-iwt", "ifaw-cybercrime", "plos-rarity-value", "frontiers-primates", "plos-youtube-exotic", "traffic-reptiles-japan", "springer-songbirds"],
        "paragraphs": [
            "The trade begins with capture, but it does not begin only with poverty, corruption or weak enforcement. It begins with desire. Someone wants a pet that feels rare. Someone wants a medicine that carries old prestige. Someone wants a carved object, a trophy, a soup, a belt, a photo, a private zoo or a song in a cage. Someone wants a skin, a scale, a tusk, a horn, a fin, a live reptile that nobody else has, or a status symbol that gains value because most people cannot legally obtain it.",
            "That demand is not morally identical everywhere. A rural household eating wild meat is not the same as a wealthy collector buying a protected tortoise. A long-standing local use is not the same as a criminal network exporting tonnes of scales. A legal aquarium shipment is not the same as an illegally sourced reef fish laundered through false paperwork. The article has to hold that nuance or it becomes too easy and too false.",
            "Still, the demand side has patterns. Rare animals can become more valuable because they are rare, a dynamic researchers call the anthropogenic Allee effect: human desire rises as scarcity itself becomes part of the attraction. The market does not always stop when a species becomes scarce. Sometimes scarcity is the advertisement. [[plos-rarity-value]]",
            "Online culture makes that problem faster. A rare animal once required specialist networks, physical markets and private contacts. Now a buyer can find desire through videos, groups, marketplace listings, direct messages and coded posts. Research on exotic-pet content and online primate trade shows how attention can normalize ownership and make difficult species look accessible. [[plos-youtube-exotic]][[frontiers-primates]]",
            "The second pattern is more uncomfortable: wildlife trafficking is not only a supply crime. It is a demand machine. Enforcement can catch a shipment, but if the animal is replaced immediately because the buyer still wants the object, the market stays alive. Demand reduction is not a soft add-on. It is part of the enforcement problem.",
            "The old image of a poacher alone in a forest misses the middle of the story. A poacher may be desperate, paid little and replaceable. The durable money is often elsewhere: with the dealer who knows the route, the exporter who knows the paperwork, the broker who knows the buyer and the platform account that finds customers. It can also sit with the corrupt official who looks away or the collector who treats law as inconvenience.",
            "A demand story also keeps the article from flattening people at the source. When a buyer in a wealthy market wants rarity, the pressure can land on a community living beside the animal. That does not excuse illegal capture, but it changes the moral geometry. The question is not only who touched the animal first. It is who created the price that made the touch worth risking.",
            "The animals carry the cost most visibly, but desire is the weather system around the trade. It decides which species becomes fashionable, which body part becomes medicine or luxury, which online image becomes a sales pitch, and which enforcement success simply raises the price."
        ],
    },
    {
        "id": "legal-trade-casts-a-shadow",
        "title": "Legal trade casts a shadow",
        "source_ids": ["cites-what", "cites-appendices", "cites-trade-db", "tradeview", "tradeview-faq", "speciesplus", "cites-wwtr-2022", "nature-cites-gaps"],
        "paragraphs": [
            "Not all wildlife trade is illegal. That sentence matters. The world legally trades animals, plants and their products for food, fashion, research, medicine, timber, pets, aquariums, zoos, hunting trophies and cultural uses. Some legal trade is regulated, documented and sustainable. Some is poorly managed. Some illegal trade hides inside legal trade, which is where the story becomes difficult.",
            "CITES, the Convention on International Trade in Endangered Species of Wild Fauna and Flora, is the treaty system at the center of international wildlife trade. Species listed in its appendices are subject to different levels of control. Appendix I generally covers species threatened with extinction where commercial international trade is highly restricted. Appendix II covers species that may become threatened if trade is not controlled. Appendix III is used when a country asks others to help regulate trade in a species it protects domestically. [[cites-what]][[cites-appendices]]",
            "That system is essential, but it is not omniscient. The CITES Trade Database and Wildlife TradeView record reported legal trade in listed species; they do not automatically show illegal trade, domestic markets, unlisted species, false declarations, laundering or animals that never enter official reporting. Wildlife TradeView's own caveats are important because readers need to understand that official trade data is a window, not the room. [[cites-trade-db]][[tradeview]][[tradeview-faq]]",
            "One original conclusion from reviewing the source stack is that the same word, 'trade,' hides at least four different realities: legal and documented trade; legal but weakly monitored trade; illegal trade in listed species; and trade in species not yet regulated internationally but still under pressure. A single policy tool cannot see all four clearly at once.",
            "The under-regulated species problem is especially sharp for animals that are small, numerous, hard to identify or fashionable in specialist markets. Nature Communications research on the reptile trade found extensive online trade in reptile species, including many not covered by international regulation. Nature Ecology & Evolution research likewise identified species likely threatened by international trade that were not all covered by CITES. [[nature-reptile-trade]][[nature-cites-gaps]]",
            "Laundering is the shadow cast by legal trade. A wild-caught animal can be declared captive-bred. A protected product can be mixed with legal product. A document can be forged. A species can be mislabeled. A shipment can be broken into pieces. A route can be chosen because inspectors are busy or identification expertise is thin.",
            "The data problem is not a failure of spreadsheets. It is a failure of reality to fit neatly into them. Legal trade records can be excellent for asking what was declared, by whom and under which code. They are weaker for asking what was hidden, mislabeled, sold domestically, moved through informal routes or never listed for protection. Good analysis has to keep those limits visible instead of pretending the neat number is the whole world.",
            "The answer is not to pretend legal trade and illegal trade are the same. They are not. The answer is to recognize that illegal trade often studies legal trade carefully. It learns the forms, the ports, the language, the loopholes and the places where a live animal can become paperwork."
        ],
    },
    {
        "id": "small-animals-move-easily",
        "title": "Small animals move easily",
        "source_ids": ["nature-reptile-trade", "traffic-reptiles-japan", "sci-reports-snake", "springer-songbirds", "traffic-songbirds", "cites-illegal-trade-reports", "frontiers-primates", "plos-iwt-value-usa"],
        "paragraphs": [
            "Elephants and rhinos dominate the public imagination because they are enormous, beloved and visually unmistakable. But much of the wildlife trade is built from animals that fit into boxes, sleeves, tubes, water bags, parcels, backpacks and false compartments. Size is an economic fact. Small animals are easier to hide, cheaper to ship and harder for a non-specialist inspector to identify.",
            "Reptiles show the pattern clearly. The pet market can make obscure species valuable precisely because they are obscure. A newly described gecko, turtle or snake can be attractive to collectors before regulators, customs officers and even many conservation readers have learned its name. Scientific discovery can accidentally become market discovery.",
            "The Nature Communications reptile-trade study found that over 35% of reptile species were traded online in the dataset the authors built, and that many traded species were not covered by international trade regulation. That is not a little niche hobby. It is a global market hiding in taxonomy. [[nature-reptile-trade]]",
            "Birds show a different texture of the same problem. Songbird trade in parts of Southeast Asia is tied to culture, status, song competitions and household keeping, but it also drives capture pressure from the wild. Research comparing online and physical markets in Indonesia found large numbers of species for sale, including threatened and protected species. [[springer-songbirds]][[traffic-songbirds]]",
            "Call it the portability trap: the animals most easily moved are often the animals least visible to the public. A tortoise in a sock, a gecko in a plastic container, a bird in a tube or a frog in a parcel may never produce the kind of image that makes a global campaign. Neither will a coral fragment in water or an eel in a bag. The market understands that advantage.",
            "The enforcement challenge is not only finding hidden animals. It is knowing what they are. Species identification can require training, DNA analysis, expert networks, reference databases and access to current taxonomy. A general customs checkpoint is being asked to read a living library under time pressure.",
            "That is why small-animal trafficking is not a minor subplot. It is the place where the trade reveals its modern form: fast, specialized, online, portable, obscure, capable of shifting species quickly and often several steps ahead of the public's moral attention."
        ],
    },
    {
        "id": "online-market-never-closes",
        "title": "The online market never closes",
        "source_ids": ["wwf-coalition", "coalition-online", "ifaw-cybercrime", "ifaw-offline", "ifaw-disrupt", "plos-youtube-exotic", "frontiers-primates", "traffic-reptiles-japan"],
        "paragraphs": [
            "Online wildlife trafficking is not just animals listed with bad spelling on an open marketplace. It is public posts, coded language, closed groups, private messages, disappearing accounts, payment workarounds, encrypted chats, livestreams, influencers, recommendation systems and buyers who learn how to move from visible curiosity to private transaction.",
            "That does not mean every animal video is trafficking. It means online attention can create demand, normalize ownership, and connect buyers and sellers at a speed physical markets cannot match. A platform does not need to be designed for wildlife crime to become useful to wildlife crime.",
            "The Coalition to End Wildlife Trafficking Online, WWF, IFAW and TRAFFIC have pushed major technology companies to detect and remove illegal wildlife listings. The existence of that coalition is itself evidence of the market's migration: if wildlife trafficking were only happening in remote forests and back rooms, platform policy would not be part of the enforcement map. [[wwf-coalition]][[coalition-online]][[ifaw-cybercrime]]",
            "IFAW's online wildlife-trade reports show how digital marketplaces collapse distance. A buyer no longer has to visit a market where illegal animals are physically visible. The buyer can browse from home, ask coded questions, verify status in private, and move payment or pickup to another channel. [[ifaw-offline]][[ifaw-disrupt]]",
            "Platform enforcement creates displacement as well as disruption. Remove a post and the seller may move to another platform, another code word, another group, another account or a private messaging app. The goal cannot be one-time takedown totals alone. It has to be intelligence: identities, networks, repeat sellers, payment trails, routes and the movement from public advertisement to private deal.",
            "Online trade also changes who participates. A casual viewer can become a buyer. A hobbyist can become a broker. A breeder can become a laundering point. A legal-looking listing can conceal illegal origin. A video that looks cute can become a storefront for an animal whose capture killed others in the process.",
            "This is where the story becomes uncomfortably ordinary. Wildlife trafficking no longer requires the buyer to enter an obviously criminal place. Sometimes the first step looks like scrolling."
        ],
    },
    {
        "id": "ports-parcels-and-paper",
        "title": "Ports, parcels and paper",
        "source_ids": ["usfws-inspection", "wco-environment", "eu-twix", "hongkong-customs", "singapore-nparks-cites", "uk-cites", "australia-cites", "canada-cites"],
        "paragraphs": [
            "A trafficking route is a story about friction. The animal has to be captured, held, consolidated, described, hidden, transported, cleared, received and sold. Every step creates a chance to detect the trade and a chance to disguise it. Ports, airports, mail centers and border posts are not just geography. They are filters.",
            "Customs work is difficult because wildlife contraband can be alive, dead, processed, powdered, carved, dried, frozen, mixed, mislabeled or disguised as something else. A shipment of reptiles may require veterinary and species expertise. A box of fish maw or shark fins may require forensic identification. A carved object may require knowing whether the material is legal, antique, synthetic or protected.",
            "Paper is one of the trade's most important habitats. Permits, invoices, health certificates, captive-bred claims, country-of-origin statements, customs codes and shipping documents all become places where reality can be bent. False paperwork is not a side issue. It is how illegal wildlife learns to pass as legal commerce.",
            "The CITES system depends on documents, and documents depend on trust, expertise and verification. A real permit can be misused. A fake permit can look real. A captive-bred claim can hide wild capture. A legal shipment can carry illegal specimens mixed inside it. A code on a form can flatten a living creature into a bureaucratic category.",
            "Enforcement has a bottleneck problem. Wildlife crime requires specialist knowledge, but borders are built for volume. The more ordinary trade moves through a checkpoint, the more wildlife traffickers benefit from the pressure to keep goods moving.",
            "This does not make enforcement hopeless. It makes intelligence essential. Risk targeting, species-identification tools, shared databases, trained inspectors, forensic labs, international cooperation and financial investigations all help turn a border from a wall into a learning system.",
            "A learning system looks for patterns rather than miracles. Which exporter names recur? Which routes look strange for the declared product? Which species appear right after a new trend spreads online? Which permits cluster around the same broker? Which shipments move through a port where wildlife expertise is thin? The best border work is not only the dramatic opening of a box. It is the quiet accumulation of suspicion before the box arrives.",
            "The shipment is only one scene. The real target is the network that made the shipment possible."
        ],
    },
    {
        "id": "ocean-products-have-routes",
        "title": "Ocean products have routes",
        "source_ids": ["fao-fish-stocks-2025", "traffic-sharks-rays", "sharks-plane", "wildaid-sharks", "eia-totoaba", "traffic-glass-eel", "stoten-glass-eels", "marine-policy-eels"],
        "paragraphs": [
            "Wildlife trafficking is often imagined as animals moving from forest to market, but the ocean is just as much part of the story. Marine wildlife becomes fins, swim bladders, dried products, live reef animals, corals, eels, sea cucumbers, shells, ornamental fish and mislabeled seafood. Some of it travels as food. Some as medicine. Some as luxury. Some as aquarium life. Some as a product whose true species identity has been erased.",
            "Fish and marine animals are hard to police because extraction can be legal, illegal, unreported or unregulated in ways that overlap. FAO's 2025 global review of marine fishery resources found that 35.5% of assessed marine fish stocks were overfished, while 64.5% were exploited within biologically sustainable levels. That split is important: management can work, but it is not reaching everything. [[fao-fish-stocks-2025]]",
            "Shark fins show how species identity can disappear into product form. Once fins are dried, sorted, trimmed or processed, enforcement may need DNA analysis or expert identification to know whether protected species are present. Research on a major shark-fin seizure found threatened and CITES-listed species hidden inside a trade where the product is intentionally detached from the animal's visible body. [[sharks-plane]][[traffic-sharks-rays]]",
            "The totoaba swim-bladder trade shows an even harsher chain of consequence. Demand for a high-value fish part has helped push the vaquita, a small porpoise caught as bycatch in illegal gillnets, toward extinction. In that case, the product being trafficked is not the only animal paying the price. [[eia-totoaba]]",
            "European glass eels show another version of the same logistics problem. Tiny juvenile eels can be packed and moved in large numbers, feeding illegal export routes and aquaculture demand. Recent research has examined the health impact on smuggled glass eels and the crime script behind illegal eel fishing and trafficking. [[stoten-glass-eels]][[marine-policy-eels]]",
            "Marine wildlife crime often hides inside food systems. That makes it politically and socially harder than a simple ban narrative. People depend on fish. Legal seafood matters. Coastal livelihoods matter. But criminal trade exploits the same dependence by hiding protected, illegal or unsustainably sourced animals inside legitimate demand.",
            "The ocean does not make the trade cleaner. It makes the evidence wetter, more perishable and easier to disguise."
        ],
    },
    {
        "id": "organized-crime-is-not-a-movie",
        "title": "Organized crime is not always cinematic",
        "source_ids": ["fatf-iwt", "fincen-wildlife-threat", "fincen-environmental-crimes", "wjc-convergence", "wjc-corruption", "global-initiative-iwt", "tnrc-crime-convergence", "rusi-illicit-finance"],
        "paragraphs": [
            "Wildlife trafficking is often described as organized crime, but that phrase can mislead if it makes readers imagine only movie villains. Organized crime can be less theatrical and more administrative: someone knows the exporter, someone knows the official, someone knows the shipping route, someone knows the buyer, someone handles payment, someone absorbs the loss when a shipment is seized.",
            "Financial-crime sources matter because they show that wildlife trafficking is not only a matter of animals and borders. FATF, FinCEN, RUSI, WWF's TNRC project and Wildlife Justice Commission reporting all treat illegal wildlife trade as a financial and corruption problem as well as a conservation problem. [[fatf-iwt]][[fincen-wildlife-threat]][[rusi-illicit-finance]]",
            "The money can be surprisingly ordinary. Wildlife profits may pass through trade companies, import-export businesses, cash couriers, informal value-transfer systems, bank accounts, shell companies, online payment services or businesses that also move legal goods. The transaction may not say 'pangolin scales.' It may say logistics, consulting, seafood, antiques, pets or something bland enough to pass.",
            "Wildlife crime often converges with other crimes at the level of services. A corrupt official, a shipping broker, a money launderer, a document fixer or a smuggling route can serve more than one illegal market. Wildlife trafficking does not need its own world when it can rent tools from existing criminal economies. [[wjc-convergence]][[tnrc-crime-convergence]]",
            "Corruption is the grease in the machine. It can appear at the source, where protected animals are removed; at the checkpoint, where documents are approved; at the port, where containers pass; at the courtroom, where cases collapse; or inside enforcement systems, where information leaks to traffickers. [[wjc-corruption]]",
            "But the organized-crime frame should not erase lower-level actors or local conditions. Some people enter the chain because poverty, weak governance or local market demand makes wildlife one of the few available cash sources. The powerful actors are often those who turn that local vulnerability into repeated export.",
            "Conservation language can become too clean here. A phrase like 'illegal wildlife trade' may contain a ranger who has not been paid, a fisher who has debts, a trader who moves several legal and illegal products and a customs officer under pressure. It may also contain a buyer with disposable income and a financier who never gets mud on their shoes. The phrase is useful, but it should not make all actors look equally powerful.",
            "That is why justice has to be precise. If enforcement only catches the replaceable collector at the bottom, the machine adapts. If it follows money, documents, communications and repeat logistics, the machine begins to lose memory."
        ],
    },
    {
        "id": "flagship-products-still-matter",
        "title": "Flagship products still matter",
        "source_ids": ["wjc-rhino", "wjc-disruption-disarray", "traffic-pangolin", "eia-tipping-scales", "eia-out-of-africa", "irf-rhino", "save-elephants-etis", "springer-pangolins-india"],
        "paragraphs": [
            "A serious article should not reduce wildlife trafficking to elephants, rhinos and pangolins. But it should not swing so far toward obscure markets that it forgets why those flagship products still matter. Ivory, rhino horn and pangolin scales have shown how organized networks can move high-value animal products across continents in large shipments.",
            "Wildlife Justice Commission's rhino horn report treats that market as transnational organized crime, not merely poaching. Its pangolin and ivory analysis describes a period when shipments from Africa to Asia reached industrial scale, followed by disruption after 2020 that did not simply reset to the earlier pattern. [[wjc-rhino]][[wjc-disruption-disarray]]",
            "Pangolins are especially useful for understanding how the public learns about wildlife crime. For years, pangolins were obscure to many readers in North America and Europe. Then large-scale seizures, conservation campaigns and pandemic-era attention made them a symbol of trafficking. The animal did not become more important when people noticed it. People became late to its importance.",
            "Ivory and rhino horn show the pull of old status markets and new enforcement pressure. Both products can be stored, carved, mixed into collections, laundered through antique claims or moved through networks that know how to handle high-risk goods. Both have generated intense conservation attention and equally intense policy disagreement about demand, stockpiles, dehorning, enforcement and trade bans.",
            "Flagship markets teach methods that smaller markets also use: concealment, corruption, forged documents, mixed shipments, route shifting, coded communication, price signaling and laundering. The species differ, but the business habits rhyme.",
            "The moral danger of flagship species is that they can make the crisis look like a few famous animals. The analytic value is that their cases leave records: seizure data, investigations, prosecutions, forensic studies, market reports, demand campaigns and network analysis.",
            "The famous animals are not the whole story. They are the loudest court documents."
        ],
    },
    {
        "id": "forensics-turns-body-into-evidence",
        "title": "Forensics turns body into evidence",
        "source_ids": ["plos-pangolin-detection", "sharks-plane", "usfws-ole", "noaa-ole", "singapore-nparks-cites", "tradeview", "speciesplus", "iucn-red-list"],
        "paragraphs": [
            "Wildlife forensics begins with a sad premise: after the animal has been captured, killed, processed or mislabeled, science may be needed to tell the law what happened. A fin, scale, feather, shell, bone, powder, carving, egg, skin or piece of meat can become evidence only if someone can identify it well enough for the law to act.",
            "That identification work is technical but not decorative. DNA testing can distinguish species in processed products. Morphology can identify specimens when the body is intact. Reference databases can connect legal listings to scientific names. Isotope analysis, genetics and trace evidence can sometimes help infer origin. The courtroom needs more than suspicion. It needs proof.",
            "Research on detection tools for wildlife contraband asks a practical enforcement question: where are you hiding the pangolins? The answer is not one technology. X-ray screening, detector dogs, forensic analysis, risk profiling and human expertise each have limits, costs and use cases. [[plos-pangolin-detection]]",
            "Forensics also exposes laundering. If a shipment declared as legal species contains protected species, the law needs a way to show it. If a product is falsely labeled, the label must be challenged. If a captive-bred claim is suspicious, investigators need a path beyond vibes.",
            "Science does not sit outside enforcement. It is enforcement infrastructure. A wildlife lab, a trained inspector and an expert taxonomist can change the legal meaning of a box.",
            "The difficulty is scale. The number of species in trade is enormous, and many agencies do not have enough access to specialist expertise. The animal world is too diverse for a border system built around commodity categories.",
            "That is why better enforcement is partly a knowledge problem. The state has to recognize life fast enough to protect it."
        ],
    },
    {
        "id": "health-and-welfare-are-not-sidebars",
        "title": "Health and welfare are not sidebars",
        "source_ids": ["ipbes-invasive", "nature-alien-vertebrates", "plos-spillover-regulation", "nature-food-risky", "wcs-wildlife-trade", "stoten-glass-eels", "frontiers-primates", "protected-planet-2024"],
        "paragraphs": [
            "Wildlife trafficking is often discussed as a threat to species, but every shipment also contains welfare and health risks. Animals are captured, crowded, starved, dehydrated, taped, boxed, chilled, overheated, transported and handled in conditions that would be unacceptable if the buyer had to watch the whole journey.",
            "That suffering is not only an ethical fact. It changes disease risk, mortality, stress physiology and the chance that animals escape or are released into ecosystems where they do not belong. Live wildlife trade can move pathogens, parasites and invasive species along with animals. [[ipbes-invasive]][[nature-alien-vertebrates]]",
            "The pandemic made wildlife trade politically explosive, sometimes in ways that flattened the science. The careful position is not that every wildlife market creates the same risk, or that bans solve everything. It is that close human-wildlife contact, stressed animals, mixed species, weak regulation and poor hygiene can increase spillover risk, and that risk management has to be specific enough to work. [[plos-spillover-regulation]][[nature-food-risky]]",
            "Animal welfare also affects enforcement outcomes. A seizure is not the end of the animal's story. Confiscated animals need quarantine, veterinary care, identification, legal holding, possible repatriation, sanctuary space or humane long-term placement. Rescue centers become part of the border system.",
            "A seizure can become a second crisis if authorities do not have a plan for the living animals they rescue. Enforcement capacity must include cages, food, veterinarians, permits, disease control and decisions about whether an animal can ever return to the wild.",
            "This is where public emotion can mislead. The photo of rescued animals feels like a happy ending. Often it is only the start of a more complicated obligation.",
            "A trade that treats animals as cargo leaves governments and caregivers to put the animal back into the category it never should have left: a living being with needs."
        ],
    },
    {
        "id": "what-actually-works",
        "title": "What actually works",
        "source_ids": ["iccwc", "iccwc-toolkit", "cites-illegal-trade-reports", "eu-twix", "fincen-environmental-crimes", "wwf-coalition", "wjc-home", "traffic-portal"],
        "paragraphs": [
            "There is no single lever that ends wildlife trafficking. If anyone promises one, they are selling a poster, not a policy. The trade is too varied: live reptiles, songbirds, pangolin scales, shark fins, eels, ivory, rhino horn, corals, primates, tortoises, skins, trophies, meat, medicines and online exotic pets do not move in exactly the same way.",
            "What works is layered. Strong laws matter, but only if penalties are credible and prosecutors can use them. Border inspections matter, but only if officers have species knowledge and risk intelligence. CITES permits matter, but only if documents can be verified. Online takedowns matter, but only if they feed investigation rather than just hiding sellers. Demand reduction matters, but only if it understands why buyers want the animal or product.",
            "Financial investigations matter because the animal is not the only trail. Money, bank accounts, shell companies, payment processors, invoices and trade businesses can identify repeat actors. That is why FinCEN and FATF sources belong in an animal story. [[fatf-iwt]][[fincen-environmental-crimes]]",
            "International cooperation matters because animals do not respect borders and traffickers exploit them. ICCWC, CITES reporting, EU-TWIX and INTERPOL operations all exist because a seizure in one country may be only a fragment of a route. [[iccwc]][[cites-illegal-trade-reports]][[eu-twix]]",
            "Community protection matters because the source is not abstract. The animal is taken from somewhere. Local rangers, Indigenous communities, fishers, forest communities and frontline conservation workers often see the trade before the world does. If they are excluded from benefits and decisions, conservation becomes a lecture delivered from far away.",
            "Rescue capacity matters too, and it is easy to forget because it begins after the headline. A raid that saves live animals still has to answer basic questions: Where will they go tonight? Who can identify them? What do they eat? Are they carrying disease? Can they be returned to the wild without harming other animals? Who pays for long-term care if return is impossible? Enforcement without aftercare can turn victory into backlog.",
            "The best responses raise risk at multiple points in the chain while lowering demand at the end. A route should become harder to use. A buyer should become less eager. A broker should become easier to identify. A corrupt official should face consequences. A local community should have a better option than feeding the chain.",
            "The trade begins with capture and ends with desire. So the response has to begin before capture and continue after desire changes shape."
        ],
    },
    {
        "id": "original-findings",
        "title": "What this review found",
        "source_ids": ["unodc-wwcr-2024", "interpol-thunder-2025", "nature-reptile-trade", "fincen-wildlife-threat", "ifaw-cybercrime", "wjc-convergence", "plos-iwt-value-usa", "traffic-portal"],
        "paragraphs": [
            "The Press reviewed more than 100 public sources for this story: international enforcement releases, treaty pages, seizure reports, government guidance, financial-crime advisories, NGO investigations, commodity reports and peer-reviewed studies. The point was not to produce a perfect measurement of a hidden market. Nobody can do that from public documents alone. The point was to identify the recurring machinery.",
            "Finding one: the trade is most visible when it becomes logistics. Seizures, prosecutions and trade databases repeatedly show animals and products moving through ports, airports, parcels, containers, documents and online listings. The capture site matters, but the supply chain is where the trade becomes durable.",
            "Finding two: the public species hierarchy is distorted. Elephants, rhinos and pangolins deserve attention, but the source stack repeatedly points to reptiles, songbirds, eels, sharks, corals, primates, turtles and lesser-known species that move because they are portable, profitable, fashionable or hard to identify.",
            "Finding three: legal trade is both essential context and exploitable cover. CITES data, permits and appendices make regulation possible, but traffickers can use false captive-bred claims, mislabeling and document fraud to make illegal origin look legitimate.",
            "Finding four: online trade changes the front door. The buyer does not always have to know a trafficker. The buyer can start with a video, a listing, a message or a hobby community and move into private channels. Platform enforcement is now part of conservation enforcement.",
            "Finding five: the money trail is underused in the public imagination. Wildlife trafficking is often narrated through animals and raids, but financial-crime sources show why suspicious transactions, trade companies and money laundering matter.",
            "Finding six: enforcement success is often mistaken for market size. A large seizure is a fact about detection and a clue about flows. It is not, by itself, a clean measure of how much trade exists. The same warning applies to takedown counts online.",
            "Finding seven: the animal welfare problem continues after rescue. Every living seizure creates care obligations. The story does not end when the crate opens.",
            "A final caution sits underneath all seven findings: public evidence is uneven. Some countries report more, some publish less, some have stronger investigative capacity, and some markets are simply harder to see. The most visible species are not always the most threatened by trade. The most photographed seizure is not always the most important one. The most available data is not always the best map.",
            "Together these findings point away from a simple crime story and toward a supply-chain story. Wildlife trafficking is what happens when living things are fed into systems built to move products quickly and cheaply."
        ],
    },
    {
        "id": "cargo-with-a-heartbeat",
        "title": "Cargo with a heartbeat",
        "source_ids": ["iucn-red-list", "iucn-summary", "ipbes-global", "wwf-iwt", "traffic-iwt", "wcs-wildlife-trade", "protected-planet-2024", "cms-migratory"],
        "paragraphs": [
            "The deepest mistake in wildlife trafficking is categorical. The trade turns an animal into inventory, then asks the world to respond after the category has already done damage.",
            "A tortoise is not inventory. A parrot is not inventory. A pangolin is not inventory. A shark is not inventory. A gecko on a phone screen is not inventory. A coral fragment is not inventory. A glass eel is not inventory. A rare animal in a private room is not proof of taste. It is evidence of a broken route between desire and restraint.",
            "This does not mean every human use of wildlife is the same. It means illegal and unsustainable trade has a particular moral logic. It separates the buyer's desire from the animal's life, the product from the ecosystem, the shipment from the capture, the permit from the truth and the price from the cost.",
            "The global biodiversity record makes the stakes plain. IPBES identifies direct exploitation, land and sea-use change, climate change, pollution and invasive alien species as major drivers of nature loss. IUCN's Red List shows risk across major groups. Wildlife trade is not the only pressure, but it is a pressure humans can identify and reduce. [[ipbes-global]][[iucn-red-list]][[iucn-summary]]",
            "The future of this trade is not predetermined. Demand can fall. Enforcement can improve. Platforms can cooperate. Communities can protect source landscapes and waters. Courts can treat wildlife crime as serious crime. Financial institutions can flag suspicious patterns. Scientists can improve identification. Buyers can stop turning rarity into status.",
            "That last sentence may sound modest, but it is where the public has real power. No reader can personally inspect every container or rewrite every treaty. A reader can stop rewarding the idea that owning the rare thing is proof of sophistication. A reader can refuse exotic-pet content that hides suffering behind cuteness. A reader can ask whether a product has a legal, traceable source. Culture is not the whole market, but it is one of the market's engines.",
            "The article ends where the trade begins: with capture. Before the port, before the permit, before the listing, before the encrypted chat, before the buyer, before the seizure photo, there is an animal in a place where it belongs.",
            "That is the point the market tries to erase. Wildlife for sale is not only a crime story. It is a story about what happens when the living world is forced to fit inside the habits of commerce, and what it would take to make the route break before the animal does."
        ],
    },
]


RAIL_SOURCE_IDS_BY_SECTION = {
    "customs-opens-the-box": [
        "interpol-thunder-2025",
        "interpol-wildlife-crime",
        "interpol-environmental-crime",
        "usfws-ole",
        "usfws-wildlife-trafficking",
        "usfws-inspection",
        "wco-environment",
        "hongkong-customs",
    ],
    "desire-is-the-demand-side": [
        "wwf-iwt",
        "wwf-uk-iwt",
        "plos-rarity-value",
        "frontiers-primates",
        "plos-youtube-exotic",
        "traffic-reptiles-japan",
        "panthera-trade",
        "irf-rhino",
    ],
    "legal-trade-casts-a-shadow": [
        "cites-what",
        "cites-appendices",
        "cites-trade-db",
        "tradeview",
        "tradeview-faq",
        "speciesplus",
        "cites-illegal-trade-reports",
        "cites-wwtr-2022",
    ],
    "small-animals-move-easily": [
        "nature-reptile-trade",
        "nature-cites-gaps",
        "sci-reports-snake",
        "springer-songbirds",
        "traffic-songbirds",
        "plos-iwt-value-usa",
        "springer-pangolins-india",
        "plos-pangolin-detection",
    ],
    "online-market-never-closes": [
        "wwf-coalition",
        "coalition-online",
        "ifaw-cybercrime",
        "ifaw-offline",
        "ifaw-disrupt",
        "traffic-publications",
        "traffic-portal",
        "wcs-wildlife-trade",
    ],
    "ports-parcels-and-paper": [
        "singapore-nparks-cites",
        "uk-cites",
        "australia-cites",
        "canada-cites",
        "nz-cites",
        "hongkong-afcd",
        "ec-wildlife-trade",
        "ec-action-plan",
    ],
    "ocean-products-have-routes": [
        "fao-fish-stocks-2025",
        "noaa-coral-bleaching",
        "traffic-sharks-rays",
        "wildaid-sharks",
        "shark-trust",
        "sharks-plane",
        "eia-totoaba",
        "traffic-glass-eel",
    ],
    "organized-crime-is-not-a-movie": [
        "fatf-iwt",
        "fincen-wildlife-threat",
        "fincen-environmental-crimes",
        "wjc-convergence",
        "wjc-corruption",
        "global-initiative-iwt",
        "tnrc-crime-convergence",
        "rusi-illicit-finance",
    ],
    "flagship-products-still-matter": [
        "wjc-rhino",
        "wjc-disruption-disarray",
        "traffic-pangolin",
        "eia-tipping-scales",
        "eia-out-of-africa",
        "save-elephants-etis",
        "south-africa-rhino",
        "nature-trade-impact",
    ],
    "forensics-turns-body-into-evidence": [
        "noaa-ole",
        "usfws-cites",
        "usfws-lacey",
        "usfws-esa",
        "doj-enrd-wildlife",
        "state-wildlife-trafficking",
        "uk-nwcu",
        "eu-twix",
    ],
    "health-and-welfare-are-not-sidebars": [
        "ipbes-invasive",
        "nature-alien-vertebrates",
        "plos-spillover-regulation",
        "nature-food-risky",
        "stoten-glass-eels",
        "marine-policy-eels",
        "cms-migratory",
        "protected-planet-2024",
    ],
    "what-actually-works": [
        "iccwc",
        "iccwc-toolkit",
        "unodc-wildlife-portal",
        "unodc-wwcr-2020",
        "oecd-seasia",
        "world-bank-wildlife-trade",
        "europol-environmental-crime",
        "india-wccb",
    ],
    "original-findings": [
        "unodc-wwcr-2024",
        "iucn-red-list",
        "iucn-summary",
        "ipbes-global",
        "traffic-iwt",
        "eia-wildlife",
        "malaysia-wildlife",
        "kenya-wildlife-service",
    ],
    "cargo-with-a-heartbeat": [
        "singapore-wildlife-trade",
        "wjc-home",
    ],
}


def h(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


SOURCE_BY_ID = {source["id"]: source for source in SOURCES}
SOURCE_INDEX = {source["id"]: idx for idx, source in enumerate(SOURCES, start=1)}


def section_source_ids(section: dict) -> list[str]:
    return RAIL_SOURCE_IDS_BY_SECTION.get(section["id"], section["source_ids"])


def rail_card_count() -> int:
    return sum(len(section_source_ids(section)) for section in SECTIONS)


def replace_refs(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        source_id = match.group(1)
        number = SOURCE_INDEX.get(source_id)
        if not number:
            raise KeyError(f"unknown source id {source_id}")
        return f'<sup class="source-ref"><a href="#source-{h(source_id)}">[{number}]</a></sup>'

    return re.sub(r"\[\[([a-z0-9-]+)\]\]", repl, text)


def source_image(source: dict) -> str:
    for extension in ("jpg", "png", "webp"):
        unique_image = f"{RAIL_IMAGE_DIR}/{source['id']}.{extension}"
        if (ROOT / unique_image).exists():
            return unique_image
    return source.get("image") or IMAGE_BY_CATEGORY.get(source.get("category"), IMAGE_BY_CATEGORY["research"])


def rail_card(source: dict) -> str:
    category = source.get("category", "research")
    image = source_image(source)
    return f"""
<article class="press-static-post press-static-post--source press-static-post--with-real-image press-static-post--clickable wildlife-rail-card" data-source-id="{h(source['id'])}" tabindex="0">
  <div class="press-static-post__top">
    <span class="press-static-post__avatar">{h(''.join(part[:1] for part in source['org'].split()[:2]).upper() or 'S')}</span>
    <div><strong>{h(source['org'])}</strong><span>{h(category.title())}</span></div>
  </div>
  <figure class="press-static-post__media--real">
    <img src="{h(image)}" alt="Editorial source-card visual for {h(source['title'])}" loading="lazy" decoding="async" />
  </figure>
  <div class="press-static-post__visual">
    <span class="press-static-post__kicker">Source</span>
    <strong>{h(source['title'])}</strong>
  </div>
  <p>{h(source['note'])}</p>
  <a href="{h(source['url'])}" target="_blank" rel="noopener noreferrer">Open source</a>
</article>
""".strip()


def gallery_card(source: dict) -> str:
    image = source_image(source)
    return (
        f'<a class="article-rail-gallery__card" href="{h(source["url"])}" '
        f'data-source-id="{h(source["id"])}" target="_blank" rel="noopener noreferrer">'
        f'<img src="{h(image)}" alt="Source-card thumbnail for {h(source["title"])}" '
        'loading="lazy" decoding="async" />'
        '</a>'
    )


def gallery_html() -> str:
    cards = "\n".join(gallery_card(source) for source in SOURCES)
    return f"""
<details class="article-rail-gallery article-rail-gallery--top" id="article-gallery" data-gallery-open-mode="manual">
  <summary>Article Gallery</summary>
  <div class="article-rail-gallery__grid">
{cards}
  </div>
</details>
""".strip()


def section_html(section: dict, idx: int) -> str:
    ids = section_source_ids(section)
    sources = [SOURCE_BY_ID[source_id] for source_id in ids]
    midpoint = (len(sources) + 1) // 2
    left_cards = "\n".join(rail_card(source) for source in sources[:midpoint])
    right_cards = "\n".join(rail_card(source) for source in sources[midpoint:])
    paragraphs = "\n".join(f"    <p>{replace_refs(text)}</p>" for text in section["paragraphs"])
    illustration = ""
    if idx == 3:
        illustration = """
    <figure class="wildlife-inline-visual">
      <img src="assets/wildlife-for-sale/flat-supply-chain.png" alt="Flat editorial illustration of the wildlife trafficking supply chain" loading="lazy" decoding="async" />
      <figcaption>Trade-chain illustration: capture, consolidation, paperwork, transport and buyer demand.</figcaption>
    </figure>
    <aside class="wildlife-terms-box" aria-label="Plain English terms">
      <h3>Terms, without the fog</h3>
      <p><strong>CITES</strong> is the global treaty that controls international trade in listed wild animals and plants. It does not ban all wildlife trade; it sets permit rules and restrictions for species that countries have agreed need protection.</p>
      <p><strong>Appendix I, II and III</strong> are CITES categories. Appendix I is usually the strictest for species threatened with extinction. Appendix II controls trade before a species is pushed there. Appendix III is a request from one country for help enforcing its own protection.</p>
      <p><strong>Laundering</strong> means making illegal wildlife look legal, often through false captive-bred claims, misleading labels, forged paperwork or mixing illegal specimens into legal shipments.</p>
      <p><strong>Seizure data</strong> means records of animals or products authorities caught. It is powerful evidence, but it is not a full count of everything trafficked. A seizure measures detection as well as crime.</p>
      <p><strong>Zoonotic spillover</strong> means a pathogen moving from animals into people. Wildlife trade is not the only spillover pathway, but stressed live animals, mixed species and weak hygiene can raise risk.</p>
      <p><strong>UNODC</strong> is the United Nations Office on Drugs and Crime. <strong>FATF</strong> is the Financial Action Task Force, a global money-laundering watchdog. <strong>FinCEN</strong> is the U.S. Treasury bureau that studies suspicious financial activity.</p>
      <p><strong>IUCN</strong> is the International Union for Conservation of Nature, best known for the Red List of threatened species. <strong>IPBES</strong> is the science-policy body that assesses biodiversity and ecosystem change. <strong>ICCWC</strong> is the International Consortium on Combating Wildlife Crime.</p>
    </aside>
""".rstrip()
    if idx == 11:
        illustration = """
    <figure class="wildlife-inline-visual">
      <img src="assets/wildlife-for-sale/flat-enforcement-map.png" alt="Flat editorial illustration of enforcement choke points across the wildlife trade" loading="lazy" decoding="async" />
      <figcaption>Enforcement-map illustration: checkpoints, labs, rescue centers, courts and community protection.</figcaption>
    </figure>
""".rstrip()
    return f"""
<div class="press-social-row press-social-row--{idx}" data-section="{h(section['id'])}">
  <aside aria-label="Left-side source cards for {h(section['title'])}" class="press-social-side press-social-side--left">
{left_cards}
  </aside>
  <section aria-labelledby="{h(section['id'])}" class="press-social-content press-feature-segment">
    <h2 id="{h(section['id'])}">{h(section['title'])}</h2>
{paragraphs}
{illustration}
  </section>
  <aside aria-label="Right-side source cards for {h(section['title'])}" class="press-social-side press-social-side--right">
{right_cards}
  </aside>
</div>
""".strip()


def source_notes_html() -> str:
    rows = "\n".join(
        f'      <li id="source-{h(source["id"])}"><strong>{h(source["org"])}</strong>, '
        f'<a href="{h(source["url"])}" target="_blank" rel="noopener noreferrer">{h(source["title"])}</a>. '
        f'{h(source["note"])}</li>'
        for source in SOURCES
    )
    return f"""
<section aria-labelledby="source-notes" class="press-social-sources press-feature-sources">
  <h2 id="source-notes">Source notes</h2>
  <p>This story draws on {len(SOURCES)} public sources: international enforcement releases, treaty records, government guidance, NGO investigations, financial-crime advisories, commodity reports and peer-reviewed studies. Source cards above are editorial visuals; the links below are the evidence trail.</p>
  <ol class="source-list atla-source-list">
{rows}
  </ol>
</section>
""".strip()


def body_html() -> str:
    sections = "\n".join(section_html(section, idx) for idx, section in enumerate(SECTIONS, start=1))
    return f"""
<section class="article-body press-feature-body wildlife-for-sale-feature">
  <div class="atla-editor-note">
    <strong>Reader note:</strong> The rail cards are clickable source cards with editorial images. The images are not presented as documentary evidence of the linked source. The sourcing separates seizure records, treaty systems, legal trade data, scientific studies, financial-crime guidance and conservation reporting.
  </div>
  <div class="article-jump-strip"><a href="#article-gallery">Article Gallery</a><a href="#source-notes">{len(SOURCES)} Source Notes</a><a href="#original-findings">Original Findings</a></div>
  <div class="press-social-feature press-feature-social-feature wildlife-for-sale-social-feature" data-social-card-count="{rail_card_count()}" data-source-count="{len(SOURCES)}" data-source-label="Wildlife trafficking source stack">
{gallery_html()}
{sections}
{source_notes_html()}
  </div>
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
</section>
""".strip()


def aside_html() -> str:
    return f"""
<section class="aside-card">
  <h3>Key points</h3>
  <ul><li>Wildlife trafficking is a supply-chain crime: capture, consolidation, documents, transport, finance, online marketing and demand.</li>
<li>The story is bigger than ivory and rhino horn. Reptiles, birds, eels, sharks, corals, primates, turtles, insects and other small or obscure animals move through the trade too.</li>
<li>CITES trade data is essential, but it does not capture illegal trade, domestic markets, unlisted species or laundering through false paperwork.</li>
<li>Online platforms and encrypted chats have changed the buyer's front door, while financial records and forensic tools can expose the back end.</li>
<li>The article is built from {len(SOURCES)} public sources and original analysis of recurring patterns across enforcement, science, policy and market evidence.</li></ul>
</section>
<section class="aside-card">
  <h3>On this page</h3>
  <ol><li><a href="#article-gallery">Article Gallery</a></li>{''.join(f'<li><a href="#{h(section["id"])}">{h(section["title"])}</a></li>' for section in SECTIONS)}<li><a href="#source-notes">Source notes</a></li></ol>
</section>
<section class="aside-card">
  <h3>How this story was built</h3>
  <p>Built from enforcement releases, CITES records, UNODC reporting, financial-crime guidance, national wildlife agencies, TRAFFIC, WWF, IFAW, Wildlife Justice Commission, EIA, scientific literature and The Press source-stack analysis.</p>
</section>
<section class="aside-card">
  <h3>Story file</h3>
  <p><strong>Section:</strong> Science</p>
  <p><strong>Type:</strong> Investigation</p>
  <p><strong>Sources:</strong> {len(SOURCES)}</p>
  <p><strong>Visuals:</strong> Photorealistic editorial rail images plus flat editorial explainers.</p>
</section>
""".strip()


def plain_word_count(markup: str) -> int:
    text = re.sub(r"<script[\s\S]*?</script>", " ", markup)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return len(re.findall(r"[A-Za-z0-9]+(?:['-][A-Za-z0-9]+)?", text))


def metadata(word_count: int) -> dict:
    return {
        "slug": SLUG,
        "filename": FILENAME,
        "title": TITLE,
        "section": "Science",
        "sectionSlug": "science",
        "type": "Investigation",
        "author": "Mira Sato",
        "authorSlug": "mira-sato",
        "authorRole": "Science Correspondent",
        "publishedLabel": "May 20, 2026 • 9:00 a.m. EDT",
        "updatedLabel": "May 20, 2026 • 9:00 a.m. EDT",
        "publishedIso": "2026-05-20T09:00:00-04:00",
        "updatedIso": "2026-05-20T09:00:00-04:00",
        "wordCount": f"{word_count:,} words",
        "wordCountNumber": word_count,
        "readTime": f"{max(1, round(word_count / 200))} min read",
        "dek": DEK,
        "image": HERO,
        "heroImage": HERO,
        "heroImageWidth": 1672,
        "heroImageHeight": 941,
        "imageAlt": HERO_ALT,
        "imageCaptionHtml": "",
        "imageCreditPlain": "The Press photorealistic editorial visual",
        "imageAiGenerated": True,
        "imageAiCaption": "",
        "imageCaption": "",
        "keywords": [
            "wildlife trafficking",
            "illegal wildlife trade",
            "CITES",
            "INTERPOL",
            "UNODC",
            "wildlife crime",
            "exotic pets",
            "online wildlife trade",
            "pangolins",
            "shark fins",
            "glass eels",
            "reptile trade",
        ],
        "asideFile": ASIDE_FILE,
        "bodyFile": BODY_FILE,
        "excerpt": "The trade begins with capture and ends with desire. Between them sits a global supply chain that turns living things into cargo, paperwork, listings, products and profit.",
        "related": [
            "science-the-ocean-has-a-fever-and-the-thermometer-is-everywhere.html",
            "world-europes-cocaine-boom-is-hiding-in-plain-sight.html",
            "systems-the-cold-chain-is-the-invisible-machine-that-feeds-the-world.html",
        ],
        "heroEligible": True,
        "imageWidth": 1672,
        "imageHeight": 941,
        "socialRailPattern": {
            "className": "press-feature-body wildlife-for-sale-feature",
            "cardsInBody": rail_card_count(),
            "sourceCount": len(SOURCES),
            "notes": "All rail cards include unique editorial images and real source links. The Article Gallery renders the same image stack as clickable thumbnails. No fake social screenshots or invented public reaction.",
        },
    }


def write(path: str, content: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    print(f"wrote {path}")


def is_old_story_row(row: object) -> bool:
    if not isinstance(row, dict):
        return False
    values = {
        str(row.get("url") or ""),
        str(row.get("filename") or ""),
        str(row.get("story_id") or ""),
        str(row.get("slug") or ""),
    }
    return bool({OLD_FILE, OLD_SLUG} & values)


def remove_old_from_generated_indexes() -> None:
    for rel in ("search-index.json", "content-index.json", "live-index.json"):
        path = ROOT / rel
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        changed = False
        if isinstance(data, list):
            filtered = [row for row in data if not is_old_story_row(row)]
            changed = len(filtered) != len(data)
            data = filtered
        elif isinstance(data, dict) and isinstance(data.get("stories"), list):
            filtered = [row for row in data["stories"] if not is_old_story_row(row)]
            changed = len(filtered) != len(data["stories"])
            data["stories"] = filtered
            data["story_count"] = len(filtered)
        if changed:
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"filtered {rel}")

    path = ROOT / "placements.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        changed = False

        def scrub(value: object) -> object:
            nonlocal changed
            if isinstance(value, list):
                filtered = [
                    scrub(item)
                    for item in value
                    if item != OLD_SLUG and not is_old_story_row(item)
                ]
                if len(filtered) != len(value):
                    changed = True
                return filtered
            if isinstance(value, dict):
                return {key: scrub(child) for key, child in value.items()}
            return value

        data = scrub(data)
        if changed:
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print("filtered placements.json")


def update_master(entry: dict) -> None:
    path = ROOT / "master-edition.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for key in ("leadOrder", "secondary", "mostRead", "editorsPicks"):
        values = data.setdefault("homepage", {}).get(key)
        if isinstance(values, list):
            data["homepage"][key] = [FILENAME] + [item for item in values if item not in {FILENAME, OLD_FILE}]
    for author in data.get("authors", []):
        if author.get("slug") == entry["authorSlug"]:
            stories = author.setdefault("stories", [])
            author["stories"] = [FILENAME] + [item for item in stories if item not in {FILENAME, OLD_FILE}]
    stories = [
        story for story in data.get("stories", [])
        if story.get("filename") not in {FILENAME, OLD_FILE}
    ]
    stories.insert(0, entry)
    data["stories"] = stories
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("updated master-edition.json")


def cleanup_old_files() -> None:
    for rel in [
        f"content/bodies/{OLD_SLUG}.html",
        f"content/asides/{OLD_SLUG}.html",
        f"metadata/{OLD_SLUG}-master-edition-entry.json",
        OLD_FILE,
    ]:
        path = ROOT / rel
        if path.exists():
            path.unlink()
            print(f"removed {rel}")


def main() -> None:
    for source in SOURCES:
        if source["id"] not in SOURCE_INDEX:
            raise SystemExit(f"bad source id {source['id']}")
    rail_ids = [source_id for section in SECTIONS for source_id in section_source_ids(section)]
    unknown_rail_ids = [source_id for source_id in rail_ids if source_id not in SOURCE_BY_ID]
    if unknown_rail_ids:
        raise SystemExit(f"unknown rail source ids: {unknown_rail_ids}")
    missing_rail_ids = sorted(set(SOURCE_BY_ID) - set(rail_ids))
    duplicate_rail_ids = sorted({source_id for source_id in rail_ids if rail_ids.count(source_id) > 1})
    if missing_rail_ids or duplicate_rail_ids:
        raise SystemExit(
            f"rail source coverage mismatch; missing={missing_rail_ids}, duplicates={duplicate_rail_ids}"
        )
    body = body_html()
    word_count = plain_word_count(body)
    entry = metadata(word_count)
    write(BODY_FILE, body)
    write(ASIDE_FILE, aside_html())
    write(METADATA_FILE, json.dumps(entry, indent=2, ensure_ascii=False) + "\n")
    write(SOURCE_STACK_FILE, json.dumps({"source_count": len(SOURCES), "rail_card_count": rail_card_count(), "sources": SOURCES}, indent=2, ensure_ascii=False) + "\n")
    remove_old_from_generated_indexes()
    update_master(entry)
    cleanup_old_files()
    print(f"done: {word_count} words, {len(SOURCES)} sources, {entry['socialRailPattern']['cardsInBody']} rail cards")


if __name__ == "__main__":
    main()
