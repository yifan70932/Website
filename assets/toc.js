/* ============================================================
   yifanova.com — table of contents behavior
   ------------------------------------------------------------
   - Highlights the currently-visible section in the TOC.
   - Mobile: handles the expand/collapse toggle.
   ============================================================ */

(function() {
"use strict";

document.addEventListener('DOMContentLoaded', function() {
  const toc = document.querySelector('.toc');
  if (!toc) return;

  // ─── Mobile toggle ───────────────────────────────────────
  const toggle = toc.querySelector('.toc-mobile-toggle');
  if (toggle) {
    toggle.addEventListener('click', function() {
      toc.classList.toggle('expanded');
    });
    // Auto-collapse on link click (mobile only)
    toc.querySelectorAll('.toc-list-wrapper a').forEach(function(a) {
      a.addEventListener('click', function() {
        if (window.matchMedia('(max-width: 1279px)').matches) {
          toc.classList.remove('expanded');
        }
      });
    });
  }

  // ─── Active section highlighting ─────────────────────────
  const links = Array.from(toc.querySelectorAll('a[href^="#sec-"]'));
  if (!links.length) return;
  const sections = links
    .map(function(a) {
      const id = a.getAttribute('href').slice(1);
      const el = document.getElementById(id);
      return el ? { id: id, el: el, link: a } : null;
    })
    .filter(Boolean);

  function setActive(id) {
    links.forEach(function(a) {
      a.classList.toggle(
        'active',
        a.getAttribute('href') === '#' + id
      );
    });
  }

  // Use intersection observer for efficiency. The trick: we observe
  // each h2 with a rootMargin that defines the "active band" — a
  // narrow strip near the top of the viewport. Whichever h2 is most
  // recently inside that band becomes the active section.
  let visible = new Set();
  const observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        visible.add(entry.target.id);
      } else {
        visible.delete(entry.target.id);
      }
    });
    // Pick the first section in document order that is currently visible
    for (let i = 0; i < sections.length; i++) {
      if (visible.has(sections[i].id)) {
        setActive(sections[i].id);
        return;
      }
    }
  }, {
    // The "active band": treat the top quarter of the viewport as the
    // detection zone. A section becomes active when its h2 enters that
    // band from below or stays within it.
    rootMargin: '0px 0px -75% 0px',
    threshold: 0,
  });

  sections.forEach(function(s) { observer.observe(s.el); });

  // Also support hash on initial load (e.g. /chess/#sec-engines)
  const hash = window.location.hash.slice(1);
  if (hash) {
    const match = sections.find(function(s) { return s.id === hash; });
    if (match) setActive(match.id);
  }
});

})();
