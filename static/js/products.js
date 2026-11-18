/* ==========================================================================
   PRODUCTS MANAGEMENT MODULE
   Fresh Cut Meat Shop Management System
   ========================================================================== */

const ProductsModule = {
  products: [],

  async load() {
    await this.fetchProducts();
    this.renderProductsTable();
  },

  async fetchProducts() {
    try {
      const res = await Api.get('/products');
      this.products = res.products || [];
    } catch (err) {
      App.showToast('Failed to load products: ' + err.message, 'error');
    }
  },

  renderProductsTable(search = '') {
    const tbody = document.getElementById('products-table-tbody');
    if (!tbody) return;

    let list = this.products;
    if (search) {
      list = list.filter(p => p.name.toLowerCase().includes(search.toLowerCase()) || p.sku.toLowerCase().includes(search.toLowerCase()));
    }

    if (list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted">No products found.</td></tr>`;
      return;
    }

    const isAdmin = (App.currentUser && App.currentUser.role === 'admin');

    tbody.innerHTML = list.map(p => `
      <tr>
        <td>
          <div class="fw-bold text-dark">${p.name}</div>
          <small class="text-muted">${p.description || 'Artisanal cut'}</small>
        </td>
        <td><span class="badge bg-light text-dark border font-monospace">${p.sku}</span></td>
        <td><span class="badge badge-${p.category}">${p.category.toUpperCase()}</span></td>
        <td><span class="badge bg-secondary-subtle text-secondary">${p.unit}</span></td>
        ${isAdmin ? `<td class="mono-num text-muted">${App.formatCurrency(p.cost_price)}</td>` : ''}
        <td class="mono-num fw-bold text-danger-emphasis">${App.formatCurrency(p.selling_price)}</td>
        <td class="text-end">
          ${isAdmin ? `
            <div class="btn-group btn-group-sm">
              <button class="btn btn-outline-secondary" onclick="ProductsModule.openEditModal('${p.id}')">
                <i class="bi bi-pencil"></i> Edit
              </button>
              <button class="btn btn-outline-danger" onclick="ProductsModule.deleteProduct('${p.id}', '${p.name}')">
                <i class="bi bi-trash"></i>
              </button>
            </div>
          ` : `<span class="badge bg-light text-muted">View Only</span>`}
        </td>
      </tr>
    `).join('');
  },

  openAddModal() {
    document.getElementById('product-modal-title').textContent = 'Add New Meat Cut / Product';
    document.getElementById('prod-form-id').value = '';
    document.getElementById('prod-form-sku').value = `CUT-${Math.floor(1000 + Math.random() * 9000)}`;
    document.getElementById('prod-form-name').value = '';
    document.getElementById('prod-form-category').value = 'poultry';
    document.getElementById('prod-form-unit').value = 'KG';
    document.getElementById('prod-form-selling').value = '';
    document.getElementById('prod-form-cost').value = '';
    document.getElementById('prod-form-min-stock').value = '5.0';
    document.getElementById('prod-form-initial-stock').value = '10.0';
    document.getElementById('prod-form-desc').value = '';

    const modal = new bootstrap.Modal(document.getElementById('productModal'));
    modal.show();
  },

  openEditModal(productId) {
    const p = this.products.find(x => x.id === productId);
    if (!p) return;

    document.getElementById('product-modal-title').textContent = `Edit Product: ${p.name}`;
    document.getElementById('prod-form-id').value = p.id;
    document.getElementById('prod-form-sku').value = p.sku;
    document.getElementById('prod-form-name').value = p.name;
    document.getElementById('prod-form-category').value = p.category;
    document.getElementById('prod-form-unit').value = p.unit;
    document.getElementById('prod-form-selling').value = p.selling_price;
    document.getElementById('prod-form-cost').value = p.cost_price || 0;
    document.getElementById('prod-form-min-stock').value = p.min_stock_level;
    document.getElementById('prod-form-initial-stock').closest('.mb-3').style.display = 'none';
    document.getElementById('prod-form-desc').value = p.description || '';

    const modal = new bootstrap.Modal(document.getElementById('productModal'));
    modal.show();
  },

  async saveProduct() {
    const id = document.getElementById('prod-form-id').value;
    const sku = document.getElementById('prod-form-sku').value.trim();
    const name = document.getElementById('prod-form-name').value.trim();
    const category = document.getElementById('prod-form-category').value;
    const unit = document.getElementById('prod-form-unit').value;
    const selling_price = parseFloat(document.getElementById('prod-form-selling').value);
    const cost_price = parseFloat(document.getElementById('prod-form-cost').value) || 0;
    const min_stock_level = parseFloat(document.getElementById('prod-form-min-stock').value) || 5;
    const initial_stock = parseFloat(document.getElementById('prod-form-initial-stock').value) || 0;
    const description = document.getElementById('prod-form-desc').value.trim();

    if (!sku || !name || isNaN(selling_price)) {
      App.showToast('Please fill all required fields.', 'warning');
      return;
    }

    try {
      if (id) {
        await Api.put(`/products/${id}`, {
          sku, name, category, unit, selling_price, cost_price, min_stock_level, description
        });
        App.showToast('Product updated successfully!', 'success');
      } else {
        await Api.post('/products', {
          sku, name, category, unit, selling_price, cost_price, min_stock_level, initial_stock, description
        });
        App.showToast('New product created!', 'success');
      }

      bootstrap.Modal.getInstance(document.getElementById('productModal')).hide();
      await this.load();
    } catch (e) {
      App.showToast(e.message, 'error');
    }
  },

  async deleteProduct(productId, name) {
    if (!confirm(`Are you sure you want to deactivate '${name}'?`)) return;
    try {
      await Api.delete(`/products/${productId}`);
      App.showToast('Product deactivated.', 'info');
      await this.load();
    } catch (e) {
      App.showToast(e.message, 'error');
    }
  }
};

window.ProductsModule = ProductsModule;
