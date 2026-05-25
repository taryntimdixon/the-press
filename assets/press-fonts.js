(() => {
  const href = 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Playfair+Display:ital,wght@0,400;0,700;0,800;1,400;1,700&family=Space+Mono:wght@400;700&display=swap';
  if (document.querySelector('[data-press-fonts]')) return;

  [
    ['https://fonts.googleapis.com', ''],
    ['https://fonts.gstatic.com', 'anonymous'],
  ].forEach(([url, crossOrigin]) => {
    if (document.querySelector(`link[rel="preconnect"][href="${url}"]`)) return;
    const link = document.createElement('link');
    link.rel = 'preconnect';
    link.href = url;
    if (crossOrigin) link.crossOrigin = crossOrigin;
    document.head.appendChild(link);
  });

  const stylesheet = document.createElement('link');
  stylesheet.rel = 'stylesheet';
  stylesheet.href = href;
  stylesheet.media = 'print';
  stylesheet.dataset.pressFonts = 'true';
  stylesheet.addEventListener('load', () => {
    stylesheet.media = 'all';
    document.documentElement.classList.add('press-fonts-ready');
  }, { once: true });
  document.head.appendChild(stylesheet);
})();
