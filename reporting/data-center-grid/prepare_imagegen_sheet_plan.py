#!/usr/bin/env python3
from __future__ import annotations

import json
import hashlib
from pathlib import Path

from prepare_image2_rail_batch import SOURCE_PATH


ROOT = Path(__file__).resolve().parents[2]
PLAN_PATH = ROOT / "reporting" / "data-center-grid" / "imagegen-sheet-plan.json"
SHEET_DIR = ROOT / "assets" / "data-center-grid" / "rail-imagegen-sheets"

CREATIVE_SCENES = {
    "EIA data": (
        "a rain-slick substation reflected in a puddle, with a distant data-center campus glowing beyond the fence",
        "a dense apartment block at night with staggered lit windows under high-voltage lines, shot from street level",
        "a utility service alley behind restaurants where conduit, transformers, and steam vents crowd the frame",
        "a drone-like overlook of a city edge where warehouses, homes, and transmission towers collide at sunset",
        "a macro editorial photo of copper busbars inside an industrial electrical cabinet, lit by inspection lamps",
        "a roadside transformer bank under storm clouds with a bright modern server building visible far behind it",
        "a night utility truck scene where workers' headlamps illuminate underground cable vaults, no logos",
        "a gritty close view of a spinning smart-meter bank with rain beads, neon reflections, and no readable digits",
        "a utility pole corridor cutting between small houses and a warehouse-scale compute campus at blue hour",
        "a control-room wall showing abstract blurred load curves while a silhouetted operator watches the screens",
        "a transformer cooling fan array blasting mist in early morning light near industrial power equipment",
        "a suburban cul-de-sac photographed from low angle with overhead distribution wires leading toward a data center",
        "a frozen winter street where service lines, porch lights, and a distant substation create a tense grid scene",
        "an industrial switchgear room with red warning beacons, thick cables, and cinematic maintenance lighting",
        "a summer heat-wave city block with window AC units, sagging distribution lines, and heat shimmer",
        "a wide shot of freight-rail power infrastructure passing a fenced data-center construction site",
        "a close-up of weathered transformer fins with condensation and orange sodium streetlight reflections",
        "an electrical vault opened in a downtown sidewalk with cable bundles glowing under portable work lights",
        "a neighborhood feeder line running past a school, gas station canopy, and distant substation lights",
        "a night aerial-feeling view of a utility yard where rows of breakers look like a mechanical city",
        "a dramatic storm-afterglow scene with utility poles, wet asphalt, and a far-off warehouse data hall",
        "a compact municipal power plant exterior with stacks, switchyard, and cooling plume at dawn",
        "a highway interchange where transmission towers stride past big-box roofs and a low data-center campus",
        "a close industrial portrait of current transformers and ceramic insulators under crisp inspection light",
    ),
    "Global energy": (
        "a colossal transmission corridor crossing open country at dusk, with red aircraft lights in the haze",
        "a data-center cooling plant beside a high-voltage substation, steam curling through cold morning air",
        "a grid-scale battery yard glowing with small status lights under a bruised sunset sky",
        "a regional grid control room shot from behind operators, with giant blurred maps and no readable text",
        "a natural-gas turbine hall with polished metal, heat shimmer, and workers dwarfed by the machinery",
        "a solar farm and substation framing a warehouse-like data center in harsh midday light",
        "a misty mountain power corridor where transmission lines disappear toward distant industrial buildings",
        "a coastal converter station at twilight with cables, fencing, and a cool ocean haze",
        "an arid desert switchyard near a cluster of data-center buildings, dust hanging in the late sun",
        "a hydroelectric dam control gallery with wet concrete textures and heavy electrical cabinets",
        "a port-side power station with container cranes, substations, and data halls under sodium lights",
        "a snowy northern transmission yard with battery containers and a low, blue industrial sky",
    ),
    "Federal lab": (
        "a national-lab server room where test racks glow behind thick glass and warning lights, no logos",
        "engineers around a high-voltage power-electronics bench, faces obscured by equipment and task lighting",
        "a chip cleanroom corridor with reflective floors, wafer tools, and sterile blue-white light",
        "a thermal test chamber connected to server racks by silver ducts and thick sensor cables",
        "a grid-modeling room with floor-to-ceiling abstract power-flow screens and silhouetted researchers",
        "a macro shot of power modules, liquid-cooled plates, and fiber cables under laboratory spotlights",
        "a chilled-water loop test rig snaking through a lab toward a row of server racks",
        "a research bay with robotic cable arms testing rack power supplies in dramatic side light",
        "a geothermal test site at dawn with pipes, steam, and a small modular data hall nearby",
        "a nuclear microreactor-style test facility exterior at night, fenced and cinematic but not branded",
        "a heat-reuse greenhouse attached to a data-center lab, vapor on glass and server glow behind it",
        "a concrete laboratory bunker with transformer pads and cooling equipment under stormy skies",
        "a close view of immersion-cooled server hardware with rippling fluid and blue inspection light",
        "a rack-scale battery backup room with cables overhead and reflective safety floor markings",
        "a cyber-physical grid simulator lab with miniature substations, cables, and blurred monitors",
        "a wind-tunnel-like airflow lab testing server rack cooling, with smoke visualization beams",
        "a loading dock where experimental cooling skids are being moved into a research data center",
        "a rooftop mechanical yard above a lab data center with fans, pipes, and dawn condensation",
        "a buried-cable test trench beside a research campus, with instruments under work lights",
        "a high-bay lab full of transformers, flexible conduits, and suspended cable trays",
        "a darkened instrument room where oscilloscopes and rack LEDs create an electric night scene",
        "a modular data-center container being instrumented in a lab yard after rain",
        "a laboratory microgrid island with solar canopy, battery containers, and a small data hall",
        "a high-voltage cage around power electronics with amber warning lamps and no readable signs",
        "a cooling-tower test platform with vapor, fans, and a server-building facade in the background",
        "a quiet lab corridor lined with power cabinets, glass reflections, and emergency-red spill light",
        "a researcher silhouette inspecting fiber trunks above dense server racks from a rolling ladder",
    ),
    "Utility scenarios": (
        "a utility planning room transformed into a wall-size grid model, with cables, magnetic tokens, and blurred load maps",
        "a sunset battery yard beside a data-center campus, with one technician silhouetted against container lights",
        "an industrial load-control room where HVAC dampers, meters, and server-rack feeds converge in one frame",
        "a dark data-center operations floor during a grid event, with noncritical aisles dimmed and monitors glowing",
    ),
    "Federal regulation": (
        "a federal hearing room seen from the witness table, microphones silhouetted against a wall of blurred power maps",
        "a marble hallway outside an energy hearing where rolling cases of evidence pass beneath cold overhead light",
    ),
    "Grid operator": (
        "a grid dispatch center at night with operators facing enormous abstract load curves, no readable labels",
        "a rain-wet substation yard with transformers, breakers, and transmission towers glowing at golden hour",
        "a battery-storage control console with colored power-flow graphics reflected in glass, no readable text",
        "a lone night-shift operator silhouetted before a regional grid wall, coffee steam caught in monitor glow",
        "a transmission maintenance staging area with insulated gear, cable reels, and storm clouds rolling in",
        "a data-center interconnection substation after rain, shot low through the fence with reflections on gravel",
        "a close-up of gloved hands on a control-room console, blurred grid screens towering in the background",
        "a sunrise helicopter-view feeling of transmission lines converging on a major switching station",
        "a black-start drill scene in a utility control center with emergency lighting and tense quiet",
        "a wide winter scene of breakers, steel lattice, and a distant data-center campus under pale light",
        "a field engineer opening a relay cabinet while a maze of power lines fills the background",
    ),
    "State record": (
        "a county planning map projected across a dark meeting room while residents' silhouettes watch, no readable text",
        "a Virginia roadside where forest, new grading, and a fenced data-center pad meet under construction lights",
        "a suburban street at dusk with utility poles leading toward warehouse-scale data halls over the hill",
        "a state records archive room where rolled infrastructure maps spill from shelves under dramatic side light",
        "a packed community meeting seen from the back row, faces indistinct, bright projector glow on the wall",
        "a rural substation beside fresh industrial construction with red clay, temporary fencing, and storm light",
    ),
    "Flexibility": (
        "a data-center operations room during a demand-response event, half the aisle lights dimmed while battery screens glow",
        "a battery-storage operator framed by container rows and a tablet of abstract controls, no readable text",
    ),
    "Company record": (
        "a hyperscale data-center loading dock at night where cooling skids and electrical gear arrive under floodlights",
        "a server hall with a technician on a ladder checking overhead cable trays, deep rows receding behind them",
        "a construction site for a data-center power yard where massive transformers hang from a crane at dusk",
        "a facilities plant room where chilled-water pipes, power meters, and valves create a dense industrial maze",
        "a close cinematic view of a cooling manifold beside server infrastructure, condensation and tool marks visible",
    ),
    "Local reporting": (
        "a neighborhood street after a storm where a utility crew works under portable lights near service lines",
        "a tense town-hall hallway outside a data-center vote, residents in silhouette beneath fluorescent light",
        "a driveway view where a quiet house faces a newly cleared transmission corridor in the distance",
        "a local road torn open for conduit trenching beside a data-center construction fence at dawn",
        "a small-town planning table with a 3D terrain model, hard hat, cable samples, and blurred permit maps",
        "a homeowner silhouetted in a kitchen window while data-center construction lights glow on the horizon",
        "a utility crew replacing a residential transformer in heavy rain, sparks of work lights on wet asphalt",
        "a wide suburban edge where backyards end abruptly at a warehouse-scale technology campus wall",
        "a rural crossroads with protest signs turned away from camera, power lines, and distant construction cranes",
        "a muddy construction entrance with tire tracks, temporary power poles, and a low server-building shell",
        "a night scene of dump trucks queuing outside a data-center site while nearby porch lights remain small",
        "a roadside substation expansion seen through chain-link fence with homes just beyond the equipment",
        "a local diner window reflecting transmission towers and construction cranes across the street",
        "a school-bus stop under utility wires near a new industrial power corridor, photographed at sunrise",
        "a county road bordered by buried-conduit markers, orange fencing, and misty tree line",
        "a quiet living-room interior with blue data-center glow visible through the curtains, no papers or bills",
        "a field of temporary generators and cable ramps powering an unfinished data-center shell at blue hour",
    ),
}

CAMERA_STYLES = (
    "low-angle industrial editorial framing",
    "wide environmental documentary framing",
    "compressed telephoto layers of infrastructure",
    "35mm cinematic street-level perspective",
    "over-the-shoulder investigative newsroom perspective",
    "macro industrial detail with shallow depth of field",
    "rain-reflection foreground with deep background scale",
    "symmetrical control-room composition with human figures as silhouettes",
)

LIGHTING_STYLES = (
    "blue-hour sodium-vapor industrial light",
    "storm-cleared sunset with wet reflective surfaces",
    "cold fluorescent interior light with one warm practical glow",
    "night-shift monitor glow and restrained shadows",
    "early-morning mist with crisp power-line silhouettes",
    "hard summer heat haze with realistic contrast",
    "dramatic side light through dust and vapor",
    "overcast documentary daylight with rich texture",
)

COLOR_ACCENTS = (
    "steel gray, wet asphalt, and utility amber",
    "deep blue monitor glow with small red warning lights",
    "concrete, copper, and pale green equipment tones",
    "black cable bundles, galvanized metal, and orange work lights",
    "cool glass reflections with muted civic-interior colors",
    "storm-sky blue, sodium orange, and white work lamps",
)


def source_hash(source: dict) -> int:
    key = f"{source['number']}|{source['category']}|{source['outlet']}|{source['title']}"
    return int(hashlib.sha256(key.encode("utf-8")).hexdigest()[:8], 16)


def pick(items: tuple[str, ...], source: dict, offset: int = 0) -> str:
    return items[(source_hash(source) + source["number"] + offset) % len(items)]


def scene_for(source: dict, category_index: int) -> str:
    scenes = CREATIVE_SCENES.get(source["category"], CREATIVE_SCENES["Federal lab"])
    return scenes[category_index % len(scenes)]


def panel_line(position: str, source: dict, category_index: int) -> str:
    camera = pick(CAMERA_STYLES, source, category_index)
    lighting = pick(LIGHTING_STYLES, source, category_index * 3)
    color = pick(COLOR_ACCENTS, source, category_index * 5)
    return (
        f"{position}: Source {source['number']:03d}, {source['category']}. "
        f"Create {scene_for(source, category_index)}. "
        f"Connect it visually to {source['title']} from {source['outlet']}. "
        f"Use {camera}, {lighting}, and {color}. Do not render readable text."
    )


def sheet_prompt(sheet: dict) -> str:
    sources = sheet["sources"]
    if len(sources) == 4:
        layout = "an exact 2x2 grid of four equal photorealistic photos"
        positions = ("top-left", "top-right", "bottom-left", "bottom-right")
    else:
        layout = "an exact two-panel horizontal diptych of two equal photorealistic photos"
        positions = ("left", "right")
    panels = "\n".join(
        panel_line(position, source, source["category_index"])
        for position, source in zip(positions, sources)
    )
    return (
        "Use case: photorealistic-natural\n"
        "Asset type: contact sheet for cropping into individual side-rail source-card photos\n"
        f"Primary request: Create {layout}. Each panel must look like a separate original cinematic news-magazine photograph: cool, creative, specific, and visually energetic, not a boring desk still life, not an outlet close-up, not an illustration, not a collage, not CGI.\n"
        f"{panels}\n"
        "Style/medium: photorealistic editorial documentary photography with true camera texture, realistic depth of field, real industrial materials, believable human scale, and cinematic but plausible light.\n"
        "Composition/framing: each panel should fill its own equal area edge to edge; keep the subject centered enough that it survives a horizontal 800 by 520 crop.\n"
        "Lighting/mood: investigative, high-energy, atmospheric, and grounded in real utility/data-center infrastructure.\n"
        "Constraints: brand-new original images generated from scratch; no reused article assets; no stock-photo look; no paper bills as the main subject; no generic wall outlets; no logos; no watermarks; no readable words; no readable numbers; no fake document layouts; no visible panel labels; no public figures. "
        "Every panel must be visibly different in setting, camera angle, lighting, and subject."
    )


def main() -> None:
    sources = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    counts: dict[str, int] = {}
    enriched = []
    for source in sources:
        category_index = counts.get(source["category"], 0)
        counts[source["category"]] = category_index + 1
        enriched.append({**source, "category_index": category_index})

    sheets = []
    for index in range(0, len(enriched), 4):
        group = enriched[index : index + 4]
        sheet_number = index // 4 + 1
        layout = "quad" if len(group) == 4 else "diptych"
        sheets.append(
            {
                "sheet": sheet_number,
                "layout": layout,
                "image": str((SHEET_DIR / f"sheet-{sheet_number:03d}.png").relative_to(ROOT)),
                "sources": group,
                "prompt": sheet_prompt({"sources": group}),
            }
        )
    SHEET_DIR.mkdir(parents=True, exist_ok=True)
    PLAN_PATH.write_text(json.dumps(sheets, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(sheets)} sheet prompts to {PLAN_PATH.relative_to(ROOT)}")
    for sheet in sheets:
        numbers = ", ".join(f"{source['number']:03d}" for source in sheet["sources"])
        print(f"sheet-{sheet['sheet']:03d}: {numbers}")


if __name__ == "__main__":
    main()
