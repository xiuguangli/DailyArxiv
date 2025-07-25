import { createRouter, createWebHashHistory } from 'vue-router';
import DailyArxiv from './components/DailyArxiv.vue';
import ArxivStats from './components/ArxivStats.vue';

const routes = [
  {
    path: '/',
    redirect: '/daily-arxiv'
  },
  {
    path: '/daily-arxiv',
    name: 'daily-arxiv',
    component: DailyArxiv
  },
  {
    path: '/stats',
    name: 'stats',
    component: ArxivStats
  }
];

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes
});

export default router;
