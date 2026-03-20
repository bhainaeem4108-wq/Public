# 🎬 Video Downloader Backend Server

Supports: **YouTube, TikTok, Instagram, Facebook**
Built with: Python + Flask + yt-dlp

---

## 📁 Files
```
app.py            → Main server code
requirements.txt  → Python packages needed
Procfile          → For Railway/Render hosting
auto_update.sh    → Daily yt-dlp auto-updater
```

---

## 🚀 HOW TO DEPLOY (Railway - Easiest)

### Step 1 — Create Account
- Go to railway.app
- Sign up with GitHub (free)

### Step 2 — Upload Your Code
- Create new project on Railway
- Upload these 4 files
- OR connect your GitHub repo

### Step 3 — Deploy
- Railway auto-detects Python
- Reads Procfile and starts server
- You get a live URL like:
  https://your-app.railway.app

### Step 4 — Test It
Open browser and go to your URL:
https://your-app.railway.app/
You should see: {"status": "running"}

---

## 🔌 API ENDPOINTS

### 1. Check Server
GET /
Returns: server status

### 2. Check App Version
GET /version
Returns: latest app version info
Your app calls this on startup to check for updates

### 3. Analyze URL (MAIN ENDPOINT)
POST /analyze
Body: { "url": "https://youtube.com/watch?v=..." }
Returns: title, thumbnail, duration, all available formats

Example response:
{
  "success": true,
  "platform": "YouTube",
  "title": "Video Title",
  "thumbnail": "https://...",
  "duration": "3:47",
  "formats": [
    { "quality": "1080p", "type": "video", "size": "48.3 MB", "format_id": "137" },
    { "quality": "720p",  "type": "video", "size": "24.1 MB", "format_id": "136" },
    { "quality": "MP3",   "type": "audio", "size": "4.2 MB",  "format_id": "140" }
  ]
}

### 4. Get Download Link
POST /get-link
Body: { "url": "...", "format_id": "137" }
Returns: direct download URL for the video

### 5. Update yt-dlp (Admin Only)
POST /update-ytdlp
Body: { "secret": "your-secret-key-here" }
Updates yt-dlp to latest version on server

---

## 🧪 TESTING WITH POSTMAN

1. Download Postman (free) from postman.com
2. Create new POST request
3. URL: https://your-app.railway.app/analyze
4. Body → raw → JSON:
   { "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ" }
5. Hit Send
6. You should see all video formats in response

---

## 🔄 KEEPING yt-dlp UPDATED

### Option A - Manual (anytime YouTube breaks)
POST /update-ytdlp
Body: { "secret": "your-secret-key" }

### Option B - Auto (recommended)
On Railway/Render: redeploy once a week
Takes 30 seconds, fully automatic

### Option C - Cron job (VPS only)
Run auto_update.sh daily (see file for instructions)

---

## 🔐 SECURITY TIPS
- Change ADMIN_SECRET in environment variables
- Never share your secret key
- Add rate limiting if you get too many users

---

## ❓ TROUBLESHOOTING

Problem: "Could not process URL"
Fix: Update yt-dlp via /update-ytdlp endpoint

Problem: Instagram/Facebook not working
Fix: Some posts require login - public posts work fine

Problem: Server times out
Fix: Increase timeout in Procfile (--timeout 180)

---

## 📞 YOUR APP CONNECTS LIKE THIS

// In your Android/Web app:
fetch('https://your-app.railway.app/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ url: userPastedURL })
})
.then(res => res.json())
.then(data => {
  // Show data.formats to user
  // Let them pick quality
  // Then call /get-link with chosen format_id
})
