from instagrapi import Client
import time
import os
from dotenv import load_dotenv
from gemini_service import generate_reply
import threading

load_dotenv()

class InstagramBot:
    def __init__(self):
        self.cl = None
        self.is_running = False
        self.is_logged_in = False
        self.replied_comments = set()
        self.replied_dms = set()
        self.activity_log = []
        self.thread = None
        
    def log_activity(self, message: str):
        """Add activity to log"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.activity_log.append(log_entry)
        if len(self.activity_log) > 100:
            self.activity_log.pop(0)
        print(log_entry)
    
    def login(self, username: str, password: str) -> tuple[bool, str]:
        """Login to Instagram"""
        try:
            self.cl = Client()
            self.cl.login(username, password)
            self.is_logged_in = True
            self.log_activity(f"✅ Instagram'ga muvaffaqiyatli kirdik: @{username}")
            return True, "Muvaffaqiyatli kirdik!"
        except Exception as e:
            self.log_activity(f"❌ Login xatosi: {str(e)}")
            return False, f"Xatolik: {str(e)}"
    
    def handle_comments(self):
        """Reply to comments on posts"""
        if not self.is_logged_in or not self.cl:
            return
        
        try:
            medias = self.cl.user_medias(self.cl.user_id, 5)
            for media in medias:
                comments = self.cl.media_comments(media.id)
                for comment in comments:
                    if comment.pk not in self.replied_comments and comment.user.pk != self.cl.user_id:
                        text = comment.text.strip()
                        if text:
                            language = os.getenv('LANGUAGE', 'uz')
                            reply = generate_reply(text, language)
                            self.cl.comment_reply(media.id, comment.pk, reply)
                            self.log_activity(f"💬 Kommentga javob: @{comment.user.username} → {reply[:50]}...")
                            self.replied_comments.add(comment.pk)
                            time.sleep(2)
        except Exception as e:
            self.log_activity(f"⚠️ Kommentlar xatosi: {str(e)}")
    
    def handle_dms(self):
        """Reply to direct messages"""
        if not self.is_logged_in or not self.cl:
            return
        
        try:
            threads = self.cl.direct_threads()
            for thread in threads:
                messages = thread.messages
                if not messages:
                    continue
                
                last_msg = messages[0]
                if last_msg.user_id != self.cl.user_id and last_msg.id not in self.replied_dms:
                    if last_msg.text:
                        language = os.getenv('LANGUAGE', 'uz')
                        reply = generate_reply(last_msg.text, language)
                        self.cl.direct_answer(thread.id, reply)
                        self.log_activity(f"📩 DM javob yuborildi: {reply[:50]}...")
                        self.replied_dms.add(last_msg.id)
                        time.sleep(2)
        except Exception as e:
            self.log_activity(f"⚠️ DM xatosi: {str(e)}")
    
    def run_bot(self):
        """Main bot loop"""
        check_interval = int(os.getenv('CHECK_INTERVAL', '30'))
        
        while self.is_running:
            try:
                self.handle_comments()
                self.handle_dms()
            except Exception as e:
                self.log_activity(f"⚠️ Bot xatosi: {str(e)}")
            
            time.sleep(check_interval)
    
    def start(self) -> tuple[bool, str]:
        """Start the bot"""
        if not self.is_logged_in:
            return False, "Avval Instagram'ga kiring!"
        
        if self.is_running:
            return False, "Bot allaqachon ishlamoqda!"
        
        self.is_running = True
        self.thread = threading.Thread(target=self.run_bot, daemon=True)
        self.thread.start()
        self.log_activity("🚀 Bot ishga tushdi!")
        return True, "Bot ishga tushdi!"
    
    def stop(self) -> tuple[bool, str]:
        """Stop the bot"""
        if not self.is_running:
            return False, "Bot ishlamayapti!"
        
        self.is_running = False
        self.log_activity("⏸️ Bot to'xtatildi!")
        return True, "Bot to'xtatildi!"
    
    def get_status(self) -> dict:
        """Get bot status"""
        return {
            'is_logged_in': self.is_logged_in,
            'is_running': self.is_running,
            'replied_comments': len(self.replied_comments),
            'replied_dms': len(self.replied_dms),
            'activity_log': self.activity_log[-20:]
        }

bot_instance = InstagramBot()
