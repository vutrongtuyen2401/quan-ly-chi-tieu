<template>
  <!-- ═══════════════════════════════════════════════════════ -->
  <!-- CÀN KHÔN LINH THẠCH CÁC — GIAO DIỆN TU TIÊN          -->
  <!-- ═══════════════════════════════════════════════════════ -->

  <!-- LOGIN SCREEN -->
  <div v-if="!isLoggedIn" class="login-realm">
    <div class="cosmic-particles"></div>
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
          <input v-model="authForm.full_name" type="text" placeholder="Tiên Nhân Vô Danh" />
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
        <div class="header-left">
          <span class="header-symbol">☯</span>
          <h1 class="header-title">Càn Khôn Linh Thạch Các</h1>
        </div>
        <div class="header-right">
          <span class="user-badge">🧙 {{ userName }}</span>
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

        <!-- Expense by Category -->
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

        <div class="wallet-grid">
          <div v-for="w in wallets" :key="w.id" class="wallet-card">
            <div class="wallet-card-top">
              <span class="wallet-type-icon">
                {{ w.wallet_type === 'cash' ? '💵' : w.wallet_type === 'bank' ? '🏦' : '📱' }}
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
          <h3 class="sub-title">✅ Kết Quả Linh Nhãn</h3>
          <div class="ocr-info-grid">
            <div class="ocr-info-item">
              <label>🏪 Cửa Hàng</label>
              <span>{{ ocrResult.store_name || 'N/A' }}</span>
            </div>
            <div class="ocr-info-item">
              <label>💰 Tổng Tiền</label>
              <span class="ocr-total">{{ formatVND(ocrResult.total_amount || 0) }}</span>
            </div>
            <div class="ocr-info-item">
              <label>📅 Ngày</label>
              <span>{{ ocrResult.date || 'N/A' }}</span>
            </div>
          </div>
          <div v-if="ocrResult.items && ocrResult.items.length" class="ocr-items">
            <h4>📋 Chi Tiết Sản Phẩm</h4>
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
          <div v-if="ocrResult.raw_text" class="ocr-raw">
            <h4>📝 Raw Text</h4>
            <pre>{{ ocrResult.raw_text }}</pre>
          </div>
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

      <!-- ═══════ TAB 7: AI CHAT ═══════ -->
      <section v-if="activeTab === 'chat'" class="tab-panel">
        <h2 class="section-title">💬 Khấu Bái Khí Linh — Trợ Lý AI Gemini</h2>

        <div class="chat-container">
          <div class="chat-messages" ref="chatMessages">
            <div class="chat-welcome">
              <div class="chat-ai-avatar">🔮</div>
              <p>Kính chào Đạo Hữu! Ta là <strong>Khí Linh Tiên Trí</strong>, trợ lý tài chính AI phong cách tu tiên. Hãy hỏi ta bất cứ điều gì về tài chính của đạo hữu!</p>
            </div>
            <div v-for="(msg, idx) in chatMessages" :key="idx"
                 :class="['chat-bubble', msg.role === 'user' ? 'user-bubble' : 'ai-bubble']">
              <div class="bubble-avatar">{{ msg.role === 'user' ? '🧙' : '🔮' }}</div>
              <div class="bubble-content" v-html="formatChatText(msg.text)"></div>
            </div>
            <div v-if="loading && activeTab === 'chat'" class="chat-bubble ai-bubble">
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
            <button class="btn-jade-sm" @click="sendChat" :disabled="loading || !chatInput.trim()">
              ⚡ Gửi
            </button>
          </div>
        </div>
      </section>
    </main>

    <!-- TOAST -->
    <div v-if="toast" class="toast-notification" :class="toast.type">
      {{ toast.message }}
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import axios from 'axios'

export default {
  name: 'CankKhonApp',
  setup() {
    // ─── STATE ────────────────────
    const isLoggedIn = ref(false)
    const authMode = ref('login')
    const authForm = ref({ email: '', password: '', full_name: '' })
    const token = ref('')
    const userName = ref('')
    const loading = ref(false)
    const errorMsg = ref('')
    const toast = ref(null)
    const activeTab = ref('dashboard')

    const tabs = [
      { id: 'dashboard',    icon: '📊', label: 'Tổng Quan' },
      { id: 'transactions', icon: '💸', label: 'Giao Dịch' },
      { id: 'wallets',      icon: '💳', label: 'Túi Càn Khôn' },
      { id: 'categories',   icon: '🏷️', label: 'Danh Mục' },
      { id: 'ocr',          icon: '🧾', label: 'Linh Nhãn OCR' },
      { id: 'budgets',      icon: '🎯', label: 'Hạn Mức' },
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

    // OCR
    const ocrFile = ref(null)
    const ocrPreview = ref(null)
    const ocrResult = ref(null)

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

    // ─── HELPERS ──────────────────
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

    // ─── AUTH ─────────────────────
    async function doLogin() {
      loading.value = true
      errorMsg.value = ''
      try {
        const { data } = await api.post('/api/auth/login', {
          email: authForm.value.email,
          password: authForm.value.password
        })
        token.value = data.token
        userName.value = data.full_name
        isLoggedIn.value = true
        localStorage.setItem('xianxia_token', data.token)
        localStorage.setItem('xianxia_user', data.full_name)
        await loadAllData()
      } catch (err) {
        errorMsg.value = err.response?.data?.detail || 'Lỗi đăng nhập!'
      }
      loading.value = false
    }

    async function doRegister() {
      loading.value = true
      errorMsg.value = ''
      try {
        const { data } = await api.post('/api/auth/register', authForm.value)
        token.value = data.token
        userName.value = data.full_name
        isLoggedIn.value = true
        localStorage.setItem('xianxia_token', data.token)
        localStorage.setItem('xianxia_user', data.full_name)
        await loadAllData()
      } catch (err) {
        errorMsg.value = err.response?.data?.detail || 'Lỗi đăng ký!'
      }
      loading.value = false
    }

    function doLogout() {
      isLoggedIn.value = false
      token.value = ''
      userName.value = ''
      localStorage.removeItem('xianxia_token')
      localStorage.removeItem('xianxia_user')
      authForm.value = { email: '', password: '', full_name: '' }
    }

    // ─── DATA LOADING ─────────────
    async function loadAllData() {
      await Promise.all([
        loadWallets(), loadCategories(), loadTransactions(),
        loadSummary(), loadBudgets(), checkBudgetAlerts()
      ])
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
        showToast(err.response?.data?.detail || 'Lỗi!', 'error')
      }
      loading.value = false
    }

    async function deleteWallet(id) {
      if (!confirm('Hủy Túi Càn Khôn này?')) return
      try {
        await api.delete(`/api/wallets/${id}`)
        showToast('Túi Càn Khôn đã hủy!')
        await loadWallets()
        await loadSummary()
      } catch {}
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
        showToast('👁️ Linh Nhãn đã hoàn thành phân tích!')
      } catch (err) {
        showToast(err.response?.data?.detail || 'Lỗi OCR!', 'error')
      }
      loading.value = false
    }

    // ─── AI CHAT ──────────────────
    async function sendChat() {
      if (!chatInput.value.trim()) return
      const msg = chatInput.value.trim()
      chatMessages.value.push({ role: 'user', text: msg })
      chatInput.value = ''
      await nextTick()
      scrollChat()

      loading.value = true
      try {
        const { data } = await api.post('/api/ai/chat', { message: msg })
        chatMessages.value.push({ role: 'ai', text: data.response })
      } catch (err) {
        chatMessages.value.push({
          role: 'ai',
          text: '⚠️ Tiên Trí gặp trở ngại: ' + (err.response?.data?.detail || 'Không thể kết nối.')
        })
      }
      loading.value = false
      await nextTick()
      scrollChat()
    }

    function scrollChat() {
      const el = chatMessagesEl.value
      if (el) el.scrollTop = el.scrollHeight
    }

    // ─── TAB SWITCH ───────────────
    function switchTab(tabId) {
      activeTab.value = tabId
    }

    // ─── INIT ─────────────────────
    onMounted(() => {
      const savedToken = localStorage.getItem('xianxia_token')
      const savedUser = localStorage.getItem('xianxia_user')
      if (savedToken) {
        token.value = savedToken
        userName.value = savedUser || 'Đạo Hữu'
        isLoggedIn.value = true
        loadAllData()
      }
    })

    return {
      isLoggedIn, authMode, authForm, loading, errorMsg, toast,
      activeTab, tabs, userName,
      wallets, categories, transactions, budgets, summary, budgetAlerts,
      chatMessages, chatInput, chatMessagesEl,
      txnForm, walletForm, catForm, budgetForm,
      ocrFile, ocrPreview, ocrResult,
      iconOptions,
      incomeCategories, expenseCategories, filteredCategories, maxCategoryExpense,
      formatVND, showToast, budgetPct, formatChatText,
      doLogin, doRegister, doLogout,
      switchTab, loadAllData,
      createTransaction, deleteTransaction,
      createWallet, deleteWallet,
      createCategory, deleteCategory,
      createBudget, deleteBudget,
      handleOCRUpload, handleOCRDrop, scanInvoice,
      sendChat,
    }
  }
}
</script>

<style>
/* ═══════════════════════════════════════════════════════════
   CÀN KHÔN LINH THẠCH CÁC — XIANXIA THEME CSS
   ═══════════════════════════════════════════════════════════ */

/* ─── RESET & BASE ─────────────────────── */
*, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

:root {
  --bg-primary: #0B1120;
  --bg-secondary: #111B2E;
  --bg-card: #15203A;
  --bg-card-hover: #1A2744;
  --jade: #059669;
  --jade-glow: #10B981;
  --jade-dim: #064E3B;
  --gold: #D97706;
  --gold-glow: #F59E0B;
  --gold-dim: #78350F;
  --purple: #7C3AED;
  --purple-glow: #A78BFA;
  --crimson: #DC2626;
  --crimson-glow: #F87171;
  --text-primary: #E2E8F0;
  --text-secondary: #94A3B8;
  --text-dim: #64748B;
  --border: #1E293B;
  --border-glow: rgba(5, 150, 105, 0.3);
  --radius: 12px;
  --radius-lg: 20px;
  --shadow-jade: 0 0 20px rgba(5, 150, 105, 0.15), 0 0 60px rgba(5, 150, 105, 0.05);
  --shadow-gold: 0 0 20px rgba(217, 119, 6, 0.15);
  --font-calligraphy: 'Noto Serif TC', 'Georgia', serif;
  --font-body: 'Inter', -apple-system, sans-serif;
}

body {
  font-family: var(--font-body);
  background: var(--bg-primary);
  color: var(--text-primary);
  line-height: 1.6;
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
}

/* ─── SCROLLBAR ────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--jade-dim); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--jade); }

/* ─── ANIMATIONS ───────────────────────── */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes glowPulse {
  0%, 100% { box-shadow: 0 0 15px rgba(5, 150, 105, 0.2); }
  50% { box-shadow: 0 0 30px rgba(5, 150, 105, 0.4), 0 0 60px rgba(5, 150, 105, 0.1); }
}
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}
@keyframes rotateSymbol {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
@keyframes cosmicDrift {
  0% { opacity: 0; transform: translate(0, 0) scale(0); }
  50% { opacity: 1; }
  100% { opacity: 0; transform: translate(var(--dx, 50px), var(--dy, -80px)) scale(1.5); }
}
@keyframes typingBounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

/* ─── LOGIN REALM ──────────────────────── */
.login-realm {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0B1120 0%, #111B2E 30%, #0F172A 60%, #1A0B2E 100%);
  position: relative;
  overflow: hidden;
}

.login-realm::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 400px 400px at 20% 30%, rgba(5, 150, 105, 0.08) 0%, transparent 70%),
    radial-gradient(ellipse 300px 300px at 80% 70%, rgba(124, 58, 237, 0.08) 0%, transparent 70%),
    radial-gradient(ellipse 200px 200px at 50% 50%, rgba(217, 119, 6, 0.05) 0%, transparent 70%);
  pointer-events: none;
}

.cosmic-particles {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}
.cosmic-particles::before,
.cosmic-particles::after {
  content: '✦';
  position: absolute;
  font-size: 10px;
  color: var(--jade-glow);
  animation: cosmicDrift 4s infinite ease-out;
}
.cosmic-particles::before { top: 30%; left: 20%; --dx: 40px; --dy: -60px; }
.cosmic-particles::after { top: 60%; left: 70%; --dx: -30px; --dy: -50px; animation-delay: 2s; color: var(--gold-glow); }

.login-card {
  position: relative;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 48px 40px;
  width: 100%;
  max-width: 460px;
  animation: fadeIn 0.8s ease-out, glowPulse 4s ease-in-out infinite;
}

.login-header { text-align: center; margin-bottom: 36px; }

.dao-symbol {
  font-size: 56px;
  display: inline-block;
  animation: rotateSymbol 20s linear infinite;
  filter: drop-shadow(0 0 15px var(--jade-glow));
  margin-bottom: 16px;
}

.title-calligraphy {
  font-family: var(--font-calligraphy);
  font-size: 28px;
  font-weight: 900;
  background: linear-gradient(135deg, var(--jade-glow), var(--gold-glow));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 2px;
}

.subtitle-glow {
  color: var(--text-secondary);
  font-size: 13px;
  margin-top: 8px;
  letter-spacing: 1px;
}

.form-title {
  font-family: var(--font-calligraphy);
  color: var(--gold-glow);
  font-size: 18px;
  margin-bottom: 24px;
  text-align: center;
}

.input-group-xianxia {
  margin-bottom: 16px;
}
.input-group-xianxia label {
  display: block;
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 6px;
  font-weight: 500;
}
.input-group-xianxia input,
.input-group-xianxia select {
  width: 100%;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 14px;
  font-family: var(--font-body);
  transition: all 0.3s ease;
  outline: none;
}
.input-group-xianxia input:focus,
.input-group-xianxia select:focus {
  border-color: var(--jade);
  box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.15);
}
.input-group-xianxia input::placeholder {
  color: var(--text-dim);
}

.btn-jade {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, var(--jade) 0%, var(--jade-glow) 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: var(--font-body);
  letter-spacing: 0.5px;
}
.btn-jade:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(5, 150, 105, 0.35);
}
.btn-jade:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.auth-switch {
  text-align: center;
  margin-top: 20px;
  font-size: 13px;
  color: var(--text-dim);
}
.auth-switch span {
  color: var(--jade-glow);
  cursor: pointer;
  font-weight: 600;
}
.auth-switch span:hover { text-decoration: underline; }

.error-banner {
  margin-top: 16px;
  padding: 12px;
  background: rgba(220, 38, 38, 0.1);
  border: 1px solid rgba(220, 38, 38, 0.3);
  border-radius: 8px;
  color: var(--crimson-glow);
  text-align: center;
  font-size: 13px;
}

/* ─── MAIN APP REALM ───────────────────── */
.app-realm {
  min-height: 100vh;
  background:
    radial-gradient(ellipse 600px 600px at 10% 0%, rgba(5, 150, 105, 0.04) 0%, transparent 60%),
    radial-gradient(ellipse 600px 600px at 90% 100%, rgba(124, 58, 237, 0.04) 0%, transparent 60%),
    var(--bg-primary);
}

/* ─── HEADER ───────────────────────────── */
.realm-header {
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(12px);
  background: rgba(17, 27, 46, 0.9);
}
.header-inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.header-symbol {
  font-size: 28px;
  animation: rotateSymbol 30s linear infinite;
  filter: drop-shadow(0 0 8px var(--jade));
}
.header-title {
  font-family: var(--font-calligraphy);
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(90deg, var(--jade-glow), var(--gold-glow));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
.user-badge {
  font-size: 14px;
  color: var(--text-secondary);
  padding: 6px 14px;
  background: var(--bg-card);
  border-radius: 20px;
  border: 1px solid var(--border);
}
.btn-logout {
  padding: 6px 14px;
  background: transparent;
  border: 1px solid var(--crimson);
  color: var(--crimson-glow);
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  font-family: var(--font-body);
  transition: all 0.3s;
}
.btn-logout:hover {
  background: rgba(220, 38, 38, 0.1);
}

/* ─── TAB NAV ──────────────────────────── */
.tab-nav {
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 64px;
  z-index: 99;
}
.tab-nav-inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  gap: 4px;
  overflow-x: auto;
  scrollbar-width: none;
}
.tab-nav-inner::-webkit-scrollbar { display: none; }

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 18px;
  border: none;
  background: transparent;
  color: var(--text-dim);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  border-bottom: 2px solid transparent;
  transition: all 0.3s;
  font-family: var(--font-body);
}
.tab-btn:hover {
  color: var(--text-primary);
  background: rgba(5, 150, 105, 0.05);
}
.tab-btn.active {
  color: var(--jade-glow);
  border-bottom-color: var(--jade-glow);
  background: rgba(5, 150, 105, 0.08);
}
.tab-icon { font-size: 16px; }

/* ─── CONTENT ──────────────────────────── */
.realm-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 32px 24px 80px;
}

.tab-panel {
  animation: fadeIn 0.4s ease-out;
}

.section-title {
  font-family: var(--font-calligraphy);
  font-size: 24px;
  font-weight: 700;
  color: var(--gold-glow);
  margin-bottom: 28px;
  letter-spacing: 1px;
}

.sub-title {
  font-family: var(--font-calligraphy);
  font-size: 16px;
  color: var(--text-primary);
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
}

/* ─── METRICS ──────────────────────────── */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 36px;
}

.metric-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 18px;
  transition: all 0.4s ease;
  position: relative;
  overflow: hidden;
}
.metric-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  border-radius: var(--radius) var(--radius) 0 0;
}
.metric-card.jade::before { background: linear-gradient(90deg, var(--jade), var(--jade-glow)); }
.metric-card.crimson::before { background: linear-gradient(90deg, var(--crimson), var(--crimson-glow)); }
.metric-card.gold::before { background: linear-gradient(90deg, var(--gold), var(--gold-glow)); }
.metric-card.purple::before { background: linear-gradient(90deg, var(--purple), var(--purple-glow)); }

.metric-card:hover {
  transform: translateY(-4px);
  border-color: var(--border-glow);
}
.metric-card.jade:hover { box-shadow: var(--shadow-jade); }
.metric-card.crimson:hover { box-shadow: 0 0 20px rgba(220, 38, 38, 0.15); }
.metric-card.gold:hover { box-shadow: var(--shadow-gold); }
.metric-card.purple:hover { box-shadow: 0 0 20px rgba(124, 58, 237, 0.15); }

.metric-icon {
  font-size: 36px;
  animation: float 3s ease-in-out infinite;
}
.metric-card:nth-child(2) .metric-icon { animation-delay: 0.5s; }
.metric-card:nth-child(3) .metric-icon { animation-delay: 1s; }
.metric-card:nth-child(4) .metric-icon { animation-delay: 1.5s; }

.metric-info { display: flex; flex-direction: column; gap: 6px; }
.metric-label { font-size: 13px; color: var(--text-secondary); font-weight: 500; }
.metric-value {
  font-size: 22px;
  font-weight: 700;
  font-family: var(--font-calligraphy);
  color: var(--text-primary);
}
.metric-value.positive { color: var(--jade-glow); }
.metric-value.negative { color: var(--crimson-glow); }

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
  background: rgba(220, 38, 38, 0.1);
  border: 1px solid rgba(220, 38, 38, 0.3);
}
.alert-card.warning {
  background: rgba(217, 119, 6, 0.1);
  border: 1px solid rgba(217, 119, 6, 0.3);
}
.alert-icon { font-size: 20px; }
.alert-msg { flex: 1; font-size: 14px; color: var(--text-primary); }
.alert-pct { font-weight: 700; font-size: 15px; color: var(--crimson-glow); }

/* ─── TABLE ────────────────────────────── */
.table-scroll { overflow-x: auto; }

.xianxia-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}
.xianxia-table thead th {
  text-align: left;
  padding: 12px 16px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 1px;
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
}
.xianxia-table tbody td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  color: var(--text-primary);
  vertical-align: middle;
}
.xianxia-table tbody tr {
  transition: background 0.2s;
}
.xianxia-table tbody tr:hover {
  background: rgba(5, 150, 105, 0.04);
}

.cat-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: var(--bg-secondary);
  border-radius: 6px;
  font-size: 13px;
  white-space: nowrap;
}

.amt-income { color: var(--jade-glow); font-weight: 600; white-space: nowrap; }
.amt-expense { color: var(--crimson-glow); font-weight: 600; white-space: nowrap; }
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
  color: var(--text-secondary);
  white-space: nowrap;
}
.cat-bar-track {
  flex: 1;
  height: 10px;
  background: var(--bg-secondary);
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
  color: var(--text-primary);
  white-space: nowrap;
}

/* ─── FORM CARD ────────────────────────── */
.form-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 28px;
  margin-bottom: 24px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

/* ─── WALLET CARDS ─────────────────────── */
.wallet-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-top: 28px;
}
.wallet-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 24px;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}
.wallet-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--jade), var(--gold-glow), var(--purple-glow));
}
.wallet-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-jade);
  border-color: var(--border-glow);
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
  font-size: 16px;
  color: var(--text-primary);
  margin-bottom: 8px;
}
.wallet-balance {
  font-size: 24px;
  font-weight: 700;
  color: var(--jade-glow);
  font-family: var(--font-calligraphy);
  margin-bottom: 4px;
}
.wallet-type-label {
  font-size: 12px;
  color: var(--text-dim);
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
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  font-size: 14px;
  transition: all 0.3s;
}
.cat-item:hover { border-color: var(--border-glow); }
.cat-item.income { border-left: 3px solid var(--jade); }
.cat-item.expense { border-left: 3px solid var(--crimson); }

/* ─── BUTTONS SMALL ────────────────────── */
.btn-sm-danger {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid rgba(220, 38, 38, 0.3);
  border-radius: 6px;
  color: var(--crimson-glow);
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}
.btn-sm-danger:hover {
  background: rgba(220, 38, 38, 0.15);
  border-color: var(--crimson);
}

/* ─── OCR UPLOAD ───────────────────────── */
.hint-text {
  color: var(--text-dim);
  font-size: 13px;
  margin-bottom: 16px;
}
.upload-zone {
  border: 2px dashed var(--border);
  border-radius: var(--radius);
  padding: 48px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: var(--bg-secondary);
}
.upload-zone:hover {
  border-color: var(--jade);
  background: rgba(5, 150, 105, 0.05);
}
.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: var(--text-dim);
}
.upload-icon { font-size: 40px; }
.ocr-preview-img {
  max-width: 100%;
  max-height: 300px;
  border-radius: 8px;
  object-fit: contain;
}

.ocr-result-card {
  background: var(--bg-card);
  border: 1px solid var(--jade-dim);
  border-radius: var(--radius);
  padding: 28px;
  margin-top: 24px;
  animation: fadeIn 0.5s ease-out;
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
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 1px;
}
.ocr-info-item span {
  font-size: 16px;
  color: var(--text-primary);
  font-weight: 600;
}
.ocr-total {
  color: var(--jade-glow) !important;
  font-family: var(--font-calligraphy);
  font-size: 22px !important;
}
.ocr-items { margin-top: 16px; }
.ocr-items h4 { margin-bottom: 12px; color: var(--text-secondary); font-size: 14px; }
.ocr-raw { margin-top: 16px; }
.ocr-raw h4 { margin-bottom: 8px; color: var(--text-dim); font-size: 13px; }
.ocr-raw pre {
  background: var(--bg-secondary);
  padding: 16px;
  border-radius: 8px;
  font-size: 12px;
  color: var(--text-secondary);
  overflow-x: auto;
  white-space: pre-wrap;
}

/* ─── BUDGETS ──────────────────────────── */
.budget-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 16px;
  margin-top: 24px;
}
.budget-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
  transition: all 0.3s;
}
.budget-card:hover { border-color: var(--border-glow); }
.budget-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 15px;
  font-weight: 600;
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
  background: var(--bg-secondary);
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
.pct-safe { color: var(--jade-glow); }
.pct-warning { color: var(--gold-glow); }
.pct-danger { color: var(--crimson-glow); }

/* ─── AI CHAT ──────────────────────────── */
.chat-container {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 280px);
  min-height: 500px;
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
  background: rgba(124, 58, 237, 0.08);
  border: 1px solid rgba(124, 58, 237, 0.2);
  border-radius: var(--radius);
  margin-bottom: 8px;
}
.chat-ai-avatar {
  font-size: 36px;
  animation: float 3s ease-in-out infinite;
}
.chat-welcome p {
  font-size: 14px;
  color: var(--text-secondary);
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
  background: linear-gradient(135deg, var(--jade), var(--jade-dim));
  color: white;
  border-bottom-right-radius: 4px;
}
.ai-bubble .bubble-content {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
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
  background: var(--jade-glow);
  border-radius: 50%;
  animation: typingBounce 1.4s infinite ease-in-out;
}
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

.chat-input-area {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--border);
  background: var(--bg-secondary);
}
.chat-input-area input {
  flex: 1;
  padding: 12px 16px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 14px;
  outline: none;
  font-family: var(--font-body);
  transition: border-color 0.3s;
}
.chat-input-area input:focus {
  border-color: var(--purple);
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.15);
}

.btn-jade-sm {
  padding: 12px 24px;
  background: linear-gradient(135deg, var(--purple), var(--purple-glow));
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  font-family: var(--font-body);
  font-size: 14px;
  transition: all 0.3s;
  white-space: nowrap;
}
.btn-jade-sm:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3);
}
.btn-jade-sm:disabled { opacity: 0.5; cursor: not-allowed; }

/* ─── TOAST ────────────────────────────── */
.toast-notification {
  position: fixed;
  bottom: 30px;
  right: 30px;
  padding: 14px 24px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  z-index: 9999;
  animation: fadeIn 0.3s ease-out;
  max-width: 400px;
  backdrop-filter: blur(8px);
}
.toast-notification.success {
  background: rgba(5, 150, 105, 0.9);
  color: white;
  border: 1px solid var(--jade-glow);
  box-shadow: 0 8px 30px rgba(5, 150, 105, 0.3);
}
.toast-notification.error {
  background: rgba(220, 38, 38, 0.9);
  color: white;
  border: 1px solid var(--crimson-glow);
  box-shadow: 0 8px 30px rgba(220, 38, 38, 0.3);
}

/* ─── EMPTY STATE ──────────────────────── */
.empty-state {
  text-align: center;
  padding: 32px;
  color: var(--text-dim);
  font-size: 14px;
  font-style: italic;
}

/* ─── RESPONSIVE ───────────────────────── */
@media (max-width: 768px) {
  .header-title { font-size: 16px; }
  .realm-content { padding: 20px 16px 60px; }
  .metrics-grid { grid-template-columns: 1fr; }
  .categories-split { grid-template-columns: 1fr; }
  .form-grid { grid-template-columns: 1fr; }
  .wallet-grid { grid-template-columns: 1fr; }
  .budget-list { grid-template-columns: 1fr; }
  .tab-btn .tab-label { display: none; }
  .tab-btn { padding: 14px 12px; }
  .login-card { margin: 16px; padding: 32px 24px; }
  .chat-container { height: calc(100vh - 240px); min-height: 400px; }
  .user-badge { display: none; }
}

@media (max-width: 480px) {
  .metric-value { font-size: 18px; }
  .section-title { font-size: 20px; }
  .cat-bar-label { min-width: 120px; font-size: 12px; }
  .cat-bar-value { min-width: 90px; font-size: 12px; }
}
</style>
