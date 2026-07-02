import { useEffect, useState } from 'react'
import { createJobSocket } from '../services/websocket'
import type { Job } from '../types/websocket'

export function useJobSocket(jobId: number | null) {
  const [job, setJob] = useState<Job | null>(null)
  const [connected, setConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!jobId) {
      setJob(null)
      setConnected(false)
      setError(null)
      return
    }

    let socket: WebSocket | null = null
    let reconnectTimer: number | undefined

    const handleOpen = () => {
      setConnected(true)
      setError(null)
    }

    const handleMessage = (nextJob: Job) => {
      setJob(nextJob)
    }

    const handleError = () => {
      setError('The job stream disconnected. Reconnecting…')
    }

    const handleClose = () => {
      setConnected(false)
      if (reconnectTimer === undefined) {
        reconnectTimer = window.setTimeout(() => {
          socket = createJobSocket(jobId, {
            onMessage: handleMessage,
            onOpen: handleOpen,
            onError: handleError,
            onClose: handleClose,
          })
        }, 1000)
      }
    }

    socket = createJobSocket(jobId, {
      onMessage: handleMessage,
      onOpen: handleOpen,
      onError: handleError,
      onClose: handleClose,
    })

    return () => {
      if (reconnectTimer !== undefined) {
        window.clearTimeout(reconnectTimer)
      }
      socket?.close()
    }
  }, [jobId])

  return { job, connected, error }
}
