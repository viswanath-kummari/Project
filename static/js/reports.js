/* ==========================================================================
   REPORTS & PANDAS ANALYTICS MODULE
   Fresh Cut Meat Shop Management System
   ========================================================================== */

const ReportsModule = {
  pnlData: null,

  async load() {
    await this.fetchPnL();
  },

  async fetchPnL() {
    const start = document.getElementById('report-start-date')?.value || '';
    const end = document.getElementById('report-end-date')?.value || '';

    try {
      const url = `/reports/pnl?start_date=${start}&end_date=${end}`;
      const res = await Api.get(url);
      this.pnlData = res.pnl;
      this.renderPnL(res.pnl);
    } catch (e) {
      App.showToast(e.message, 'error');
    }
  },

  renderPnL(pnl) {
    if (!pnl) return;

    const setVal = (id, val, isCurrency = true) => {
      const el = document.getElementById(id);
      if (el) {
        el.textContent = isCurrency ? App.formatCurrency(val) : val;
      }
    };

    setVal('pnl-revenue', pnl.total_revenue);
    setVal('pnl-cogs', pnl.total_cogs);
    setVal('pnl-gross-profit', pnl.gross_profit);
    setVal('pnl-expenses', pnl.operating_expenses);
    setVal('pnl-wastage', pnl.wastage_cost);
    setVal('pnl-net-result', pnl.net_operating_result);

    const marginEl = document.getElementById('pnl-gross-margin');
    if (marginEl) marginEl.textContent = `${pnl.gross_margin_percent}%`;

    const netMarginEl = document.getElementById('pnl-net-margin');
    if (netMarginEl) netMarginEl.textContent = `${pnl.net_profit_percent}%`;

    const billsEl = document.getElementById('pnl-bills-count');
    if (billsEl) billsEl.textContent = pnl.total_bills;
  },

  exportReport(type, format) {
    const start = document.getElementById('report-start-date')?.value || '';
    const end = document.getElementById('report-end-date')?.value || '';
    const token = Api.getToken();

    const url = `/api/reports/export?type=${type}&format=${format}&start_date=${start}&end_date=${end}`;
    
    App.showToast(`Generating ${format.toUpperCase()} export for ${type.toUpperCase()}...`, 'info');

    // Trigger download via fetch with bearer token
    fetch(url, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(response => {
      if (!response.ok) throw new Error('Export generation failed');
      return response.blob();
    })
    .then(blob => {
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = `fresh_cut_${type}_${new Date().toISOString().split('T')[0]}.${format === 'excel' ? 'xlsx' : format}`;
      link.click();
      App.showToast(`${format.toUpperCase()} export downloaded!`, 'success');
    })
    .catch(err => {
      App.showToast(err.message, 'error');
    });
  }
};

window.ReportsModule = ReportsModule;
