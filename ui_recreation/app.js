/**
 * DukanIQ / ShopIQ Frontend Controller & Backend Integration
 * Full interactive client connected to FastAPI backend at http://localhost:8000/api/v1
 */

const API_BASE = 'http://localhost:8000/api/v1';

// App State
const state = {
  token: localStorage.getItem('dukaniq_token') || '',
  user: JSON.parse(localStorage.getItem('dukaniq_user') || 'null'),
  dashboardStats: null,
  products: [],
  categories: [],
  suppliers: [],
  batches: [],
  damagedGoods: [],
  auditLogs: [],
  notifications: [],
  currentRoute: 'dashboard',
  cart: [],
  paymentMethod: 'cash',
  customerName: '',
  amountReceived: 0,
  discountAmount: 0,
};

// Available Accounts for quick switching
const DEMO_USERS = [
  { name: 'Mehul Sharma', email: 'owner@dukaniq.com', password: 'admin123', role: 'Store Owner' },
  { name: 'Sunita Rao', email: 'manager@dukaniq.com', password: 'manager123', role: 'Store Manager' },
  { name: 'Amit Kumar', email: 'cashier@dukaniq.com', password: 'cashier123', role: 'Cashier' }
];

// Helper: Show Toast Notification
function showToast(message, type = 'success') {
  let toastContainer = document.getElementById('toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toast-container';
    toastContainer.className = 'fixed bottom-5 right-5 z-[9999] flex flex-col gap-2 pointer-events-none';
    document.body.appendChild(toastContainer);
  }

  const toast = document.createElement('div');
  const bg = type === 'success' ? 'bg-emerald-600 text-white' : type === 'error' ? 'bg-red-600 text-white' : 'bg-slate-800 text-white';
  const icon = type === 'success' ? 'check_circle' : type === 'error' ? 'error' : 'info';
  
  toast.className = `${bg} px-4 py-3 rounded-xl shadow-lg flex items-center gap-2.5 text-sm font-medium transition-all duration-300 transform translate-y-4 opacity-0 pointer-events-auto max-w-md`;
  toast.innerHTML = `
    <span class="material-symbols-outlined text-lg">${icon}</span>
    <span class="flex-1">${message}</span>
  `;

  toastContainer.appendChild(toast);
  requestAnimationFrame(() => {
    toast.classList.remove('translate-y-4', 'opacity-0');
  });

  setTimeout(() => {
    toast.classList.add('opacity-0', 'translate-y-2');
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// Helper: API Fetch with Auth
async function apiFetch(endpoint, options = {}) {
  const headers = options.headers || {};
  if (state.token) {
    headers['Authorization'] = `Bearer ${state.token}`;
  }
  if (!(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  try {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers
    });

    if (res.status === 401) {
      console.warn('Session expired or unauthorized, logging in again...');
      await autoLogin();
      return apiFetch(endpoint, options);
    }

    if (!res.ok) {
      const errData = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(errData.detail || `Request failed with status ${res.status}`);
    }

    return await res.json();
  } catch (err) {
    console.error(`API Error [${endpoint}]:`, err);
    throw err;
  }
}

// Auto Login with Owner credentials
async function autoLogin(email = 'owner@dukaniq.com', password = 'admin123') {
  try {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData
    });

    if (!res.ok) throw new Error('Authentication failed');
    const data = await res.json();
    state.token = data.access_token;
    state.user = data.user;
    localStorage.setItem('dukaniq_token', state.token);
    localStorage.setItem('dukaniq_user', JSON.stringify(state.user));
    
    updateUserUI();
    return true;
  } catch (e) {
    console.error('Login error:', e);
    showToast('Could not connect to backend at localhost:8000', 'error');
    return false;
  }
}

// Update User UI elements
function updateUserUI() {
  if (!state.user) return;
  const nameEl = document.querySelector('header .xl\\:flex span.font-label-md');
  const roleEl = document.querySelector('header .xl\\:flex span.font-caption-sm');
  if (nameEl) nameEl.textContent = state.user.name || 'Store Admin';
  if (roleEl) roleEl.textContent = (state.user.role || 'Owner').toUpperCase();
  
  const welcomeH1 = document.querySelector('main h1');
  if (welcomeH1 && welcomeH1.textContent.includes('Welcome back')) {
    welcomeH1.textContent = `Welcome back, ${state.user.name.split(' ')[0]}!`;
  }
}

// Fetch all initial data
async function loadAppData() {
  try {
    const [stats, prods, cats, supps] = await Promise.all([
      apiFetch('/dashboard').catch(() => null),
      apiFetch('/products').catch(() => []),
      apiFetch('/products/categories').catch(() => []),
      apiFetch('/suppliers').catch(() => [])
    ]);

    state.dashboardStats = stats;
    state.products = prods || [];
    state.categories = cats || [];
    state.suppliers = supps || [];

    updateDashboardKPIs();
    updateSidebarBadges();
  } catch (err) {
    console.error('Error loading app data:', err);
  }
}

// Update Dashboard KPI cards with live backend numbers
function updateDashboardKPIs() {
  const s = state.dashboardStats;
  if (!s) return;

  // 1. Gross sales
  const salesEl = document.querySelector('.bg-surface-card .font-metric-display');
  if (salesEl) {
    salesEl.textContent = `₹${(s.today_sales_amount || 0).toLocaleString('en-IN')}`;
  }

  // 2. Stock value
  const allCards = document.querySelectorAll('.grid-cols-1.sm\\:grid-cols-2.lg\\:grid-cols-4 > div');
  if (allCards.length >= 4) {
    // Card 1: Sales
    const c1Num = allCards[0].querySelector('.font-metric-display');
    if (c1Num) c1Num.textContent = `₹${(s.today_sales_amount || 0).toLocaleString('en-IN')}`;
    const c1Sub = allCards[0].querySelector('p');
    if (c1Sub) c1Sub.innerHTML = `<span class="material-symbols-outlined text-data-table">shopping_bag</span> ${s.today_sales_count || 0} Bills Settled Today`;

    // Card 2: Stock Value
    const c2Num = allCards[1].querySelector('.font-metric-display');
    if (c2Num) c2Num.textContent = `₹${(s.current_stock_value || 0).toLocaleString('en-IN')}`;
    const c2Sub = allCards[1].querySelector('p');
    if (c2Sub) c2Sub.innerHTML = `<span class="material-symbols-outlined text-data-table">inventory_2</span> ${s.total_active_products || 0} Active SKUs in Store`;

    // Card 3: Risk & FEFO Expiry
    const c3Num = allCards[2].querySelector('.font-metric-display');
    if (c3Num) c3Num.textContent = `${(s.expiring_soon_count || 0) + (s.expired_stock_count || 0)} Items`;
    const c3Sub = allCards[2].querySelector('p');
    if (c3Sub) c3Sub.innerHTML = `<span class="material-symbols-outlined text-data-table">warning</span> ${s.expired_stock_count || 0} Expired • ${s.expiring_soon_count || 0} Expiring Soon`;

    // Card 4: Vendor Payables
    const c4Num = allCards[3].querySelector('.font-metric-display');
    if (c4Num) c4Num.textContent = `₹${(s.supplier_outstanding || 0).toLocaleString('en-IN')}`;
    const c4Sub = allCards[3].querySelector('p');
    if (c4Sub) c4Sub.innerHTML = `<span class="material-symbols-outlined text-data-table">pending_actions</span> ${state.suppliers.length} Registered Suppliers`;
  }
}

// Update sidebar alert badges
function updateSidebarBadges() {
  const s = state.dashboardStats;
  if (!s) return;

  const lowStockBadge = document.querySelector('nav a[data-path="low-stock-alerts"] span.bg-error');
  if (lowStockBadge) {
    lowStockBadge.textContent = s.low_stock_count || 0;
    lowStockBadge.style.display = s.low_stock_count > 0 ? 'inline-block' : 'none';
  }

  const expiryBadge = document.querySelector('nav a[data-path="expiry-tracker"] span.bg-status-urgent');
  if (expiryBadge) {
    expiryBadge.textContent = `${s.expiring_soon_count || 0} FEFO`;
  }
}

// Navigation & View Routing
function initNavigation() {
  const navLinks = document.querySelectorAll('nav a[data-path]');
  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const path = link.getAttribute('data-path');
      navigateTo(path);
    });
  });

  // Handle window hash
  window.addEventListener('hashchange', () => {
    const hash = window.location.hash.replace('#', '') || 'dashboard';
    navigateTo(hash, false);
  });

  const initialHash = window.location.hash.replace('#', '') || 'dashboard';
  navigateTo(initialHash, false);
}

function navigateTo(path, updateHash = true) {
  state.currentRoute = path;
  if (updateHash) {
    window.location.hash = path;
  }

  // Update sidebar active classes
  document.querySelectorAll('nav a[data-path]').forEach(a => {
    if (a.getAttribute('data-path') === path) {
      a.className = 'flex items-center gap-space-sm px-space-sm py-2 rounded-lg font-body-sm bg-primary-container text-on-primary font-semibold transition-colors';
      const icon = a.querySelector('.material-symbols-outlined');
      if (icon) icon.className = 'material-symbols-outlined text-body-lg text-on-primary';
    } else {
      a.className = 'flex items-center gap-space-sm px-space-sm py-2 rounded-lg font-body-sm text-inverse-on-surface hover:bg-on-background/40 hover:text-surface-bright transition-colors';
      const icon = a.querySelector('.material-symbols-outlined');
      if (icon) icon.className = 'material-symbols-outlined text-body-lg text-outline-variant';
    }
  });

  renderView(path);
}

// Render dynamic sub-view in Main Container
function renderView(route) {
  const main = document.querySelector('main');
  if (!main) return;

  // If dashboard, restore default executive dashboard view
  if (route === 'dashboard') {
    const customView = document.getElementById('custom-subview');
    if (customView) customView.remove();
    const dashboardView = document.getElementById('dashboard-main-view');
    if (dashboardView) dashboardView.style.display = 'block';
    loadAppData();
    return;
  }

  // Hide dashboard view, show custom view
  const dashboardView = document.getElementById('dashboard-main-view');
  if (dashboardView) dashboardView.style.display = 'none';

  let customView = document.getElementById('custom-subview');
  if (!customView) {
    customView = document.createElement('div');
    customView.id = 'custom-subview';
    customView.className = 'p-space-lg space-y-space-lg';
    main.appendChild(customView);
  }

  customView.innerHTML = `
    <div class="flex items-center justify-center p-12 text-slate-500">
      <span class="material-symbols-outlined animate-spin text-3xl text-primary">sync</span>
    </div>
  `;

  // Render appropriate view
  switch (route) {
    case 'products-catalogue':
      renderProductsView(customView);
      break;
    case 'batch-inventory-ledger':
      renderInventoryView(customView);
      break;
    case 'low-stock-alerts':
      renderLowStockView(customView);
      break;
    case 'sales-pos-terminal':
      renderPOSView(customView);
      break;
    case 'purchases-inward-goods':
      renderPurchasesView(customView);
      break;
    case 'suppliers-ledgers':
      renderSuppliersView(customView);
      break;
    case 'expiry-tracker':
      renderExpiryView(customView);
      break;
    case 'damaged-goods':
      renderDamagedGoodsView(customView);
      break;
    case 'reports-analytics':
      renderReportsView(customView);
      break;
    case 'store-settings-audit-logs':
      renderSettingsAuditView(customView);
      break;
    default:
      customView.innerHTML = `
        <div class="bg-surface-card rounded-xl p-8 shadow-sm text-center">
          <h2 class="text-xl font-bold mb-2">Module Under Active Construction</h2>
          <p class="text-slate-500 mb-4">You can navigate back to the operational dashboard.</p>
          <button onclick="navigateTo('dashboard')" class="px-4 py-2 bg-primary text-white rounded-lg">Return to Dashboard</button>
        </div>
      `;
  }
}

// ──────────────────────────────────────────
// 1. PRODUCTS VIEW
// ──────────────────────────────────────────
async function renderProductsView(container) {
  try {
    const products = await apiFetch('/products');
    state.products = products;

    container.innerHTML = `
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-surface-card p-6 rounded-xl shadow-sm">
        <div>
          <h1 class="text-2xl font-bold text-on-surface">Product Master Catalogue</h1>
          <p class="text-sm text-slate-500">Manage catalogue SKUs, barcodes, selling prices and inventory thresholds.</p>
        </div>
        <div class="flex items-center gap-2">
          <button onclick="openAddProductModal()" class="flex items-center gap-1.5 px-4 py-2 bg-primary hover:bg-primary-container text-white rounded-lg font-medium shadow transition">
            <span class="material-symbols-outlined text-lg">add</span>
            Add Product SKU
          </button>
        </div>
      </div>

      <div class="bg-surface-card rounded-xl shadow-sm overflow-hidden">
        <div class="p-4 border-b border-slate-100 flex items-center justify-between gap-4">
          <div class="relative flex-1 max-w-md">
            <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">search</span>
            <input id="product-search-input" oninput="filterProductsTable()" type="text" placeholder="Search by name, SKU or barcode..." class="w-full pl-9 pr-4 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary">
          </div>
          <span class="text-xs text-slate-500 font-medium">${products.length} Products registered</span>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse text-sm" id="products-table">
            <thead>
              <tr class="bg-slate-50 text-slate-500 border-b border-slate-100 font-semibold text-xs uppercase tracking-wider">
                <th class="p-4">SKU / ID</th>
                <th class="p-4">Product Name</th>
                <th class="p-4">Barcode</th>
                <th class="p-4">Current Stock</th>
                <th class="p-4">Cost Price</th>
                <th class="p-4">Selling Price</th>
                <th class="p-4">Status</th>
                <th class="p-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              ${products.map(p => `
                <tr class="hover:bg-slate-50/80 transition-colors">
                  <td class="p-4 font-mono text-xs font-semibold text-primary">#${p.sku || p.id}</td>
                  <td class="p-4">
                    <p class="font-semibold text-slate-900">${p.name}</p>
                    <span class="text-xs text-slate-400">${p.unit}</span>
                  </td>
                  <td class="p-4 font-mono text-xs text-slate-600">${p.barcode || '—'}</td>
                  <td class="p-4">
                    <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold ${p.current_stock <= p.min_stock_threshold ? 'bg-red-100 text-red-700' : 'bg-emerald-100 text-emerald-700'}">
                      ${p.current_stock} ${p.unit}
                    </span>
                  </td>
                  <td class="p-4 tabular-nums">₹${p.default_purchase_price}</td>
                  <td class="p-4 tabular-nums font-semibold text-slate-900">₹${p.selling_price}</td>
                  <td class="p-4">
                    <span class="inline-block w-2 h-2 rounded-full ${p.is_active ? 'bg-emerald-500' : 'bg-slate-300'} mr-1"></span>
                    <span class="text-xs text-slate-600">${p.is_active ? 'Active' : 'Inactive'}</span>
                  </td>
                  <td class="p-4 text-right">
                    <button onclick="addToPosDirect(${p.id})" class="px-2.5 py-1 bg-slate-100 hover:bg-primary hover:text-white rounded text-xs font-medium transition" title="Add to POS Cart">
                      + Bill
                    </button>
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  } catch (err) {
    container.innerHTML = `<div class="p-6 bg-red-50 text-red-700 rounded-xl">Error loading products: ${err.message}</div>`;
  }
}

function filterProductsTable() {
  const query = document.getElementById('product-search-input')?.value.toLowerCase() || '';
  const rows = document.querySelectorAll('#products-table tbody tr');
  rows.forEach(row => {
    const text = row.textContent.toLowerCase();
    row.style.display = text.includes(query) ? '' : 'none';
  });
}

// ──────────────────────────────────────────
// 2. SALES & POS TERMINAL VIEW
// ──────────────────────────────────────────
async function renderPOSView(container) {
  if (state.products.length === 0) {
    state.products = await apiFetch('/products').catch(() => []);
  }

  container.innerHTML = `
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <!-- Left: Product Picker (7 Cols) -->
      <div class="lg:col-span-7 space-y-4">
        <div class="bg-surface-card p-4 rounded-xl shadow-sm flex items-center gap-3">
          <div class="relative flex-1">
            <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">search</span>
            <input id="pos-search-input" oninput="filterPosProducts()" type="text" placeholder="Scan barcode or type product name..." class="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary">
          </div>
          <button onclick="openBarcodeScanModal()" class="px-3 py-2 bg-slate-100 hover:bg-slate-200 rounded-lg text-slate-700 text-sm font-medium flex items-center gap-1">
            <span class="material-symbols-outlined text-lg">qr_code_scanner</span>
            Scan
          </button>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-3 gap-3" id="pos-products-grid">
          ${state.products.map(p => `
            <div onclick="addToCart(${p.id})" class="pos-item-card bg-surface-card p-3 rounded-xl border border-slate-200 hover:border-primary hover:shadow-md cursor-pointer transition flex flex-col justify-between">
              <div>
                <span class="text-[10px] uppercase font-mono text-slate-400">#${p.sku || p.barcode || p.id}</span>
                <h4 class="font-bold text-slate-900 text-sm line-clamp-2 mt-0.5">${p.name}</h4>
                <p class="text-xs text-slate-500 mt-1">Stock: ${p.current_stock} ${p.unit}</p>
              </div>
              <div class="mt-3 pt-2 border-t border-slate-100 flex items-center justify-between">
                <span class="font-bold text-base text-primary tabular-nums">₹${p.selling_price}</span>
                <span class="w-7 h-7 rounded-lg bg-primary/10 text-primary flex items-center justify-center font-bold text-sm">+</span>
              </div>
            </div>
          `).join('')}
        </div>
      </div>

      <!-- Right: Active Cart & Billing Terminal (5 Cols) -->
      <div class="lg:col-span-5 bg-surface-card rounded-xl shadow-sm p-6 flex flex-col justify-between min-h-[580px]">
        <div>
          <div class="flex items-center justify-between pb-4 border-b border-slate-100">
            <div>
              <h2 class="text-lg font-bold text-slate-900 flex items-center gap-2">
                <span class="material-symbols-outlined text-primary">point_of_sale</span>
                Active Bill Register
              </h2>
              <p class="text-xs text-slate-500">Invoice: AUTO-GEN (FEFO Batched)</p>
            </div>
            <button onclick="clearCart()" class="text-xs text-red-600 hover:underline font-medium">Clear Cart</button>
          </div>

          <!-- Customer details -->
          <div class="py-3 border-b border-slate-100 flex gap-2">
            <input id="cart-customer-name" value="${state.customerName}" oninput="state.customerName = this.value" type="text" placeholder="Customer Name (Optional)" class="flex-1 px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs">
          </div>

          <!-- Cart items list -->
          <div id="cart-items-container" class="divide-y divide-slate-100 max-h-72 overflow-y-auto my-2">
            <!-- Dynamic Cart Items Rendered Here -->
          </div>
        </div>

        <!-- Bill Summary & Checkout -->
        <div class="pt-4 border-t border-slate-100 space-y-3">
          <div class="space-y-1.5 text-sm">
            <div class="flex justify-between text-slate-600">
              <span>Subtotal:</span>
              <span id="cart-subtotal" class="font-semibold tabular-nums">₹0.00</span>
            </div>
            <div class="flex justify-between text-slate-600">
              <span>Discount (₹):</span>
              <input id="cart-discount" type="number" min="0" value="${state.discountAmount}" oninput="updateCartDiscount(this.value)" class="w-20 px-2 py-0.5 text-right bg-slate-50 border border-slate-200 rounded text-xs font-semibold">
            </div>
            <div class="flex justify-between text-base font-bold text-slate-900 pt-2 border-t border-slate-200">
              <span>Grand Total:</span>
              <span id="cart-grand-total" class="text-primary text-xl tabular-nums">₹0.00</span>
            </div>
          </div>

          <!-- Payment Method Selector -->
          <div class="grid grid-cols-3 gap-2 pt-2">
            <button type="button" onclick="setPaymentMethod('cash')" id="pay-cash-btn" class="py-2 rounded-lg border text-xs font-bold transition flex items-center justify-center gap-1 ${state.paymentMethod === 'cash' ? 'bg-primary text-white border-primary' : 'bg-slate-50 text-slate-700'}">
              <span class="material-symbols-outlined text-sm">payments</span>
              Cash
            </button>
            <button type="button" onclick="setPaymentMethod('upi')" id="pay-upi-btn" class="py-2 rounded-lg border text-xs font-bold transition flex items-center justify-center gap-1 ${state.paymentMethod === 'upi' ? 'bg-primary text-white border-primary' : 'bg-slate-50 text-slate-700'}">
              <span class="material-symbols-outlined text-sm">qr_code_2</span>
              UPI
            </button>
            <button type="button" onclick="setPaymentMethod('card')" id="pay-card-btn" class="py-2 rounded-lg border text-xs font-bold transition flex items-center justify-center gap-1 ${state.paymentMethod === 'card' ? 'bg-primary text-white border-primary' : 'bg-slate-50 text-slate-700'}">
              <span class="material-symbols-outlined text-sm">credit_card</span>
              Card
            </button>
          </div>

          <!-- Amount received & Change calculation for cash -->
          <div id="cash-change-calc" class="flex items-center justify-between text-xs bg-slate-50 p-2 rounded-lg ${state.paymentMethod === 'cash' ? '' : 'hidden'}">
            <span class="text-slate-600">Received (₹):</span>
            <input id="cash-received-input" oninput="calculateChange(this.value)" type="number" class="w-24 px-2 py-1 bg-white border border-slate-200 rounded text-right font-semibold">
            <span class="text-slate-600">Change: <strong id="cash-change-val" class="text-emerald-700 font-bold">₹0.00</strong></span>
          </div>

          <button onclick="submitCheckout()" id="checkout-btn" class="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl shadow-md transition flex items-center justify-center gap-2">
            <span class="material-symbols-outlined">check_circle</span>
            Complete & Print Bill (F1)
          </button>
        </div>
      </div>
    </div>
  `;

  renderCart();
}

function filterPosProducts() {
  const query = document.getElementById('pos-search-input')?.value.toLowerCase() || '';
  const cards = document.querySelectorAll('.pos-item-card');
  cards.forEach(card => {
    const text = card.textContent.toLowerCase();
    card.style.display = text.includes(query) ? '' : 'none';
  });
}

function addToCart(productId) {
  const product = state.products.find(p => p.id === productId);
  if (!product) return;

  const existing = state.cart.find(i => i.product_id === productId);
  if (existing) {
    existing.quantity += 1;
  } else {
    state.cart.push({
      product_id: product.id,
      name: product.name,
      unit_price: product.selling_price,
      quantity: 1,
      unit: product.unit
    });
  }

  renderCart();
  showToast(`Added ${product.name} to bill`, 'info');
}

function addToPosDirect(productId) {
  addToCart(productId);
  navigateTo('sales-pos-terminal');
}

function updateCartQty(productId, delta) {
  const item = state.cart.find(i => i.product_id === productId);
  if (!item) return;

  item.quantity += delta;
  if (item.quantity <= 0) {
    state.cart = state.cart.filter(i => i.product_id !== productId);
  }

  renderCart();
}

function clearCart() {
  state.cart = [];
  renderCart();
}

function setPaymentMethod(method) {
  state.paymentMethod = method;
  ['cash', 'upi', 'card'].forEach(m => {
    const btn = document.getElementById(`pay-${m}-btn`);
    if (btn) {
      if (m === method) {
        btn.className = 'py-2 rounded-lg border text-xs font-bold transition flex items-center justify-center gap-1 bg-primary text-white border-primary';
      } else {
        btn.className = 'py-2 rounded-lg border text-xs font-bold transition flex items-center justify-center gap-1 bg-slate-50 text-slate-700';
      }
    }
  });

  const cashCalc = document.getElementById('cash-change-calc');
  if (cashCalc) {
    if (method === 'cash') cashCalc.classList.remove('hidden');
    else cashCalc.classList.add('hidden');
  }
}

function updateCartDiscount(val) {
  state.discountAmount = parseFloat(val) || 0;
  calculateCartTotals();
}

function calculateChange(receivedVal) {
  const received = parseFloat(receivedVal) || 0;
  state.amountReceived = received;
  const subtotal = state.cart.reduce((sum, i) => sum + (i.unit_price * i.quantity), 0);
  const total = Math.max(0, subtotal - state.discountAmount);
  const change = Math.max(0, received - total);
  const changeEl = document.getElementById('cash-change-val');
  if (changeEl) changeEl.textContent = `₹${change.toFixed(2)}`;
}

function renderCart() {
  const container = document.getElementById('cart-items-container');
  if (!container) return;

  if (state.cart.length === 0) {
    container.innerHTML = `
      <div class="py-12 text-center text-slate-400">
        <span class="material-symbols-outlined text-4xl mb-1">shopping_basket</span>
        <p class="text-xs">No items added to current bill</p>
      </div>
    `;
  } else {
    container.innerHTML = state.cart.map(item => `
      <div class="py-2.5 flex items-center justify-between gap-3 text-sm">
        <div class="min-w-0 flex-1">
          <p class="font-semibold text-slate-900 truncate">${item.name}</p>
          <p class="text-xs text-slate-500 tabular-nums">₹${item.unit_price} × ${item.quantity}</p>
        </div>
        <div class="flex items-center gap-2">
          <div class="flex items-center border border-slate-200 rounded-lg overflow-hidden bg-slate-50">
            <button onclick="updateCartQty(${item.product_id}, -1)" class="w-6 h-6 flex items-center justify-center text-slate-600 hover:bg-slate-200 font-bold">-</button>
            <span class="w-8 text-center text-xs font-bold tabular-nums">${item.quantity}</span>
            <button onclick="updateCartQty(${item.product_id}, 1)" class="w-6 h-6 flex items-center justify-center text-slate-600 hover:bg-slate-200 font-bold">+</button>
          </div>
          <span class="font-bold text-slate-900 tabular-nums w-16 text-right">₹${(item.unit_price * item.quantity).toFixed(2)}</span>
        </div>
      </div>
    `).join('');
  }

  calculateCartTotals();
}

function calculateCartTotals() {
  const subtotal = state.cart.reduce((sum, i) => sum + (i.unit_price * i.quantity), 0);
  const total = Math.max(0, subtotal - state.discountAmount);

  const subEl = document.getElementById('cart-subtotal');
  const totEl = document.getElementById('cart-grand-total');
  if (subEl) subEl.textContent = `₹${subtotal.toFixed(2)}`;
  if (totEl) totEl.textContent = `₹${total.toFixed(2)}`;
}

// Submit Checkout calling POST /api/v1/sales
async function submitCheckout() {
  if (state.cart.length === 0) {
    showToast('Add at least one product to complete bill', 'error');
    return;
  }

  const subtotal = state.cart.reduce((sum, i) => sum + (i.unit_price * i.quantity), 0);
  const total = Math.max(0, subtotal - state.discountAmount);

  const today = new Date().toISOString().split('T')[0];
  const payload = {
    sale_date: today,
    payment_method: state.paymentMethod,
    discount_amount: state.discountAmount,
    amount_received: state.paymentMethod === 'cash' ? (state.amountReceived || total) : total,
    customer_name: state.customerName || 'Walk-in Customer',
    items: state.cart.map(i => ({
      product_id: i.product_id,
      quantity: i.quantity,
      unit_price: i.unit_price,
      discount_percent: 0.0
    }))
  };

  const btn = document.getElementById('checkout-btn');
  if (btn) btn.disabled = true;

  try {
    const saleResult = await apiFetch('/sales', {
      method: 'POST',
      body: JSON.stringify(payload)
    });

    showToast(`Sale #${saleResult.receipt_number} Completed!`, 'success');
    openReceiptModal(saleResult);

    // Reset cart and reload stats
    state.cart = [];
    state.discountAmount = 0;
    state.customerName = '';
    renderCart();
    loadAppData();
  } catch (err) {
    showToast(`Checkout Failed: ${err.message}`, 'error');
  } finally {
    if (btn) btn.disabled = false;
  }
}

// Receipt Modal
function openReceiptModal(sale) {
  const modal = document.createElement('div');
  modal.id = 'receipt-modal';
  modal.className = 'fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4';
  
  modal.innerHTML = `
    <div class="bg-white rounded-2xl max-w-sm w-full p-6 shadow-2xl space-y-4">
      <div class="text-center pb-3 border-b border-dashed border-slate-300">
        <h3 class="text-xl font-bold tracking-tight text-slate-900">DukanIQ Retail</h3>
        <p class="text-xs text-slate-500">Branch #1 MG Road, Bangalore</p>
        <p class="text-xs text-slate-400 mt-1">Receipt #${sale.receipt_number}</p>
        <p class="text-xs text-slate-400 font-mono">${new Date(sale.created_at || Date.now()).toLocaleString()}</p>
      </div>

      <div class="space-y-2 text-xs divide-y divide-slate-100 max-h-48 overflow-y-auto">
        ${(sale.items || []).map(i => `
          <div class="pt-1.5 flex justify-between">
            <span>Item #${i.product_id} × ${i.quantity}</span>
            <span class="font-mono font-semibold">₹${i.line_total}</span>
          </div>
        `).join('')}
      </div>

      <div class="pt-3 border-t border-dashed border-slate-300 space-y-1 text-xs">
        <div class="flex justify-between font-bold text-sm text-slate-900">
          <span>Total Paid:</span>
          <span class="text-primary font-mono text-base">₹${sale.net_amount || sale.total_amount}</span>
        </div>
        <div class="flex justify-between text-slate-500">
          <span>Payment Mode:</span>
          <span class="uppercase font-semibold">${sale.payment_method}</span>
        </div>
      </div>

      <div class="pt-2 flex gap-2">
        <button onclick="window.print()" class="flex-1 py-2 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-lg text-xs font-bold transition flex items-center justify-center gap-1">
          <span class="material-symbols-outlined text-sm">print</span> Print
        </button>
        <button onclick="document.getElementById('receipt-modal').remove()" class="flex-1 py-2 bg-primary hover:bg-primary-container text-white rounded-lg text-xs font-bold transition">
          Done
        </button>
      </div>
    </div>
  `;

  document.body.appendChild(modal);
}

// ──────────────────────────────────────────
// 3. PURCHASES & INWARD GOODS (GRN) VIEW
// ──────────────────────────────────────────
async function renderPurchasesView(container) {
  try {
    const [purchases, suppliers] = await Promise.all([
      apiFetch('/purchases').catch(() => []),
      apiFetch('/suppliers').catch(() => [])
    ]);

    state.suppliers = suppliers;

    container.innerHTML = `
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-surface-card p-6 rounded-xl shadow-sm">
        <div>
          <h1 class="text-2xl font-bold text-on-surface">Purchases & Inward Goods (GRN)</h1>
          <p class="text-sm text-slate-500">Record supplier purchase consignments, FEFO batches & inward lots.</p>
        </div>
        <button onclick="openNewPurchaseModal()" class="flex items-center gap-1.5 px-4 py-2 bg-primary hover:bg-primary-container text-white rounded-lg font-medium shadow transition">
          <span class="material-symbols-outlined text-lg">add</span>
          New Inward GRN (F3)
        </button>
      </div>

      <div class="bg-surface-card rounded-xl shadow-sm overflow-hidden">
        <div class="p-4 border-b border-slate-100 font-semibold text-sm text-slate-700">
          Recent Purchase Consignments
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse text-sm">
            <thead>
              <tr class="bg-slate-50 text-slate-500 border-b border-slate-100 font-semibold text-xs uppercase tracking-wider">
                <th class="p-4">GRN #</th>
                <th class="p-4">Date</th>
                <th class="p-4">Supplier</th>
                <th class="p-4">Invoice #</th>
                <th class="p-4">Total Amount</th>
                <th class="p-4">Paid</th>
                <th class="p-4">Balance</th>
                <th class="p-4">Status</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              ${purchases.length === 0 ? `
                <tr><td colspan="8" class="p-8 text-center text-slate-400">No purchases recorded yet. Click "New Inward GRN" to add.</td></tr>
              ` : purchases.map(p => `
                <tr class="hover:bg-slate-50 transition">
                  <td class="p-4 font-mono text-xs font-semibold text-primary">#GRN-${p.id}</td>
                  <td class="p-4 font-mono text-xs text-slate-600">${p.purchase_date}</td>
                  <td class="p-4 font-semibold text-slate-900">Supplier #${p.supplier_id}</td>
                  <td class="p-4 font-mono text-xs">${p.supplier_invoice_number || '—'}</td>
                  <td class="p-4 tabular-nums font-bold">₹${p.total_amount}</td>
                  <td class="p-4 tabular-nums text-emerald-700">₹${p.amount_paid}</td>
                  <td class="p-4 tabular-nums text-red-600 font-semibold">₹${p.outstanding_balance}</td>
                  <td class="p-4">
                    <span class="px-2 py-0.5 rounded-full text-xs font-semibold ${p.status === 'posted' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}">
                      ${p.status.toUpperCase()}
                    </span>
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  } catch (err) {
    container.innerHTML = `<div class="p-6 bg-red-50 text-red-700 rounded-xl">Error: ${err.message}</div>`;
  }
}

// ──────────────────────────────────────────
// 4. SUPPLIERS & LEDGERS VIEW
// ──────────────────────────────────────────
async function renderSuppliersView(container) {
  try {
    const suppliers = await apiFetch('/suppliers');
    state.suppliers = suppliers;

    container.innerHTML = `
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-surface-card p-6 rounded-xl shadow-sm">
        <div>
          <h1 class="text-2xl font-bold text-on-surface">Suppliers & Accounts Payable</h1>
          <p class="text-sm text-slate-500">Track vendor directory, outstanding credit balances and payment vouchers.</p>
        </div>
        <button onclick="openAddSupplierModal()" class="flex items-center gap-1.5 px-4 py-2 bg-primary hover:bg-primary-container text-white rounded-lg font-medium shadow transition">
          <span class="material-symbols-outlined text-lg">add</span>
          Add Vendor
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        ${suppliers.map(s => `
          <div class="bg-surface-card p-5 rounded-xl shadow-sm border border-slate-100 space-y-3">
            <div class="flex items-start justify-between">
              <div>
                <h3 class="font-bold text-slate-900 text-base">${s.business_name}</h3>
                <p class="text-xs text-slate-500">${s.contact_person || 'Direct Contact'}</p>
              </div>
              <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${s.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-200 text-slate-700'}">ACTIVE</span>
            </div>

            <div class="space-y-1 text-xs text-slate-600">
              <p class="flex items-center gap-1"><span class="material-symbols-outlined text-sm text-slate-400">call</span> ${s.phone || 'No phone'}</p>
              <p class="flex items-center gap-1"><span class="material-symbols-outlined text-sm text-slate-400">mail</span> ${s.email || 'No email'}</p>
            </div>

            <div class="pt-3 border-t border-slate-100 flex items-center justify-between">
              <div>
                <span class="text-[10px] text-slate-400 uppercase font-semibold">Payable Balance</span>
                <p class="text-lg font-bold text-red-600 tabular-nums">₹${s.outstanding_balance}</p>
              </div>
              <button onclick="openSupplierPaymentModal(${s.id}, '${s.business_name}')" class="px-3 py-1.5 bg-primary/10 hover:bg-primary hover:text-white text-primary text-xs font-bold rounded-lg transition">
                Record Payout
              </button>
            </div>
          </div>
        `).join('')}
      </div>
    `;
  } catch (err) {
    container.innerHTML = `<div class="p-6 bg-red-50 text-red-700 rounded-xl">Error: ${err.message}</div>`;
  }
}

// ──────────────────────────────────────────
// 5. INVENTORY & BATCH LEDGER VIEW
// ──────────────────────────────────────────
async function renderInventoryView(container) {
  try {
    const [snapshot, batches] = await Promise.all([
      apiFetch('/inventory').catch(() => []),
      apiFetch('/inventory/batches').catch(() => [])
    ]);

    container.innerHTML = `
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-surface-card p-6 rounded-xl shadow-sm">
        <div>
          <h1 class="text-2xl font-bold text-on-surface">Batch Inventory & Stock Ledger</h1>
          <p class="text-sm text-slate-500">Live batch quantities, purchase lots, FEFO expiry dates and valuation.</p>
        </div>
        <button onclick="openStockAdjustmentModal()" class="flex items-center gap-1.5 px-4 py-2 bg-slate-800 hover:bg-slate-900 text-white rounded-lg font-medium shadow transition">
          <span class="material-symbols-outlined text-lg">tune</span>
          Stock Adjustment
        </button>
      </div>

      <div class="bg-surface-card rounded-xl shadow-sm overflow-hidden">
        <div class="p-4 border-b border-slate-100 font-semibold text-sm text-slate-700">
          Active FEFO Batches (${batches.length} Lots)
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse text-sm">
            <thead>
              <tr class="bg-slate-50 text-slate-500 border-b border-slate-100 font-semibold text-xs uppercase tracking-wider">
                <th class="p-4">Batch #</th>
                <th class="p-4">Product</th>
                <th class="p-4">Qty Remaining</th>
                <th class="p-4">Unit Cost</th>
                <th class="p-4">Expiry Date</th>
                <th class="p-4">Batch Status</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              ${batches.map(b => `
                <tr class="hover:bg-slate-50 transition">
                  <td class="p-4 font-mono font-semibold text-primary text-xs">#${b.batch_number}</td>
                  <td class="p-4 font-semibold text-slate-900">${b.product_name || `Product #${b.product_id}`}</td>
                  <td class="p-4 tabular-nums font-bold">${b.quantity_remaining}</td>
                  <td class="p-4 tabular-nums">₹${b.unit_cost}</td>
                  <td class="p-4 font-mono text-xs ${b.expiry_date && new Date(b.expiry_date) < new Date() ? 'text-red-600 font-bold' : 'text-slate-600'}">
                    ${b.expiry_date || 'No Expiry'}
                  </td>
                  <td class="p-4">
                    <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${b.quantity_remaining > 0 ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-500'}">
                      ${b.quantity_remaining > 0 ? 'IN STOCK' : 'DEPLETED'}
                    </span>
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  } catch (err) {
    container.innerHTML = `<div class="p-6 bg-red-50 text-red-700 rounded-xl">Error: ${err.message}</div>`;
  }
}

// ──────────────────────────────────────────
// 6. LOW STOCK ALERTS VIEW
// ──────────────────────────────────────────
async function renderLowStockView(container) {
  try {
    const lowStock = await apiFetch('/inventory/low-stock');

    container.innerHTML = `
      <div class="bg-surface-card p-6 rounded-xl shadow-sm flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-on-surface">Low Stock Alerts & Reorder</h1>
          <p class="text-sm text-slate-500">Products where inventory count has fallen below the safety threshold.</p>
        </div>
        <button onclick="navigateTo('purchases-inward-goods')" class="px-4 py-2 bg-primary text-white rounded-lg text-sm font-semibold">
          Create Purchase PO
        </button>
      </div>

      <div class="bg-surface-card rounded-xl shadow-sm overflow-hidden">
        ${lowStock.length === 0 ? `
          <div class="p-12 text-center text-slate-400">
            <span class="material-symbols-outlined text-4xl text-emerald-500 mb-2">check_circle</span>
            <p class="text-base font-semibold text-slate-700">All Stock Healthy!</p>
            <p class="text-xs text-slate-500">No SKUs are currently below their minimum threshold.</p>
          </div>
        ` : `
          <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse text-sm">
              <thead>
                <tr class="bg-slate-50 text-slate-500 border-b border-slate-100 font-semibold text-xs uppercase tracking-wider">
                  <th class="p-4">Product Name</th>
                  <th class="p-4">Current Stock</th>
                  <th class="p-4">Min Threshold</th>
                  <th class="p-4">Deficit</th>
                  <th class="p-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100">
                ${lowStock.map(p => `
                  <tr class="hover:bg-slate-50">
                    <td class="p-4 font-bold text-slate-900">${p.name}</td>
                    <td class="p-4 text-red-600 font-bold">${p.current_stock} ${p.unit}</td>
                    <td class="p-4">${p.min_stock_threshold} ${p.unit}</td>
                    <td class="p-4 font-semibold text-amber-700 font-mono">-${Math.max(0, p.min_stock_threshold - p.current_stock)}</td>
                    <td class="p-4 text-right">
                      <button onclick="openNewPurchaseModal(${p.id})" class="px-3 py-1 bg-primary text-white rounded text-xs font-semibold">Reorder</button>
                    </td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        `}
      </div>
    `;
  } catch (err) {
    container.innerHTML = `<div class="p-6 bg-red-50 text-red-700 rounded-xl">Error: ${err.message}</div>`;
  }
}

// ──────────────────────────────────────────
// 7. EXPIRY TRACKER (FEFO) VIEW
// ──────────────────────────────────────────
async function renderExpiryView(container) {
  try {
    const expiryData = await apiFetch('/inventory/expiry?days=45');

    container.innerHTML = `
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-surface-card p-6 rounded-xl shadow-sm">
        <div>
          <h1 class="text-2xl font-bold text-on-surface">FEFO Expiry Risk Radar</h1>
          <p class="text-sm text-slate-500">Monitor perishable batches and apply clearance promotions before write-offs.</p>
        </div>
        <button onclick="openRecordDamageModal()" class="flex items-center gap-1.5 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium shadow transition">
          <span class="material-symbols-outlined text-lg">delete</span>
          Quarantine / Write-Off
        </button>
      </div>

      <div class="bg-surface-card rounded-xl shadow-sm overflow-hidden">
        <div class="p-4 border-b border-slate-100 flex items-center justify-between">
          <span class="font-semibold text-sm text-slate-700">Expiring Lots Queue</span>
          <span class="text-xs text-amber-700 font-bold bg-amber-50 px-2 py-0.5 rounded">FEFO Protected</span>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse text-sm">
            <thead>
              <tr class="bg-slate-50 text-slate-500 border-b border-slate-100 font-semibold text-xs uppercase tracking-wider">
                <th class="p-4">Batch Number</th>
                <th class="p-4">Product</th>
                <th class="p-4">Stock Left</th>
                <th class="p-4">Expiry Date</th>
                <th class="p-4">Risk Level</th>
                <th class="p-4 text-right">Clearance Action</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              ${expiryData.length === 0 ? `
                <tr><td colspan="6" class="p-8 text-center text-slate-400">No batches expiring in the next 45 days.</td></tr>
              ` : expiryData.map(e => {
                const daysLeft = e.days_to_expiry !== undefined ? e.days_to_expiry : Math.ceil((new Date(e.expiry_date) - new Date()) / (1000 * 60 * 60 * 24));
                const isExpired = daysLeft <= 0;
                const isUrgent = daysLeft > 0 && daysLeft <= 7;
                return `
                  <tr class="hover:bg-slate-50">
                    <td class="p-4 font-mono font-semibold text-xs text-primary">#${e.batch_number}</td>
                    <td class="p-4 font-semibold text-slate-900">${e.product_name || `Product #${e.product_id}`}</td>
                    <td class="p-4 tabular-nums font-bold">${e.quantity_remaining}</td>
                    <td class="p-4 font-mono text-xs font-semibold ${isExpired ? 'text-red-600' : isUrgent ? 'text-amber-600' : 'text-slate-600'}">
                      ${e.expiry_date}
                    </td>
                    <td class="p-4">
                      <span class="px-2 py-0.5 rounded-full text-xs font-bold ${isExpired ? 'bg-red-100 text-red-800' : isUrgent ? 'bg-amber-100 text-amber-800' : 'bg-blue-100 text-blue-800'}">
                        ${isExpired ? 'EXPIRED' : `${daysLeft} DAYS LEFT`}
                      </span>
                    </td>
                    <td class="p-4 text-right">
                      <button onclick="showToast('Promo alert created for batch ${e.batch_number}', 'info')" class="px-2.5 py-1 bg-amber-50 hover:bg-amber-100 text-amber-800 rounded text-xs font-semibold mr-1">
                        30% Off Clearance
                      </button>
                    </td>
                  </tr>
                `;
              }).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  } catch (err) {
    container.innerHTML = `<div class="p-6 bg-red-50 text-red-700 rounded-xl">Error: ${err.message}</div>`;
  }
}

// ──────────────────────────────────────────
// 8. DAMAGED GOODS VIEW
// ──────────────────────────────────────────
async function renderDamagedGoodsView(container) {
  try {
    const list = await apiFetch('/damaged-goods');

    container.innerHTML = `
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-surface-card p-6 rounded-xl shadow-sm">
        <div>
          <h1 class="text-2xl font-bold text-on-surface">Damaged Goods & Salvage Log</h1>
          <p class="text-sm text-slate-500">Record breakage, leakage, expired write-offs & vendor claims.</p>
        </div>
        <button onclick="openRecordDamageModal()" class="flex items-center gap-1.5 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium shadow transition">
          <span class="material-symbols-outlined text-lg">add</span>
          Record Damage
        </button>
      </div>

      <div class="bg-surface-card rounded-xl shadow-sm overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse text-sm">
            <thead>
              <tr class="bg-slate-50 text-slate-500 border-b border-slate-100 font-semibold text-xs uppercase tracking-wider">
                <th class="p-4">Date</th>
                <th class="p-4">Product ID</th>
                <th class="p-4">Quantity</th>
                <th class="p-4">Loss Value</th>
                <th class="p-4">Reason</th>
                <th class="p-4">Status</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              ${list.length === 0 ? `
                <tr><td colspan="6" class="p-8 text-center text-slate-400">No damaged goods recorded.</td></tr>
              ` : list.map(d => `
                <tr class="hover:bg-slate-50">
                  <td class="p-4 font-mono text-xs">${d.damage_date}</td>
                  <td class="p-4 font-semibold text-slate-900">SKU #${d.product_id}</td>
                  <td class="p-4 font-bold text-red-600">${d.quantity}</td>
                  <td class="p-4 font-bold tabular-nums">₹${d.estimated_value}</td>
                  <td class="p-4 text-slate-600">${d.reason || 'Damaged in transit / store'}</td>
                  <td class="p-4">
                    <span class="px-2 py-0.5 rounded-full text-xs font-bold uppercase bg-red-100 text-red-800">
                      ${d.status}
                    </span>
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  } catch (err) {
    container.innerHTML = `<div class="p-6 bg-red-50 text-red-700 rounded-xl">Error: ${err.message}</div>`;
  }
}

// ──────────────────────────────────────────
// 9. REPORTS & PROFIT ANALYTICS VIEW
// ──────────────────────────────────────────
async function renderReportsView(container) {
  try {
    const [salesReport, profitReport] = await Promise.all([
      apiFetch('/reports/sales').catch(() => null),
      apiFetch('/reports/gross-profit').catch(() => null)
    ]);

    container.innerHTML = `
      <div class="bg-surface-card p-6 rounded-xl shadow-sm">
        <h1 class="text-2xl font-bold text-on-surface">Financial Reports & Profit Analytics</h1>
        <p class="text-sm text-slate-500">Real-time Gross Profit Margin, COGS, Sales Velocity and GSTR-1 Summaries.</p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-surface-card p-5 rounded-xl shadow-sm">
          <span class="text-xs text-slate-400 font-semibold uppercase tracking-wider">Gross Revenue</span>
          <p class="text-2xl font-bold text-slate-900 tabular-nums mt-1">₹${profitReport?.total_revenue || 0}</p>
          <span class="text-xs text-emerald-600 font-medium mt-1 inline-block">Billed sales</span>
        </div>
        <div class="bg-surface-card p-5 rounded-xl shadow-sm">
          <span class="text-xs text-slate-400 font-semibold uppercase tracking-wider">Cost of Goods Sold (COGS)</span>
          <p class="text-2xl font-bold text-slate-700 tabular-nums mt-1">₹${profitReport?.total_cogs || 0}</p>
          <span class="text-xs text-slate-500 font-medium mt-1 inline-block">Direct purchase cost</span>
        </div>
        <div class="bg-surface-card p-5 rounded-xl shadow-sm">
          <span class="text-xs text-slate-400 font-semibold uppercase tracking-wider">Gross Profit</span>
          <p class="text-2xl font-bold text-emerald-600 tabular-nums mt-1">₹${profitReport?.gross_profit || 0}</p>
          <span class="text-xs text-emerald-600 font-medium mt-1 inline-block">Net trading gain</span>
        </div>
        <div class="bg-surface-card p-5 rounded-xl shadow-sm">
          <span class="text-xs text-slate-400 font-semibold uppercase tracking-wider">Gross Margin %</span>
          <p class="text-2xl font-bold text-primary tabular-nums mt-1">${profitReport?.gross_margin_percent || 0}%</p>
          <span class="text-xs text-primary font-medium mt-1 inline-block">Target: 25%+</span>
        </div>
      </div>

      <div class="bg-surface-card p-6 rounded-xl shadow-sm space-y-4">
        <h3 class="font-bold text-slate-900 text-base">Top Selling Products & Profit Breakdown</h3>
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse text-sm">
            <thead>
              <tr class="bg-slate-50 text-slate-500 font-semibold text-xs uppercase tracking-wider border-b border-slate-100">
                <th class="p-3">Product Name</th>
                <th class="p-3">Units Sold</th>
                <th class="p-3">Revenue</th>
                <th class="p-3">COGS</th>
                <th class="p-3">Gross Profit</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              ${(profitReport?.by_product || []).map(p => `
                <tr class="hover:bg-slate-50">
                  <td class="p-3 font-semibold text-slate-900">${p.product_name}</td>
                  <td class="p-3 font-bold tabular-nums">${p.quantity_sold}</td>
                  <td class="p-3 tabular-nums font-semibold">₹${p.revenue}</td>
                  <td class="p-3 tabular-nums text-slate-500">₹${p.cogs}</td>
                  <td class="p-3 tabular-nums text-emerald-600 font-bold">₹${p.gross_profit}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  } catch (err) {
    container.innerHTML = `<div class="p-6 bg-red-50 text-red-700 rounded-xl">Error: ${err.message}</div>`;
  }
}

// ──────────────────────────────────────────
// 10. SETTINGS & AUDIT LOGS VIEW
// ──────────────────────────────────────────
async function renderSettingsAuditView(container) {
  try {
    const logs = await apiFetch('/audit-logs');

    container.innerHTML = `
      <div class="bg-surface-card p-6 rounded-xl shadow-sm">
        <h1 class="text-2xl font-bold text-on-surface">Store Settings & System Audit Logs</h1>
        <p class="text-sm text-slate-500">Immutable chronological record of sensitive operations for supervisory compliance.</p>
      </div>

      <div class="bg-surface-card rounded-xl shadow-sm overflow-hidden">
        <div class="p-4 border-b border-slate-100 font-semibold text-sm text-slate-700">
          Supervisory Audit Trail (${logs.length} Operations)
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse text-sm">
            <thead>
              <tr class="bg-slate-50 text-slate-500 border-b border-slate-100 font-semibold text-xs uppercase tracking-wider">
                <th class="p-4">Timestamp</th>
                <th class="p-4">User</th>
                <th class="p-4">Action</th>
                <th class="p-4">Module / Entity</th>
                <th class="p-4">Details</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 font-mono text-xs">
              ${logs.map(l => `
                <tr class="hover:bg-slate-50">
                  <td class="p-4 text-slate-500">${new Date(l.created_at).toLocaleString()}</td>
                  <td class="p-4 font-bold text-slate-900">${l.user_email || `User #${l.user_id}`}</td>
                  <td class="p-4 text-primary font-bold">${l.action}</td>
                  <td class="p-4 text-slate-700 font-sans">${l.entity_type} #${l.entity_id || ''}</td>
                  <td class="p-4 text-slate-500 font-sans max-w-xs truncate">${l.details || '—'}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  } catch (err) {
    container.innerHTML = `<div class="p-6 bg-red-50 text-red-700 rounded-xl">Error: ${err.message}</div>`;
  }
}

// ──────────────────────────────────────────
// MODALS & ACTION DIALOGS
// ──────────────────────────────────────────

// Add Product Modal
function openAddProductModal() {
  const modal = document.createElement('div');
  modal.id = 'add-product-modal';
  modal.className = 'fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4';

  modal.innerHTML = `
    <div class="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
      <div class="flex items-center justify-between border-b pb-3 border-slate-100">
        <h3 class="text-lg font-bold text-slate-900">Add New Product SKU</h3>
        <button onclick="document.getElementById('add-product-modal').remove()" class="text-slate-400 hover:text-slate-600">
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>

      <form id="add-product-form" onsubmit="submitAddProduct(event)" class="space-y-3 text-xs">
        <div>
          <label class="block font-semibold text-slate-700 mb-1">Product Name *</label>
          <input required id="p-name" type="text" placeholder="e.g. Amul Salted Butter 100g" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm">
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-semibold text-slate-700 mb-1">SKU Code</label>
            <input id="p-sku" type="text" placeholder="e.g. AMUL-BUT-100" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm">
          </div>
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Barcode</label>
            <input id="p-barcode" type="text" placeholder="e.g. 890126201001" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm">
          </div>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Unit Type</label>
            <select id="p-unit" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm">
              <option value="piece">Piece (pc)</option>
              <option value="kg">Kilogram (kg)</option>
              <option value="liter">Liter (L)</option>
              <option value="pack">Pack</option>
            </select>
          </div>
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Min Threshold</label>
            <input id="p-threshold" type="number" value="5" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm">
          </div>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Purchase Cost (₹)</label>
            <input id="p-cost" type="number" step="0.5" value="45" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm">
          </div>
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Selling Price (₹) *</label>
            <input required id="p-price" type="number" step="0.5" value="56" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm">
          </div>
        </div>
        <div class="pt-3 flex gap-2">
          <button type="button" onclick="document.getElementById('add-product-modal').remove()" class="flex-1 py-2.5 bg-slate-100 text-slate-700 rounded-lg font-bold">Cancel</button>
          <button type="submit" class="flex-1 py-2.5 bg-primary text-white rounded-lg font-bold">Save Product</button>
        </div>
      </form>
    </div>
  `;

  document.body.appendChild(modal);
}

async function submitAddProduct(e) {
  e.preventDefault();
  const payload = {
    name: document.getElementById('p-name').value,
    sku: document.getElementById('p-sku').value || null,
    barcode: document.getElementById('p-barcode').value || null,
    unit: document.getElementById('p-unit').value,
    min_stock_threshold: parseFloat(document.getElementById('p-threshold').value) || 0,
    default_purchase_price: parseFloat(document.getElementById('p-cost').value) || 0,
    selling_price: parseFloat(document.getElementById('p-price').value),
    track_expiry: true
  };

  try {
    const newProd = await apiFetch('/products', {
      method: 'POST',
      body: JSON.stringify(payload)
    });

    showToast(`Product "${newProd.name}" Created!`, 'success');
    document.getElementById('add-product-modal')?.remove();
    loadAppData();
    if (state.currentRoute === 'products-catalogue') {
      renderProductsView(document.getElementById('custom-subview'));
    }
  } catch (err) {
    showToast(`Error: ${err.message}`, 'error');
  }
}

// New Inward Purchase (GRN) Modal
function openNewPurchaseModal(preselectedProductId = null) {
  const modal = document.createElement('div');
  modal.id = 'new-purchase-modal';
  modal.className = 'fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4';

  modal.innerHTML = `
    <div class="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
      <div class="flex items-center justify-between border-b pb-3 border-slate-100">
        <div>
          <h3 class="text-lg font-bold text-slate-900">New Inward Purchase Consignment (GRN)</h3>
          <p class="text-xs text-slate-500">Inward batch lot will automatically update current inventory.</p>
        </div>
        <button onclick="document.getElementById('new-purchase-modal').remove()" class="text-slate-400 hover:text-slate-600">
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>

      <form id="new-purchase-form" onsubmit="submitNewPurchase(event)" class="space-y-3 text-xs">
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Select Supplier *</label>
            <select required id="grn-supplier" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm">
              ${state.suppliers.map(s => `<option value="${s.id}">${s.business_name}</option>`).join('')}
            </select>
          </div>
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Supplier Invoice #</label>
            <input id="grn-invoice" type="text" placeholder="e.g. INV-2026-99" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm">
          </div>
        </div>

        <div class="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
          <h4 class="font-bold text-slate-800 text-xs uppercase">Consignment Item Lot</h4>
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Product SKU *</label>
            <select required id="grn-product" class="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm">
              ${state.products.map(p => `
                <option value="${p.id}" ${p.id === preselectedProductId ? 'selected' : ''}>${p.name} (Stock: ${p.current_stock})</option>
              `).join('')}
            </select>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block font-semibold text-slate-700 mb-1">Batch #</label>
              <input id="grn-batch" type="text" value="B-${Date.now().toString().slice(-4)}" class="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm">
            </div>
            <div>
              <label class="block font-semibold text-slate-700 mb-1">Expiry Date</label>
              <input id="grn-expiry" type="date" value="2027-01-15" class="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm">
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block font-semibold text-slate-700 mb-1">Inward Quantity *</label>
              <input required id="grn-qty" type="number" min="1" value="20" class="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm font-bold">
            </div>
            <div>
              <label class="block font-semibold text-slate-700 mb-1">Unit Cost (₹) *</label>
              <input required id="grn-cost" type="number" step="0.5" value="45" class="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm font-bold">
            </div>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Amount Paid Immediately (₹)</label>
            <input id="grn-paid" type="number" step="0.5" value="500" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm">
          </div>
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Purchase Date</label>
            <input id="grn-date" type="date" value="${new Date().toISOString().split('T')[0]}" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm">
          </div>
        </div>

        <div class="pt-3 flex gap-2">
          <button type="button" onclick="document.getElementById('new-purchase-modal').remove()" class="flex-1 py-2.5 bg-slate-100 text-slate-700 rounded-lg font-bold">Cancel</button>
          <button type="submit" class="flex-1 py-2.5 bg-primary text-white rounded-lg font-bold">Post Inward GRN</button>
        </div>
      </form>
    </div>
  `;

  document.body.appendChild(modal);
}

async function submitNewPurchase(e) {
  e.preventDefault();
  const qty = parseFloat(document.getElementById('grn-qty').value);
  const cost = parseFloat(document.getElementById('grn-cost').value);
  const paid = parseFloat(document.getElementById('grn-paid').value) || 0;

  const payload = {
    supplier_id: parseInt(document.getElementById('grn-supplier').value),
    supplier_invoice_number: document.getElementById('grn-invoice').value || null,
    purchase_date: document.getElementById('grn-date').value,
    discount_amount: 0.0,
    tax_amount: 0.0,
    additional_charges: 0.0,
    amount_paid: paid,
    items: [{
      product_id: parseInt(document.getElementById('grn-product').value),
      batch_number: document.getElementById('grn-batch').value || null,
      expiry_date: document.getElementById('grn-expiry').value || null,
      quantity: qty,
      unit_cost: cost,
      discount_percent: 0.0,
      tax_percent: 0.0
    }]
  };

  try {
    const res = await apiFetch('/purchases', {
      method: 'POST',
      body: JSON.stringify(payload)
    });

    showToast(`Inward GRN #${res.id} Posted! Stock updated.`, 'success');
    document.getElementById('new-purchase-modal')?.remove();
    loadAppData();
    if (state.currentRoute === 'purchases-inward-goods') {
      renderPurchasesView(document.getElementById('custom-subview'));
    }
  } catch (err) {
    showToast(`Error: ${err.message}`, 'error');
  }
}

// Add Supplier Modal
function openAddSupplierModal() {
  const modal = document.createElement('div');
  modal.id = 'add-supplier-modal';
  modal.className = 'fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4';

  modal.innerHTML = `
    <div class="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
      <div class="flex items-center justify-between border-b pb-3 border-slate-100">
        <h3 class="text-lg font-bold text-slate-900">Add Supplier / Vendor</h3>
        <button onclick="document.getElementById('add-supplier-modal').remove()" class="text-slate-400 hover:text-slate-600">
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>

      <form onsubmit="submitAddSupplier(event)" class="space-y-3 text-xs">
        <div>
          <label class="block font-semibold text-slate-700 mb-1">Business Name *</label>
          <input required id="supp-name" type="text" placeholder="e.g. Metro Cash & Carry Bangalore" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm">
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Contact Person</label>
            <input id="supp-contact" type="text" placeholder="e.g. Suresh Kumar" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm">
          </div>
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Phone *</label>
            <input required id="supp-phone" type="text" placeholder="+91 98765 00000" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm">
          </div>
        </div>
        <div>
          <label class="block font-semibold text-slate-700 mb-1">Opening Balance (₹)</label>
          <input id="supp-balance" type="number" value="0" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm">
        </div>
        <div class="pt-3 flex gap-2">
          <button type="button" onclick="document.getElementById('add-supplier-modal').remove()" class="flex-1 py-2.5 bg-slate-100 text-slate-700 rounded-lg font-bold">Cancel</button>
          <button type="submit" class="flex-1 py-2.5 bg-primary text-white rounded-lg font-bold">Save Vendor</button>
        </div>
      </form>
    </div>
  `;

  document.body.appendChild(modal);
}

async function submitAddSupplier(e) {
  e.preventDefault();
  const payload = {
    business_name: document.getElementById('supp-name').value,
    contact_person: document.getElementById('supp-contact').value || null,
    phone: document.getElementById('supp-phone').value,
    opening_balance: parseFloat(document.getElementById('supp-balance').value) || 0
  };

  try {
    const res = await apiFetch('/suppliers', {
      method: 'POST',
      body: JSON.stringify(payload)
    });

    showToast(`Supplier "${res.business_name}" added!`, 'success');
    document.getElementById('add-supplier-modal')?.remove();
    loadAppData();
    if (state.currentRoute === 'suppliers-ledgers') {
      renderSuppliersView(document.getElementById('custom-subview'));
    }
  } catch (err) {
    showToast(`Error: ${err.message}`, 'error');
  }
}

// Supplier Payment Payout Modal
function openSupplierPaymentModal(supplierId, supplierName) {
  const modal = document.createElement('div');
  modal.id = 'supplier-payment-modal';
  modal.className = 'fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4';

  modal.innerHTML = `
    <div class="bg-white rounded-2xl max-w-sm w-full p-6 shadow-2xl space-y-4">
      <div class="flex items-center justify-between border-b pb-3 border-slate-100">
        <div>
          <h3 class="text-lg font-bold text-slate-900">Record Payout</h3>
          <p class="text-xs text-slate-500">${supplierName}</p>
        </div>
        <button onclick="document.getElementById('supplier-payment-modal').remove()" class="text-slate-400 hover:text-slate-600">
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>

      <form onsubmit="submitSupplierPayment(event, ${supplierId})" class="space-y-3 text-xs">
        <div>
          <label class="block font-semibold text-slate-700 mb-1">Payment Amount (₹) *</label>
          <input required id="payout-amount" type="number" step="0.5" placeholder="500" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm font-bold">
        </div>
        <div>
          <label class="block font-semibold text-slate-700 mb-1">Payment Method</label>
          <select id="payout-method" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm">
            <option value="bank_transfer">Bank Transfer / NEFT</option>
            <option value="upi">UPI / GPay / PhonePe</option>
            <option value="cash">Cash Counter</option>
            <option value="cheque">Cheque</option>
          </select>
        </div>
        <div>
          <label class="block font-semibold text-slate-700 mb-1">Reference / UTR #</label>
          <input id="payout-ref" type="text" placeholder="e.g. UTR-982189021" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm">
        </div>
        <div class="pt-3 flex gap-2">
          <button type="button" onclick="document.getElementById('supplier-payment-modal').remove()" class="flex-1 py-2.5 bg-slate-100 text-slate-700 rounded-lg font-bold">Cancel</button>
          <button type="submit" class="flex-1 py-2.5 bg-primary text-white rounded-lg font-bold">Confirm Payout</button>
        </div>
      </form>
    </div>
  `;

  document.body.appendChild(modal);
}

async function submitSupplierPayment(e, supplierId) {
  e.preventDefault();
  const payload = {
    supplier_id: supplierId,
    amount: parseFloat(document.getElementById('payout-amount').value),
    payment_method: document.getElementById('payout-method').value,
    reference: document.getElementById('payout-ref').value || null,
    payment_date: new Date().toISOString().split('T')[0]
  };

  try {
    await apiFetch(`/suppliers/${supplierId}/payments`, {
      method: 'POST',
      body: JSON.stringify(payload)
    });

    showToast('Payment recorded successfully!', 'success');
    document.getElementById('supplier-payment-modal')?.remove();
    loadAppData();
    if (state.currentRoute === 'suppliers-ledgers') {
      renderSuppliersView(document.getElementById('custom-subview'));
    }
  } catch (err) {
    showToast(`Error: ${err.message}`, 'error');
  }
}

// Record Damage Goods Modal
function openRecordDamageModal() {
  const modal = document.createElement('div');
  modal.id = 'damage-modal';
  modal.className = 'fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4';

  modal.innerHTML = `
    <div class="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
      <div class="flex items-center justify-between border-b pb-3 border-slate-100">
        <h3 class="text-lg font-bold text-red-600 flex items-center gap-2">
          <span class="material-symbols-outlined">delete</span>
          Record Damaged Goods
        </h3>
        <button onclick="document.getElementById('damage-modal').remove()" class="text-slate-400 hover:text-slate-600">
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>

      <form onsubmit="submitRecordDamage(event)" class="space-y-3 text-xs">
        <div>
          <label class="block font-semibold text-slate-700 mb-1">Select Product SKU *</label>
          <select required id="dmg-product" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm">
            ${state.products.map(p => `<option value="${p.id}">${p.name} (Stock: ${p.current_stock})</option>`).join('')}
          </select>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Quantity *</label>
            <input required id="dmg-qty" type="number" min="1" value="1" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm font-bold">
          </div>
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Damage Date</label>
            <input id="dmg-date" type="date" value="${new Date().toISOString().split('T')[0]}" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm">
          </div>
        </div>
        <div>
          <label class="block font-semibold text-slate-700 mb-1">Reason for Damage *</label>
          <select id="dmg-reason" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm">
            <option value="expired">Expired on Shelf</option>
            <option value="broken">Broken / Packaging Crushed</option>
            <option value="leakage">Liquid Leakage / Puncture</option>
            <option value="pest">Pest / Rodent Infestation</option>
            <option value="transit">Damaged in Transit / GRN Unloading</option>
          </select>
        </div>
        <div class="pt-3 flex gap-2">
          <button type="button" onclick="document.getElementById('damage-modal').remove()" class="flex-1 py-2.5 bg-slate-100 text-slate-700 rounded-lg font-bold">Cancel</button>
          <button type="submit" class="flex-1 py-2.5 bg-red-600 text-white rounded-lg font-bold">Write-Off Stock</button>
        </div>
      </form>
    </div>
  `;

  document.body.appendChild(modal);
}

async function submitRecordDamage(e) {
  e.preventDefault();
  const payload = {
    product_id: parseInt(document.getElementById('dmg-product').value),
    quantity: parseFloat(document.getElementById('dmg-qty').value),
    damage_date: document.getElementById('dmg-date').value,
    reason: document.getElementById('dmg-reason').value
  };

  try {
    const res = await apiFetch('/damaged-goods', {
      method: 'POST',
      body: JSON.stringify(payload)
    });

    showToast(`Recorded damage for SKU #${res.product_id}!`, 'success');
    document.getElementById('damage-modal')?.remove();
    loadAppData();
    if (state.currentRoute === 'damaged-goods') {
      renderDamagedGoodsView(document.getElementById('custom-subview'));
    }
  } catch (err) {
    showToast(`Error: ${err.message}`, 'error');
  }
}

// Quick Scan & Barcode Lookup Modal (F2)
function openBarcodeScanModal() {
  const modal = document.createElement('div');
  modal.id = 'scan-modal';
  modal.className = 'fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4';

  modal.innerHTML = `
    <div class="bg-white rounded-2xl max-w-sm w-full p-6 shadow-2xl space-y-4">
      <div class="flex items-center justify-between border-b pb-3 border-slate-100">
        <h3 class="text-lg font-bold text-slate-900 flex items-center gap-2">
          <span class="material-symbols-outlined text-secondary">qr_code_scanner</span>
          Barcode Quick Lookup
        </h3>
        <button onclick="document.getElementById('scan-modal').remove()" class="text-slate-400 hover:text-slate-600">
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>

      <div class="space-y-3">
        <div class="relative">
          <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">barcode</span>
          <input autofocus id="scan-barcode-input" oninput="handleBarcodeQuery(this.value)" type="text" placeholder="Scan or enter barcode / SKU..." class="w-full pl-9 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary">
        </div>

        <div id="scan-result" class="p-3 bg-slate-50 rounded-xl min-h-[100px] flex items-center justify-center text-xs text-slate-400">
          Scan a barcode or enter SKU code above...
        </div>
      </div>
    </div>
  `;

  document.body.appendChild(modal);
}

function handleBarcodeQuery(val) {
  const q = val.trim().toLowerCase();
  const resContainer = document.getElementById('scan-result');
  if (!resContainer) return;

  if (!q) {
    resContainer.innerHTML = 'Scan a barcode or enter SKU code above...';
    return;
  }

  const match = state.products.find(p => 
    (p.barcode && p.barcode.toLowerCase() === q) || 
    (p.sku && p.sku.toLowerCase() === q) || 
    p.name.toLowerCase().includes(q)
  );

  if (match) {
    resContainer.innerHTML = `
      <div class="w-full space-y-2 text-left">
        <div class="flex justify-between items-start">
          <h4 class="font-bold text-slate-900 text-sm">${match.name}</h4>
          <span class="font-bold text-primary text-base tabular-nums">₹${match.selling_price}</span>
        </div>
        <p class="text-xs text-slate-500">Barcode: ${match.barcode || '—'} • SKU: ${match.sku || '—'}</p>
        <p class="text-xs text-emerald-700 font-semibold">Available Stock: ${match.current_stock} ${match.unit}</p>
        <button onclick="addToCart(${match.id}); document.getElementById('scan-modal').remove(); navigateTo('sales-pos-terminal');" class="w-full mt-2 py-2 bg-primary hover:bg-primary-container text-white text-xs font-bold rounded-lg transition flex items-center justify-center gap-1">
          <span class="material-symbols-outlined text-sm">add_shopping_cart</span>
          Add to Bill Register
        </button>
      </div>
    `;
  } else {
    resContainer.innerHTML = `<span class="text-red-500">No SKU found matching "${val}"</span>`;
  }
}

// Gemini AI Copilot Drawer & Loss Intelligence
function toggleGeminiDrawer() {
  let drawer = document.getElementById('gemini-copilot-drawer');
  if (drawer) {
    drawer.remove();
    return;
  }

  drawer = document.createElement('div');
  drawer.id = 'gemini-copilot-drawer';
  drawer.className = 'fixed right-0 top-0 bottom-0 w-96 bg-white shadow-2xl z-50 flex flex-col border-l border-slate-200 transform transition-transform duration-300';

  drawer.innerHTML = `
    <div class="p-4 bg-gradient-to-r from-blue-600 to-indigo-700 text-white flex items-center justify-between">
      <div class="flex items-center gap-2">
        <span class="material-symbols-outlined text-amber-300">smart_toy</span>
        <div>
          <h3 class="font-bold text-sm">Gemini AI Retail Copilot</h3>
          <p class="text-[10px] text-blue-200">Loss Intelligence & Inventory Advisory</p>
        </div>
      </div>
      <button onclick="toggleGeminiDrawer()" class="text-blue-100 hover:text-white">
        <span class="material-symbols-outlined">close</span>
      </button>
    </div>

    <!-- Quick Action Chips -->
    <div class="p-3 bg-slate-50 border-b border-slate-100 flex flex-wrap gap-1.5 text-[11px]">
      <button onclick="sendGeminiPrompt('Analyze store loss and risk factors.')" class="px-2 py-1 bg-white hover:bg-blue-50 text-blue-700 border border-blue-200 rounded-full font-medium transition">
        📉 Loss Diagnosis
      </button>
      <button onclick="sendGeminiPrompt('Which items need immediate clearance discounts?')" class="px-2 py-1 bg-white hover:bg-blue-50 text-blue-700 border border-blue-200 rounded-full font-medium transition">
        ⏳ Clearance Plan
      </button>
      <button onclick="sendGeminiPrompt('Recommend reorder quantities for low stock items.')" class="px-2 py-1 bg-white hover:bg-blue-50 text-blue-700 border border-blue-200 rounded-full font-medium transition">
        📦 Reorder Advice
      </button>
    </div>

    <!-- Chat Messages -->
    <div id="gemini-chat-msgs" class="flex-1 p-4 overflow-y-auto space-y-3 text-xs">
      <div class="bg-blue-50 p-3 rounded-2xl rounded-tl-none text-slate-800 space-y-1">
        <p class="font-semibold text-blue-900">Namaste Rajesh! 👋</p>
        <p>I am your DukanIQ Retail Copilot. I analyze your sales, batch expiry queues, and damaged stock to help you stop leakages and protect your store margins.</p>
        <p class="text-[10px] text-slate-500 pt-1">Ask me anything about your stock or click a prompt above!</p>
      </div>
    </div>

    <!-- Input -->
    <div class="p-3 border-t border-slate-200 bg-white">
      <form onsubmit="handleGeminiSubmit(event)" class="flex gap-2">
        <input id="gemini-input" type="text" placeholder="Ask Gemini Copilot..." class="flex-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-blue-600">
        <button type="submit" class="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg">
          <span class="material-symbols-outlined text-sm">send</span>
        </button>
      </form>
    </div>
  `;

  document.body.appendChild(drawer);
}

async function sendGeminiPrompt(text) {
  const container = document.getElementById('gemini-chat-msgs');
  if (!container) return;

  // Add User msg
  const userMsg = document.createElement('div');
  userMsg.className = 'bg-slate-800 text-white p-3 rounded-2xl rounded-tr-none text-xs ml-8';
  userMsg.textContent = text;
  container.appendChild(userMsg);

  // Add Thinking bot msg
  const botMsg = document.createElement('div');
  botMsg.className = 'bg-blue-50 text-slate-800 p-3 rounded-2xl rounded-tl-none text-xs mr-8 flex items-center gap-2';
  botMsg.innerHTML = '<span class="material-symbols-outlined animate-spin text-sm text-blue-600">sync</span> Analyzing store data...';
  container.appendChild(botMsg);
  container.scrollTop = container.scrollHeight;

  try {
    const res = await apiFetch('/gemini/chat', {
      method: 'POST',
      body: JSON.stringify({ prompt: text, include_context: true })
    });

    botMsg.innerHTML = `<div class="whitespace-pre-line leading-relaxed">${res.reply || res.analysis || 'Analysis complete.'}</div>`;
  } catch (err) {
    botMsg.innerHTML = `<span class="text-red-600">Error connecting to Gemini API: ${err.message}</span>`;
  }

  container.scrollTop = container.scrollHeight;
}

function handleGeminiSubmit(e) {
  e.preventDefault();
  const input = document.getElementById('gemini-input');
  if (!input || !input.value.trim()) return;
  const text = input.value.trim();
  input.value = '';
  sendGeminiPrompt(text);
}

// User Profile Switcher Dropdown
function toggleUserDropdown() {
  let menu = document.getElementById('user-switch-menu');
  if (menu) {
    menu.remove();
    return;
  }

  const profileEl = document.querySelector('header .flex.items-center.gap-space-sm');
  if (!profileEl) return;

  menu = document.createElement('div');
  menu.id = 'user-switch-menu';
  menu.className = 'absolute right-6 top-14 w-60 bg-white rounded-xl shadow-xl border border-slate-100 py-2 z-50 text-xs';

  menu.innerHTML = `
    <div class="px-3 py-1.5 border-b border-slate-100 font-semibold text-slate-400 uppercase tracking-wider text-[10px]">
      Switch Store Role
    </div>
    ${DEMO_USERS.map(u => `
      <button onclick="switchUser('${u.email}', '${u.password}')" class="w-full text-left px-3 py-2 hover:bg-slate-50 flex items-center justify-between transition">
        <div>
          <p class="font-bold text-slate-900">${u.name}</p>
          <p class="text-[10px] text-slate-500">${u.role}</p>
        </div>
        ${state.user && state.user.email === u.email ? '<span class="material-symbols-outlined text-sm text-emerald-600">check</span>' : ''}
      </button>
    `).join('')}
  `;

  document.body.appendChild(menu);

  // Close when clicked outside
  setTimeout(() => {
    window.addEventListener('click', function closeMenu(e) {
      if (!menu.contains(e.target) && !profileEl.contains(e.target)) {
        menu.remove();
        window.removeEventListener('click', closeMenu);
      }
    });
  }, 10);
}

async function switchUser(email, password) {
  document.getElementById('user-switch-menu')?.remove();
  const ok = await autoLogin(email, password);
  if (ok) {
    showToast(`Switched account to ${state.user.name} (${state.user.role})`, 'success');
    renderView(state.currentRoute);
  }
}

// Attach Event Listeners to static buttons from index.html
function attachGlobalListeners() {
  // Top header buttons
  const headerBtns = document.querySelectorAll('header button');
  headerBtns.forEach(btn => {
    const text = btn.textContent.trim().toLowerCase();
    if (text.includes('new sale')) {
      btn.onclick = () => navigateTo('sales-pos-terminal');
    } else if (text.includes('new purchase')) {
      btn.onclick = () => openNewPurchaseModal();
    } else if (text.includes('quick scan')) {
      btn.onclick = () => openBarcodeScanModal();
    } else if (btn.querySelector('.material-symbols-outlined')?.textContent.includes('notifications')) {
      btn.onclick = () => {
        const s = state.dashboardStats;
        showToast(`Store Alerts: ${s?.low_stock_count || 0} Low Stock • ${s?.expiring_soon_count || 0} Expiring Soon`, 'info');
      };
    }
  });

  // User Profile click
  const profileContainer = document.querySelector('header .flex.items-center.gap-space-sm');
  if (profileContainer) {
    profileContainer.style.cursor = 'pointer';
    profileContainer.onclick = toggleUserDropdown;
  }

  // Header Search Input (Ctrl+K)
  const headerSearch = document.querySelector('header input[type="text"]');
  if (headerSearch) {
    headerSearch.addEventListener('click', () => openBarcodeScanModal());
  }

  // Fast action bar shortcut buttons (Quick Bill, New GRN, Scan, Audit Ledger, Z-Report)
  const fastBtns = document.querySelectorAll('.bg-surface-card .flex-wrap.items-center.gap-space-xs button');
  fastBtns.forEach(btn => {
    const text = btn.textContent.trim().toLowerCase();
    if (text.includes('quick bill')) {
      btn.onclick = () => navigateTo('sales-pos-terminal');
    } else if (text.includes('new grn')) {
      btn.onclick = () => openNewPurchaseModal();
    } else if (text.includes('scan')) {
      btn.onclick = () => openBarcodeScanModal();
    } else if (text.includes('audit ledger')) {
      btn.onclick = () => navigateTo('batch-inventory-ledger');
    } else if (text.includes('z-report')) {
      btn.onclick = () => navigateTo('reports-analytics');
    }
  });

  // Keyboard Shortcuts: F1 (POS), F2 (Scan), F3 (GRN), Ctrl+K (Search)
  window.addEventListener('keydown', (e) => {
    if (e.key === 'F1') {
      e.preventDefault();
      navigateTo('sales-pos-terminal');
    } else if (e.key === 'F2') {
      e.preventDefault();
      openBarcodeScanModal();
    } else if (e.key === 'F3') {
      e.preventDefault();
      openNewPurchaseModal();
    } else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      openBarcodeScanModal();
    }
  });

  // Floating Gemini AI Button at bottom-right
  const geminiBtn = document.createElement('button');
  geminiBtn.id = 'floating-gemini-btn';
  geminiBtn.className = 'fixed bottom-6 right-6 w-14 h-14 rounded-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-xl flex items-center justify-center hover:scale-105 active:scale-95 transition-all z-40';
  geminiBtn.title = 'Open Gemini AI Copilot';
  geminiBtn.innerHTML = '<span class="material-symbols-outlined text-2xl">smart_toy</span>';
  geminiBtn.onclick = toggleGeminiDrawer;
  document.body.appendChild(geminiBtn);
}

// Wrap existing Dashboard in #dashboard-main-view container so we can show/hide cleanly
function prepareDashboardDOM() {
  const main = document.querySelector('main');
  if (!main) return;

  const firstDiv = main.querySelector('.flex.flex-col.w-full');
  if (firstDiv && !firstDiv.id) {
    firstDiv.id = 'dashboard-main-view';
  }
}

// Initialize on DOM load
window.addEventListener('DOMContentLoaded', async () => {
  prepareDashboardDOM();
  await autoLogin();
  await loadAppData();
  initNavigation();
  attachGlobalListeners();
});
