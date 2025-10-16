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
- **October 16, 2025 - DM Self-Reply Fix (CRITICAL)**: Completely rewrote DM handling logic to prevent bot from replying to its own messages:
  - Now only processes the latest message in each thread (not all historical messages)
  - Converts user IDs to integers for accurate comparison
  - Skips any message from the bot itself (my_user_id == msg_user_id)
  - Added detailed logging showing which message triggered a reply
  - Prevents infinite loop of bot replying to itself
- **October 16, 2025 - Self-Reply Prevention Fix**: Fixed critical bug where bot could reply to its own messages. Added:
  - DM loop logic fix (continue instead of break for already-replied messages)
  - API error handling to prevent posting error messages as replies
  - Growth bot duplicate comment prevention (checks existing comments before posting)
- **October 16, 2025 - Instagram API Error Handling**: Added graceful handling for Instagram API `KeyError: 'data'` errors
  - Bot continues running even when Instagram API fails temporarily
  - Better error messages in logs for debugging
- **October 16, 2025 - Gemini API Improvements**: Enhanced Gemini error handling and logging
  - More detailed error messages
  - Prevents sending error messages as replies to users
- **October 16, 2025 - Session Cookie Login**: Added sessionid-based login to bypass Instagram rate limiting (429 errors), 2FA, and checkpoint challenges. This is now the recommended login method.
- **October 16, 2025 - Import to Replit**: Successfully imported and configured project in Replit environment
  - Installed all Python dependencies (Flask, instagrapi, google-generativeai)
  - Set up workflow for automatic server management
  - Added .gitignore for Python projects
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
