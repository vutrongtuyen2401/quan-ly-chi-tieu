import { isReactive, isRef, toRaw, toRef } from 'vue'
import * as format from '../utils/format'
import { useSessionStore } from '../stores/session'
import { useWalletStore } from '../stores/wallets'
import { useCategoryStore } from '../stores/categories'
import { useTransactionStore } from '../stores/transactions'
import { useBudgetStore } from '../stores/budgets'
import { useReportStore } from '../stores/reports'
import { useDebtStore } from '../stores/debts'
import { useGoalStore } from '../stores/goals'
import { useAiStore } from '../stores/ai'
import { useAdminStore } from '../stores/admin'

const STORES = [
  useSessionStore, useWalletStore, useCategoryStore, useTransactionStore, useBudgetStore,
  useReportStore, useDebtStore, useGoalStore, useAiStore, useAdminStore,
]

function bindStore(store, bindings) {
  const raw = toRaw(store)
  for (const key of Object.keys(raw)) {
    if (key.startsWith('$') || key.startsWith('_')) continue // thuộc tính nội bộ của Pinia
    if (key in bindings) throw new Error(`Trùng tên "${key}" giữa các store (${store.$id})`)
    const value = raw[key]
    bindings[key] = isRef(value) || isReactive(value) ? toRef(store, key) : value
  }
}

/**
 * Gộp state / computed / hàm của mọi store (cùng các hàm định dạng trong utils/format.js) thành một object phẳng
 * để template dùng trực tiếp (VD: `wallets`, `txnForm.amount`, `v-model="chatInput"`, `@click="createWallet"`).
 * State được bọc bằng toRef nên v-model ghi ngược vào đúng store.
 */
export function useAppBindings() {
  const bindings = { ...format }
  for (const useStore of STORES) bindStore(useStore(), bindings)
  return bindings
}
