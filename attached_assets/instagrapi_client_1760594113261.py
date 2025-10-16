# instagrapi_client.py
from instagrapi import Client
import time
from config import INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD, CHECK_INTERVAL
from gemini_service import generate_reply

class InstagramBot:
    def __init__(self):
        self.cl = Client()
        self.cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        print("✅ Instagram’ga muvaffaqiyatli ulandik!")

        self.replied_comments = set()
        self.replied_dms = set()

    def handle_comments(self):
        """Postlardagi kommentlarga javob yozish"""
        medias = self.cl.user_medias(self.cl.user_id, 5)
        for media in medias:
            comments = self.cl.media_comments(media.id)
            for comment in comments:
                if comment.pk not in self.replied_comments:
                    text = comment.text.lower().strip()
                    if text:
                        reply = generate_reply(text)
                        self.cl.comment_reply(media.id, comment.pk, reply)
                        print(f"💬 Kommentga javob yozildi: {reply}")
                        self.replied_comments.add(comment.pk)

    def handle_dms(self):
        """DM (xabarlar)ga javob yozish"""
        threads = self.cl.direct_threads()
        for thread in threads:
            messages = thread.messages
            if not messages:
                continue
            last_msg = messages[0]
            if last_msg.user_id != self.cl.user_id and last_msg.id not in self.replied_dms:
                reply = generate_reply(last_msg.text)
                self.cl.direct_answer(thread.id, reply)
                print(f"📩 DM javob yuborildi: {reply}")
                self.replied_dms.add(last_msg.id)

    def run(self):
        """Botni doimiy ishlatish"""
        while True:
            try:
                self.handle_comments()
                self.handle_dms()
            except Exception as e:
                print(f"⚠️ Xatolik: {e}")
            time.sleep(CHECK_INTERVAL)
