# 🚀 Complete Deployment Guide - OneWhat to Your Private Website

## What You'll Deploy

1. **Backend API** → Cloud server (Render/Railway/your VPS)
2. **Frontend Web UI** → Netlify (static hosting)

**Total time:** 15-30 minutes  
**Cost:** Free tier available, or $5-10/month for better performance

---

## 🎯 Recommended Approach (Easiest)

### Backend: Render.com (Free tier with CPU)
### Frontend: Netlify (Free)

**Total cost:** $0/month  
**Performance:** ~1-2s latency (CPU-only)  
**Best for:** Testing, demos, low-traffic sites

---

## Step-by-Step: Deploy Everything

### Part 1: Deploy Backend to Render (10 minutes)

#### 1. Prepare Your Repository

First, push your code to GitHub:

```powershell
cd o:\OneWhat

# Initialize git (if not already)
git init

# Add files
git add .

# Commit
git commit -m "Initial commit - OneWhat Translation System"

# Create repo on GitHub, then:
git remote add origin https://github.com/yourusername/onewhat.git
git push -u origin main
```

#### 2. Create Render Account

1. Go to https://render.com
2. Sign up with GitHub
3. Authorize Render to access your repos

#### 3. Create Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repo
3. Configure:
   - **Name:** `onewhat-api`
   - **Environment:** Docker
   - **Region:** Choose closest to you
   - **Branch:** main
   - **Dockerfile Path:** `infrastructure/docker/Dockerfile`
   - **Instance Type:** Free (or Starter $7/mo for faster CPU)

#### 4. Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**:

```
WHISPER_DEVICE=cpu
NMT_DEVICE=cpu
TTS_DEVICE=cpu
WHISPER_MODEL=medium
WHISPER_COMPUTE_TYPE=int8
API_HOST=0.0.0.0
API_PORT=10000
LOG_LEVEL=INFO
```

#### 5. Add Disk for Models

Under **"Disk"**:
- **Name:** models
- **Mount Path:** /app/models
- **Size:** 20GB

#### 6. Deploy!

Click **"Create Web Service"**

Render will:
- Build your Docker image (~10-15 minutes first time)
- Download models (~5 minutes)
- Start the API

**Your API URL:** `https://onewhat-api.onrender.com`

#### 7. Test Your API

```powershell
# Check health
curl https://onewhat-api.onrender.com/health

# Should return: {"status":"healthy","version":"1.0.0"}

# Get languages
curl https://onewhat-api.onrender.com/languages
```

✅ **Backend is live!**

---

### Part 2: Deploy Frontend to Netlify (5 minutes)

#### Option A: Drag & Drop (Easiest)

1. Go to https://app.netlify.com/drop
2. Drag your `o:\OneWhat\frontend` folder
3. Wait for upload
4. Done! Get URL like `https://onewhat-abc123.netlify.app`

#### Option B: Git Deploy (Auto-updates)

1. Push frontend to GitHub (if not already):
   ```powershell
   cd o:\OneWhat
   git add frontend/
   git commit -m "Add frontend"
   git push
   ```

2. Go to https://app.netlify.com
3. Click **"Add new site"** → **"Import an existing project"**
4. Choose GitHub → Select your repo
5. Configure:
   - **Base directory:** `frontend`
   - **Publish directory:** `frontend`
   - **Build command:** (leave empty)
6. Click **"Deploy site"**

**Your Frontend URL:** `https://onewhat-abc123.netlify.app`

#### 8. Update Frontend API URL

You have two options:

**Option 1: Just use the UI settings**
- Users configure API URL in the web UI
- Good for testing/demos

**Option 2: Hard-code your API URL**

Edit `frontend/index.html` line 409:

```javascript
let apiUrl = localStorage.getItem('apiUrl') || 'https://onewhat-api.onrender.com';
```

Then redeploy to Netlify.

---

### Part 3: Configure CORS (Critical!)

Your API needs to allow requests from your Netlify frontend.

#### On Render:

1. Go to your service → **Environment**
2. Add variable:
   ```
   CORS_ORIGINS=["https://onewhat-abc123.netlify.app"]
   ```
   (Replace with YOUR Netlify URL)
3. Save → Service auto-redeploys

#### If using .env locally:

Edit `o:\OneWhat\.env`:

```env
CORS_ORIGINS=["https://onewhat-abc123.netlify.app","http://localhost:8000"]
```

---

### Part 4: Test End-to-End

1. Open your Netlify URL: `https://onewhat-abc123.netlify.app`
2. Check connection status (should be green ✅)
3. Upload a short audio file
4. Select languages (e.g., English → Spanish)
5. Click "🚀 Translate Audio"
6. Wait 2-10 seconds
7. See results!

✅ **Everything is deployed!**

---

## 🎨 Customize Your Deployment

### Change Netlify Site Name

1. Go to **Site Settings** → **General**
2. Click **"Change site name"**
3. Enter: `onewhat-translation` or your preferred name
4. New URL: `https://onewhat-translation.netlify.app`

### Add Custom Domain

#### For Frontend (Netlify):

1. Go to **Site Settings** → **Domain Management**
2. Click **"Add custom domain"**
3. Enter: `translate.yourwebsite.com`
4. Add DNS record at your domain registrar:
   ```
   Type: CNAME
   Name: translate
   Value: onewhat-abc123.netlify.app
   ```
5. SSL auto-enabled!

#### For Backend (Render):

1. Go to service **Settings** → **Custom Domains**
2. Click **"Add Custom Domain"**
3. Enter: `api.yourwebsite.com`
4. Add DNS record:
   ```
   Type: CNAME
   Name: api
   Value: onewhat-api.onrender.com
   ```

### Update Frontend Branding

Edit `frontend/index.html`:

```html
<!-- Line 274 - Change title -->
<h1>🌍 Your Company Name</h1>
<p class="subtitle">Your Custom Tagline</p>

<!-- Line 393 - Change footer -->
<p>Powered by <strong>Your Company</strong></p>
```

Commit and push → Netlify auto-deploys!

---

## 💰 Cost Options

### Free Tier (Good for Testing)

**Backend:** Render Free
- ✅ Free forever
- ⚠️ CPU-only (slower, ~2-3s latency)
- ⚠️ Sleeps after 15min inactivity (30s wake-up)
- ✅ 750 hours/month

**Frontend:** Netlify Free
- ✅ 100GB bandwidth/month
- ✅ Unlimited sites
- ✅ SSL included
- ✅ Auto-deploy from Git

**Total:** $0/month

### Paid Tier (Better Performance)

**Backend:** Render Starter ($7/mo) or Railway ($5-10/mo)
- ✅ Better CPU
- ✅ No sleep
- ✅ ~1s latency
- ✅ 24/7 uptime

**Frontend:** Netlify Free (more than enough)

**Total:** $5-10/month

### GPU Tier (Best Performance)

**Backend:** Your own VPS with GPU ($40-200/mo)
- ✅ <500ms latency
- ✅ High concurrency
- ✅ Full control

**Frontend:** Netlify Free

**Total:** $40-200/month

---

## 🔧 Troubleshooting

### Backend won't build on Render

**Problem:** Docker build fails  
**Solution:**
1. Check build logs in Render dashboard
2. Ensure Dockerfile path is correct: `infrastructure/docker/Dockerfile`
3. Check you have all files committed to Git

### Backend is slow

**Problem:** 5-10s latency  
**Solutions:**
1. **Use smaller models:**
   ```env
   WHISPER_MODEL=small  # Instead of medium/large
   NMT_MODEL=facebook/nllb-200-distilled-600M  # Smallest NLLB
   ```
2. **Upgrade instance:** Render Starter ($7/mo) has better CPU
3. **Use GPU:** Switch to Railway or your own server

### Backend sleeps (Render Free)

**Problem:** First request takes 30s  
**Solutions:**
1. Upgrade to Render Starter ($7/mo) - no sleep
2. Use https://cron-job.org to ping `/health` every 10 min
3. Accept 30s wake-up for free tier

### CORS errors

**Problem:** Browser blocks requests  
**Solution:**
```env
# In Render environment variables
CORS_ORIGINS=["https://your-netlify-url.netlify.app"]
```

Make sure to include HTTPS!

### Models not loading

**Problem:** API crashes on startup  
**Solution:**
1. Ensure disk is added (20GB)
2. Check mount path: `/app/models`
3. Models auto-download on first run
4. Check logs for download progress

---

## 📊 Monitoring Your Deployment

### Check API Health

```powershell
# Health check
curl https://onewhat-api.onrender.com/health

# API docs
https://onewhat-api.onrender.com/docs
```

### View Logs (Render)

1. Go to your service
2. Click **"Logs"** tab
3. See real-time logs

### Analytics (Netlify)

1. Go to your site
2. Click **"Analytics"** tab
3. See visitor stats (free tier: basic stats)

---

## 🚀 Production Optimizations

### 1. Enable Caching

Add Redis to Render:

1. **New** → **Redis**
2. Name: `onewhat-redis`
3. Get internal URL
4. Add to API env: `REDIS_HOST=<internal-redis-url>`

### 2. Add Monitoring

Use Render's built-in monitoring:
- **Auto-restarts** on crashes
- **Health checks** every 30s
- **Email alerts** on downtime

### 3. Set Up CI/CD

Already done if using Git deploy!
- Push to GitHub → Auto-deploys
- Render builds → Tests → Deploys
- Rollback with one click

### 4. Add Rate Limiting

Edit `src/api/main.py`:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/translate")
@limiter.limit("10/minute")  # 10 requests per minute
async def translate(...):
    ...
```

---

## ✅ Final Checklist

Before going live:

- [ ] Backend deployed and responding at `/health`
- [ ] Frontend deployed to Netlify
- [ ] CORS configured correctly
- [ ] End-to-end translation test passed
- [ ] Custom domain configured (optional)
- [ ] Analytics enabled (optional)
- [ ] Rate limiting added (optional)
- [ ] Error handling tested
- [ ] Logs monitored

---

## 🎊 You're Live!

**Your Translation System:**
- 🌐 Frontend: `https://onewhat-abc123.netlify.app`
- 🔌 Backend: `https://onewhat-api.onrender.com`
- 📊 Docs: `https://onewhat-api.onrender.com/docs`

**Share it:**
- Send URL to friends/colleagues
- Add to your website
- Share on social media
- Use for your projects

---

## 📞 Need Help?

**Deployment Issues:**
- Check `DEPLOY_PRIVATE.md` for detailed guides
- Review Render/Netlify logs
- Test API endpoints directly

**Configuration:**
- Check `.env` variables
- Review `frontend/README.md`
- Test CORS settings

**Performance:**
- See "Cost Options" above
- Consider GPU upgrade
- Check model sizes

---

**Congratulations! Your private translation system is now live! 🎉**

*Share your URL and start translating!*
