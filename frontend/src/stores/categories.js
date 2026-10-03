/** Danh mục thu / chi. */
import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import api from '../api'
import { useBudgetStore } from './budgets'
import { useSessionStore } from './session'

export const useCategoryStore = defineStore('categories', () => {
  // Store khác chỉ được đọc bên trong hàm (không đọc state ngay lúc khởi tạo) để tránh vòng lặp
  const budgetStore = useBudgetStore()
  const session = useSessionStore()

  const showEditCatModal = ref(false)
  const editCatForm = ref({ id: null, category_name: '', icon: '📦' })
  const categories = ref([])
  const catForm = ref({ category_name: '', category_type: 'EXPENSE', icon: '📦' })

  const iconOptions = ['🍕','🛍️','🚗','💵','🎁','🏠','💊','📚','🎮','☕','🍜','🎬','🏋️','✈️','📱','👕','🎵','🐾','🔧','📦']

  // ─── COMPUTED ─────────────────
  const incomeCategories = computed(() => categories.value.filter(c => c.category_type === 'INCOME'))
  const expenseCategories = computed(() => categories.value.filter(c => c.category_type === 'EXPENSE'))
  async function loadCategories() {
    try { categories.value = (await api.get('/api/categories')).data } catch {}
  }

  function openEditCategory(c) {
    editCatForm.value = { id: c.id, category_name: c.category_name, icon: c.icon }
    showEditCatModal.value = true
  }

  async function updateCategory() {
    if (!editCatForm.value.category_name.trim()) {
      session.showToast('Tên danh mục không được để trống!', 'error')
      return
    }
    session.loading = true
    try {
      await api.put(`/api/categories/${editCatForm.value.id}`, {
        category_name: editCatForm.value.category_name,
        icon: editCatForm.value.icon
      })
      session.showToast('✨ Danh mục đã được cập nhật!')
      showEditCatModal.value = false
      await loadCategories()
    } catch (err) {
      session.showToast(err.response?.data?.detail || 'Lỗi cập nhật danh mục!', 'error')
    }
    session.loading = false
  }

  async function createCategory() {
    if (!catForm.value.category_name) {
      session.showToast('Vui lòng nhập tên danh mục!', 'error')
      return
    }
    session.loading = true
    try {
      await api.post('/api/categories', catForm.value)
      session.showToast('✨ Danh mục mới đã khai mở!')
      catForm.value = { category_name: '', category_type: 'EXPENSE', icon: '📦' }
      await loadCategories()
    } catch (err) {
      session.showToast(err.response?.data?.detail || 'Lỗi!', 'error')
    }
    session.loading = false
  }

  async function deleteCategory(id) {
    if (!confirm('Xóa danh mục này?')) return
    try {
      await api.delete(`/api/categories/${id}`)
      session.showToast('Danh mục đã xóa!')
      await Promise.all([loadCategories(), budgetStore.loadBudgets(), budgetStore.checkBudgetAlerts()])
    } catch (err) {
      session.showToast(err.response?.data?.detail || 'Lỗi khi xóa danh mục!', 'error')
    }
  }

  return {
    showEditCatModal, editCatForm, categories, catForm, iconOptions, incomeCategories, expenseCategories,
    loadCategories, openEditCategory, updateCategory, createCategory, deleteCategory,
  }
})
