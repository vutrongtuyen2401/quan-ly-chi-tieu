<template>
  <!-- ═══════ TAB 3: WALLETS ═══════ -->
  <section class="tab-panel">
    <h2 class="section-title">💳 Túi Càn Khôn — Quản Lý Ví</h2>

    <div class="form-card">
      <h3 class="sub-title">➕ Khai Mở Túi Càn Khôn Mới</h3>
      <div class="form-grid">
        <div class="input-group-xianxia">
          <label>Tên Ví</label>
          <input v-model="walletForm.wallet_name" type="text" list="bankList" placeholder="VD: Linh Mạch BIDV" />
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
        <div class="input-group-xianxia">
          <label>Ghi Chú (Tùy chọn)</label>
          <input v-model="transferForm.note" type="text" placeholder="VD: Rút tiền mặt, nạp Momo..." />
        </div>
      </div>
      <button class="btn-jade" @click="doTransfer" :disabled="loading || !transferForm.from_wallet_id || !transferForm.to_wallet_id || !transferForm.amount" style="margin-top: 16px;">
        {{ loading ? '⏳ Đang chuyển...' : '🔄 Chuyển Linh Thạch' }}
      </button>

      <div v-if="walletTransfers.length" class="table-scroll" style="margin-top: 20px;">
        <table class="xianxia-table">
          <thead>
            <tr>
              <th>Thời Gian</th>
              <th>Từ Ví</th>
              <th>Đến Ví</th>
              <th>Số Tiền</th>
              <th>Ghi Chú</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="t in walletTransfers" :key="'tf-'+t.id">
              <td>{{ t.created_at }}</td>
              <td>{{ t.from_wallet_name }}</td>
              <td>{{ t.to_wallet_name }}</td>
              <td>{{ formatVND(t.amount) }}</td>
              <td>{{ t.note || '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="wallet-grid">
      <div v-for="w in wallets" :key="w.id" class="wallet-card">
        <div class="wallet-card-top">
          <span class="wallet-type-icon">
            {{ walletTypeIcon(w.wallet_type) }}
          </span>
          <div class="card-action-btns">
            <button class="btn-sm-edit" @click="openEditWallet(w)" title="Sửa ví">✏️</button>
            <button class="btn-sm-danger" @click="deleteWallet(w.id)" title="Hủy ví">✕</button>
          </div>
        </div>
        <h4 class="wallet-name">{{ w.wallet_name }}</h4>
        <p class="wallet-balance">{{ formatVND(w.balance) }}</p>
        <span class="wallet-type-label">{{ w.wallet_type === 'cash' ? 'Tiền Mặt' : w.wallet_type === 'bank' ? 'Ngân Hàng' : 'Ví Điện Tử' }}</span>
      </div>
      <div v-if="!wallets.length" class="empty-state">Chưa có Túi Càn Khôn nào...</div>
    </div>
  </section>

  <Teleport to="#modal-root" defer>
    <!-- EDIT WALLET MODAL -->
    <div v-if="showEditWalletModal" class="modal-backdrop" @click.self="showEditWalletModal = false">
      <div class="modal-card">
        <div class="modal-header">
          <h3 class="modal-title">✏️ Chỉnh Sửa Túi Càn Khôn</h3>
          <button class="modal-close" @click="showEditWalletModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="input-group-xianxia">
            <label>Tên Ví</label>
            <input v-model="editWalletForm.wallet_name" type="text" list="bankList" placeholder="Tên ví..." />
          </div>
          <div class="input-group-xianxia">
            <label>Loại Ví</label>
            <select v-model="editWalletForm.wallet_type">
              <option value="cash">💵 Tiền Mặt</option>
              <option value="bank">🏦 Ngân Hàng</option>
              <option value="e-wallet">📱 Ví Điện Tử</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showEditWalletModal = false">Hủy</button>
          <button class="btn-jade-sm" @click="updateWallet" :disabled="loading">
            {{ loading ? '⏳...' : '💾 Cập Nhật Ví' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script>
import { useAppBindings } from '../composables/useAppBindings'

export default {
  name: 'WalletsView',
  setup() {
    return useAppBindings()
  },
}
</script>
