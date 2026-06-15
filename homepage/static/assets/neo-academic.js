(function () {
  'use strict';

  var nav = document.getElementById('neoNav');
  var toggler = document.getElementById('neoNavToggler');
  var collapse = document.getElementById('neoNavCollapse');

  function setNavOpen(open) {
    if (!nav) return;
    nav.classList.toggle('neo-nav--open', open);
    document.body.classList.toggle('neo-nav-open', open);
    if (toggler) {
      toggler.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggler.setAttribute('aria-label', open ? 'Đóng menu' : 'Mở menu');
    }
  }

  function closeNav() {
    setNavOpen(false);
  }

  window.neoNavInit = function () {
    if (nav) {
      var onScroll = function () {
        nav.classList.toggle('neo-nav--scrolled', window.scrollY > 40);
      };
      window.addEventListener('scroll', onScroll, { passive: true });
      onScroll();
    }

    if (toggler) {
      toggler.addEventListener('click', function () {
        setNavOpen(!nav.classList.contains('neo-nav--open'));
      });
    }

    if (collapse) {
      collapse.querySelectorAll('a').forEach(function (link) {
        link.addEventListener('click', closeNav);
      });
    }

    document.addEventListener('click', function (event) {
      if (!nav || !nav.classList.contains('neo-nav--open')) return;
      if (nav.contains(event.target)) return;
      closeNav();
    });

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') closeNav();
    });

    window.addEventListener('resize', function () {
      if (window.innerWidth > 768) closeNav();
    }, { passive: true });
  };

  document.querySelectorAll('.neo-animate').forEach(function (el, i) {
    el.style.animationDelay = (i * 0.08) + 's';
  });

  window.neoNavInit();
})();
