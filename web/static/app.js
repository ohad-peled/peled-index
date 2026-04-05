/* ── Peled Index – app.js ── */

(function () {
  'use strict';

  const searchInput    = document.getElementById('search-input');
  const dropdown       = document.getElementById('dropdown');
  const dropdownStatus = document.getElementById('dropdown-status');
  const authorCard     = document.getElementById('author-card');
  const authorInfo     = document.getElementById('author-info');
  const plotsSection   = document.getElementById('plots-section');

  let searchTimer = null;
  let currentAuthorId = null;
  let currentFields   = [];

  /* ── Utility ── */

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  /* ── Dropdown helpers ── */

  function showDropdown() {
    dropdown.classList.add('visible');
  }

  function hideDropdown() {
    dropdown.classList.remove('visible');
  }

  function setDropdownStatus(msg) {
    dropdownStatus.textContent = msg;
    dropdownStatus.style.display = msg ? 'block' : 'none';
  }

  function clearDropdownItems() {
    Array.from(dropdown.children).forEach(function (child) {
      if (child !== dropdownStatus) {
        dropdown.removeChild(child);
      }
    });
  }

  /* ── Scholar scrape UI ── */

  function renderScholarPrompt() {
    clearDropdownItems();
    setDropdownStatus('');

    var wrapper = document.createElement('div');
    wrapper.id = 'scholar-prompt';
    wrapper.style.padding = '0.75rem 1rem';

    wrapper.innerHTML =
      '<div style="color:#94a3b8;font-size:0.85rem;margin-bottom:0.5rem;">' +
        'Author not found. Enter a Google Scholar ID to scrape:' +
      '</div>' +
      '<div style="display:flex;gap:0.5rem;">' +
        '<input id="scholar-id-input" type="text" placeholder="e.g. nFTM_YIAAAAJ"' +
          ' style="flex:1;padding:0.5rem 0.7rem;background:#0f172a;border:1px solid #334155;' +
          'border-radius:6px;color:#ffffff;font-size:0.9rem;outline:none;" />' +
        '<button id="scholar-scrape-btn"' +
          ' style="padding:0.5rem 1rem;background:#0096ff;border:none;border-radius:6px;' +
          'color:#ffffff;font-size:0.85rem;font-weight:600;cursor:pointer;">Go</button>' +
      '</div>' +
      '<div id="scholar-scrape-status" style="margin-top:0.4rem;font-size:0.82rem;color:#94a3b8;"></div>';

    dropdown.appendChild(wrapper);

    var scholarInput = document.getElementById('scholar-id-input');
    var scrapeBtn    = document.getElementById('scholar-scrape-btn');

    scrapeBtn.addEventListener('click', function () {
      var scholarId = scholarInput.value.trim();
      if (!scholarId) return;
      runScholarScrape(scholarId);
    });

    scholarInput.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') {
        var scholarId = scholarInput.value.trim();
        if (!scholarId) return;
        runScholarScrape(scholarId);
      }
    });
  }

  function runScholarScrape(scholarId) {
    var statusEl = document.getElementById('scholar-scrape-status');
    var scrapeBtn = document.getElementById('scholar-scrape-btn');
    var scholarInput = document.getElementById('scholar-id-input');

    statusEl.textContent = 'Scraping Google Scholar… This may take a minute.';
    statusEl.style.color = '#94a3b8';
    scrapeBtn.disabled = true;
    scholarInput.disabled = true;

    fetch('/api/authors/scholar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scholar_id: scholarId }),
    })
      .then(function (res) {
        if (!res.ok) {
          return res.json().then(function (body) {
            throw new Error(body.detail || 'Scrape failed (' + res.status + ')');
          }).catch(function (err) {
            if (err.message) throw err;
            throw new Error('Scrape failed (' + res.status + ')');
          });
        }
        return res.json();
      })
      .then(function (author) {
        selectAuthor(author);
      })
      .catch(function (err) {
        statusEl.textContent = 'Error: ' + err.message;
        statusEl.style.color = '#ff3366';
        scrapeBtn.disabled = false;
        scholarInput.disabled = false;
      });
  }

  /* ── Search ── */

  function onSearchInput() {
    var query = searchInput.value.trim();

    clearTimeout(searchTimer);
    clearDropdownItems();
    hideDropdown();

    if (query.length < 2) {
      return;
    }

    searchTimer = setTimeout(function () {
      runSearch(query);
    }, 250);
  }

  function runSearch(query) {
    setDropdownStatus('Searching…');
    showDropdown();

    fetch('/api/authors/search?query=' + encodeURIComponent(query))
      .then(function (res) {
        if (!res.ok) {
          throw new Error('Search failed (' + res.status + ')');
        }
        return res.json();
      })
      .then(function (authors) {
        clearDropdownItems();

        if (authors.length === 0) {
          renderScholarPrompt();
          return;
        }

        setDropdownStatus('');

        authors.forEach(function (author) {
          var item = document.createElement('div');
          item.className = 'dropdown-item';

          var scoreRounded = (author.author_score || 0).toFixed(2);
          item.innerHTML =
            '<span class="item-score">' + escapeHtml(scoreRounded) + '</span>' +
            '<div class="item-name">' + escapeHtml(author.name) + '</div>' +
            '<div class="item-meta">' +
              escapeHtml(author.institution || '—') +
              ' &nbsp;·&nbsp; ' +
              escapeHtml(author.total_papers || 0) + ' papers' +
            '</div>';

          item.addEventListener('click', function () {
            selectAuthor(author);
          });

          dropdown.appendChild(item);
        });
      })
      .catch(function (err) {
        clearDropdownItems();
        setDropdownStatus('Error: ' + err.message);
      });
  }

  /* ── Author selection ── */

  function selectAuthor(author) {
    hideDropdown();
    searchInput.value = author.name;
    currentAuthorId   = author.author_id;
    currentFields     = author.fields || [];

    renderAuthorCard(author);
    renderPlots(author.author_id, author.fields || []);
  }

  function renderAuthorCard(author) {
    var scoreRounded = (author.author_score || 0).toFixed(2);
    var fieldTags = (author.fields || []).map(function (f) {
      return '<span class="field-tag">' + escapeHtml(f) + '</span>';
    }).join('');

    authorInfo.innerHTML =
      '<h2>' + escapeHtml(author.name) + '</h2>' +
      '<div class="institution">' + escapeHtml(author.institution || '—') + '</div>' +
      '<div class="stats-row">' +
        '<div class="stat-item">' +
          '<span class="stat-label">Author Score</span>' +
          '<span class="stat-value">' + escapeHtml(scoreRounded) + '</span>' +
        '</div>' +
        '<div class="stat-item">' +
          '<span class="stat-label">Total Papers</span>' +
          '<span class="stat-value">' + escapeHtml(author.total_papers || 0) + '</span>' +
        '</div>' +
      '</div>' +
      (fieldTags ? '<div class="fields-list">' + fieldTags + '</div>' : '');

    authorCard.classList.add('visible');
  }

  /* ── Plots ── */

  function renderPlots(authorId, fields) {
    plotsSection.innerHTML = '';

    if (!fields || fields.length === 0) {
      return;
    }

    fields.forEach(function (field) {
      var container = document.createElement('div');
      container.className = 'plot-container';
      container.id = 'plot-' + encodeURIComponent(field);

      container.innerHTML =
        '<div class="plot-meta">' +
          '<span class="plot-field-title">' + escapeHtml(field) + '</span>' +
          '<div class="plot-stats" id="plot-stats-' + encodeURIComponent(field) + '"></div>' +
        '</div>' +
        '<div class="plot-img-wrapper" id="plot-img-' + encodeURIComponent(field) + '">' +
          '<div class="plot-loading">Generating plot…</div>' +
        '</div>';

      plotsSection.appendChild(container);
      fetchPlot(authorId, field);
    });
  }

  function fetchPlot(authorId, field) {
    var imgWrapperId = 'plot-img-' + encodeURIComponent(field);
    var statsId      = 'plot-stats-' + encodeURIComponent(field);

    fetch('/api/authors/' + encodeURIComponent(authorId) + '/plot/' + encodeURIComponent(field))
      .then(function (res) {
        if (!res.ok) {
          return res.json().then(function (body) {
            throw new Error(body.detail || 'Request failed (' + res.status + ')');
          }).catch(function () {
            throw new Error('Request failed (' + res.status + ')');
          });
        }
        return res.json();
      })
      .then(function (data) {
        var imgWrapper = document.getElementById(imgWrapperId);
        var statsEl    = document.getElementById(statsId);

        if (!imgWrapper) return;

        if (statsEl) {
          statsEl.innerHTML =
            '<span class="plot-stat">Percentile: <span>' + escapeHtml(data.percentile) + '</span></span>' +
            '<span class="plot-stat">Group size: <span>' + escapeHtml(data.comparison_group_size) + '</span></span>';
        }

        var img = document.createElement('img');
        img.src = 'data:image/png;base64,' + data.plot_base64;
        img.alt = field + ' score distribution';
        imgWrapper.innerHTML = '';
        imgWrapper.appendChild(img);
      })
      .catch(function (err) {
        var imgWrapper = document.getElementById(imgWrapperId);
        if (imgWrapper) {
          imgWrapper.innerHTML = '<div class="plot-error">' + escapeHtml(err.message) + '</div>';
        }
      });
  }

  /* ── Event listeners ── */

  searchInput.addEventListener('input', onSearchInput);

  document.addEventListener('click', function (e) {
    var searchWrapper = searchInput.parentElement;
    if (!searchWrapper.contains(e.target)) {
      hideDropdown();
    }
  });

  searchInput.addEventListener('focus', function () {
    if (searchInput.value.trim().length >= 2 && dropdown.children.length > 1) {
      showDropdown();
    }
  });
}());
