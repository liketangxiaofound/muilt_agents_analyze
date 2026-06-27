import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import HomeView from './views/HomeView.vue'
import AnalysisView from './views/AnalysisView.vue'
import ReportView from './views/ReportView.vue'
import KnowledgeView from './views/KnowledgeView.vue'
import './style/main.css'

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/analysis', name: 'analysis', component: AnalysisView },
  { path: '/report/:id', name: 'report', component: ReportView, props: true },
  { path: '/knowledge', name: 'knowledge', component: KnowledgeView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

const app = createApp(App)
app.use(router)
app.mount('#app')
