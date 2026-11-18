/* ==========================================================================
   SETTINGS & AUDIT LOGS MODULES
   Fresh Cut Meat Shop Management System
   ========================================================================== */

const SettingsModule = {
  async load() {
    await this.fetchSettings();
  },

  async fetchSettings() {
    try {
      const res = await Api.get('/settings');
      const profile = res.settings.shop_profile || {};
      const supabase = res.settings.supabase_config || {};

      document.getElementById('shop-name-input').value = profile.name || '';
      document.getElementById('shop-tagline-input').value = profile.tagline || '';
      document.getElementById('shop-phone-input').value = profile.phone || '';
      document.getElementById('shop-address-input').value = profile.address || '';
      document.getElementById('shop-gst-input').value = profile.gst_no || '';
      document.getElementById('shop-tax-input').value = profile.tax_percent || 5.0;
      document.getElementById('shop-currency-input').value = profile.currency || '₹';
      document.getElementById('shop-prefix-input').value = profile.invoice_prefix || 'FC-';

      const statusBadge = document.getElementById('supabase-status-badge');
      if (statusBadge) {
        statusBadge.textContent = supabase.status === 'connected' ? 'SUPABASE CLOUD CONNECTED' : 'LOCAL PERSISTENT ENGINE';
        statusBadge.className = `badge ${supabase.status === 'connected' ? 'bg-success' : 'bg-secondary'}`;
      }
    } catch (e) {
      App.showToast(e.message, 'error');
    }
  },

  async saveShopProfile() {
    const payload = {
      name: document.getElementById('shop-name-input').value.trim(),
      tagline: document.getElementById('shop-tagline-input').value.trim(),
      phone: document.getElementById('shop-phone-input').value.trim(),
      address: document.getElementById('shop-address-input').value.trim(),
      gst_no: document.getElementById('shop-gst-input').value.trim(),
      tax_percent: parseFloat(document.getElementById('shop-tax-input').value) || 5.0,
      currency: document.getElementById('shop-currency-input').value.trim(),
      invoice_prefix: document.getElementById('shop-prefix-input').value.trim()
    };

    try {
      const res = await Api.post('/settings/profile', payload);
      App.shopSettings = res.shop_profile;
      App.showToast('Shop parameters updated successfully!', 'success');
      App.updateUserUI();
    } catch (e) {
      App.showToast(e.message, 'error');
    }
  },

  async testSupabase() {
    const url = document.getElementById('supabase-url-input').value.trim();
    const key = document.getElementById('supabase-key-input').value.trim();

    App.showToast('Connecting to Supabase PostgreSQL...', 'info');

    try {
      const res = await Api.post('/settings/supabase', { supabase_url: url, supabase_key: key });
      App.showToast(`Supabase: ${res.diagnostic}`, 'success');
      await this.fetchSettings();
    } catch (e) {
      App.showToast(e.message, 'error');
    }
  }
};

const AuditModule = {
  async load() {
    await this.fetchLogs();
  },

  async fetchLogs(module = 'all') {
    try {
      const res = await Api.get(`/audit?module=${module}`);
      const tbody = document.getElementById('audit-table-tbody');
      if (!tbody) return;

      if (!res.audit_logs || res.audit_logs.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-muted">No audit logs found.</td></tr>`;
        return;
      }

      tbody.innerHTML = res.audit_logs.map(log => `
        <tr>
          <td class="small font-monospace text-muted">${new Date(log.created_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'medium' })}</td>
          <td>
            <div class="fw-bold">${log.user_name}</div>
            <small class="text-muted text-uppercase">${log.role}</small>
          </td>
          <td><span class="badge bg-dark-subtle text-dark border font-monospace">${log.module}</span></td>
          <td><span class="badge bg-secondary-subtle text-secondary-emphasis">${log.action}</span></td>
          <td class="small text-muted font-monospace">${JSON.stringify(log.details)}</td>
          <td class="small text-muted font-monospace">${log.ip_address}</td>
        </tr>
      `).join('');
    } catch (e) {
      App.showToast(e.message, 'error');
    }
  }
};

window.SettingsModule = SettingsModule;
window.AuditModule = AuditModule;
