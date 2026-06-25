import { useState } from 'react'
import { ChevronDown, ChevronUp, Settings } from 'lucide-react'
import { useAppStore } from '@/store/appStore'

export function AdvancedOptions() {
  const [open, setOpen] = useState(false)
  const { options, setOptions } = useAppStore()

  return (
    <div className="card">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center justify-between w-full text-left"
      >
        <div className="flex items-center gap-2">
          <Settings className="w-4 h-4 text-accent" />
          <span className="font-medium">Advanced Options</span>
        </div>
        {open ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>

      {open && (
        <div className="mt-6 space-y-6 animate-in slide-in-from-top-2 duration-300">
          {/* Target Duration */}
          <div>
            <label className="text-sm text-muted mb-2 block">
              Target Duration: {options.target_duration_minutes} min
            </label>
            <input
              type="range" min={10} max={120} step={5}
              value={options.target_duration_minutes}
              onChange={(e) => setOptions({ target_duration_minutes: +e.target.value })}
              className="w-full accent-accent"
            />
          </div>

          {/* Sample Rate */}
          <div>
            <label className="text-sm text-muted mb-2 block">Sample Rate</label>
            <div className="flex gap-2">
              {[16000, 22050, 44100].map((sr) => (
                <button
                  key={sr}
                  onClick={() => setOptions({ target_sample_rate: sr })}
                  className={`btn-secondary text-sm ${options.target_sample_rate === sr ? 'border-accent text-accent' : ''}`}
                >
                  {sr}
                </button>
              ))}
            </div>
          </div>

          {/* Bit Depth */}
          <div>
            <label className="text-sm text-muted mb-2 block">Bit Depth</label>
            <div className="flex gap-2">
              {[16, 24, 32].map((bd) => (
                <button
                  key={bd}
                  onClick={() => setOptions({ bit_depth: bd })}
                  className={`btn-secondary text-sm ${options.bit_depth === bd ? 'border-accent text-accent' : ''}`}
                >
                  {bd}-bit
                </button>
              ))}
            </div>
          </div>

          {/* Channels */}
          <div>
            <label className="text-sm text-muted mb-2 block">Channels</label>
            <div className="flex gap-2">
              {(['mono', 'stereo'] as const).map((ch) => (
                <button
                  key={ch}
                  onClick={() => setOptions({ channels: ch })}
                  className={`btn-secondary text-sm capitalize ${options.channels === ch ? 'border-accent text-accent' : ''}`}
                >
                  {ch}
                </button>
              ))}
            </div>
          </div>

          {/* Clip Length */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm text-muted mb-2 block">Min Clip (s)</label>
              <input
                type="number" step={0.5} min={0.5} max={10}
                value={options.min_clip_duration_sec}
                onChange={(e) => setOptions({ min_clip_duration_sec: +e.target.value })}
                className="input-field w-full"
              />
            </div>
            <div>
              <label className="text-sm text-muted mb-2 block">Max Clip (s)</label>
              <input
                type="number" step={1} min={5} max={60}
                value={options.max_clip_duration_sec}
                onChange={(e) => setOptions({ max_clip_duration_sec: +e.target.value })}
                className="input-field w-full"
              />
            </div>
          </div>

          {/* Denoise Strength */}
          <div>
            <label className="text-sm text-muted mb-2 block">Noise Removal</label>
            <div className="flex gap-2">
              {(['off', 'light', 'medium', 'aggressive'] as const).map((s) => (
                <button
                  key={s}
                  onClick={() => setOptions({ denoise_strength: s })}
                  className={`btn-secondary text-sm capitalize ${options.denoise_strength === s ? 'border-accent text-accent' : ''}`}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          {/* Quality Threshold */}
          <div>
            <label className="text-sm text-muted mb-2 block">
              Quality Threshold: {options.quality_threshold}
            </label>
            <input
              type="range" min={0} max={100} step={5}
              value={options.quality_threshold}
              onChange={(e) => setOptions({ quality_threshold: +e.target.value })}
              className="w-full accent-accent"
            />
          </div>

          {/* Speaker Similarity Threshold */}
          <div>
            <label className="text-sm text-muted mb-2 block">
              Speaker Similarity: {options.speaker_similarity_threshold}
              <span className="ml-2 text-xs opacity-60">
                ({options.speaker_similarity_threshold >= 0.85 ? 'strict' : options.speaker_similarity_threshold >= 0.75 ? 'balanced' : 'lenient'})
              </span>
            </label>
            <input
              type="range" min={0.5} max={0.95} step={0.05}
              value={options.speaker_similarity_threshold}
              onChange={(e) => setOptions({ speaker_similarity_threshold: +e.target.value })}
              className="w-full accent-accent"
            />
            <p className="text-xs text-muted mt-1 opacity-60">
              Higher = stricter voice matching, fewer but purer clips
            </p>
          </div>

          {/* Output Format */}
          <div>
            <label className="text-sm text-muted mb-2 block">Output Format</label>
            <div className="flex flex-wrap gap-2">
              {(['ljspeech', 'vctk', 'rvc', 'raw', 'custom'] as const).map((f) => (
                <button
                  key={f}
                  onClick={() => setOptions({ output_format: f })}
                  className={`btn-secondary text-sm uppercase ${options.output_format === f ? 'border-accent text-accent' : ''}`}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>

          {/* Search Strategy */}
          <div>
            <label className="text-sm text-muted mb-2 block">Search Strategy</label>
            <div className="flex flex-wrap gap-2">
              {(['auto', 'hub_only', 'scrape_only', 'hybrid'] as const).map((s) => (
                <button
                  key={s}
                  onClick={() => setOptions({ search_strategy: s })}
                  className={`btn-secondary text-sm ${options.search_strategy === s ? 'border-accent text-accent' : ''}`}
                >
                  {s.replace('_', ' ')}
                </button>
              ))}
            </div>
          </div>

          {/* Toggles */}
          <div className="space-y-3">
            {[
              { key: 'use_demucs' as const, label: 'Vocal Separation (Demucs)' },
              { key: 'use_vad' as const, label: 'Voice Activity Detection' },
              { key: 'transcribe' as const, label: 'Auto-transcribe (Whisper)' },
            ].map(({ key, label }) => (
              <label key={key} className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={options[key]}
                  onChange={(e) => setOptions({ [key]: e.target.checked })}
                  className="w-4 h-4 rounded accent-accent"
                />
                <span className="text-sm">{label}</span>
              </label>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
