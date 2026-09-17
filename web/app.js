/**
 * Infer/Daily — InShorts & Pinterest Hybrid Application Logic
 */

document.addEventListener('DOMContentLoaded', () => {
  let allCards = [];
  let currentTab = 'learn';
  let viewMode = 'grid'; // 'grid' (Pinterest) or 'stack' (InShorts)
  let searchQuery = '';
  let filterColabOnly = false;
  let currentStackIndex = 0;

  // DOM Elements
  const tabButtons = document.querySelectorAll('.tab-btn');
  const cardsGrid = document.getElementById('cards-grid');
  const emptyState = document.getElementById('empty-state');
  const dateBadgeText = document.getElementById('digest-date-text');
  
  const searchInput = document.getElementById('search-input');
  const clearSearchBtn = document.getElementById('clear-search');
  const filterColabBtn = document.getElementById('filter-colab');
  
  const viewGridBtn = document.getElementById('view-grid');
  const viewStackBtn = document.getElementById('view-stack');
  const masonryView = document.getElementById('masonry-view');
  const stackView = document.getElementById('stack-view');
  
  const stackPrevBtn = document.getElementById('stack-prev');
  const stackNextBtn = document.getElementById('stack-next');
  const stackCurrentNum = document.getElementById('stack-current-num');
  const stackTotalNum = document.getElementById('stack-total-num');
  const stackCardWrapper = document.getElementById('stack-card-wrapper');
  
  const toast = document.getElementById('toast');
  const toastMessage = document.getElementById('toast-message');

  // Load Digest Data
  async function loadDigestData() {
    const dataSources = [
      'latest.json',
      'data/digests/latest.json',
      'web/data/digests/latest.json',
      '../data/digests/latest.json',
      'sample.json',
      'data/digests/sample.json',
      '../data/digests/sample.json'
    ];

    let loadedData = null;
    for (const src of dataSources) {
      try {
        const resp = await fetch(src);
        if (resp.ok) {
          loadedData = await resp.json();
          console.log(`[Infer/Daily] Data loaded from ${src}`);
          break;
        }
      } catch (e) {
        // Fallback to next source
      }
    }

    if (loadedData && Array.isArray(loadedData)) {
      allCards = loadedData;
      updateCounts();
      updateDateBadge();
      renderActiveView();
    } else {
      showErrorState();
    }
  }

  function getFilteredCards() {
    return allCards.filter(card => {
      // Tab matching
      if (card.tab !== currentTab) return false;
      
      // Colab filter matching
      if (filterColabOnly && !card.colab_runnable) return false;

      // Search query matching
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        const text = `${card.headline} ${card.summary} ${card.why_it_matters} ${card.source_name}`.toLowerCase();
        if (!text.includes(query)) return false;
      }

      return true;
    });
  }

  function updateCounts() {
    const counts = { learn: 0, trending: 0, linkedin_idea: 0 };
    allCards.forEach(card => {
      if (counts.hasOwnProperty(card.tab)) {
        counts[card.tab]++;
      }
    });

    document.getElementById('count-learn').textContent = counts.learn;
    document.getElementById('count-trending').textContent = counts.trending;
    document.getElementById('count-linkedin_idea').textContent = counts.linkedin_idea;
  }

  function updateDateBadge() {
    if (allCards.length > 0 && allCards[0].date) {
      dateBadgeText.textContent = `As of ${allCards[0].date}`;
    } else {
      dateBadgeText.textContent = `As of ${new Date().toISOString().split('T')[0]}`;
    }
  }

  function renderActiveView() {
    const cards = getFilteredCards();

    if (cards.length === 0) {
      masonryView.classList.add('hidden');
      stackView.classList.add('hidden');
      emptyState.classList.remove('hidden');
      return;
    }

    emptyState.classList.add('hidden');

    if (viewMode === 'grid') {
      stackView.classList.add('hidden');
      masonryView.classList.remove('hidden');
      renderMasonryGrid(cards);
    } else {
      masonryView.classList.add('hidden');
      stackView.classList.remove('hidden');
      if (currentStackIndex >= cards.length) {
        currentStackIndex = 0;
      }
      renderStackCard(cards);
    }
  }

  // Render Pinterest Style Masonry Grid
  function renderMasonryGrid(cards) {
    cardsGrid.innerHTML = '';
    cards.forEach(card => {
      const cardElement = createCardElement(card, false);
      cardsGrid.appendChild(cardElement);
    });
  }

  // Render InShorts Style Stack Focused Card
  function renderStackCard(cards) {
    stackCardWrapper.innerHTML = '';
    stackCurrentNum.textContent = currentStackIndex + 1;
    stackTotalNum.textContent = cards.length;

    stackPrevBtn.disabled = currentStackIndex === 0;
    stackNextBtn.disabled = currentStackIndex === cards.length - 1;

    const currentCard = cards[currentStackIndex];
    if (currentCard) {
      const cardElement = createCardElement(currentCard, true);
      stackCardWrapper.appendChild(cardElement);
    }
  }

  // Create Card Element
  function createCardElement(card, isStack = false) {
    const cardDiv = document.createElement('div');
    cardDiv.className = 'digest-card';
    cardDiv.dataset.id = card.id;
    cardDiv.dataset.source = card.source_name;

    const colabBadgeHtml = card.colab_runnable
      ? `<span class="badge badge-colab">🧪 Try on Colab</span>`
      : '';

    const linkedinActionBtn = card.tab === 'linkedin_idea'
      ? `<button class="action-btn copy-linkedin-btn" title="Copy formatted LinkedIn post draft">
          <span>📝 Copy Post Draft</span>
        </button>`
      : `<button class="action-btn copy-summary-btn" title="Copy card summary">
          <span>📋 Copy</span>
        </button>`;

    cardDiv.innerHTML = `
      <div class="card-top-row">
        <span class="badge badge-source">${escapeHtml(card.source_name)}</span>
        ${colabBadgeHtml}
      </div>

      <h2 class="card-headline">${escapeHtml(card.headline)}</h2>
      <p class="card-summary">${escapeHtml(card.summary)}</p>
      
      <div class="why-matters-box">
        <div class="why-matters-title">Why it matters</div>
        <div class="why-matters-text">${escapeHtml(card.why_it_matters || 'Key development in inference engineering.')}</div>
      </div>

      <div class="card-footer-actions">
        <a href="${escapeHtml(card.source_url)}" target="_blank" rel="noopener noreferrer" class="source-btn" onclick="event.stopPropagation()">
          <span>Read Source</span> ↗
        </a>
        <div class="card-btns">
          ${linkedinActionBtn}
        </div>
      </div>
    `;

    // Event listeners for copy actions
    const copyLinkedInBtn = cardDiv.querySelector('.copy-linkedin-btn');
    if (copyLinkedInBtn) {
      copyLinkedInBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const postText = `💡 Inference Engineering Insight:\n\n${card.headline}\n\n${card.summary}\n\n🔥 Why it matters: ${card.why_it_matters}\n\nSource: ${card.source_url}`;
        copyToClipboard(postText, 'LinkedIn post draft copied to clipboard!');
      });
    }

    const copySummaryBtn = cardDiv.querySelector('.copy-summary-btn');
    if (copySummaryBtn) {
      copySummaryBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const text = `${card.headline}\n\n${card.summary}\n\nSource: ${card.source_url}`;
        copyToClipboard(text, 'Summary copied to clipboard!');
      });
    }

    return cardDiv;
  }

  function copyToClipboard(text, msg) {
    navigator.clipboard.writeText(text).then(() => {
      showToast(msg);
    }).catch(() => {
      showToast('Copied!');
    });
  }

  function showToast(message) {
    toastMessage.textContent = message;
    toast.classList.remove('hidden');
    setTimeout(() => {
      toast.classList.add('hidden');
    }, 2500);
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function showErrorState() {
    dateBadgeText.textContent = 'Data Unavailable';
    masonryView.classList.add('hidden');
    stackView.classList.add('hidden');
    emptyState.classList.remove('hidden');
  }

  // Tab Switcher
  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      tabButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentTab = btn.dataset.tab;
      currentStackIndex = 0;
      renderActiveView();
    });
  });

  // View Switcher (Pinterest Grid vs InShorts Stack)
  viewGridBtn.addEventListener('click', () => {
    viewGridBtn.classList.add('active');
    viewStackBtn.classList.remove('active');
    viewMode = 'grid';
    renderActiveView();
  });

  viewStackBtn.addEventListener('click', () => {
    viewStackBtn.classList.add('active');
    viewGridBtn.classList.remove('active');
    viewMode = 'stack';
    renderActiveView();
  });

  // Search Input Handler
  searchInput.addEventListener('input', (e) => {
    searchQuery = e.target.value;
    if (searchQuery.length > 0) {
      clearSearchBtn.classList.remove('hidden');
    } else {
      clearSearchBtn.classList.add('hidden');
    }
    currentStackIndex = 0;
    renderActiveView();
  });

  clearSearchBtn.addEventListener('click', () => {
    searchInput.value = '';
    searchQuery = '';
    clearSearchBtn.classList.add('hidden');
    currentStackIndex = 0;
    renderActiveView();
  });

  // Colab Filter Toggle
  filterColabBtn.addEventListener('click', () => {
    filterColabOnly = !filterColabOnly;
    filterColabBtn.classList.toggle('active', filterColabOnly);
    currentStackIndex = 0;
    renderActiveView();
  });

  // InShorts Stack Navigation
  stackPrevBtn.addEventListener('click', () => {
    if (currentStackIndex > 0) {
      currentStackIndex--;
      renderActiveView();
    }
  });

  stackNextBtn.addEventListener('click', () => {
    const cards = getFilteredCards();
    if (currentStackIndex < cards.length - 1) {
      currentStackIndex++;
      renderActiveView();
    }
  });

  // Keyboard Arrow Key Navigation for InShorts Stack Mode
  document.addEventListener('keydown', (e) => {
    if (viewMode === 'stack') {
      const cards = getFilteredCards();
      if (e.key === 'ArrowLeft' && currentStackIndex > 0) {
        currentStackIndex--;
        renderActiveView();
      } else if ((e.key === 'ArrowRight' || e.key === ' ') && currentStackIndex < cards.length - 1) {
        currentStackIndex++;
        renderActiveView();
      }
    }
  });

  // Initialize
  loadDigestData();
});
