/**
 * Resilient API Client with automatic cold-start detection, retry-with-backoff,
 * and user-friendly error normalization for Render/Cloud platforms.
 */

export interface FetchOptions extends RequestInit {
  timeoutMs?: number
  retries?: number
  onWakingUp?: () => void
}

/**
 * Executes an HTTP fetch with automatic retry on 504/502/503/network timeouts
 */
export async function resilientFetch(url: string, options: FetchOptions = {}): Promise<Response> {
  const { timeoutMs = 25000, retries = 1, onWakingUp, ...fetchOptions } = options

  let attempt = 0
  while (attempt <= retries) {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs)

    try {
      const response = await fetch(url, {
        ...fetchOptions,
        signal: controller.signal
      })
      clearTimeout(timeoutId)

      // If gateway timeout or server waking up, trigger retry
      if ((response.status === 504 || response.status === 502 || response.status === 503) && attempt < retries) {
        attempt++
        if (onWakingUp) onWakingUp()
        await new Promise((res) => setTimeout(res, 2500 * attempt))
        continue
      }

      return response
    } catch (err: any) {
      clearTimeout(timeoutId)
      const isTimeout = err.name === 'AbortError' || err.message?.includes('timeout')
      const isNetwork = err.message?.includes('Failed to fetch') || err.message?.includes('NetworkError')

      if ((isTimeout || isNetwork) && attempt < retries) {
        attempt++
        if (onWakingUp) onWakingUp()
        await new Promise((res) => setTimeout(res, 2500 * attempt))
        continue
      }

      throw err
    }
  }

  throw new Error('Server connection timed out. Please try again.')
}

/**
 * Normalizes HTTP status errors into user-friendly fintech UX explanations
 */
export function normalizeHttpError(err: any): string {
  const msg = (err?.message || '').toLowerCase()
  if (msg.includes('504') || msg.includes('timeout') || msg.includes('aborterror')) {
    return 'Intelligence server is warming up from sleep. Telemetry will sync in a moment.'
  }
  if (msg.includes('502') || msg.includes('503')) {
    return 'Backend services are currently deploying. Please retry shortly.'
  }
  if (msg.includes('failed to fetch') || msg.includes('network')) {
    return 'Unable to reach the server. Operating in offline/standalone client mode.'
  }
  return err?.message || 'A network error occurred.'
}
