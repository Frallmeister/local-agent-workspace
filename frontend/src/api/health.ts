/** Contract shared with the backend's Pydantic HealthResponse. */
export interface HealthResponse {
  status: 'ok'
}

function isHealthResponse(value: unknown): value is HealthResponse {
  return (
    typeof value === 'object' &&
    value !== null &&
    'status' in value &&
    value.status === 'ok'
  )
}

/** Validate external data before exposing it to the UI. */
export async function getHealth(signal?: AbortSignal): Promise<HealthResponse> {
  const timeout = AbortSignal.timeout(5000)
  const response = await fetch('/api/health', {
    signal: signal ? AbortSignal.any([signal, timeout]) : timeout,
    headers: { Accept: 'application/json' },
  })
  if (!response.ok) {
    throw new Error(`Health check failed (HTTP ${response.status}).`)
  }

  const data: unknown = await response.json()
  if (!isHealthResponse(data)) {
    throw new Error('The backend returned an unexpected health response.')
  }
  return data
}
