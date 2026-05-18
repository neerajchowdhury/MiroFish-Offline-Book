import service, { requestWithRetry } from './index'

export const createBookSimProject = (data) => {
  return requestWithRetry(() => service.post('/api/book-sim/projects', data), 2, 500)
}

export const createEvidencePack = (data) => {
  return requestWithRetry(() => service.post('/api/book-sim/evidence-packs', data), 2, 500)
}

export const runBookSimulation = (data) => {
  return requestWithRetry(() => service.post('/api/book-sim/simulate', data), 2, 500)
}

export const getBookSimReport = (projectId) => {
  return service.get(`/api/book-sim/projects/${projectId}/report`)
}

export const chatWithBookPersona = (personaId, data) => {
  return requestWithRetry(() => service.post(`/api/book-sim/personas/${personaId}/chat`, data), 2, 500)
}

export const compareBookDrafts = (data) => {
  return requestWithRetry(() => service.post('/api/book-sim/compare', data), 2, 500)
}

export const getBookSimHealth = () => {
  return service.get('/api/book-sim/health')
}
