/* ==========================================================================
   DASHBOARD MODULE & CHART.JS VISUALIZATIONS
   Fresh Cut Meat Shop Management System
   ========================================================================== */

const DashboardModule = {
  trendChart: null,
  categoryChart: null,

  async load() {
    try {
      const data = await Api.get('/reports/dashboard');
      this.renderKPIs(data.kpis);
      this.renderCharts(data.charts);
      this.renderRecentTransactions(data.recent_transactions);
    } catch (err) {
      App.showToast(`Error loading dashboard: ${err.message}`, 'error');
    }
  },

  renderKPIs(kpis) {
    const isAdmin = (App.currentUser && App.currentUser.role === 'admin');
    const currency = App.shopSettings.currency;

    // Animated numerical counters
    App.animateCounter('kpi-today-sales', kpis.today_sales, 800, `${currency} `, 2);
    App.animateCounter('kpi-total-revenue', kpis.total_revenue, 900, `${currency} `, 2);
    App.animateCounter('kpi-total-bills', kpis.total_bills, 700, '', 0);
    App.animateCounter('kpi-stock-kg', kpis.total_stock_kg, 800, '', 2);

    const lowStockEl = document.getElementById('kpi-low-stock');
    if (lowStockEl) {
      lowStockEl.textContent = kpis.low_stock_alerts;
      if (kpis.low_stock_alerts > 0) {
        lowStockEl.closest('.stat-card').classList.add('pulse-alert');
      } else {
        lowStockEl.closest('.stat-card').classList.remove('pulse-alert');
      }
    }

    // Admin-specific financial KPIs
    const profitCard = document.getElementById('kpi-gross-profit-card');
    const expensesCard = document.getElementById('kpi-expenses-card');
    const netResultCard = document.getElementById('kpi-net-result-card');

    if (isAdmin) {
      if (profitCard) profitCard.style.display = 'block';
      if (expensesCard) expensesCard.style.display = 'block';
      if (netResultCard) netResultCard.style.display = 'block';

      App.animateCounter('kpi-gross-profit', kpis.gross_profit || 0, 1000, `${currency} `, 2);
      App.animateCounter('kpi-total-expenses', kpis.total_expenses || 0, 900, `${currency} `, 2);
      App.animateCounter('kpi-net-result', kpis.net_operating_result || 0, 1100, `${currency} `, 2);
    } else {
      if (profitCard) profitCard.style.display = 'none';
      if (expensesCard) expensesCard.style.display = 'none';
      if (netResultCard) netResultCard.style.display = 'none';
    }
  },

  renderCharts(charts) {
    if (!charts || !window.Chart) return;

    // 1. 7-Day Revenue vs Expenses Trend
    const trendCtx = document.getElementById('dashboardTrendChart');
    if (trendCtx) {
      if (this.trendChart) this.trendChart.destroy();

      const ctx = trendCtx.getContext('2d');
      const redGradient = ctx.createLinearGradient(0, 0, 0, 300);
      redGradient.addColorStop(0, 'rgba(153, 27, 27, 0.28)');
      redGradient.addColorStop(1, 'rgba(153, 27, 27, 0.01)');

      const datasets = [
        {
          label: 'Revenue (₹)',
          data: charts.trend.revenue,
          borderColor: '#991b1b',
          backgroundColor: redGradient,
          borderWidth: 2.5,
          tension: 0.38,
          fill: true,
          pointBackgroundColor: '#991b1b',
          pointRadius: 4,
          pointHoverRadius: 6
        }
      ];

      // If Admin, display expenses trend line
      if (App.currentUser && App.currentUser.role === 'admin' && charts.trend.expenses) {
        datasets.push({
          label: 'Operating Expenses (₹)',
          data: charts.trend.expenses,
          borderColor: '#d97706',
          backgroundColor: 'transparent',
          borderWidth: 2,
          borderDash: [5, 5],
          tension: 0.38,
          pointBackgroundColor: '#d97706',
          pointRadius: 3
        });
      }

      this.trendChart = new Chart(trendCtx, {
        type: 'line',
        data: {
          labels: charts.trend.labels,
          datasets: datasets
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: {
            duration: 1000,
            easing: 'easeOutQuart'
          },
          plugins: {
            legend: {
              position: 'top',
              labels: {
                boxWidth: 12,
                font: { family: 'Plus Jakarta Sans', weight: '600', size: 12 }
              }
            },
            tooltip: {
              backgroundColor: '#0f172a',
              padding: 12,
              cornerRadius: 8,
              titleFont: { family: 'Plus Jakarta Sans', size: 13 },
              bodyFont: { family: 'Space Grotesk', size: 13 }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: { color: 'rgba(226, 232, 240, 0.6)' },
              ticks: {
                font: { family: 'Space Grotesk' },
                callback: (val) => `${App.shopSettings.currency}${val.toLocaleString('en-IN')}`
              }
            },
            x: {
              grid: { display: false },
              ticks: { font: { family: 'Plus Jakarta Sans', size: 11 } }
            }
          }
        }
      });
    }

    // 2. Category Distribution Doughnut
    const catCtx = document.getElementById('dashboardCategoryChart');
    if (catCtx) {
      if (this.categoryChart) this.categoryChart.destroy();

      this.categoryChart = new Chart(catCtx, {
        type: 'doughnut',
        data: {
          labels: charts.categories.labels,
          datasets: [{
            data: charts.categories.values,
            backgroundColor: [
              '#991b1b', // Poultry
              '#d97706', // Mutton
              '#be185d', // Beef
              '#059669', // Seafood
              '#7c3aed'  // Deli
            ],
            borderWidth: 2,
            borderColor: '#ffffff',
            hoverOffset: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: {
            animateRotate: true,
            duration: 900
          },
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                boxWidth: 10,
                font: { family: 'Plus Jakarta Sans', weight: '600', size: 11 }
              }
            }
          },
          cutout: '72%'
        }
      });
    }
  },

  renderRecentTransactions(transactions) {
    const tbody = document.getElementById('recent-sales-tbody');
    if (!tbody) return;

    if (!transactions || transactions.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-muted">No recent transactions recorded today.</td></tr>`;
      return;
    }

    tbody.innerHTML = transactions.map(s => `
      <tr class="interactive-row">
        <td>
          <span class="badge bg-light text-dark border font-monospace px-2 py-1">${s.invoice_number}</span>
        </td>
        <td>
          <div class="fw-bold">${s.customer_name}</div>
          <small class="text-muted">${s.customer_phone || 'Walk-in Customer'}</small>
        </td>
        <td>
          <span class="badge ${s.payment_method === 'UPI' ? 'bg-success-subtle text-success border border-success' : (s.payment_method === 'CARD' ? 'bg-primary-subtle text-primary border border-primary' : 'bg-warning-subtle text-warning-emphasis border border-warning')} px-2 py-1">
            ${s.payment_method}
          </span>
        </td>
        <td class="text-muted small">${new Date(s.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</td>
        <td class="fw-bold mono-num text-danger-emphasis">${App.formatCurrency(s.total_amount)}</td>
        <td class="text-end">
          <button class="btn btn-sm btn-outline-secondary" onclick="PosModule.viewInvoice('${s.invoice_number}')" title="View Thermal Receipt">
            <i class="bi bi-printer"></i>
          </button>
        </td>
      </tr>
    `).join('');
  }
};

window.DashboardModule = DashboardModule;
