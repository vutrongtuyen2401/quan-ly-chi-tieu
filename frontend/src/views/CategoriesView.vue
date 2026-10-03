<template>
  <!-- ═══════ TAB 4: CATEGORIES ═══════ -->
  <section class="tab-panel">
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
          <div class="cat-actions">
            <button class="btn-sm-edit" @click="openEditCategory(c)" title="Sửa">✏️</button>
            <button class="btn-sm-danger" @click="deleteCategory(c.id)" title="Xóa">✕</button>
          </div>
        </div>
        <div v-if="!incomeCategories.length" class="empty-state">Chưa có danh mục thu...</div>
      </div>
      <div class="cat-col">
        <h3 class="sub-title">🔥 Tiêu Hao (EXPENSE)</h3>
        <div v-for="c in expenseCategories" :key="c.id" class="cat-item expense">
          <span>{{ c.icon }} {{ c.category_name }}</span>
          <div class="cat-actions">
            <button class="btn-sm-edit" @click="openEditCategory(c)" title="Sửa">✏️</button>
            <button class="btn-sm-danger" @click="deleteCategory(c.id)" title="Xóa">✕</button>
          </div>
        </div>
        <div v-if="!expenseCategories.length" class="empty-state">Chưa có danh mục chi...</div>
      </div>
    </div>
  </section>

  <Teleport to="#modal-root" defer>
    <!-- EDIT CATEGORY MODAL -->
    <div v-if="showEditCatModal" class="modal-backdrop" @click.self="showEditCatModal = false">
      <div class="modal-card">
        <div class="modal-header">
          <h3 class="modal-title">✏️ Chỉnh Sửa Danh Mục</h3>
          <button class="modal-close" @click="showEditCatModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="input-group-xianxia">
            <label>Tên Danh Mục</label>
            <input v-model="editCatForm.category_name" type="text" placeholder="Tên danh mục..." />
          </div>
          <div class="input-group-xianxia">
            <label>Biểu Tượng (Icon)</label>
            <select v-model="editCatForm.icon">
              <option v-for="ic in iconOptions" :key="'edit-ic-'+ic" :value="ic">{{ ic }}</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showEditCatModal = false">Hủy</button>
          <button class="btn-jade-sm" @click="updateCategory" :disabled="loading">
            {{ loading ? '⏳...' : '💾 Cập Nhật Danh Mục' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script>
import { useAppBindings } from '../composables/useAppBindings'

export default {
  name: 'CategoriesView',
  setup() {
    return useAppBindings()
  },
}
</script>
