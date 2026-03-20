"""
Video Downloader Backend Server
Supports: YouTube, TikTok, Instagram, Facebook
Built with Python + Flask + yt-dlp
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import re
import os

app = Flask(__name__)
CORS(app)  # Allow requests from your app/website

# ─────────────────────────────────────────
# App version checker (for in-app updates)
# ─────────────────────────────────────────
APP_VERSION = {
    "latest_version": "1.0",
    "force_update": False,
    "update_url": "https://yourwebsite.com/app.apk",
    "message": "New version available with bug fixes!"
}

# ─────────────────────────────────────────
# Detect which platform the URL is from
# ─────────────────────────────────────────
def detect_platform(url):
    if "youtube.com" in url or "youtu.be" in url:
        return "YouTube"
    elif "tiktok.com" in url:
        return "TikTok"
    elif "instagram.com" in url:
        return "Instagram"
    elif "facebook.com" in url or "fb.watch" in url:
        return "Facebook"
    else:
        return "Unknown"

# ─────────────────────────────────────────
# Format file size nicely (e.g. 48.3 MB)
# ─────────────────────────────────────────
def format_size(bytes):
    if not bytes:
        return "Unknown"
    mb = bytes / (1024 * 1024)
    if mb >= 1000:
        return f"{mb/1024:.1f} GB"
    return f"{mb:.1f} MB"

# ─────────────────────────────────────────
# HOME - Check server is running
# ─────────────────────────────────────────
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "running",
        "message": "Video Downloader API is live!",
        "supported_platforms": ["YouTube", "TikTok", "Instagram", "Facebook"],
        "version": APP_VERSION["latest_version"]
    })

# ─────────────────────────────────────────
# VERSION CHECK - App calls this on startup
# ─────────────────────────────────────────
@app.route("/version", methods=["GET"])
def version():
    return jsonify(APP_VERSION)

# ─────────────────────────────────────────
# ANALYZE URL - Returns all available formats
# ─────────────────────────────────────────
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()

    # Validate input
    if not data or "url" not in data:
        return jsonify({"error": "Please provide a URL"}), 400

    url = data["url"].strip()
    platform = detect_platform(url)

    if platform == "Unknown":
        return jsonify({"error": "Platform not supported. Use YouTube, TikTok, Instagram or Facebook"}), 400

    # yt-dlp options - just extract info, don't download
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        # Build response
        formats = []
        seen = set()  # avoid duplicate qualities

        # Video formats
        for f in info.get("formats", []):
            height = f.get("height")
            ext = f.get("ext", "mp4")
            filesize = f.get("filesize") or f.get("filesize_approx")
            vcodec = f.get("vcodec", "none")
            acodec = f.get("acodec", "none")

            # Skip formats with no video or no audio (unless audio-only)
            if vcodec == "none" and acodec == "none":
                continue

            # Video formats
            if height and vcodec != "none":
                label = f"{height}p"
                if label not in seen and height in [2160, 1080, 720, 480, 360]:
                    seen.add(label)
                    formats.append({
                        "format_id": f["format_id"],
                        "quality": label,
                        "type": "video",
                        "ext": "mp4",
                        "size": format_size(filesize),
                        "label": f"{label} MP4"
                    })

            # Audio only formats
            if vcodec == "none" and acodec != "none" and "mp3" not in seen and "m4a" not in seen:
                seen.add("mp3")
                formats.append({
                    "format_id": f["format_id"],
                    "quality": "MP3",
                    "type": "audio",
                    "ext": "mp3",
                    "size": format_size(filesize),
                    "label": "MP3 Audio"
                })

        # Sort: best quality first
        quality_order = {"2160p": 0, "1080p": 1, "720p": 2, "480p": 3, "360p": 4, "MP3": 5}
        formats.sort(key=lambda x: quality_order.get(x["quality"], 99))

        # Get duration nicely
        duration_sec = info.get("duration", 0)
        minutes = int(duration_sec // 60)
        seconds = int(duration_sec % 60)
        duration_str = f"{minutes}:{seconds:02d}" if duration_sec else "Unknown"

        return jsonify({
            "success": True,
            "platform": platform,
            "title": info.get("title", "Unknown Title"),
            "thumbnail": info.get("thumbnail", ""),
            "duration": duration_str,
            "uploader": info.get("uploader", "Unknown"),
            "view_count": info.get("view_count", 0),
            "formats": formats
        })

    except yt_dlp.utils.DownloadError as e:
        return jsonify({"error": f"Could not process this URL: {str(e)[:200]}"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)[:200]}"}), 500


# ─────────────────────────────────────────
# GET DOWNLOAD LINK - Returns direct link
# ─────────────────────────────────────────
@app.route("/get-link", methods=["POST"])
def get_link():
    data = request.get_json()

    if not data or "url" not in data or "format_id" not in data:
        return jsonify({"error": "Provide url and format_id"}), 400

    url = data["url"].strip()
    format_id = data["format_id"]
    is_audio = data.get("is_audio", False)

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "format": format_id,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Get the direct download URL
            if "url" in info:
                download_url = info["url"]
            elif "formats" in info:
                for f in info["formats"]:
                    if f["format_id"] == format_id:
                        download_url = f.get("url", "")
                        break
                else:
                    download_url = info["formats"][-1].get("url", "")
            else:
                return jsonify({"error": "Could not get download link"}), 400

        return jsonify({
            "success": True,
            "download_url": download_url,
            "title": info.get("title", "video"),
            "ext": info.get("ext", "mp4")
        })

    except Exception as e:
        return jsonify({"error": str(e)[:200]}), 500


# ─────────────────────────────────────────
# UPDATE yt-dlp - Call this to self-update
# ─────────────────────────────────────────
@app.route("/update-ytdlp", methods=["POST"])
def update_ytdlp():
    # Protect with a secret key
    data = request.get_json()
    secret = data.get("secret", "")
    
    if secret != os.environ.get("ADMIN_SECRET", "your-secret-key-here"):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        import subprocess
        result = subprocess.run(
            ["pip", "install", "-U", "yt-dlp"],
            capture_output=True, text=True
        )
        return jsonify({
            "success": True,
            "message": "yt-dlp updated successfully",
            "output": result.stdout[-500:]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
