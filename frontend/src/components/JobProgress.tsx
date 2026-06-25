import { useState } from 'react'
import { Check, Loader2, Clock, XCircle } from 'lucide-react'
import { useAppStore } from '@/store/appStore'
import { cancelJob } from '@/lib/api'
import toast from 'react-hot-toast'

export function JobProgress() {
  const [cancelling, setCancelling] = useState(false)
  const { progress, currentStage, stages, uiState, currentJobId, reset } = useAppStore()

  if (uiState === 'idle' || uiState === 'previewing') return null

  const handleCancel = async () => {
    if (!currentJobId) return
    setCancelling(true)
    try {
      await cancelJob(currentJobId)
      toast.success('Job cancelled successfully')
      reset()
    } catch (e) {
      toast.error('Failed to cancel job')
    } finally {
      setCancelling(false)
    }
  }

  return (
    <div className="card space-y-8 bg-surface/50 backdrop-blur-md border border-border/60 shadow-2xl animate-slideIn">
      {/* Progress Bar Header */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Loader2 className="w-4 h-4 text-accent animate-spin" />
            <span className="text-sm font-bold tracking-wide text-white">{currentStage || 'Processing...'}</span>
          </div>
          <span className="text-sm font-mono font-bold text-accent text-glow">{progress}%</span>
        </div>
        <div className="w-full h-2.5 bg-background/80 rounded-full overflow-hidden p-0.5 border border-border/30">
          <div
            className="h-full bg-gradient-to-r from-accent via-secondary to-accent rounded-full transition-all duration-500 shadow-[0_0_12px_rgba(0,229,255,0.45)]"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Stepper Pipeline Flow */}
      <div className="grid grid-cols-2 sm:grid-cols-5 xl:grid-cols-10 gap-x-2 gap-y-4 pt-2">
        {stages.map((stage, idx) => {
          const isDone = stage.status === 'done'
          const isActive = stage.status === 'active'
          return (
            <div
              key={stage.name}
              className={`flex flex-col items-center text-center p-3 rounded-2xl border transition-all duration-300 relative ${
                isDone
                  ? 'bg-accent/5 border-accent/30 text-accent'
                  : isActive
                  ? 'bg-secondary/10 border-secondary text-secondary animate-pulse scale-102 shadow-[0_0_15px_rgba(139,92,246,0.15)]'
                  : 'bg-background/40 border-border/30 text-muted/60'
              }`}
            >
              {/* Stepper Circle */}
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center border-2 mb-2 transition-all duration-300 ${
                  isDone
                    ? 'bg-accent/15 border-accent text-accent shadow-[0_0_10px_rgba(0,229,255,0.15)]'
                    : isActive
                    ? 'bg-secondary/25 border-secondary text-secondary shadow-[0_0_12px_rgba(139,92,246,0.25)]'
                    : 'bg-background border-border/60 text-muted/50'
                }`}
              >
                {isDone ? (
                  <Check className="w-3.5 h-3.5 stroke-[2.5]" />
                ) : isActive ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin stroke-[2.5]" />
                ) : (
                  <Clock className="w-3.5 h-3.5 opacity-40" />
                )}
              </div>
              
              {/* Label */}
              <span className={`text-[10px] font-bold tracking-wide leading-tight ${
                isDone ? 'text-accent' : isActive ? 'text-secondary font-extrabold' : 'text-muted/60'
              }`}>
                {stage.name}
              </span>
            </div>
          )
        })}
      </div>

      {/* Cancel button section */}
      <div className="pt-6 flex justify-center border-t border-border/30">
        <button
          onClick={handleCancel}
          disabled={cancelling}
          className="flex items-center gap-2 px-5 py-2.5 text-xs font-bold uppercase tracking-widest text-red-400 bg-red-950/20 hover:bg-red-950/40 border border-red-500/25 hover:border-red-500/50 rounded-xl transition-all duration-300 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
        >
          {cancelling ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Cancelling...
            </>
          ) : (
            <>
              <XCircle className="w-4 h-4" />
              Cancel Generation
            </>
          )}
        </button>
      </div>
    </div>
  )
}
