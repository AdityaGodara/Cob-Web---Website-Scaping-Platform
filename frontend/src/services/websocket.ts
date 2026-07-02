import { normalizeJob, type Job } from '../types/websocket'

const DEFAULT_RECONNECT_DELAY = 1000

export function createJobSocket(jobId: number, handlers: { onMessage: (job: Job) => void; onOpen?: () => void; onError?: (error: Event) => void; onClose?: () => void }) {
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const socket = new WebSocket(`${protocol}://${window.location.host}/ws/jobs/${jobId}`)

  socket.addEventListener('open', () => {
    handlers.onOpen?.()
  })

  socket.addEventListener('message', (event) => {
    try {
      const payload = JSON.parse(event.data as string) as Partial<Job>
      handlers.onMessage(normalizeJob(payload))
    } catch {
      handlers.onError?.(new Event('message-error'))
    }
  })

  socket.addEventListener('error', (event) => {
    handlers.onError?.(event)
  })

  socket.addEventListener('close', () => {
    handlers.onClose?.()
  })

  return socket
}

export function reconnectJobSocket(jobId: number, handlers: { onMessage: (job: Job) => void; onOpen?: () => void; onError?: (error: Event) => void; onClose?: () => void }, delay = DEFAULT_RECONNECT_DELAY) {
  return window.setTimeout(() => {
    createJobSocket(jobId, handlers)
  }, delay)
}
