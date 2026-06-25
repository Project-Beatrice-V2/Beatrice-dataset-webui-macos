import { Link, useLocation } from 'react-router-dom'
import { Mic, History, FileAudio, Search } from 'lucide-react'
import { motion } from 'framer-motion'
import { clsx } from 'clsx'

const navItems = [
  { path: '/', label: 'Search', icon: Search },
  { path: '/convert', label: 'Convert', icon: FileAudio },
  { path: '/history', label: 'History', icon: History },
]

export function Header() {
  const location = useLocation()

  return (
    <header className="sticky top-2 z-50 max-w-7xl mx-auto px-6 pointer-events-none mb-0">
      <div className="glass-dock rounded-2xl px-6 py-3 flex items-center justify-between border border-border/40 pointer-events-auto backdrop-blur-md">
        <Link to="/" className="flex items-center gap-3 group">
          <div className="w-9 h-9 rounded-xl bg-accent/10 border border-accent/30 flex items-center justify-center group-hover:bg-accent/20 transition-all duration-300 group-hover:scale-105 shadow-[0_0_10px_rgba(0,229,255,0.15)] group-hover:shadow-[0_0_15px_rgba(0,229,255,0.35)]">
            <Mic className="w-4.5 h-4.5 text-accent" />
          </div>
          <span className="font-display font-bold text-xl tracking-tight text-white group-hover:text-accent transition-colors duration-300">
            Voice<span className="text-transparent bg-clip-text bg-gradient-to-r from-accent to-secondary text-glow font-bold">Forge</span>
          </span>
        </Link>

        <nav className="flex items-center gap-1 bg-background/30 p-1 rounded-xl border border-border/30">
          {navItems.map(({ path, label, icon: Icon }) => {
            const isActive = location.pathname === path
            return (
              <Link
                key={path}
                to={path}
                className={clsx(
                  'relative flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all duration-300',
                  isActive ? 'text-accent font-bold' : 'text-muted hover:text-white'
                )}
              >
                {isActive && (
                  <motion.div
                    layoutId="active-nav-pill"
                    className="absolute inset-0 bg-accent/10 border border-accent/20 rounded-xl -z-10 shadow-[0_0_15px_rgba(0,229,255,0.08)]"
                    transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                  />
                )}
                <Icon className={clsx('w-4 h-4 transition-all duration-300', isActive ? 'scale-110 text-accent' : 'opacity-85')} />
                {label}
              </Link>
            )
          })}
        </nav>
      </div>
    </header>
  )
}
