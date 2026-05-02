(function () {
  // Wait for Leaflet to load (deferred), and for DOM ready.
  function ready(fn) {
    if (document.readyState !== 'loading') fn();
    else document.addEventListener('DOMContentLoaded', fn);
  }
  function whenLeafletReady(fn) {
    if (typeof L !== 'undefined') return fn();
    const check = setInterval(() => {
      if (typeof L !== 'undefined') {
        clearInterval(check);
        fn();
      }
    }, 50);
  }
  ready(() => whenLeafletReady(initAccidentsMap));

  function initAccidentsMap() {
    const widget = document.getElementById('accidents-widget');
    if (!widget || typeof L === 'undefined') return;
    // Pull ACCIDENTS from global, set by /assets/accidents-data.js (deferred)
    const ACCIDENTS = window.ACCIDENTS || [];
    if (!ACCIDENTS.length) {
      console.warn('Accidents data not yet loaded; widget cannot render.');
      return;
    }
    const mapEl = document.getElementById('accidents-map');
    const listEl = document.getElementById('accidents-list');
    const yearFromEl = document.getElementById('accidents-year-from');
    const yearToEl = document.getElementById('accidents-year-to');
    const yearDisplayEl = document.getElementById('accidents-year-display');

    // ─── Set up map ──────────────────────────────────────────────
    const map = L.map(mapEl, {
      worldCopyJump: true,
      zoomControl: true,
    }).setView([20, 30], 2);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
      attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map);

    // ─── Marker color & size by fatality count (log scale) ──────
    function tierColor(n) {
      if (n === 0) return '#ffffff';
      if (n < 10)   return '#fff7bc';
      if (n < 50)   return '#fec44f';
      if (n < 150)  return '#fb9a29';
      if (n < 300)  return '#cc4c02';
      return '#7f0000';
    }
    function tierRadius(n) {
      // Log-scale radius between 6 and 22 px
      const minN = 1, maxN = 600;
      const v = Math.max(minN, Math.min(maxN, n));
      const t = Math.log(v) / Math.log(maxN);
      return 6 + t * 16;
    }

    // ─── Build markers + list rows ──────────────────────────────
    const lang = () => document.body.getAttribute('data-lang') || 'en';

    const markers = []; // parallel array, same order as ACCIDENTS
    ACCIDENTS.forEach((a, idx) => {
      const fatTotal = a.fatalities.total;
      const m = L.circleMarker([a.lat, a.lon], {
        radius: tierRadius(fatTotal),
        fillColor: tierColor(fatTotal),
        color: '#222',
        weight: 1,
        opacity: 0.9,
        fillOpacity: 0.85,
      });
      m.accidentIdx = idx;
      m.bindPopup(() => buildPopupHtml(a, lang()), { maxWidth: 340, autoPan: true });
      m.on('click', () => highlightListEntry(idx, /*scroll=*/true));
      m.addTo(map);
      markers.push(m);
    });

    // ─── Build list rows ────────────────────────────────────────
    ACCIDENTS.forEach((a, idx) => {
      const li = document.createElement('li');
      li.className = 'accident-entry';
      li.dataset.idx = idx;
      li.innerHTML =
        '<div class="accident-row1">' +
          '<span class="accident-date">' + a.date + '</span>' +
          '<span class="accident-fatalities">' + a.fatalities.total + ' †</span>' +
        '</div>' +
        '<div class="accident-title">' + a.airline + ' ' + a.flight + '</div>' +
        '<div class="accident-meta accident-meta-en"' + (lang() === 'zh' ? ' style="display:none"' : '') + '>' +
          a.aircraft + ' · ' + a.location +
        '</div>';
      // We render a separate ZH meta if helpful, but for now just keep one
      li.addEventListener('click', () => {
        highlightListEntry(idx, /*scroll=*/false);
        const m = markers[idx];
        map.setView([a.lat, a.lon], Math.max(map.getZoom(), 5), { animate: true });
        m.openPopup();
      });
      listEl.appendChild(li);
    });

    let activeIdx = -1;
    function highlightListEntry(idx, scrollTo) {
      if (activeIdx === idx) return;
      if (activeIdx >= 0) {
        const old = listEl.children[activeIdx];
        if (old) old.classList.remove('active');
      }
      activeIdx = idx;
      const cur = listEl.children[idx];
      if (cur) {
        cur.classList.add('active');
        if (scrollTo) {
          const wrap = listEl.parentElement;
          const off = cur.offsetTop - wrap.clientHeight / 3;
          wrap.scrollTo({ top: Math.max(0, off), behavior: 'smooth' });
        }
      }
    }

    // ─── Popup HTML builder (re-runs on lang change via lazy eval) ─
    function buildPopupHtml(a, l) {
      const summary = (l === 'zh') ? a.summary_zh : a.summary_en;
      const labelDate = (l === 'zh') ? '日期' : 'Date';
      const labelFat  = (l === 'zh') ? '罹难' : 'Fatalities';
      const labelOcc  = (l === 'zh') ? '机上' : 'aboard';
      const labelLoc  = (l === 'zh') ? '位置' : 'Location';
      const labelAc   = (l === 'zh') ? '机型' : 'Aircraft';
      let html = '';
      html += '<div class="acc-popup-title">' + a.airline + ' ' + a.flight + '</div>';
      html += '<div class="acc-popup-meta">' + a.date + ' · ' + a.aircraft + ' · ' + a.registration + '</div>';
      html += '<div class="acc-popup-meta">' + a.location + '</div>';
      html += '<div class="acc-popup-meta">' + a.fatalities.total + ' ' + labelFat.toLowerCase() +
              ' / ' + a.fatalities.occupants + ' ' + labelOcc + '</div>';
      html += '<div class="acc-popup-summary">' + summary + '</div>';
      if (a.links && a.links.length) {
        html += '<div class="acc-popup-links">';
        a.links.forEach(link => {
          html += '<a href="' + link.url + '" target="_blank" rel="noopener noreferrer">' + link.label + '</a>';
        });
        html += '</div>';
      }
      return html;
    }

    // ─── Time slider ────────────────────────────────────────────
    function updateYearFilter() {
      let from = parseInt(yearFromEl.value, 10);
      let to = parseInt(yearToEl.value, 10);
      // Keep from <= to
      if (from > to) {
        if (event && event.target === yearFromEl) yearToEl.value = from;
        else yearFromEl.value = to;
        from = parseInt(yearFromEl.value, 10);
        to = parseInt(yearToEl.value, 10);
      }
      yearDisplayEl.textContent = from + '–' + to;
      ACCIDENTS.forEach((a, idx) => {
        const y = parseInt(a.date.substring(0, 4), 10);
        const visible = y >= from && y <= to;
        const m = markers[idx];
        if (visible && !map.hasLayer(m)) m.addTo(map);
        else if (!visible && map.hasLayer(m)) map.removeLayer(m);
        listEl.children[idx].style.display = visible ? '' : 'none';
      });
    }
    yearFromEl.addEventListener('input', updateYearFilter);
    yearToEl.addEventListener('input', updateYearFilter);
    updateYearFilter();

    // ─── Refresh popups + list meta on language change ──────────
    document.addEventListener('flying:langchange', () => {
      // Re-open active popup if any to refresh content
      markers.forEach(m => {
        if (m.isPopupOpen()) {
          m.closePopup();
          m.openPopup();
        }
      });
    });

    // Force Leaflet to recalc map size after the figure becomes laid out
    setTimeout(() => map.invalidateSize(), 200);
  }
})();
