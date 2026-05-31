import { describe, it, expect, beforeEach, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import NewSimulationWizardView from '../views/swarmbook/NewSimulationWizardView.vue';
import { createRouter, createWebHistory } from 'vue-router';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: { template: '<div></div>' } },
    { path: '/swarmbook/wizard', component: NewSimulationWizardView }
  ]
});

// Mock the swarmbookSession store
vi.mock('@/store/swarmbookSession', () => ({
  swarmbookSession: {
    projectId: null,
    title: '',
    authorName: '',
    contentType: 'novel',
    bookType: 'fiction',
    testGoal: '',
    targetReader: '',
    intendedPromise: '',
    genreCategory: '',
    compTitles: '',
    marketPositioning: '',
    privacyMode: 'local_only',
    simulationSeed: 42,
    cohortExclusions: [],
    runEditorBoard: true,
    fileMetadata: null
  },
  getSwarmbookSession: vi.fn(() => ({
    projectId: null,
    title: '',
    authorName: '',
    contentType: 'novel',
    bookType: 'fiction',
    testGoal: '',
    targetReader: '',
    intendedPromise: '',
    genreCategory: '',
    compTitles: '',
    marketPositioning: '',
    privacyMode: 'local_only',
    simulationSeed: 42,
    cohortExclusions: [],
    runEditorBoard: true,
    fileMetadata: null,
    metadata: { projectName: '', title: '', authorName: '' },
    manuscript: { text: '', filename: '', language: 'en', wordCount: 0, sectionCount: 0 },
    evidencePack: null,
    simulationRun: null,
    simulationConfig: { platforms: [], personaCount: 30, simulationSeed: 17 }
  })),
  resetSession: vi.fn(),
  updateField: vi.fn(),
  updateSwarmbookSession: vi.fn()
}));

// Mock the API
vi.mock('@/api/bookSim', () => ({
  default: {
    createProject: vi.fn().mockResolvedValue({ success: true, data: { project_id: '123' } }),
    parseFile: vi.fn().mockResolvedValue({ success: true, data: { text: 'mock text', word_count: 100 } }),
    buildEvidencePack: vi.fn().mockResolvedValue({ success: true, data: { evidence_pack: { pack_id: 'pack_1' } } })
  },
  getBookSimHealth: vi.fn().mockResolvedValue({ success: true, data: {} })
}));

describe('NewSimulationWizardView', () => {
  let wrapper;

  beforeEach(async () => {
    wrapper = mount(NewSimulationWizardView, {
      global: {
        plugins: [router],
        stubs: {
          SwarmbookAppShell: {
            template: '<div><slot></slot></div>'
          }
        }
      }
    });
    await router.isReady();
  });

  it('renders Step 1 initially', () => {
    expect(wrapper.text()).toContain('Step 1 of 6');
    expect(wrapper.text()).toContain('What are we testing?');
  });

  it('prevents proceeding to step 2 if required fields are empty', async () => {
    // Attempt to click "Save & Continue"
    const nextBtn = wrapper.find('.primary-btn');
    await nextBtn.trigger('click');

    // Should stay on step 1 and show validation error
    expect(wrapper.vm.currentStep).toBe(1);
    expect(wrapper.vm.validationErrors).toContain('Missing required field: Content title');
  });

  it('allows proceeding to step 2 if required fields are filled', async () => {
    // Fill the required fields
    wrapper.vm.form.projectName = 'test_project_123';
    wrapper.vm.form.title = 'Test Title';
    wrapper.vm.form.authorName = 'Test Author';
    wrapper.vm.form.genre = 'Fiction';
    
    // Trigger validation / next
    await wrapper.vm.nextStep();
    
    expect(wrapper.vm.currentStep).toBe(2);
  });
});
