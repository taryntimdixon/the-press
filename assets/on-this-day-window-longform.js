(() => {
  const moments = window.PRESS_ON_THIS_DAY_MOMENTS || {};
  const windowKeys = Object.keys(moments).sort();

  if (!windowKeys.length) return;

  const LANE_COPY = {
    tech: {
      label: 'technology',
      room: 'a workspace where machines, investors, users, engineers, and public curiosity started pulling in the same direction',
      stakes: 'it changed how people used tools, information, screens, networks, or systems in daily life',
      consequence: 'The practical result was not only a new object or platform; it was a new rhythm of attention, work, money, and expectation.',
    },
    space: {
      label: 'space exploration',
      room: 'a mission environment where hardware, risk, mathematics, weather, and public imagination had to line up',
      stakes: 'it pushed the boundary between ordinary life on Earth and the dangerous machinery of exploration',
      consequence: 'The lasting meaning sits in the mix of engineering discipline and public wonder: one mission becomes a shared picture of what humans can attempt.',
    },
    rights: {
      label: 'rights and public power',
      room: 'a public institution or street-level confrontation where law, identity, courage, and pressure met in the open',
      stakes: 'it changed who could claim safety, dignity, citizenship, visibility, or equal treatment',
      consequence: 'The consequence was not only legal or symbolic; it changed what people could demand from institutions that had once excluded them.',
    },
    conflict: {
      label: 'war and crisis',
      room: 'a dangerous setting where command decisions, civilians, soldiers, geography, and timing collided',
      stakes: 'it changed the balance of power and left people living with consequences far beyond the day itself',
      consequence: 'Conflict history matters because the line between strategy and human cost is never clean; the map changes, and lives change with it.',
    },
    culture: {
      label: 'culture',
      room: 'a theater, shop, studio, page, screen, or public crowd where an idea moved from private work into mass imagination',
      stakes: 'it altered taste, language, fandom, entertainment, memory, or the way audiences recognized themselves',
      consequence: 'Cultural history can look light from a distance, but it shapes childhood, markets, style, technology, and the stories people carry around for decades.',
    },
    civic: {
      label: 'government and civic power',
      room: 'a formal place where documents, offices, ceremonies, laws, and public legitimacy became the center of the story',
      stakes: 'it changed who held authority and how that authority could be justified, limited, celebrated, or challenged',
      consequence: 'Civic history is built from paper and ceremony, but paper and ceremony can decide land, rights, money, punishment, and the future of whole communities.',
    },
    transport: {
      label: 'transportation',
      room: 'a route, vehicle, station, bridge, port, or horizon where distance started to feel different',
      stakes: 'it changed how bodies, goods, news, armies, families, and ambition moved through the world',
      consequence: 'Transportation history is really about distance losing some of its power: the journey becomes shorter, riskier, more public, or more possible.',
    },
    music: {
      label: 'music and broadcast culture',
      room: 'a performance, studio, stadium, record shop, broadcast booth, or crowd where sound became a public event',
      stakes: 'it changed how audiences gathered, remembered, mourned, celebrated, or imagined themselves through music',
      consequence: 'A music event can become more than a show because songs travel into politics, charity, identity, commerce, and private memory.',
    },
    science: {
      label: 'science',
      room: 'a field site, lab, observatory, instrument room, or announcement where evidence forced people to update the picture of reality',
      stakes: 'it changed what could be measured, proven, feared, predicted, or imagined',
      consequence: 'Science history matters because a result can move from a graph or observation into policy, technology, danger, or wonder.',
    },
    medicine: {
      label: 'medicine and public health',
      room: 'a clinic, lab, hospital, farm, health office, or research institute where bodies and evidence changed the argument',
      stakes: 'it changed how people understood disease, treatment, risk, biology, or care',
      consequence: 'Medical history is personal even when it is institutional: every discovery or warning eventually lands inside families, bodies, and choices.',
    },
    protest: {
      label: 'protest',
      room: 'a street, square, prison, factory gate, school, or public building where ordinary people made power answer back',
      stakes: 'it changed the emotional temperature of politics and showed what pressure from below could do',
      consequence: 'Protest history is about the moment private frustration becomes public force, and public force becomes impossible to ignore.',
    },
    crime: {
      label: 'crime and accountability',
      room: 'a hallway, office, courtroom, evidence table, newsroom, or police setting where a case became bigger than the act itself',
      stakes: 'it changed public trust, institutions, law enforcement, media attention, or constitutional pressure',
      consequence: 'Crime history can become civic history when evidence, secrecy, power, and accountability all enter the same room.',
    },
    chronicle: {
      label: 'history',
      room: 'a recorded setting where documents, eyewitnesses, objects, and later memory keep pulling one date back into view',
      stakes: 'it changed how later generations understood the period around it',
      consequence: 'A calendar entry matters when one date opens into institutions, people, material evidence, and consequences that did not end at midnight.',
    },
  };

  const EVENT_SPECIFICS = {
    '05-25': {
      setting: 'the first 1977 theater lines, a gamble by 20th Century Fox, George Lucas, Industrial Light & Magic, John Williams, and audiences discovering that space fantasy could become the new blockbuster language',
      legacy: 'It made opening weekend energy, visual-effects mythmaking, soundtrack memory, merchandising, sequel culture, and fan identity feel like one connected machine.',
      sources: [
        source('Official Archive', 'StarWars.com search: 1977 release', 'https://www.starwars.com/search?q=Star%20Wars%201977', 'Official franchise articles, interviews, anniversary pieces, and image-led history around the original film.'),
        source('Film Record', 'AFI Catalog search: Star Wars', 'https://catalog.afi.com/Search?searchField=MovieName&searchText=Star%20Wars', 'Film-catalog records and production/release context from the American Film Institute.'),
      ],
    },
    '05-26': {
      setting: 'the beaches and harbor approaches around Dunkirk as Operation Dynamo began moving stranded Allied soldiers toward warships and civilian vessels under air attack',
      legacy: 'Dunkirk became a rescue story, a military retreat, a civilian-mobilization myth, and a turning point in how Britain remembered endurance in 1940.',
      sources: [
        source('War Museum', 'Imperial War Museums: Dunkirk evacuation', 'https://www.iwm.org.uk/history/what-you-need-to-know-about-the-dunkirk-evacuations', 'IWM overview of Operation Dynamo, the evacuation routes, the soldiers, and the civilian vessels.'),
        source('Museum Feature', 'National WWII Museum search: Dunkirk', 'https://www.nationalww2museum.org/search?keys=Dunkirk', 'U.S. museum articles and education material on the campaign and its memory.'),
      ],
    },
    '05-27': {
      setting: 'the pedestrian opening of the Golden Gate Bridge, with San Francisco and Marin joined by a suspension span that turned engineering into civic spectacle',
      legacy: 'The bridge became infrastructure, icon, tourist ritual, migration corridor, labor monument, and proof that a dangerous strait could become a daily crossing.',
      sources: [
        source('Bridge Archive', 'Golden Gate Bridge: History & Research', 'https://www.goldengate.org/bridge/history-research/', 'Official bridge district archive pages, timelines, construction background, and historical materials.'),
        source('Parks Context', 'National Park Service search: Golden Gate Bridge', 'https://www.nps.gov/search/?query=Golden%20Gate%20Bridge', 'Park-service context for the bridge, the strait, and Bay Area public history.'),
      ],
    },
    '05-28': {
      setting: 'the Chagai test range in Balochistan, where Pakistan answered India’s nuclear tests and made nuclear status a public fact',
      legacy: 'The tests hardened South Asian deterrence, changed nonproliferation politics, and made nuclear nationalism visible in landscape, science, and state ceremony.',
      sources: [
        source('Test Ban Context', 'CTBTO search: Chagai-I', 'https://www.ctbto.org/search?search=Chagai-I', 'Nuclear-test-ban context and monitoring background connected to the 1998 tests.'),
        source('Nuclear Profile', 'NTI search: Pakistan nuclear tests', 'https://www.nti.org/search/?q=Pakistan%20nuclear%20tests', 'Nuclear Threat Initiative country and proliferation background.'),
      ],
    },
    '05-29': {
      setting: 'the 1953 Everest expedition at the summit ridge, with Tenzing Norgay and Edmund Hillary climbing inside a world of Sherpa expertise, empire, oxygen equipment, and global news hunger',
      legacy: 'The summit became an endurance myth, but also a story about Himalayan labor, imperial timing, expedition logistics, and who receives credit for exploration.',
      sources: [
        source('Geography Archive', 'Royal Geographical Society search: Everest 1953', 'https://www.rgs.org/search/?query=Everest%201953', 'Collection and expedition-history leads from the Royal Geographical Society.'),
        source('Museum Collection', 'National Geographic search: Everest 1953', 'https://www.nationalgeographic.com/search?q=Everest%201953', 'Magazine, expedition, image, and geography-history coverage.'),
      ],
    },
    '05-30': {
      setting: 'Rouen after Joan of Arc’s politically charged trial, with church authority, English power, French memory, gender, prophecy, and military symbolism colliding',
      legacy: 'Joan’s death became a trial record, a martyrdom story, a national symbol, and a recurring argument about sanctity, politics, youth, and power.',
      sources: [
        source('Reference Biography', 'Britannica: Saint Joan of Arc', 'https://www.britannica.com/biography/Saint-Joan-of-Arc', 'Reference biography and historical context around Joan’s trial, execution, and later memory.'),
        source('Manuscript Search', 'Gallica search: Jeanne d’Arc', 'https://gallica.bnf.fr/services/engine/search/sru?operation=searchRetrieve&query=dc.title%20all%20%22Jeanne%20d%27Arc%22', 'French national-library search lead for manuscripts, books, images, and public memory.'),
      ],
    },
    '05-31': {
      setting: 'Tulsa’s Greenwood District as racial terror, white mobs, law enforcement failure, aerial attack claims, fire, and displacement destroyed Black Wall Street',
      legacy: 'The massacre became a case study in racial violence, economic destruction, suppressed memory, reparations debate, and archival recovery.',
      sources: [
        source('Local History', 'Tulsa Historical Society: 1921 Tulsa Race Massacre', 'https://www.tulsahistory.org/exhibit/1921-tulsa-race-massacre/', 'Local museum exhibit, timeline, photographs, and historical context.'),
        source('National Archive', 'National Archives search: Tulsa Race Massacre', 'https://catalog.archives.gov/search?q=Tulsa%20Race%20Massacre', 'Federal records, photographs, court materials, and public-history leads.'),
      ],
    },
    '06-01': {
      setting: 'a 1980 cable-news studio and control room where Ted Turner’s 24-hour news experiment turned clocks, satellite feeds, anchors, and crisis coverage into routine',
      legacy: 'CNN changed what viewers expected from breaking news and helped make politics, war, disaster, markets, and spectacle feel continuous.',
      sources: [
        source('Network Context', 'CNN: About CNN', 'https://www.cnn.com/about', 'Network background and institutional context for CNN’s global news operation.'),
        source('Reference Context', 'Britannica: CNN', 'https://www.britannica.com/topic/CNN', 'Reference background on CNN, cable news, and the network’s launch context.'),
      ],
    },
    '06-02': {
      setting: 'Surveyor 1 on the lunar surface, proving that a robotic spacecraft could soft-land and send back information needed for Apollo',
      legacy: 'The mission turned the Moon from a distant target into a place engineers could touch with instruments before astronauts arrived.',
      sources: [
        source('Mission Data', 'NASA NSSDC: Surveyor 1', 'https://nssdc.gsfc.nasa.gov/nmc/spacecraft/display.action?id=1966-045A', 'NASA spacecraft record with mission dates, objectives, and technical data.'),
        source('Image Archive', 'NASA Image search: Surveyor 1', 'https://images.nasa.gov/search-results?q=Surveyor%201', 'Mission images, diagrams, and NASA media connected to the lunar landing.'),
      ],
    },
    '06-03': {
      setting: 'Gemini 4 above Earth as Ed White floated outside the capsule with a hand-held maneuvering gun and a tether back to the spacecraft',
      legacy: 'The spacewalk turned orbital flight into a human image: vulnerable, beautiful, risky, and visibly outside the machine.',
      sources: [
        source('Mission Data', 'NASA NSSDC: Gemini 4', 'https://nssdc.gsfc.nasa.gov/nmc/spacecraft/display.action?id=1965-043A', 'NASA mission record with crew, objectives, and orbital details.'),
        source('Image Archive', 'NASA Image search: Ed White EVA', 'https://images.nasa.gov/search-results?q=Ed%20White%20Gemini%204', 'NASA photographs and video stills from the first American spacewalk.'),
      ],
    },
    '06-04': {
      setting: 'Beijing after weeks of student-led demonstrations, hunger strikes, public debate, martial law, armored force, and contested memory',
      legacy: 'Tiananmen became a global symbol of democratic aspiration, state violence, censorship, diaspora memory, and the politics of historical silence.',
      sources: [
        source('Document Archive', 'National Security Archive search: Tiananmen Square 1989', 'https://nsarchive.gwu.edu/search?search_api_fulltext=Tiananmen%20Square%201989', 'Declassified diplomatic records and chronology leads from George Washington University’s archive.'),
        source('Rights Context', 'Amnesty International search: Tiananmen', 'https://www.amnesty.org/en/search/tiananmen/', 'Human-rights reports, remembrance pieces, and ongoing accountability context.'),
      ],
    },
    '06-05': {
      setting: 'a public-health report describing unusual pneumonia in five young gay men in Los Angeles, before HIV/AIDS had its name, scale, or politics fully visible',
      legacy: 'The report became an early official trace of a crisis that transformed medicine, activism, sexuality, stigma, grief, drug approval, and public health.',
      sources: [
        source('Primary Public Health', 'CDC MMWR: Pneumocystis Pneumonia, Los Angeles', 'https://www.cdc.gov/mmwr/preview/mmwrhtml/june_5.htm', 'The June 5, 1981 CDC report that became an early public signal of AIDS.'),
        source('Museum Context', 'NIH/NLM search: AIDS 1981', 'https://www.nlm.nih.gov/search/?query=AIDS%201981', 'National Library of Medicine collection and exhibition leads on HIV/AIDS history.'),
      ],
    },
    '06-06': {
      setting: 'Normandy’s beaches, airborne drop zones, landing craft, naval guns, hedgerows, weather decisions, and multinational planning on D-Day',
      legacy: 'The landings became a decisive operation and a memory machine for liberation, sacrifice, logistics, alliance warfare, and twentieth-century democracy.',
      sources: [
        source('Museum Topic', 'National WWII Museum: D-Day and Normandy Campaign', 'https://www.nationalww2museum.org/war/topics/d-day-and-normandy-campaign', 'Museum overview of the landings, planning, beaches, and campaign.'),
        source('Archive Search', 'Eisenhower Library search: D-Day', 'https://www.eisenhowerlibrary.gov/search?search=D-Day', 'Commander-level documents, photographs, speeches, and campaign records.'),
      ],
    },
    '06-07': {
      setting: 'Pietermaritzburg station, where Gandhi’s removal from a first-class railway compartment became a remembered trigger in his thinking about racial discrimination',
      legacy: 'The incident became part of a larger story about colonial law, Indian South Africans, nonviolent resistance, and Gandhi’s later political formation.',
      sources: [
        source('South African History', 'SA History Online search: Gandhi Pietermaritzburg', 'https://www.sahistory.org.za/search?search_api_fulltext=Gandhi%20Pietermaritzburg', 'South African history leads on the railway incident and Gandhi’s early activism.'),
        source('Reference Biography', 'Britannica: Mahatma Gandhi', 'https://www.britannica.com/biography/Mahatma-Gandhi', 'Reference biography and context for Gandhi’s South African years.'),
      ],
    },
    '06-08': {
      setting: 'the Laki fissure eruption in Iceland, where lava, gases, livestock death, crop failure, haze, and climate effects made geology a social disaster',
      legacy: 'Laki became an environmental-history warning about volcanoes, atmosphere, famine, climate stress, and the global reach of local eruptions.',
      sources: [
        source('Volcano Record', 'Smithsonian Global Volcanism Program search: Laki', 'https://volcano.si.edu/search_eruption.cfm?eruption_search=Laki', 'Volcanology data and eruption-history leads from the Smithsonian.'),
        source('Earth Science', 'USGS search: Laki eruption', 'https://www.usgs.gov/search?keywords=Laki%20eruption', 'Geological and volcanic-hazard background from the U.S. Geological Survey.'),
      ],
    },
    '06-09': {
      setting: 'Rome at the end of Nero’s rule, as flight, military defection, Senate politics, and succession crisis broke the Julio-Claudian line',
      legacy: 'Nero’s death opened the Year of the Four Emperors and became a durable lesson in spectacle, tyranny, legitimacy, and imperial instability.',
      sources: [
        source('Reference Biography', 'Britannica: Nero', 'https://www.britannica.com/biography/Nero-Roman-emperor', 'Reference biography and political context for Nero’s reign and death.'),
        source('Ancient Sources', 'Perseus search: Nero', 'https://www.perseus.tufts.edu/hopper/searchresults?q=Nero', 'Classical texts and translations connected to Nero and Roman imperial memory.'),
      ],
    },
    '06-10': {
      setting: 'the final ceasefire of the Six-Day War, after territorial capture transformed the map around Israel, Egypt, Jordan, Syria, Gaza, the West Bank, Sinai, East Jerusalem, and the Golan Heights',
      legacy: 'The war reshaped diplomacy, occupation, settlement politics, national trauma, military doctrine, and peace-process debates for generations.',
      sources: [
        source('Reference History', 'Britannica: Six-Day War', 'https://www.britannica.com/event/Six-Day-War', 'Reference account of the war, belligerents, territory, and aftermath.'),
        source('Policy Archive', 'Wilson Center search: Six-Day War', 'https://www.wilsoncenter.org/search?search=Six-Day%20War', 'Cold War document and policy-history leads on diplomacy and regional context.'),
      ],
    },
    '06-11': {
      setting: 'the University of Alabama’s registration site, where Vivian Malone and James Hood entered under federal protection after George Wallace’s symbolic blockade',
      legacy: 'The day compressed civil-rights law, presidential power, state resistance, television, and student courage into one visible confrontation.',
      sources: [
        source('Civil Rights Archive', 'JFK Library search: University of Alabama desegregation', 'https://www.jfklibrary.org/search?search=University%20of%20Alabama%20desegregation', 'Presidential records, speeches, images, and federal-response context.'),
        source('State History', 'Encyclopedia of Alabama search: schoolhouse door', 'https://encyclopediaofalabama.org/?s=schoolhouse+door', 'Alabama history context on Wallace, desegregation, and the university.'),
      ],
    },
    '06-12': {
      setting: 'the Supreme Court’s Loving v. Virginia decision, where Richard and Mildred Loving’s marriage case struck down bans on interracial marriage',
      legacy: 'The decision became a constitutional landmark for marriage, equal protection, due process, family privacy, and later civil-rights arguments.',
      sources: [
        source('Court Case', 'Oyez: Loving v. Virginia', 'https://www.oyez.org/cases/1966/395', 'Case summary, oral argument materials, and Supreme Court context.'),
        source('Primary Opinion', 'Justia: Loving v. Virginia', 'https://supreme.justia.com/cases/federal/us/388/1/', 'Full Supreme Court opinion and legal citation.'),
      ],
    },
    '06-13': {
      setting: 'the Supreme Court’s Miranda decision, linking police interrogation rooms, constitutional rights, counsel, silence, and procedural warnings',
      legacy: 'Miranda warnings became one of the most recognizable pieces of constitutional language in American daily life and crime media.',
      sources: [
        source('Court Case', 'Oyez: Miranda v. Arizona', 'https://www.oyez.org/cases/1965/759', 'Case summary, oral argument materials, and Supreme Court context.'),
        source('Primary Opinion', 'Justia: Miranda v. Arizona', 'https://supreme.justia.com/cases/federal/us/384/436/', 'Full Supreme Court opinion and legal citation.'),
      ],
    },
    '06-14': {
      setting: 'Paris under German occupation in June 1940, with military columns, civilian shock, abandoned institutions, and the symbolic fall of a world capital',
      legacy: 'The occupation changed French politics, resistance memory, collaboration debates, daily survival, and the war’s emotional geography.',
      sources: [
        source('Reference Context', 'Britannica search: Paris World War II occupation', 'https://www.britannica.com/search?query=Paris%20World%20War%20II%20occupation', 'Reference leads on France, occupation, and Paris during the war.'),
        source('Museum Search', 'Imperial War Museums search: Paris 1940 occupation', 'https://www.iwm.org.uk/search/global?query=Paris%201940%20occupation', 'Photographs, collection objects, and wartime context.'),
      ],
    },
    '06-15': {
      setting: 'Runnymede in 1215, where royal authority, baronial pressure, church power, parchment, seals, and forced negotiation produced Magna Carta',
      legacy: 'Magna Carta became less important as a peace deal than as a later symbol of due process, limited power, and rights under law.',
      sources: [
        source('Document Archive', 'UK National Archives: Magna Carta', 'https://www.nationalarchives.gov.uk/education/resources/magna-carta/', 'Primary-document context, images, translation work, and historical background.'),
        source('Archive Context', 'UK National Archives search: Magna Carta', 'https://www.nationalarchives.gov.uk/search/?_q=Magna%20Carta', 'Government archive materials, education pages, and document history.'),
      ],
    },
    '06-16': {
      setting: 'Valentina Tereshkova’s Vostok 6 launch, where Soviet space politics, gender symbolism, engineering, and propaganda met in orbit',
      legacy: 'The flight made the first woman in space a global image and exposed both possibility and limits in the gender politics of the space age.',
      sources: [
        source('NASA History', 'NASA: Sally Ride and Valentina Tereshkova', 'https://www.nasa.gov/topics/history/features/ride_anniversary.html', 'NASA history feature connecting Tereshkova, Sally Ride, and women in space.'),
        source('Space Record', 'Britannica: Valentina Tereshkova', 'https://www.britannica.com/biography/Valentina-Tereshkova', 'Reference biography and mission context.'),
      ],
    },
    '06-17': {
      setting: 'the Watergate complex at night, where taped doors, burglary tools, campaign politics, reporters, courts, and congressional investigation converged',
      legacy: 'The break-in became a constitutional crisis about executive power, evidence, press scrutiny, secrecy, and accountability.',
      sources: [
        source('National Archive', 'National Archives: Watergate', 'https://www.archives.gov/research/investigations/watergate', 'Federal records and investigative context around the Watergate scandal.'),
        source('FBI Archive', 'FBI Vault: Watergate', 'https://vault.fbi.gov/watergate', 'FBI documents and files connected to the investigation.'),
      ],
    },
    '06-18': {
      setting: 'Waterloo’s fields, roads, farms, cavalry charges, mud, coalition command, and Napoleon’s final military gamble',
      legacy: 'The battle ended the Napoleonic Wars and became shorthand for defeat, diplomatic reset, and the nineteenth-century balance of power.',
      sources: [
        source('Military Museum', 'National Army Museum: Battle of Waterloo', 'https://www.nam.ac.uk/explore/battle-waterloo', 'Museum overview of the battle, armies, tactics, and consequences.'),
        source('Reference History', 'Britannica: Battle of Waterloo', 'https://www.britannica.com/event/Battle-of-Waterloo', 'Reference account of the battle and Napoleonic aftermath.'),
      ],
    },
    '06-19': {
      setting: 'Galveston in 1865, where General Order No. 3 announced freedom after slavery had already legally ended elsewhere but enforcement lagged',
      legacy: 'Juneteenth became a Black freedom holiday, a memory of delayed emancipation, and a national argument about law, liberation, and public celebration.',
      sources: [
        source('Museum Context', 'NMAAHC: Juneteenth', 'https://nmaahc.si.edu/juneteenth', 'Smithsonian history, public memory, and cultural context around Juneteenth.'),
        source('Archive Context', 'National Archives search: General Order No. 3 Juneteenth', 'https://catalog.archives.gov/search?q=General%20Order%20No.%203%20Juneteenth', 'Federal records and document leads for emancipation in Texas.'),
      ],
    },
    '06-20': {
      setting: 'movie theaters in 1975 as Jaws turned a shark thriller into a summer-release phenomenon with television advertising, suspense, and audience fear',
      legacy: 'The film helped define the modern summer blockbuster, changed beach imagination, and showed how marketing, music, and wide release could work together.',
      sources: [
        source('Film Record', 'AFI Catalog search: Jaws', 'https://catalog.afi.com/Search?searchField=MovieName&searchText=Jaws', 'Film-catalog production, release, and credits context.'),
        source('Film Reference', 'Britannica: Jaws', 'https://www.britannica.com/topic/Jaws-film-by-Spielberg', 'Reference background on Spielberg’s film, release, and cultural impact.'),
      ],
    },
    '06-21': {
      setting: 'the Manchester Baby computer running its first stored program, a tiny machine-room milestone behind modern programmable computing',
      legacy: 'The run proved the stored-program principle in working hardware and helped move computing from special-purpose machines toward general-purpose architecture.',
      sources: [
        source('University Archive', 'University of Manchester search: Baby computer', 'https://www.manchester.ac.uk/discover/news/?s=Baby%20computer', 'University history and anniversary writing about the Manchester Baby.'),
        source('Computer History', 'Computer History Museum search: Manchester Baby', 'https://www.computerhistory.org/search/?q=Manchester%20Baby', 'Computing-history collection and exhibit leads.'),
      ],
    },
    '06-22': {
      setting: 'Operation Barbarossa’s opening, when Nazi Germany invaded the Soviet Union across a huge front and turned the war into an immense eastern catastrophe',
      legacy: 'The invasion reshaped World War II, the Holocaust, Soviet memory, military scale, civilian suffering, and the eventual defeat of Nazi Germany.',
      sources: [
        source('Holocaust Encyclopedia', 'USHMM: Invasion of the Soviet Union, June 1941', 'https://encyclopedia.ushmm.org/content/en/article/invasion-of-the-soviet-union-june-1941', 'Holocaust Museum account of the invasion and its genocidal context.'),
        source('War Museum Search', 'Imperial War Museums search: Operation Barbarossa', 'https://www.iwm.org.uk/search/global?query=Operation%20Barbarossa', 'Collection objects, photographs, and military-history leads.'),
      ],
    },
    '06-23': {
      setting: 'the 2016 Brexit referendum count, where ballots, regional divides, campaign language, sovereignty claims, and economic uncertainty converged overnight',
      legacy: 'Brexit reshaped British party politics, trade, immigration debate, constitutional tension, Northern Ireland questions, and Europe’s political imagination.',
      sources: [
        source('Election Data', 'UK Electoral Commission: EU Referendum results', 'https://www.electoralcommission.org.uk/research-reports-and-data/our-reports-and-data-past-elections-and-referendums/eu-referendum/electorate-and-count-information', 'Official count and electorate data from the referendum.'),
        source('Parliament Context', 'UK Parliament search: Brexit referendum', 'https://www.parliament.uk/search/?q=Brexit%20referendum', 'Parliamentary research, committee, and legislative context.'),
      ],
    },
    '06-24': {
      setting: 'Berlin in 1948 as Soviet blockade pressure turned roads, rails, coal, food, aircraft, and Cold War diplomacy into one logistical emergency',
      legacy: 'The blockade and airlift became a foundational Cold War story about divided Berlin, allied resolve, supply chains, and urban survival.',
      sources: [
        source('Presidential Library', 'Truman Library: Berlin Airlift inquiry', 'https://www.trumanlibrary.gov/education/presidential-inquiries/berlin-airlift', 'Documents and teaching materials on the blockade and airlift.'),
        source('Military Museum', 'National Museum of the USAF search: Berlin Airlift', 'https://www.nationalmuseum.af.mil/Search/?Search=Berlin%20Airlift', 'Aircraft, logistics, and airlift-history collection leads.'),
      ],
    },
    '06-25': {
      setting: 'the global news shock after Michael Jackson’s death, with Los Angeles, television, radio, internet traffic, fans, and celebrity medicine under scrutiny',
      legacy: 'His death became a story about pop memory, fame, grief, race, childhood, media saturation, legal accountability, and the afterlife of an entertainment empire.',
      sources: [
        source('Music Biography', 'Britannica: Michael Jackson', 'https://www.britannica.com/biography/Michael-Jackson', 'Reference biography and career context.'),
        source('Awards Archive', 'GRAMMY search: Michael Jackson', 'https://www.grammy.com/search?keys=Michael%20Jackson', 'Awards, recordings, and music-industry context.'),
      ],
    },
    '06-26': {
      setting: 'a 1997 British publishing launch for Harry Potter and the Philosopher’s Stone before the series became a worldwide reading, film, and fandom phenomenon',
      legacy: 'The book changed children’s publishing, midnight-release culture, fantasy fandom, adaptation economics, and the shared language of a generation of readers.',
      sources: [
        source('Publisher Context', 'Bloomsbury: Harry Potter', 'https://www.bloomsbury.com/uk/discover/harry-potter/', 'Publisher history, editions, and series background.'),
        source('Book Reference', 'Britannica: Harry Potter and the Philosopher’s Stone', 'https://www.britannica.com/topic/Harry-Potter-and-the-Philosophers-Stone', 'Reference background on the first book and its publishing impact.'),
      ],
    },
    '06-27': {
      setting: 'early-1970s California electronics and arcade culture as Atari turned coin-operated video games into a new youth and entertainment industry',
      legacy: 'Atari helped define arcade culture, home consoles, startup mythology, interactive entertainment, and the business language of video games.',
      sources: [
        source('Game Museum', 'The Strong search: Atari', 'https://www.museumofplay.org/?s=Atari', 'Museum of Play articles and collection leads on Atari and video-game history.'),
        source('Company/Industry Search', 'Internet Archive search: Atari early video games', 'https://archive.org/search?query=Atari%20early%20video%20games', 'Manuals, ads, magazines, interviews, and early game documents.'),
      ],
    },
    '06-28': {
      setting: 'Greenwich Village outside the Stonewall Inn after a police raid, where queer resistance, street anger, nightlife, and press attention fed a new movement memory',
      legacy: 'Stonewall became a catalytic symbol for LGBTQ liberation, Pride, policing debates, queer public space, and community memory.',
      sources: [
        source('National Monument', 'NPS: Stonewall National Monument', 'https://www.nps.gov/places/stonewall-national-monument.htm', 'National Park Service context for the site and its public memory.'),
        source('Library Feature', 'Library of Congress: Today in History, June 28', 'https://www.loc.gov/item/today-in-history/june-28/', 'Library of Congress date feature and source trail for Stonewall.'),
      ],
    },
    '06-29': {
      setting: 'Apple retail stores in 2007, where lines, glass storefronts, touchscreens, cameras, maps, music, and phone contracts announced pocket computing',
      legacy: 'The iPhone reorganized mobile software, photography, attention, app economies, payments, maps, messaging, and the everyday meaning of a phone.',
      sources: [
        source('Launch Release', 'Apple: iPhone premieres at Apple Retail Stores', 'https://www.apple.com/newsroom/2007/06/28iPhone-Premieres-This-Friday-Night-at-Apple-Retail-Stores/', 'Apple’s launch-night retail release for the first iPhone.'),
        source('Product Reveal', 'Apple: Apple reinvents the phone with iPhone', 'https://www.apple.com/newsroom/2007/01/09Apple-Reinvents-the-Phone-with-iPhone/', 'Original January 2007 iPhone announcement and product framing.'),
      ],
    },
    '06-30': {
      setting: 'Leopoldville/Kinshasa at independence, with Belgian colonial rule ending amid ceremony, speeches, mineral wealth, Cold War pressure, and Congolese self-determination',
      legacy: 'Congolese independence became a hopeful and volatile decolonization landmark shaped by sovereignty, assassination, secession, minerals, and global power.',
      sources: [
        source('Reference History', 'Britannica: Democratic Republic of the Congo', 'https://www.britannica.com/place/Democratic-Republic-of-the-Congo', 'Reference history of colonial rule, independence, and postcolonial politics.'),
        source('Policy Archive', 'Wilson Center search: Congo independence 1960', 'https://www.wilsoncenter.org/search?search=Congo%20independence%201960', 'Cold War and policy-history leads on Congo’s independence crisis.'),
      ],
    },
    '07-01': {
      setting: 'Tokyo electronics retail culture in 1979, where the Sony Walkman made cassette listening private, portable, stylish, and urban',
      legacy: 'The Walkman helped invent personal audio culture before smartphones: headphones, commuting soundtracks, product design, youth identity, and private public space.',
      sources: [
        source('Company History', 'Sony History: Walkman', 'https://www.sony.com/en/SonyInfo/CorporateInfo/History/SonyHistory/2-10.html', 'Sony’s corporate history chapter on the Walkman’s development and launch.'),
        source('Museum Search', 'Smithsonian search: Walkman', 'https://www.si.edu/search?edan_q=Walkman', 'Museum object and design-history leads for portable audio.'),
      ],
    },
    '07-02': {
      setting: 'the Civil Rights Act of 1964 entering law, backed by movement pressure, congressional struggle, presidential signature, and public-accommodation enforcement',
      legacy: 'The law became a landmark against segregation and discrimination, reshaping schools, workplaces, hotels, restaurants, federal power, and civil-rights litigation.',
      sources: [
        source('Milestone Document', 'National Archives: Civil Rights Act', 'https://www.archives.gov/milestone-documents/civil-rights-act', 'Primary-document context and historical background.'),
        source('Presidential Library', 'LBJ Library search: Civil Rights Act 1964', 'https://www.lbjlibrary.org/search?query=Civil%20Rights%20Act%201964', 'Presidential records, photographs, speeches, and signing context.'),
      ],
    },
    '07-03': {
      setting: '1985 movie theaters where Back to the Future mixed teen comedy, time travel, rock-and-roll nostalgia, product design, and high-concept studio storytelling',
      legacy: 'The film became a durable pop-science language for timelines, sequels, DeLorean imagery, 1950s nostalgia, and blockbuster comedy craft.',
      sources: [
        source('Film Record', 'AFI Catalog search: Back to the Future', 'https://catalog.afi.com/Search?searchField=MovieName&searchText=Back%20to%20the%20Future', 'Film-catalog production, release, and credits context.'),
        source('Film Reference', 'Britannica: Back to the Future', 'https://www.britannica.com/topic/Back-to-the-Future', 'Reference background on the film and its pop-cultural afterlife.'),
      ],
    },
    '07-04': {
      setting: 'CERN’s 2012 announcement hall, where ATLAS and CMS data, physicists, detector images, and decades of theory focused on a new particle',
      legacy: 'The Higgs announcement confirmed a central piece of the Standard Model and made particle physics briefly feel like front-page public drama.',
      sources: [
        source('Research Institution', 'CERN: Higgs boson discovery', 'https://home.cern/science/physics/higgs-boson', 'CERN background on the Higgs field, boson, and discovery.'),
        source('Experiment Context', 'ATLAS: Higgs boson discovery', 'https://atlas.cern/Discover/Physics/Higgs', 'ATLAS experiment explanation and visual context for the discovery.'),
      ],
    },
    '07-05': {
      setting: 'the Roslin Institute lambing and laboratory world where Dolly became the first mammal cloned from an adult somatic cell',
      legacy: 'Dolly changed biotechnology debate, cloning ethics, genetics, livestock science, identity questions, and public fear about what laboratories could copy.',
      sources: [
        source('Research Institute', 'Roslin Institute: The life of Dolly', 'https://vet.ed.ac.uk/roslin/about/dolly/facts/the-life-of-dolly', 'Roslin Institute history of Dolly’s birth, science, and later life.'),
        source('Museum Object', 'National Museums Scotland search: Dolly the sheep', 'https://www.nms.ac.uk/search?term=Dolly%20the%20sheep', 'Museum context for Dolly’s preserved remains and public memory.'),
      ],
    },
    '07-06': {
      setting: 'parks, plazas, sidewalks, smartphones, GPS, cameras, and game servers as Pokemon Go made augmented reality feel physically public',
      legacy: 'The launch changed mobile gaming, location data, social play, public space, nostalgia, and how fast a digital craze could spill into streets.',
      sources: [
        source('Official Release', 'Pokemon press release: Pokemon Go available today', 'https://press.pokemon.com/en/GET-UP-AND-GO-POKEMON-GO-AVAILABLE-TODAY-ON-iPHONE-AND-ANDROID-DEVICES', 'Official launch release for the game’s iPhone and Android rollout.'),
        source('Developer Search', 'Niantic blog search: Pokemon Go launch', 'https://nianticlabs.com/news?search=Pokemon%20Go%20launch', 'Developer updates and company context for location-based play.'),
      ],
    },
    '07-07': {
      setting: 'Live Earth’s synchronized 2007 concerts, where climate messaging moved through stadiums, broadcast feeds, celebrities, pop spectacle, and online attention',
      legacy: 'The concerts showed both the promise and limits of celebrity climate awareness: massive reach, uneven politics, and a new media model for advocacy.',
      sources: [
        source('UN Context', 'United Nations search: Live Earth climate concerts', 'https://www.un.org/search?query=Live%20Earth%20concerts%20climate', 'United Nations climate and public-awareness context.'),
        source('Music Reference', 'Britannica search: Live Earth concerts', 'https://www.britannica.com/search?query=Live%20Earth%20concerts', 'Reference leads on the event and participating concerts.'),
      ],
    },
    '07-08': {
      setting: 'Kennedy Space Center as Atlantis launched STS-135, closing the Space Shuttle era with fuel, flame, crowds, cameras, and program memory',
      legacy: 'The final launch turned the shuttle from working spacecraft into historical symbol: reusable ambition, orbital construction, tragedy, and transition.',
      sources: [
        source('Mission Archive', 'NASA: STS-135', 'https://www.nasa.gov/mission/sts-135/', 'NASA mission articles, images, and shuttle-program context.'),
        source('Image Archive', 'NASA Images search: STS-135', 'https://images.nasa.gov/search-results?q=STS-135', 'Launch photos, crew images, and mission media.'),
      ],
    },
    '07-09': {
      setting: 'Japanese arcades in 1981, where Donkey Kong fused platforms, characters, cabinet culture, and Nintendo’s future identity',
      legacy: 'The game helped define character-driven design, platform mechanics, arcade competition, and Nintendo’s road toward home-console dominance.',
      sources: [
        source('Game Museum', 'The Strong: Donkey Kong', 'https://www.museumofplay.org/games/donkey-kong/', 'Museum of Play context on the game’s design and significance.'),
        source('Archive Search', 'Internet Archive search: Donkey Kong 1981 arcade', 'https://archive.org/search?query=Donkey%20Kong%201981%20arcade', 'Manuals, magazines, scans, and early game-culture traces.'),
      ],
    },
    '07-10': {
      setting: 'Telstar 1’s launch and tracking network, with Bell Labs, NASA launch hardware, ground stations, antennas, and live television linking continents',
      legacy: 'Telstar made communications satellites public and visible, turning orbit into a route for television, phone calls, diplomacy, and pop futurism.',
      sources: [
        source('Reference Tech', 'Britannica: Telstar', 'https://www.britannica.com/technology/Telstar-communications-satellite', 'Reference background on Telstar and communications satellites.'),
        source('Engineering History', 'IEEE search: Telstar 1', 'https://ethw.org/w/index.php?search=Telstar+1&title=Special%3ASearch', 'Engineering-history leads on satellite communications and Bell Labs.'),
      ],
    },
    '07-11': {
      setting: 'Skylab’s fiery reentry over the Indian Ocean and Western Australia, where space debris became a media event, legal joke, and public spectacle',
      legacy: 'The fall made orbital decay visible and turned space infrastructure into a story about risk, uncertainty, debris, and public imagination.',
      sources: [
        source('NASA History', 'NASA: Skylab reenters Earth’s atmosphere', 'https://www.nasa.gov/history/45-years-ago-skylab-reenters-earths-atmosphere/', 'NASA anniversary history of Skylab’s reentry and debris path.'),
        source('Image Archive', 'NASA Images search: Skylab reentry', 'https://images.nasa.gov/search-results?q=Skylab%20reentry', 'Images, media, and archive leads connected to Skylab’s return.'),
      ],
    },
    '07-12': {
      setting: 'Paris and Stade de France in 1998, where France’s diverse team, Zidane’s goals, Brazil’s pressure, and national celebration became one broadcast memory',
      legacy: 'The win fused sport, identity, immigration debate, television, national euphoria, and the myth of a “Black-Blanc-Beur” France.',
      sources: [
        source('Tournament Archive', 'FIFA search: France 1998 final', 'https://www.fifa.com/search?q=France%201998%20final', 'FIFA match, tournament, photo, and archive leads.'),
        source('Sports Archive', 'Olympics search: France 1998 World Cup', 'https://olympics.com/en/search?q=France%201998%20World%20Cup', 'Sports-history and athlete context around France’s win.'),
      ],
    },
    '07-13': {
      setting: 'London and Philadelphia stadiums in 1985, where Live Aid turned rock performance, television, famine relief, and celebrity activism into a shared broadcast event',
      legacy: 'Live Aid changed benefit concerts, global television spectacle, charity debate, media-driven activism, and the relationship between pop stars and humanitarian crises.',
      sources: [
        source('Reference Event', 'Britannica: Live Aid', 'https://www.britannica.com/event/Live-Aid', 'Reference context for the concerts, performers, and relief effort.'),
        source('Broadcast Archive', 'BBC search: Live Aid 1985', 'https://www.bbc.co.uk/search?q=Live%20Aid%201985', 'Broadcast-history, interview, and anniversary leads.'),
      ],
    },
    '07-14': {
      setting: 'Paris at the Bastille, where fortress, prison, arms, crowds, royal authority, rumor, and revolutionary violence became a founding symbol',
      legacy: 'The storming became a key image of popular sovereignty, revolutionary myth, state collapse, and French national memory.',
      sources: [
        source('Reference Event', 'Britannica: Storming of the Bastille', 'https://www.britannica.com/event/storming-of-the-Bastille', 'Reference history of the event and French Revolution context.'),
        source('French Archive Search', 'Gallica search: Bastille 1789', 'https://gallica.bnf.fr/services/engine/search/sru?operation=searchRetrieve&query=dc.title%20all%20%22Bastille%201789%22', 'French national-library lead for images, books, and revolutionary memory.'),
      ],
    },
    '07-15': {
      setting: 'Japanese electronics shops in 1983, where Nintendo’s Family Computer moved video games from arcades toward living rooms',
      legacy: 'Famicom helped define home-console design, cartridges, family play, controller language, and Nintendo’s global comeback after the crash in other markets.',
      sources: [
        source('Company History', 'Nintendo history', 'https://www.nintendo.com/en-gb/Hardware/Nintendo-History/Nintendo-History-625945.html', 'Nintendo’s company hardware timeline and historical context.'),
        source('Game Archive', 'Internet Archive search: Famicom 1983', 'https://archive.org/search?query=Famicom%201983', 'Manuals, magazines, advertisements, and early-console media.'),
      ],
    },
    '07-16': {
      setting: 'Apollo 11’s Saturn V lifting from Kennedy Space Center, with astronauts, launch crews, television, spectators, and Cold War urgency in the same frame',
      legacy: 'The launch began the mission that made lunar landing a human event, not only a technical objective.',
      sources: [
        source('Mission Archive', 'NASA: Apollo 11', 'https://www.nasa.gov/mission/apollo-11/', 'NASA mission overview, crew, timeline, and image context.'),
        source('Image Archive', 'NASA Images search: Apollo 11 launch', 'https://images.nasa.gov/search-results?q=Apollo%2011%20launch', 'Launch photographs, video, and mission media.'),
      ],
    },
    '07-17': {
      setting: 'Disneyland’s televised 1955 opening day, where themed environments, family tourism, corporate showmanship, and live broadcast glitches all became part of the myth',
      legacy: 'Disneyland built a template for themed space, brand immersion, television promotion, leisure architecture, and global entertainment tourism.',
      sources: [
        source('Disney Archive', 'D23 search: Disneyland opening day', 'https://d23.com/search/disneyland%20opening%20day/', 'Disney historical notes, images, and opening-day context.'),
        source('Company Search', 'Disney Parks Blog search: Disneyland opening day', 'https://disneyparks.disney.go.com/blog/search/?search=Disneyland%20opening%20day', 'Anniversary stories, images, and theme-park history leads.'),
      ],
    },
    '07-18': {
      setting: 'a 1968 semiconductor startup world of silicon wafers, memory chips, venture capital, engineering notebooks, and Santa Clara Valley ambition',
      legacy: 'Intel became central to microprocessors, personal computers, data centers, manufacturing strategy, and the geopolitical weight of chips.',
      sources: [
        source('Company History', 'Intel: Intel’s founding', 'https://www.intel.com/content/www/us/en/history/virtual-vault/articles/intels-founding.html', 'Intel’s official history of the company’s 1968 founding.'),
        source('Computer History', 'Computer History Museum search: Intel founding', 'https://www.computerhistory.org/search/?q=Intel%20founding', 'Collection and exhibit leads on Intel and semiconductor history.'),
      ],
    },
    '07-19': {
      setting: 'Cassini looking back from Saturn, with Earth reduced to a tiny point inside a planetary portrait and a public invitation to look up',
      legacy: 'The Day the Earth Smiled became a cosmic self-portrait about scale, planetary science, public participation, and emotional astronomy.',
      sources: [
        source('Mission Feature', 'JPL: The Day the Earth Smiled', 'https://www.jpl.nasa.gov/news/the-day-the-earth-smiled-saturn-shines-in-newest-cassini-image/', 'NASA/JPL feature on the Cassini image and public campaign.'),
        source('Image Archive', 'NASA Images search: Day the Earth Smiled', 'https://images.nasa.gov/search-results?q=The%20Day%20the%20Earth%20Smiled', 'Mission images and related visual materials.'),
      ],
    },
    '07-20': {
      setting: 'the Lunar Module Eagle on the Sea of Tranquility, where landing alarms, fuel margins, crew calm, television, and lunar dust became history',
      legacy: 'The landing became a central image of the twentieth century and a permanent reference point for engineering, politics, television, and human ambition.',
      sources: [
        source('Mission Archive', 'NASA: Apollo 11', 'https://www.nasa.gov/mission/apollo-11/', 'NASA mission overview, crew, timeline, and image context.'),
        source('Primary Audio/Video', 'NASA Images search: Apollo 11 Moon landing', 'https://images.nasa.gov/search-results?q=Apollo%2011%20Moon%20landing', 'Landing photographs, audio, video, and mission media.'),
      ],
    },
    '07-21': {
      setting: 'midnight bookstore lines in 2007, where secrecy, spoilers, costumes, global publishing logistics, and childhood attachment converged around the final Harry Potter book',
      legacy: 'The release became a mass reading event and a marker of how publishing could generate global synchronized fandom.',
      sources: [
        source('Publisher Context', 'Bloomsbury: Harry Potter', 'https://www.bloomsbury.com/uk/discover/harry-potter/', 'Publisher history, editions, and series background.'),
        source('Book Reference', 'Britannica: Harry Potter and the Deathly Hallows', 'https://www.britannica.com/topic/Harry-Potter-and-the-Deathly-Hallows', 'Reference background on the final book and series finale.'),
      ],
    },
    '07-22': {
      setting: 'Wiley Post’s airfield arrival after a solo circumnavigation, with Winnie Mae, navigation, fatigue, press cameras, fuel stops, and aviation celebrity',
      legacy: 'The flight made global aviation feel personally survivable and turned endurance, technology, route planning, and public spectacle into one story.',
      sources: [
        source('Aircraft Object', 'Smithsonian NASM search: Wiley Post Winnie Mae', 'https://airandspace.si.edu/search?search=Wiley%20Post%20Winnie%20Mae', 'Aircraft, object, image, and aviation-history leads.'),
        source('Reference Biography', 'Britannica: Wiley Post', 'https://www.britannica.com/biography/Wiley-Post', 'Reference biography and aviation-history context.'),
      ],
    },
    '07-23': {
      setting: 'Telstar’s live transatlantic television link, where satellite orbit, ground stations, broadcast control rooms, presidents, and viewers shared a signal',
      legacy: 'The broadcast made live global television feel possible and connected space infrastructure to ordinary living-room experience.',
      sources: [
        source('Technology Story', 'Wired: Telstar provides first TV link', 'https://www.wired.com/2012/07/july-23-1962-telstar-provides-first-ever-tv-link-between-u-s-europe/', 'Technology-history account of the first live transatlantic television link.'),
        source('Engineering History', 'IEEE search: Telstar television broadcast', 'https://ethw.org/w/index.php?search=Telstar%20television%20broadcast&title=Special%3ASearch', 'Engineering-history leads on satellite communication and television.'),
      ],
    },
    '07-24': {
      setting: 'Apollo 11’s Pacific splashdown, where astronauts, quarantine procedures, Navy divers, helicopters, cameras, and recovery ships completed the lunar mission',
      legacy: 'The return turned triumph into procedure: survival, contamination fears, debriefing, global television, and the beginning of lunar memory.',
      sources: [
        source('Mission Archive', 'NASA: Apollo 11', 'https://www.nasa.gov/mission/apollo-11/', 'NASA mission overview, crew, timeline, and image context.'),
        source('Image Archive', 'NASA Images search: Apollo 11 splashdown', 'https://images.nasa.gov/search-results?q=Apollo%2011%20splashdown', 'Recovery photographs, video, and mission media.'),
      ],
    },
  };

  windowKeys.forEach((key) => {
    if (key === '05-24') return;
    const moment = moments[key];
    if (!moment || moment.article) return;
    applyGeneratedLongform(moment);
  });

  function applyGeneratedLongform(moment) {
    const lane = LANE_COPY[moment.visual] || LANE_COPY.chronicle;
    const specific = EVENT_SPECIFICS[moment.date] || {};
    const originalSummary = Array.isArray(moment.summary) ? moment.summary.filter(Boolean) : [];
    const related = Array.isArray(moment.related) ? moment.related : [];
    const sourceLabel = moment.sourceLabel || `Wikipedia: ${moment.title}`;
    const sourceDescription = moment.sourceDescription || moment.headline || moment.text || '';
    const title = moment.title || 'Historical Moment';
    const year = formatYear(moment.year);
    const date = moment.displayDate || moment.date || '';
    const topic = moment.topic || title;
    const firstSourceTitle = cleanSourceLabel(sourceLabel);

    moment.dek = specific.dek || buildDek(moment, lane);
    moment.text = ensureSentence(moment.text || moment.headline || `${title} happened on ${date}, ${year}`);
    moment.sources = buildSourceLeads(moment, lane, specific);
    moment.facts = buildFactGrid(moment, lane, specific);
    moment.coolFacts = buildCoolFacts(moment, lane);
    moment.article = buildArticle(moment, lane, specific, {
      title,
      topic,
      year,
      date,
      firstSourceTitle,
      sourceDescription,
      originalSummary,
      related,
    });
    moment.summary = moment.article
      .filter((block) => block.type !== 'heading')
      .slice(0, 3)
      .map((block) => block.text);
    moment.wordCount = countWords(moment.article.map((block) => block.text || '').join(' '));
  }

  function buildDek(moment, lane) {
    const opening = firstCompleteSentence(moment.text || moment.headline || moment.title);
    return `${opening} The deeper story is how this ${lane.label} moment changed what people could expect from the world around them.`;
  }

  function buildFactGrid(moment, lane, specific = {}) {
    const facts = [
      { label: 'Date', value: moment.displayDate || moment.date || '' },
      { label: 'Year', value: formatYear(moment.year) },
      { label: 'Lane', value: capitalize(lane.label) },
      { label: 'Main event', value: moment.title || moment.topic || 'Historical event' },
      { label: 'Why it mattered', value: lane.stakes },
      { label: 'Source trail', value: moment.sourceDescription || cleanSourceLabel(moment.sourceLabel || '') || 'Primary background source' },
    ];
    if (specific.setting) facts.splice(4, 0, { label: 'Scene', value: trimWords(specific.setting, 18) });
    return facts;
  }

  function buildCoolFacts(moment, lane) {
    return [
      `${moment.displayDate} places the reader in ${formatYear(moment.year)}, inside a ${lane.label} story with consequences beyond the date itself.`,
      ensureSentence(moment.text || moment.headline || moment.title),
      `The central source trail begins with ${cleanSourceLabel(moment.sourceLabel || 'the main event record')}.`,
      `The big historical pressure point: ${lane.stakes}.`,
      lane.consequence,
    ].map(ensureSentence);
  }

  function buildSourceLeads(moment, lane, specific = {}) {
    const query = encodeURIComponent(`${moment.title || moment.topic || ''} ${formatYear(moment.year)}`.trim());
    const broadQuery = encodeURIComponent(`${moment.topic || moment.title || ''}`.trim());
    const sources = [
      {
        kind: 'Image Archive',
        title: `Wikimedia Commons: ${moment.title}`,
        href: `https://commons.wikimedia.org/w/index.php?search=${query}&title=Special:MediaSearch&type=image`,
        description: 'Image, object, map, and media leads connected to the event or its historical setting.',
      },
      {
        kind: 'Archive Search',
        title: `Internet Archive: ${moment.title}`,
        href: `https://archive.org/search?query=${query}`,
        description: 'Books, broadcast material, public-domain media, and older documentary traces.',
      },
      {
        kind: 'Reference Search',
        title: `Britannica search: ${moment.title}`,
        href: `https://www.britannica.com/search?query=${broadQuery}`,
        description: 'Reference background for the people, institutions, places, and themes around the event.',
      },
    ];

    const institutional = institutionalSource(moment, lane, query);
    if (institutional) sources.splice(1, 0, institutional);

    sources.push({
      kind: 'News/Research Lead',
      title: `The New York Times archive search: ${moment.title}`,
      href: `https://www.nytimes.com/search?query=${query}`,
      description: 'Press archive lead for later coverage, anniversary writing, reviews, and public memory.',
    });

    return dedupeSources([...(specific.sources || []), ...sources]);
  }

  function institutionalSource(moment, lane, query) {
    if (moment.visual === 'space') {
      return {
        kind: 'Space Archive',
        title: `NASA search: ${moment.title}`,
        href: `https://www.nasa.gov/search/?search=${query}`,
        description: 'Mission pages, images, technical background, and space-history context where available.',
      };
    }

    if (moment.visual === 'medicine') {
      return {
        kind: 'Medical Research',
        title: `PubMed search: ${moment.title}`,
        href: `https://pubmed.ncbi.nlm.nih.gov/?term=${query}`,
        description: 'Medical and scientific literature leads connected to the health or biotechnology history.',
      };
    }

    if (moment.visual === 'rights' || moment.visual === 'civic' || moment.visual === 'protest' || moment.visual === 'crime' || moment.visual === 'conflict') {
      return {
        kind: 'Public Records',
        title: `National Archives search: ${moment.title}`,
        href: `https://catalog.archives.gov/search?q=${query}`,
        description: 'Public records, photographs, documents, and government-history leads.',
      };
    }

    if (moment.visual === 'science' && /higgs|cern/i.test(`${moment.title} ${moment.topic}`)) {
      return {
        kind: 'Research Institution',
        title: `CERN search: ${moment.title}`,
        href: `https://home.cern/search?query=${query}`,
        description: 'Institutional background, images, explainers, and research context from CERN.',
      };
    }

    return {
      kind: 'Museum/Collection Search',
      title: `Smithsonian search: ${moment.title}`,
      href: `https://www.si.edu/search?edan_q=${query}`,
      description: 'Museum objects, archival traces, photographs, and public-history collection leads.',
    };
  }

  function buildArticle(moment, lane, specific = {}, context) {
    const eventText = ensureSentence(moment.text || moment.headline || context.title);
    const headline = ensureSentence(/\.\.\./.test(moment.headline || '') ? (moment.text || context.title) : (moment.headline || moment.text || context.title));
    const sourcePhrase = context.sourceDescription
      ? `The main source record describes the subject as ${lowerFirst(ensureSentence(context.sourceDescription))}`
      : `The main source record gives the reader the first stable trail into the event.`;
    const mainRef = 1;
    const archiveRef = 2;
    const institutionRef = 3;
    const referenceRef = 4;
    const pressRef = 6;
    const recordDetails = (context.originalSummary || [])
      .map((item) => trimSentence(item, 44))
      .filter(Boolean)
      .slice(0, 3)
      .join(' ');
    const relatedTrail = (context.related || [])
      .map((item) => item && item.title)
      .filter(Boolean)
      .slice(0, 4)
      .join(', ');

    return [
      { type: 'heading', text: 'Why This Day Still Has A Pulse' },
      {
        text: `${context.date}, ${context.year}, is not just a date label for ${context.title}. It is the point where a larger ${lane.label} story becomes visible enough to study. ${eventText} The useful way to read the event is to slow it down: who had power in the room, what tools or institutions made the moment possible, who had to live with the result, and why later generations kept returning to it. That is what turns a calendar note into history. The event looks simple in one sentence, but the one sentence is only the doorway.`,
        sources: [mainRef],
      },
      {
        text: `${headline} That sentence already contains the spine of the story: a date, a public action, a result, and a claim about importance. What the short version cannot show is the atmosphere around it. The day belonged to people moving through a specific world with the technology, politics, prejudices, hopes, and limits of their time. The point of expanding this entry is to let the reader stand inside that world long enough to understand why the event mattered before it became famous, clean, and easy to summarize.`,
        sources: [mainRef],
      },
      { type: 'heading', text: 'The Scene Behind The Headline' },
      {
        text: `The strongest image for this entry is not a symbol floating in empty space. It is ${specific.setting || lane.room}. That matters because historical change does not happen in abstract nouns. It happens in rooms, streets, laboratories, courts, stadiums, launch pads, offices, shops, ships, fields, and homes. ${context.title} belongs to a real setting full of material clues: documents, machines, voices, clothing, weather, architecture, instruments, crowds, and waiting. Those clues help the event feel less like trivia and more like a situation people had to navigate in real time.`,
        sources: [archiveRef, institutionRef],
      },
      {
        text: `The headline version tells us what happened. The historical version asks what had to be true for it to happen at all. Someone had to build the institution, fund the system, write the law, stage the performance, open the route, command the operation, publish the result, organize the crowd, or make the tool. The event also needed an audience. Sometimes that audience was a government, sometimes a scientific community, sometimes a mass public, sometimes a small group whose memory later became much larger. Either way, the day became durable because it connected action with witness.`,
        sources: [mainRef, referenceRef],
      },
      { type: 'heading', text: 'What Was Really At Stake' },
      {
        text: `The stakes were straightforward but deep: ${lane.stakes}. That is why this moment is larger than the people most closely attached to it. History often remembers a name, a title, or an image, but the pressure underneath is broader. A single event can expose a system that was already changing. It can reveal who had access, who was excluded, who controlled the tools, who controlled the narrative, and who paid the cost. ${context.title} matters because it gives the reader a handle on those pressures without pretending they began or ended on one day.`,
        sources: [mainRef],
      },
      {
        text: `${sourcePhrase} That kind of source description is useful because it anchors the story before interpretation begins. From there, the reader can move outward into archive searches, museum collections, press coverage, and reference histories. No single source should carry the whole event. The richer version lives in the overlap: the main record for the fact pattern, image archives for visual evidence, institutional pages for context, and later coverage for how memory changed. A serious history feature should make that trail visible instead of hiding it behind a polished paragraph.`,
        sources: [mainRef, archiveRef, institutionRef, referenceRef],
      },
      ...(recordDetails ? [
        {
          text: `The event record also gives this page its factual grain: ${recordDetails} ${relatedTrail ? `The related trail points to ${relatedTrail}, which gives the reader names, places, institutions, and neighboring subjects to follow after the main entry.` : ''} Those details matter because they keep the article attached to the actual historical event instead of drifting into a generic lesson. They give the reader a way to ask better questions: what happened first, what happened next, which people or systems were closest to the change, and which pieces of evidence are worth opening in a new tab.`,
          sources: [mainRef, referenceRef],
        },
      ] : []),
      ...(specific.legacy ? [
        { type: 'heading', text: 'The Specific Turn' },
        {
          text: `${specific.legacy} That is the specific turn inside ${context.title}. The event does not matter only because it appears on a timeline; it matters because it rearranged expectations around a particular institution, medium, body of law, machine, movement, audience, or landscape. The reader can follow that turn through the source trail: the official record, the images, the museum or institutional material, and later reporting that shows how the event kept changing after the first headlines passed.`,
          sources: [mainRef, 2, 3, 4],
        },
      ] : []),
      { type: 'heading', text: 'The Human Scale' },
      {
        text: `It is also worth asking what the day felt like to people who were not trying to make history. Some were watching from the edge of the room. Some were hearing the news secondhand. Some had no power over the decision but would still inherit its consequences. The public version of ${context.title} may belong to famous names and institutions, but the human version belongs to everyone touched by the change afterward. That is where history becomes more than chronology: the event enters work, family, fear, excitement, movement, identity, or everyday speech.`,
        sources: [mainRef, archiveRef],
      },
      {
        text: `The human scale also keeps the event honest. A breakthrough can be thrilling and still uneven. A victory can be real and still incomplete. A cultural launch can bring joy while also changing business and attention. A military or political turning point can look decisive on a timeline while remaining painful and contested for people on the ground. Reading ${context.title} carefully means holding those layers together. The date is important because it concentrates them in one visible place, not because it simplifies them.`,
        sources: [mainRef, referenceRef],
      },
      { type: 'heading', text: 'Why People Later Remembered It' },
      {
        text: `The reason ${context.title} survives is not only that it happened. Countless things happen every day and vanish. This event stayed available because it helped explain something larger about its period. It may have marked a breakthrough, a defeat, a public shock, a legal turn, a cultural launch, a scientific proof, a journey, or a crisis. Whatever the form, it gave later people a before-and-after story. Before this, the world looked one way. After this, people had new evidence, a new tool, a new warning, a new symbol, or a new argument about what should happen next.`,
        sources: [mainRef, referenceRef],
      },
      {
        text: `The memory of the event also changes depending on who is doing the remembering. A government may remember ceremony. A community may remember pain or pride. A company may remember invention. A movement may remember courage. Fans may remember the feeling of being present at the beginning. Scholars may remember the structures that made the moment possible. The best entry leaves room for all of that. It does not flatten ${context.title} into a slogan. It lets the reader see the difference between event, evidence, myth, and consequence.`,
        sources: [archiveRef, pressRef],
      },
      { type: 'heading', text: 'The Wider Ripple' },
      {
        text: `${lane.consequence} For ${context.title}, the ripple runs through the fields named in the source trail and through the ordinary habits that followed. Some events change law. Some change markets. Some change screens, songs, sports, medicine, engineering, war, travel, or public space. Some change the stories families tell. The important thing is to connect the big claim to concrete movement: decisions made afterward, institutions forced to respond, audiences formed, technologies adopted, records preserved, and debates that did not go away.`,
        sources: [mainRef, referenceRef],
      },
      {
        text: `Visual evidence is part of that ripple. Photographs, drawings, objects, maps, machines, buildings, uniforms, tickets, papers, and surviving artifacts can reveal what a plain summary misses. They show scale, texture, design, risk, crowd behavior, and the physical world around the event. They also remind the reader that history was not lived as a paragraph. It was lived through surfaces and sounds: metal, paper, cloth, weather, light, architecture, smoke, screens, engines, silence, applause, or confusion. Those details keep the story grounded.`,
        sources: [archiveRef, institutionRef],
      },
      { type: 'heading', text: 'How To Read The Sources' },
      {
        text: `The source trail works best as a starting map. The main record gives the basic event. Commons and museum-style searches help locate images, artifacts, maps, and visual clues. Archive searches can surface older books, broadcasts, newspapers, and public-domain traces. Reference searches help with names, institutions, and chronology. Press archive searches show how later writers, critics, reporters, and anniversary pieces kept the event alive or changed its meaning. Together, they make the story less like a closed summary and more like a research doorway.`,
        sources: [mainRef, archiveRef, institutionRef, referenceRef, pressRef],
      },
      {
        text: `That structure is important because longform history should invite curiosity without pretending to be the last word. ${context.title} is the main event, but the reader can follow the evidence outward: to images, original records, institutional pages, newspapers, oral histories, maps, reviews, court records, scientific explainers, or museum objects. The strongest historical reading usually comes from comparing those traces. One source gives the date; another gives the object; another gives the public reaction; another shows what later memory did to the event.`,
        sources: [mainRef, archiveRef, institutionRef, referenceRef],
      },
      {
        text: `For ${context.title}, the detail work starts with the nouns inside the event itself: ${trimSentence(moment.text || moment.headline || context.title, 32)} Each noun points outward. If the entry names a person, the reader should ask what network, training, opposition, or opportunity surrounded that person. If it names a tool, building, route, law, performance, or mission, the reader should ask who made it, who used it, who paid for it, and who was left outside its benefits. That is how the one-day marker becomes a story about process, cause, and consequence.`,
        sources: [mainRef, archiveRef, referenceRef],
      },
      { type: 'heading', text: 'The Takeaway' },
      {
        text: `The short version of ${context.date} is easy: ${trimSentence(moment.text || moment.headline || context.title, 34)} The fuller version is that this was a day when the world revealed one of its moving parts. People saw a tool, a right, a danger, a performance, a mission, a decision, or a public shock differently afterward. That is why this entry belongs in the daily history calendar. It gives the reader something exact to look at, but it also opens into a bigger question: what changed once people understood that this had happened?`,
        sources: [mainRef],
      },
      {
        text: `The answer is not always neat. Some consequences were immediate, some took years, and some are still argued over. But that is what makes the date worth keeping. ${context.title} is not just a memory marker; it is a pressure point where evidence, emotion, institutions, and public meaning meet. A reader arriving on this date should come away with more than a fact. They should feel why the fact had weight, what kind of world produced it, and where to go next if they want to keep digging.`,
        sources: [mainRef, referenceRef, pressRef],
      },
    ];
  }

  function cleanSourceLabel(value) {
    return String(value || '').replace(/^Wikipedia:\s*/i, '').trim();
  }

  function source(kind, title, href, description) {
    return { kind, title, href, description };
  }

  function dedupeSources(sources) {
    const seen = new Set();
    return sources.filter((item) => {
      const key = String(item.href || item.title || '').trim().toLowerCase();
      if (!key || seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }

  function trimWords(value, maxWords) {
    const text = String(value || '').replace(/\s+/g, ' ').trim();
    const words = text.split(/\s+/).filter(Boolean);
    if (words.length <= maxWords) return words.join(' ');
    return firstCompleteSentence(text);
  }

  function trimSentence(value, maxWords) {
    const text = String(value || '').replace(/\s+/g, ' ').trim();
    const words = text.split(/\s+/).filter(Boolean);
    return ensureSentence(words.length > maxWords ? firstCompleteSentence(text) : text);
  }

  function firstCompleteSentence(value) {
    const text = String(value || '').replace(/\s+/g, ' ').trim().replace(/\.\.\./g, '.');
    if (!text) return '';
    const sentence = text.match(/^.{12,420}?[.!?](?:\s|$)/);
    return ensureSentence(sentence ? sentence[0] : text);
  }

  function ensureSentence(value) {
    const text = String(value || '').replace(/\s+/g, ' ').trim().replace(/\.\.\./g, '.');
    if (!text) return '';
    return /[.!?]$/.test(text) ? text : `${text}.`;
  }

  function formatYear(yearValue) {
    const value = Number(yearValue);
    if (!Number.isFinite(value)) return '';
    return value < 0 ? `${Math.abs(value)} BCE` : String(value);
  }

  function countWords(value) {
    return (String(value || '').match(/[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*/g) || []).length;
  }

  function capitalize(value) {
    const text = String(value || '').trim();
    return text ? `${text.charAt(0).toUpperCase()}${text.slice(1)}` : text;
  }

  function lowerFirst(value) {
    const text = String(value || '').trim();
    return text ? `${text.charAt(0).toLowerCase()}${text.slice(1)}` : text;
  }
})();
