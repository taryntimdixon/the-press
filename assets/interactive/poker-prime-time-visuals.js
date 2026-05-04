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

        const sourceLink = target.closest('.poker-rail-card .press-static-post__source a[href^="#source-"]');
        if (sourceLink && feature.contains(sourceLink) && scrollToReceipt(sourceLink)) {
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

        const heading = card.querySelector('h3');
        const title = heading ? heading.textContent.trim() : `rail card ${railId.toUpperCase()}`;
        const figure = document.createElement('figure');
        figure.className = 'press-static-post__media press-static-post__media--illustration poker-rail-card__media';

        const image = document.createElement('img');
        image.src = `assets/social/illustrations/sports-texas-holdem-prime-time-moment-back-${railId}.svg`;
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
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPokerPrimeTimeVisuals);
  } else {
    initPokerPrimeTimeVisuals();
  }
})();
