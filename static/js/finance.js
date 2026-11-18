/* ==========================================================================
   FINANCE & EXPENSES MODULE
   Fresh Cut Meat Shop Management System
   ========================================================================== */

const FinanceModule = {
  expenses: [],

  async load() {
    await this.fetchExpenses();
    this.renderExpensesTable();
  },

  async fetchExpenses() {
    try {
      const res = await Api.get('/finance/expenses');
      this.expenses = res.expenses || [];
      const totalEl = document.getElementById('finance-total-expenses');
      if (totalEl) totalEl.textContent = App.formatCurrency(res.total_amount);
    } catch (e) {
      App.showToast(e.message, 'error');
    }
  },

  renderExpensesTable(filterCategory = 'all') {
    const tbody = document.getElementById('expenses-table-tbody');
    if (!tbody) return;

    let list = this.expenses;
    if (filterCategory !== 'all') {
      list = list.filter(e => e.category === filterCategory);
    }

    if (list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-muted">No operating expenses recorded.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(exp => `
      <tr>
        <td class="small font-monospace">${exp.expense_date}</td>
        <td><span class="badge bg-secondary-subtle text-secondary-emphasis">${exp.category}</span></td>
        <td class="fw-bold mono-num text-danger">${App.formatCurrency(exp.amount)}</td>
        <td><span class="badge bg-light text-dark border">${exp.payment_method}</span></td>
        <td class="text-muted small">${exp.description || '-'}</td>
        <td class="text-end">
          <button class="btn btn-sm btn-outline-danger" onclick="FinanceModule.deleteExpense('${exp.id}')">
            <i class="bi bi-trash"></i>
          </button>
        </td>
      </tr>
    `).join('');
  },

  openAddModal() {
    document.getElementById('exp-form-category').value = 'Electricity & Cold Chain';
    document.getElementById('exp-form-amount').value = '';
    document.getElementById('exp-form-date').value = new Date().toISOString().split('T')[0];
    document.getElementById('exp-form-method').value = 'UPI';
    document.getElementById('exp-form-desc').value = '';

    const modal = new bootstrap.Modal(document.getElementById('expenseModal'));
    modal.show();
  },

  async saveExpense() {
    const category = document.getElementById('exp-form-category').value;
    const amount = parseFloat(document.getElementById('exp-form-amount').value);
    const expense_date = document.getElementById('exp-form-date').value;
    const payment_method = document.getElementById('exp-form-method').value;
    const description = document.getElementById('exp-form-desc').value.trim();

    if (isNaN(amount) || amount <= 0) {
      App.showToast('Please enter a valid expense amount.', 'warning');
      return;
    }

    try {
      await Api.post('/finance/expenses', {
        category, amount, expense_date, payment_method, description
      });

      App.showToast('Operating expense recorded.', 'success');
      bootstrap.Modal.getInstance(document.getElementById('expenseModal')).hide();
      await this.load();
    } catch (e) {
      App.showToast(e.message, 'error');
    }
  },

  async deleteExpense(id) {
    if (!confirm('Are you sure you want to delete this expense record?')) return;
    try {
      await Api.delete(`/finance/expenses/${id}`);
      App.showToast('Expense removed.', 'info');
      await this.load();
    } catch (e) {
      App.showToast(e.message, 'error');
    }
  }
};

window.FinanceModule = FinanceModule;
