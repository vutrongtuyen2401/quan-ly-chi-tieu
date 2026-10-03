import { createRouter, createWebHashHistory } from 'vue-router'

// Mỗi tab là một route; tên route = id tab (store.switchTab(id) → router.push({ name: id })).
// Các view được tải lười (code-splitting) để giảm dung lượng tải lần đầu.
// Dùng hash history (#/...) để chạy được trên mọi web server tĩnh mà không cần cấu hình fallback.
const routes = [
  { path: '/', name: 'dashboard', component: () => import('./views/DashboardView.vue') },
  { path: '/transactions', name: 'transactions', component: () => import('./views/TransactionsView.vue') },
  { path: '/debts', name: 'debts', component: () => import('./views/DebtsView.vue') },
  { path: '/goals', name: 'goals', component: () => import('./views/GoalsView.vue') },
  { path: '/wallets', name: 'wallets', component: () => import('./views/WalletsView.vue') },
  { path: '/categories', name: 'categories', component: () => import('./views/CategoriesView.vue') },
  { path: '/ocr', name: 'ocr', component: () => import('./views/OcrView.vue') },
  { path: '/budgets', name: 'budgets', component: () => import('./views/BudgetsView.vue') },
  { path: '/stats', name: 'stats', component: () => import('./views/StatsView.vue') },
  { path: '/chat', name: 'chat', component: () => import('./views/ChatView.vue') },
  { path: '/admin', name: 'admin', component: () => import('./views/AdminView.vue'), meta: { adminOnly: true } },
  { path: '/:pathMatch(.*)*', redirect: { name: 'dashboard' } },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

export default router
