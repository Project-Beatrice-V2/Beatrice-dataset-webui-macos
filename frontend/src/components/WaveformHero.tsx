import { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import type { UIState } from '@/store/appStore'

interface WaveformHeroProps {
  uiState: UIState
  progress: number
}

export function WaveformHero({ uiState, progress }: WaveformHeroProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const animRef = useRef<number>(0)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')!
    const dpr = window.devicePixelRatio || 1

    const resize = () => {
      const w = canvas.parentElement?.offsetWidth || canvas.offsetWidth
      const h = canvas.parentElement?.offsetHeight || canvas.offsetHeight
      canvas.width = w * dpr
      canvas.height = h * dpr
      ctx.scale(dpr, dpr)
    }

    resize()
    window.addEventListener('resize', resize)

    let frame = 0

    const draw = () => {
      const w = canvas.width / dpr
      const h = canvas.height / dpr
      ctx.clearRect(0, 0, w, h)

      const centerY = h / 2

      // Wave configurations based on UI state
      let config = {
        speed: 0.02,
        amplitude: 15,
        frequency: 1.5,
        glow: 'rgba(0, 229, 255, 0.4)',
      }

      switch (uiState) {
        case 'searching':
        case 'downloading':
          config = {
            speed: 0.08,
            amplitude: 28,
            frequency: 3.5,
            glow: 'rgba(139, 92, 246, 0.5)',
          }
          break
        case 'processing':
        case 'packaging':
          config = {
            speed: 0.04,
            amplitude: 35,
            frequency: 2.2,
            glow: 'rgba(0, 229, 255, 0.6)',
          }
          break
        case 'done':
          config = {
            speed: 0.015,
            amplitude: 18,
            frequency: 1.2,
            glow: 'rgba(0, 229, 255, 0.3)',
          }
          break
        case 'failed':
          config = {
            speed: 0.12,
            amplitude: 6,
            frequency: 8.0,
            glow: 'rgba(239, 68, 68, 0.4)',
          }
          break
        case 'idle':
        default:
          config = {
            speed: 0.025,
            amplitude: 16,
            frequency: 1.6,
            glow: 'rgba(0, 229, 255, 0.4)',
          }
      }

      // Draw 3 layers of overlapping waves
      const drawSingleWave = (
        speedMult: number,
        ampMult: number,
        freqMult: number,
        phase: number,
        gradientStart: string,
        gradientEnd: string,
        glowColor: string,
        lineWidth: number
      ) => {
        ctx.save()
        ctx.beginPath()

        // Enable glowing shadow
        ctx.shadowBlur = 12
        ctx.shadowColor = glowColor

        const gradient = ctx.createLinearGradient(0, 0, w, 0)
        gradient.addColorStop(0, 'rgba(0,0,0,0)')
        gradient.addColorStop(0.2, gradientStart)
        gradient.addColorStop(0.5, gradientEnd)
        gradient.addColorStop(0.8, gradientStart)
        gradient.addColorStop(1, 'rgba(0,0,0,0)')

        ctx.strokeStyle = gradient
        ctx.lineWidth = lineWidth
        ctx.lineCap = 'round'

        for (let x = 0; x < w; x++) {
          // Tapering envelope so waves fade out at both left and right edges
          const envelope = Math.pow(Math.sin((x / w) * Math.PI), 2)
          const angle = (x / w) * Math.PI * 2 * config.frequency * freqMult + frame * config.speed * speedMult + phase
          const y = centerY + Math.sin(angle) * config.amplitude * ampMult * envelope

          if (x === 0) {
            ctx.moveTo(x, y)
          } else {
            ctx.lineTo(x, y)
          }
        }

        ctx.stroke()
        ctx.restore()
      }

      if (uiState === 'failed') {
        // Red erratic static line
        drawSingleWave(1.0, 1.0, 1.0, 0, 'rgba(239, 68, 68, 0.6)', 'rgba(248, 113, 113, 0.8)', 'rgba(239, 68, 68, 0.4)', 2)
      } else {
        // Layer 1: Back slow wave (Secondary color)
        drawSingleWave(0.6, 0.7, 0.8, Math.PI / 3, 'rgba(139, 92, 246, 0.3)', 'rgba(167, 139, 250, 0.5)', 'rgba(139, 92, 246, 0.2)', 1.5)

        // Layer 2: Middle wave (Mix color)
        drawSingleWave(1.2, 0.85, 1.3, -Math.PI / 4, 'rgba(0, 229, 255, 0.35)', 'rgba(139, 92, 246, 0.45)', 'rgba(0, 229, 255, 0.25)', 2)

        // Layer 3: Main front wave (Accent color)
        drawSingleWave(1.0, 1.1, 1.0, 0, 'rgba(0, 229, 255, 0.6)', 'rgba(0, 229, 255, 0.95)', config.glow, 2.5)
      }

      frame++
      animRef.current = requestAnimationFrame(draw)
    }

    draw()
    return () => {
      cancelAnimationFrame(animRef.current)
      window.removeEventListener('resize', resize)
    }
  }, [uiState])

  return (
    <div className="relative w-full h-32 overflow-hidden rounded-xl bg-background/25">
      <canvas ref={canvasRef} className="w-full h-full block" />
      {uiState !== 'idle' && uiState !== 'previewing' && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="absolute bottom-3 right-4 px-2 py-0.5 rounded-md bg-accent/15 border border-accent/25 text-[10px] font-mono font-bold text-accent shadow-[0_0_10px_rgba(0,229,255,0.1)] uppercase tracking-wider"
        >
          {progress}%
        </motion.div>
      )}
    </div>
  )
}
