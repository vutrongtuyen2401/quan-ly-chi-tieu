import { isReactive, isRef, toRaw, toRef } from 'vue'
import { useAppStore } from '../stores/app'

/**
 * Trả về state / computed / hàm của store dưới dạng object phẳng để template dùng trực tiếp
 * (VD: `wallets`, `txnForm.amount`, `v-model="chatInput"`, `@click="createWallet"`) — giống hệt khi
 * toàn bộ logic còn nằm trong setup() của App.vue. State được bọc bằng toRef nên v-model ghi ngược vào store.
 */
export function useAppBindings() {
  const store = useAppStore()
  const raw = toRaw(store)
  const bindings = {}
  for (const key of Object.keys(raw)) {
    if (key.startsWith('$') || key.startsWith('_')) continue // thuộc tính nội bộ của Pinia
    const value = raw[key]
    bindings[key] = isRef(value) || isReactive(value) ? toRef(store, key) : value
  }
  return bindings
}
