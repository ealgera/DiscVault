import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import CollectionView from '../views/CollectionView.vue'
import ScanView from '../views/ScanView.vue'
import LocationView from '../views/LocationView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: DashboardView,
    },
    {
      path: '/collection',
      name: 'collection',
      component: CollectionView,
    },
    {
      path: '/scan',
      name: 'scan',
      component: ScanView,
    },
    {
      path: '/locations',
      name: 'locations',
      component: LocationView,
    },
  ],
})

export default router