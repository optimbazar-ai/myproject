# Instagram Gemini AI Bot

## Overview
An intelligent Instagram bot that automatically replies to comments and direct messages using Google Gemini AI. Built with Flask web framework for easy monitoring and control through a web dashboard.

## Project Architecture
- **Backend**: Flask (Python 3.11)
- **Instagram API**: instagrapi library
- **AI Service**: Google Gemini AI (gemini-1.5-flash model)
- **Threading**: Background bot operation with manual start/stop controls

## Key Features
- Automatic comment replies using AI
- Automatic DM replies using AI
- Web dashboard for monitoring bot activity
- Manual start/stop controls
- Real-time activity logs
- Configurable response language (Uzbek by default)
- Dual login methods: password-based and session cookie (bypasses rate limits)

## Project Structure
```
/
├── app.py                  # Flask web application
├── bot_service.py          # Instagram bot logic
├── gemini_service.py       # Gemini AI integration
├── static/                 # CSS and JS files
│   └── style.css
├── templates/              # HTML templates
│   └── index.html
├── requirements.txt        # Python dependencies
└── .env                    # Configuration (not committed)
```

## Recent Changes
- **October 16, 2025 - Session Cookie Login**: Added sessionid-based login to bypass Instagram rate limiting (429 errors), 2FA, and checkpoint challenges. This is now the recommended login method.
- Initial project setup (October 16, 2025)
- Converted from Docker-based to Replit-compatible web application
- Added Flask web dashboard for bot monitoring
- Implemented session persistence to avoid re-login on every restart
- Added persistent storage for replied comment/DM IDs to prevent duplicates
- Improved thread management with proper join on stop
- Enhanced error handling with user-friendly Uzbek messages

## Configuration
Required environment variables:
- `INSTAGRAM_USERNAME`: Your Instagram username
- `INSTAGRAM_PASSWORD`: Your Instagram password
- `GEMINI_API_KEY`: Google Gemini API key
- `LANGUAGE`: Response language (default: "uz" for Uzbek)
- `CHECK_INTERVAL`: Seconds between checks (default: 30)

## User Preferences
- Original code was in Uzbek language
- Maintains original functionality while adding web interface
