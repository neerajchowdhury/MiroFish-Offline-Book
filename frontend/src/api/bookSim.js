import service, { requestWithRetry } from './index'

export const createBookSimProject = (data) => {
  return requestWithRetry(() => service.post('/api/book-sim/projects', data), 2, 500)
}

export const createEvidencePack = (data) => {
  return requestWithRetry(() => service.post('/api/book-sim/evidence-packs', data), 2, 500)
}

export const runBookSimulation = (data, config = {}) => {
  return requestWithRetry(() => service.post('/api/book-sim/simulate', data, config), 2, 500)
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

export const parseManuscriptFile = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return service.post('/api/book-sim/parse-file', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}
