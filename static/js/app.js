/* ==========================================================================
   APPLICATION CONTROLLER & ROUTER
   Fresh Cut Meat Shop Management System
   ========================================================================== */

const App = {
  currentView: 'dashboard',
  currentUser: null,
  shopSettings: {
    name: 'Fresh Cut Artisanal Meat Co.',
    currency: '₹',
    tax_percent: 5.0,
    invoice_prefix: 'FC-'
  },

  async init() {
    console.log('🥩 Initializing Fresh Cut Meat Shop App...');
    
    // Check existing auth or default auto-login to Admin for smooth demo
    let user = Api.getUser();
    if (!user || !Api.getToken()) {
      await this.quickLogin('admin@freshcut.com', 'AdminPassword123!');
    } else {
      this.currentUser = user;
    }

    this.updateUserUI();
    this.setupEventListeners();
    await this.loadShopSettings();

    // Default route
    const hash = window.location.hash.replace('#', '') || 'dashboard';
    this.navigateTo(hash);
  },

  async quickLogin(email, password, pin = null) {
    try {
      const payload = pin ? { pin } : { email, password };
      const res = await Api.post('/auth/login', payload);
      Api.setAuth(res.token, res.user);
      this.currentUser = res.user;
      this.updateUserUI();
      this.showToast(`Welcome back, ${res.user.full_name}! (${res.user.role.toUpperCase()})`, 'success');
      this.navigateTo('dashboard');
    } catch (err) {
      this.showToast(err.message, 'error');
    }
  },

  async switchRole(roleTarget) {
    if (roleTarget === 'admin') {
      await this.quickLogin('admin@freshcut.com', 'AdminPassword123!');
    } else {
      await this.quickLogin('cashier@freshcut.com', 'CashierPassword123!');
    }
  },

  async loadShopSettings() {
    try {
      const res = await Api.get('/settings');
      if (res.settings && res.settings.shop_profile) {
        this.shopSettings = res.settings.shop_profile;
      }
    } catch (e) {
      console.warn('Could not load shop settings:', e);
    }
  },

  updateUserUI() {
    if (!this.currentUser) return;
    const nameEl = document.getElementById('header-user-name');
    const roleEl = document.getElementById('header-user-role');
    const avatarEl = document.getElementById('header-user-avatar');
    const roleBadgeEl = document.getElementById('current-role-badge');

    if (nameEl) nameEl.textContent = this.currentUser.full_name;
    if (roleEl) roleEl.textContent = this.currentUser.role.toUpperCase();
    if (avatarEl) avatarEl.textContent = this.currentUser.full_name.charAt(0);
    if (roleBadgeEl) {
      roleBadgeEl.textContent = this.currentUser.role.toUpperCase();
      roleBadgeEl.className = `badge ${this.currentUser.role === 'admin' ? 'bg-danger' : 'bg-success'}`;
    }

    // Role-based visibility toggle for sidebar and admin modules
    const isAdmin = (this.currentUser.role === 'admin');
    document.querySelectorAll('.admin-only').forEach(el => {
      el.style.display = isAdmin ? '' : 'none';
    });
  },

  setupEventListeners() {
    // Hash change router
    window.addEventListener('hashchange', () => {
      const hash = window.location.hash.replace('#', '') || 'dashboard';
      this.navigateTo(hash);
    });

    // Sidebar navigation clicks
    document.querySelectorAll('.sidebar-link').forEach(link => {
      link.addEventListener('click', (e) => {
        const view = link.getAttribute('data-view');
        if (view) {
          e.preventDefault();
          this.navigateTo(view);
        }
      });
    });

    // Mobile sidebar toggle
    const toggleBtn = document.getElementById('sidebar-toggle');
    if (toggleBtn) {
      toggleBtn.addEventListener('click', () => {
        document.getElementById('sidebar').classList.toggle('show');
      });
    }

    // Role switcher dropdown buttons
    document.querySelectorAll('[data-switch-role]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const role = btn.getAttribute('data-switch-role');
        this.switchRole(role);
      });
    });
  },

  navigateTo(viewName) {
    // If regular employee tries to navigate to admin-only view, deny gracefully
    const adminViews = ['employees', 'expenses', 'suppliers', 'settings', 'audit'];
    if (this.currentUser && this.currentUser.role !== 'admin' && adminViews.includes(viewName)) {
      this.showToast('Access restricted: Administrator role required for this module.', 'warning');
      viewName = 'pos';
    }

    this.currentView = viewName;
    window.location.hash = viewName;

    // Update active nav link
    document.querySelectorAll('.sidebar-link').forEach(link => {
      link.classList.toggle('active', link.getAttribute('data-view') === viewName);
    });

    // Hide all view sections
    document.querySelectorAll('.view-section').forEach(sec => {
      sec.style.display = 'none';
      sec.classList.remove('page-view');
    });

    // Show target section with animation
    const targetSection = document.getElementById(`view-${viewName}`);
    if (targetSection) {
      targetSection.style.display = 'block';
      targetSection.classList.add('page-view');
    }

    // Close mobile sidebar if open
    const sidebar = document.getElementById('sidebar');
    if (sidebar && sidebar.classList.contains('show')) {
      sidebar.classList.remove('show');
    }

    // Trigger module loaders
    this.dispatchViewInit(viewName);
  },

  dispatchViewInit(viewName) {
    switch (viewName) {
      case 'dashboard':
        if (window.DashboardModule) DashboardModule.load();
        break;
      case 'pos':
        if (window.PosModule) PosModule.load();
        break;
      case 'products':
        if (window.ProductsModule) ProductsModule.load();
        break;
      case 'inventory':
        if (window.InventoryModule) InventoryModule.load();
        break;
      case 'customers':
        if (window.CustomersModule) CustomersModule.load();
        break;
      case 'suppliers':
        if (window.SuppliersModule) SuppliersModule.load();
        break;
      case 'expenses':
        if (window.FinanceModule) FinanceModule.load();
        break;
      case 'reports':
        if (window.ReportsModule) ReportsModule.load();
        break;
      case 'employees':
        if (window.EmployeesModule) EmployeesModule.load();
        break;
      case 'settings':
        if (window.SettingsModule) SettingsModule.load();
        break;
      case 'audit':
        if (window.AuditModule) AuditModule.load();
        break;
    }
  },

  // Interactive Animated Numerical Counter
  animateCounter(elementId, targetVal, duration = 1000, prefix = '', decimals = 2) {
    const el = document.getElementById(elementId);
    if (!el) return;

    const startVal = parseFloat(el.getAttribute('data-val') || '0');
    const startTime = performance.now();

    function update(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease out cubic
      const ease = 1 - Math.pow(1 - progress, 3);
      const currentVal = startVal + (targetVal - startVal) * ease;

      el.textContent = `${prefix}${currentVal.toLocaleString('en-IN', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
      })}`;

      if (progress < 1) {
        requestAnimationFrame(update);
      } else {
        el.setAttribute('data-val', targetVal);
        el.textContent = `${prefix}${targetVal.toLocaleString('en-IN', {
          minimumFractionDigits: decimals,
          maximumFractionDigits: decimals
        })}`;
      }
    }

    requestAnimationFrame(update);
  },

  // Notification Toast System
  showToast(message, type = 'info', duration = 3500) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `custom-toast toast-${type}`;

    let icon = 'bi-info-circle-fill text-primary';
    if (type === 'success') icon = 'bi-check-circle-fill text-success';
    if (type === 'error') icon = 'bi-x-circle-fill text-danger';
    if (type === 'warning') icon = 'bi-exclamation-triangle-fill text-warning';

    toast.innerHTML = `
      <i class="bi ${icon} fs-5"></i>
      <div class="flex-grow-1">
        <div class="fw-bold fs-7 text-dark">${type.toUpperCase()}</div>
        <div class="small text-muted">${message}</div>
      </div>
      <button type="button" class="btn-close btn-close-sm" aria-label="Close"></button>
    `;

    toast.querySelector('.btn-close').addEventListener('click', () => {
      toast.classList.add('toast-out');
      setTimeout(() => toast.remove(), 250);
    });

    container.appendChild(toast);

    setTimeout(() => {
      if (toast.parentElement) {
        toast.classList.add('toast-out');
        setTimeout(() => toast.remove(), 250);
      }
    }, duration);
  },

  formatCurrency(amount) {
    return `${this.shopSettings.currency} ${parseFloat(amount || 0).toLocaleString('en-IN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })}`;
  },

  formatWeight(quantity, unit = 'KG') {
    if (unit === 'PCS') {
      return `${Math.round(quantity)} PCS`;
    }
    return `${parseFloat(quantity || 0).toFixed(3)} KG`;
  }
};

window.App = App;
document.addEventListener('DOMContentLoaded', () => App.init());
