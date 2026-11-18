/* ==========================================================================
   INVENTORY & WASTAGE MODULE CONTROLLER
   Fresh Cut Meat Shop Management System
   ========================================================================== */

const InventoryModule = {
  inventoryItems: [],
  selectedFilter: 'all',
  selectedCategory: 'all',

  async load() {
    await this.fetchInventory();
    await this.fetchMovements();
    this.populateProductSelects();
  },

  async fetchInventory() {
    try {
      const res = await Api.get('/inventory');
      this.inventoryItems = res.inventory || [];
      this.renderSummary(res.summary);
      this.renderInventoryTable();
    } catch (err) {
      App.showToast('Failed to load inventory: ' + err.message, 'error');
    }
  },

  renderSummary(summary) {
    if (!summary) return;
    const kgEl = document.getElementById('inv-total-kg');
    const pcsEl = document.getElementById('inv-total-pcs');
    const lowEl = document.getElementById('inv-low-count');
    const outEl = document.getElementById('inv-out-count');

    if (kgEl) kgEl.textContent = `${summary.total_stock_kg.toFixed(2)} KG`;
    if (pcsEl) pcsEl.textContent = `${summary.total_stock_pcs} PCS`;
    if (lowEl) lowEl.textContent = summary.low_stock_count;
    if (outEl) outEl.textContent = summary.out_of_stock_count;
  },

  filterStatus(status) {
    this.selectedFilter = status;
    document.querySelectorAll('[data-inv-filter]').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-inv-filter') === status);
    });
    this.renderInventoryTable();
  },

  renderInventoryTable() {
    const tbody = document.getElementById('inventory-table-tbody');
    if (!tbody) return;

    let filtered = this.inventoryItems;
    if (this.selectedFilter !== 'all') {
      filtered = filtered.filter(i => i.status === this.selectedFilter);
    }

    if (filtered.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" class="text-center py-4 text-muted">No inventory records matching filter.</td></tr>`;
      return;
    }

    const isAdmin = (App.currentUser && App.currentUser.role === 'admin');

    tbody.innerHTML = filtered.map(item => {
      const isOut = item.status === 'out_of_stock';
      const isLow = item.status === 'low_stock';
      const badge = isOut
        ? `<span class="badge badge-out-of-stock">Out of Stock</span>`
        : (isLow ? `<span class="badge badge-low-stock pulse-alert">Low Stock Alert</span>` : `<span class="badge badge-in-stock">In Stock</span>`);

      return `
        <tr class="interactive-row">
          <td>
            <div class="fw-bold text-dark">${item.product_name}</div>
            <small class="text-muted">${item.sku}</small>
          </td>
          <td><span class="badge badge-${item.category}">${item.category.toUpperCase()}</span></td>
          <td class="fw-bold mono-num fs-6 ${isOut ? 'text-danger' : (isLow ? 'text-warning-emphasis' : 'text-success')}">
            ${item.current_stock.toFixed(item.unit === 'KG' ? 3 : 0)} ${item.unit}
          </td>
          <td class="text-muted mono-num">${item.min_stock_level.toFixed(item.unit === 'KG' ? 3 : 0)} ${item.unit}</td>
          ${isAdmin ? `<td class="mono-num text-muted">${App.formatCurrency(item.cost_price)}</td>` : ''}
          <td class="mono-num fw-semibold text-danger-emphasis">${App.formatCurrency(item.selling_price)}</td>
          <td>${badge}</td>
          <td class="text-end">
            <div class="btn-group btn-group-sm">
              <button class="btn btn-outline-danger" onclick="InventoryModule.openWastageModal('${item.product_id}', '${item.product_name}', '${item.unit}', ${item.current_stock})" title="Log Wastage / Spoilage">
                <i class="bi bi-trash-fill"></i> Spoilage
              </button>
              ${isAdmin ? `
                <button class="btn btn-outline-secondary" onclick="InventoryModule.openAdjustmentModal('${item.product_id}', '${item.product_name}', '${item.unit}', ${item.current_stock})" title="Adjust Stock">
                  <i class="bi bi-sliders"></i>
                </button>
              ` : ''}
            </div>
          </td>
        </tr>
      `;
    }).join('');
  },

  async fetchMovements() {
    try {
      const res = await Api.get('/inventory/movements');
      const tbody = document.getElementById('inventory-movements-tbody');
      if (!tbody) return;

      if (!res.movements || res.movements.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted">No stock movements recorded yet.</td></tr>`;
        return;
      }

      tbody.innerHTML = res.movements.map(m => {
        const isPos = m.quantity > 0;
        const typeBadge = m.movement_type === 'SALE'
          ? 'bg-primary-subtle text-primary border border-primary'
          : (m.movement_type === 'PURCHASE'
            ? 'bg-success-subtle text-success border border-success'
            : (m.movement_type === 'WASTAGE' ? 'bg-danger-subtle text-danger border border-danger' : 'bg-secondary-subtle text-secondary border'));

        return `
          <tr>
            <td class="small text-muted">${new Date(m.created_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}</td>
            <td class="fw-semibold">${m.product_name}</td>
            <td><span class="badge ${typeBadge}">${m.movement_type}</span></td>
            <td class="mono-num fw-bold ${isPos ? 'text-success' : 'text-danger'}">
              ${isPos ? '+' : ''}${m.quantity.toFixed(m.unit === 'KG' ? 3 : 0)} ${m.unit}
            </td>
            <td class="mono-num small text-muted">${m.previous_stock.toFixed(m.unit === 'KG' ? 3 : 0)} &rarr; ${m.new_stock.toFixed(m.unit === 'KG' ? 3 : 0)}</td>
            <td class="small font-monospace">${m.reference_id || '-'}</td>
            <td class="small text-muted">${m.reason || '-'}</td>
          </tr>
        `;
      }).join('');
    } catch (e) {
      console.warn('Movements load failed', e);
    }
  },

  populateProductSelects() {
    const wastageSelect = document.getElementById('modal-wastage-product-id');
    const adjustSelect = document.getElementById('modal-adjust-product-id');

    const options = this.inventoryItems.map(i => `<option value="${i.product_id}">${i.product_name} (${i.current_stock} ${i.unit})</option>`).join('');

    if (wastageSelect) wastageSelect.innerHTML = `<option value="">Select product...</option>${options}`;
    if (adjustSelect) adjustSelect.innerHTML = `<option value="">Select product...</option>${options}`;
  },

  openWastageModal(productId = '', productName = '', unit = 'KG', curStock = 0) {
    const modalEl = document.getElementById('invWastageModal');
    if (!modalEl) return;

    const selectEl = document.getElementById('modal-wastage-product-id');
    const unitLabel = document.getElementById('modal-wastage-unit-label');
    const maxHint = document.getElementById('modal-wastage-max-hint');

    if (selectEl && productId) selectEl.value = productId;
    if (unitLabel) unitLabel.textContent = unit;
    if (maxHint) maxHint.textContent = `Available stock: ${curStock} ${unit}`;

    const modal = new bootstrap.Modal(modalEl);
    modal.show();
  },

  async submitWastage() {
    const selectEl = document.getElementById('modal-wastage-product-id');
    const qtyInput = document.getElementById('modal-wastage-qty');
    const reasonSelect = document.getElementById('modal-wastage-reason');
    const notesInput = document.getElementById('modal-wastage-notes');

    const productId = selectEl.value;
    const quantity = parseFloat(qtyInput.value);
    const reasonType = reasonSelect.value;
    const notes = notesInput.value.trim();

    if (!productId || isNaN(quantity) || quantity <= 0) {
      App.showToast('Please specify a valid product and positive wastage quantity.', 'warning');
      return;
    }

    const fullReason = `${reasonType}: ${notes || 'Recorded via Inventory Station'}`;

    try {
      const res = await Api.post('/inventory/wastage', {
        product_id: productId,
        quantity: quantity,
        reason: fullReason
      });

      App.showToast(res.message, 'success');
      bootstrap.Modal.getInstance(document.getElementById('invWastageModal')).hide();
      qtyInput.value = '';
      notesInput.value = '';
      await this.load();
    } catch (e) {
      App.showToast(e.message, 'error');
    }
  },

  openAdjustmentModal(productId = '', productName = '', unit = 'KG', curStock = 0) {
    const modalEl = document.getElementById('invAdjustmentModal');
    if (!modalEl) return;

    const selectEl = document.getElementById('modal-adjust-product-id');
    const unitLabel = document.getElementById('modal-adjust-unit-label');
    const curStockEl = document.getElementById('modal-adjust-cur-stock');

    if (selectEl && productId) selectEl.value = productId;
    if (unitLabel) unitLabel.textContent = unit;
    if (curStockEl) curStockEl.textContent = `Current Stock: ${curStock} ${unit}`;

    const modal = new bootstrap.Modal(modalEl);
    modal.show();
  },

  async submitAdjustment() {
    const selectEl = document.getElementById('modal-adjust-product-id');
    const typeSelect = document.getElementById('modal-adjust-type');
    const qtyInput = document.getElementById('modal-adjust-qty');
    const reasonInput = document.getElementById('modal-adjust-reason');

    const productId = selectEl.value;
    let qty = parseFloat(qtyInput.value);
    const adjType = typeSelect.value;
    const reason = reasonInput.value.trim();

    if (!productId || isNaN(qty) || qty === 0) {
      App.showToast('Please specify a valid product and non-zero adjustment quantity.', 'warning');
      return;
    }

    if (adjType === 'REDUCE') {
      qty = -Math.abs(qty);
    }

    try {
      const res = await Api.post('/inventory/adjustment', {
        product_id: productId,
        type: 'ADJUSTMENT',
        quantity: qty,
        reason: reason || 'Manual inventory recount/audit'
      });

      App.showToast(res.message, 'success');
      bootstrap.Modal.getInstance(document.getElementById('invAdjustmentModal')).hide();
      qtyInput.value = '';
      reasonInput.value = '';
      await this.load();
    } catch (e) {
      App.showToast(e.message, 'error');
    }
  }
};

window.InventoryModule = InventoryModule;
