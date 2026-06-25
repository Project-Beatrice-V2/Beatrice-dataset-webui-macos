import { useState, useEffect } from 'react'
import toast from 'react-hot-toast'
import { ArrowLeft } from 'lucide-react'
import { useAppStore } from '@/store/appStore'
import { searchPreview, createJob } from '@/lib/api'
import { useJobWebSocket } from '@/hooks/useJobWebSocket'
import { SearchBar } from '@/components/SearchBar'
import { SourcePreview } from '@/components/SourcePreview'
import { AdvancedOptions } from '@/components/AdvancedOptions'
import { JobProgress } from '@/components/JobProgress'
import { LiveClipFeed } from '@/components/LiveClipFeed'
import { DatasetViewer } from '@/components/DatasetViewer'
import { useQuery } from '@tanstack/react-query'
import { getJob } from '@/lib/api'

export function HomePage() {
  const [loading, setLoading] = useState(false)
  const {
    query, queryType, language, options, uiState,
    preview, setPreview, setUiState, setCurrentJobId,
    currentJobId, reset,
  } = useAppStore()

  useJobWebSocket(currentJobId)

  const { data: jobStatus } = useQuery({
    queryKey: ['job', currentJobId],
    queryFn: () => getJob(currentJobId!),
    enabled: !!currentJobId && !['idle', 'previewing', 'done', 'failed'].includes(uiState),
    refetchInterval: 3000,
  })

  useEffect(() => {
    if (!jobStatus) return
    if (jobStatus.status === 'failed') {
      setUiState('failed')
      toast.error(jobStatus.error_msg || 'Job failed')
    } else if (jobStatus.status === 'done') {
      setUiState('done')
    } else if (jobStatus.status !== 'queued') {
      setUiState('processing')
    }
  }, [jobStatus, setUiState])

  const { data: completedJob } = useQuery({
    queryKey: ['job-done', currentJobId],
    queryFn: () => getJob(currentJobId!),
    enabled: !!currentJobId && uiState === 'done',
  })

  const handleSearch = async () => {
    if (!query.trim()) return
    setLoading(true)
    try {
      const result = await searchPreview(query, queryType, language)
      setPreview(result)
      setUiState('previewing')
    } catch (e) {
      toast.error('Search preview failed')
    } finally {
      setLoading(false)
    }
  }

  const handleGenerate = async () => {
    setLoading(true)
    try {
      const result = await createJob({
        query, query_type: queryType, language, options,
      })
      setCurrentJobId(result.job_id)
      setUiState('queued')
      toast.success('Dataset generation started!')
    } catch (e) {
      toast.error('Failed to start job')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="relative max-w-5xl mx-auto px-6 pt-2 pb-12 space-y-8">
      {uiState === 'idle' || uiState === 'previewing' ? (
        <>
          <div className="text-center space-y-2 mb-8">
            <h1 className="text-4xl font-display font-bold tracking-tight">
              AI Voice <span className="text-accent">Dataset</span> Creator
            </h1>
            <p className="text-muted max-w-xl mx-auto">
              Search any character, celebrity, or voice actor — automatically generate
              professional-grade voice datasets for TTS training, Beatrice model training, Rvc model training.
            </p>
          </div>

          <SearchBar onSearch={handleSearch} onGenerate={handleGenerate} loading={loading} />
        </>
      ) : (
        <div className="flex items-center justify-between pb-4 border-b border-border/60">
          <button
            onClick={() => reset()}
            className="flex items-center gap-2 text-sm text-muted hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" /> Back to Search
          </button>
          <span className="text-xs font-mono text-muted uppercase tracking-wider">
            Job ID: {currentJobId?.slice(0, 8)}
          </span>
        </div>
      )}

      {preview && uiState === 'previewing' && (
        <>
          <SourcePreview preview={preview} />
          <AdvancedOptions />
        </>
      )}

      {uiState !== 'idle' && uiState !== 'previewing' && uiState !== 'done' && (
        <>
          <JobProgress />
          <LiveClipFeed />
        </>
      )}

      {uiState === 'done' && completedJob && (
        <DatasetViewer job={completedJob} />
      )}

      {uiState === 'failed' && (
        <div className="card border-red-500/30 bg-red-500/5 text-center py-8">
          <p className="text-red-400 font-medium">Job failed</p>
          <p className="text-sm text-muted mt-2">Try adjusting settings or using a different search strategy.</p>
        </div>
      )}

      {(uiState === 'idle' || uiState === 'previewing') && (
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[350px] bg-accent/5 blur-[120px] rounded-full pointer-events-none -z-10 animate-pulse" style={{ animationDuration: '8s' }} />
      )}
    </div>
  )
}
