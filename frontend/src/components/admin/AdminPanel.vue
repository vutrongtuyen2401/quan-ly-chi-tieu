<template>
  <div class="admin-panel-container">
    <!-- Header Section -->
    <AdminHeader />

    <!-- System Stats Cards (Pure Account / Access Metrics — Zero Financial Aggregates) -->
    <AdminStatsRow :admin-stats="adminStats" />

    <!-- User Management Table Workspace -->
    <UserManagementTable
      :users="adminUsers"
      :current-user-id="currentUserId"
      :loading="loading"
      @toggle-active="onToggleActive"
      @open-role-modal="openRoleModal"
      @refresh="$emit('refresh-users')"
    />

    <!-- Role Confirmation Modal (Secured Action Protocol) -->
    <RoleConfirmModal
      :show="showRoleModal"
      :target-user="roleTargetUser"
      :target-role="roleTargetRole"
      :loading="roleLoading"
      @confirm="onConfirmRoleChange"
      @close="closeRoleModal"
    />
  </div>
</template>

<script>
import { ref } from 'vue'
import AdminHeader from './AdminHeader.vue'
import AdminStatsRow from './AdminStatsRow.vue'
import UserManagementTable from './UserManagementTable.vue'
import RoleConfirmModal from './RoleConfirmModal.vue'

export default {
  name: 'AdminPanel',
  components: {
    AdminHeader,
    AdminStatsRow,
    UserManagementTable,
    RoleConfirmModal
  },
  props: {
    adminStats: {
      type: Object,
      default: () => ({ total_users: 0, active_users: 0, locked_users: 0 })
    },
    adminUsers: {
      type: Array,
      default: () => []
    },
    currentUserId: {
      type: Number,
      default: null
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['toggle-user-active', 'change-user-role', 'refresh-users'],
  setup(props, { emit }) {
    const showRoleModal = ref(false)
    const roleTargetUser = ref(null)
    const roleTargetRole = ref('user')
    const roleLoading = ref(false)

    function openRoleModal(payload) {
      if (!payload || !payload.user) return
      roleTargetUser.value = payload.user
      roleTargetRole.value = payload.targetRole || (payload.user.role === 'admin' ? 'user' : 'admin')
      showRoleModal.value = true
    }

    function closeRoleModal() {
      showRoleModal.value = false
      roleTargetUser.value = null
      roleLoading.value = false
    }

    function onConfirmRoleChange(payload) {
      emit('change-user-role', {
        user: payload.user,
        newRole: payload.newRole
      })
      closeRoleModal()
    }

    function onToggleActive(user) {
      emit('toggle-user-active', user)
    }

    return {
      showRoleModal,
      roleTargetUser,
      roleTargetRole,
      roleLoading,
      openRoleModal,
      closeRoleModal,
      onConfirmRoleChange,
      onToggleActive
    }
  }
}
</script>

<style scoped>
.admin-panel-container {
  display: flex;
  flex-direction: column;
  gap: var(--space-xl, 1.5rem);
  width: 100%;
  max-width: 1360px;
  margin: 0 auto;
  padding-bottom: var(--space-3xl, 3rem);
  animation: fadeInAdmin 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes fadeInAdmin {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .admin-panel-container {
    gap: var(--space-lg, 1.25rem);
    padding-bottom: var(--space-2xl, 2rem);
  }
}
</style>
