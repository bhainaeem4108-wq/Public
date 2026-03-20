#!/bin/bash
# ─────────────────────────────────────────
# AUTO UPDATE SCRIPT
# Run this daily on your server to keep
# yt-dlp updated automatically
#
# To set up daily auto-run:
# 1. Open terminal on your server
# 2. Type: crontab -e
# 3. Add this line:
#    0 3 * * * /path/to/auto_update.sh >> /var/log/ytdlp_update.log 2>&1
# This runs every day at 3:00 AM
# ─────────────────────────────────────────

echo "================================"
echo "Auto-update started: $(date)"
echo "================================"

# Update yt-dlp
echo "Updating yt-dlp..."
pip install -U yt-dlp

# Check the version installed
echo "Current yt-dlp version:"
yt-dlp --version

# Restart the server so changes take effect
echo "Restarting server..."
# Uncomment the line that matches your setup:

# For Railway / Render - they auto-restart, nothing needed

# For your own VPS with systemd:
# sudo systemctl restart video-downloader

# For your own VPS with pm2:
# pm2 restart video-downloader

echo "Update complete: $(date)"
echo "================================"
