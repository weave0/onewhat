# OneWhat - Quick Start Guide

Get up and running with OneWhat real-time translation in minutes.

## Prerequisites

- **Python 3.11+** installed
- **NVIDIA GPU** with CUDA 12.1+ (recommended) or CPU
- **16GB+ RAM** (32GB+ recommended for GPU)
- **50GB+ disk space** for models

## Installation

### 1. Clone and Navigate

```powershell
git clone <repository-url>
cd OneWhat
```

### 2. Run Setup Script

```powershell
# Windows PowerShell
.\scripts\setup.ps1

# Follow prompts to:
# - Create virtual environment
# - Install dependencies
# - Download models (optional)
```

### 3. Configure Environment

Edit `.env` file with your settings:

```env
# Device settings (cuda or cpu)
WHISPER_DEVICE=cuda
NMT_DEVICE=cuda
TTS_DEVICE=cuda

# API settings
API_HOST=0.0.0.0
API_PORT=8000
```

### 4. Download Models (if not done in setup)

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Download models
python scripts\download_models.py
```

## Running the System

### Option 1: Development Server

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run API with auto-reload
python -m uvicorn src.api.main:app --reload
```

Visit http://localhost:8000/docs for interactive API documentation.

### Option 2: Docker (Recommended for Production)

```powershell
cd infrastructure\docker

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api
```

Services:
- API: http://localhost:8000
- Grafana: http://localhost:3001 (admin/admin)
- Prometheus: http://localhost:9090

## Testing

### Quick Test

```powershell
# Test pipeline
python scripts\test_pipeline.py
```

### API Test

```powershell
# Using curl
curl http://localhost:8000/health

# Check supported languages
curl http://localhost:8000/languages
```

### WebSocket Test

See `frontend/` for a complete web client example.

## Usage Examples

### Python API

```python
import asyncio
import numpy as np
from src.orchestration.pipeline import create_pipeline, TranslationRequest

async def translate():
    # Create pipeline
    pipeline = create_pipeline()
    
    # Load audio (or generate test audio)
    audio = np.random.randn(16000).astype(np.float32)
    
    # Create request
    request = TranslationRequest(
        audio=audio.tolist(),
        sample_rate=16000,
        source_lang="en",
        target_lang="es",
    )
    
    # Translate
    response = await pipeline.translate(request)
    
    print(f"Transcription: {response.transcription}")
    print(f"Translation: {response.translation}")
    print(f"Latency: {response.latency_ms:.2f}ms")

asyncio.run(translate())
```

### REST API

```python
import requests
import numpy as np

# Generate test audio
audio = np.random.randn(16000).astype(np.float32).tolist()

# Make request
response = requests.post(
    "http://localhost:8000/translate",
    json={
        "audio": audio,
        "sample_rate": 16000,
        "source_lang": "en",
        "target_lang": "es",
    }
)

result = response.json()
print(f"Translation: {result['translation']}")
print(f"Latency: {result['latency_ms']:.2f}ms")
```

### WebSocket (Streaming)

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/translate');

// Send config
ws.onopen = () => {
    ws.send(JSON.stringify({
        source_lang: 'en',
        target_lang: 'es',
        sample_rate: 16000
    }));
};

// Receive translations
ws.onmessage = (event) => {
    const result = JSON.parse(event.data);
    console.log('Translation:', result.translation);
    console.log('Latency:', result.latency_ms);
};

// Send audio chunks
function sendAudioChunk(audioBytes) {
    ws.send(audioBytes);
}
```

## Supported Languages

OneWhat supports 200+ languages via NLLB-200:

**Major Languages:**
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Chinese (zh)
- Japanese (ja)
- Korean (ko)
- Arabic (ar)
- Hindi (hi)
- Portuguese (pt)
- Russian (ru)
- Italian (it)

And 188 more! See `/languages` endpoint for full list.

## Performance Tips

### GPU Optimization

```env
# Use float16 for better performance
WHISPER_COMPUTE_TYPE=float16

# Or int8 for even faster (slight quality trade-off)
WHISPER_COMPUTE_TYPE=int8
```

### Batch Processing

```python
# Translate multiple texts at once
results = nmt_engine.translate_batch(
    texts=["Hello", "Goodbye"],
    source_lang="eng_Latn",
    target_lang="spa_Latn",
)
```

### Model Selection

```env
# Faster but less accurate
NMT_MODEL=facebook/nllb-200-distilled-600M

# Slower but more accurate
NMT_MODEL=facebook/nllb-200-3.3B
```

## Troubleshooting

### CUDA Out of Memory

Reduce batch sizes or use INT8:

```env
WHISPER_COMPUTE_TYPE=int8
```

### Models Not Found

Download models manually:

```powershell
python scripts\download_models.py
```

### Port Already in Use

Change port in `.env`:

```env
API_PORT=8001
```

### Import Errors

Ensure virtual environment is activated:

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Next Steps

- 📖 Read full [README.md](../README.md)
- 🎯 Review [PROJECT_VISION.md](../PROJECT_VISION.md)
- 🏗️ Check [architecture documentation](../docs/)
- 🧪 Run [evaluation suite](../src/evaluation/)
- 🚀 Deploy with [Kubernetes](../infrastructure/kubernetes/)

## Support

- 📧 Email: support@onewhat.ai
- 💬 Discord: https://discord.gg/onewhat
- 🐛 Issues: https://github.com/onewhat/onewhat/issues

## License

See [LICENSE](../LICENSE) for details.
