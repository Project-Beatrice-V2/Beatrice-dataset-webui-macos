#!/bin/bash
# Beatrice Dataset Studio — one-time setup for macOS.
# Creates the Python venv, installs the ML stack and the web UI, and starts Redis.
set -e

echo "=== Beatrice Dataset Studio setup (macOS) ==="

ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND="$ROOT/voiceforge-backend"
cd "$BACKEND"

have() { command -v "$1" &>/dev/null; }

# Python 3.11 or 3.12: the ML stack (torch, pyannote, demucs) is unreliable elsewhere.
PYTHON=""
FALLBACK=""
for candidate in python3.12 python3.11 python3; do
    if have "$candidate"; then
        ver=$("$candidate" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "0.0")
        major=${ver%%.*}
        minor=${ver#*.}
        if [ "$major" -eq 3 ] && [ "$minor" -ge 11 ] && [ "$minor" -le 12 ]; then
            PYTHON="$candidate"
            break
        fi
        if [ -z "$FALLBACK" ] && [ "$major" -eq 3 ] && [ "$minor" -ge 13 ]; then
            FALLBACK="$candidate"
        fi
    fi
done
if [ -z "$PYTHON" ] && [ -n "$FALLBACK" ]; then
    PYTHON="$FALLBACK"
fi
if [ -z "$PYTHON" ]; then
    echo "ERROR: Python 3.11 or 3.12 not found (macOS's built-in python3 is too old)."
    echo "       Install it with: brew install python@3.12"
    exit 1
fi

PY_VER=$("$PYTHON" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Using Python $PY_VER ($PYTHON)"
if [ "${PY_VER#*.}" -gt 12 ]; then
    echo "WARNING: Python $PY_VER detected. The ML packages work best on 3.11 or 3.12."
    echo "         Install 3.12 with: brew install python@3.12"
fi

# FFmpeg (audio decoding) and Node.js (web UI) are required.
if ! have ffmpeg; then
    if have brew; then
        echo "Installing FFmpeg..."
        brew install ffmpeg
    else
        echo "ERROR: FFmpeg not found. Install Homebrew (https://brew.sh), then: brew install ffmpeg"
        exit 1
    fi
fi
if ! have npm; then
    if have brew; then
        echo "Installing Node.js..."
        brew install node
    else
        echo "ERROR: Node.js not found. Install Node.js 20.19+ or 22 LTS from https://nodejs.org"
        exit 1
    fi
fi

# Recreate the venv if it was built with a different Python version
if [ -d "venv" ]; then
    if [ -f "venv/.python-version" ]; then
        OLD_VER=$(cat venv/.python-version)
    else
        OLD_VER=$(venv/bin/python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "unknown")
    fi
    if [ "$OLD_VER" != "$PY_VER" ]; then
        echo "Removing old venv (was Python $OLD_VER, need $PY_VER)..."
        rm -rf venv
    fi
fi

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    "$PYTHON" -m venv venv
    echo "$PY_VER" > venv/.python-version
fi
source venv/bin/activate

echo "Installing Python dependencies (this downloads PyTorch and several GB of packages)..."
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
# resemblyzer pins the source-only `webrtcvad`; its dependencies are already installed
# (webrtcvad-wheels provides the same module), so install it without them.
python -m pip install --no-deps "resemblyzer>=0.1.4"

# Playwright for the BTVA resolver (optional)
echo "Installing Playwright Chromium (optional)..."
python -m playwright install chromium 2>/dev/null || echo "Playwright install skipped (optional)"

# Pre-download the Demucs model (optional, ~300 MB; otherwise it downloads on first use)
echo "Pre-downloading the Demucs model (htdemucs_ft)..."
python -c "
try:
    from demucs.pretrained import get_model
    get_model('htdemucs_ft')
    print('Demucs model downloaded')
except Exception as e:
    print(f'Demucs download skipped: {e}')
" 2>/dev/null || true

mkdir -p static/outputs tmp

if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created voiceforge-backend/.env from .env.example: add your HF_TOKEN for speaker diarization"
fi

echo "Initializing database..."
python -c "from database import init_db; init_db(); print('Database initialized')"

# Web UI
echo "Installing web UI dependencies..."
cd "$ROOT/frontend"
npm install

# Redis (required for the Celery job queue)
cd "$BACKEND"
if ! redis-cli ping &>/dev/null; then
    if have brew; then
        if ! brew list redis &>/dev/null; then
            echo "Installing Redis..."
            brew install redis
        fi
        echo "Starting Redis..."
        brew services start redis
        sleep 2
    fi
    if ! redis-cli ping &>/dev/null; then
        echo "WARNING: Redis is not running. Install it with: brew install redis && brew services start redis"
    else
        echo "Redis ready"
    fi
else
    echo "Redis already running"
fi

echo ""
echo "=== Setup complete ==="
echo "Next: put your Hugging Face token in voiceforge-backend/.env (HF_TOKEN=...), then run ./start.sh"
