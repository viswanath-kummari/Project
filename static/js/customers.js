/* ==========================================================================
   CUSTOMERS & SUPPLIERS MODULES
   Fresh Cut Meat Shop Management System
   ========================================================================== */

const CustomersModule = {
  customers: [],

  async load() {
    await this.fetchCustomers();
    this.renderCustomersTable();
  },

  async fetchCustomers() {
    try {
      const res = await Api.get('/customers');
      this.customers = res.customers || [];
    } catch (e) {
      App.showToast(e.message, 'error');
    }
  },

  renderCustomersTable(search = '') {
    const tbody = document.getElementById('customers-table-tbody');
    if (!tbody) return;

    let list = this.customers;
    if (search) {
      list = list.filter(c => c.name.toLowerCase().includes(search.toLowerCase()) || c.phone.includes(search));
    }

    if (list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted">No customers registered yet.</td></tr>`;
      return;
    }

    tbody.innerHTML = list.map(c => `
      <tr>
        <td class="fw-bold">${c.name}</td>
        <td><span class="font-monospace text-primary">${c.phone}</span></td>
        <td class="text-muted small">${c.email || '-'}</td>
        <td class="mono-num fw-semibold">${App.formatCurrency(c.total_spent)}</td>
        <td><span class="badge bg-warning-subtle text-warning-emphasis border border-warning px-2 py-1">${c.loyalty_points} pts</span></td>
        <td class="mono-num ${c.pending_balance > 0 ? 'text-danger fw-bold' : 'text-muted'}">${App.formatCurrency(c.pending_balance)}</td>
        <td class="text-muted small">${c.notes || '-'}</td>
      </tr>
    `).join('');
  },

  openAddModal() {
    document.getElementById('cust-form-name').value = '';
    document.getElementById('cust-form-phone').value = '';
    document.getElementById('cust-form-email').value = '';
    document.getElementById('cust-form-address').value = '';
    document.getElementById('cust-form-notes').value = '';

    const modal = new bootstrap.Modal(document.getElementById('customerModal'));
    modal.show();
  },

  async saveCustomer() {
    const name = document.getElementById('cust-form-name').value.trim();
    const phone = document.getElementById('cust-form-phone').value.trim();
    const email = document.getElementById('cust-form-email').value.trim();
    const address = document.getElementById('cust-form-address').value.trim();
    const notes = document.getElementById('cust-form-notes').value.trim();

    if (!name || !phone) {
      App.showToast('Name and Phone are mandatory.', 'warning');
      return;
    }

    try {
      await Api.post('/customers', { name, phone, email, address, notes });
      App.showToast('Customer profile registered!', 'success');
      bootstrap.Modal.getInstance(document.getElementById('customerModal')).hide();
      await this.load();
      if (window.PosModule) PosModule.fetchCustomers();
    } catch (e) {
      App.showToast(e.message, 'error');
    }
  }
};

const SuppliersModule = {
  suppliers: [],

  async load() {
    await this.fetchSuppliers();
    this.renderSuppliersTable();
  },

  async fetchSuppliers() {
    try {
      const res = await Api.get('/suppliers');
      this.suppliers = res.suppliers || [];
    } catch (e) {
      App.showToast(e.message, 'error');
    }
  },

  renderSuppliersTable() {
    const tbody = document.getElementById('suppliers-table-tbody');
    if (!tbody) return;

    if (this.suppliers.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted">No suppliers registered.</td></tr>`;
      return;
    }

    tbody.innerHTML = this.suppliers.map(s => `
      <tr>
        <td>
          <div class="fw-bold">${s.company_name}</div>
          <small class="text-muted">GST: ${s.gst_or_tax_id || '-'}</small>
        </td>
        <td>${s.contact_person || '-'}</td>
        <td class="font-monospace">${s.phone}</td>
        <td class="small text-muted">${s.email || '-'}</td>
        <td class="mono-num fw-bold ${s.outstanding_balance > 0 ? 'text-danger' : 'text-success'}">
          ${App.formatCurrency(s.outstanding_balance)}
        </td>
        <td class="text-muted small">${s.address || '-'}</td>
        <td class="text-end">
          <button class="btn btn-sm btn-outline-primary" onclick="SuppliersModule.openIntakeModal('${s.id}')">
            <i class="bi bi-box-arrow-in-down"></i> Record Intake
          </button>
        </td>
      </tr>
    `).join('');
  },

  openAddModal() {
    document.getElementById('supp-form-company').value = '';
    document.getElementById('supp-form-contact').value = '';
    document.getElementById('supp-form-phone').value = '';
    document.getElementById('supp-form-email').value = '';
    document.getElementById('supp-form-gst').value = '';
    document.getElementById('supp-form-address').value = '';

    const modal = new bootstrap.Modal(document.getElementById('supplierModal'));
    modal.show();
  },

  async saveSupplier() {
    const company_name = document.getElementById('supp-form-company').value.trim();
    const contact_person = document.getElementById('supp-form-contact').value.trim();
    const phone = document.getElementById('supp-form-phone').value.trim();
    const email = document.getElementById('supp-form-email').value.trim();
    const gst_or_tax_id = document.getElementById('supp-form-gst').value.trim();
    const address = document.getElementById('supp-form-address').value.trim();

    if (!company_name || !phone) {
      App.showToast('Company Name and Phone are required.', 'warning');
      return;
    }

    try {
      await Api.post('/suppliers', { company_name, contact_person, phone, email, gst_or_tax_id, address });
      App.showToast('Supplier profile created!', 'success');
      bootstrap.Modal.getInstance(document.getElementById('supplierModal')).hide();
      await this.load();
    } catch (e) {
      App.showToast(e.message, 'error');
    }
  },

  openIntakeModal(supplierId = '') {
    const select = document.getElementById('intake-form-supplier');
    if (select) {
      select.innerHTML = this.suppliers.map(s => `<option value="${s.id}" ${s.id === supplierId ? 'selected' : ''}>${s.company_name}</option>`).join('');
    }

    // Populate products
    const prodSelect = document.getElementById('intake-form-product');
    if (prodSelect && window.ProductsModule && ProductsModule.products) {
      prodSelect.innerHTML = ProductsModule.products.map(p => `<option value="${p.id}">${p.name} (${p.unit})</option>`).join('');
    }

    document.getElementById('intake-form-qty').value = '';
    document.getElementById('intake-form-cost').value = '';
    document.getElementById('intake-form-invoice-no').value = `PO-${Date.now().toString().slice(-6)}`;

    const modal = new bootstrap.Modal(document.getElementById('purchaseIntakeModal'));
    modal.show();
  },

  async submitIntake() {
    const supplier_id = document.getElementById('intake-form-supplier').value;
    const product_id = document.getElementById('intake-form-product').value;
    const quantity = parseFloat(document.getElementById('intake-form-qty').value);
    const unit_cost_price = parseFloat(document.getElementById('intake-form-cost').value);
    const purchase_invoice_no = document.getElementById('intake-form-invoice-no').value.trim();

    if (!supplier_id || !product_id || isNaN(quantity) || isNaN(unit_cost_price) || quantity <= 0 || unit_cost_price <= 0) {
      App.showToast('Please fill all intake details with valid quantities and unit costs.', 'warning');
      return;
    }

    try {
      await Api.post('/suppliers/purchases', {
        supplier_id,
        purchase_invoice_no,
        items: [{
          product_id,
          quantity,
          unit_cost_price
        }],
        paid_amount: roundVal(quantity * unit_cost_price)
      });

      App.showToast('Purchase intake processed and inventory credited!', 'success');
      bootstrap.Modal.getInstance(document.getElementById('purchaseIntakeModal')).hide();
      await this.load();
    } catch (e) {
      App.showToast(e.message, 'error');
    }
  }
};

function roundVal(v) {
  return Math.round(v * 100) / 100;
}

window.CustomersModule = CustomersModule;
window.SuppliersModule = SuppliersModule;
