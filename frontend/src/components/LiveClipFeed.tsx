import { useAppStore } from '@/store/appStore'

export function LiveClipFeed() {
  const { liveClips, uiState } = useAppStore()

  if (uiState !== 'processing' && liveClips.length === 0) return null

  return (
    <div className="card">
      <h3 className="text-sm font-medium text-muted mb-4">Live Clip Feed</h3>
      <div className="max-h-64 overflow-y-auto space-y-1">
        {liveClips.length === 0 ? (
          <p className="text-sm text-muted text-center py-8">Waiting for clips...</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-muted text-left">
                <th className="pb-2 font-medium">File</th>
                <th className="pb-2 font-medium">Duration</th>
                <th className="pb-2 font-medium">SNR</th>
                <th className="pb-2 font-medium">Quality</th>
              </tr>
            </thead>
            <tbody>
              {liveClips.map((clip) => (
                <tr key={clip.id} className="border-t border-border/50 animate-in fade-in duration-300">
                  <td className="py-1.5 font-mono text-accent">{clip.filename}</td>
                  <td className="py-1.5">{clip.duration_s?.toFixed(1)}s</td>
                  <td className="py-1.5">{clip.snr_db?.toFixed(0)} dB</td>
                  <td className="py-1.5">
                    <span className={`badge ${
                      (clip.quality_score || 0) >= 80 ? 'bg-accent/20 text-accent' :
                      (clip.quality_score || 0) >= 60 ? 'bg-secondary/20 text-secondary' :
                      'bg-red-500/20 text-red-400'
                    }`}>
                      {clip.quality_score?.toFixed(0) || '—'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
