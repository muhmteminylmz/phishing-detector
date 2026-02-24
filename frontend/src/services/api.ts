import axios, { AxiosInstance } from 'axios'
import type { ScanResult, BulkScanResponse, BulkScanStatus, StatsResponse, HealthResponse } from '../types'

const BASE_URL = import.meta.env.VITE_API_URL ?? '/api/v1'

const createClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: BASE_URL,
    timeout: 30000,
    headers: { 'Content-Type': 'application/json' },
  })

  // Retry interceptor
  client.interceptors.response.use(
    (res) => res,
    async (error) => {
      const config = error.config
      if (!config || config.__retryCount >= 3) return Promise.reject(error)
      config.__retryCount = (config.__retryCount ?? 0) + 1
      await new Promise((r) => setTimeout(r, 500 * config.__retryCount))
      return client(config)
    }
  )

  return client
}

const api = createClient()

export const scanUrl = async (url: string): Promise<ScanResult> => {
  const { data } = await api.post<ScanResult>('/scan/url', { url })
  return data
}

export const bulkScan = async (urls: string[]): Promise<BulkScanResponse> => {
  const { data } = await api.post<BulkScanResponse>('/scan/bulk', { urls })
  return data
}

export const getBulkStatus = async (taskId: string): Promise<BulkScanStatus> => {
  const { data } = await api.get<BulkScanStatus>(`/scan/bulk/${taskId}`)
  return data
}

export const getScanHistory = async (skip = 0, limit = 10): Promise<ScanResult[]> => {
  const { data } = await api.get<ScanResult[]>('/scan/history', {
    params: { skip, limit },
  })
  return data
}

export const getScanById = async (id: string): Promise<ScanResult> => {
  const { data } = await api.get<ScanResult>(`/scan/${id}`)
  return data
}

export const getStats = async (): Promise<StatsResponse> => {
  const { data } = await api.get<StatsResponse>('/reports/stats')
  return data
}

export const getHealth = async (): Promise<HealthResponse> => {
  const { data } = await api.get<HealthResponse>('/health')
  return data
}
