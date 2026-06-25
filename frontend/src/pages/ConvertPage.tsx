import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, Download, Check, Loader2, FileAudio, X, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { api } from '@/lib/api'

export function ConvertPage() {
  const [files, setFiles] = useState<File[]>([])
  const [converting, setConverting] = useState(false)
  const [progress, setProgress] = useState(0)
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null)
  const [sampleRate, setSampleRate] = useState(22050)
  const [bitDepth, setBitDepth] = useState(16)
  const [channels, setChannels] = useState('mono')
  const [normalize, setNormalize] = useState(true)

  const onDrop = useCallback((accepted: File[]) => {
    setFiles((prev) => [...prev, ...accepted])
    setDownloadUrl(null)
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'audio/*': ['.wav', '.mp3', '.flac', '.ogg', '.opus', '.m4a', '.aac', '.aiff', '.webm'],
      'application/octet-stream': ['.parquet', '.npy', '.arrow', '.hdf5', '.h5'],
      'application/zip': ['.zip'],
      'application/gzip': ['.tar.gz', '.tgz'],
    },
  })

  const removeFile = (idx: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== idx))
  }

  const clearAll = () => {
    setFiles([])
    setDownloadUrl(null)
  }

  const handleConvert = async () => {
    if (files.length === 0) return
    setConverting(true)
    setProgress(0)

    const formData = new FormData()
    files.forEach((f) => formData.append('files', f))
    formData.append('target_format', 'wav')
    formData.append('sample_rate', String(sampleRate))
    formData.append('bit_depth', String(bitDepth))
    formData.append('channels', channels)
    formData.append('normalize', String(normalize))

    try {
      const res = await api.post('/api/convert', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (e) => {
          if (e.total) setProgress(Math.round((e.loaded / e.total) * 100))
        },
      })
      setProgress(100)
      setDownloadUrl(res.data.download_url)
      toast.success(`Converted ${res.data.files_converted} files! Go to History to download the ZIP.`, { duration: 6000 })
    } catch {
      toast.error('Conversion failed')
    } finally {
      setConverting(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto px-6 pt-2 pb-12 space-y-8 animate-slideIn">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-display font-bold text-white">Universal Audio Converter</h1>
        <p className="text-muted text-sm max-w-md mx-auto">
          Convert raw clips, HuggingFace Parquet, or nested datasets into training-ready WAV audio.
        </p>
      </div>

      {/* Drag & Drop Zone */}
      <div
        {...getRootProps()}
        className={`glass-card border-dashed border-2 cursor-pointer transition-all duration-300 text-center py-14 relative overflow-hidden group ${
          isDragActive
            ? 'border-accent bg-accent/5 scale-[1.01] shadow-[0_0_20px_rgba(0,229,255,0.15)]'
            : 'border-border/80 hover:border-accent/40 hover:bg-surface/30'
        }`}
      >
        <input {...getInputProps()} />
        <div className="absolute inset-0 bg-gradient-to-br from-accent/5 via-transparent to-secondary/5 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
        <div className="relative space-y-4">
          <div className="w-16 h-16 mx-auto rounded-2xl bg-surface/80 border border-border/60 flex items-center justify-center group-hover:scale-105 group-hover:border-accent/40 group-hover:shadow-[0_0_15px_rgba(0,229,255,0.15)] transition-all duration-300">
            <Upload className={`w-7 h-7 transition-colors duration-300 ${isDragActive ? 'text-accent animate-bounce' : 'text-muted group-hover:text-accent'}`} />
          </div>
          <div>
            <p className="text-base font-semibold text-white">Drop files here or click to browse</p>
            <p className="text-xs text-muted/70 mt-2 font-mono max-w-sm mx-auto">
              WAV, MP3, FLAC, OGG, OPUS, M4A, Parquet, NPY, ZIP/TAR.GZ
            </p>
          </div>
        </div>
      </div>

      {/* Queued Files List */}
      {files.length > 0 && (
        <div className="glass-card space-y-4 border-border/60 shadow-xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-muted uppercase tracking-wider">
              Files Queued ({files.length})
            </span>
            <button
              onClick={clearAll}
              className="flex items-center gap-1 text-xs text-red-400 hover:text-red-300 transition-colors font-semibold cursor-pointer"
            >
              <Trash2 className="w-3.5 h-3.5" /> Clear All
            </button>
          </div>
          <div className="max-h-52 overflow-y-auto space-y-2 pr-2">
            {files.map((f, i) => (
              <div
                key={i}
                className="flex items-center justify-between bg-background/50 border border-border/50 rounded-xl px-4 py-2.5 hover:border-accent/20 transition-all duration-200"
              >
                <div className="flex items-center gap-2.5 min-w-0">
                  <FileAudio className="w-4 h-4 text-accent flex-shrink-0" />
                  <span className="text-xs font-mono text-white/90 truncate">{f.name}</span>
                  <span className="text-[10px] text-muted/65 flex-shrink-0">
                    ({(f.size / (1024 * 1024)).toFixed(2)} MB)
                  </span>
                </div>
                <button
                  onClick={() => removeFile(i)}
                  className="p-1 text-muted/60 hover:text-white rounded-lg hover:bg-white/5 transition-colors cursor-pointer"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Conversion Options Cards */}
      <div className="glass-card grid grid-cols-1 sm:grid-cols-2 gap-5 border-border/60 shadow-xl">
        <div>
          <label className="text-xs font-bold text-muted/80 uppercase tracking-widest mb-2 block">Sample Rate</label>
          <select
            value={sampleRate}
            onChange={(e) => setSampleRate(+e.target.value)}
            className="input-field w-full bg-background/45 border-border/60 text-sm cursor-pointer"
          >
            <option value={16000}>16000 Hz (TTS standard)</option>
            <option value={22050}>22050 Hz (Recommended)</option>
            <option value={44100}>44100 Hz (High-fidelity)</option>
          </select>
        </div>
        <div>
          <label className="text-xs font-bold text-muted/80 uppercase tracking-widest mb-2 block">Bit Depth</label>
          <select
            value={bitDepth}
            onChange={(e) => setBitDepth(+e.target.value)}
            className="input-field w-full bg-background/45 border-border/60 text-sm cursor-pointer"
          >
            <option value={16}>16-bit PCM</option>
            <option value={24}>24-bit PCM</option>
            <option value={32}>32-bit Float</option>
          </select>
        </div>
        <div>
          <label className="text-xs font-bold text-muted/80 uppercase tracking-widest mb-2 block">Channels</label>
          <select
            value={channels}
            onChange={(e) => setChannels(e.target.value)}
            className="input-field w-full bg-background/45 border-border/60 text-sm cursor-pointer"
          >
            <option value="mono">Mono (Recommended for TTS)</option>
            <option value="stereo">Stereo</option>
          </select>
        </div>
        <div className="flex items-center pl-1 pt-4 sm:pt-0">
          <label className="flex items-center gap-3 cursor-pointer group">
            <input
              type="checkbox"
              checked={normalize}
              onChange={(e) => setNormalize(e.target.checked)}
              className="w-4 h-4 rounded accent-accent bg-background border-border/60"
            />
            <span className="text-sm font-semibold text-white/95 group-hover:text-white transition-colors">
              Normalize loudness (-20 dBFS)
            </span>
          </label>
        </div>
      </div>

      {/* Progress Bar (Visible during conversion) */}
      {converting && (
        <div className="space-y-2 animate-fadeIn">
          <div className="flex justify-between text-xs font-bold text-muted">
            <span>Uploading & Converting...</span>
            <span>{progress}%</span>
          </div>
          <div className="w-full h-2 bg-background/80 rounded-full overflow-hidden p-0.5 border border-border/20">
            <div
              className="h-full bg-gradient-to-r from-accent to-secondary rounded-full transition-all duration-300 shadow-[0_0_10px_rgba(0,229,255,0.35)]"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-4">
        <button
          onClick={handleConvert}
          disabled={files.length === 0 || converting}
          className="btn-primary flex items-center gap-2.5 flex-1 justify-center py-3 rounded-xl tracking-wide cursor-pointer disabled:opacity-40"
        >
          {converting ? (
            <Loader2 className="w-4.5 h-4.5 animate-spin" />
          ) : (
            <Upload className="w-4.5 h-4.5" />
          )}
          Convert {files.length > 0 ? `(${files.length} Files)` : ''}
        </button>
        {downloadUrl && (
          <a
            href={downloadUrl}
            className="btn-secondary flex items-center gap-2.5 px-6 py-3 rounded-xl tracking-wide hover:shadow-[0_0_15px_rgba(139,92,246,0.15)] cursor-pointer"
          >
            <Download className="w-4.5 h-4.5" /> Download ZIP
          </a>
        )}
      </div>
    </div>
  )
}
