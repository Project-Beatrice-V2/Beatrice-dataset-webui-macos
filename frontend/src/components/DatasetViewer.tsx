import { Download, Volume2, BarChart3 } from 'lucide-react'
import { motion } from 'framer-motion'
import type { Job } from '@/lib/api'
import { getDownloadUrl, getJobClips } from '@/lib/api'
import { QualityChart } from './QualityChart'
import { useQuery } from '@tanstack/react-query'

interface DatasetViewerProps {
  job: Job
}

export function DatasetViewer({ job }: DatasetViewerProps) {
  const isConversion = job.query_type === 'conversion'
  const durationMin = (job.total_seconds / 60).toFixed(1)

  const { data: clipsData } = useQuery({
    queryKey: ['job-clips', job.id],
    queryFn: () => getJobClips(job.id, 1, 200),
    enabled: !!job.id && !isConversion,
  })

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card space-y-6"
    >
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-display font-bold">
            {isConversion ? 'Conversion Complete' : 'Dataset Complete'}
          </h2>
          <p className="text-muted text-sm mt-1">
            {isConversion
              ? `${job.total_clips.toLocaleString()} files converted`
              : `${job.total_clips.toLocaleString()} clips · ${durationMin} minutes`}
          </p>
        </div>
        <a
          href={getDownloadUrl(job.id)}
          className="btn-primary flex items-center gap-2 animate-pulse-glow"
        >
          <Download className="w-4 h-4" />
          Download ZIP
        </a>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {isConversion ? (
          [
            { label: 'Converted Files', value: job.total_clips.toLocaleString() },
            { label: 'Format', value: job.options?.output_format || 'wav' },
          ].map((stat) => (
            <div key={stat.label} className="bg-background rounded-lg p-4 text-center">
              <p className="text-2xl font-display font-bold text-accent">{stat.value}</p>
              <p className="text-xs text-muted mt-1">{stat.label}</p>
            </div>
          ))
        ) : (
          [
            { label: 'Clips', value: job.total_clips.toLocaleString() },
            { label: 'Duration', value: `${durationMin} min` },
            { label: 'Strategy', value: job.strategy || 'auto' },
            { label: 'Format', value: job.options?.output_format || 'ljspeech' },
          ].map((stat) => (
            <div key={stat.label} className="bg-background rounded-lg p-4 text-center">
              <p className="text-2xl font-display font-bold text-accent">{stat.value}</p>
              <p className="text-xs text-muted mt-1">{stat.label}</p>
            </div>
          ))
        )}
      </div>

      {!isConversion && <QualityChart clips={clipsData?.clips || []} />}
    </motion.div>
  )
}
