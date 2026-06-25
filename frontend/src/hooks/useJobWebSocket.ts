import { useEffect, useRef, useState } from 'react'
import { WS_URL } from '@/lib/config'
import { useAppStore } from '@/store/appStore'

export function useJobWebSocket(jobId: string | null) {
  const wsRef = useRef<WebSocket | null>(null)
  const {
    setProgress, setCurrentStage, setUiState, addLiveClip, setStages, uiState,
  } = useAppStore()

  useEffect(() => {
    if (!jobId) return
    if (['idle', 'previewing', 'done', 'failed'].includes(uiState)) return

    const ws = new WebSocket(`${WS_URL}/ws/jobs/${jobId}`)
    wsRef.current = ws

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)

      switch (data.event) {
        case 'stage_start':
          setCurrentStage(data.stage || '')
          if (data.progress) setProgress(data.progress)
          setUiState(mapStageToUiState(data.stage))
          updateStageStatus(data.stage, 'active')
          break
        case 'progress':
          setProgress(data.progress || 0)
          if (data.stage) setCurrentStage(data.stage)
          break
        case 'stage_complete':
          if (data.progress) setProgress(data.progress)
          updateStageStatus(data.stage, 'done')
          break
        case 'clip_ready':
          if (data.clip) {
            addLiveClip({
              id: Date.now(),
              filename: data.clip.filename,
              duration_s: data.clip.duration,
              snr_db: data.clip.snr,
              quality_score: data.clip.quality_score || 0,
              transcript: null,
              kept: true,
            })
          }
          break
        case 'done':
          setProgress(100)
          setUiState('done')
          break
        case 'error':
          setUiState('failed')
          break
      }
    }

    ws.onerror = () => setUiState('failed')

    return () => {
      ws.close()
      wsRef.current = null
    }
  }, [jobId, uiState])

  function updateStageStatus(stageName: string, status: 'done' | 'active' | 'pending') {
    const stages = useAppStore.getState().stages.map((s) => {
      if (s.name.toLowerCase().includes(stageName?.toLowerCase().split(' ')[0] || '')) {
        return { ...s, status }
      }
      if (status === 'active' && s.status === 'active') {
        return { ...s, status: 'done' as const }
      }
      return s
    })
    setStages(stages)
  }

  return wsRef
}

function mapStageToUiState(stage: string): import('@/store/appStore').UIState {
  const s = stage?.toLowerCase() || ''
  if (s.includes('search') || s.includes('enrichment')) return 'searching'
  if (s.includes('download')) return 'downloading'
  if (s.includes('packag')) return 'packaging'
  if (s.includes('separat') || s.includes('diariz') || s.includes('segment') || s.includes('quality') || s.includes('transcri')) return 'processing'
  return 'processing'
}
