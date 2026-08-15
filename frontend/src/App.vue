<template>
  <!-- ═══════════════════════════════════════════════════════ -->
  <!-- CÀN KHÔN LINH THẠCH CÁC v3.0 — GIAO DIỆN TU TIÊN     -->
  <!-- ═══════════════════════════════════════════════════════ -->

  <!-- PERSISTENT XIANXIA CELESTIAL BACKDROP -->
  <div class="xianxia-backdrop">
    <div class="sun-aura-glow"></div>
    <div class="mountain-layer far-mountains">
      <svg viewBox="0 0 1440 320" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
        <path fill="#7ba3c4" fill-opacity="0.45" d="M0,160 Q120,80 240,150 T480,100 T720,170 T960,90 T1200,160 T1440,110 L1440,320 L0,320 Z"></path>
      </svg>
    </div>
    <div class="mountain-layer mid-mountains">
      <svg viewBox="0 0 1440 320" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
        <path fill="#4b759a" fill-opacity="0.65" d="M0,210 L60,160 L90,185 L140,130 L180,175 L250,110 L310,180 L380,135 L440,200 L510,120 L580,190 L670,140 L740,210 L820,125 L900,200 L980,130 L1060,190 L1150,140 L1230,210 L1320,150 L1440,190 L1440,320 L0,320 Z"></path>
      </svg>
    </div>
    <div class="mountain-layer near-mountains">
      <svg viewBox="0 0 1440 320" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
        <path fill="#2c4660" fill-opacity="0.9" d="M0,260 L40,210 L80,240 L130,170 L180,230 L230,190 L290,270 L350,195 L400,245 L480,175 L540,255 L610,190 L680,275 L760,185 L820,245 L890,170 L950,235 L1020,180 L1100,265 L1180,190 L1250,250 L1340,195 L1440,240 L1440,320 L0,320 Z"></path>
      </svg>
    </div>
    <div class="sea-of-clouds-wrapper">
      <div class="sea-of-clouds wave-1"></div>
      <div class="sea-of-clouds wave-2"></div>
    </div>
    <div class="floating-clouds">
      <div class="cloud-cluster cloud-1"></div>
      <div class="cloud-cluster cloud-2"></div>
      <div class="cloud-cluster cloud-3"></div>
    </div>
    <div class="spirit-particle-field">
      <div v-for="n in 25" :key="n" :class="'spirit-particle p-' + n"></div>
    </div>
  </div>

  <!-- LOGIN SCREEN -->
  <div v-if="!isLoggedIn" class="login-realm">
    <div class="login-card">
      <div class="login-header">
        <div class="dao-symbol">☯</div>
        <h1 class="title-calligraphy">Càn Khôn Linh Thạch Các</h1>
        <p class="subtitle-glow">Quản Lý Chi Tiêu AI — Phong Cách Tu Tiên</p>
      </div>

      <div v-if="authMode === 'login'" class="auth-form">
        <h2 class="form-title">🔮 Xác Thực Đạo Tâm</h2>
        <div class="input-group-xianxia">
          <label>📧 Linh Bưu (Email)</label>
          <input v-model="authForm.email" type="email" placeholder="dao.huu@tongmon.com" @keyup.enter="doLogin" />
        </div>
        <div class="input-group-xianxia">
          <label>🔑 Khẩu Quyết (Mật khẩu)</label>
          <input v-model="authForm.password" type="password" placeholder="••••••" @keyup.enter="doLogin" />
        </div>
        <button class="btn-jade" @click="doLogin" :disabled="loading">
          {{ loading ? '⏳ Đang xác thực...' : '⚡ Khai Mở Thần Thức' }}
        </button>
        <p class="auth-switch" @click="authMode = 'register'">Chưa có Đạo Tâm? <span>Đăng ký ngay</span></p>
      </div>

      <div v-else class="auth-form">
        <h2 class="form-title">✨ Khai Mở Đạo Tâm Mới</h2>
        <div class="input-group-xianxia">
          <label>👤 Đạo Hiệu (Họ tên)</label>
          <input v-model="authForm.full_name" type="text" placeholder="Ký Chủ" />
        </div>
        <div class="input-group-xianxia">
          <label>📧 Linh Bưu (Email)</label>
          <input v-model="authForm.email" type="email" placeholder="dao.huu@tongmon.com" />
        </div>
        <div class="input-group-xianxia">
          <label>🔑 Khẩu Quyết (Mật khẩu)</label>
          <input v-model="authForm.password" type="password" placeholder="••••••" />
        </div>
        <button class="btn-jade" @click="doRegister" :disabled="loading">
          {{ loading ? '⏳ Đang khai mở...' : '🌟 Nhập Môn Tông Phái' }}
        </button>
        <p class="auth-switch" @click="authMode = 'login'">Đã có Đạo Tâm? <span>Đăng nhập</span></p>
      </div>
      <div v-if="errorMsg" class="error-banner">🔥 {{ errorMsg }}</div>
    </div>
  </div>

  <!-- MAIN APP -->
  <div v-else class="app-realm">
    <!-- HEADER -->
    <header class="realm-header">
      <div class="header-inner">
        <!-- REQUIREMENT 4: Click Title -> Switch to Dashboard -->
        <div class="header-left clickable-brand" @click="switchTab('dashboard')" title="Trở về Đạo Đường Tổng Quan">
          <span class="header-symbol">☯</span>
          <h1 class="header-title">Càn Khôn Linh Thạch Các</h1>
          <span class="version-badge">v3.0</span>
        </div>
        <div class="header-right">
          <!-- REQUIREMENT 5 & 6: User Badge click -> Open Account Management -->
          <button class="user-badge-btn" @click="openProfileModal" title="Quản Lý Đạo Tâm (Tài Khoản)">
            🧙 {{ userName }}
          </button>
          <button class="btn-logout" @click="doLogout">🚪 Hạ Sơn</button>
        </div>
      </div>
    </header>

    <!-- TAB NAVIGATION -->
    <nav class="tab-nav">
      <div class="tab-nav-inner">
        <button v-for="tab in tabs" :key="tab.id"
                :class="['tab-btn', { active: activeTab === tab.id }]"
                @click="switchTab(tab.id)">
          <span class="tab-icon">{{ tab.icon }}</span>
          <span class="tab-label">{{ tab.label }}</span>
        </button>
      </div>
    </nav>

    <!-- CONTENT AREA -->
    <main class="realm-content">
      <!-- ═══════ TAB 1: DASHBOARD ═══════ -->
      <section v-if="activeTab === 'dashboard'" class="tab-panel">
        <h2 class="section-title">📊 Đạo Đường Tổng Quan</h2>

        <!-- Metrics Cards -->
        <div class="metrics-grid">
          <div class="metric-card jade">
            <div class="metric-icon">💰</div>
            <div class="metric-info">
              <span class="metric-label">Thu Nhập Linh Mạch</span>
              <span class="metric-value">{{ formatVND(summary.total_income) }}</span>
            </div>
          </div>
          <div class="metric-card crimson">
            <div class="metric-icon">🔥</div>
            <div class="metric-info">
              <span class="metric-label">Tiêu Hao Linh Thạch</span>
              <span class="metric-value">{{ formatVND(summary.total_expense) }}</span>
            </div>
          </div>
          <div class="metric-card gold">
            <div class="metric-icon">⚖️</div>
            <div class="metric-info">
              <span class="metric-label">Tiết Kiệm Thuần</span>
              <span class="metric-value" :class="summary.net_savings >= 0 ? 'positive' : 'negative'">
                {{ formatVND(summary.net_savings) }}
              </span>
            </div>
          </div>
          <div class="metric-card purple">
            <div class="metric-icon">👛</div>
            <div class="metric-info">
              <span class="metric-label">Tổng Túi Càn Khôn</span>
              <span class="metric-value">{{ formatVND(summary.total_balance) }}</span>
            </div>
          </div>
        </div>

        <!-- Budget Alerts -->
        <div v-if="budgetAlerts.length" class="alerts-section">
          <h3 class="sub-title">⚠️ Cảnh Báo Tâm Ma Chi Tiêu</h3>
          <div v-for="alert in budgetAlerts" :key="alert.category"
               :class="['alert-card', alert.level === 'DANGER' ? 'danger' : 'warning']">
            <span class="alert-icon">{{ alert.icon }}</span>
            <span class="alert-msg">{{ alert.message }}</span>
            <span class="alert-pct">{{ alert.percent }}%</span>
          </div>
        </div>

        <!-- Dashboard Charts Row -->
        <div class="dashboard-charts-row">
          <div class="chart-card" v-if="summary.expense_by_category && summary.expense_by_category.length">
            <ChartComponent
              type="doughnut"
              :chart-data="dashboardDoughnutData"
              title="🥧 Phân Bổ Chi Tiêu Tháng Này"
            />
          </div>
          <div class="chart-card" v-if="trendData.trend && trendData.trend.length">
            <ChartComponent
              type="bar"
              :chart-data="dashboardBarData"
              title="📊 Thu/Chi 6 Tháng Gần Đây"
            />
          </div>
        </div>

        <!-- AI Saving Tips -->
        <div class="saving-tips-section">
          <div class="saving-tips-header">
            <h3 class="sub-title">🔮 Khai Thị Tiết Kiệm AI</h3>
            <button class="btn-jade-sm" @click="loadSavingTips" :disabled="loadingTips">
              {{ loadingTips ? '🔮 Đang cầu tiên...' : '✨ Nhận Khai Thị' }}
            </button>
          </div>
          <div v-if="savingTips" class="saving-tips-card">
            <div class="tips-meta">
              <span>📅 Tháng: {{ savingTips.month_year }}</span>
              <span>📈 Tỷ lệ tiết kiệm: <strong :class="savingTips.savings_rate >= 20 ? 'positive' : 'negative'">{{ savingTips.savings_rate }}%</strong></span>
            </div>
            <div class="tips-content" v-html="formatChatText(savingTips.tips)"></div>
          </div>
        </div>

        <!-- Recent Transactions -->
        <h3 class="sub-title">📜 Giao Dịch Linh Thạch Gần Đây</h3>
        <div class="table-scroll">
          <table class="xianxia-table">
            <thead>
              <tr>
                <th>Ngày</th>
                <th>Danh Mục</th>
                <th>Ghi Chú</th>
                <th>Ví</th>
                <th>Số Tiền</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="txn in transactions.slice(0, 10)" :key="txn.id">
                <td>{{ txn.transaction_date }}</td>
                <td><span class="cat-badge">{{ txn.category_icon }} {{ txn.category_name }}</span></td>
                <td>{{ txn.note || '—' }}</td>
                <td>{{ txn.wallet_name }}</td>
                <td :class="txn.transaction_type === 'INCOME' ? 'amt-income' : 'amt-expense'">
                  {{ txn.transaction_type === 'INCOME' ? '+' : '-' }}{{ formatVND(txn.amount) }}
                </td>
              </tr>
              <tr v-if="!transactions.length">
                <td colspan="5" class="empty-row">Chưa có giao dịch nào...</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Expense by Category (bar breakdown) -->
        <div v-if="summary.expense_by_category && summary.expense_by_category.length" class="category-breakdown">
          <h3 class="sub-title">📈 Phân Bổ Tiêu Hao Theo Danh Mục</h3>
          <div class="cat-bars">
            <div v-for="cat in summary.expense_by_category" :key="cat.category_name" class="cat-bar-row">
              <span class="cat-bar-label">{{ cat.icon }} {{ cat.category_name }}</span>
              <div class="cat-bar-track">
                <div class="cat-bar-fill"
                     :style="{ width: Math.min(100, (cat.total / maxCategoryExpense * 100)) + '%' }"></div>
              </div>
              <span class="cat-bar-value">{{ formatVND(cat.total) }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- ═══════ TAB 2: TRANSACTIONS ═══════ -->
      <section v-if="activeTab === 'transactions'" class="tab-panel">
        <h2 class="section-title">💸 Tàng Kinh Giao Dịch</h2>

        <!-- Add Transaction Form -->
        <div class="form-card">
          <h3 class="sub-title">✍️ Ghi Nhận Giao Dịch Linh Thạch</h3>
          <div class="form-grid">
            <div class="input-group-xianxia">
              <label>Loại Giao Dịch</label>
              <select v-model="txnForm.transaction_type">
                <option value="EXPENSE">🔥 Tiêu Hao (Chi)</option>
                <option value="INCOME">💎 Thu Hoạch (Thu)</option>
              </select>
            </div>
            <div class="input-group-xianxia">
              <label>Số Linh Thạch (VNĐ)</label>
              <input v-model.number="txnForm.amount" type="number" placeholder="0" min="0" />
            </div>
            <div class="input-group-xianxia">
              <label>Túi Càn Khôn (Ví)</label>
              <select v-model="txnForm.wallet_id">
                <option v-for="w in wallets" :key="w.id" :value="w.id">{{ w.wallet_name }}</option>
              </select>
            </div>
            <div class="input-group-xianxia">
              <label>Danh Mục</label>
              <select v-model="txnForm.category_id">
                <option v-for="c in filteredCategories" :key="c.id" :value="c.id">{{ c.icon }} {{ c.category_name }}</option>
              </select>
            </div>
            <div class="input-group-xianxia">
              <label>Ngày Giao Dịch</label>
              <input v-model="txnForm.transaction_date" type="date" />
            </div>
            <div class="input-group-xianxia">
              <label>Ghi Chú</label>
              <input v-model="txnForm.note" type="text" placeholder="Mô tả giao dịch..." />
            </div>
          </div>
          <button class="btn-jade" @click="createTransaction" :disabled="loading" style="margin-top: 16px;">
            {{ loading ? '⏳...' : '⚡ Ghi Nhận Giao Dịch' }}
          </button>
        </div>

        <!-- Transactions Table -->
        <h3 class="sub-title" style="margin-top: 32px;">📜 Lịch Sử Giao Dịch Đầy Đủ</h3>
        <div class="table-scroll">
          <table class="xianxia-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Ngày</th>
                <th>Danh Mục</th>
                <th>Ghi Chú</th>
                <th>Ví</th>
                <th>Số Tiền</th>
                <th>Thao Tác</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(txn, idx) in transactions" :key="txn.id">
                <td>{{ idx + 1 }}</td>
                <td>{{ txn.transaction_date }}</td>
                <td><span class="cat-badge">{{ txn.category_icon }} {{ txn.category_name }}</span></td>
                <td>{{ txn.note || '—' }}</td>
                <td>{{ txn.wallet_name }}</td>
                <td :class="txn.transaction_type === 'INCOME' ? 'amt-income' : 'amt-expense'">
                  {{ txn.transaction_type === 'INCOME' ? '+' : '-' }}{{ formatVND(txn.amount) }}
                </td>
                <td>
                  <button class="btn-sm-danger" @click="deleteTransaction(txn.id)" title="Xóa">🗑️</button>
                </td>
              </tr>
              <tr v-if="!transactions.length">
                <td colspan="7" class="empty-row">Chưa có giao dịch nào...</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- ═══════ TAB 3: WALLETS ═══════ -->
      <section v-if="activeTab === 'wallets'" class="tab-panel">
        <h2 class="section-title">💳 Túi Càn Khôn — Quản Lý Ví</h2>

        <div class="form-card">
          <h3 class="sub-title">➕ Khai Mở Túi Càn Khôn Mới</h3>
          <div class="form-grid">
            <div class="input-group-xianxia">
              <label>Tên Ví</label>
              <input v-model="walletForm.wallet_name" type="text" placeholder="VD: Linh Mạch BIDV" />
            </div>
            <div class="input-group-xianxia">
              <label>Số Dư Ban Đầu (VNĐ)</label>
              <input v-model.number="walletForm.balance" type="number" placeholder="0" />
            </div>
            <div class="input-group-xianxia">
              <label>Loại Ví</label>
              <select v-model="walletForm.wallet_type">
                <option value="cash">💵 Tiền Mặt</option>
                <option value="bank">🏦 Ngân Hàng</option>
                <option value="e-wallet">📱 Ví Điện Tử</option>
              </select>
            </div>
          </div>
          <button class="btn-jade" @click="createWallet" :disabled="loading" style="margin-top: 16px;">
            {{ loading ? '⏳...' : '✨ Khai Mở Ví Mới' }}
          </button>
        </div>

        <!-- Wallet Transfer -->
        <div class="form-card transfer-card">
          <h3 class="sub-title">🔄 Chuyển Linh Thạch Giữa Các Ví</h3>
          <div class="form-grid">
            <div class="input-group-xianxia">
              <label>Từ Ví</label>
              <select v-model="transferForm.from_wallet_id">
                <option :value="null" disabled>— Chọn ví nguồn —</option>
                <option v-for="w in wallets" :key="'from-'+w.id" :value="w.id">
                  {{ walletTypeIcon(w.wallet_type) }} {{ w.wallet_name }} ({{ formatVND(w.balance) }})
                </option>
              </select>
            </div>
            <div class="input-group-xianxia transfer-arrow-col">
              <span class="transfer-arrow">⚡→</span>
            </div>
            <div class="input-group-xianxia">
              <label>Đến Ví</label>
              <select v-model="transferForm.to_wallet_id">
                <option :value="null" disabled>— Chọn ví đích —</option>
                <option v-for="w in wallets" :key="'to-'+w.id" :value="w.id"
                        :disabled="w.id === transferForm.from_wallet_id">
                  {{ walletTypeIcon(w.wallet_type) }} {{ w.wallet_name }}
                </option>
              </select>
            </div>
            <div class="input-group-xianxia">
              <label>Số Tiền Chuyển (VNĐ)</label>
              <input v-model.number="transferForm.amount" type="number" placeholder="0" min="0" />
            </div>
          </div>
          <button class="btn-jade" @click="doTransfer" :disabled="loading || !transferForm.from_wallet_id || !transferForm.to_wallet_id || !transferForm.amount" style="margin-top: 16px;">
            {{ loading ? '⏳ Đang chuyển...' : '🔄 Chuyển Linh Thạch' }}
          </button>
        </div>

        <div class="wallet-grid">
          <div v-for="w in wallets" :key="w.id" class="wallet-card">
            <div class="wallet-card-top">
              <span class="wallet-type-icon">
                {{ walletTypeIcon(w.wallet_type) }}
              </span>
              <button class="btn-sm-danger" @click="deleteWallet(w.id)" title="Hủy ví">✕</button>
            </div>
            <h4 class="wallet-name">{{ w.wallet_name }}</h4>
            <p class="wallet-balance">{{ formatVND(w.balance) }}</p>
            <span class="wallet-type-label">{{ w.wallet_type === 'cash' ? 'Tiền Mặt' : w.wallet_type === 'bank' ? 'Ngân Hàng' : 'Ví Điện Tử' }}</span>
          </div>
          <div v-if="!wallets.length" class="empty-state">Chưa có Túi Càn Khôn nào...</div>
        </div>
      </section>

      <!-- ═══════ TAB 4: CATEGORIES ═══════ -->
      <section v-if="activeTab === 'categories'" class="tab-panel">
        <h2 class="section-title">🏷️ Danh Mục Thu Chi</h2>

        <div class="form-card">
          <h3 class="sub-title">➕ Thêm Danh Mục Mới</h3>
          <div class="form-grid">
            <div class="input-group-xianxia">
              <label>Tên Danh Mục</label>
              <input v-model="catForm.category_name" type="text" placeholder="VD: Linh Dược Y Tế" />
            </div>
            <div class="input-group-xianxia">
              <label>Loại</label>
              <select v-model="catForm.category_type">
                <option value="EXPENSE">🔥 Tiêu Hao (Chi)</option>
                <option value="INCOME">💎 Thu Hoạch (Thu)</option>
              </select>
            </div>
            <div class="input-group-xianxia">
              <label>Icon</label>
              <select v-model="catForm.icon">
                <option v-for="ic in iconOptions" :key="ic" :value="ic">{{ ic }}</option>
              </select>
            </div>
          </div>
          <button class="btn-jade" @click="createCategory" :disabled="loading" style="margin-top: 16px;">
            {{ loading ? '⏳...' : '✨ Khai Mở Danh Mục' }}
          </button>
        </div>

        <div class="categories-split">
          <div class="cat-col">
            <h3 class="sub-title">💎 Thu Hoạch (INCOME)</h3>
            <div v-for="c in incomeCategories" :key="c.id" class="cat-item income">
              <span>{{ c.icon }} {{ c.category_name }}</span>
              <button class="btn-sm-danger" @click="deleteCategory(c.id)">✕</button>
            </div>
            <div v-if="!incomeCategories.length" class="empty-state">Chưa có danh mục thu...</div>
          </div>
          <div class="cat-col">
            <h3 class="sub-title">🔥 Tiêu Hao (EXPENSE)</h3>
            <div v-for="c in expenseCategories" :key="c.id" class="cat-item expense">
              <span>{{ c.icon }} {{ c.category_name }}</span>
              <button class="btn-sm-danger" @click="deleteCategory(c.id)">✕</button>
            </div>
            <div v-if="!expenseCategories.length" class="empty-state">Chưa có danh mục chi...</div>
          </div>
        </div>
      </section>

      <!-- ═══════ TAB 5: OCR INVOICE ═══════ -->
      <section v-if="activeTab === 'ocr'" class="tab-panel">
        <h2 class="section-title">🧾 Linh Nhãn Tầm Bảo — Quét Hóa Đơn AI</h2>

        <div class="form-card">
          <h3 class="sub-title">📸 Tải Lên Hóa Đơn</h3>
          <p class="hint-text">Linh Nhãn AI sẽ tự động trích xuất thông tin từ ảnh hóa đơn / receipt</p>
          <div class="upload-zone" @click="$refs.ocrInput.click()"
               @dragover.prevent @drop.prevent="handleOCRDrop">
            <input ref="ocrInput" type="file" accept="image/*" @change="handleOCRUpload" hidden />
            <div v-if="!ocrPreview" class="upload-placeholder">
              <span class="upload-icon">📷</span>
              <span>Kéo thả hoặc nhấn để chọn ảnh hóa đơn</span>
            </div>
            <img v-else :src="ocrPreview" class="ocr-preview-img" alt="Preview" />
          </div>
          <button class="btn-jade" @click="scanInvoice" :disabled="loading || !ocrFile" style="margin-top: 16px;">
            {{ loading ? '🔮 Linh Nhãn đang phân tích...' : '👁️ Kích Hoạt Linh Nhãn OCR' }}
          </button>
        </div>

        <div v-if="ocrResult" class="ocr-result-card">
          <h3 class="sub-title">✅ Kết Quả Linh Nhãn — Xác Nhận Giao Dịch</h3>
          <p class="hint-text" style="margin-bottom: 16px;">Vui lòng kiểm tra và chỉnh sửa thông tin nếu cần trước khi thêm vào lịch sử thu chi:</p>

          <div class="form-grid">
            <div class="input-group-xianxia">
              <label>🏪 Cửa Hàng / Nội Dung Giao Dịch</label>
              <input v-model="ocrConfirmForm.note" type="text" placeholder="Tên cửa hàng..." />
            </div>
            <div class="input-group-xianxia">
              <label>💰 Số Tiền (VNĐ)</label>
              <input v-model.number="ocrConfirmForm.amount" type="number" placeholder="0" />
            </div>
            <div class="input-group-xianxia">
              <label>📅 Ngày Giao Dịch</label>
              <input v-model="ocrConfirmForm.transaction_date" type="date" />
            </div>
            <div class="input-group-xianxia">
              <label>💳 Túi Càn Khôn (Ví)</label>
              <select v-model="ocrConfirmForm.wallet_id">
                <option v-for="w in wallets" :key="w.id" :value="w.id">{{ w.wallet_name }} ({{ formatVND(w.balance) }})</option>
              </select>
            </div>
            <div class="input-group-xianxia">
              <label>🏷️ Danh Mục Chi</label>
              <select v-model="ocrConfirmForm.category_id">
                <option v-for="c in expenseCategories" :key="c.id" :value="c.id">{{ c.icon }} {{ c.category_name }}</option>
              </select>
            </div>
          </div>

          <div v-if="ocrResult.items && ocrResult.items.length" class="ocr-items" style="margin-top: 16px;">
            <h4>📋 Chi Tiết Sản Phẩm Trích Xuất</h4>
            <table class="xianxia-table">
              <thead><tr><th>Sản Phẩm</th><th>SL</th><th>Đơn Giá</th></tr></thead>
              <tbody>
                <tr v-for="(item, i) in ocrResult.items" :key="i">
                  <td>{{ item.name }}</td>
                  <td>{{ item.quantity || 1 }}</td>
                  <td>{{ formatVND(item.price || 0) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <button class="btn-jade" @click="confirmOCRTransaction" :disabled="loading" style="margin-top: 20px;">
            {{ loading ? '⏳ Đang lưu giao dịch...' : '⚡ Xác Nhận & Thêm Vào Lịch Sử Giao Dịch' }}
          </button>
        </div>
      </section>

      <!-- ═══════ TAB 6: BUDGETS ═══════ -->
      <section v-if="activeTab === 'budgets'" class="tab-panel">
        <h2 class="section-title">🎯 Hạn Mức Tu Luyện — Ngân Sách</h2>

        <div class="form-card">
          <h3 class="sub-title">➕ Thiết Lập Hạn Mức</h3>
          <div class="form-grid">
            <div class="input-group-xianxia">
              <label>Danh Mục Chi</label>
              <select v-model="budgetForm.category_id">
                <option v-for="c in expenseCategories" :key="c.id" :value="c.id">{{ c.icon }} {{ c.category_name }}</option>
              </select>
            </div>
            <div class="input-group-xianxia">
              <label>Hạn Mức (VNĐ)</label>
              <input v-model.number="budgetForm.limit_amount" type="number" placeholder="0" />
            </div>
            <div class="input-group-xianxia">
              <label>Tháng</label>
              <input v-model="budgetForm.month_year" type="month" />
            </div>
          </div>
          <button class="btn-jade" @click="createBudget" :disabled="loading" style="margin-top: 16px;">
            {{ loading ? '⏳...' : '🎯 Thiết Lập Hạn Mức' }}
          </button>
        </div>

        <div class="budget-list">
          <div v-for="b in budgets" :key="b.id" class="budget-card">
            <div class="budget-header">
              <span>{{ b.category_icon }} {{ b.category_name }}</span>
              <button class="btn-sm-danger" @click="deleteBudget(b.id)">✕</button>
            </div>
            <div class="budget-amounts">
              <span>Đã chi: <strong>{{ formatVND(b.spent) }}</strong></span>
              <span>Hạn mức: <strong>{{ formatVND(b.limit_amount) }}</strong></span>
            </div>
            <div class="progress-track">
              <div class="progress-fill"
                   :class="budgetPct(b) >= 100 ? 'danger' : budgetPct(b) >= 80 ? 'warning' : 'safe'"
                   :style="{ width: Math.min(100, budgetPct(b)) + '%' }">
              </div>
            </div>
            <span class="budget-pct" :class="budgetPct(b) >= 100 ? 'pct-danger' : budgetPct(b) >= 80 ? 'pct-warning' : 'pct-safe'">
              {{ budgetPct(b).toFixed(1) }}%
              <span v-if="budgetPct(b) >= 100"> — 🔥 TẨU HỎA NHẬP MA!</span>
              <span v-else-if="budgetPct(b) >= 80"> — ⚠️ Cảnh Báo Tâm Ma</span>
            </span>
          </div>
          <div v-if="!budgets.length" class="empty-state">Chưa thiết lập hạn mức tu luyện nào...</div>
        </div>
      </section>

      <!-- ═══════ TAB 7: STATISTICS ═══════ -->
      <section v-if="activeTab === 'stats'" class="tab-panel">
        <h2 class="section-title">📈 Thiên Cơ Thống Kê — Phân Tích Nâng Cao</h2>

        <!-- Trend Chart -->
        <div class="stats-chart-card" v-if="trendData.trend && trendData.trend.length">
          <ChartComponent
            type="bar"
            :chart-data="trendBarData"
            title="📊 Xu Hướng Thu/Chi 6 Tháng"
          />
        </div>

        <!-- Weekly Chart -->
        <div class="stats-chart-card" v-if="weeklyData.data && weeklyData.data.length">
          <ChartComponent
            type="line"
            :chart-data="weeklyLineData"
            title="📉 Chi Tiêu Theo Tuần (4 Tuần Gần Đây)"
          />
        </div>

        <!-- Doughnut -->
        <div class="stats-chart-card" v-if="summary.expense_by_category && summary.expense_by_category.length">
          <ChartComponent
            type="doughnut"
            :chart-data="statsDoughnutData"
            title="🥧 Tỷ Trọng Chi Tiêu Theo Danh Mục"
          />
        </div>

        <!-- Month Comparison -->
        <div class="compare-section">
          <h3 class="sub-title">🔀 So Sánh Chi Tiêu Hai Tháng</h3>
          <div class="compare-controls">
            <div class="input-group-xianxia">
              <label>Tháng 1</label>
              <input v-model="compareMonth1" type="month" @change="loadCompare" />
            </div>
            <span class="compare-vs">VS</span>
            <div class="input-group-xianxia">
              <label>Tháng 2</label>
              <input v-model="compareMonth2" type="month" @change="loadCompare" />
            </div>
          </div>
          <div v-if="compareData" class="compare-grid">
            <div class="compare-card">
              <h4>📅 {{ compareData.month1.month }}</h4>
              <div class="compare-stat">
                <span>Thu: <strong class="positive">{{ formatVND(compareData.month1.income) }}</strong></span>
                <span>Chi: <strong class="negative">{{ formatVND(compareData.month1.expense) }}</strong></span>
                <span>Tiết kiệm: <strong :class="compareData.month1.savings >= 0 ? 'positive' : 'negative'">{{ formatVND(compareData.month1.savings) }}</strong></span>
              </div>
            </div>
            <div class="compare-delta">
              <div class="delta-item" :class="compareData.delta_income >= 0 ? 'delta-up' : 'delta-down'">
                <span class="delta-arrow">{{ compareData.delta_income >= 0 ? '▲' : '▼' }}</span>
                <span>Thu: {{ formatVND(Math.abs(compareData.delta_income)) }}</span>
              </div>
              <div class="delta-item" :class="compareData.delta_expense <= 0 ? 'delta-up' : 'delta-down'">
                <span class="delta-arrow">{{ compareData.delta_expense >= 0 ? '▲' : '▼' }}</span>
                <span>Chi: {{ formatVND(Math.abs(compareData.delta_expense)) }}</span>
              </div>
              <div class="delta-item" :class="compareData.delta_savings >= 0 ? 'delta-up' : 'delta-down'">
                <span class="delta-arrow">{{ compareData.delta_savings >= 0 ? '▲' : '▼' }}</span>
                <span>Tiết kiệm: {{ formatVND(Math.abs(compareData.delta_savings)) }}</span>
              </div>
            </div>
            <div class="compare-card">
              <h4>📅 {{ compareData.month2.month }}</h4>
              <div class="compare-stat">
                <span>Thu: <strong class="positive">{{ formatVND(compareData.month2.income) }}</strong></span>
                <span>Chi: <strong class="negative">{{ formatVND(compareData.month2.expense) }}</strong></span>
                <span>Tiết kiệm: <strong :class="compareData.month2.savings >= 0 ? 'positive' : 'negative'">{{ formatVND(compareData.month2.savings) }}</strong></span>
              </div>
            </div>
          </div>
        </div>

        <div v-if="!trendData.trend?.length && !weeklyData.data?.length" class="empty-state">
          Chưa có đủ dữ liệu để hiển thị thống kê. Hãy thêm giao dịch!
        </div>
      </section>

      <!-- ═══════ TAB 8: AI CHAT ═══════ -->
      <section v-if="activeTab === 'chat'" class="tab-panel">
        <h2 class="section-title">💬 Khấu Bái Khí Linh — Trợ Lý AI Gemini</h2>

        <div class="chat-container">
          <div class="chat-messages" ref="chatMessagesEl">
            <div class="chat-welcome">
              <div class="chat-ai-avatar">🔮</div>
              <p>Kính chào Ký Chủ! Ta là <strong>Khí Linh Tiên Trí</strong>, trợ lý tài chính AI phong cách tu tiên. Hãy hỏi ta bất cứ điều gì về tài chính của đạo hữu!</p>
            </div>
            <div v-for="(msg, idx) in chatMessages" :key="idx"
                 :class="['chat-bubble', msg.role === 'user' ? 'user-bubble' : 'ai-bubble']">
              <div class="bubble-avatar">{{ msg.role === 'user' ? '🧙' : '🔮' }}</div>
              <div class="bubble-content" v-html="formatChatText(msg.text)"></div>
            </div>
            <div v-if="chatLoading && activeTab === 'chat'" class="chat-bubble ai-bubble">
              <div class="bubble-avatar">🔮</div>
              <div class="bubble-content typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
          <div class="chat-input-area">
            <input v-model="chatInput" type="text"
                   placeholder="Hỏi Tiên Trí về tài chính..."
                   @keyup.enter="sendChat" />
            <button class="btn-jade-sm" @click="sendChat" :disabled="chatLoading || !chatInput.trim()">
              ⚡ Gửi
            </button>
          </div>
        </div>
      </section>
    </main>

    <!-- REQUIREMENT 5: ACCOUNT MANAGEMENT MODAL -->
    <div v-if="showProfileModal" class="modal-backdrop" @click.self="showProfileModal = false">
      <div class="modal-card">
        <div class="modal-header">
          <h3 class="modal-title">🧘 Quản Lý Đạo Tâm (Tài Khoản)</h3>
          <button class="modal-close" @click="showProfileModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="input-group-xianxia">
            <label>📧 Linh Bưu (Email)</label>
            <input :value="userEmail" type="email" disabled class="disabled-input" />
          </div>
          <div class="input-group-xianxia">
            <label>👤 Đạo Hiệu Hiển Thị</label>
            <input v-model="profileForm.full_name" type="text" placeholder="Nhập đạo hiệu mới..." @keyup.enter="saveProfile" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showProfileModal = false">Hủy</button>
          <button class="btn-jade-sm" @click="saveProfile" :disabled="loadingProfile">
            {{ loadingProfile ? '⏳ Đang lưu...' : '✨ Lưu Đạo Hiệu' }}
          </button>
        </div>
      </div>
    </div>

    <!-- TOAST -->
    <div v-if="toast" class="toast-notification" :class="toast.type">
      {{ toast.message }}
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, nextTick } from 'vue'
import axios from 'axios'
import ChartComponent from './components/ChartComponents.vue'

export default {
  name: 'CankKhonApp',
  components: { ChartComponent },
  setup() {
    // ─── STATE ────────────────────
    const isLoggedIn = ref(false)
    const authMode = ref('login')
    const authForm = ref({ email: '', password: '', full_name: '' })
    const token = ref('')
    const userName = ref('Ký Chủ')
    const userEmail = ref('')
    const loading = ref(false)
    const loadingTips = ref(false)
    const loadingProfile = ref(false)
    const errorMsg = ref('')
    const toast = ref(null)
    const activeTab = ref('dashboard')

    // Profile modal state
    const showProfileModal = ref(false)
    const profileForm = ref({ full_name: '' })

    const tabs = [
      { id: 'dashboard',    icon: '📊', label: 'Tổng Quan' },
      { id: 'transactions', icon: '💸', label: 'Giao Dịch' },
      { id: 'wallets',      icon: '💳', label: 'Túi Càn Khôn' },
      { id: 'categories',   icon: '🏷️', label: 'Danh Mục' },
      { id: 'ocr',          icon: '🧾', label: 'Linh Nhãn OCR' },
      { id: 'budgets',      icon: '🎯', label: 'Hạn Mức' },
      { id: 'stats',        icon: '📈', label: 'Thống Kê' },
      { id: 'chat',         icon: '💬', label: 'Khí Linh AI' },
    ]

    // Data
    const wallets = ref([])
    const categories = ref([])
    const transactions = ref([])
    const budgets = ref([])
    const summary = ref({ total_income: 0, total_expense: 0, net_savings: 0, total_balance: 0, expense_by_category: [] })
    const budgetAlerts = ref([])
    const chatMessages = ref([])
    const chatInput = ref('')
    const chatMessagesEl = ref(null)

    // New v3 data
    const trendData = ref({ trend: [] })
    const weeklyData = ref({ data: [] })
    const compareData = ref(null)
    const savingTips = ref(null)

    // Compare month defaults
    const now = new Date()
    const compareMonth2 = ref(now.toISOString().slice(0, 7))
    const prevMonth = new Date(now.getFullYear(), now.getMonth() - 1, 1)
    const compareMonth1 = ref(prevMonth.toISOString().slice(0, 7))

    // Forms
    const txnForm = ref({
      transaction_type: 'EXPENSE', amount: 0, wallet_id: null,
      category_id: null, transaction_date: new Date().toISOString().slice(0, 10), note: ''
    })
    const walletForm = ref({ wallet_name: '', balance: 0, wallet_type: 'cash' })
    const catForm = ref({ category_name: '', category_type: 'EXPENSE', icon: '📦' })
    const budgetForm = ref({
      category_id: null, limit_amount: 0,
      month_year: new Date().toISOString().slice(0, 7)
    })
    const transferForm = ref({ from_wallet_id: null, to_wallet_id: null, amount: 0 })

    // OCR
    const ocrFile = ref(null)
    const ocrPreview = ref(null)
    const ocrResult = ref(null)
    const ocrConfirmForm = ref({
      note: '',
      amount: 0,
      transaction_date: new Date().toISOString().slice(0, 10),
      wallet_id: null,
      category_id: null,
      transaction_type: 'EXPENSE'
    })
    const chatLoading = ref(false)

    const iconOptions = ['🍕','🛍️','🚗','💵','🎁','🏠','💊','📚','🎮','☕','🍜','🎬','🏋️','✈️','📱','👕','🎵','🐾','🔧','📦']

    // ─── AXIOS CONFIG ─────────────
    const api = axios.create({ baseURL: '' })
    api.interceptors.request.use(config => {
      if (token.value) config.headers.Authorization = `Bearer ${token.value}`
      return config
    })

    // ─── COMPUTED ─────────────────
    const incomeCategories = computed(() => categories.value.filter(c => c.category_type === 'INCOME'))
    const expenseCategories = computed(() => categories.value.filter(c => c.category_type === 'EXPENSE'))
    const filteredCategories = computed(() =>
      categories.value.filter(c => c.category_type === txnForm.value.transaction_type)
    )
    const maxCategoryExpense = computed(() => {
      if (!summary.value.expense_by_category?.length) return 1
      return Math.max(...summary.value.expense_by_category.map(c => c.total), 1)
    })

    // ─── CHART DATA COMPUTED ──────
    const dashboardDoughnutData = computed(() => ({
      labels: (summary.value.expense_by_category || []).map(c => `${c.icon} ${c.category_name}`),
      values: (summary.value.expense_by_category || []).map(c => c.total),
    }))

    const dashboardBarData = computed(() => ({
      labels: (trendData.value.trend || []).map(t => t.month),
      income: (trendData.value.trend || []).map(t => t.income),
      expense: (trendData.value.trend || []).map(t => t.expense),
    }))

    const trendBarData = computed(() => ({
      labels: (trendData.value.trend || []).map(t => t.month),
      income: (trendData.value.trend || []).map(t => t.income),
      expense: (trendData.value.trend || []).map(t => t.expense),
    }))

    const weeklyLineData = computed(() => ({
      labels: (weeklyData.value.data || []).map(w => w.week_start || w.week),
      expense: (weeklyData.value.data || []).map(w => w.expense),
      income: (weeklyData.value.data || []).map(w => w.income),
    }))

    const statsDoughnutData = computed(() => ({
      labels: (summary.value.expense_by_category || []).map(c => `${c.icon} ${c.category_name}`),
      values: (summary.value.expense_by_category || []).map(c => c.total),
    }))

    // ─── HELPERS ──────────────────
    function resetAllState() {
      wallets.value = []
      categories.value = []
      transactions.value = []
      budgets.value = []
      summary.value = { total_income: 0, total_expense: 0, net_savings: 0, total_balance: 0, expense_by_category: [] }
      budgetAlerts.value = []
      chatMessages.value = []
      chatInput.value = ''
      chatLoading.value = false
      trendData.value = { trend: [] }
      weeklyData.value = { data: [] }
      compareData.value = null
      savingTips.value = null
      ocrFile.value = null
      ocrPreview.value = null
      ocrResult.value = null
      ocrConfirmForm.value = {
        note: '',
        amount: 0,
        transaction_date: new Date().toISOString().slice(0, 10),
        wallet_id: null,
        category_id: null,
        transaction_type: 'EXPENSE'
      }
      errorMsg.value = ''
      toast.value = null
    }

    function formatVND(val) {
      if (val === undefined || val === null) return '0 ₫'
      return Number(val).toLocaleString('vi-VN') + ' ₫'
    }

    function showToast(message, type = 'success') {
      toast.value = { message, type }
      setTimeout(() => { toast.value = null }, 3500)
    }

    function budgetPct(b) {
      return b.limit_amount > 0 ? (b.spent / b.limit_amount * 100) : 0
    }

    function formatChatText(text) {
      if (!text) return ''
      return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br/>')
    }

    function walletTypeIcon(type) {
      return type === 'cash' ? '💵' : type === 'bank' ? '🏦' : '📱'
    }

    // ─── AUTH ─────────────────────
    async function doLogin() {
      loading.value = true
      errorMsg.value = ''
      resetAllState()
      try {
        const { data } = await api.post('/api/auth/login', {
          email: authForm.value.email,
          password: authForm.value.password
        })
        token.value = data.token
        userName.value = data.full_name || 'Ký Chủ'
        userEmail.value = data.email
        isLoggedIn.value = true
        localStorage.setItem('xianxia_token', data.token)
        localStorage.setItem('xianxia_user', userName.value)
        localStorage.setItem('xianxia_email', data.email)
        await loadAllData()
      } catch (err) {
        errorMsg.value = err.response?.data?.detail || 'Lỗi đăng nhập!'
      }
      loading.value = false
    }

    async function doRegister() {
      loading.value = true
      errorMsg.value = ''
      resetAllState()
      try {
        const regForm = {
          ...authForm.value,
          full_name: authForm.value.full_name.trim() || 'Ký Chủ'
        }
        const { data } = await api.post('/api/auth/register', regForm)
        token.value = data.token
        userName.value = data.full_name || 'Ký Chủ'
        userEmail.value = data.email
        isLoggedIn.value = true
        localStorage.setItem('xianxia_token', data.token)
        localStorage.setItem('xianxia_user', userName.value)
        localStorage.setItem('xianxia_email', data.email)
        await loadAllData()
      } catch (err) {
        errorMsg.value = err.response?.data?.detail || 'Lỗi đăng ký!'
      }
      loading.value = false
    }

    function doLogout() {
      isLoggedIn.value = false
      token.value = ''
      userName.value = 'Ký Chủ'
      userEmail.value = ''
      localStorage.removeItem('xianxia_token')
      localStorage.removeItem('xianxia_user')
      localStorage.removeItem('xianxia_email')
      authForm.value = { email: '', password: '', full_name: '' }
      resetAllState()
    }

    // ─── USER PROFILE MANAGEMENT ──
    function openProfileModal() {
      profileForm.value.full_name = userName.value
      showProfileModal.value = true
    }

    async function saveProfile() {
      const newName = profileForm.value.full_name.trim()
      if (!newName) {
        showToast('Vui lòng nhập đạo hiệu!', 'error')
        return
      }
      loadingProfile.value = true
      try {
        await api.put('/api/user/profile', { full_name: newName })
        userName.value = newName
        localStorage.setItem('xianxia_user', newName)
        showToast('✨ Đạo hiệu đã được cập nhật!')
        showProfileModal.value = false
      } catch (err) {
        showToast(err.response?.data?.detail || 'Lỗi cập nhật tên!', 'error')
      }
      loadingProfile.value = false
    }

    async function fetchUserProfile() {
      try {
        const { data } = await api.get('/api/user/profile')
        if (data && data.full_name) {
          userName.value = data.full_name
          userEmail.value = data.email
          localStorage.setItem('xianxia_user', data.full_name)
        }
      } catch {}
    }

    // ─── DATA LOADING ─────────────
    async function loadAllData() {
      await Promise.all([
        fetchUserProfile(),
        loadWallets(), loadCategories(), loadTransactions(),
        loadSummary(), loadBudgets(), checkBudgetAlerts(),
        loadTrend(), loadWeekly(), loadChatHistory(),
      ])
    }

    async function loadChatHistory() {
      try {
        const { data } = await api.get('/api/ai/chat-history')
        if (data && data.length) {
          const history = []
          const sorted = [...data].reverse()
          for (const row of sorted) {
            history.push({ role: 'user', text: row.prompt_question })
            history.push({ role: 'ai', text: row.ai_response })
          }
          chatMessages.value = history
        } else {
          chatMessages.value = []
        }
      } catch {}
    }

    async function loadWallets() {
      try { wallets.value = (await api.get('/api/wallets')).data } catch {}
    }
    async function loadCategories() {
      try { categories.value = (await api.get('/api/categories')).data } catch {}
    }
    async function loadTransactions() {
      try { transactions.value = (await api.get('/api/transactions?limit=100')).data } catch {}
    }
    async function loadSummary() {
      try { summary.value = (await api.get('/api/reports/summary')).data } catch {}
    }
    async function loadBudgets() {
      try { budgets.value = (await api.get('/api/budgets')).data } catch {}
    }
    async function checkBudgetAlerts() {
      try { budgetAlerts.value = (await api.post('/api/ai/check-budget')).data.alerts } catch {}
    }
    async function loadTrend() {
      try { trendData.value = (await api.get('/api/reports/trend?months=6')).data } catch {}
    }
    async function loadWeekly() {
      try { weeklyData.value = (await api.get('/api/reports/weekly?weeks=4')).data } catch {}
    }
    async function loadCompare() {
      if (!compareMonth1.value || !compareMonth2.value) return
      try {
        compareData.value = (await api.get(`/api/reports/compare?month1=${compareMonth1.value}&month2=${compareMonth2.value}`)).data
      } catch {}
    }
    async function loadSavingTips() {
      loadingTips.value = true
      try {
        savingTips.value = (await api.post('/api/ai/saving-tips')).data
        showToast('🔮 Khai Thị Tiết Kiệm đã đến!')
      } catch (err) {
        showToast(err.response?.data?.detail || 'Không thể nhận khai thị (cần API key Gemini)', 'error')
      }
      loadingTips.value = false
    }

    // ─── CRUD ─────────────────────
    async function createTransaction() {
      if (!txnForm.value.amount || !txnForm.value.wallet_id || !txnForm.value.category_id) {
        showToast('Vui lòng điền đầy đủ thông tin!', 'error')
        return
      }
      loading.value = true
      try {
        await api.post('/api/transactions', txnForm.value)
        showToast('⚡ Giao dịch Linh Thạch đã ghi nhận!')
        txnForm.value = {
          transaction_type: 'EXPENSE', amount: 0, wallet_id: txnForm.value.wallet_id,
          category_id: null, transaction_date: new Date().toISOString().slice(0, 10), note: ''
        }
        await loadAllData()
      } catch (err) {
        showToast(err.response?.data?.detail || 'Lỗi tạo giao dịch!', 'error')
      }
      loading.value = false
    }

    async function deleteTransaction(id) {
      if (!confirm('Xóa giao dịch này?')) return
      try {
        await api.delete(`/api/transactions/${id}`)
        showToast('Giao dịch đã xóa!')
        await loadAllData()
      } catch {}
    }

    async function createWallet() {
      if (!walletForm.value.wallet_name) {
        showToast('Vui lòng nhập tên ví!', 'error')
        return
      }
      loading.value = true
      try {
        await api.post('/api/wallets', walletForm.value)
        showToast('✨ Túi Càn Khôn mới đã khai mở!')
        walletForm.value = { wallet_name: '', balance: 0, wallet_type: 'cash' }
        await loadWallets()
        await loadSummary()
      } catch (err) {
        showToast(err.response?.data?.detail || 'Lỗi tạo ví!', 'error')
      }
      loading.value = false
    }

    async function deleteWallet(id) {
      if (!confirm('Xóa ví này? Các giao dịch thuộc ví cũng sẽ bị ảnh hưởng.')) return
      try {
        await api.delete(`/api/wallets/${id}`)
        showToast('Ví đã xóa!')
        await loadAllData()
      } catch {}
    }

    async function doTransfer() {
      if (!transferForm.value.from_wallet_id || !transferForm.value.to_wallet_id || !transferForm.value.amount) {
        showToast('Vui lòng điền đầy đủ thông tin chuyển tiền!', 'error')
        return
      }
      loading.value = true
      try {
        const { data } = await api.post('/api/wallets/transfer', transferForm.value)
        showToast(`⚡ ${data.message}`)
        transferForm.value = { from_wallet_id: null, to_wallet_id: null, amount: 0 }
        await loadWallets()
        await loadSummary()
      } catch (err) {
        showToast(err.response?.data?.detail || 'Lỗi chuyển tiền!', 'error')
      }
      loading.value = false
    }

    async function createCategory() {
      if (!catForm.value.category_name) {
        showToast('Vui lòng nhập tên danh mục!', 'error')
        return
      }
      loading.value = true
      try {
        await api.post('/api/categories', catForm.value)
        showToast('✨ Danh mục mới đã khai mở!')
        catForm.value = { category_name: '', category_type: 'EXPENSE', icon: '📦' }
        await loadCategories()
      } catch (err) {
        showToast(err.response?.data?.detail || 'Lỗi!', 'error')
      }
      loading.value = false
    }

    async function deleteCategory(id) {
      if (!confirm('Xóa danh mục này?')) return
      try {
        await api.delete(`/api/categories/${id}`)
        showToast('Danh mục đã xóa!')
        await loadCategories()
      } catch {}
    }

    async function createBudget() {
      if (!budgetForm.value.category_id || !budgetForm.value.limit_amount) {
        showToast('Vui lòng điền đầy đủ!', 'error')
        return
      }
      loading.value = true
      try {
        await api.post('/api/budgets', budgetForm.value)
        showToast('🎯 Hạn mức tu luyện đã thiết lập!')
        await loadBudgets()
        await checkBudgetAlerts()
      } catch (err) {
        showToast(err.response?.data?.detail || 'Lỗi!', 'error')
      }
      loading.value = false
    }

    async function deleteBudget(id) {
      if (!confirm('Xóa hạn mức này?')) return
      try {
        await api.delete(`/api/budgets/${id}`)
        showToast('Hạn mức đã xóa!')
        await loadBudgets()
      } catch {}
    }

    // ─── OCR ──────────────────────
    function handleOCRUpload(e) {
      const file = e.target.files[0]
      if (file) {
        ocrFile.value = file
        ocrPreview.value = URL.createObjectURL(file)
        ocrResult.value = null
      }
    }

    function handleOCRDrop(e) {
      const file = e.dataTransfer.files[0]
      if (file && file.type.startsWith('image/')) {
        ocrFile.value = file
        ocrPreview.value = URL.createObjectURL(file)
        ocrResult.value = null
      }
    }

    async function scanInvoice() {
      if (!ocrFile.value) return
      loading.value = true
      try {
        const formData = new FormData()
        formData.append('file', ocrFile.value)
        const { data } = await api.post('/api/ai/scan-invoice', formData)
        ocrResult.value = data.data

        const defaultWallet = wallets.value.length ? wallets.value[0].id : null
        const defaultCat = expenseCategories.value.length ? expenseCategories.value[0].id : null
        ocrConfirmForm.value = {
          note: data.data.store_name || 'Chi tiêu từ hóa đơn',
          amount: data.data.total_amount || 0,
          transaction_date: data.data.date || new Date().toISOString().slice(0, 10),
          wallet_id: defaultWallet,
          category_id: defaultCat,
          transaction_type: 'EXPENSE'
        }
        showToast('👁️ Linh Nhãn đã hoàn thành phân tích! Vui lòng kiểm tra và xác nhận.')
      } catch (err) {
        showToast(err.response?.data?.detail || 'Lỗi OCR!', 'error')
      }
      loading.value = false
    }

    async function confirmOCRTransaction() {
      if (!ocrConfirmForm.value.amount || ocrConfirmForm.value.amount <= 0) {
        showToast('Vui lòng nhập số tiền hợp lệ!', 'error')
        return
      }
      if (!ocrConfirmForm.value.wallet_id || !ocrConfirmForm.value.category_id) {
        showToast('Vui lòng chọn Túi Càn Khôn và Danh Mục Chi!', 'error')
        return
      }
      loading.value = true
      try {
        await api.post('/api/transactions', ocrConfirmForm.value)
        showToast('⚡ Giao dịch từ hóa đơn đã được thêm vào lịch sử!')
        ocrResult.value = null
        ocrFile.value = null
        ocrPreview.value = null
        await loadAllData()
        activeTab.value = 'transactions'
      } catch (err) {
        showToast(err.response?.data?.detail || 'Lỗi lưu giao dịch!', 'error')
      }
      loading.value = false
    }

    // ─── AI CHAT ──────────────────
    async function sendChat() {
      if (!chatInput.value.trim() || chatLoading.value) return
      if (!Array.isArray(chatMessages.value)) {
        chatMessages.value = []
      }
      const msg = chatInput.value.trim()
      chatMessages.value.push({ role: 'user', text: msg })
      chatInput.value = ''
      await nextTick()
      scrollChat()

      chatLoading.value = true
      try {
        const { data } = await api.post('/api/ai/chat', { message: msg })
        if (!Array.isArray(chatMessages.value)) chatMessages.value = []
        chatMessages.value.push({ role: 'ai', text: data.response })
      } catch (err) {
        if (!Array.isArray(chatMessages.value)) chatMessages.value = []
        chatMessages.value.push({
          role: 'ai',
          text: '⚠️ Tiên Trí gặp trở ngại: ' + (err.response?.data?.detail || 'Không thể kết nối.')
        })
      } finally {
        chatLoading.value = false
        await nextTick()
        scrollChat()
      }
    }

    function scrollChat() {
      const el = chatMessagesEl.value
      if (el) el.scrollTop = el.scrollHeight
    }

    // ─── TAB SWITCH ───────────────
    function switchTab(tabId) {
      activeTab.value = tabId
      if (tabId === 'stats') {
        loadTrend()
        loadWeekly()
        loadCompare()
      }
    }

    // ─── INIT ─────────────────────
    onMounted(() => {
      const savedToken = localStorage.getItem('xianxia_token')
      const savedUser = localStorage.getItem('xianxia_user')
      const savedEmail = localStorage.getItem('xianxia_email')
      if (savedToken) {
        token.value = savedToken
        userName.value = (savedUser && savedUser !== 'Đạo Hữu Admin') ? savedUser : 'Ký Chủ'
        userEmail.value = savedEmail || 'admin@gmail.com'
        isLoggedIn.value = true
        loadAllData()
      }
    })

    return {
      isLoggedIn, authMode, authForm, loading, loadingTips, loadingProfile, errorMsg, toast,
      activeTab, tabs, userName, userEmail,
      showProfileModal, profileForm,
      wallets, categories, transactions, budgets, summary, budgetAlerts,
      chatMessages, chatInput, chatMessagesEl, chatLoading,
      txnForm, walletForm, catForm, budgetForm, transferForm,
      ocrFile, ocrPreview, ocrResult, ocrConfirmForm,
      iconOptions,
      incomeCategories, expenseCategories, filteredCategories, maxCategoryExpense,
      // v3 data
      trendData, weeklyData, compareData, savingTips,
      compareMonth1, compareMonth2,
      // chart computed
      dashboardDoughnutData, dashboardBarData,
      trendBarData, weeklyLineData, statsDoughnutData,
      // methods
      formatVND, showToast, budgetPct, formatChatText, walletTypeIcon,
      doLogin, doRegister, doLogout,
      openProfileModal, saveProfile,
      switchTab, loadAllData, loadCompare, loadSavingTips,
      createTransaction, deleteTransaction,
      createWallet, deleteWallet, doTransfer,
      createCategory, deleteCategory,
      createBudget, deleteBudget,
      handleOCRUpload, handleOCRDrop, scanInvoice, confirmOCRTransaction,
      sendChat,
    }
  }
}
</script>

<style>
/* ═══════════════════════════════════════════════════════════
   CÀN KHÔN LINH THẠCH CÁC v3.5 — CELESTIAL XIANXIA THEME
   ═══════════════════════════════════════════════════════════ */

/* ─── RESET & BASE ─────────────────────── */
*, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

:root {
  --bg-primary: #1a3a5c;
  --bg-secondary: rgba(255, 255, 255, 0.7);
  --bg-card: rgba(255, 255, 255, 0.78);
  --bg-card-hover: rgba(255, 255, 255, 0.92);

  --jade: #2b8a82;
  --jade-glow: #4fa8a0;
  --jade-dim: #1e5a55;

  --gold: #b38217;
  --gold-glow: #e8c874;
  --gold-dim: #78530b;

  --purple: #6d4ab8;
  --purple-glow: #8e6ee8;

  --crimson: #c0392b;
  --crimson-glow: #e74c3c;

  --text-primary: #2c3e50;
  --text-secondary: #476582;
  --text-dim: #6b88a5;
  --text-light: #f5f5f0;

  --border: rgba(232, 200, 116, 0.45);
  --border-glow: rgba(232, 200, 116, 0.85);

  --radius: 12px;
  --radius-lg: 20px;

  --shadow-jade: 0 8px 25px rgba(79, 168, 160, 0.25), 0 0 15px rgba(79, 168, 160, 0.15);
  --shadow-gold: 0 8px 25px rgba(232, 200, 116, 0.35), 0 0 20px rgba(232, 200, 116, 0.2);

  --font-calligraphy: 'Lora', 'Cormorant Garamond', 'Georgia', serif;
  --font-body: 'Inter', -apple-system, sans-serif;

  /* Custom Cursor: Embedded Sword SVG với Hotspot chính xác tại ĐẦU MŨI KIẾM (22 2) */
  --cursor-sword: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%234fa8a0' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='m14.5 17.5-5-5'/><path d='m10 13-6.5 6.5a1 1 0 0 0 1.4 1.4L11.4 14'/><path d='m12.5 8.5 7-7a2.12 2.12 0 0 1 3 3l-7 7'/><path d='M9 11 3 5'/><path d='M15 17l6 6'/></svg>") 22 2, auto;
  --cursor-pointer: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%23e8c874' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='m14.5 17.5-5-5'/><path d='m10 13-6.5 6.5a1 1 0 0 0 1.4 1.4L11.4 14'/><path d='m12.5 8.5 7-7a2.12 2.12 0 0 1 3 3l-7 7'/><path d='M9 11 3 5'/><path d='M15 17l6 6'/></svg>") 22 2, pointer;
}

body {
  font-family: var(--font-body);
  background: linear-gradient(180deg, #1a3a5c 0%, #3f688e 25%, #6d9bc3 50%, #9cbcdb 75%, #eef4f8 100%) attachment fixed;
  color: var(--text-primary);
  line-height: 1.6;
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
  cursor: var(--cursor-sword);
}

button, a, select, input, textarea, label, [role="button"], .clickable-brand, .user-badge-btn, .tab-btn, .btn-jade, .btn-jade-sm, .ocr-dropzone {
  cursor: var(--cursor-pointer) !important;
}

/* ─── SCROLLBAR ────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: rgba(238, 244, 248, 0.5); }
::-webkit-scrollbar-thumb { background: rgba(79, 168, 160, 0.4); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--jade-glow); }

/* ─── PERSISTENT XIANXIA BACKDROP ───────── */
.xianxia-backdrop {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.sun-aura-glow {
  position: absolute;
  top: -100px;
  left: 50%;
  transform: translateX(-50%);
  width: 1100px;
  height: 650px;
  background: radial-gradient(ellipse at center, rgba(255, 248, 220, 0.65) 0%, rgba(232, 200, 116, 0.3) 35%, rgba(143, 184, 217, 0.12) 65%, transparent 80%);
  filter: blur(25px);
  animation: auraPulse 10s ease-in-out infinite alternate;
}

@keyframes auraPulse {
  0% { opacity: 0.7; transform: translateX(-50%) scale(0.95); }
  100% { opacity: 1; transform: translateX(-50%) scale(1.05); }
}

.mountain-layer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  width: 100%;
  pointer-events: none;
}

.far-mountains { height: 280px; z-index: 1; opacity: 0.55; }
.mid-mountains { height: 240px; z-index: 2; opacity: 0.75; }
.near-mountains { height: 190px; z-index: 3; opacity: 0.92; }

.mountain-layer svg {
  width: 100%;
  height: 100%;
  display: block;
}

/* Sea of Clouds (Biển Mây) */
.sea-of-clouds-wrapper {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 180px;
  z-index: 4;
  overflow: hidden;
  pointer-events: none;
}

.sea-of-clouds {
  position: absolute;
  bottom: 0;
  width: 200%;
  height: 100%;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0) 0%, rgba(238, 244, 248, 0.8) 45%, rgba(255, 255, 255, 0.98) 100%);
  mask-image: radial-gradient(ellipse 100% 100% at 50% 100%, black 65%, transparent 100%);
}

.sea-of-clouds.wave-1 {
  animation: seaCloudsScroll 75s linear infinite;
  opacity: 0.85;
}
.sea-of-clouds.wave-2 {
  animation: seaCloudsScroll 110s linear infinite reverse;
  opacity: 0.6;
  bottom: -20px;
}

@keyframes seaCloudsScroll {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}

/* Floating Clouds */
.floating-clouds {
  position: absolute;
  top: 0;
  inset-inline: 0;
  height: 50vh;
  z-index: 2;
  pointer-events: none;
}

.cloud-cluster {
  position: absolute;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.7) 0%, rgba(238, 244, 248, 0.35) 60%, transparent 80%);
  border-radius: 50%;
  filter: blur(16px);
}

.cloud-1 {
  width: 340px; height: 130px; top: 8%; left: -120px;
  animation: floatCloudLeftToRight 85s linear infinite;
  opacity: 0.6;
}
.cloud-2 {
  width: 480px; height: 170px; top: 22%; left: -220px;
  animation: floatCloudLeftToRight 125s linear infinite 18s;
  opacity: 0.45;
}
.cloud-3 {
  width: 290px; height: 110px; top: 4%; left: -160px;
  animation: floatCloudLeftToRight 68s linear infinite 35s;
  opacity: 0.65;
}

@keyframes floatCloudLeftToRight {
  0% { transform: translateX(0); }
  100% { transform: translateX(calc(100vw + 550px)); }
}

/* Spirit Particles */
.spirit-particle-field {
  position: absolute;
  inset: 0;
  z-index: 3;
  pointer-events: none;
}

.spirit-particle {
  position: absolute;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #ffffff;
  box-shadow: 0 0 8px #e8c874, 0 0 16px #ffffff;
  animation: spiritFloatUp 9s ease-in-out infinite;
  opacity: 0;
}

@keyframes spiritFloatUp {
  0% { opacity: 0; transform: translateY(100vh) scale(0.4) translateX(0); }
  30% { opacity: 0.85; }
  75% { opacity: 0.95; }
  100% { opacity: 0; transform: translateY(-50px) scale(1.3) translateX(var(--sway, 30px)); }
}

.p-1  { left: 5%;  animation-duration: 9s;  animation-delay: 0s;   --sway: 25px; }
.p-2  { left: 12%; animation-duration: 12s; animation-delay: 1.5s; --sway: -30px; background: #e8c874; }
.p-3  { left: 18%; animation-duration: 7s;  animation-delay: 3s;   --sway: 15px; }
.p-4  { left: 24%; animation-duration: 11s; animation-delay: 0.8s; --sway: -20px; }
.p-5  { left: 30%; animation-duration: 8.5s;animation-delay: 4s;   --sway: 35px; background: #e8c874; }
.p-6  { left: 37%; animation-duration: 10s; animation-delay: 2s;   --sway: -15px; }
.p-7  { left: 43%; animation-duration: 13s; animation-delay: 5s;   --sway: 40px; }
.p-8  { left: 49%; animation-duration: 7.5s;animation-delay: 1s;   --sway: -25px; background: #e8c874; }
.p-9  { left: 55%; animation-duration: 9.5s;animation-delay: 3.5s; --sway: 20px; }
.p-10 { left: 62%; animation-duration: 11.5s;animation-delay: 0.5s;--sway: -35px; }
.p-11 { left: 68%; animation-duration: 8s;  animation-delay: 2.5s; --sway: 30px; background: #e8c874; }
.p-12 { left: 74%; animation-duration: 10.5s;animation-delay: 4.5s;--sway: -18px; }
.p-13 { left: 80%; animation-duration: 12.5s;animation-delay: 1.8s;--sway: 22px; }
.p-14 { left: 86%; animation-duration: 9s;  animation-delay: 3.2s; --sway: -28px; background: #e8c874; }
.p-15 { left: 92%; animation-duration: 7.8s;animation-delay: 0.2s; --sway: 16px; }
.p-16 { left: 8%;  animation-duration: 11s; animation-delay: 5.5s; --sway: -32px; }
.p-17 { left: 21%; animation-duration: 9.8s;animation-delay: 2.2s; --sway: 28px; background: #e8c874; }
.p-18 { left: 35%; animation-duration: 13.5s;animation-delay: 4.2s;--sway: -22px; }
.p-19 { left: 47%; animation-duration: 8.2s;animation-delay: 1.2s; --sway: 18px; }
.p-20 { left: 59%; animation-duration: 10.2s;animation-delay: 3.8s;--sway: -26px; background: #e8c874; }
.p-21 { left: 71%; animation-duration: 7.2s;animation-delay: 0.9s; --sway: 34px; }
.p-22 { left: 83%; animation-duration: 12s; animation-delay: 5.1s; --sway: -14px; }
.p-23 { left: 95%; animation-duration: 9.2s;animation-delay: 2.7s; --sway: 24px; background: #e8c874; }
.p-24 { left: 15%; animation-duration: 10.8s;animation-delay: 4.8s;--sway: -38px; }
.p-25 { left: 65%; animation-duration: 8.8s;animation-delay: 1.6s; --sway: 20px; }

/* ─── ANIMATIONS ───────────────────────── */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeInScale {
  from { opacity: 0; transform: scale(0.97) translateY(8px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}
@keyframes glowPulse {
  0%, 100% { box-shadow: 0 0 15px rgba(232, 200, 116, 0.2); }
  50% { box-shadow: 0 0 30px rgba(232, 200, 116, 0.45), 0 0 50px rgba(79, 168, 160, 0.2); }
}
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}
@keyframes rotateSymbol {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
@keyframes typingBounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}
@keyframes slideInRight {
  from { opacity: 0; transform: translateX(20px); }
  to { opacity: 1; transform: translateX(0); }
}

/* ─── LOGIN REALM ──────────────────────── */
.login-realm {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  padding: 24px;
}

.login-card {
  position: relative;
  z-index: 10;
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(232, 200, 116, 0.6);
  border-radius: var(--radius-lg);
  padding: 48px 40px;
  width: 100%;
  max-width: 460px;
  animation: fadeIn 0.8s ease-out, glowPulse 5s ease-in-out infinite;
  backdrop-filter: blur(16px);
  box-shadow: 0 20px 50px rgba(26, 58, 92, 0.15), 0 0 30px rgba(232, 200, 116, 0.25);
}

.login-header { text-align: center; margin-bottom: 36px; }

.dao-symbol {
  font-size: 56px;
  display: inline-block;
  animation: rotateSymbol 25s linear infinite;
  filter: drop-shadow(0 0 12px rgba(232, 200, 116, 0.8));
  margin-bottom: 16px;
}

.title-calligraphy {
  font-family: var(--font-calligraphy);
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #1a3a5c 0%, #b38217 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 1.5px;
}

.subtitle-glow {
  color: var(--text-secondary);
  font-size: 13px;
  margin-top: 8px;
  letter-spacing: 0.5px;
}

.form-title {
  font-family: var(--font-calligraphy);
  color: var(--gold);
  font-size: 19px;
  margin-bottom: 24px;
  text-align: center;
}

.input-group-xianxia {
  margin-bottom: 18px;
}
.input-group-xianxia label {
  display: block;
  font-size: 13px;
  color: var(--text-primary);
  margin-bottom: 6px;
  font-weight: 600;
}
.input-group-xianxia input,
.input-group-xianxia select {
  width: 100%;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(232, 200, 116, 0.5);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 14px;
  font-family: var(--font-body);
  transition: all 0.3s ease;
  outline: none;
}
.input-group-xianxia input:focus,
.input-group-xianxia select:focus {
  border-color: var(--jade-glow);
  box-shadow: 0 0 0 3px rgba(79, 168, 160, 0.25);
  background: #ffffff;
}
.input-group-xianxia input::placeholder {
  color: var(--text-dim);
}

.btn-jade {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #e8c874 0%, #d99b26 100%);
  color: #1a3a5c;
  border: 1px solid #f3d994;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 700;
  transition: all 0.3s ease;
  font-family: var(--font-body);
  letter-spacing: 0.5px;
  box-shadow: 0 4px 15px rgba(232, 200, 116, 0.35);
}
.btn-jade:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(232, 200, 116, 0.55), 0 0 15px rgba(79, 168, 160, 0.3);
}
.btn-jade:disabled {
  opacity: 0.65;
}

.auth-switch {
  text-align: center;
  margin-top: 20px;
  font-size: 13px;
  color: var(--text-secondary);
}
.auth-switch span {
  color: var(--gold);
  font-weight: 700;
}
.auth-switch span:hover { text-decoration: underline; }

.error-banner {
  margin-top: 16px;
  padding: 12px;
  background: rgba(192, 57, 43, 0.12);
  border: 1px solid rgba(192, 57, 43, 0.4);
  border-radius: 8px;
  color: var(--crimson);
  text-align: center;
  font-size: 13px;
  font-weight: 600;
}

/* ─── MAIN APP REALM ───────────────────── */
.app-realm {
  min-height: 100vh;
  position: relative;
}

/* ─── HEADER ───────────────────────────── */
.realm-header {
  background: rgba(255, 255, 255, 0.82);
  border-bottom: 2px solid rgba(232, 200, 116, 0.5);
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(16px);
  box-shadow: 0 4px 20px rgba(26, 58, 92, 0.06);
}
.header-inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  height: 68px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.clickable-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 12px;
  border-radius: 10px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  user-select: none;
}
.clickable-brand:hover {
  background: rgba(232, 200, 116, 0.2);
  transform: translateY(-2px) scale(1.01);
}

.header-symbol {
  font-size: 28px;
  animation: rotateSymbol 30s linear infinite;
  filter: drop-shadow(0 0 10px rgba(232, 200, 116, 0.6));
}
.header-title {
  font-family: var(--font-calligraphy);
  font-size: 22px;
  font-weight: 700;
  background: linear-gradient(90deg, #1a3a5c 0%, #b38217 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.version-badge {
  font-size: 10px;
  padding: 2px 8px;
  background: linear-gradient(135deg, #4fa8a0, #2b8a82);
  color: white;
  border-radius: 12px;
  font-weight: 700;
  letter-spacing: 0.5px;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-badge-btn {
  font-size: 14px;
  color: #1a3a5c;
  padding: 7px 16px;
  background: rgba(232, 200, 116, 0.2);
  border-radius: 20px;
  border: 1px solid rgba(232, 200, 116, 0.7);
  font-family: var(--font-body);
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 2px 10px rgba(232, 200, 116, 0.2);
}
.user-badge-btn:hover {
  background: rgba(232, 200, 116, 0.4);
  box-shadow: var(--shadow-gold);
  transform: translateY(-2px);
}

.btn-logout {
  padding: 7px 16px;
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid var(--crimson);
  color: var(--crimson);
  border-radius: 8px;
  font-size: 13px;
  font-family: var(--font-body);
  font-weight: 600;
  transition: all 0.3s;
}
.btn-logout:hover {
  background: rgba(192, 57, 43, 0.12);
}

/* ─── TAB NAV ──────────────────────────── */
.tab-nav {
  background: rgba(255, 255, 255, 0.75);
  border-bottom: 1px solid rgba(232, 200, 116, 0.4);
  position: sticky;
  top: 68px;
  z-index: 99;
  backdrop-filter: blur(14px);
}
.tab-nav-inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  gap: 6px;
  overflow-x: auto;
  scrollbar-width: none;
}
.tab-nav-inner::-webkit-scrollbar { display: none; }

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 20px;
  border: none;
  background: transparent;
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  border-bottom: 3px solid transparent;
  transition: all 0.3s;
  font-family: var(--font-body);
}
.tab-btn:hover {
  color: var(--gold);
  background: rgba(232, 200, 116, 0.15);
}
.tab-btn.active {
  color: #1a3a5c;
  font-weight: 700;
  border-bottom-color: var(--gold);
  background: linear-gradient(180deg, rgba(232, 200, 116, 0.25) 0%, rgba(232, 200, 116, 0.05) 100%);
}
.tab-icon { font-size: 16px; }

/* ─── CONTENT ──────────────────────────── */
.realm-content {
  position: relative;
  z-index: 1;
  max-width: 1400px;
  margin: 0 auto;
  padding: 32px 24px 100px;
}

.tab-panel {
  animation: fadeInScale 0.4s ease-out;
}

.section-title {
  font-family: var(--font-calligraphy);
  font-size: 25px;
  font-weight: 700;
  color: #1a3a5c;
  margin-bottom: 28px;
  letter-spacing: 1px;
  text-shadow: 0 2px 10px rgba(232, 200, 116, 0.3);
}

.sub-title {
  font-family: var(--font-calligraphy);
  font-size: 18px;
  color: #1a3a5c;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(232, 200, 116, 0.4);
}

/* ─── METRICS ──────────────────────────── */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
  margin-bottom: 36px;
}

.metric-card {
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(232, 200, 116, 0.5);
  border-radius: var(--radius);
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 18px;
  transition: all 0.4s ease;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(12px);
  box-shadow: 0 8px 24px rgba(26, 58, 92, 0.06);
}
.metric-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;
  border-radius: var(--radius) var(--radius) 0 0;
}
.metric-card.jade::before { background: linear-gradient(90deg, var(--jade), var(--jade-glow)); }
.metric-card.crimson::before { background: linear-gradient(90deg, var(--crimson), var(--crimson-glow)); }
.metric-card.gold::before { background: linear-gradient(90deg, var(--gold), var(--gold-glow)); }
.metric-card.purple::before { background: linear-gradient(90deg, var(--purple), var(--purple-glow)); }

.metric-card:hover {
  transform: translateY(-4px);
  border-color: #e8c874;
  box-shadow: 0 12px 30px rgba(232, 200, 116, 0.35);
}

.metric-icon {
  font-size: 36px;
  animation: float 3s ease-in-out infinite;
}
.metric-card:nth-child(2) .metric-icon { animation-delay: 0.5s; }
.metric-card:nth-child(3) .metric-icon { animation-delay: 1s; }
.metric-card:nth-child(4) .metric-icon { animation-delay: 1.5s; }

.metric-info { display: flex; flex-direction: column; gap: 6px; }
.metric-label { font-size: 13px; color: var(--text-secondary); font-weight: 600; }
.metric-value {
  font-size: 22px;
  font-weight: 700;
  font-family: var(--font-calligraphy);
  color: #1a3a5c;
}
.metric-value.positive, .positive { color: var(--jade); }
.metric-value.negative, .negative { color: var(--crimson); }

/* ─── ALERTS ───────────────────────────── */
.alerts-section { margin-bottom: 32px; }
.alert-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  border-radius: 10px;
  margin-bottom: 8px;
  animation: fadeIn 0.5s ease-out;
}
.alert-card.danger {
  background: rgba(192, 57, 43, 0.12);
  border: 1px solid rgba(192, 57, 43, 0.35);
}
.alert-card.warning {
  background: rgba(232, 200, 116, 0.2);
  border: 1px solid rgba(232, 200, 116, 0.6);
}
.alert-icon { font-size: 20px; }
.alert-msg { flex: 1; font-size: 14px; color: var(--text-primary); font-weight: 500; }
.alert-pct { font-weight: 700; font-size: 15px; color: var(--crimson); }

/* ─── DASHBOARD CHARTS ROW ─────────────── */
.dashboard-charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 36px;
}
.chart-card {
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(232, 200, 116, 0.5);
  border-radius: var(--radius);
  padding: 24px;
  transition: all 0.3s;
  animation: fadeInScale 0.5s ease-out;
  backdrop-filter: blur(12px);
  box-shadow: 0 8px 24px rgba(26, 58, 92, 0.06);
}
.chart-card:hover {
  border-color: #e8c874;
  box-shadow: 0 12px 30px rgba(232, 200, 116, 0.3);
}

/* ─── SAVING TIPS ──────────────────────── */
.saving-tips-section {
  margin-bottom: 36px;
}
.saving-tips-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.saving-tips-header .sub-title {
  margin-bottom: 0;
  border-bottom: none;
  padding-bottom: 0;
}
.saving-tips-card {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(232, 200, 116, 0.5);
  border-radius: var(--radius);
  padding: 28px;
  animation: fadeInScale 0.5s ease-out;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(12px);
  box-shadow: 0 8px 24px rgba(26, 58, 92, 0.06);
}
.saving-tips-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--purple), var(--gold-glow), var(--jade-glow));
}
.tips-meta {
  display: flex;
  gap: 24px;
  margin-bottom: 16px;
  font-size: 13px;
  color: var(--text-secondary);
}
.tips-content {
  font-size: 14px;
  line-height: 1.8;
  color: var(--text-primary);
}

/* ─── TABLE ────────────────────────────── */
.table-scroll { overflow-x: auto; }

.xianxia-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(12px);
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(26, 58, 92, 0.06);
}
.xianxia-table thead th {
  text-align: left;
  padding: 14px 18px;
  background: rgba(232, 200, 116, 0.2);
  color: #1a3a5c;
  font-family: var(--font-calligraphy);
  font-weight: 700;
  font-size: 13px;
  letter-spacing: 0.5px;
  border-bottom: 1px solid rgba(232, 200, 116, 0.5);
  white-space: nowrap;
}
.xianxia-table tbody td {
  padding: 14px 18px;
  border-bottom: 1px solid rgba(232, 200, 116, 0.25);
  color: var(--text-primary);
  vertical-align: middle;
}
.xianxia-table tbody tr {
  transition: background 0.2s;
}
.xianxia-table tbody tr:hover {
  background: rgba(232, 200, 116, 0.15);
}

.cat-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: rgba(232, 200, 116, 0.15);
  border: 1px solid rgba(232, 200, 116, 0.4);
  border-radius: 6px;
  font-size: 13px;
  color: #1a3a5c;
  white-space: nowrap;
}

.amt-income { color: var(--jade); font-weight: 700; white-space: nowrap; }
.amt-expense { color: var(--crimson); font-weight: 700; white-space: nowrap; }
.empty-row { text-align: center; color: var(--text-dim); font-style: italic; }

/* ─── CATEGORY BREAKDOWN ──────────────── */
.category-breakdown { margin-top: 32px; }
.cat-bars { display: flex; flex-direction: column; gap: 12px; }
.cat-bar-row {
  display: flex;
  align-items: center;
  gap: 14px;
}
.cat-bar-label {
  min-width: 180px;
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
  white-space: nowrap;
}
.cat-bar-track {
  flex: 1;
  height: 10px;
  background: rgba(232, 200, 116, 0.2);
  border-radius: 5px;
  overflow: hidden;
}
.cat-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--jade), var(--jade-glow));
  border-radius: 5px;
  transition: width 0.8s ease;
}
.cat-bar-value {
  min-width: 120px;
  text-align: right;
  font-size: 13px;
  font-weight: 600;
  color: #1a3a5c;
  white-space: nowrap;
}

/* ─── FORM CARD ────────────────────────── */
.form-card {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(232, 200, 116, 0.5);
  border-radius: var(--radius);
  padding: 28px;
  margin-bottom: 24px;
  backdrop-filter: blur(12px);
  box-shadow: 0 8px 24px rgba(26, 58, 92, 0.06);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

/* ─── WALLET TRANSFER ──────────────────── */
.transfer-card {
  border-color: rgba(232, 200, 116, 0.6);
  position: relative;
}
.transfer-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--jade-glow), var(--gold-glow), var(--purple-glow));
  border-radius: var(--radius) var(--radius) 0 0;
}
.transfer-arrow-col {
  display: flex;
  align-items: center;
  justify-content: center;
}
.transfer-arrow {
  font-size: 24px;
  color: var(--gold);
  animation: glowPulse 2s ease-in-out infinite;
  margin-top: 20px;
}

/* ─── WALLET CARDS ─────────────────────── */
.wallet-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-top: 28px;
}
.wallet-card {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(232, 200, 116, 0.5);
  border-radius: var(--radius);
  padding: 24px;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(12px);
  box-shadow: 0 8px 24px rgba(26, 58, 92, 0.06);
}
.wallet-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--jade), var(--gold-glow), var(--purple-glow));
}
.wallet-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(232, 200, 116, 0.35);
  border-color: #e8c874;
}
.wallet-card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.wallet-type-icon { font-size: 28px; }
.wallet-name {
  font-family: var(--font-calligraphy);
  font-size: 17px;
  color: #1a3a5c;
  margin-bottom: 8px;
}
.wallet-balance {
  font-size: 24px;
  font-weight: 700;
  color: var(--jade);
  font-family: var(--font-calligraphy);
  margin-bottom: 4px;
}
.wallet-type-label {
  font-size: 12px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* ─── CATEGORIES ───────────────────────── */
.categories-split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-top: 28px;
}
.cat-col { display: flex; flex-direction: column; gap: 8px; }
.cat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(232, 200, 116, 0.4);
  border-radius: 10px;
  font-size: 14px;
  transition: all 0.3s;
}
.cat-item:hover { border-color: #e8c874; }
.cat-item.income { border-left: 4px solid var(--jade); }
.cat-item.expense { border-left: 4px solid var(--crimson); }

/* ─── BUTTONS SMALL ────────────────────── */
.btn-sm-danger {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(192, 57, 43, 0.1);
  border: 1px solid rgba(192, 57, 43, 0.3);
  border-radius: 6px;
  color: var(--crimson);
  font-size: 14px;
  transition: all 0.3s;
}
.btn-sm-danger:hover {
  background: rgba(192, 57, 43, 0.25);
  border-color: var(--crimson);
}

/* ─── OCR UPLOAD ───────────────────────── */
.hint-text {
  color: var(--text-secondary);
  font-size: 13px;
  margin-bottom: 16px;
}
.upload-zone {
  border: 2px dashed rgba(232, 200, 116, 0.7);
  border-radius: var(--radius);
  padding: 48px 24px;
  text-align: center;
  transition: all 0.3s;
  background: rgba(255, 255, 255, 0.75);
}
.upload-zone:hover {
  border-color: var(--gold);
  background: rgba(232, 200, 116, 0.15);
}
.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: var(--text-secondary);
}
.upload-icon { font-size: 40px; }
.ocr-preview-img {
  max-width: 100%;
  max-height: 300px;
  border-radius: 8px;
  object-fit: contain;
}

.ocr-result-card {
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid #e8c874;
  border-radius: var(--radius);
  padding: 28px;
  margin-top: 24px;
  animation: fadeIn 0.5s ease-out;
  box-shadow: 0 8px 24px rgba(26, 58, 92, 0.08);
}
.ocr-info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}
.ocr-info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.ocr-info-item label {
  font-size: 12px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 1px;
}
.ocr-info-item span {
  font-size: 16px;
  color: var(--text-primary);
  font-weight: 600;
}
.ocr-total {
  color: var(--jade) !important;
  font-family: var(--font-calligraphy);
  font-size: 22px !important;
}
.ocr-items { margin-top: 16px; }
.ocr-items h4 { margin-bottom: 12px; color: var(--text-primary); font-size: 14px; }
.ocr-raw { margin-top: 16px; }
.ocr-raw h4 { margin-bottom: 8px; color: var(--text-secondary); font-size: 13px; }
.ocr-raw pre {
  background: rgba(238, 244, 248, 0.8);
  padding: 16px;
  border-radius: 8px;
  font-size: 12px;
  color: var(--text-primary);
  overflow-x: auto;
  white-space: pre-wrap;
  border: 1px solid rgba(232, 200, 116, 0.3);
}

/* ─── BUDGETS ──────────────────────────── */
.budget-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 16px;
  margin-top: 24px;
}
.budget-card {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(232, 200, 116, 0.5);
  border-radius: var(--radius);
  padding: 20px;
  transition: all 0.3s;
  box-shadow: 0 8px 24px rgba(26, 58, 92, 0.06);
}
.budget-card:hover { border-color: #e8c874; box-shadow: 0 12px 30px rgba(232, 200, 116, 0.3); }
.budget-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 15px;
  font-weight: 600;
  color: #1a3a5c;
}
.budget-amounts {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 10px;
}
.progress-track {
  height: 12px;
  background: rgba(232, 200, 116, 0.2);
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 8px;
}
.progress-fill {
  height: 100%;
  border-radius: 6px;
  transition: width 0.8s ease;
}
.progress-fill.safe { background: linear-gradient(90deg, var(--jade), var(--jade-glow)); }
.progress-fill.warning { background: linear-gradient(90deg, var(--gold), var(--gold-glow)); }
.progress-fill.danger {
  background: linear-gradient(90deg, var(--crimson), var(--crimson-glow));
  animation: glowPulse 1.5s ease-in-out infinite;
}
.budget-pct { font-size: 13px; font-weight: 600; }
.pct-safe { color: var(--jade); }
.pct-warning { color: var(--gold); }
.pct-danger { color: var(--crimson); }

/* ─── STATISTICS TAB ───────────────────── */
.stats-chart-card {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(232, 200, 116, 0.5);
  border-radius: var(--radius);
  padding: 28px;
  margin-bottom: 28px;
  animation: fadeInScale 0.5s ease-out;
  transition: all 0.3s;
  box-shadow: 0 8px 24px rgba(26, 58, 92, 0.06);
}
.stats-chart-card:hover {
  border-color: #e8c874;
  box-shadow: 0 12px 30px rgba(232, 200, 116, 0.3);
}

/* ─── COMPARE SECTION ──────────────────── */
.compare-section {
  margin-top: 8px;
}
.compare-controls {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  margin-bottom: 24px;
}
.compare-vs {
  font-size: 20px;
  font-weight: 700;
  color: var(--gold);
  font-family: var(--font-calligraphy);
  padding-bottom: 16px;
}
.compare-grid {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 20px;
  align-items: stretch;
}
.compare-card {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(232, 200, 116, 0.5);
  border-radius: var(--radius);
  padding: 24px;
  animation: slideInRight 0.5s ease-out;
  box-shadow: 0 8px 24px rgba(26, 58, 92, 0.06);
}
.compare-card h4 {
  font-family: var(--font-calligraphy);
  color: #1a3a5c;
  margin-bottom: 16px;
  font-size: 16px;
}
.compare-stat {
  display: flex;
  flex-direction: column;
  gap: 10px;
  font-size: 14px;
  color: var(--text-secondary);
}
.compare-stat strong {
  font-size: 16px;
  color: var(--text-primary);
}
.compare-delta {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 12px;
}
.delta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
}
.delta-up {
  background: rgba(43, 138, 130, 0.12);
  color: var(--jade);
  border: 1px solid rgba(43, 138, 130, 0.3);
}
.delta-down {
  background: rgba(192, 57, 43, 0.12);
  color: var(--crimson);
  border: 1px solid rgba(192, 57, 43, 0.3);
}
.delta-arrow {
  font-size: 14px;
}

/* ─── AI CHAT ──────────────────────────── */
.chat-container {
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(232, 200, 116, 0.6);
  border-radius: var(--radius-lg);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 280px);
  min-height: 500px;
  backdrop-filter: blur(14px);
  box-shadow: 0 12px 35px rgba(26, 58, 92, 0.08);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chat-welcome {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 20px;
  background: rgba(232, 200, 116, 0.15);
  border: 1px solid rgba(232, 200, 116, 0.4);
  border-radius: var(--radius);
  margin-bottom: 8px;
}
.chat-ai-avatar {
  font-size: 36px;
  animation: float 3s ease-in-out infinite;
}
.chat-welcome p {
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.7;
}

.chat-bubble {
  display: flex;
  gap: 12px;
  max-width: 85%;
  animation: fadeIn 0.3s ease-out;
}
.user-bubble { align-self: flex-end; flex-direction: row-reverse; }
.ai-bubble { align-self: flex-start; }

.bubble-avatar { font-size: 24px; flex-shrink: 0; }
.bubble-content {
  padding: 14px 18px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.7;
}
.user-bubble .bubble-content {
  background: linear-gradient(135deg, #e8c874, #d99b26);
  color: #1a3a5c;
  font-weight: 500;
  border-bottom-right-radius: 4px;
  box-shadow: 0 4px 12px rgba(232, 200, 116, 0.3);
}
.ai-bubble .bubble-content {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(232, 200, 116, 0.4);
  color: var(--text-primary);
  border-bottom-left-radius: 4px;
}

.typing-indicator {
  display: flex;
  gap: 6px;
  padding: 8px 12px !important;
}
.typing-indicator span {
  width: 8px;
  height: 8px;
  background: var(--gold);
  border-radius: 50%;
  animation: typingBounce 1.4s infinite ease-in-out;
}
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

.chat-input-area {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid rgba(232, 200, 116, 0.4);
  background: rgba(238, 244, 248, 0.6);
}
.chat-input-area input {
  flex: 1;
  padding: 12px 16px;
  background: #ffffff;
  border: 1px solid rgba(232, 200, 116, 0.5);
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 14px;
  outline: none;
  font-family: var(--font-body);
  transition: border-color 0.3s;
}
.chat-input-area input:focus {
  border-color: var(--jade-glow);
  box-shadow: 0 0 0 3px rgba(79, 168, 160, 0.2);
}

.btn-jade-sm {
  padding: 12px 24px;
  background: linear-gradient(135deg, #e8c874, #d99b26);
  color: #1a3a5c;
  border: 1px solid #f3d994;
  border-radius: 10px;
  font-weight: 700;
  font-family: var(--font-body);
  font-size: 14px;
  transition: all 0.3s;
  white-space: nowrap;
  box-shadow: 0 4px 12px rgba(232, 200, 116, 0.3);
}
.btn-jade-sm:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(232, 200, 116, 0.5);
}
.btn-jade-sm:disabled { opacity: 0.5; }

/* ─── MODAL ACCOUNT MANAGEMENT ────────── */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(26, 58, 92, 0.4);
  backdrop-filter: blur(8px);
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  animation: fadeIn 0.3s ease-out;
}
.modal-card {
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid #e8c874;
  border-radius: var(--radius-lg);
  width: 100%;
  max-width: 440px;
  padding: 28px;
  box-shadow: 0 20px 50px rgba(26, 58, 92, 0.2), 0 0 30px rgba(232, 200, 116, 0.3);
  animation: fadeInScale 0.3s ease-out;
}
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
.modal-title {
  font-family: var(--font-calligraphy);
  font-size: 19px;
  color: #1a3a5c;
  font-weight: 700;
}
.modal-close {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-size: 20px;
  transition: color 0.2s;
}
.modal-close:hover { color: var(--crimson); }
.disabled-input {
  opacity: 0.7;
  background: rgba(238, 244, 248, 0.8) !important;
}
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}
.btn-secondary {
  padding: 10px 20px;
  background: transparent;
  border: 1px solid rgba(232, 200, 116, 0.6);
  color: var(--text-primary);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}
.btn-secondary:hover { background: rgba(232, 200, 116, 0.15); }

/* ─── TOAST ────────────────────────────── */
.toast-notification {
  position: fixed;
  bottom: 30px;
  right: 30px;
  padding: 14px 24px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  z-index: 9999;
  animation: fadeIn 0.3s ease-out;
  max-width: 400px;
  backdrop-filter: blur(8px);
}
.toast-notification.success {
  background: rgba(43, 138, 130, 0.95);
  color: white;
  border: 1px solid var(--jade-glow);
  box-shadow: 0 8px 30px rgba(43, 138, 130, 0.4);
}
.toast-notification.error {
  background: rgba(192, 57, 43, 0.95);
  color: white;
  border: 1px solid var(--crimson-glow);
  box-shadow: 0 8px 30px rgba(192, 57, 43, 0.4);
}

/* ─── EMPTY STATE ──────────────────────── */
.empty-state {
  text-align: center;
  padding: 32px;
  color: var(--text-secondary);
  font-size: 14px;
  font-style: italic;
}

/* ─── RESPONSIVE ───────────────────────── */
@media (max-width: 768px) {
  .header-title { font-size: 17px; }
  .version-badge { display: none; }
  .realm-content { padding: 20px 16px 80px; }
  .metrics-grid { grid-template-columns: 1fr; }
  .categories-split { grid-template-columns: 1fr; }
  .form-grid { grid-template-columns: 1fr; }
  .wallet-grid { grid-template-columns: 1fr; }
  .budget-list { grid-template-columns: 1fr; }
  .tab-btn .tab-label { display: none; }
  .tab-btn { padding: 14px 12px; }
  .login-card { margin: 16px; padding: 32px 24px; }
  .chat-container { height: calc(100vh - 240px); min-height: 400px; }
  .user-badge-btn { padding: 6px 10px; font-size: 12px; }
  .dashboard-charts-row { grid-template-columns: 1fr; }
  .compare-grid { grid-template-columns: 1fr; }
  .compare-delta { flex-direction: row; flex-wrap: wrap; justify-content: center; }
  .compare-controls { flex-direction: column; }
  .compare-vs { padding-bottom: 0; }
  .transfer-arrow-col { display: none; }

  /* Mobile backdrop optimization */
  .far-mountains { height: 180px; }
  .mid-mountains { height: 150px; }
  .near-mountains { height: 120px; }
  .floating-clouds { display: none; }
  .spirit-particle-field .spirit-particle:nth-child(n+13) { display: none; }
}

@media (max-width: 480px) {
  .metric-value { font-size: 19px; }
  .section-title { font-size: 21px; }
  .cat-bar-label { min-width: 120px; font-size: 12px; }
  .cat-bar-value { min-width: 90px; font-size: 12px; }
  .saving-tips-header { flex-direction: column; gap: 12px; align-items: flex-start; }
}
</style>
