import { useQuery } from '@tanstack/react-query'
import { Download, RefreshCw, Trash2, Clock, Layers, Eye, Check, Calendar, Loader2 } from 'lucide-react'
import { getHistory } from '@/lib/api'
import { api } from '@/lib/api'
import toast from 'react-hot-toast'
import { useNavigate } from 'react-router-dom'
import { useAppStore } from '@/store/appStore'

const STATUS_COLORS: Record<string, string> = {
  done: 'bg-accent/20 text-accent border border-accent/25',
  failed: 'bg-red-500/15 text-red-400 border border-red-500/20',
  processing: 'bg-secondary/20 text-secondary border border-secondary/25',
  queued: 'bg-yellow-500/15 text-yellow-400 border border-yellow-500/20',
  searching: 'bg-secondary/20 text-secondary border border-secondary/25',
  downloading: 'bg-secondary/20 text-secondary border border-secondary/25',
  packaging: 'bg-secondary/20 text-secondary border border-secondary/25',
}

const STATUS_BORDER: Record<string, string> = {
  done: 'border-l-[5px] border-l-accent',
  failed: 'border-l-[5px] border-l-red-500/80',
  processing: 'border-l-[5px] border-l-secondary animate-pulse',
  queued: 'border-l-[5px] border-l-yellow-500/70',
  searching: 'border-l-[5px] border-l-secondary animate-pulse',
  downloading: 'border-l-[5px] border-l-secondary animate-pulse',
  packaging: 'border-l-[5px] border-l-secondary animate-pulse',
}

export function HistoryPage() {
  const navigate = useNavigate()
  const { setCurrentJobId, setUiState, setQuery, setQueryType, setLanguage } = useAppStore()

  const { data: history, refetch, isLoading } = useQuery({
    queryKey: ['history'],
    queryFn: getHistory,
    refetchInterval: 10000,
  })

  const handleViewJob = (job: any) => {
    setCurrentJobId(job.id)
    setQuery(job.query)
    setQueryType(job.query_type)
    setLanguage(job.language || '')
    if (job.status === 'done') {
      setUiState('done')
    } else if (job.status === 'failed') {
      setUiState('failed')
    } else {
      setUiState('processing')
    }
    navigate('/')
  }

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this job and all its generated audio files?')) return
    try {
      await api.delete(`/api/jobs/${id}`)
      toast.success('Job deleted')
      refetch()
    } catch {
      toast.error('Delete failed')
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-6 pt-2 pb-12 space-y-8 animate-slideIn">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-display font-bold text-white">Job History</h1>
          <p className="text-muted text-sm mt-1">Manage and download your generated voice datasets</p>
        </div>
        <button
          onClick={() => refetch()}
          className="btn-secondary flex items-center gap-2 px-4 py-2 text-sm font-semibold cursor-pointer"
        >
          <RefreshCw className="w-4 h-4" /> Refresh
        </button>
      </div>

      {isLoading ? (
        <div className="text-center py-20 text-muted/70 flex flex-col items-center justify-center gap-3">
          <Loader2 className="w-8 h-8 animate-spin text-accent" />
          <span className="font-mono text-sm">Retrieving job history...</span>
        </div>
      ) : !history?.length ? (
        <div className="glass-card text-center py-20 text-muted/70 border-border/50">
          No jobs found. Start by creating your first dataset on the Search page!
        </div>
      ) : (
        <div className="space-y-4">
          {history.map((job) => {
            const isCompleted = job.status === 'done'
            const borderClass = STATUS_BORDER[job.status] || 'border-l-[5px] border-l-border/80'
            return (
              <div
                key={job.id}
                className={`glass-card flex items-center justify-between gap-4 p-5 hover:border-accent/40 transition-all duration-300 hover:scale-[1.005] hover:shadow-[0_4px_24px_rgba(0,0,0,0.4)] ${borderClass}`}
              >
                <div
                  className="flex-1 min-w-0 cursor-pointer space-y-2"
                  onClick={() => handleViewJob(job)}
                >
                  <div className="flex flex-wrap items-center gap-2.5">
                    <h3 className="font-bold text-white text-base truncate hover:text-accent transition-colors duration-200">
                      {job.query}
                    </h3>
                    <span className={`badge ${STATUS_COLORS[job.status] || 'bg-surface text-muted'}`}>
                      {job.status}
                    </span>
                    <span className="badge bg-background/50 border border-border/60 text-muted uppercase">
                      {job.query_type.replace('_', ' ')}
                    </span>
                    {job.language && (
                      <span className="badge bg-background/50 border border-border/60 text-accent uppercase">
                        {job.language}
                      </span>
                    )}
                  </div>
                  
                  <div className="flex flex-wrap items-center gap-5 text-xs text-muted/80">
                    <span className="flex items-center gap-1.5">
                      <Layers className="w-3.5 h-3.5 text-accent" />{' '}
                      {job.query_type === 'conversion'
                        ? `${job.total_clips} files`
                        : `${job.total_clips} clips`}
                    </span>
                    {job.query_type !== 'conversion' && (
                      <span className="flex items-center gap-1.5">
                        <Clock className="w-3.5 h-3.5 text-secondary" /> {(job.total_seconds / 60).toFixed(1)} min
                      </span>
                    )}
                    <span className="flex items-center gap-1.5">
                      <Calendar className="w-3.5 h-3.5 opacity-60" />
                      {new Date(job.created_at).toLocaleDateString(undefined, {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric',
                      })}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {isCompleted && (
                    <div className="flex items-center justify-center w-8 h-8 rounded-full bg-accent/15 border border-accent/25 text-accent shadow-[0_0_8px_rgba(0,229,255,0.15)] mr-1">
                      <Check className="w-4.5 h-4.5 stroke-[2.5]" />
                    </div>
                  )}
                  <button
                    onClick={() => handleViewJob(job)}
                    className="btn-secondary p-2.5 hover:bg-accent/10 hover:border-accent/40 hover:text-accent transition-colors cursor-pointer"
                    title="View Progress / Dataset"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                  {job.download_url && (
                    <a
                      href={job.download_url}
                      className="btn-secondary p-2.5 hover:bg-secondary/10 hover:border-secondary/40 hover:text-secondary transition-colors cursor-pointer"
                      title="Download Dataset ZIP"
                    >
                      <Download className="w-4 h-4" />
                    </a>
                  )}
                  <button
                    onClick={() => handleDelete(job.id)}
                    className="btn-secondary p-2.5 text-red-400 hover:bg-red-500/10 hover:border-red-500/40 hover:text-red-400 transition-colors cursor-pointer"
                    title="Delete Job"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
