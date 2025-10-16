from flask import Flask, render_template, request, jsonify
from bot_service import bot_instance
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SESSION_SECRET', 'dev-secret-key-change-in-production')

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/login', methods=['POST'])
def login():
    """Login to Instagram"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username va parol kerak!'}), 400
    
    success, message = bot_instance.login(username, password)
    return jsonify({'success': success, 'message': message})

@app.route('/api/login_sessionid', methods=['POST'])
def login_sessionid():
    """Login to Instagram using session cookie"""
    data = request.json
    sessionid = data.get('sessionid', '').strip()
    
    if not sessionid:
        return jsonify({'success': False, 'message': 'Session cookie kerak!'}), 400
    
    success, message = bot_instance.login_with_sessionid(sessionid)
    return jsonify({'success': success, 'message': message})

@app.route('/api/start', methods=['POST'])
def start_bot():
    """Start the bot"""
    success, message = bot_instance.start()
    return jsonify({'success': success, 'message': message})

@app.route('/api/stop', methods=['POST'])
def stop_bot():
    """Stop the bot"""
    success, message = bot_instance.stop()
    return jsonify({'success': success, 'message': message})

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get bot status"""
    status = bot_instance.get_status()
    return jsonify(status)

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get configuration"""
    return jsonify({
        'language': os.getenv('LANGUAGE', 'uz'),
        'check_interval': os.getenv('CHECK_INTERVAL', '30'),
        'has_gemini_key': bool(os.getenv('GEMINI_API_KEY')),
        'target_hashtags': os.getenv('TARGET_HASHTAGS', 'cafe,restoran,tadbirlar'),
        'auto_like_enabled': os.getenv('AUTO_LIKE_ENABLED', 'false'),
        'auto_follow_enabled': os.getenv('AUTO_FOLLOW_ENABLED', 'false'),
        'auto_comment_enabled': os.getenv('AUTO_COMMENT_ENABLED', 'false'),
        'daily_like_limit': os.getenv('DAILY_LIKE_LIMIT', '100'),
        'daily_follow_limit': os.getenv('DAILY_FOLLOW_LIMIT', '40'),
        'daily_comment_limit': os.getenv('DAILY_COMMENT_LIMIT', '10')
    })

@app.route('/api/growth/toggle', methods=['POST'])
def toggle_growth():
    """Toggle growth bot on/off"""
    data = request.json
    enabled = data.get('enabled', False)
    success, message = bot_instance.toggle_growth(enabled)
    return jsonify({'success': success, 'message': message})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
