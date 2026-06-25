import { Search, Play, Loader2, Tv, Star, Mic, Gamepad2, Music, Sparkles } from 'lucide-react'
import { motion } from 'framer-motion'
import { useAppStore } from '@/store/appStore'
import { WaveformHero } from './WaveformHero'

const QUERY_TYPES = [
  { id: 'anime', label: 'Anime', icon: Tv },
  { id: 'celebrity', label: 'Celebrity', icon: Star },
  { id: 'voice_actor', label: 'Voice Actor', icon: Mic },
  { id: 'game_character', label: 'Game', icon: Gamepad2 },
  { id: 'musician', label: 'Musician', icon: Music },
  { id: 'fictional', label: 'Fictional', icon: Sparkles },
]

const LANGUAGES = [
  { id: 'jp', label: '🇯🇵 Japanese' },
  { id: 'en', label: '🇺🇸 English' },
  { id: 'both', label: 'Both' },
]

interface SearchBarProps {
  onSearch: () => void
  onGenerate: () => void
  loading: boolean
}

export function SearchBar({ onSearch, onGenerate, loading }: SearchBarProps) {
  const {
    query, setQuery, queryType, setQueryType,
    language, setLanguage, uiState, progress, preview,
  } = useAppStore()

  const showGenerate = preview !== null

  return (
    <div className="space-y-8 max-w-4xl mx-auto animate-slideIn">
      {/* Waveform Hero Visualizer Container */}
      <div className="relative rounded-2xl bg-surface/35 border border-border/50 p-1.5 backdrop-blur-xl shadow-2xl">
        <div className="absolute inset-0 bg-gradient-to-r from-accent/5 to-secondary/5 rounded-2xl pointer-events-none" />
        <WaveformHero uiState={uiState} progress={progress} />
      </div>

      <div className="space-y-4">
        {/* Search input field with background neon glow */}
        <div className="relative group">
          <div className="absolute -inset-0.5 bg-gradient-to-r from-accent to-secondary rounded-2xl blur-lg opacity-25 group-focus-within:opacity-40 transition duration-500" />
          <div className="relative flex items-center bg-surface/60 border border-border/80 rounded-2xl overflow-hidden shadow-2xl transition-all duration-300 group-focus-within:border-accent/40 backdrop-blur-md">
            <Search className="absolute left-5 w-5 h-5 text-muted group-focus-within:text-accent transition-colors duration-300" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && onSearch()}
              placeholder="Search for any character, celebrity, or voice actor..."
              className="w-full bg-transparent pl-14 pr-38 py-4 text-base font-display text-white placeholder-muted/40 focus:outline-none"
            />
            <button
              onClick={showGenerate ? onGenerate : onSearch}
              disabled={!query.trim() || loading}
              className="absolute right-3 btn-primary flex items-center gap-2 px-5 py-2.5 rounded-xl transition-transform active:scale-95 cursor-pointer disabled:opacity-50"
            >
              {loading ? (
                <Loader2 className="w-4.5 h-4.5 animate-spin" />
              ) : showGenerate ? (
                <Play className="w-4 h-4 fill-current" />
              ) : (
                <Search className="w-4 h-4" />
              )}
              <span className="font-semibold tracking-wide">{showGenerate ? 'Generate' : 'Search'}</span>
            </button>
          </div>
        </div>

        {/* Suggestion tags */}
        <div className="flex flex-wrap items-center justify-center gap-2.5 text-xs text-muted">
          <span className="opacity-70">Try searching:</span>
          {[
            { name: 'Satoru Gojo', type: 'anime' },
            { name: 'Hatsune Miku', type: 'musician' },
            { name: 'Eminem', type: 'celebrity' },
            { name: 'Geralt of Rivia', type: 'game_character' },
          ].map((s) => (
            <button
              key={s.name}
              onClick={() => {
                setQuery(s.name)
                setQueryType(s.type)
              }}
              className="px-3 py-1.5 rounded-xl bg-surface/35 border border-border/50 hover:border-accent/40 hover:text-white transition-all duration-300 cursor-pointer hover:bg-surface/75 hover:scale-102 hover:shadow-[0_2px_8px_rgba(0,229,255,0.08)]"
            >
              {s.name}
            </button>
          ))}
        </div>
      </div>

      {/* Category selector grid */}
      <div className="space-y-4">
        <span className="block text-xs font-bold text-muted/80 uppercase tracking-widest text-center">Category</span>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3.5">
          {QUERY_TYPES.map((t) => {
            const Icon = t.icon
            const isSelected = queryType === t.id
            return (
              <button
                key={t.id}
                onClick={() => setQueryType(t.id)}
                className={`relative flex flex-col items-center justify-center p-4 rounded-2xl border text-center transition-all duration-300 group cursor-pointer ${
                  isSelected
                    ? 'bg-accent/10 border-accent/70 text-accent shadow-[0_4px_20px_rgba(0,229,255,0.15)] scale-[1.03]'
                    : 'bg-surface/20 border-border/40 text-muted hover:text-white hover:border-accent/25 hover:bg-surface/45 hover:scale-[1.01]'
                }`}
              >
                {isSelected && (
                  <div className="absolute inset-0 bg-gradient-to-br from-accent/5 to-secondary/5 rounded-2xl pointer-events-none" />
                )}
                <div className={`p-2.5 rounded-xl mb-2 transition-all duration-300 ${
                  isSelected ? 'bg-accent/15 scale-110 shadow-[0_0_12px_rgba(0,229,255,0.15)]' : 'bg-background/40 group-hover:bg-accent/10 group-hover:scale-105'
                }`}>
                  <Icon className={`w-5 h-5 transition-colors duration-300 ${
                    isSelected ? 'text-accent' : 'text-muted group-hover:text-accent/90'
                  }`} />
                </div>
                <span className="text-xs font-bold tracking-wide">{t.label}</span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Target Language selection bar */}
      {(queryType === 'anime' || queryType === 'fictional' || queryType === 'game_character') && (
        <div className="flex flex-col items-center space-y-3 py-2 animate-fadeIn">
          <span className="text-xs font-bold text-muted/80 uppercase tracking-widest">Target Language</span>
          <div className="relative flex p-1 bg-surface/30 border border-border/50 rounded-2xl max-w-sm mx-auto shadow-inner">
            {LANGUAGES.map((l) => {
              const isSelected = language === l.id
              return (
                <button
                  key={l.id}
                  onClick={() => setLanguage(l.id)}
                  className={`relative px-5 py-2.5 rounded-xl text-xs font-bold tracking-wide transition-all duration-300 cursor-pointer ${
                    isSelected ? 'text-accent font-extrabold' : 'text-muted hover:text-white'
                  }`}
                >
                  {isSelected && (
                    <motion.div
                      layoutId="active-language-pill"
                      className="absolute inset-0 bg-accent/10 border border-accent/20 rounded-xl shadow-[0_0_15px_rgba(0,229,255,0.08)]"
                      transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                    />
                  )}
                  {l.label}
                </button>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
