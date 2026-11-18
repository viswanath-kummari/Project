/* ==========================================================================
   STAFF & USER MANAGEMENT MODULE (ADMIN ONLY)
   Fresh Cut Meat Shop Management System
   ========================================================================== */

const EmployeesModule = {
  employees: [],

  async load() {
    await this.fetchEmployees();
    this.renderEmployeesTable();
  },

  async fetchEmployees() {
    try {
      const res = await Api.get('/auth/employees');
      this.employees = res.employees || [];
    } catch (e) {
      App.showToast(e.message, 'error');
    }
  },

  renderEmployeesTable() {
    const tbody = document.getElementById('employees-table-tbody');
    if (!tbody) return;

    if (this.employees.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted">No employees registered.</td></tr>`;
      return;
    }

    tbody.innerHTML = this.employees.map(emp => `
      <tr>
        <td>
          <div class="fw-bold">${emp.full_name}</div>
          <small class="text-muted">${emp.email}</small>
        </td>
        <td>
          <span class="badge ${emp.role === 'admin' ? 'bg-danger' : 'bg-primary'} text-uppercase">
            ${emp.role}
          </span>
        </td>
        <td><span class="font-monospace text-muted">•••• (${emp.pin})</span></td>
        <td class="font-monospace">${emp.phone || '-'}</td>
        <td>
          <span class="badge ${emp.is_active ? 'badge-in-stock' : 'badge-out-of-stock'}">
            ${emp.is_active ? 'Active' : 'Deactivated'}
          </span>
        </td>
        <td class="small text-muted">${emp.last_login ? new Date(emp.last_login).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' }) : 'Never'}</td>
        <td class="text-end">
          <div class="btn-group btn-group-sm">
            <button class="btn btn-outline-secondary" onclick="EmployeesModule.openEditModal('${emp.id}')">
              <i class="bi bi-pencil"></i> Edit
            </button>
            <button class="btn ${emp.is_active ? 'btn-outline-danger' : 'btn-outline-success'}" onclick="EmployeesModule.toggleStatus('${emp.id}', ${!emp.is_active})">
              ${emp.is_active ? 'Deactivate' : 'Reactivate'}
            </button>
          </div>
        </td>
      </tr>
    `).join('');
  },

  openAddModal() {
    document.getElementById('emp-form-name').value = '';
    document.getElementById('emp-form-email').value = '';
    document.getElementById('emp-form-role').value = 'employee';
    document.getElementById('emp-form-pin').value = '1234';
    document.getElementById('emp-form-phone').value = '';
    document.getElementById('emp-form-password').value = 'FreshCut2026!';

    const modal = new bootstrap.Modal(document.getElementById('employeeModal'));
    modal.show();
  },

  async saveEmployee() {
    const full_name = document.getElementById('emp-form-name').value.trim();
    const email = document.getElementById('emp-form-email').value.trim();
    const role = document.getElementById('emp-form-role').value;
    const pin = document.getElementById('emp-form-pin').value.trim();
    const phone = document.getElementById('emp-form-phone').value.trim();
    const password = document.getElementById('emp-form-password').value.trim();

    if (!full_name || !email || !pin) {
      App.showToast('Please fill all required employee fields.', 'warning');
      return;
    }

    try {
      await Api.post('/auth/employees', {
        full_name, email, role, pin, phone, password
      });

      App.showToast('Employee account created!', 'success');
      bootstrap.Modal.getInstance(document.getElementById('employeeModal')).hide();
      await this.load();
    } catch (e) {
      App.showToast(e.message, 'error');
    }
  },

  async toggleStatus(id, newStatus) {
    try {
      await Api.put(`/auth/employees/${id}`, { is_active: newStatus });
      App.showToast(`Employee status updated to ${newStatus ? 'Active' : 'Deactivated'}.`, 'info');
      await this.load();
    } catch (e) {
      App.showToast(e.message, 'error');
    }
  }
};

window.EmployeesModule = EmployeesModule;
