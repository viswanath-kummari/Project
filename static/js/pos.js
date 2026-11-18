/* ==========================================================================
   HIGH-SPEED POS BILLING SYSTEM CONTROLLER
   Fresh Cut Meat Shop Management System
   ========================================================================== */

const PosModule = {
  products: [],
  cart: [],
  selectedCategory: 'all',
  selectedPaymentMethod: 'CASH',
  selectedCustomer: null,
  activeTaxPercent: 5.0,
  discountAmount: 0.0,
  cashTendered: 0.0,

  async load() {
    await this.fetchProducts();
    await this.fetchCustomers();
    this.renderCategoryTabs();
    this.renderProductGrid();
    this.updateCartUI();
  },

  async fetchProducts() {
    try {
      const res = await Api.get('/products');
      this.products = res.products || [];
    } catch (err) {
      App.showToast('Could not load products: ' + err.message, 'error');
    }
  },

  async fetchCustomers() {
    try {
      const res = await Api.get('/customers');
      const selectEl = document.getElementById('pos-customer-select');
      if (selectEl) {
        selectEl.innerHTML = `
          <option value="">Walk-in Customer</option>
          ${res.customers.map(c => `
            <option value="${c.id}">${c.name} (${c.phone}) - Pts: ${c.loyalty_points}</option>
          `).join('')}
        `;
      }
    } catch (e) {
      console.warn('Customer load failed', e);
    }
  },

  renderCategoryTabs() {
    const tabsContainer = document.getElementById('pos-category-tabs');
    if (!tabsContainer) return;

    const categories = [
      { id: 'all', label: 'All Cuts', icon: 'bi-grid-fill' },
      { id: 'poultry', label: 'Poultry', icon: 'bi-egg-fill' },
      { id: 'mutton', label: 'Mutton & Lamb', icon: 'bi-fire' },
      { id: 'seafood', label: 'Seafood & Fish', icon: 'bi-water' },
      { id: 'deli', label: 'Marinated & Deli', icon: 'bi-stars' }
    ];

    tabsContainer.innerHTML = categories.map(cat => `
      <button class="pos-category-btn ${this.selectedCategory === cat.id ? 'active' : ''}" onclick="PosModule.filterCategory('${cat.id}')">
        <i class="bi ${cat.icon}"></i> ${cat.label}
      </button>
    `).join('');
  },

  filterCategory(catId) {
    this.selectedCategory = catId;
    this.renderCategoryTabs();
    this.renderProductGrid();
  },

  searchProducts(query) {
    this.renderProductGrid(query.toLowerCase());
  },

  renderProductGrid(searchQuery = '') {
    const grid = document.getElementById('pos-products-grid');
    if (!grid) return;

    let filtered = this.products;
    if (this.selectedCategory !== 'all') {
      filtered = filtered.filter(p => p.category === this.selectedCategory);
    }
    if (searchQuery) {
      filtered = filtered.filter(p => p.name.toLowerCase().includes(searchQuery) || p.sku.toLowerCase().includes(searchQuery));
    }

    if (filtered.length === 0) {
      grid.innerHTML = `
        <div class="col-12 text-center py-5 text-muted">
          <i class="bi bi-search fs-1 mb-2"></i>
          <div>No products match the selected criteria.</div>
        </div>
      `;
      return;
    }

    grid.innerHTML = filtered.map(p => {
      const isOutOfStock = p.current_stock <= 0;
      const isLowStock = p.current_stock <= p.min_stock_level;
      const stockBadge = isOutOfStock
        ? `<span class="badge badge-out-of-stock">Out of Stock</span>`
        : (isLowStock ? `<span class="badge badge-low-stock pulse-alert">${p.current_stock} ${p.unit} left</span>` : `<span class="badge badge-in-stock">${p.current_stock} ${p.unit}</span>`);

      const defaultImg = 'https://images.unsplash.com/photo-1604503468506-a8da13d82791?auto=format&fit=crop&w=400&q=80';
      const imgSrc = p.image_url || defaultImg;

      return `
        <div class="pos-card pos-product-card ${isOutOfStock ? 'opacity-50 pointer-events-none' : ''}" onclick="PosModule.addToCart('${p.id}')">
          <div class="pos-card-img-wrap">
            <img src="${imgSrc}" alt="${p.name}" class="pos-card-img" loading="lazy" onerror="this.src='${defaultImg}'">
            <div class="pos-card-badges-overlay">
              <span class="badge badge-${p.category}">${p.category.toUpperCase()}</span>
              ${stockBadge}
            </div>
          </div>
          <div>
            <div class="pos-prod-name" title="${p.name}">${p.name}</div>
            <div class="pos-prod-sku">${p.sku} &bull; ${p.unit}</div>
          </div>
          <div class="d-flex justify-content-between align-items-end mt-2">
            <div class="pos-prod-price">
              ${App.shopSettings.currency}${p.selling_price.toFixed(2)}<small>/${p.unit}</small>
            </div>
            <button class="btn btn-sm btn-danger rounded-circle d-flex align-items-center justify-content-center shadow-sm" style="width:34px; height:34px;" ${isOutOfStock ? 'disabled' : ''}>
              <i class="bi bi-plus-lg"></i>
            </button>
          </div>
        </div>
      `;
    }).join('');
  },

  addToCart(productId, quantity = null) {
    const prod = this.products.find(p => p.id === productId);
    if (!prod) return;

    if (prod.current_stock <= 0) {
      App.showToast(`'${prod.name}' is out of stock!`, 'warning');
      return;
    }

    const defaultQty = (prod.unit === 'KG') ? 1.000 : 1;
    const addQty = quantity !== null ? quantity : defaultQty;

    const existingIndex = this.cart.findIndex(item => item.product.id === productId);
    if (existingIndex > -1) {
      const nextQty = (prod.unit === 'KG') 
        ? +(this.cart[existingIndex].quantity + addQty).toFixed(3)
        : Math.round(this.cart[existingIndex].quantity + addQty);
      
      if (nextQty > prod.current_stock) {
        App.showToast(`Cannot exceed current stock (${prod.current_stock} ${prod.unit})`, 'warning');
        return;
      }
      this.cart[existingIndex].quantity = nextQty;
    } else {
      if (addQty > prod.current_stock) {
        App.showToast(`Cannot exceed current stock (${prod.current_stock} ${prod.unit})`, 'warning');
        return;
      }
      this.cart.push({
        product: prod,
        quantity: addQty
      });
    }

    this.updateCartUI();
  },

  updateItemQuantity(index, newQty) {
    if (index < 0 || index >= this.cart.length) return;
    const item = this.cart[index];
    const unit = item.product.unit;

    let qty = (unit === 'KG') ? parseFloat(newQty) : parseInt(newQty, 10);
    if (isNaN(qty) || qty <= 0) {
      this.removeItem(index);
      return;
    }

    if (qty > item.product.current_stock) {
      App.showToast(`Exceeds available stock (${item.product.current_stock} ${unit})`, 'warning');
      qty = item.product.current_stock;
    }

    item.quantity = (unit === 'KG') ? +(qty).toFixed(3) : Math.round(qty);
    this.updateCartUI();
  },

  stepQuantity(index, step) {
    if (index < 0 || index >= this.cart.length) return;
    const item = this.cart[index];
    const next = item.quantity + step;
    this.updateItemQuantity(index, next);
  },

  // Weight scale preset quick-add to the latest cart item
  applyWeightPreset(weightKg) {
    if (this.cart.length === 0) {
      App.showToast('Select a product to set weight scale value.', 'info');
      return;
    }
    const lastItem = this.cart[this.cart.length - 1];
    if (lastItem.product.unit !== 'KG') {
      App.showToast('Selected item is sold by Piece, not by KG weight scale.', 'warning');
      return;
    }
    this.updateItemQuantity(this.cart.length - 1, weightKg);
    App.showToast(`Scale input set to ${weightKg} KG for ${lastItem.product.name}`, 'info');
  },

  removeItem(index) {
    this.cart.splice(index, 1);
    this.updateCartUI();
  },

  clearCart() {
    this.cart = [];
    this.discountAmount = 0.0;
    this.cashTendered = 0.0;
    this.updateCartUI();
  },

  updateCartUI() {
    const container = document.getElementById('pos-cart-items');
    const countBadge = document.getElementById('cart-items-count');
    const subtotalEl = document.getElementById('cart-subtotal');
    const discountEl = document.getElementById('cart-discount');
    const taxEl = document.getElementById('cart-tax');
    const grandTotalEl = document.getElementById('cart-grand-total');
    const checkoutBtn = document.getElementById('pos-checkout-btn');

    if (!container) return;

    if (countBadge) countBadge.textContent = `${this.cart.length} items`;

    if (this.cart.length === 0) {
      container.innerHTML = `
        <div class="text-center py-5 text-muted">
          <i class="bi bi-cart3 fs-1 d-block mb-2 text-secondary opacity-50"></i>
          <span class="small">Cart is currently empty. Tap any fresh cut meat product to start billing.</span>
        </div>
      `;
      if (subtotalEl) subtotalEl.textContent = App.formatCurrency(0);
      if (discountEl) discountEl.textContent = App.formatCurrency(0);
      if (taxEl) taxEl.textContent = App.formatCurrency(0);
      if (grandTotalEl) grandTotalEl.textContent = App.formatCurrency(0);
      if (checkoutBtn) checkoutBtn.disabled = true;
      return;
    }

    if (checkoutBtn) checkoutBtn.disabled = false;

    let subtotal = 0.0;

    container.innerHTML = this.cart.map((item, idx) => {
      const lineTotal = +(item.quantity * item.product.selling_price).toFixed(2);
      subtotal += lineTotal;
      const stepVal = (item.product.unit === 'KG') ? 0.25 : 1;

      return `
        <div class="cart-item-row">
          <div class="cart-item-info">
            <div class="cart-item-name">${item.product.name}</div>
            <div class="cart-item-meta mono-num">
              ${App.shopSettings.currency}${item.product.selling_price.toFixed(2)} &times; ${item.quantity} ${item.product.unit}
            </div>
          </div>
          <div class="cart-qty-ctrl me-2">
            <button class="cart-qty-btn" onclick="PosModule.stepQuantity(${idx}, -${stepVal})">&minus;</button>
            <input type="number" step="${item.product.unit === 'KG' ? '0.001' : '1'}" min="0.001" class="cart-qty-input mono-num" value="${item.quantity}" onchange="PosModule.updateItemQuantity(${idx}, this.value)">
            <button class="cart-qty-btn" onclick="PosModule.stepQuantity(${idx}, ${stepVal})">&plus;</button>
          </div>
          <div class="fw-bold mono-num text-end" style="width: 75px;">
            ${App.shopSettings.currency}${lineTotal.toFixed(2)}
          </div>
          <button class="btn btn-link text-danger p-0 ms-2" onclick="PosModule.removeItem(${idx})" title="Remove item">
            <i class="bi bi-trash"></i>
          </button>
        </div>
      `;
    }).join('');

    const taxable = Math.max(0, subtotal - this.discountAmount);
    const taxAmount = +(taxable * (this.activeTaxPercent / 100)).toFixed(2);
    const grandTotal = +(taxable + taxAmount).toFixed(2);

    if (subtotalEl) subtotalEl.textContent = App.formatCurrency(subtotal);
    if (discountEl) discountEl.textContent = App.formatCurrency(this.discountAmount);
    if (taxEl) taxEl.textContent = App.formatCurrency(taxAmount);
    if (grandTotalEl) grandTotalEl.textContent = App.formatCurrency(grandTotal);

    this.currentGrandTotal = grandTotal;
  },

  setPaymentMethod(method) {
    this.selectedPaymentMethod = method;
    document.querySelectorAll('.pay-btn-mode').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-method') === method);
    });

    const cashCalcRow = document.getElementById('cash-tendered-row');
    if (cashCalcRow) {
      cashCalcRow.style.display = (method === 'CASH') ? 'flex' : 'none';
    }
  },

  calculateChange(tenderedVal) {
    this.cashTendered = parseFloat(tenderedVal) || 0.0;
    const change = Math.max(0, this.cashTendered - this.currentGrandTotal);
    const changeEl = document.getElementById('pos-change-returned');
    if (changeEl) {
      changeEl.textContent = App.formatCurrency(change);
    }
  },

  async promptDiscount() {
    const val = prompt('Enter discount amount in ₹:', this.discountAmount || '0');
    if (val !== null) {
      this.discountAmount = Math.max(0, parseFloat(val) || 0);
      this.updateCartUI();
    }
  },

  async executeCheckout() {
    if (this.cart.length === 0) {
      App.showToast('Please add items to the cart.', 'warning');
      return;
    }

    const customerSelect = document.getElementById('pos-customer-select');
    const customerId = customerSelect ? customerSelect.value : null;

    // If UPI selected, show interactive UPI modal with payment simulation
    if (this.selectedPaymentMethod === 'UPI') {
      this.showUPIPaymentModal(this.currentGrandTotal, async () => {
        await this.submitSalePayload(customerId);
      });
      return;
    }

    await this.submitSalePayload(customerId);
  },

  async submitSalePayload(customerId) {
    const payload = {
      items: this.cart.map(item => ({
        product_id: item.product.id,
        quantity: item.quantity
      })),
      customer_id: customerId || null,
      payment_method: this.selectedPaymentMethod,
      discount_amount: this.discountAmount,
      cash_tendered: this.selectedPaymentMethod === 'CASH' ? this.cashTendered : 0.0,
      notes: ''
    };

    try {
      const res = await Api.post('/pos/checkout', payload);
      App.showToast(`Sale Invoice #${res.sale.invoice_number} generated successfully!`, 'success');

      // Clear cart
      this.clearCart();

      // Refresh product list stock
      await this.fetchProducts();
      this.renderProductGrid();

      // Show Thermal Receipt preview modal
      this.showReceiptModal(res.sale);
    } catch (err) {
      App.showToast(err.message, 'error');
    }
  },

  showUPIPaymentModal(amount, onVerified) {
    const modalEl = document.getElementById('posUpiModal');
    if (!modalEl) {
      onVerified();
      return;
    }
    const upiAmountEl = document.getElementById('upi-modal-amount');
    if (upiAmountEl) upiAmountEl.textContent = App.formatCurrency(amount);

    const bsModal = new bootstrap.Modal(modalEl);
    bsModal.show();

    const verifyBtn = document.getElementById('upi-verify-success-btn');
    const newVerifyBtn = verifyBtn.cloneNode(true);
    verifyBtn.parentNode.replaceChild(newVerifyBtn, verifyBtn);

    newVerifyBtn.addEventListener('click', () => {
      bsModal.hide();
      onVerified();
    });
  },

  showReceiptModal(sale) {
    const preview = document.getElementById('thermal-receipt-preview');
    if (!preview) return;

    preview.innerHTML = `
      <div class="thermal-header">
        <h4 style="margin: 0; font-weight: bold; font-size: 16px;">${App.shopSettings.name}</h4>
        <div>${App.shopSettings.address}</div>
        <div>Tel: ${App.shopSettings.phone}</div>
        <div>GSTIN: ${App.shopSettings.gst_no}</div>
        <div class="thermal-divider"></div>
        <div><strong>TAX INVOICE: ${sale.invoice_number}</strong></div>
        <div>Date: ${new Date(sale.created_at).toLocaleString()}</div>
        <div>Cashier: ${sale.employee_name}</div>
        <div>Customer: ${sale.customer_name}</div>
      </div>
      <table style="width: 100%; border-collapse: collapse; font-size: 11px;">
        <thead>
          <tr style="border-bottom: 1px dashed #000;">
            <th style="text-align: left; padding: 2px 0;">Item</th>
            <th style="text-align: right; padding: 2px 0;">Qty</th>
            <th style="text-align: right; padding: 2px 0;">Rate</th>
            <th style="text-align: right; padding: 2px 0;">Amt</th>
          </tr>
        </thead>
        <tbody>
          ${sale.items.map(it => `
            <tr>
              <td style="padding: 2px 0;">${it.product_name}</td>
              <td style="text-align: right;">${it.quantity} ${it.unit}</td>
              <td style="text-align: right;">${it.unit_selling_price.toFixed(2)}</td>
              <td style="text-align: right;">${it.subtotal.toFixed(2)}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
      <div class="thermal-divider"></div>
      <div style="font-size: 11px;">
        <div style="display: flex; justify-content: space-between;">
          <span>Subtotal:</span>
          <span>${App.shopSettings.currency}${sale.subtotal.toFixed(2)}</span>
        </div>
        ${sale.discount_amount > 0 ? `
          <div style="display: flex; justify-content: space-between;">
            <span>Discount:</span>
            <span>-${App.shopSettings.currency}${sale.discount_amount.toFixed(2)}</span>
          </div>` : ''}
        <div style="display: flex; justify-content: space-between;">
          <span>Tax (GST ${App.shopSettings.tax_percent}%):</span>
          <span>${App.shopSettings.currency}${sale.tax_amount.toFixed(2)}</span>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 14px; font-weight: bold; margin-top: 4px;">
          <span>TOTAL:</span>
          <span>${App.shopSettings.currency}${sale.total_amount.toFixed(2)}</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin-top: 2px;">
          <span>Paid via:</span>
          <span>${sale.payment_method}</span>
        </div>
        ${sale.payment_method === 'CASH' && sale.cash_tendered > 0 ? `
          <div style="display: flex; justify-content: space-between;">
            <span>Cash Tendered:</span>
            <span>${App.shopSettings.currency}${sale.cash_tendered.toFixed(2)}</span>
          </div>
          <div style="display: flex; justify-content: space-between;">
            <span>Change Returned:</span>
            <span>${App.shopSettings.currency}${sale.change_returned.toFixed(2)}</span>
          </div>` : ''}
      </div>
      <div class="thermal-divider"></div>
      <div style="text-align: center; font-size: 10px;">
        <div>*** Fresh Cut Guarantee ***</div>
        <div>Store chilled between 0-4°C. Cook thoroughly.</div>
        <div>Thank you for choosing artisanal quality!</div>
      </div>
    `;

    const modalEl = document.getElementById('thermalReceiptModal');
    if (modalEl) {
      const bsModal = new bootstrap.Modal(modalEl);
      bsModal.show();
    }
  },

  async viewInvoice(invoiceNumber) {
    try {
      const res = await Api.get(`/pos/invoice/${invoiceNumber}`);
      this.showReceiptModal(res.sale);
    } catch (e) {
      App.showToast(e.message, 'error');
    }
  },

  printReceipt() {
    window.print();
  }
};

window.PosModule = PosModule;
