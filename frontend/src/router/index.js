import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Process from '../views/MainView.vue'
import SimulationView from '../views/SimulationView.vue'
import SimulationRunView from '../views/SimulationRunView.vue'
import ReportView from '../views/ReportView.vue'
import InteractionView from '../views/InteractionView.vue'
import SwarmbookHomeView from '../views/swarmbook/SwarmbookHomeView.vue'
import SwarmbookUploadView from '../views/swarmbook/SwarmbookUploadView.vue'
import SwarmbookMetadataView from '../views/swarmbook/SwarmbookMetadataView.vue'
import SwarmbookEvidenceView from '../views/swarmbook/SwarmbookEvidenceView.vue'
import SwarmbookSimulationView from '../views/swarmbook/SwarmbookSimulationView.vue'
import SwarmbookReportView from '../views/swarmbook/SwarmbookReportView.vue'
import SwarmbookPersonasView from '../views/swarmbook/SwarmbookPersonasView.vue'
import SwarmbookCompareView from '../views/swarmbook/SwarmbookCompareView.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/process/:projectId',
    name: 'Process',
    component: Process,
    props: true
  },
  {
    path: '/simulation/:simulationId',
    name: 'Simulation',
    component: SimulationView,
    props: true
  },
  {
    path: '/simulation/:simulationId/start',
    name: 'SimulationRun',
    component: SimulationRunView,
    props: true
  },
  {
    path: '/report/:reportId',
    name: 'Report',
    component: ReportView,
    props: true
  },
  {
    path: '/interaction/:reportId',
    name: 'Interaction',
    component: InteractionView,
    props: true
  },
  {
    path: '/swarmbook',
    name: 'SwarmbookHome',
    component: SwarmbookHomeView
  },
  {
    path: '/swarmbook/project/:projectId/upload',
    name: 'SwarmbookUpload',
    component: SwarmbookUploadView,
    props: true
  },
  {
    path: '/swarmbook/project/:projectId/metadata',
    name: 'SwarmbookMetadata',
    component: SwarmbookMetadataView,
    props: true
  },
  {
    path: '/swarmbook/project/:projectId/evidence',
    name: 'SwarmbookEvidence',
    component: SwarmbookEvidenceView,
    props: true
  },
  {
    path: '/swarmbook/project/:projectId/simulate',
    name: 'SwarmbookSimulation',
    component: SwarmbookSimulationView,
    props: true
  },
  {
    path: '/swarmbook/project/:projectId/report',
    name: 'SwarmbookReport',
    component: SwarmbookReportView,
    props: true
  },
  {
    path: '/swarmbook/project/:projectId/personas',
    name: 'SwarmbookPersonas',
    component: SwarmbookPersonasView,
    props: true
  },
  {
    path: '/swarmbook/project/:projectId/compare',
    name: 'SwarmbookCompare',
    component: SwarmbookCompareView,
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
