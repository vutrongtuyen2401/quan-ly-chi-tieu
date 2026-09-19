<template>
  <div class="wallets-realm">
    <!-- Subtle Ambient Glow Orbs -->
    <div class="ambient-glow-orb orb-primary" aria-hidden="true"></div>
    <div class="ambient-glow-orb orb-secondary" aria-hidden="true"></div>

    <!-- ═══ HEADER & ACTION BAR ═══ -->
    <section class="wallets-page-header">
      <div class="header-text-group">
        <div class="header-badge-row">
          <div class="status-pulse-dot"></div>
          <span class="badge-text">PHÁP BẢO TỒN KHO • TIỀN TỆ TRẬN PHÁP</span>
        </div>
        <h1 class="page-title">Túi Càn Khôn (Quản Lý Ví Nguồn)</h1>
        <p class="page-subtitle">
          Quản lý các nguồn tiền mặt, tài khoản ngân hàng, ví điện tử và điều chuyển nội bộ theo chuẩn mực song đối nguyên tử (Atomic Two-sided Transfers).
        </p>
      </div>

      <div class="header-action-group">
        <!-- Toggle Transfer Section Button -->
        <button
          type="button"
          class="btn-stitch-secondary"
          :class="{ active: showTransferPanel }"
          @click="toggleTransferPanel"
          title="Mở bảng điều chuyển linh thạch"
        >
          <span class="material-symbols-outlined icon-tertiary">sync_alt</span>
          <span>Điều Chuyển Linh Thạch</span>
        </button>

        <!-- Toggle Add Wallet Form Button -->
        <button
          type="button"
          class="btn-stitch-primary"
          @click="showAddWalletForm = !showAddWalletForm"
          title="Khai mở túi càn khôn mới"
        >
          <span class="material-symbols-outlined">{{ showAddWalletForm ? 'close' : 'add' }}</span>
          <span>{{ showAddWalletForm ? 'Đóng Biểu Mẫu' : 'Khai Mở Ví Mới' }}</span>
        </button>
      </div>
    </section>

    <!-- ═══ TOTAL LIQUIDITY MASTER PANEL (HERO) ═══ -->
    <section class="liquidity-hero-card" aria-label="Tổng hợp thanh khoản">
      <div class="hero-content-grid">
        <!-- Left: Total Liquidity Overview -->
        <div class="hero-summary-col">
          <div class="hero-badge-row">
            <span class="hero-chip">
              <span class="pulse-indicator"></span>
              Tổng Hợp {{ wallets.length }} Ví Hoạt Động
            </span>
            <span class="hero-caption">Chu kỳ quyết toán: Nhật Triều</span>
          </div>

          <div class="hero-balance-label">Tổng Số Dư Khả Dụng Toàn Hệ Thống</div>

          <div class="hero-balance-display">
            <span class="balance-number tabular-num font-bold">
              {{ formatVND(totalBalance) }}
            </span>
            <span class="currency-tag">₫</span>
            <span class="trend-pill" v-if="wallets.length > 0">
              <span class="material-symbols-outlined icon-xs">trending_up</span>
              Cân Bằng Nội Bộ
            </span>
          </div>

          <p class="hero-desc">
            Dòng thanh khoản linh hoạt đã kết nối qua linh thạch ấn tín. Mọi biến động được đối soát nguyên tử và bảo toàn giá trị pháp bảo.
          </p>
        </div>

        <!-- Right: Liquidity Allocation Bar & Legend -->
        <div class="hero-allocation-col">
          <div class="allocation-header">
            <span class="allocation-title">Phân Bổ Dòng Chảy Linh Thạch</span>
            <span class="allocation-status tabular-num">
              {{ totalBalance > 0 ? '100% Hoàn Bị' : 'Chưa Có Dữ Liệu' }}
            </span>
          </div>

          <!-- Progress Composition Bar -->
          <div class="composition-bar-track" v-if="totalBalance > 0">
            <div
              v-for="(w, idx) in wallets"
              :key="'bar-' + w.id"
              class="bar-segment"
              :style="{
                width: getWalletPct(w) + '%',
                backgroundColor: getWalletColor(idx)
              }"
              :title="`${w.wallet_name}: ${formatVND(w.balance)} (${getWalletPct(w)}%)`"
            ></div>
          </div>
          <div class="composition-bar-empty" v-else>
            <div class="bar-empty-fill"></div>
          </div>

          <!-- Legend Strip -->
          <div class="allocation-legend-grid" v-if="wallets.length">
            <div
              v-for="(w, idx) in wallets"
              :key="'legend-' + w.id"
              class="legend-item"
            >
              <span
                class="legend-dot"
                :style="{ backgroundColor: getWalletColor(idx) }"
              ></span>
              <span class="legend-name truncate" :title="w.wallet_name">
                {{ w.wallet_name }}
              </span>
              <span class="legend-pct tabular-num ml-auto">
                {{ getWalletPct(w) }}%
              </span>
            </div>
          </div>
          <div v-else class="legend-empty">
            <span>Chưa có nguồn tiền nào để tính toán phân bổ...</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══ COLLAPSIBLE CREATE WALLET FORM ═══ -->
    <transition name="tray-expand">
      <section v-if="showAddWalletForm" class="add-wallet-card" aria-label="Khai mở ví mới">
        <div class="card-header-row">
          <div class="title-with-icon">
            <span class="material-symbols-outlined text-jade">add_card</span>
            <h2 class="card-title">Khai Mở Túi Càn Khôn Mới</h2>
          </div>
          <button
            type="button"
            class="btn-icon-close"
            @click="showAddWalletForm = false"
            title="Đóng biểu mẫu"
          >
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>

        <div class="form-grid">
          <div class="input-col">
            <label class="input-label">Tên Ví / Pháp Bảo</label>
            <input
              v-model="walletForm.wallet_name"
              type="text"
              list="bankList"
              placeholder="VD: Linh Mạch Vietcombank..."
              class="stitch-input"
            />
            <datalist id="bankList">
              <option value="Linh Mạch Vietcombank"></option>
              <option value="Linh Mạch Techcombank"></option>
              <option value="Linh Mạch BIDV"></option>
              <option value="Linh Mạch VietinBank"></option>
              <option value="Linh Mạch Agribank"></option>
              <option value="Linh Mạch MB Bank"></option>
              <option value="Linh Mạch ACB"></option>
              <option value="Linh Mạch VPBank"></option>
              <option value="Linh Mạch Sacombank"></option>
              <option value="Linh Mạch TPBank"></option>
              <option value="Linh Mạch HDBank"></option>
              <option value="Linh Mạch MoMo"></option>
              <option value="Linh Mạch ZaloPay"></option>
              <option value="Linh Mạch ViettelPay"></option>
              <option value="Linh Mạch Tiền Mặt"></option>
            </datalist>
          </div>

          <div class="input-col">
            <label class="input-label">Số Dư Ban Đầu (VNĐ)</label>
            <input
              v-model.number="walletForm.balance"
              type="number"
              placeholder="0"
              min="0"
              class="stitch-input tabular-num"
            />
          </div>

          <div class="input-col">
            <label class="input-label">Loại Ví</label>
            <select v-model="walletForm.wallet_type" class="stitch-select">
              <option value="cash">💵 Tiền Mặt Động Phủ</option>
              <option value="bank">🏦 Tài Khoản Ngân Hàng</option>
              <option value="e-wallet">📱 Ví Điện Tử Tiện Lợi</option>
            </select>
          </div>
        </div>

        <div class="form-actions-row">
          <button
            type="button"
            class="btn-stitch-primary"
            @click="$emit('create-wallet')"
            :disabled="loading || !walletForm.wallet_name"
          >
            <span class="material-symbols-outlined">auto_fix_high</span>
            <span>{{ loading ? 'Đang khai mở...' : 'Khai Mở Ví Mới' }}</span>
          </button>
        </div>
      </section>
    </transition>

    <!-- ═══ WALLETS CARDS GRID ═══ -->
    <section class="wallets-grid-section" aria-label="Danh sách ví">
      <div class="section-header-row">
        <div class="title-with-icon">
          <span class="material-symbols-outlined text-jade">inventory_2</span>
          <h2 class="section-title">Pháp Trận Danh Sách Ví Nguồn</h2>
        </div>
        <span class="section-caption">Quản lý và điều phối các dòng lưu chuyển tiền tệ</span>
      </div>

      <!-- Grid Cards -->
      <div class="wallets-cards-grid" v-if="wallets.length">
        <div
          v-for="w in wallets"
          :key="w.id"
          class="wallet-card-item"
        >
          <!-- Corner Ambient Accent -->
          <div class="card-ambient-corner" :class="'corner-' + (w.wallet_type || 'cash')"></div>

          <!-- Card Header -->
          <div class="card-top-row">
            <div class="wallet-type-avatar" :class="'avatar-' + (w.wallet_type || 'cash')">
              <span class="material-symbols-outlined">
                {{ getWalletIcon(w.wallet_type) }}
              </span>
            </div>
            <span class="wallet-type-chip" :class="'chip-' + (w.wallet_type || 'cash')">
              {{ getWalletTypeLabel(w.wallet_type) }}
            </span>
          </div>

          <!-- Card Body -->
          <div class="card-body-meta">
            <h3 class="wallet-card-name truncate" :title="w.wallet_name">
              {{ w.wallet_name }}
            </h3>
            <p class="wallet-card-subtitle">
              {{ getWalletSubtext(w.wallet_type) }}
            </p>
          </div>

          <!-- Card Balance -->
          <div class="card-balance-block">
            <span class="balance-sublabel">Số dư khả dụng</span>
            <div class="balance-val-row">
              <span
                class="balance-amt tabular-num font-currency-display"
                :class="w.balance >= 0 ? 'text-on-surface' : 'text-danger'"
              >
                {{ formatVND(w.balance) }}
              </span>
            </div>
          </div>

          <!-- Card Action Buttons -->
          <div class="card-actions-row">
            <button
              type="button"
              class="btn-card-transfer"
              @click="initiateTransferFrom(w.id)"
              title="Chuyển tiền từ ví này"
            >
              <span class="material-symbols-outlined icon-sm">sync_alt</span>
              <span>Chuyển</span>
            </button>
            <button
              type="button"
              class="btn-card-icon btn-edit"
              @click="$emit('edit-wallet', w)"
              title="Chỉnh sửa thông tin ví"
            >
              <span class="material-symbols-outlined icon-sm">edit</span>
            </button>
            <button
              type="button"
              class="btn-card-icon btn-delete"
              @click="$emit('delete-wallet', w.id)"
              title="Hủy / Xóa ví nguồn"
            >
              <span class="material-symbols-outlined icon-sm">delete</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="wallets-empty-state">
        <div class="empty-icon-wrap">
          <span class="material-symbols-outlined empty-icon">account_balance_wallet</span>
        </div>
        <h3 class="empty-title">Chưa Có Túi Càn Khôn Nào</h3>
        <p class="empty-desc">
          Đạo hữu hãy bắt đầu bằng việc khai mở một ví nguồn đầu tiên để theo dõi dòng lưu chuyển ngân thạch.
        </p>
        <button
          type="button"
          class="btn-stitch-primary"
          @click="showAddWalletForm = true"
        >
          <span class="material-symbols-outlined">add</span>
          <span>Khai Mở Ví Đầu Tiên</span>
        </button>
      </div>
    </section>

    <!-- ═══ INTERNAL ATOMIC TRANSFER PANEL ═══ -->
    <transition name="tray-expand">
      <section
        v-if="showTransferPanel"
        ref="transferSectionRef"
        class="transfer-master-section"
        aria-label="Lệnh điều chuyển linh thạch"
      >
        <div class="transfer-grid-layout">
          <!-- Left: Transfer Form (7 cols) -->
          <div class="transfer-form-card">
            <div class="transfer-form-header">
              <div class="transfer-title-group">
                <div class="icon-avatar-jade">
                  <span class="material-symbols-outlined">swap_horiz</span>
                </div>
                <div>
                  <h2 class="transfer-card-title">Lệnh Điều Chuyển Linh Thạch</h2>
                  <p class="transfer-card-desc">
                    Quy trình chuyển dịch năng lượng hai chiều đối ứng (Atomic &amp; Two-sided)
                  </p>
                </div>
              </div>
              <div class="idempotency-badge">
                <span class="material-symbols-outlined icon-xs">lock</span>
                <span>Idempotent Guard</span>
              </div>
            </div>

            <!-- Transfer Form -->
            <form class="transfer-inputs-flow" @submit.prevent="$emit('do-transfer')">
              <!-- Wallets Selection Row (From -> To) -->
              <div class="wallet-select-pair-row">
                <!-- From Wallet -->
                <div class="select-col">
                  <label class="input-label-pair">
                    <span class="dot-from"></span>
                    <span>Ví Nguồn (Xuất)</span>
                  </label>
                  <select
                    v-model="transferForm.from_wallet_id"
                    class="stitch-select-large"
                    required
                  >
                    <option :value="null" disabled>— Chọn ví nguồn xuất tiền —</option>
                    <option
                      v-for="w in wallets"
                      :key="'from-' + w.id"
                      :value="w.id"
                    >
                      {{ getWalletTypeLabel(w.wallet_type) }} • {{ w.wallet_name }} ({{ formatVND(w.balance) }})
                    </option>
                  </select>
                </div>

                <!-- Swap Button -->
                <button
                  type="button"
                  class="btn-swap-wallets"
                  @click="swapTransferWallets"
                  title="Đảo chiều ví nguồn và đích"
                >
                  <span class="material-symbols-outlined">swap_horiz</span>
                </button>

                <!-- To Wallet -->
                <div class="select-col">
                  <label class="input-label-pair">
                    <span class="dot-to"></span>
                    <span>Ví Đích (Nhập)</span>
                  </label>
                  <select
                    v-model="transferForm.to_wallet_id"
                    class="stitch-select-large"
                    required
                  >
                    <option :value="null" disabled>— Chọn ví đích nhận tiền —</option>
                    <option
                      v-for="w in wallets"
                      :key="'to-' + w.id"
                      :value="w.id"
                      :disabled="w.id === transferForm.from_wallet_id"
                    >
                      {{ getWalletTypeLabel(w.wallet_type) }} • {{ w.wallet_name }} ({{ formatVND(w.balance) }})
                    </option>
                  </select>
                </div>
              </div>

              <!-- Transfer Amount + Preset Fast Buttons -->
              <div class="transfer-amount-block">
                <div class="amount-label-row">
                  <label class="input-label">Số Tiền Cần Điều Chuyển</label>
                  <span class="rate-badge">Tỷ lệ quy đổi: 1:1 nội bộ • Miễn phí ấn chú</span>
                </div>
                <div class="amount-input-wrap">
                  <input
                    v-model.number="transferForm.amount"
                    type="number"
                    placeholder="0"
                    min="1"
                    class="stitch-input-large tabular-num"
                    required
                  />
                  <span class="currency-affix">₫</span>
                </div>

                <!-- Quick Amount Pill Buttons -->
                <div class="quick-pills-row">
                  <button
                    type="button"
                    class="pill-btn"
                    @click="setQuickAmount(1000000)"
                  >
                    1.000.000 ₫
                  </button>
                  <button
                    type="button"
                    class="pill-btn"
                    @click="setQuickAmount(2000000)"
                  >
                    2.000.000 ₫
                  </button>
                  <button
                    type="button"
                    class="pill-btn"
                    @click="setQuickAmount(5000000)"
                  >
                    5.000.000 ₫
                  </button>
                  <button
                    type="button"
                    class="pill-btn"
                    @click="setQuickAmount(10000000)"
                  >
                    10.000.000 ₫
                  </button>
                  <button
                    type="button"
                    class="pill-btn pill-btn-all ml-auto"
                    @click="setAllAvailableAmount"
                    title="Chuyển toàn bộ số dư của ví nguồn"
                  >
                    Toàn Bộ Khả Dụng
                  </button>
                </div>
              </div>

              <!-- Security & Idempotency Notice Box -->
              <div class="acid-security-box">
                <span class="material-symbols-outlined text-jade acid-icon">verified_user</span>
                <div class="acid-text-wrap">
                  <span class="acid-title">Bảo Toàn Chu Kỳ Nguyên Tử (ACID)</span>
                  <p class="acid-desc">
                    Lệnh chuyển sẽ tự động khởi tạo đồng thời 2 bản ghi giao dịch đối ứng (Trừ tiền nguồn và cộng tiền đích) với thuật toán chống trùng lặp. Số dư điều hòa tức thì.
                  </p>
                </div>
              </div>

              <!-- Submit Action Button -->
              <div class="transfer-btn-wrap">
                <button
                  type="submit"
                  class="btn-stitch-transfer-submit"
                  :disabled="loading || !canSubmitTransfer"
                >
                  <span class="material-symbols-outlined">bolt</span>
                  <span>{{ loading ? 'Đang thực hiện chuyển...' : 'Xác Nhận Thực Hiện Điều Chuyển' }}</span>
                  <span class="tag-auto-oppose">Đối Ứng Tự Động</span>
                </button>
              </div>
            </form>
          </div>

          <!-- Right: Mini Analytics & Transfer Simulation (5 cols) -->
          <div class="transfer-companion-col">
            <!-- Dynamic Simulation Diagram Card -->
            <div class="simulation-card">
              <div class="sim-header">
                <span class="sim-caption">Mô Phỏng Dòng Chảy</span>
                <span
                  class="sim-badge"
                  :class="canSubmitTransfer ? 'badge-ready' : 'badge-idle'"
                >
                  {{ canSubmitTransfer ? 'Sẵn Sàng Thực Thi' : 'Đang Chờ Kích Hoạt' }}
                </span>
              </div>

              <!-- Dynamic Visualization Box -->
              <div class="simulation-diagram-box">
                <div class="diagram-nodes-row">
                  <!-- From Node -->
                  <div class="diagram-node">
                    <span class="material-symbols-outlined node-icon text-jade">
                      {{ getWalletIcon(selectedFromWallet?.wallet_type) }}
                    </span>
                    <span class="node-name truncate" :title="selectedFromWallet?.wallet_name || 'Ví Nguồn'">
                      {{ selectedFromWallet?.wallet_name || 'Ví Nguồn' }}
                    </span>
                    <span class="node-delta text-danger tabular-num">
                      -{{ formatVND(transferForm.amount || 0) }}
                    </span>
                  </div>

                  <!-- Animated Vector Path -->
                  <div class="diagram-path">
                    <svg class="path-svg" fill="none" viewBox="0 0 100 24">
                      <path
                        class="path-line"
                        d="M0 12 H100"
                        stroke="currentColor"
                        stroke-dasharray="4 4"
                        stroke-width="2"
                      ></path>
                      <circle class="path-orb" cx="50" cy="12" r="4"></circle>
                      <path
                        class="path-arrow"
                        d="M92 7 L100 12 L92 17"
                        stroke="currentColor"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                      ></path>
                    </svg>
                    <span class="path-amt tabular-num">
                      {{ formatVND(transferForm.amount || 0) }}
                    </span>
                  </div>

                  <!-- To Node -->
                  <div class="diagram-node">
                    <span class="material-symbols-outlined node-icon text-secondary">
                      {{ getWalletIcon(selectedToWallet?.wallet_type) }}
                    </span>
                    <span class="node-name truncate" :title="selectedToWallet?.wallet_name || 'Ví Đích'">
                      {{ selectedToWallet?.wallet_name || 'Ví Đích' }}
                    </span>
                    <span class="node-delta text-jade tabular-num">
                      +{{ formatVND(transferForm.amount || 0) }}
                    </span>
                  </div>
                </div>

                <!-- Projected Balance Line -->
                <div class="sim-projected-row">
                  <span class="projected-label">Dư nợ sau chuyển (dự kiến):</span>
                  <div class="projected-vals tabular-num">
                    <span v-if="selectedFromWallet">
                      {{ selectedFromWallet.wallet_name }}: {{ formatVND(projectedFromBalance) }}
                    </span>
                    <span v-if="selectedFromWallet && selectedToWallet"> • </span>
                    <span v-if="selectedToWallet">
                      {{ selectedToWallet.wallet_name }}: {{ formatVND(projectedToBalance) }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Quick Rules Strip -->
              <div class="sim-rules-list">
                <div class="rule-item">
                  <span class="material-symbols-outlined text-jade icon-xs">check_circle</span>
                  <span>Không ảnh hưởng đến báo cáo Tổng Thu / Tổng Chi thực tế trong tháng.</span>
                </div>
                <div class="rule-item">
                  <span class="material-symbols-outlined text-jade icon-xs">check_circle</span>
                  <span>Khởi tạo 2 giao dịch liên kết đối ứng với định danh đồng bộ.</span>
                </div>
                <div class="rule-item">
                  <span class="material-symbols-outlined text-jade icon-xs">check_circle</span>
                  <span>Bảo toàn giá trị thanh khoản linh thạch toàn hệ thống tức thì.</span>
                </div>
              </div>
            </div>

            <!-- Treasury Philosophy Card -->
            <div class="philosophy-card">
              <div class="philosophy-icon-wrap">
                <span class="material-symbols-outlined text-gold">savings</span>
              </div>
              <div class="philosophy-text-group">
                <h4 class="philosophy-title">Túi Càn Khôn Độc Lập</h4>
                <p class="philosophy-desc">
                  Phân định rạch ròi ngân lưu chi tiêu thiết yếu và linh thạch đầu tư tích lũy giúp tăng tốc độ tích tụ đạo căn tài chính thêm 22%.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'

const props = defineProps({
  wallets: {
    type: Array,
    default: () => []
  },
  walletForm: {
    type: Object,
    required: true
  },
  transferForm: {
    type: Object,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  formatVND: {
    type: Function,
    required: true
  },
  walletTypeIcon: {
    type: Function,
    default: () => 'account_balance_wallet'
  }
})

defineEmits([
  'create-wallet',
  'delete-wallet',
  'edit-wallet',
  'do-transfer'
])

// Local UI toggles (presentation only, do not modify backend or global state)
const showAddWalletForm = ref(false)
const showTransferPanel = ref(true)
const transferSectionRef = ref(null)

// Total liquidity computed as sum of wallet balances
const totalBalance = computed(() => {
  return (props.wallets || []).reduce((acc, w) => acc + Number(w.balance || 0), 0)
})

// Palette for liquidity bar segments
const walletColors = [
  '#7dd6cc', // Celestial Jade
  '#c4c1fb', // Celestial Indigo
  '#e3c370', // Celestial Gold
  '#449f96', // Deep Cyan
  '#818cf8', // Lavender Indigo
  '#fbbf24', // Amber
  '#38bdf8', // Sky Blue
  '#a78bfa'  // Purple
]

function getWalletColor(index) {
  return walletColors[index % walletColors.length]
}

function getWalletPct(wallet) {
  const total = totalBalance.value
  if (!total || total <= 0) return 0
  const bal = Math.max(0, Number(wallet.balance || 0))
  const pct = (bal / total) * 100
  return pct >= 1 ? Math.round(pct * 10) / 10 : Math.round(pct * 100) / 100
}

function getWalletIcon(type) {
  if (type === 'bank') return 'account_balance'
  if (type === 'cash') return 'payments'
  if (type === 'e-wallet') return 'qr_code_scanner'
  if (type === 'crypto') return 'token'
  return 'account_balance_wallet'
}

function getWalletTypeLabel(type) {
  if (type === 'bank') return 'Ngân Hàng'
  if (type === 'cash') return 'Tiền Mặt'
  if (type === 'e-wallet') return 'Ví Điện Tử'
  if (type === 'crypto') return 'Linh Thạch Số'
  return 'Ví Nguồn'
}

function getWalletSubtext(type) {
  if (type === 'bank') return 'Tài khoản ngân hàng & chuyển khoản'
  if (type === 'cash') return 'Chi tiêu thường nhật tại động phủ'
  if (type === 'e-wallet') return 'Quét mã QR thanh toán nhanh'
  if (type === 'crypto') return 'Tài sản số & quỹ thanh thản'
  return 'Nguồn tiền dự trữ linh thạch'
}

// Quick transfer helpers
const selectedFromWallet = computed(() => {
  return (props.wallets || []).find(w => w.id === props.transferForm.from_wallet_id) || null
})

const selectedToWallet = computed(() => {
  return (props.wallets || []).find(w => w.id === props.transferForm.to_wallet_id) || null
})

const canSubmitTransfer = computed(() => {
  return (
    Boolean(props.transferForm.from_wallet_id) &&
    Boolean(props.transferForm.to_wallet_id) &&
    props.transferForm.from_wallet_id !== props.transferForm.to_wallet_id &&
    Number(props.transferForm.amount) > 0
  )
})

const projectedFromBalance = computed(() => {
  if (!selectedFromWallet.value) return 0
  const bal = Number(selectedFromWallet.value.balance || 0)
  const amt = Number(props.transferForm.amount || 0)
  return bal - amt
})

const projectedToBalance = computed(() => {
  if (!selectedToWallet.value) return 0
  const bal = Number(selectedToWallet.value.balance || 0)
  const amt = Number(props.transferForm.amount || 0)
  return bal + amt
})

function initiateTransferFrom(walletId) {
  props.transferForm.from_wallet_id = walletId
  showTransferPanel.value = true
  nextTick(() => {
    if (transferSectionRef.value?.scrollIntoView) {
      transferSectionRef.value.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  })
}

function swapTransferWallets() {
  const tmp = props.transferForm.from_wallet_id
  props.transferForm.from_wallet_id = props.transferForm.to_wallet_id
  props.transferForm.to_wallet_id = tmp
}

function setQuickAmount(amt) {
  props.transferForm.amount = amt
}

function setAllAvailableAmount() {
  if (selectedFromWallet.value) {
    const bal = Math.max(0, Number(selectedFromWallet.value.balance || 0))
    props.transferForm.amount = bal
  }
}

function toggleTransferPanel() {
  showTransferPanel.value = !showTransferPanel.value
  if (showTransferPanel.value) {
    nextTick(() => {
      if (transferSectionRef.value?.scrollIntoView) {
        transferSectionRef.value.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    })
  }
}
</script>

<style scoped>
/* ═══════════════════════════════════════════════════════════════════════════
   CÀN KHÔN LINH THẠCH CÁC — WALLETS VIEW (STITCH CELESTIAL TREASURY)
   ═══════════════════════════════════════════════════════════════════════════ */

.wallets-realm {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: var(--space-lg, 24px);
  width: 100%;
}

/* ─── AMBIENT GLOW ORBS ─── */
.ambient-glow-orb {
  position: absolute;
  border-radius: 9999px;
  filter: blur(80px);
  pointer-events: none;
  z-index: 0;
}

.orb-primary {
  top: -40px;
  right: -20px;
  width: 320px;
  height: 320px;
  background: rgba(125, 214, 204, 0.08);
}

.orb-secondary {
  top: 380px;
  left: -40px;
  width: 280px;
  height: 280px;
  background: rgba(196, 193, 251, 0.06);
}

/* ─── HEADER & ACTION BAR ─── */
.wallets-page-header {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: var(--space-md, 16px);
}

@media (min-width: 1024px) {
  .wallets-page-header {
    flex-direction: row;
    align-items: flex-end;
  }
}

.header-text-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs, 6px);
}

.header-badge-row {
  display: inline-flex;
  align-items: center;
  gap: var(--space-xs, 8px);
}

.status-pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 9999px;
  background: var(--primary, #7dd6cc);
  box-shadow: 0 0 10px rgba(125, 214, 204, 0.8);
  animation: pulse-glow 2s infinite ease-in-out;
}

@keyframes pulse-glow {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.85); }
}

.badge-text {
  font-family: var(--font-label-sm, 'Inter', sans-serif);
  font-size: var(--text-label-sm, 11px);
  font-weight: 600;
  letter-spacing: 0.1em;
  color: var(--primary, #7dd6cc);
  text-transform: uppercase;
}

.page-title {
  font-family: var(--font-headline-lg, 'Inter', sans-serif);
  font-size: clamp(24px, 3vw, 32px);
  font-weight: 700;
  color: var(--on-surface, #dae2fd);
  letter-spacing: -0.02em;
  line-height: 1.25;
  margin: 0;
}

.page-subtitle {
  font-family: var(--font-body-md, 'Inter', sans-serif);
  font-size: var(--text-body-md, 14px);
  color: var(--on-surface-variant, #bdc9c6);
  max-width: 680px;
  line-height: 1.5;
  margin: 0;
}

.header-action-group {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-sm, 10px);
}

/* ─── BUTTONS (STITCH CELESTIAL STYLING) ─── */
.btn-stitch-primary {
  display: inline-flex;
  align-items: center;
  gap: var(--space-xs, 8px);
  padding: 10px 18px;
  background: var(--primary-container, #449f96);
  color: var(--on-primary-container, #00302c);
  font-family: var(--font-label-lg, 'Inter', sans-serif);
  font-size: var(--text-label-lg, 14px);
  font-weight: 600;
  border-radius: var(--radius-xl, 12px);
  border: 1px solid rgba(125, 214, 204, 0.4);
  box-shadow: 0 0 16px rgba(68, 159, 150, 0.35);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.btn-stitch-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 0 24px rgba(125, 214, 204, 0.5);
  background: var(--primary, #7dd6cc);
}

.btn-stitch-primary:active:not(:disabled) {
  transform: translateY(0);
}

.btn-stitch-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-stitch-secondary {
  display: inline-flex;
  align-items: center;
  gap: var(--space-xs, 8px);
  padding: 10px 18px;
  background: var(--surface-container-high, #222a3d);
  color: var(--on-surface, #dae2fd);
  font-family: var(--font-label-lg, 'Inter', sans-serif);
  font-size: var(--text-label-lg, 14px);
  font-weight: 500;
  border-radius: var(--radius-xl, 12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-stitch-secondary:hover {
  background: var(--surface-bright, #31394d);
  border-color: rgba(125, 214, 204, 0.3);
}

.btn-stitch-secondary.active {
  background: rgba(68, 159, 150, 0.2);
  border-color: var(--primary, #7dd6cc);
  color: var(--primary, #7dd6cc);
}

/* ─── LIQUIDITY HERO MASTER PANEL ─── */
.liquidity-hero-card {
  position: relative;
  z-index: 1;
  background: var(--surface-container-low, #131b2e);
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: var(--radius-2xl, 16px);
  padding: var(--space-lg, 24px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
  overflow: hidden;
}

.hero-content-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-lg, 24px);
  align-items: center;
}

@media (min-width: 900px) {
  .hero-content-grid {
    grid-template-columns: 7fr 5fr;
  }
}

.hero-summary-col {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs, 8px);
}

.hero-badge-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-sm, 10px);
}

.hero-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 9999px;
  background: var(--surface-container-highest, #2d3449);
  color: var(--primary, #7dd6cc);
  font-family: var(--font-label-sm, 'Inter', sans-serif);
  font-size: var(--text-label-sm, 11px);
  font-weight: 600;
}

.pulse-indicator {
  width: 6px;
  height: 6px;
  border-radius: 9999px;
  background: var(--primary, #7dd6cc);
  animation: pulse-glow 1.5s infinite;
}

.hero-caption {
  font-size: var(--text-label-sm, 11px);
  color: var(--on-surface-variant, #bdc9c6);
}

.hero-balance-label {
  font-size: var(--text-label-md, 13px);
  color: var(--on-surface-variant, #bdc9c6);
  padding-top: 4px;
}

.hero-balance-display {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: var(--space-xs, 8px);
}

.balance-number {
  font-family: var(--font-headline-xl, 'Inter', sans-serif);
  font-size: clamp(28px, 4vw, 38px);
  color: var(--on-surface, #dae2fd);
  letter-spacing: -0.02em;
  line-height: 1.15;
}

.currency-tag {
  font-size: 22px;
  color: var(--primary, #7dd6cc);
  font-weight: 600;
}

.trend-pill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  border-radius: 6px;
  background: rgba(68, 159, 150, 0.18);
  color: var(--primary, #7dd6cc);
  font-size: 12px;
  font-weight: 600;
  margin-left: 6px;
}

.hero-desc {
  font-size: var(--text-body-sm, 13px);
  color: var(--on-surface-variant, #bdc9c6);
  line-height: 1.5;
  margin: 0;
  max-width: 580px;
}

/* Allocation Bar & Legend */
.hero-allocation-col {
  background: rgba(23, 31, 51, 0.65);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-xl, 14px);
  padding: var(--space-md, 18px);
  backdrop-filter: blur(12px);
  display: flex;
  flex-direction: column;
  gap: var(--space-sm, 12px);
}

.allocation-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: var(--text-label-sm, 12px);
  color: var(--on-surface-variant, #bdc9c6);
}

.allocation-title {
  font-weight: 500;
}

.allocation-status {
  color: var(--on-surface, #dae2fd);
  font-weight: 600;
}

.composition-bar-track {
  width: 100%;
  height: 12px;
  background: var(--surface-container-highest, #2d3449);
  border-radius: 9999px;
  overflow: hidden;
  display: flex;
}

.composition-bar-empty {
  width: 100%;
  height: 12px;
  background: var(--surface-container-highest, #2d3449);
  border-radius: 9999px;
}

.bar-segment {
  height: 100%;
  transition: width 0.3s ease;
}

.allocation-legend-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: var(--space-xs, 8px) var(--space-md, 16px);
  font-size: var(--text-label-sm, 11px);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  overflow: hidden;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 9999px;
  flex-shrink: 0;
}

.legend-name {
  color: var(--on-surface, #dae2fd);
}

.legend-pct {
  color: var(--on-surface-variant, #bdc9c6);
  font-weight: 600;
}

.legend-empty {
  font-size: var(--text-body-sm, 12px);
  color: var(--on-surface-variant, #bdc9c6);
  font-style: italic;
}

/* ─── COLLAPSIBLE ADD WALLET CARD ─── */
.add-wallet-card {
  position: relative;
  z-index: 1;
  background: var(--surface-container-low, #131b2e);
  border: 1px solid rgba(125, 214, 204, 0.3);
  border-radius: var(--radius-2xl, 16px);
  padding: var(--space-lg, 24px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
}

.card-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-md, 18px);
}

.title-with-icon {
  display: flex;
  align-items: center;
  gap: var(--space-xs, 8px);
}

.card-title {
  font-size: var(--text-title-lg, 18px);
  font-weight: 600;
  color: var(--on-surface, #dae2fd);
  margin: 0;
}

.btn-icon-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: transparent;
  color: var(--on-surface-variant, #bdc9c6);
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-icon-close:hover {
  background: var(--surface-container-high, #222a3d);
  color: var(--on-surface, #dae2fd);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--space-md, 16px);
}

.input-col {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.input-label {
  font-size: var(--text-label-md, 13px);
  font-weight: 500;
  color: var(--on-surface, #dae2fd);
}

.stitch-input,
.stitch-select {
  height: 44px;
  padding: 0 14px;
  background: var(--surface-container-high, #222a3d);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-xl, 12px);
  color: var(--on-surface, #dae2fd);
  font-size: var(--text-body-md, 14px);
  font-family: inherit;
  transition: all 0.2s ease;
}

.stitch-input:focus,
.stitch-select:focus {
  outline: none;
  border-color: var(--primary, #7dd6cc);
  background: var(--surface-bright, #31394d);
  box-shadow: 0 0 12px rgba(125, 214, 204, 0.2);
}

.form-actions-row {
  margin-top: var(--space-md, 20px);
  display: flex;
  justify-content: flex-end;
}

/* ─── WALLETS GRID SECTION ─── */
.wallets-grid-section {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-md, 16px);
}

.section-header-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-xs, 8px);
}

.section-title {
  font-size: var(--text-title-lg, 18px);
  font-weight: 600;
  color: var(--on-surface, #dae2fd);
  margin: 0;
}

.section-caption {
  font-size: var(--text-label-sm, 12px);
  color: var(--on-surface-variant, #bdc9c6);
}

.wallets-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-md, 20px);
}

/* ─── INDIVIDUAL WALLET CARD ─── */
.wallet-card-item {
  position: relative;
  background: var(--surface-container-low, #131b2e);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: var(--radius-2xl, 16px);
  padding: var(--space-lg, 22px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.wallet-card-item:hover {
  transform: translateY(-3px);
  background: var(--surface-container, #171f33);
  border-color: rgba(125, 214, 204, 0.25);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.35);
}

/* Decorative ambient corner aura */
.card-ambient-corner {
  position: absolute;
  top: 0;
  right: 0;
  width: 90px;
  height: 90px;
  border-bottom-left-radius: 9999px;
  pointer-events: none;
  opacity: 0.12;
  transition: opacity 0.3s ease;
}

.wallet-card-item:hover .card-ambient-corner {
  opacity: 0.25;
}

.corner-bank { background: var(--primary, #7dd6cc); }
.corner-cash { background: var(--tertiary, #e3c370); }
.corner-e-wallet { background: var(--secondary, #c4c1fb); }

.card-top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-sm, 14px);
}

.wallet-type-avatar {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-xl, 12px);
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--surface-container-high, #222a3d);
  transition: transform 0.2s ease;
}

.wallet-card-item:hover .wallet-type-avatar {
  transform: scale(1.06);
}

.avatar-bank { color: var(--primary, #7dd6cc); }
.avatar-cash { color: var(--tertiary, #e3c370); }
.avatar-e-wallet { color: var(--secondary, #c4c1fb); }

.wallet-type-chip {
  padding: 4px 10px;
  border-radius: 9999px;
  font-size: var(--text-label-sm, 11px);
  font-weight: 600;
}

.chip-bank {
  background: rgba(125, 214, 204, 0.15);
  color: var(--primary, #7dd6cc);
}

.chip-cash {
  background: rgba(227, 195, 112, 0.15);
  color: var(--tertiary, #e3c370);
}

.chip-e-wallet {
  background: rgba(196, 193, 251, 0.15);
  color: var(--secondary, #c4c1fb);
}

.card-body-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-bottom: var(--space-md, 16px);
}

.wallet-card-name {
  font-size: var(--text-title-md, 16px);
  font-weight: 600;
  color: var(--on-surface, #dae2fd);
  margin: 0;
}

.wallet-card-subtitle {
  font-size: var(--text-body-sm, 12px);
  color: var(--on-surface-variant, #bdc9c6);
  margin: 0;
}

.card-balance-block {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 12px 0;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.balance-sublabel {
  font-size: var(--text-label-sm, 11px);
  color: var(--on-surface-variant, #bdc9c6);
}

.balance-amt {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.01em;
}

.card-actions-row {
  display: flex;
  align-items: center;
  gap: var(--space-xs, 8px);
  padding-top: var(--space-xs, 8px);
}

.btn-card-transfer {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  height: 36px;
  border-radius: var(--radius-lg, 10px);
  background: var(--surface-container-high, #222a3d);
  color: var(--on-surface, #dae2fd);
  font-size: var(--text-label-md, 13px);
  font-weight: 500;
  border: 1px solid rgba(255, 255, 255, 0.06);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-card-transfer:hover {
  background: var(--primary, #7dd6cc);
  color: var(--on-primary, #003733);
}

.btn-card-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-lg, 10px);
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--surface-container-high, #222a3d);
  color: var(--on-surface-variant, #bdc9c6);
  border: 1px solid rgba(255, 255, 255, 0.06);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-card-icon:hover {
  background: var(--surface-bright, #31394d);
  color: var(--on-surface, #dae2fd);
}

.btn-delete:hover {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  border-color: rgba(239, 68, 68, 0.4);
}

/* Empty State */
.wallets-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  background: var(--surface-container-low, #131b2e);
  border: 1px dashed rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-2xl, 16px);
  text-align: center;
}

.empty-icon-wrap {
  width: 64px;
  height: 64px;
  border-radius: 9999px;
  background: var(--surface-container-high, #222a3d);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--space-md, 16px);
}

.empty-icon {
  font-size: 32px;
  color: var(--on-surface-variant, #bdc9c6);
}

.empty-title {
  font-size: var(--text-title-lg, 18px);
  font-weight: 600;
  color: var(--on-surface, #dae2fd);
  margin-bottom: var(--space-xs, 6px);
}

.empty-desc {
  font-size: var(--text-body-md, 14px);
  color: var(--on-surface-variant, #bdc9c6);
  max-width: 420px;
  margin-bottom: var(--space-md, 18px);
}

/* ─── INTERNAL ATOMIC TRANSFER MASTER SECTION ─── */
.transfer-master-section {
  position: relative;
  z-index: 1;
}

.transfer-grid-layout {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-lg, 24px);
  align-items: start;
}

@media (min-width: 1024px) {
  .transfer-grid-layout {
    grid-template-columns: 7fr 5fr;
  }
}

.transfer-form-card {
  background: var(--surface-container-low, #131b2e);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-2xl, 16px);
  padding: var(--space-lg, 24px);
  box-shadow: 0 10px 32px rgba(0, 0, 0, 0.35);
  position: relative;
  overflow: hidden;
}

.transfer-form-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, var(--primary, #7dd6cc), var(--secondary, #c4c1fb), transparent);
}

.transfer-form-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-sm, 12px);
  padding-bottom: var(--space-md, 16px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  margin-bottom: var(--space-md, 18px);
}

.transfer-title-group {
  display: flex;
  align-items: center;
  gap: var(--space-xs, 10px);
}

.icon-avatar-jade {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-xl, 12px);
  background: rgba(125, 214, 204, 0.15);
  color: var(--primary, #7dd6cc);
  display: flex;
  align-items: center;
  justify-content: center;
}

.transfer-card-title {
  font-size: var(--text-title-lg, 18px);
  font-weight: 600;
  color: var(--on-surface, #dae2fd);
  margin: 0;
}

.transfer-card-desc {
  font-size: var(--text-label-sm, 12px);
  color: var(--on-surface-variant, #bdc9c6);
  margin: 0;
}

.idempotency-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 9999px;
  background: var(--surface-container-high, #222a3d);
  color: var(--primary, #7dd6cc);
  font-size: var(--text-label-sm, 11px);
  font-weight: 600;
}

.transfer-inputs-flow {
  display: flex;
  flex-direction: column;
  gap: var(--space-md, 18px);
}

.wallet-select-pair-row {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: flex-end;
  gap: var(--space-sm, 10px);
}

@media (max-width: 640px) {
  .wallet-select-pair-row {
    grid-template-columns: 1fr;
  }
}

.select-col {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.input-label-pair {
  font-size: var(--text-label-md, 13px);
  font-weight: 500;
  color: var(--on-surface, #dae2fd);
  display: flex;
  align-items: center;
  gap: 6px;
}

.dot-from {
  width: 8px;
  height: 8px;
  border-radius: 9999px;
  background: var(--primary, #7dd6cc);
}

.dot-to {
  width: 8px;
  height: 8px;
  border-radius: 9999px;
  background: var(--secondary, #c4c1fb);
}

.stitch-select-large {
  height: 48px;
  padding: 0 14px;
  background: var(--surface-container-high, #222a3d);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-xl, 12px);
  color: var(--on-surface, #dae2fd);
  font-size: var(--text-body-md, 14px);
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s ease;
  width: 100%;
}

.stitch-select-large:focus {
  outline: none;
  border-color: var(--primary, #7dd6cc);
  background: var(--surface-bright, #31394d);
}

.btn-swap-wallets {
  height: 48px;
  width: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--surface-container-high, #222a3d);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-xl, 12px);
  color: var(--on-surface-variant, #bdc9c6);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-swap-wallets:hover {
  background: var(--surface-bright, #31394d);
  color: var(--primary, #7dd6cc);
  transform: rotate(180deg);
}

/* Transfer Amount Block */
.transfer-amount-block {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs, 8px);
}

.amount-label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.rate-badge {
  font-size: var(--text-label-sm, 11px);
  color: var(--primary, #7dd6cc);
}

.amount-input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.stitch-input-large {
  width: 100%;
  height: 52px;
  padding-left: 16px;
  padding-right: 48px;
  background: var(--surface-container-high, #222a3d);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-xl, 14px);
  color: var(--on-surface, #dae2fd);
  font-size: 22px;
  font-weight: 700;
  font-family: inherit;
  transition: all 0.2s ease;
}

.stitch-input-large:focus {
  outline: none;
  border-color: var(--primary, #7dd6cc);
  background: var(--surface-bright, #31394d);
  box-shadow: 0 0 16px rgba(125, 214, 204, 0.2);
}

.currency-affix {
  position: absolute;
  right: 18px;
  font-size: 18px;
  font-weight: 600;
  color: var(--primary, #7dd6cc);
  pointer-events: none;
}

.quick-pills-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-xs, 8px);
  padding-top: 4px;
}

.pill-btn {
  padding: 6px 12px;
  border-radius: 8px;
  background: var(--surface-container, #171f33);
  color: var(--on-surface-variant, #bdc9c6);
  border: 1px solid rgba(255, 255, 255, 0.06);
  font-size: var(--text-label-sm, 12px);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pill-btn:hover {
  background: var(--surface-container-high, #222a3d);
  color: var(--primary, #7dd6cc);
  border-color: rgba(125, 214, 204, 0.3);
}

.pill-btn-all {
  background: rgba(227, 195, 112, 0.15);
  color: var(--tertiary, #e3c370);
  border-color: rgba(227, 195, 112, 0.3);
}

.pill-btn-all:hover {
  background: rgba(227, 195, 112, 0.25);
  color: var(--tertiary, #e3c370);
}

/* ACID Box */
.acid-security-box {
  display: flex;
  align-items: flex-start;
  gap: var(--space-sm, 12px);
  padding: var(--space-md, 14px);
  border-radius: var(--radius-xl, 12px);
  background: var(--surface-container-high, #222a3d);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.acid-icon {
  margin-top: 2px;
  font-size: 20px;
  flex-shrink: 0;
}

.acid-text-wrap {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.acid-title {
  font-size: var(--text-label-md, 13px);
  font-weight: 600;
  color: var(--on-surface, #dae2fd);
}

.acid-desc {
  font-size: var(--text-body-sm, 12px);
  color: var(--on-surface-variant, #bdc9c6);
  line-height: 1.45;
  margin: 0;
}

.transfer-btn-wrap {
  padding-top: var(--space-xs, 4px);
}

.btn-stitch-transfer-submit {
  width: 100%;
  height: 52px;
  border-radius: var(--radius-xl, 14px);
  background: var(--primary-container, #449f96);
  color: var(--on-primary-container, #00302c);
  font-family: var(--font-label-lg, 'Inter', sans-serif);
  font-size: var(--text-label-lg, 15px);
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-xs, 8px);
  border: 1px solid rgba(125, 214, 204, 0.4);
  box-shadow: 0 0 20px rgba(68, 159, 150, 0.35);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.btn-stitch-transfer-submit:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 0 28px rgba(125, 214, 204, 0.5);
  background: var(--primary, #7dd6cc);
}

.btn-stitch-transfer-submit:disabled {
  opacity: 0.45;
  cursor: not-allowed;
  box-shadow: none;
}

.tag-auto-oppose {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 6px;
  background: rgba(0, 48, 44, 0.25);
  font-weight: 500;
}

/* ─── TRANSFER COMPANION COLUMN (RIGHT 5 COLS) ─── */
.transfer-companion-col {
  display: flex;
  flex-direction: column;
  gap: var(--space-md, 16px);
}

.simulation-card {
  background: var(--surface-container-low, #131b2e);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-2xl, 16px);
  padding: var(--space-lg, 22px);
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  gap: var(--space-md, 16px);
}

.sim-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sim-caption {
  font-size: var(--text-label-sm, 11px);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 600;
  color: var(--on-surface-variant, #bdc9c6);
}

.sim-badge {
  padding: 2px 8px;
  border-radius: 6px;
  font-size: var(--text-label-sm, 11px);
  font-weight: 600;
}

.badge-ready {
  background: rgba(125, 214, 204, 0.18);
  color: var(--primary, #7dd6cc);
}

.badge-idle {
  background: var(--surface-container-high, #222a3d);
  color: var(--on-surface-variant, #bdc9c6);
}

.simulation-diagram-box {
  background: rgba(23, 31, 51, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-xl, 14px);
  padding: var(--space-md, 16px);
  display: flex;
  flex-direction: column;
  gap: var(--space-sm, 12px);
}

.diagram-nodes-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-xs, 8px);
}

.diagram-node {
  width: 96px;
  padding: 8px 6px;
  border-radius: 10px;
  background: var(--surface-container-high, #222a3d);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 2px;
}

.node-icon {
  font-size: 22px;
}

.node-name {
  font-size: 11px;
  font-weight: 600;
  color: var(--on-surface, #dae2fd);
  width: 100%;
}

.node-delta {
  font-size: 10px;
  font-weight: 700;
}

.diagram-path {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.path-svg {
  width: 100%;
  height: 24px;
  color: var(--primary, #7dd6cc);
}

.path-line {
  color: rgba(255, 255, 255, 0.2);
}

.path-orb {
  fill: var(--primary, #7dd6cc);
  animation: pulse-glow 1.5s infinite;
}

.path-arrow {
  stroke: var(--primary, #7dd6cc);
}

.path-amt {
  font-size: 11px;
  font-weight: 700;
  color: var(--primary, #7dd6cc);
  margin-top: 2px;
}

.sim-projected-row {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 11px;
  color: var(--on-surface-variant, #bdc9c6);
  padding-top: 6px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.projected-label {
  font-weight: 500;
}

.projected-vals {
  color: var(--on-surface, #dae2fd);
  font-weight: 600;
}

.sim-rules-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs, 6px);
  font-size: var(--text-body-sm, 12px);
  color: var(--on-surface-variant, #bdc9c6);
}

.rule-item {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  line-height: 1.4;
}

.philosophy-card {
  background: var(--surface-container-low, #131b2e);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: var(--radius-2xl, 16px);
  padding: var(--space-md, 18px);
  display: flex;
  align-items: center;
  gap: var(--space-md, 14px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.philosophy-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-xl, 12px);
  background: rgba(227, 195, 112, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.philosophy-text-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.philosophy-title {
  font-size: var(--text-title-sm, 13px);
  font-weight: 600;
  color: var(--on-surface, #dae2fd);
  margin: 0;
}

.philosophy-desc {
  font-size: var(--text-body-sm, 12px);
  color: var(--on-surface-variant, #bdc9c6);
  line-height: 1.4;
  margin: 0;
}

/* ─── GENERAL UTILITIES ─── */
.text-jade { color: var(--primary, #7dd6cc); }
.text-secondary { color: var(--secondary, #c4c1fb); }
.text-gold { color: var(--tertiary, #e3c370); }
.text-danger { color: #ef4444; }
.tabular-num { font-variant-numeric: tabular-nums; }
.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.ml-auto { margin-left: auto; }
.icon-xs { font-size: 14px !important; }
.icon-sm { font-size: 18px !important; }
.icon-tertiary { color: var(--tertiary, #e3c370); }

/* Transitions */
.tray-expand-enter-active,
.tray-expand-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  overflow: hidden;
}
.tray-expand-enter-from,
.tray-expand-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
