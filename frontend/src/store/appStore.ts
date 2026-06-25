import { create } from 'zustand'
import type { JobOptions, SearchPreview, Clip } from '@/lib/api'
import { defaultOptions } from '@/lib/api'

export type UIState = 'idle' | 'previewing' | 'queued' | 'searching' | 'downloading' | 'processing' | 'packaging' | 'done' | 'failed'

interface AppState {
  query: string
  queryType: string
  language: string
  options: JobOptions
  uiState: UIState
  currentJobId: string | null
  preview: SearchPreview | null
  progress: number
  currentStage: string
  liveClips: Clip[]
  stages: { name: string; status: 'done' | 'active' | 'pending' }[]

  setQuery: (q: string) => void
  setQueryType: (t: string) => void
  setLanguage: (l: string) => void
  setOptions: (o: Partial<JobOptions>) => void
  setUiState: (s: UIState) => void
  setCurrentJobId: (id: string | null) => void
  setPreview: (p: SearchPreview | null) => void
  setProgress: (p: number) => void
  setCurrentStage: (s: string) => void
  addLiveClip: (clip: Clip) => void
  setStages: (stages: { name: string; status: 'done' | 'active' | 'pending' }[]) => void
  reset: () => void
}

const PIPELINE_STAGES = [
  'Query Enrichment', 'Hub Search', 'Download', 'Vocal Separation',
  'Diarization', 'Segmentation', 'Quality Filter', 'Speaker Verify', 'Transcription', 'Packaging',
]

export const useAppStore = create<AppState>((set) => ({
  query: '',
  queryType: 'anime',
  language: 'jp',
  options: defaultOptions(),
  uiState: 'idle',
  currentJobId: null,
  preview: null,
  progress: 0,
  currentStage: '',
  liveClips: [],
  stages: PIPELINE_STAGES.map((name) => ({ name, status: 'pending' as const })),

  setQuery: (q) => set({ query: q }),
  setQueryType: (t) => set({ queryType: t }),
  setLanguage: (l) => set({ language: l }),
  setOptions: (o) => set((s) => ({ options: { ...s.options, ...o } })),
  setUiState: (uiState) => set({ uiState }),
  setCurrentJobId: (id) => set({ currentJobId: id }),
  setPreview: (p) => set({ preview: p }),
  setProgress: (p) => set({ progress: p }),
  setCurrentStage: (s) => set({ currentStage: s }),
  addLiveClip: (clip) => set((s) => ({ liveClips: [clip, ...s.liveClips].slice(0, 50) })),
  setStages: (stages) => set({ stages }),
  reset: () => set({
    uiState: 'idle',
    currentJobId: null,
    preview: null,
    progress: 0,
    currentStage: '',
    liveClips: [],
    stages: PIPELINE_STAGES.map((name) => ({ name, status: 'pending' as const })),
  }),
}))
