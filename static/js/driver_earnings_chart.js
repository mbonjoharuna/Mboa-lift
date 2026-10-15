/**
 * driver_earnings_chart.js
 * ------------------------
 * Interactive Driver Earnings & Cashout Engine for MboaLift Douala.
 * Visualizes revenue earned via MTN MoMo vs Orange Money per day (last 7 days)
 * or per week (last 4 weeks) with custom dual-bar SVG rendering, tooltips,
 * and Mobile Money instant payout (cashout) modal handling.
 */

(function () {
  'use strict';

  let currentPeriod = 'daily'; // 'daily' or 'weekly'
  let earningsData = null;

  // Format currency with standard French space separator (e.g. 15 000)
  function formatXAF(num) {
    const val = Math.round(Number(num) || 0);
    return val.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
  }

  // Get active UI language ('fr' or 'en')
  function getCurrentLang() {
    if (window.MboaLiftI18n && typeof window.MboaLiftI18n.getCurrentLanguage === 'function') {
      return window.MboaLiftI18n.getCurrentLanguage() || 'fr';
    }
    return (document.documentElement.lang || 'fr').toLowerCase().startsWith('en') ? 'en' : 'fr';
  }

  // Render SVG dual-bar chart into #chartViewport
  function renderChart() {
    const container = document.getElementById('chartViewport');
    if (!container || !earningsData) return;

    const series = currentPeriod === 'daily' ? earningsData.daily : earningsData.weekly;
    if (!series || series.length === 0) {
      container.innerHTML = '<div style="padding:20px;color:#94a3b8;text-align:left;">Aucune donnée de recette disponible.</div>';
      return;
    }

    const lang = getCurrentLang();
    const maxVal = currentPeriod === 'daily' ? earningsData.max_daily : earningsData.max_weekly;
    const safeMax = Math.max(maxVal * 1.15, 1000); // 15% headroom for aesthetic spacing

    let html = `
      <div class="dual-bar-chart-grid" role="group" aria-label="Graphique des revenus">
    `;

    series.forEach((item, idx) => {
      const label = lang === 'fr' ? (item.label_fr || item.date) : (item.label_en || item.date);
      const momoHeight = Math.max(4, Math.round((item.momo / safeMax) * 100));
      const orangeHeight = Math.max(4, Math.round((item.orange / safeMax) * 100));
      const totalFormatted = formatXAF(item.total);
      const momoFormatted = formatXAF(item.momo);
      const orangeFormatted = formatXAF(item.orange);

      html += `
        <div class="chart-column" tabindex="0" data-idx="${idx}">
          <div class="chart-bars-wrap">
            <!-- MTN MoMo Bar -->
            <div class="bar-col bar-momo" style="height:${momoHeight}%;" title="MTN MoMo: ${momoFormatted} XAF">
              <span class="bar-inner-label">${item.momo >= (safeMax * 0.25) ? momoFormatted : ''}</span>
            </div>
            <!-- Orange Money Bar -->
            <div class="bar-col bar-orange" style="height:${orangeHeight}%;" title="Orange Money: ${orangeFormatted} XAF">
              <span class="bar-inner-label">${item.orange >= (safeMax * 0.25) ? orangeFormatted : ''}</span>
            </div>
          </div>

          <!-- Hover / Touch Tooltip -->
          <div class="chart-bar-tooltip">
            <strong class="tooltip-header">${label}</strong>
            <div class="tooltip-row momo-row">
              <span>🟡 MTN MoMo :</span>
              <strong>${momoFormatted} XAF</strong>
            </div>
            <div class="tooltip-row orange-row">
              <span>🟠 Orange Money :</span>
              <strong>${orangeFormatted} XAF</strong>
            </div>
            <div class="tooltip-total">
              <span>Total :</span>
              <strong>${totalFormatted} XAF</strong>
            </div>
          </div>

          <!-- X-Axis Label -->
          <div class="chart-x-label">${label}</div>
          <div class="chart-x-total">${totalFormatted}</div>
        </div>
      `;
    });

    html += `</div>`;
    container.innerHTML = html;

    // Update Period Subtitle
    const titleEl = document.getElementById('chartPeriodTitle');
    if (titleEl) {
      if (currentPeriod === 'daily') {
        titleEl.textContent = lang === 'fr' 
          ? 'Revenus quotidiens (7 derniers jours)' 
          : 'Daily revenue (last 7 days)';
      } else {
        titleEl.textContent = lang === 'fr' 
          ? 'Revenus hebdomadaires (4 dernières semaines)' 
          : 'Weekly revenue (last 4 weeks)';
      }
    }
  }

  // Setup Period Toggle (Daily vs Weekly)
  function setupPeriodToggle() {
    const btnDaily = document.getElementById('btnPeriodDaily');
    const btnWeekly = document.getElementById('btnPeriodWeekly');

    if (btnDaily) {
      btnDaily.addEventListener('click', () => {
        if (currentPeriod === 'daily') return;
        currentPeriod = 'daily';
        btnDaily.classList.add('active');
        if (btnWeekly) btnWeekly.classList.remove('active');
        renderChart();
      });
    }

    if (btnWeekly) {
      btnWeekly.addEventListener('click', () => {
        if (currentPeriod === 'weekly') return;
        currentPeriod = 'weekly';
        btnWeekly.classList.add('active');
        if (btnDaily) btnDaily.classList.remove('active');
        renderChart();
      });
    }
  }

  // Setup Mobile Money Cashout Modal & Quick Amount Pills
  function setupCashoutModal() {
    const modal = document.getElementById('cashoutModalBackdrop');
    const openBtn = document.getElementById('btnOpenCashoutModal');
    const closeBtn = document.getElementById('btnCloseCashoutModal');
    const cancelBtn = document.getElementById('btnCancelCashout');
    const amountInput = document.getElementById('cashoutAmount');

    if (!modal || !openBtn) return;

    function openModal() {
      modal.style.display = 'flex';
      modal.setAttribute('aria-hidden', 'false');
      if (amountInput) amountInput.focus();
    }

    function closeModal() {
      modal.style.display = 'none';
      modal.setAttribute('aria-hidden', 'true');
    }

    openBtn.addEventListener('click', openModal);
    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (cancelBtn) cancelBtn.addEventListener('click', closeModal);

    // Dismiss on backdrop click
    modal.addEventListener('click', (e) => {
      if (e.target === modal) closeModal();
    });

    // Escape key closes modal
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && modal.style.display === 'flex') {
        closeModal();
      }
    });

    // Quick amount pills
    document.querySelectorAll('.btn-amount-pill').forEach(pill => {
      pill.addEventListener('click', (e) => {
        e.preventDefault();
        const val = pill.getAttribute('data-val');
        if (amountInput && val) {
          amountInput.value = val;
        }
      });
    });

    // Operator selection cards visual sync
    const operatorRadios = modal.querySelectorAll('input[name="operator"]');
    operatorRadios.forEach(radio => {
      radio.addEventListener('change', () => {
        modal.querySelectorAll('.operator-choice').forEach(lbl => lbl.classList.remove('active'));
        if (radio.checked) {
          radio.closest('.operator-choice').classList.add('active');
        }
      });
    });
  }

  // Initialize
  function init() {
    const dataScript = document.getElementById('driverEarningsData');
    if (!dataScript) return;

    try {
      earningsData = JSON.parse(dataScript.textContent || '{}');
    } catch (e) {
      console.warn('[MboaLift Earnings] JSON parse error:', e);
      earningsData = null;
    }

    if (earningsData) {
      renderChart();
      setupPeriodToggle();
      setupCashoutModal();
    }

    // Re-render when language changes
    window.addEventListener('languageChanged', () => {
      renderChart();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
