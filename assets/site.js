(() => {
  const quoteData = document.querySelector('#homepage-quotes');
  if (quoteData) {
    const quotes = JSON.parse(quoteData.textContent);
    const quote = quotes[Math.floor(Math.random() * quotes.length)];
    document.querySelector('[data-hero-quote]').textContent = `“${quote.text}”`;
    document.querySelector('[data-quote-author]').textContent = quote.author;
    document.querySelector('[data-quote-work]').textContent = quote.work;
    document.querySelector('[data-quote-source]').href = quote.source;
  }

  const cards = [...document.querySelectorAll('[data-ship-card]')];
  const search = document.querySelector('[data-ship-search]');
  const filters = [...document.querySelectorAll('[data-filter]')];
  const count = document.querySelector('#results-count');
  const empty = document.querySelector('[data-empty]');
  let activeLine = 'all';

  function updateCards() {
    if (!cards.length) return;
    const query = search.value.trim().toLocaleLowerCase();
    let visible = 0;
    for (const card of cards) {
      const matches = (activeLine === 'all' || card.dataset.line === activeLine)
        && (card.dataset.name.includes(query) || card.dataset.line.toLocaleLowerCase().includes(query));
      card.hidden = !matches;
      if (matches) visible += 1;
    }
    count.textContent = visible === cards.length && !query && activeLine === 'all'
      ? `Showing all ${visible} ships`
      : `Showing ${visible} ${visible === 1 ? 'ship' : 'ships'}`;
    empty.hidden = visible !== 0;
  }

  for (const filter of filters) {
    filter.addEventListener('click', () => {
      activeLine = filter.dataset.filter;
      for (const option of filters) {
        const selected = option === filter;
        option.classList.toggle('active', selected);
        option.setAttribute('aria-pressed', String(selected));
      }
      updateCards();
    });
  }
  search?.addEventListener('input', updateCards);

  for (const frame of document.querySelectorAll('[data-camera-frame]')) {
    const image = frame.querySelector('[data-camera-image]');
    const fallback = frame.querySelector('.camera-fallback');
    if (!image) continue;
    const unavailable = () => {
      image.classList.add('is-unavailable');
      fallback?.setAttribute('aria-hidden', 'false');
    };
    const available = () => {
      image.classList.remove('is-unavailable');
      fallback?.setAttribute('aria-hidden', 'true');
    };
    image.addEventListener('error', unavailable);
    image.addEventListener('load', available);
    if (image.complete) {
      image.naturalWidth ? available() : unavailable();
    }
  }

  const refresh = document.querySelector('[data-camera-refresh]');
  const detailImage = document.querySelector('.camera-visual-large [data-camera-image]');
  if (refresh && detailImage) {
    const original = detailImage.getAttribute('src');
    refresh.addEventListener('click', () => {
      const next = new URL(original, document.baseURI);
      next.searchParams.set('_sw_refresh', Date.now().toString());
      detailImage.src = next.href;
    });
  }
})();
