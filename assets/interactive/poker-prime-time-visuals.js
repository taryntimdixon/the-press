(function () {
  function initPokerPrimeTimeVisuals() {
    const feature = document.querySelector('.poker-prime-time-feature');
    if (feature) {
      const scrollToReceipt = (link) => {
        const href = link.getAttribute('href') || '';
        if (!href.startsWith('#source-')) return false;

        const target = document.getElementById(href.slice(1));
        if (!target) return false;

        document.querySelectorAll('.press-source-notes li.is-receipt-target').forEach((item) => {
          item.classList.remove('is-receipt-target');
        });
        target.classList.add('is-receipt-target');

        const url = new URL(window.location.href);
        url.hash = target.id;
        window.history.pushState(null, '', url);
        const previousScrollBehavior = document.documentElement.style.scrollBehavior;
        document.documentElement.style.scrollBehavior = 'auto';
        target.scrollIntoView({ block: 'start' });
        window.requestAnimationFrame(() => {
          document.documentElement.style.scrollBehavior = previousScrollBehavior;
        });
        if (!target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
        target.focus({ preventScroll: true });
        return true;
      };

      feature.addEventListener('click', (event) => {
        if (event.defaultPrevented || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        const target = event.target instanceof Element ? event.target : null;
        if (!target) return;

        const receiptLink = target.closest('.poker-rail-card .press-static-post__source a[href^="#source-"], .poker-static-visuals a[href^="#source-"]');
        if (receiptLink && feature.contains(receiptLink) && scrollToReceipt(receiptLink)) {
          event.preventDefault();
          event.stopPropagation();
          return;
        }

        if (target.closest('button, input, textarea, select, label, [contenteditable="true"]')) return;

        const card = target.closest('.poker-rail-card[data-rail-card]');
        if (!card || !feature.contains(card)) return;

        const firstReceiptLink = card.querySelector('.press-static-post__source a[href^="#source-"]');
        if (firstReceiptLink && scrollToReceipt(firstReceiptLink)) {
          event.preventDefault();
          event.stopPropagation();
        }
      }, true);

      feature.addEventListener('keydown', (event) => {
        if (!['Enter', ' '].includes(event.key)) return;
        const target = event.target instanceof Element ? event.target : null;
        if (!target || target.closest('a, button, input, textarea, select, label, [contenteditable="true"]')) return;

        const card = target.closest('.poker-rail-card[data-rail-card]');
        if (!card || !feature.contains(card)) return;

        const firstReceiptLink = card.querySelector('.press-static-post__source a[href^="#source-"]');
        if (firstReceiptLink && scrollToReceipt(firstReceiptLink)) {
          event.preventDefault();
          event.stopPropagation();
        }
      }, true);

      feature.querySelectorAll('.poker-rail-card[data-rail-card]').forEach((card) => {
        if (card.querySelector('.press-static-post__media')) return;

        const railId = (card.getAttribute('data-rail-card') || '').toLowerCase();
        if (!railId) return;
        const illustrationVersion = 'unique-20260504';

        const heading = card.querySelector('h3');
        const title = heading ? heading.textContent.trim() : `rail card ${railId.toUpperCase()}`;
        const figure = document.createElement('figure');
        figure.className = 'press-static-post__media press-static-post__media--illustration poker-rail-card__media';

        const image = document.createElement('img');
        image.src = `assets/social/illustrations/sports-texas-holdem-prime-time-moment-back-${railId}.svg?v=${illustrationVersion}`;
        image.alt = `Editorial source illustration for ${title}.`;
        image.loading = 'lazy';
        image.decoding = 'async';
        image.onerror = () => {
          figure.remove();
          card.classList.add('press-static-post--text-only');
        };

        const caption = document.createElement('figcaption');
        caption.textContent = 'Local editorial illustration, not a social-media screenshot.';

        figure.append(image, caption);
        card.insertBefore(figure, heading || card.firstChild);
        card.classList.add('press-static-post--with-illustration');
      });
    }

    const setPressedGroup = (buttons, activeButton) => {
      buttons.forEach((button) => {
        const active = button === activeButton;
        button.classList.toggle('is-active', active);
        button.setAttribute('aria-pressed', String(active));
      });
    };

    const timeline = document.querySelector('[data-poker-widget="timeline"]');
    if (timeline) {
      const buttons = timeline.querySelectorAll('[data-step]');
      const panels = timeline.querySelectorAll('[data-panel]');

      const setTimelineStep = (button) => {
        const step = button.getAttribute('data-step');
        buttons.forEach((item) => {
          const active = item === button;
          item.classList.toggle('is-active', active);
          item.setAttribute('aria-selected', String(active));
          item.setAttribute('tabindex', active ? '0' : '-1');
        });
        panels.forEach((panel) => {
          const active = panel.getAttribute('data-panel') === step;
          panel.classList.toggle('is-active', active);
          panel.toggleAttribute('hidden', !active);
        });
      };

      buttons.forEach((button) => {
        button.setAttribute('role', 'tab');
        button.setAttribute('aria-selected', button.classList.contains('is-active') ? 'true' : 'false');
        button.setAttribute('tabindex', button.classList.contains('is-active') ? '0' : '-1');
        button.addEventListener('click', () => {
          setTimelineStep(button);
        });
        button.addEventListener('keydown', (event) => {
          if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
          event.preventDefault();
          const current = Array.prototype.indexOf.call(buttons, button);
          const last = buttons.length - 1;
          const nextIndex = event.key === 'Home'
            ? 0
            : event.key === 'End'
              ? last
              : event.key === 'ArrowRight'
                ? (current + 1) % buttons.length
                : (current - 1 + buttons.length) % buttons.length;
          buttons[nextIndex].focus();
          setTimelineStep(buttons[nextIndex]);
        });
      });
      panels.forEach((panel) => {
        panel.setAttribute('role', 'tabpanel');
        panel.toggleAttribute('hidden', !panel.classList.contains('is-active'));
      });
    }

    const stats = document.querySelector('[data-poker-widget="stats"]');
    if (stats) {
      const notes = {
        '2023': '2023 broke the modern Main Event scale barrier with 10,043 entries and a $12.1 million first prize.',
        '2024': '2024 set the modern high-water mark with 10,112 entries and a $94,041,600 prize pool.',
        '2025': '2025 still delivered a massive field: 9,735 entries and Michael Mizrachi winning $10 million.'
      };
      const note = stats.querySelector('.poker-stat-note');
      stats.querySelectorAll('[data-stat]').forEach((button) => {
        button.setAttribute('aria-pressed', button.classList.contains('is-active') ? 'true' : 'false');
        button.addEventListener('click', () => {
          const key = button.getAttribute('data-stat');
          stats.querySelectorAll('[data-stat]').forEach((b) => {
            const active = b === button;
            b.classList.toggle('is-active', active);
            b.setAttribute('aria-pressed', String(active));
          });
          if (note && notes[key]) note.textContent = notes[key];
        });
      });
    }

    const seatMap = document.querySelector('[data-poker-widget="seat-map"]');
    if (seatMap) {
      const seats = seatMap.querySelectorAll('[data-seat]');
      const detail = seatMap.querySelector('.poker-seat-detail');
      const seatDetails = {
        '1': {
          kicker: 'Seat 1',
          title: 'Chip leader',
          body: 'The stack to beat gets framed as both power and burden. Every fold looks disciplined; every call can look like a coronation or a leak.',
          pressure: 'Protect the lead without freezing',
          hook: 'The camera watches patience turn into dominance'
        },
        '2': {
          kicker: 'Seat 2',
          title: 'Satellite qualifier',
          body: 'The purest Main Event fantasy is an ordinary buy-in path turning into a life-changing final table. ESPN can make this seat feel like the door is still open.',
          pressure: 'Play fearless without punting the miracle',
          hook: 'The audience gets a modern Moneymaker-shaped dream'
        },
        '3': {
          kicker: 'Seat 3',
          title: 'Table pro',
          body: 'The pro gives the table a measuring stick. If the pro is hunting, everyone else becomes prey; if the pro is cornered, the room can feel it.',
          pressure: 'Convert edge while everyone knows you have one',
          hook: 'Commentary can turn solver logic into readable stakes'
        },
        '4': {
          kicker: 'Seat 4',
          title: 'Short stack',
          body: 'The short stack turns every orbit into a countdown. Folds become expensive, shoves become announcements, and survival becomes an episode.',
          pressure: 'Find a hand before the blinds do it for you',
          hook: 'A single double-up can reset the whole table'
        },
        '5': {
          kicker: 'Seat 5',
          title: 'Closer',
          body: 'The closer is dangerous when the table gets tired. That player knows exactly when a final table shifts from survival to taking the title.',
          pressure: 'Sense the moment before it disappears',
          hook: 'The edit can show aggression arriving like weather'
        },
        '6': {
          kicker: 'Seat 6',
          title: 'Wild card',
          body: 'Every broadcast needs somebody who breaks the rhythm. The wild card forces better players into strange decisions and gives the audience something to argue about.',
          pressure: 'Stay unpredictable without becoming reckless',
          hook: 'One strange line can become the clip of the night'
        },
        '7': {
          kicker: 'Seat 7',
          title: 'Online kid',
          body: 'This seat connects the live felt to the regulated online pipeline. The story is speed, study, volume, and whether the screen-born game travels under lights.',
          pressure: 'Translate online confidence into live patience',
          hook: 'The booth can explain modern poker without burying people'
        },
        '8': {
          kicker: 'Seat 8',
          title: 'Veteran',
          body: 'The veteran gives the finale memory. Every decision carries years of almosts, bad beats, and the hard-earned calm that makes pressure visible.',
          pressure: 'Use experience without playing scared',
          hook: 'The broadcast can show how long a Main Event dream can last'
        },
        '9': {
          kicker: 'Seat 9',
          title: 'Rail favorite',
          body: 'The rail favorite gives the room a rooting interest. Every shove has sound around it, and every river card gets a human reaction shot.',
          pressure: 'Feed the energy without letting it steer',
          hook: 'The crowd becomes part of the hand, not just background'
        }
      };

      const renderSeat = (button) => {
        const key = button.getAttribute('data-seat');
        const item = seatDetails[key];
        if (!item || !detail) return;
        setPressedGroup(seats, button);
        detail.innerHTML = `
          <p class="poker-detail-kicker">${item.kicker}</p>
          <h4>${item.title}</h4>
          <p>${item.body}</p>
          <dl>
            <div><dt>Pressure</dt><dd>${item.pressure}</dd></div>
            <div><dt>Broadcast hook</dt><dd>${item.hook}</dd></div>
          </dl>
        `;
      };

      seats.forEach((button) => {
        button.addEventListener('click', () => renderSeat(button));
      });
    }

    const controlRoom = document.querySelector('[data-poker-widget="control-room"]');
    if (controlRoom) {
      const buttons = controlRoom.querySelectorAll('[data-control]');
      const monitor = controlRoom.querySelector('.poker-control-monitor');
      const controlDetails = {
        'hole-cards': {
          status: 'ON AIR',
          title: 'Hole-card reveal',
          body: 'The audience sees the secret, so the same bet stops being random motion and starts reading like intent.'
        },
        'stack-pressure': {
          status: 'STACK CAM',
          title: 'Stack pressure',
          body: 'A 12-big-blind stack makes every orbit feel expensive. The bet size matters because the player may not get another clean chance.'
        },
        'pay-jump': {
          status: 'MONEY LADDER',
          title: 'Pay jump',
          body: 'The next elimination can mean six or seven figures. That changes which calls are brave, which folds are wise, and which bluffs are cruel.'
        },
        rail: {
          status: 'REACTION SHOT',
          title: 'Rail cam',
          body: 'Friends, coaches, and family turn silent math into visible stakes. The hand gets a room, not just a table.'
        },
        integrity: {
          status: 'FLOOR WATCH',
          title: 'Integrity layer',
          body: 'Device and coaching limits matter because the player in the chair has to be the one making the decision.'
        },
        clip: {
          status: 'SOCIAL CUT',
          title: 'Clip afterlife',
          body: 'A great final-table hand needs one sentence people can post with it: the dream survived, the favorite folded, the bluff got through.'
        }
      };

      const renderControl = (button) => {
        const key = button.getAttribute('data-control');
        const item = controlDetails[key];
        if (!item || !monitor) return;
        setPressedGroup(buttons, button);
        monitor.innerHTML = `
          <p class="poker-monitor-status">${item.status}</p>
          <h4>${item.title}</h4>
          <p>${item.body}</p>
        `;
      };

      buttons.forEach((button) => {
        button.addEventListener('click', () => renderControl(button));
      });
    }

    const pressureSim = document.querySelector('[data-poker-widget="pressure-sim"]');
    if (pressureSim) {
      const buttons = pressureSim.querySelectorAll('[data-pressure]');
      const meter = pressureSim.querySelector('.poker-pressure-meter span');
      const score = pressureSim.querySelector('.poker-pressure-score');
      const copy = pressureSim.querySelector('.poker-pressure-copy');
      const labels = {
        low: 'The spot has texture, but the show can move quickly. This is a setup hand unless the river gets weird.',
        medium: 'The decision has enough money, stack, and camera pressure to slow down. The viewer can feel why one click matters.',
        high: 'This is prime-time tension: stack pain, real money, visible faces, and a clock that makes silence loud.'
      };

      const updatePressure = () => {
        const groups = {};
        buttons.forEach((button) => {
          const group = button.getAttribute('data-pressure');
          if (button.classList.contains('is-active')) groups[group] = Number(button.getAttribute('data-value') || 0);
        });
        const value = Math.min(100, Object.values(groups).reduce((sum, item) => sum + item, 0));
        const label = value >= 78 ? labels.high : value >= 55 ? labels.medium : labels.low;
        if (meter) meter.style.width = `${value}%`;
        if (score) score.textContent = String(value);
        if (copy) copy.textContent = label;
      };

      buttons.forEach((button) => {
        button.addEventListener('click', () => {
          const group = button.getAttribute('data-pressure');
          const groupButtons = pressureSim.querySelectorAll(`[data-pressure="${group}"]`);
          setPressedGroup(groupButtons, button);
          updatePressure();
        });
      });
      updatePressure();
    }

    const ecosystemMap = document.querySelector('[data-poker-widget="ecosystem-map"]');
    if (ecosystemMap) {
      const nodes = ecosystemMap.querySelectorAll('[data-node]');
      const detail = ecosystemMap.querySelector('.poker-map-detail');
      const nodeDetails = {
        brand: {
          kicker: 'WSOP brand',
          title: 'New ownership, old prestige',
          body: 'The brand sale makes the ESPN return feel less like nostalgia and more like a growth move: the title still carries history, but the business around it is being reset.',
          links: [['Open sale receipt', '#source-caesars-close-wsop-sale']]
        },
        venue: {
          kicker: 'Las Vegas room',
          title: 'The pilgrimage site',
          body: 'Horseshoe and Paris give the Main Event a physical center: thousands of players moving through one summer room toward one final table.',
          links: [['Open schedule receipt', '#source-wsop-2026-schedule-news']]
        },
        broadcast: {
          kicker: 'ESPN window',
          title: 'Mainstream distribution',
          body: 'ESPN gives the half-curious sports fan a clean path back into poker, especially when the final table has three nights to breathe.',
          links: [['Open ESPN receipt', '#source-espn-pressroom-wsop']]
        },
        field: {
          kicker: '10K-ish field',
          title: 'Mass scale',
          body: 'The recent fields prove the Main Event is not a nostalgia act. The question is whether the audience can become as big as the room again.',
          links: [['2025 field', '#source-espn-2025-mizrachi'], ['2024 field', '#source-caesars-2024-tamayo']]
        },
        online: {
          kicker: 'Online pipeline',
          title: 'More places to dream',
          body: 'Shared liquidity and regulated online rooms matter because playing more hands creates more people who can imagine a WSOP seat.',
          links: [['Pennsylvania receipt', '#source-pa-msiga'], ['Michigan receipt', '#source-michigan-fanduel-multistate']]
        },
        audience: {
          kicker: 'Casual viewer',
          title: 'The half-curious fan',
          body: 'Poker needs the viewer who remembers the boom but has not watched lately. ESPN can turn that viewer from nostalgic into invested.',
          links: [['Moneymaker receipt', '#source-espn-moneymaker-legacy']]
        }
      };

      const renderNode = (button) => {
        const key = button.getAttribute('data-node');
        const item = nodeDetails[key];
        if (!item || !detail) return;
        setPressedGroup(nodes, button);
        const links = item.links.map(([label, href]) => `<a href="${href}">${label}</a>`).join('');
        detail.innerHTML = `
          <p class="poker-detail-kicker">${item.kicker}</p>
          <h4>${item.title}</h4>
          <p>${item.body}</p>
          <div class="poker-source-links">${links}</div>
        `;
      };

      nodes.forEach((button) => {
        button.addEventListener('click', () => renderNode(button));
      });
    }

    const sourceConstellation = document.querySelector('[data-poker-widget="source-constellation"]');
    if (sourceConstellation) {
      const buttons = sourceConstellation.querySelectorAll('[data-source-cluster]');
      const detail = sourceConstellation.querySelector('.poker-source-detail');
      const sourceDetails = {
        broadcast: {
          kicker: 'Broadcast deal',
          title: 'The return is documented from both sides',
          body: 'ESPN and WSOP both frame the agreement around the Main Event’s return, 100-plus hours of coverage, and the August final-table window.',
          links: [['ESPN receipt', '#source-espn-pressroom-wsop'], ['WSOP receipt', '#source-wsop-espn-agreement'], ['PokerNews receipt', '#source-pokernews-espn-return']]
        },
        scale: {
          kicker: 'Field size',
          title: 'The tournament is still enormous',
          body: 'The last three Main Events keep the scale argument honest: 10,043 entries in 2023, 10,112 in 2024, and 9,735 in 2025.',
          links: [['2023 receipt', '#source-caesars-2023-weinman'], ['2024 receipt', '#source-caesars-2024-tamayo'], ['2025 receipt', '#source-espn-2025-mizrachi']]
        },
        integrity: {
          kicker: 'Integrity rules',
          title: 'The decision has to belong to the player',
          body: 'The final table is only compelling if viewers trust that charts, apps, AI tools, and rail coaching are not making the hand for someone else.',
          links: [['Poker.org receipt', '#source-pokerorg-wsop-rule-change'], ['Casino.org receipt', '#source-casino-org-ai-coaching-ban'], ['Review-Journal receipt', '#source-reviewjournal-rule-changes']]
        },
        online: {
          kicker: 'Online pipeline',
          title: 'More liquidity means more dreamers',
          body: 'Pennsylvania and Michigan context shows how the regulated online ecosystem can feed interest back into live poker and the WSOP fantasy.',
          links: [['Pennsylvania receipt', '#source-pa-msiga'], ['Michigan receipt', '#source-michigan-fanduel-multistate'], ['PokerStars receipt', '#source-pokerstars-fanduel-note']]
        },
        history: {
          kicker: 'Boom memory',
          title: 'Television once made poker legible',
          body: 'Moneymaker, the hole-card cam, and the WPT era explain why seeing the secret changed poker from casino footage into a story engine.',
          links: [['Moneymaker receipt', '#source-wsop-moneymaker-profile'], ['ESPN legacy', '#source-espn-moneymaker-legacy'], ['Hole-card cam', '#source-casino-org-hole-card-cam']]
        }
      };

      const renderSource = (button) => {
        const key = button.getAttribute('data-source-cluster');
        const item = sourceDetails[key];
        if (!item || !detail) return;
        setPressedGroup(buttons, button);
        const links = item.links.map(([label, href]) => `<a href="${href}">${label}</a>`).join('');
        detail.innerHTML = `
          <p class="poker-detail-kicker">${item.kicker}</p>
          <h4>${item.title}</h4>
          <p>${item.body}</p>
          <div class="poker-source-links">${links}</div>
        `;
      };

      buttons.forEach((button) => {
        button.addEventListener('click', () => renderSource(button));
      });
    }

    const clipBuilder = document.querySelector('[data-poker-widget="clip-builder"]');
    if (clipBuilder) {
      const buttons = clipBuilder.querySelectorAll('[data-clip]');
      const detail = clipBuilder.querySelector('.poker-clip-detail');
      const clipDetails = {
        setup: {
          kicker: 'Beat 1',
          title: 'Setup',
          body: 'The viewer needs a clean reason to care before the cards matter: chip lead, survival, revenge, a rail, a country, a mortgage, a second chance.'
        },
        decision: {
          kicker: 'Beat 2',
          title: 'Decision',
          body: 'The hand becomes television when the audience understands the price of every option: fold and live, call and risk it, shove and demand an answer.'
        },
        reveal: {
          kicker: 'Beat 3',
          title: 'Reveal',
          body: 'The hole cards, board texture, and commentary let the viewer feel either genius or disaster before the players can see the river.'
        },
        afterlife: {
          kicker: 'Beat 4',
          title: 'Afterlife',
          body: 'The clip travels when the outcome compresses into one emotional sentence: the bluff got through, the hero call failed, the dream survived.'
        }
      };

      const renderClip = (button) => {
        const key = button.getAttribute('data-clip');
        const item = clipDetails[key];
        if (!item || !detail) return;
        setPressedGroup(buttons, button);
        detail.innerHTML = `
          <p class="poker-detail-kicker">${item.kicker}</p>
          <h4>${item.title}</h4>
          <p>${item.body}</p>
        `;
      };

      buttons.forEach((button) => {
        button.addEventListener('click', () => renderClip(button));
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPokerPrimeTimeVisuals);
  } else {
    initPokerPrimeTimeVisuals();
  }
})();
