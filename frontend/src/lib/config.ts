const API_URL = import.meta.env.VITE_API_URL || ''
const WS_URL = import.meta.env.VITE_WS_URL || `ws://${window.location.hostname}:8000`

export { API_URL, WS_URL }
