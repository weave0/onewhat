# Deploy OneWhat to Your Private Website - Step-by-Step Guide

## Deployment Strategy

Since OneWhat is a **GPU-accelerated backend API**, we need:

1. **Backend API** → Cloud server with GPU (Render, Railway, or your own VPS)
2. **Frontend UI** → Netlify (static site that calls your API)

**Why not all on Netlify?**
- Netlify is for static sites (HTML/CSS/JS only)
- OneWhat needs Python + GPU + ML models (13GB+)
- Solution: Backend on cloud server, frontend on Netlify

---

## Option 1: Render.com (Easiest - Recommended)

**Pros:** Free tier, auto-deploy from Git, SSL included, no credit card for trial  
**Cons:** CPU-only on free tier (slower), GPU instances cost $50-100/month

### Step 1: Prepare for Render

Create `render.yaml` in project root:

```yaml
services:
  # API Service
  - type: web
    name: onewhat-api
    env: docker
    dockerfilePath: ./infrastructure/docker/Dockerfile
    envVars:
      - key: WHISPER_DEVICE
        value: cpu  # Change to cuda if using GPU instance
      - key: NMT_DEVICE
        value: cpu
      - key: TTS_DEVICE
        value: cpu
      - key: API_HOST
        value: 0.0.0.0
      - key: API_PORT
        value: 10000
      - key: PYTHONUNBUFFERED
        value: 1
    healthCheckPath: /health
    disk:
      name: models
      mountPath: /app/models
      sizeGB: 20
```

### Step 2: Deploy to Render

1. **Create account:** https://render.com
2. **New Web Service** → Connect GitHub repo
3. **Settings:**
   - Environment: Docker
   - Region: Choose closest to you
   - Instance Type: Free (CPU) or Starter ($7/month for better CPU)
   - Disk: Add 20GB for models
4. **Deploy!** Render auto-builds and deploys

**Your API URL:** `https://onewhat-api.onrender.com`

### Step 3: Test Your API

```powershell
# Check health
curl https://onewhat-api.onrender.com/health

# Get languages
curl https://onewhat-api.onrender.com/languages
```

---

## Option 2: Railway.app (Easy, Better Performance)

**Pros:** Better performance than Render free tier, simple deploy  
**Cons:** Requires credit card, ~$5/month minimum

### Step 1: Create Railway Config

Create `railway.json`:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "infrastructure/docker/Dockerfile"
  },
  "deploy": {
    "numReplicas": 1,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Step 2: Deploy to Railway

```powershell
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up
```

**Your API URL:** Railway provides a URL like `onewhat-production.up.railway.app`

---

## Option 3: Your Own Server (Most Control)

**Best if you have:** Your own VPS (DigitalOcean, Linode, AWS EC2) with GPU

### Step 1: Setup Server

```bash
# SSH into your server
ssh user@your-server.com

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install NVIDIA Docker (if you have GPU)
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

### Step 2: Deploy with Docker

```bash
# Clone your repo
git clone https://github.com/yourusername/onewhat.git
cd onewhat

# Build image
docker build -f infrastructure/docker/Dockerfile -t onewhat-api .

# Run with GPU
docker run -d \
  --name onewhat \
  --gpus all \
  -p 80:8000 \
  -v $(pwd)/models:/app/models \
  -e WHISPER_DEVICE=cuda \
  -e NMT_DEVICE=cuda \
  -e TTS_DEVICE=cuda \
  onewhat-api

# Or without GPU
docker run -d \
  --name onewhat \
  -p 80:8000 \
  -v $(pwd)/models:/app/models \
  -e WHISPER_DEVICE=cpu \
  -e NMT_DEVICE=cpu \
  -e TTS_DEVICE=cpu \
  onewhat-api
```

### Step 3: Setup SSL with Caddy

Create `Caddyfile`:

```
api.yourwebsite.com {
    reverse_proxy localhost:8000
}
```

```bash
# Install Caddy
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/caddy-stable-archive-keyring.gpg] https://dl.cloudsmith.io/public/caddy/stable/deb/debian any-version main" | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy

# Run Caddy (auto SSL!)
sudo caddy run --config Caddyfile
```

**Your API:** `https://api.yourwebsite.com`

---

## Frontend Deployment (Netlify)

Now let's create a simple web UI and deploy to Netlify.

### Step 1: Create Frontend

I'll create a React frontend in the next step.

### Step 2: Deploy to Netlify

```powershell
# Install Netlify CLI
npm install -g netlify-cli

# Navigate to frontend
cd frontend

# Build
npm run build

# Deploy
netlify deploy --prod
```

Or use Netlify's web UI:
1. Go to https://netlify.com
2. Drag & drop your `frontend/build` folder
3. Done! Get URL like `onewhat.netlify.app`

---

## Environment Variables

For all deployments, set these:

```env
# Required
WHISPER_DEVICE=cpu  # or cuda if GPU available
NMT_DEVICE=cpu
TTS_DEVICE=cpu

# Optional - Performance
WHISPER_MODEL=medium  # Use smaller model on CPU
WHISPER_COMPUTE_TYPE=int8  # Faster on CPU

# Optional - API
CORS_ORIGINS=["https://onewhat.netlify.app"]  # Your frontend URL
API_HOST=0.0.0.0
API_PORT=8000

# Optional - Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

---

## Cost Comparison

| Option | Free Tier | Paid | Performance | Setup Time |
|--------|-----------|------|-------------|------------|
| **Render** | ✅ Yes (CPU) | $7-100/mo | ⭐⭐⭐ | 5 min |
| **Railway** | ❌ No | $5-50/mo | ⭐⭐⭐⭐ | 10 min |
| **Own Server** | ❌ No | $40-200/mo | ⭐⭐⭐⭐⭐ | 30 min |
| **Netlify (Frontend)** | ✅ Yes | $0-19/mo | ⭐⭐⭐⭐⭐ | 2 min |

---

## Recommended Setup for You

### For Testing/Demo (Free)
- **Backend:** Render.com free tier (CPU-only)
- **Frontend:** Netlify free tier
- **Cost:** $0/month
- **Performance:** ~2-3s latency (CPU slower)

### For Production (Best Value)
- **Backend:** Railway ($5-10/month for better CPU)
- **Frontend:** Netlify free tier
- **Cost:** ~$5-10/month
- **Performance:** ~1s latency (good CPU)

### For Best Performance
- **Backend:** Your own GPU server ($40-100/month)
- **Frontend:** Netlify free tier
- **Cost:** $40-100/month
- **Performance:** <500ms latency (GPU accelerated)

---

## Next Steps

1. Choose deployment option above
2. I'll create the frontend web UI for you
3. Deploy backend first, then frontend
4. Connect frontend to your backend API URL

**Which option would you like to use?**
- Render (easiest, free to try)
- Railway (better performance, $5/mo)
- Your own server (best performance, you manage)

Let me know and I'll guide you through the specific steps!
