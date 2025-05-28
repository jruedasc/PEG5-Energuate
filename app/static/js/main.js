document.addEventListener('DOMContentLoaded', function() {
  const carousel   = document.getElementById('carouselImgs');
  const items      = carousel.querySelectorAll('.carousel-item');
  const indicators = carousel.querySelectorAll('.carousel-indicators button');
  let currentIndex = 0;

  function showSlide(index) {
    items[currentIndex].classList.remove('active');
    indicators[currentIndex].classList.remove('active');
    currentIndex = (index + items.length) % items.length;
    items[currentIndex].classList.add('active');
    indicators[currentIndex].classList.add('active');
  }

  // click en cada punto
  indicators.forEach((dot, idx) => {
    dot.addEventListener('click', () => showSlide(idx));
  });

  // auto-slide cada 5 segundos
  setInterval(() => showSlide(currentIndex + 1), 3000);
});
