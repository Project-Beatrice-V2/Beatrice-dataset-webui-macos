import { Database, Youtube, Globe, HardDrive, Clock, Layers } from 'lucide-react'
import type { SearchPreview } from '@/lib/api'

const SOURCE_ICONS: Record<string, typeof Database> = {
  huggingface: Database,
  youtube: Youtube,
  bilibili: Globe,
  nicovideo: Globe,
  openslr: HardDrive,
}

interface SourcePreviewProps {
  preview: SearchPreview
}

export function SourcePreview({ preview }: SourcePreviewProps) {
  const info = preview.character_info || {}

  return (
    <div className="card space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-wrap gap-4 text-sm">
        <div>
          <span className="text-muted">Character:</span>{' '}
          <span className="font-semibold text-white">{(info as Record<string, string>).name || '—'}</span>
        </div>
        {(info as Record<string, string>).series && (
          <div>
            <span className="text-muted">Series:</span>{' '}
            <span className="text-white">{(info as Record<string, string>).series}</span>
          </div>
        )}
        {(info as Record<string, string>).voice_actor_jp && (
          <div>
            <span className="text-muted">JP Voice:</span>{' '}
            <span className="text-white">{(info as Record<string, string>).voice_actor_jp}</span>
          </div>
        )}
        {(info as Record<string, string>).voice_actor_en && (
          <div>
            <span className="text-muted">EN Voice:</span>{' '}
            <span className="text-white">{(info as Record<string, string>).voice_actor_en}</span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {preview.sources_found.map((source, i) => {
          const Icon = SOURCE_ICONS[source.type] || Database
          return (
            <div key={i} className="bg-background border border-border rounded-lg p-4 space-y-2">
              <div className="flex items-center gap-2">
                <Icon className="w-4 h-4 text-accent" />
                <span className="font-medium capitalize">{source.type.replace('_', ' ')}</span>
              </div>
              {source.clips && (
                <p className="text-2xl font-display font-bold text-accent">{source.clips.toLocaleString()} clips</p>
              )}
              {source.videos && (
                <p className="text-2xl font-display font-bold text-accent">{source.videos} videos</p>
              )}
              {source.size_gb && (
                <p className="text-sm text-muted">{source.size_gb} GB</p>
              )}
              {source.estimated_duration_minutes && (
                <p className="text-sm text-muted flex items-center gap-1">
                  <Clock className="w-3 h-3" /> ~{source.estimated_duration_minutes} min
                </p>
              )}
              {source.dataset && (
                <p className="text-xs font-mono text-muted truncate">{source.dataset}</p>
              )}
            </div>
          )
        })}
      </div>

      <div className="flex items-center justify-between pt-4 border-t border-border">
        <div className="flex items-center gap-6 text-sm">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-secondary" />
            <span className="text-muted">Est. output:</span>
            <span className="font-semibold">~{preview.estimated_output_clips.toLocaleString()} clips</span>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-secondary" />
            <span className="text-muted">Duration:</span>
            <span className="font-semibold">~{preview.estimated_duration_minutes} min</span>
          </div>
          <div>
            <span className="text-muted">Strategy:</span>{' '}
            <span className="badge bg-secondary/20 text-secondary">{preview.recommended_strategy}</span>
          </div>
        </div>
      </div>
    </div>
  )
}
