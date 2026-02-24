export interface ScanResult {
  id: string
  url: string
  is_phishing: boolean
  confidence: number
  risk_score: number
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  features: Record<string, number | boolean>
  feature_importance: Record<string, number>
  model_version: string
  scan_time_ms: number
  error?: string
  created_at: string
}

export interface BulkScanResponse {
  task_id: string
  status: string
  total_urls: number
  message: string
}

export interface BulkScanStatus {
  task_id: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  total_urls: number
  processed_urls: number
  results?: ScanResult[]
  created_at: string
  completed_at?: string
}

export interface StatsResponse {
  total_scans: number
  phishing_count: number
  clean_count: number
  avg_confidence: number
  phishing_rate: number
}

export interface HealthResponse {
  status: string
  version: string
  model_loaded: boolean
  database: string
  redis: string
}
