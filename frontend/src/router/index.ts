import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import CollectionView from '../views/CollectionView.vue'
import ScanView from '../views/ScanView.vue'
import LocationView from '../views/LocationView.vue'
import TagView from '../views/TagView.vue'
import GenreView from '../views/GenreView.vue'
import AlbumDetailView from '../views/AlbumDetailView.vue'

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
      path: '/albums/:id',
      name: 'album-detail',
      component: AlbumDetailView,
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
    {
      path: '/tags',
      name: 'tags',
      component: TagView,
    },
    {
      path: '/genres',
      name: 'genres',
      component: GenreView,
    },
    {
      path: '/management',
      name: 'management',
      component: () => import('../views/ManagementView.vue'),
    },
    {
      path: '/reports',
      name: 'reports',
      component: () => import('../views/ReportsView.vue'),
    },
    {
      path: '/reports/:type',
      name: 'report-detail',
      component: () => import('../views/ReportDetailView.vue'),
    },
  ],
})

export default router