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
        'has_gemini_key': bool(os.getenv('GEMINI_API_KEY'))
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
