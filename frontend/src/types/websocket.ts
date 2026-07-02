export type JobURL = {
  id: number
  url: string
  status: string
}

export type Job = {
  id: number
  status: string
  progress: number
  urls: JobURL[]
  created_at?: string
  updated_at?: string
}

export type ScrapeResult = {
  id: number
  job_url_id: number
  data: Record<string, unknown>
}

export function normalizeJob(job: Partial<Job> & { id?: number }): Job {
  return {
    id: job.id ?? 0,
    status: job.status ?? 'PENDING',
    progress: job.progress ?? 0,
    urls: Array.isArray(job.urls) ? job.urls : [],
    created_at: job.created_at,
    updated_at: job.updated_at,
  }
}

export function sortJobsByRecency(a: Job, b: Job) {
  const aTime = Date.parse(a.updated_at ?? a.created_at ?? '0')
  const bTime = Date.parse(b.updated_at ?? b.created_at ?? '0')

  return bTime - aTime || b.id - a.id
}
