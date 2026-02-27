/**
 * Client-side phishing detection engine.
 *
 * Replicates the backend feature extraction and runs inference using
 * a Random Forest model exported as JSON.  This allows the app to work
 * entirely in the browser (e.g. on GitHub Pages) without any backend.
 */

// ── Constants (mirrored from backend) ──────────────────────────────────────

const SHORTENED_DOMAINS = new Set([
  'bit.ly', 'tinyurl.com', 'goo.gl', 'ow.ly', 't.co', 'is.gd',
  'buff.ly', 'adf.ly', 'short.link', 'rebrand.ly', 'tiny.cc',
  'cutt.ly', 'v.gd', 'bl.ink', 'shorturl.at',
])

const PHISHING_WORDS = new Set([
  'login', 'secure', 'bank', 'update', 'verify', 'account', 'confirm',
  'password', 'paypal', 'signin', 'wallet', 'ebay', 'amazon', 'alert',
  'suspended', 'urgent', 'limited', 'validate', 'credential', 'webscr',
])

const SUSPICIOUS_BRAND_SUBS = new Set([
  'paypa1', 'g00gle', 'g0ogle', 'amaz0n', 'micros0ft', 'netfl1x',
  'facebok', 'faceb00k', 'appleid', 'lnstagram', 'tw1tter',
])

const FEATURE_NAMES = [
  'url_length', 'hostname_length', 'path_length', 'query_length',
  'num_dots', 'num_hyphens', 'num_underscores', 'num_slashes',
  'num_question_marks', 'num_at_symbols', 'num_equals',
  'num_ampersands', 'num_percent', 'num_hash',
  'num_digits_in_domain', 'num_subdomains',
  'has_ip_address', 'has_https', 'https_in_hostname', 'has_port',
  'path_entropy', 'special_char_ratio', 'digit_ratio', 'letter_ratio',
  'is_shortened', 'suspicious_words', 'brand_impersonation',
  'url_depth', 'redirection_count', 'query_param_count',
  'fragment_length', 'tld_length', 'domain_length',
  'domain_age_days', 'domain_registration_length',
  'has_valid_ssl', 'ssl_issuer_is_trusted', 'ssl_days_remaining',
  'is_blacklisted', 'html_form_count', 'external_link_ratio',
  'null_hyperlinks', 'iframe_count', 'javascript_obfuscated',
  'favicon_from_external', 'meta_refresh', 'right_click_disabled',
]

const RISK_LEVELS: Array<{ min: number; max: number; level: string }> = [
  { min: 0, max: 30, level: 'LOW' },
  { min: 31, max: 60, level: 'MEDIUM' },
  { min: 61, max: 85, level: 'HIGH' },
  { min: 86, max: 100, level: 'CRITICAL' },
]

// ── Helpers ────────────────────────────────────────────────────────────────

function shannonEntropy(s: string): number {
  if (!s) return 0
  const freq: Record<string, number> = {}
  for (const c of s) freq[c] = (freq[c] ?? 0) + 1
  let ent = 0
  const len = s.length
  for (const count of Object.values(freq)) {
    const p = count / len
    ent -= p * Math.log2(p)
  }
  return Math.round(ent * 10000) / 10000
}

const IP_RE = /^(\d{1,3}\.){3}\d{1,3}$/

function parseUrl(raw: string): URL | null {
  try {
    let u = raw.trim()
    if (!/^https?:\/\//i.test(u)) u = 'http://' + u
    return new URL(u)
  } catch {
    return null
  }
}

/**
 * Lightweight TLD extraction.  Uses the URL hostname and a simple
 * heuristic: the last dot-separated segment is the TLD (suffix), the
 * one before it is the domain, everything before that is the subdomain.
 * Handles two-part TLDs like "co.uk" by checking a small allow-list.
 */
const TWO_PART_TLDS = new Set([
  'co.uk', 'org.uk', 'ac.uk', 'com.au', 'com.br', 'co.jp', 'co.kr',
  'co.in', 'co.nz', 'co.za', 'com.tr', 'com.mx', 'com.cn', 'com.tw',
  'com.sg', 'com.hk', 'com.ar', 'com.ua', 'org.au', 'net.au',
])

interface TldParts { subdomain: string; domain: string; suffix: string }

function extractTld(hostname: string): TldParts {
  const parts = hostname.toLowerCase().replace(/\.$/, '').split('.')
  if (parts.length <= 1) return { subdomain: '', domain: parts[0] ?? '', suffix: '' }
  if (parts.length === 2) return { subdomain: '', domain: parts[0], suffix: parts[1] }

  const lastTwo = parts.slice(-2).join('.')
  if (TWO_PART_TLDS.has(lastTwo) && parts.length >= 3) {
    return {
      subdomain: parts.slice(0, -3).join('.'),
      domain: parts[parts.length - 3],
      suffix: lastTwo,
    }
  }
  return {
    subdomain: parts.slice(0, -2).join('.'),
    domain: parts[parts.length - 2],
    suffix: parts[parts.length - 1],
  }
}

// ── Feature extraction ─────────────────────────────────────────────────────

export function extractFeatures(rawUrl: string): Record<string, number> {
  const parsed = parseUrl(rawUrl)
  if (!parsed) {
    // Return zeros for everything if parsing fails
    const z: Record<string, number> = {}
    for (const k of FEATURE_NAMES) z[k] = 0
    return z
  }

  const fullUrl = parsed.href
  const hostname = parsed.hostname ?? ''
  const path = parsed.pathname ?? ''
  const query = parsed.search?.replace('?', '') ?? ''
  const fragment = parsed.hash?.replace('#', '') ?? ''
  const { subdomain, domain, suffix } = extractTld(hostname)
  const registeredDomain = domain && suffix ? `${domain}.${suffix}` : ''

  const f: Record<string, number> = {}

  // URL length features
  f.url_length = fullUrl.length
  f.hostname_length = hostname.length
  f.path_length = path.length
  f.query_length = query.length

  // Character counts
  f.num_dots = (fullUrl.match(/\./g) ?? []).length
  f.num_hyphens = (fullUrl.match(/-/g) ?? []).length
  f.num_underscores = (fullUrl.match(/_/g) ?? []).length
  f.num_slashes = (fullUrl.match(/\//g) ?? []).length
  f.num_question_marks = (fullUrl.match(/\?/g) ?? []).length
  f.num_at_symbols = (fullUrl.match(/@/g) ?? []).length
  f.num_equals = (fullUrl.match(/=/g) ?? []).length
  f.num_ampersands = (fullUrl.match(/&/g) ?? []).length
  f.num_percent = (fullUrl.match(/%/g) ?? []).length
  f.num_hash = (fullUrl.match(/#/g) ?? []).length

  // Domain features
  f.num_digits_in_domain = (hostname.match(/\d/g) ?? []).length
  f.num_subdomains = subdomain ? subdomain.split('.').length : 0

  // Boolean indicators
  f.has_ip_address = IP_RE.test(hostname) ? 1 : 0
  f.has_https = parsed.protocol === 'https:' ? 1 : 0
  f.https_in_hostname = hostname.toLowerCase().includes('https') ? 1 : 0
  f.has_port = parsed.port ? 1 : 0

  // Entropy & ratios
  f.path_entropy = shannonEntropy(path)
  const totalLen = fullUrl.length || 1
  f.special_char_ratio = Math.round(([...fullUrl].filter(c => !/[a-zA-Z0-9]/.test(c)).length / totalLen) * 10000) / 10000
  f.digit_ratio = Math.round(([...fullUrl].filter(c => /\d/.test(c)).length / totalLen) * 10000) / 10000
  f.letter_ratio = Math.round(([...fullUrl].filter(c => /[a-zA-Z]/.test(c)).length / totalLen) * 10000) / 10000

  // Suspicious indicators
  f.is_shortened = SHORTENED_DOMAINS.has(registeredDomain) ? 1 : 0
  const lower = fullUrl.toLowerCase()
  f.suspicious_words = [...PHISHING_WORDS].some(w => lower.includes(w)) ? 1 : 0
  f.brand_impersonation = [...SUSPICIOUS_BRAND_SUBS].some(s => lower.includes(s)) ? 1 : 0

  // URL structure
  f.url_depth = path ? (path.match(/\//g) ?? []).length : 0
  f.redirection_count = Math.max(0, (fullUrl.match(/\/\//g) ?? []).length - 1)
  f.query_param_count = query ? new URLSearchParams(query).size : 0
  f.fragment_length = fragment.length

  // TLD features
  f.tld_length = suffix.length
  f.domain_length = domain.length

  // Placeholder features (would need external services)
  f.domain_age_days = -1
  f.domain_registration_length = -1
  f.has_valid_ssl = 0
  f.ssl_issuer_is_trusted = 0
  f.ssl_days_remaining = -1
  f.is_blacklisted = 0
  f.html_form_count = 0
  f.external_link_ratio = 0
  f.null_hyperlinks = 0
  f.iframe_count = 0
  f.javascript_obfuscated = 0
  f.favicon_from_external = 0
  f.meta_refresh = 0
  f.right_click_disabled = 0

  return f
}

// ── Model types ────────────────────────────────────────────────────────────

interface TreeData {
  children_left: number[]
  children_right: number[]
  feature: number[]
  threshold: number[]
  value: number[][]    // value[nodeIndex] = [count_class_0, count_class_1]
}

interface ModelData {
  version: string
  feature_names: string[]
  n_features: number
  n_trees: number
  trees: TreeData[]
  feature_importance: Record<string, number>
}

// ── Random Forest inference ────────────────────────────────────────────────

const LEAF_SENTINEL = -1

function predictTree(tree: TreeData, features: number[]): number[] {
  let node = 0
  while (tree.children_left[node] !== LEAF_SENTINEL) {
    const feat = tree.feature[node]
    if (features[feat] <= tree.threshold[node]) {
      node = tree.children_left[node]
    } else {
      node = tree.children_right[node]
    }
  }
  const val = tree.value[node]
  const total = val[0] + val[1]
  return total > 0 ? [val[0] / total, val[1] / total] : [0.5, 0.5]
}

function predictForest(model: ModelData, features: number[]): number[] {
  const probas = model.trees.map(t => predictTree(t, features))
  const avg = [0, 0]
  for (const p of probas) {
    avg[0] += p[0]
    avg[1] += p[1]
  }
  avg[0] /= probas.length
  avg[1] /= probas.length
  return avg
}

// ── Public API ─────────────────────────────────────────────────────────────

let _cachedModel: ModelData | null = null

export async function loadModel(): Promise<ModelData> {
  if (_cachedModel) return _cachedModel
  const base = import.meta.env.BASE_URL ?? '/'
  const resp = await fetch(`${base}model.json`)
  if (!resp.ok) throw new Error('Failed to load model.json')
  _cachedModel = await resp.json() as ModelData
  return _cachedModel
}

export interface LocalScanResult {
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
  created_at: string
}

export async function scanUrlLocally(rawUrl: string): Promise<LocalScanResult> {
  const start = performance.now()
  const model = await loadModel()
  const features = extractFeatures(rawUrl)
  const vector = model.feature_names.map(k => features[k] ?? 0)
  const proba = predictForest(model, vector)
  const phishingProb = proba[1]
  const riskScore = Math.round(phishingProb * 100)
  const isPhishing = phishingProb >= 0.5
  const confidence = isPhishing ? phishingProb : 1.0 - phishingProb
  const level = (RISK_LEVELS.find(r => riskScore >= r.min && riskScore <= r.max)?.level ?? 'CRITICAL') as LocalScanResult['risk_level']
  const elapsed = Math.round(performance.now() - start)

  return {
    id: crypto.randomUUID(),
    url: rawUrl,
    is_phishing: isPhishing,
    confidence: Math.round(confidence * 10000) / 10000,
    risk_score: riskScore,
    risk_level: level,
    features,
    feature_importance: model.feature_importance,
    model_version: model.version,
    scan_time_ms: elapsed,
    created_at: new Date().toISOString(),
  }
}
