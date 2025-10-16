from instagrapi import Client
import time
import os
import json
from pathlib import Path
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
        self.session_file = "instagram_session.json"
        self.replied_ids_file = "replied_ids.json"
        self._load_replied_ids()
        
    def _load_replied_ids(self):
        """Load previously replied IDs from file"""
        try:
            if Path(self.replied_ids_file).exists():
                with open(self.replied_ids_file, 'r') as f:
                    data = json.load(f)
                    self.replied_comments = set(data.get('comments', []))
                    self.replied_dms = set(data.get('dms', []))
        except Exception as e:
            print(f"Replied IDs yuklash xatosi: {e}")
    
    def _save_replied_ids(self):
        """Save replied IDs to file"""
        try:
            with open(self.replied_ids_file, 'w') as f:
                json.dump({
                    'comments': list(self.replied_comments),
                    'dms': list(self.replied_dms)
                }, f)
        except Exception as e:
            print(f"Replied IDs saqlash xatosi: {e}")
    
    def log_activity(self, message: str):
        """Add activity to log"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.activity_log.append(log_entry)
        if len(self.activity_log) > 100:
            self.activity_log.pop(0)
        print(log_entry)
    
    def login(self, username: str, password: str) -> tuple[bool, str]:
        """Login to Instagram with session persistence"""
        try:
            self.cl = Client()
            self.cl.delay_range = [1, 3]
            
            if Path(self.session_file).exists():
                try:
                    self.cl.load_settings(self.session_file)
                    self.cl.login(username, password)
                    self.log_activity("✅ Sessiondan qayta kirdik")
                except Exception as load_error:
                    self.log_activity(f"⚠️ Eski session ishlamadi, yangi yaratilmoqda...")
                    Path(self.session_file).unlink(missing_ok=True)
                    self.cl = Client()
                    self.cl.delay_range = [1, 3]
                    self.cl.login(username, password)
                    self.cl.dump_settings(self.session_file)
                    self.log_activity("✅ Yangi session yaratildi")
            else:
                self.cl.login(username, password)
                self.cl.dump_settings(self.session_file)
                self.log_activity("✅ Birinchi marta session yaratildi")
            
            self.is_logged_in = True
            self.log_activity(f"✅ Instagram'ga muvaffaqiyatli kirdik: @{username}")
            return True, "Muvaffaqiyatli kirdik!"
        except Exception as e:
            error_msg = str(e)
            self.log_activity(f"❌ Login xatosi: {error_msg}")
            
            if "429" in error_msg or "rate" in error_msg.lower():
                return False, "❌ Instagram sizni blokladi (429 Rate Limit). Parol orqali kirish ishlamaydi. Yuqoridagi 'Session Cookie' usulidan foydalaning!"
            elif "challenge" in error_msg.lower():
                return False, "Instagram tasdiqlash so'ramoqda. 'Session Cookie' usulidan foydalaning."
            elif "two_factor" in error_msg.lower() or "2fa" in error_msg.lower():
                return False, "2FA yoqilgan. 'Session Cookie' usulidan foydalaning."
            elif "checkpoint" in error_msg.lower():
                return False, "Instagram checkpoint talab qilmoqda. 'Session Cookie' usulidan foydalaning."
            elif "password" in error_msg.lower():
                return False, "Login yoki parol noto'g'ri. Qaytadan tekshiring."
            elif "NoneType" in error_msg:
                return False, "Instagram javob bermadi (bloklangan bo'lishi mumkin). 'Session Cookie' usulidan foydalaning."
            else:
                return False, f"Xatolik: {error_msg[:100]}"
    
    def login_with_sessionid(self, sessionid: str) -> tuple[bool, str]:
        """Login to Instagram using session cookie (bypasses rate limits and 2FA)"""
        try:
            self.cl = Client()
            self.cl.delay_range = [1, 3]
            
            self.cl.login_by_sessionid(sessionid)
            self.cl.dump_settings(self.session_file)
            
            username = self.cl.username
            self.is_logged_in = True
            self.log_activity(f"✅ Session cookie orqali muvaffaqiyatli kirdik: @{username}")
            return True, f"Muvaffaqiyatli! @{username} sifatida kirdik"
        except Exception as e:
            error_msg = str(e)
            self.log_activity(f"❌ Session cookie xatosi: {error_msg}")
            
            if "sessionid" in error_msg.lower() or "cookie" in error_msg.lower():
                return False, "Session cookie noto'g'ri yoki muddati o'tgan. Yangi sessionid oling."
            else:
                return False, f"Xatolik: {error_msg[:100]}"
    
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
                            self._save_replied_ids()
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
                        self._save_replied_ids()
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
            
            for _ in range(check_interval):
                if not self.is_running:
                    break
                time.sleep(1)
    
    def start(self) -> tuple[bool, str]:
        """Start the bot"""
        if not self.is_logged_in:
            return False, "Avval Instagram'ga kiring!"
        
        if self.is_running:
            return False, "Bot allaqachon ishlamoqda!"
        
        if self.thread and self.thread.is_alive():
            return False, "Avvalgi thread hali ishlamoqda!"
        
        self.is_running = True
        self.thread = threading.Thread(target=self.run_bot, daemon=False)
        self.thread.start()
        self.log_activity("🚀 Bot ishga tushdi!")
        return True, "Bot ishga tushdi!"
    
    def stop(self) -> tuple[bool, str]:
        """Stop the bot"""
        if not self.is_running:
            return False, "Bot ishlamayapti!"
        
        self.is_running = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join()
            self.thread = None
        
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
