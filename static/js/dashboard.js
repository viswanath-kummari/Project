/* ==========================================================================
   UPGRADED DASHBOARD MODULE & CHART.JS ADVANCED VISUALIZATIONS
   Fresh Cut Meat Shop Management System
   ========================================================================== */

const DashboardModule = {
  trendChart: null,
  categoryChart: null,
  volumeBarChart: null,
  stockHealthChart: null,

  async load() {
    try {
      const data = await Api.get('/reports/dashboard');
      this.renderKPIs(data.kpis);
      this.renderCharts(data.charts);
      this.renderRecentTransactions(data.recent_transactions);
      await this.loadAdvancedVisualizations();
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

    // 1. 7-Day Revenue vs Expenses Trend (Upgraded Multi-Stop Gradient)
    const trendCtx = document.getElementById('dashboardTrendChart');
    if (trendCtx) {
      if (this.trendChart) this.trendChart.destroy();

      const ctx = trendCtx.getContext('2d');
      const redGradient = ctx.createLinearGradient(0, 0, 0, 320);
      redGradient.addColorStop(0, 'rgba(225, 29, 72, 0.32)');
      redGradient.addColorStop(0.5, 'rgba(225, 29, 72, 0.10)');
      redGradient.addColorStop(1, 'rgba(225, 29, 72, 0.00)');

      const datasets = [
        {
          label: 'Net Sales Revenue (₹)',
          data: charts.trend.revenue,
          borderColor: '#e11d48',
          backgroundColor: redGradient,
          borderWidth: 3,
          tension: 0.38,
          fill: true,
          pointBackgroundColor: '#ffffff',
          pointBorderColor: '#e11d48',
          pointBorderWidth: 2.5,
          pointRadius: 4.5,
          pointHoverRadius: 7
        }
      ];

      // If Admin, display expenses trend line
      if (App.currentUser && App.currentUser.role === 'admin' && charts.trend.expenses) {
        datasets.push({
          label: 'Operating Expenses (₹)',
          data: charts.trend.expenses,
          borderColor: '#d97706',
          backgroundColor: 'transparent',
          borderWidth: 2.5,
          borderDash: [6, 6],
          tension: 0.38,
          pointBackgroundColor: '#d97706',
          pointRadius: 4
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
            duration: 1100,
            easing: 'easeOutQuart'
          },
          plugins: {
            legend: {
              position: 'top',
              labels: {
                boxWidth: 14,
                usePointStyle: true,
                pointStyle: 'circle',
                font: { family: 'Plus Jakarta Sans', weight: '700', size: 12 }
              }
            },
            tooltip: {
              backgroundColor: '#0f172a',
              padding: 14,
              cornerRadius: 10,
              titleFont: { family: 'Plus Jakarta Sans', size: 13, weight: '700' },
              bodyFont: { family: 'Space Grotesk', size: 13 }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: { color: 'rgba(226, 232, 240, 0.7)' },
              ticks: {
                font: { family: 'Space Grotesk' },
                callback: (val) => `${App.shopSettings.currency}${val.toLocaleString('en-IN')}`
              }
            },
            x: {
              grid: { display: false },
              ticks: { font: { family: 'Plus Jakarta Sans', size: 11, weight: '600' } }
            }
          }
        }
      });
    }

    // 2. Category Distribution Doughnut (Poultry, Mutton, Seafood, Deli)
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
              '#e11d48', // Poultry (Crimson Rose)
              '#d97706', // Mutton (Amber)
              '#059669', // Seafood (Emerald)
              '#7c3aed'  // Deli (Violet)
            ],
            borderWidth: 3,
            borderColor: '#ffffff',
            hoverOffset: 8
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: {
            animateRotate: true,
            duration: 1000
          },
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                boxWidth: 12,
                usePointStyle: true,
                font: { family: 'Plus Jakarta Sans', weight: '700', size: 11 }
              }
            }
          },
          cutout: '70%'
        }
      });
    }
  },

  async loadAdvancedVisualizations() {
    // 3. Category Sales Volume Comparison Bar Chart
    const barCtx = document.getElementById('dashboardVolumeBarChart');
    if (barCtx) {
      if (this.volumeBarChart) this.volumeBarChart.destroy();

      this.volumeBarChart = new Chart(barCtx, {
        type: 'bar',
        data: {
          labels: ['Poultry', 'Mutton & Lamb', 'Seafood & Fish', 'Delicatessen'],
          datasets: [
            {
              label: 'Stock In Cold Room (KG/PCS)',
              data: [68.7, 39.8, 23.6, 39.2],
              backgroundColor: 'rgba(5, 150, 105, 0.85)',
              borderRadius: 8
            },
            {
              label: 'Sales Velocity (KG/PCS)',
              data: [28.4, 18.2, 12.5, 14.8],
              backgroundColor: 'rgba(225, 29, 72, 0.85)',
              borderRadius: 8
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: { duration: 900 },
          plugins: {
            legend: {
              position: 'top',
              labels: { font: { family: 'Plus Jakarta Sans', weight: '700', size: 11 } }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: { color: 'rgba(226, 232, 240, 0.7)' },
              ticks: { font: { family: 'Space Grotesk' } }
            },
            x: {
              grid: { display: false },
              ticks: { font: { family: 'Plus Jakarta Sans', weight: '600' } }
            }
          }
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
