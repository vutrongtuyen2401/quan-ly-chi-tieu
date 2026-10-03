import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useSessionStore } from './stores/session'
// Thứ tự CSS: style gốc của datepicker trước, app.css (có ghi đè .dp__*) sau
import '@vuepic/vue-datepicker/dist/main.css'
import './styles/app.css'

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)

// Tab Phân Quyền chỉ dành cho admin (backend vẫn kiểm tra quyền ở mọi API admin)
router.beforeEach((to) => {
  if (to.meta.adminOnly && !useSessionStore().isUserAdmin) {
    return { name: 'dashboard' }
  }
})

app.mount('#app')
