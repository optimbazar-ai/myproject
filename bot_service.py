from instagrapi import Client
import time
import os
import json
from pathlib import Path
from gemini_service import generate_reply
from growth_bot import GrowthBot
import threading

class InstagramBot:
    def __init__(self):
        self.cl = None
        self.is_running = False
        self.is_logged_in = False
        self.replied_comments = set()
        self.replied_dms = set()
        self.activity_log = []
        self.thread = None
        self.growth_bot = None
        self.growth_enabled = False
        self.session_file = "instagram_session.json"
        self.replied_ids_file = "replied_ids.json"
        self._load_replied_ids()
        
    def _load_replied_ids(self):
        """Load previously replied IDs from file"""
        try:
            if Path(self.replied_ids_file).exists():
                with open(self.replied_ids_file, 'r') as f:
                    data = json.load(f)
                    self.replied_comments = set(str(x) for x in data.get('comments', []))
                    self.replied_dms = set(str(x) for x in data.get('dms', []))
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
            self.growth_bot = GrowthBot(self.cl)
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
            self.growth_bot = GrowthBot(self.cl)
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
                    comment_id = str(comment.pk)
                    if comment_id not in self.replied_comments and comment.user.pk != self.cl.user_id:
                        text = comment.text.strip()
                        if text:
                            language = os.getenv('LANGUAGE', 'uz')
                            reply = generate_reply(text, language)
                            self.cl.media_comment(media.id, reply, replied_to_comment_id=comment.pk)
                            self.log_activity(f"💬 Kommentga javob: @{comment.user.username} → {reply[:50]}...")
                            self.replied_comments.add(comment_id)
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
                
                for message in messages:
                    if message.user_id == self.cl.user_id:
                        continue
                    
                    msg_id = str(message.id)
                    if msg_id in self.replied_dms:
                        break
                    
                    if message.text:
                        language = os.getenv('LANGUAGE', 'uz')
                        reply = generate_reply(message.text, language)
                        self.cl.direct_answer(thread.id, reply)
                        self.log_activity(f"📩 DM javob: @{message.user_id} → {reply[:50]}...")
                        self.replied_dms.add(msg_id)
                        self._save_replied_ids()
                        time.sleep(2)
                        break
        except Exception as e:
            self.log_activity(f"⚠️ DM xatosi: {str(e)}")
    
    def handle_growth(self):
        """Handle growth bot activities"""
        if not self.growth_enabled or not self.growth_bot:
            return
        
        try:
            hashtags = os.getenv('TARGET_HASHTAGS', 'cafe,restoran,tadbirlar').split(',')
            
            for hashtag in hashtags:
                hashtag = hashtag.strip()
                if not hashtag:
                    continue
                
                if os.getenv('AUTO_LIKE_ENABLED', 'false').lower() == 'true':
                    count, msg = self.growth_bot.auto_like_by_hashtag(hashtag, max_likes=5)
                    if count > 0:
                        self.log_activity(f"👍 {msg}")
                    time.sleep(10)
                
                if os.getenv('AUTO_FOLLOW_ENABLED', 'false').lower() == 'true':
                    count, msg = self.growth_bot.auto_follow_by_hashtag(hashtag, max_follows=2)
                    if count > 0:
                        self.log_activity(f"👥 {msg}")
                    time.sleep(15)
                
                if os.getenv('AUTO_COMMENT_ENABLED', 'false').lower() == 'true':
                    count, msg = self.growth_bot.auto_comment_by_hashtag(hashtag, max_comments=1)
                    if count > 0:
                        self.log_activity(f"💬 {msg}")
                    time.sleep(20)
                
        except Exception as e:
            self.log_activity(f"⚠️ Growth bot xatosi: {str(e)}")
    
    def run_bot(self):
        """Main bot loop"""
        check_interval = int(os.getenv('CHECK_INTERVAL', '30'))
        
        while self.is_running:
            try:
                self.handle_comments()
                self.handle_dms()
                self.handle_growth()
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
    
    def toggle_growth(self, enabled: bool) -> tuple[bool, str]:
        """Enable/disable growth bot"""
        if not self.is_logged_in:
            return False, "Avval Instagram'ga kiring!"
        
        self.growth_enabled = enabled
        status = "yoqildi" if enabled else "o'chirildi"
        self.log_activity(f"🚀 Growth bot {status}!")
        return True, f"Growth bot {status}!"
    
    def get_status(self) -> dict:
        """Get bot status"""
        growth_stats = {}
        if self.growth_bot:
            growth_stats = self.growth_bot.get_stats()
        
        return {
            'is_logged_in': self.is_logged_in,
            'is_running': self.is_running,
            'growth_enabled': self.growth_enabled,
            'replied_comments': len(self.replied_comments),
            'replied_dms': len(self.replied_dms),
            'activity_log': self.activity_log[-20:],
            'growth_stats': growth_stats
        }

bot_instance = InstagramBot()
