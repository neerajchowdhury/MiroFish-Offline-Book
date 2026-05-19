import axios from 'axios'

function apiErrorMessage(payload) {
  if (!payload || typeof payload !== 'object') return null
  const errorText = payload.error || payload.message
  if (!errorText) return null
  const code = payload.error_code ? ` (${payload.error_code})` : ''
  return `${errorText}${code}`
}

// Create axios instance
const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001',
  timeout: 300000, // 5 minute timeout (ontology generation may require longer time)
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
service.interceptors.request.use(
  config => {
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor (fault-tolerant retry mechanism)
service.interceptors.response.use(
  response => {
    const res = response.data

    // If the returned status code is not success, throw error
    if (!res.success && res.success !== undefined) {
      const message = apiErrorMessage(res) || 'Unknown API error'
      console.error('API Error:', message, res.details || {})
      const error = new Error(message)
      error.details = res.details
      error.errorCode = res.error_code
      return Promise.reject(error)
    }

    return res
  },
  error => {
    console.error('Response error:', error)

    const payload = error?.response?.data
    const message = apiErrorMessage(payload)
    if (message) {
      const normalized = new Error(message)
      normalized.details = payload.details
      normalized.errorCode = payload.error_code
      return Promise.reject(normalized)
    }

    // Handle timeout
    if (error.code === 'ECONNABORTED' && error.message.includes('timeout')) {
      console.error('Request timeout')
    }

    // Handle network error
    if (error.message === 'Network Error') {
      console.error('Network error - please check your connection')
    }

    return Promise.reject(error)
  }
)

// Request function with retry
export const requestWithRetry = async (requestFn, maxRetries = 3, delay = 1000) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await requestFn()
    } catch (error) {
      if (i === maxRetries - 1) throw error

      console.warn(`Request failed, retrying (${i + 1}/${maxRetries})...`)
      await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)))
    }
  }
}

export default service
