# OneWhat Frontend

Simple, beautiful web interface for the OneWhat Translation API.

## Features

- 🎨 Beautiful, modern UI
- 📁 Upload audio files for translation
- 🌍 Support for 12+ major languages
- 📊 Real-time performance metrics
- 🔊 Play translated audio
- ⚙️ Configurable API endpoint

## Quick Start

### Option 1: Open Locally

Simply open `index.html` in your web browser!

```powershell
# From PowerShell
Start-Process frontend\index.html

# Or just double-click index.html
```

### Option 2: Deploy to Netlify (Recommended)

#### A. Drag & Drop (Easiest)

1. Go to https://app.netlify.com/drop
2. Drag the `frontend` folder into the upload area
3. Done! Get URL like `https://onewhat-abc123.netlify.app`

#### B. Using Netlify CLI

```powershell
# Install Netlify CLI
npm install -g netlify-cli

# Navigate to frontend
cd frontend

# Deploy
netlify deploy --prod

# Follow prompts, then get your URL!
```

#### C. Connect to Git (Auto-deploy on changes)

1. Push `frontend/` to GitHub
2. Go to https://app.netlify.com
3. Click "Add new site" → "Import an existing project"
4. Connect your GitHub repo
5. Set publish directory to `frontend`
6. Deploy!

### Option 3: Use with Local API

```powershell
# Start your API locally
.\venv\Scripts\Activate.ps1
python -m uvicorn src.api.main:app --reload

# Open frontend
Start-Process frontend\index.html

# Configure API URL in the UI to: http://localhost:8000
```

## Configuration

### API URL

The frontend needs to know where your API is:

1. Click **"⚙️ API Configuration"** in the UI
2. Enter your API URL:
   - Local: `http://localhost:8000`
   - Render: `https://onewhat-api.onrender.com`
   - Railway: `https://onewhat-production.up.railway.app`
   - Your server: `https://api.yourwebsite.com`
3. Click **"Test Connection"** to verify

### CORS (Important!)

Your API needs to allow requests from your frontend URL.

Edit your `.env` file:

```env
# For local testing
CORS_ORIGINS=["http://localhost:8000","http://127.0.0.1:8000"]

# For Netlify deployment
CORS_ORIGINS=["https://onewhat-abc123.netlify.app"]

# For both
CORS_ORIGINS=["http://localhost:8000","https://onewhat-abc123.netlify.app"]
```

Then restart your API.

## Usage

1. **Select Languages:**
   - Choose source language (language of your audio)
   - Choose target language (language to translate to)

2. **Upload Audio:**
   - Click "Choose Audio File"
   - Select MP3, WAV, or other audio file
   - File should be clear speech (not music)

3. **Translate:**
   - Click "🚀 Translate Audio"
   - Wait for processing (2-10 seconds depending on CPU/GPU)
   - See results!

4. **Results:**
   - Original transcription
   - Translated text
   - Performance metrics (latency breakdown)
   - Play translated audio

## Supported Audio Formats

- ✅ WAV
- ✅ MP3
- ✅ OGG
- ✅ M4A
- ✅ FLAC
- ✅ Most common formats

## Tips for Best Results

### Audio Quality

- **Clear speech:** Background noise reduces accuracy
- **Good microphone:** Better input = better output
- **Short clips:** 5-30 seconds work best
- **Single speaker:** Multiple speakers may confuse the system

### Language Selection

- **Match your audio:** Select the correct source language
- **Common languages:** English, Spanish, French work best
- **Accents:** System handles various accents well

### Performance

- **First translation:** May take longer (model loading)
- **Subsequent:** Much faster
- **CPU vs GPU:** GPU is 10-50x faster
- **Audio length:** Longer audio = more time

## Customization

### Change Theme Colors

Edit the CSS in `index.html`:

```css
/* Line 20-21 - Background gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Line 31 - Primary color */
color: #667eea;

/* Line 104 - Button gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Add More Languages

Edit the select options in `index.html` (around line 300):

```html
<option value="nl">Dutch</option>
<option value="sv">Swedish</option>
<option value="no">Norwegian</option>
<!-- Add more! -->
```

### Change Logo/Title

Edit line 274 in `index.html`:

```html
<h1>🌍 Your Company Name</h1>
<p class="subtitle">Your Tagline</p>
```

## Troubleshooting

### "Cannot connect to API"

**Problem:** Frontend can't reach backend  
**Solution:**
1. Check API URL in settings
2. Make sure API is running
3. Check CORS settings in API `.env`
4. Try accessing API directly: `https://your-api.com/health`

### "Translation failed"

**Problem:** API returned an error  
**Solution:**
1. Check audio file format (WAV/MP3 work best)
2. Check API logs for errors
3. Make sure languages are supported
4. Try a shorter audio clip

### "Audio won't play"

**Problem:** Translated audio doesn't play  
**Solution:**
1. Check browser console for errors
2. Try a different browser (Chrome/Edge work best)
3. Check audio format support
4. Download and play in media player

### CORS Errors

**Problem:** Browser blocks requests  
**Solution:**
```env
# In API .env file
CORS_ORIGINS=["https://your-frontend.netlify.app"]
```

Then restart API.

## Production Deployment Checklist

- [ ] Deploy backend API (Render/Railway/VPS)
- [ ] Get API URL (e.g., `https://api.yoursite.com`)
- [ ] Configure CORS in API `.env`
- [ ] Test API at `/health` endpoint
- [ ] Update frontend API URL in code (or make configurable)
- [ ] Deploy frontend to Netlify
- [ ] Test end-to-end translation
- [ ] Set up custom domain (optional)
- [ ] Add analytics (optional)

## Custom Domain (Optional)

### For Netlify

1. Go to Site Settings → Domain Management
2. Add custom domain (e.g., `translate.yourwebsite.com`)
3. Update DNS:
   - CNAME record: `translate` → `your-site.netlify.app`
4. SSL auto-enabled!

### For API

If using your own server:

1. Point DNS A record to your server IP
2. Use Caddy or nginx for SSL
3. Update frontend API URL

## Next Steps

1. **Deploy backend** using `DEPLOY_PRIVATE.md`
2. **Deploy this frontend** to Netlify
3. **Configure CORS** to allow frontend
4. **Test** end-to-end
5. **Customize** branding and colors
6. **Add features:**
   - Real-time microphone recording
   - Translation history
   - Download translated audio
   - Share translations

## Support

- Check `DEPLOY_PRIVATE.md` for backend deployment
- Check main `README.md` for API documentation
- Check `GETTING_STARTED.md` for setup help

## License

Same as main OneWhat project.
