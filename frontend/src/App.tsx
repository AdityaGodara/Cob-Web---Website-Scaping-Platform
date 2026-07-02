import { useEffect, useMemo, useState } from 'react'
import './App.css'

type JobURL = {
  id: number
  url: string
  status: string
}

type Job = {
  id: number
  status: string
  progress: number
  urls: JobURL[]
  created_at?: string
  updated_at?: string
}

type ScrapeResult = {
  id: number
  job_url_id: number
  data: Record<string, unknown>
}

const JOBS_API = '/api/v1/jobs/'

function normalizeJob(job: Partial<Job> & { id?: number }): Job {
  return {
    id: job.id ?? 0,
    status: job.status ?? 'PENDING',
    progress: job.progress ?? 0,
    urls: Array.isArray(job.urls) ? job.urls : [],
    created_at: job.created_at,
    updated_at: job.updated_at,
  }
}

function sortJobsByRecency(a: Job, b: Job) {
  const aTime = Date.parse(a.updated_at ?? a.created_at ?? '0')
  const bTime = Date.parse(b.updated_at ?? b.created_at ?? '0')

  return bTime - aTime || b.id - a.id
}

async function readJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || `Request failed with ${response.status}`)
  }

  return response.json() as Promise<T>
}

function App() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [selectedJobId, setSelectedJobId] = useState<number | null>(null)
  const [selectedJobDetails, setSelectedJobDetails] = useState<Job | null>(null)
  const [urlInput, setUrlInput] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSelectingJob, setIsSelectingJob] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [urlResults, setUrlResults] = useState<Record<number, ScrapeResult | null>>({})
  const [resultErrors, setResultErrors] = useState<Record<number, string>>({})
  const [loadingResults, setLoadingResults] = useState<Record<number, boolean>>({})

  const stats = useMemo(() => {
    const total = jobs.length
    const active = jobs.filter((job) => ['PENDING', 'RUNNING'].includes(job.status)).length
    const completed = jobs.filter((job) => job.status === 'SUCCESS').length

    return { total, active, completed }
  }, [jobs])

  const selectedJob = useMemo(() => {
    if (selectedJobDetails) {
      return selectedJobDetails
    }

    if (!selectedJobId) {
      return null
    }

    return jobs.find((job) => job.id === selectedJobId) ?? null
  }, [selectedJobDetails, selectedJobId, jobs])

  const fetchJobs = async (showLoading = true) => {
    if (showLoading) {
      setIsLoading(true)
    }
    setError(null)

    try {
      const response = await fetch(JOBS_API)
      const data = await readJson<Partial<Job>[]>(response)
      const normalizedJobs = data.map((job) => normalizeJob(job)).sort(sortJobsByRecency)
      setJobs(normalizedJobs)

      const nextSelectedJobId = selectedJobId ?? normalizedJobs[0]?.id ?? null
      setSelectedJobId(nextSelectedJobId)
      setSelectedJobDetails((current) => {
        if (!nextSelectedJobId) {
          return current ?? null
        }

        const freshMatch = normalizedJobs.find((job) => job.id === nextSelectedJobId)
        return freshMatch ?? current
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load jobs right now.')
    } finally {
      if (showLoading) {
        setIsLoading(false)
      }
    }
  }

  useEffect(() => {
    void fetchJobs(true)

    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        void fetchJobs(false)
      }
    }

    const handleWindowFocus = () => {
      void fetchJobs(false)
    }

    document.addEventListener('visibilitychange', handleVisibilityChange)
    window.addEventListener('focus', handleWindowFocus)

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange)
      window.removeEventListener('focus', handleWindowFocus)
    }
  }, [])

  const fetchUrlResult = async (jobUrlId: number) => {
    if (loadingResults[jobUrlId]) {
      return
    }

    setLoadingResults((current) => ({ ...current, [jobUrlId]: true }))
    setResultErrors((current) => ({ ...current, [jobUrlId]: '' }))

    try {
      const response = await fetch(`${JOBS_API}job_urls/${jobUrlId}/result`)
      if (!response.ok) {
        throw new Error('No result available yet.')
      }

      const result = await readJson<ScrapeResult>(response)
      setUrlResults((current) => ({ ...current, [jobUrlId]: result }))
    } catch {
      setResultErrors((current) => ({ ...current, [jobUrlId]: 'No result available yet.' }))
      setUrlResults((current) => ({ ...current, [jobUrlId]: null }))
    } finally {
      setLoadingResults((current) => ({ ...current, [jobUrlId]: false }))
    }
  }

  const selectJob = async (job: Job) => {
    setSelectedJobId(job.id)
    setSelectedJobDetails(job)
    setIsSelectingJob(true)
    setError(null)

    try {
      const response = await fetch(`${JOBS_API}${job.id}`)
      const data = await readJson<Partial<Job>>(response)
      setSelectedJobDetails(normalizeJob({ ...data, id: job.id }))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load job details.')
    } finally {
      setIsSelectingJob(false)
    }
  }

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const urls = urlInput
      .split(/\n|,|;/)
      .map((entry) => entry.trim())
      .filter(Boolean)
      .map((entry) => (entry.startsWith('http') ? entry : `https://${entry}`))

    if (urls.length === 0) {
      setError('Enter at least one valid URL.')
      return
    }

    setIsSubmitting(true)
    setError(null)

    try {
      const response = await fetch(JOBS_API, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ urls }),
      })
      const createdJob = await readJson<Partial<Job>>(response)
      setUrlInput('')
      setSelectedJobId(createdJob.id ?? null)
      setSelectedJobDetails(normalizeJob(createdJob))
      await fetchJobs()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Job creation failed.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const statusTone = (status: string) => {
    switch (status) {
      case 'SUCCESS':
        return 'good'
      case 'RUNNING':
        return 'warn'
      case 'FAILED':
        return 'bad'
      default:
        return 'neutral'
    }
  }

  return (
    <div className="app-shell">
      <header className="hero-card">
        <div>
          <p className="eyebrow">CobWeb scraping platform</p>
          <h1>Launch smarter website scrapes in seconds.</h1>
          <p className="hero-copy">
            Queue URLs, monitor progress, and inspect each scrape job from a single,
            polished control center.
          </p>
        </div>

        <div className="hero-stats">
          <div>
            <strong>{stats.total}</strong>
            <span>Total jobs</span>
          </div>
          <div>
            <strong>{stats.active}</strong>
            <span>Active</span>
          </div>
          <div>
            <strong>{stats.completed}</strong>
            <span>Succeeded</span>
          </div>
        </div>
      </header>

      <section className="dashboard-grid">
        <article className="panel form-panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Create a new job</p>
              <h2>Queue your next scrape</h2>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="job-form">
            <label htmlFor="urls">Website URLs</label>
            <textarea
              id="urls"
              value={urlInput}
              onChange={(event) => setUrlInput(event.target.value)}
              placeholder="https://example.com&#10;https://another-site.com"
              rows={8}
            />
            <button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Creating…' : 'Create scrape job'}
            </button>
          </form>
        </article>

        <article className="panel list-panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Recent jobs</p>
              <h2>Job board</h2>
            </div>
            <button type="button" className="ghost-button" onClick={() => void fetchJobs()}>
              Refresh
            </button>
          </div>

          {isLoading ? (
            <p className="panel-empty">Loading jobs…</p>
          ) : error ? (
            <p className="panel-empty">{error}</p>
          ) : jobs.length === 0 ? (
            <p className="panel-empty">No jobs have been created yet.</p>
          ) : (
            <div className="job-list">
              {jobs.map((job) => (
                <button
                  key={job.id}
                  type="button"
                  className={`job-card ${selectedJob?.id === job.id ? 'active' : ''}`}
                  onClick={() => void selectJob(job)}
                  aria-pressed={selectedJob?.id === job.id}
                >
                  <div className="job-card-top">
                    <span className={`pill ${statusTone(job.status)}`}>{job.status}</span>
                    <span className="job-id">#{job.id}</span>
                  </div>
                  <h3>Job {job.id}</h3>
                  <p>{job.urls.length} URL{job.urls.length === 1 ? '' : 's'}</p>
                  <div className="progress-row">
                    <div className="progress-track">
                      <div className="progress-fill" style={{ width: `${job.progress}%` }} />
                    </div>
                    <span>{job.progress}%</span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </article>
      </section>

      <article className="panel detail-panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Job details</p>
            <h2>{selectedJob ? `Inspect job #${selectedJob.id}` : 'Inspect a scrape'}</h2>
          </div>
        </div>

        {!selectedJob ? (
          <p className="panel-empty">Select a job to inspect its URLs and status.</p>
        ) : (
          <div className="detail-layout">
            {isSelectingJob ? (
              <div className="detail-loading">Loading job details…</div>
            ) : null}
            <div className="detail-summary">
              <div className="detail-row">
                <span className="detail-label">Status</span>
                <span className={`pill ${statusTone(selectedJob.status)}`}>{selectedJob.status}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Progress</span>
                <span>{selectedJob.progress}%</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">URLs</span>
                <span>{selectedJob.urls.length}</span>
              </div>
            </div>

            <div className="url-list">
              {selectedJob.urls.map((url) => (
                <div key={url.id} className="url-item">
                  <div className="url-item-main">
                    <div>
                      <p className="url-link">{url.url}</p>
                      <p className="url-meta">ID {url.id}</p>
                    </div>
                    <span className={`pill ${statusTone(url.status)}`}>{url.status}</span>
                  </div>

                  <div className="result-section">
                    {selectedJob.status === 'SUCCESS' && url.status === 'SUCCESS' ? (
                      <button
                        type="button"
                        className="result-button"
                        onClick={(event) => {
                          event.stopPropagation()
                          void fetchUrlResult(url.id)
                        }}
                        disabled={loadingResults[url.id]}
                      >
                        {loadingResults[url.id] ? 'Loading…' : urlResults[url.id] ? 'Refresh result' : 'Fetch result'}
                      </button>
                    ) : null}

                    {loadingResults[url.id] ? (
                      <p className="result-state">Loading scrape result…</p>
                    ) : resultErrors[url.id] ? (
                      <p className="result-state">{resultErrors[url.id]}</p>
                    ) : urlResults[url.id] ? (
                      <pre className="result-card">{JSON.stringify(urlResults[url.id]?.data, null, 2)}</pre>
                    ) : (
                      <p className="result-state">Result pending.</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </article>
    </div>
  )
}

export default App
