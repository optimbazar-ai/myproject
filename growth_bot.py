import time
import random
import os
from gemini_service import generate_reply
from pathlib import Path
import json


class GrowthBot:
    """Instagram Growth Bot - Auto like, follow, comment"""
    
    def __init__(self, cl):
        self.cl = cl
        self.growth_stats_file = "growth_stats.json"
        self.stats = self._load_stats()
        
    def _load_stats(self) -> dict:
        """Load growth statistics"""
        try:
            if Path(self.growth_stats_file).exists():
                with open(self.growth_stats_file, 'r') as f:
                    return json.load(f)
            return {
                'likes_today': 0,
                'follows_today': 0,
                'comments_today': 0,
                'last_reset': time.strftime("%Y-%m-%d")
            }
        except:
            return {
                'likes_today': 0,
                'follows_today': 0,
                'comments_today': 0,
                'last_reset': time.strftime("%Y-%m-%d")
            }
    
    def _save_stats(self):
        """Save growth statistics"""
        try:
            with open(self.growth_stats_file, 'w') as f:
                json.dump(self.stats, f)
        except Exception as e:
            print(f"Statistika saqlash xatosi: {e}")
    
    def _reset_daily_stats(self):
        """Reset stats if new day"""
        today = time.strftime("%Y-%m-%d")
        if self.stats.get('last_reset') != today:
            self.stats = {
                'likes_today': 0,
                'follows_today': 0,
                'comments_today': 0,
                'last_reset': today
            }
            self._save_stats()
    
    def _random_delay(self, min_sec: int = 2, max_sec: int = 5):
        """Random delay to look human"""
        time.sleep(random.uniform(min_sec, max_sec))
    
    def auto_like_by_hashtag(self, hashtag: str, max_likes: int = 10) -> tuple[int, str]:
        """Auto-like posts by hashtag"""
        try:
            self._reset_daily_stats()
            
            like_limit = int(os.getenv('DAILY_LIKE_LIMIT', '100'))
            if self.stats['likes_today'] >= like_limit:
                return 0, f"Kunlik like limiti ({like_limit}) tugadi"
            
            likes_done = 0
            medias = self.cl.hashtag_medias_recent(hashtag, amount=max_likes)
            
            for media in medias:
                if self.stats['likes_today'] >= like_limit:
                    break
                
                if likes_done >= max_likes:
                    break
                
                try:
                    if not media.has_liked:
                        self.cl.media_like(media.id)
                        likes_done += 1
                        self.stats['likes_today'] += 1
                        self._save_stats()
                        self._random_delay(2, 5)
                except:
                    continue
            
            return likes_done, f"✅ {likes_done} ta like qo'yildi #{hashtag}"
            
        except Exception as e:
            return 0, f"❌ Like xatosi: {str(e)[:50]}"
    
    def auto_follow_by_hashtag(self, hashtag: str, max_follows: int = 5) -> tuple[int, str]:
        """Auto-follow users from hashtag"""
        try:
            self._reset_daily_stats()
            
            follow_limit = int(os.getenv('DAILY_FOLLOW_LIMIT', '40'))
            if self.stats['follows_today'] >= follow_limit:
                return 0, f"Kunlik follow limiti ({follow_limit}) tugadi"
            
            follows_done = 0
            medias = self.cl.hashtag_medias_recent(hashtag, amount=max_follows * 2)
            
            for media in medias:
                if self.stats['follows_today'] >= follow_limit:
                    break
                
                if follows_done >= max_follows:
                    break
                
                try:
                    user = self.cl.user_info(media.user.pk)
                    if not user.is_private and media.user.pk != self.cl.user_id:
                        friendship_status = self.cl.user_friendship_v1(media.user.pk)
                        if not friendship_status.following:
                            self.cl.user_follow(media.user.pk)
                            follows_done += 1
                            self.stats['follows_today'] += 1
                            self._save_stats()
                            self._random_delay(3, 6)
                except:
                    continue
            
            return follows_done, f"✅ {follows_done} ta follow qilindi #{hashtag}"
            
        except Exception as e:
            return 0, f"❌ Follow xatosi: {str(e)[:50]}"
    
    def auto_comment_by_hashtag(self, hashtag: str, max_comments: int = 3) -> tuple[int, str]:
        """Auto-comment with AI on posts"""
        try:
            self._reset_daily_stats()
            
            comment_limit = int(os.getenv('DAILY_COMMENT_LIMIT', '10'))
            if self.stats['comments_today'] >= comment_limit:
                return 0, f"Kunlik comment limiti ({comment_limit}) tugadi"
            
            comments_done = 0
            medias = self.cl.hashtag_medias_recent(hashtag, amount=max_comments * 2)
            
            for media in medias:
                if self.stats['comments_today'] >= comment_limit:
                    break
                
                if comments_done >= max_comments:
                    break
                
                try:
                    if media.user.pk != self.cl.user_id:
                        caption = media.caption_text or "Ajoyib post"
                        comment_text = self._generate_smart_comment(caption)
                        
                        self.cl.media_comment(media.id, comment_text)
                        comments_done += 1
                        self.stats['comments_today'] += 1
                        self._save_stats()
                        self._random_delay(5, 10)
                except:
                    continue
            
            return comments_done, f"✅ {comments_done} ta comment yozildi #{hashtag}"
            
        except Exception as e:
            return 0, f"❌ Comment xatosi: {str(e)[:50]}"
    
    def _generate_smart_comment(self, post_caption: str) -> str:
        """Generate smart comment using AI"""
        try:
            prompt = f"Instagram post matni: '{post_caption[:100]}'\n\nBu postga qisqa, do'stona komment yozing (max 50 so'z, emoji bilan)"
            comment = generate_reply(prompt, "uz")
            if len(comment) > 150:
                comment = comment[:150]
            return comment
        except:
            comments = [
                "Ajoyib! 👏",
                "Zo'r ekan! 👍",
                "Juda yoqdi! ❤️",
                "Davom eting! 💪",
                "Mukammal! ✨"
            ]
            return random.choice(comments)
    
    def get_stats(self) -> dict:
        """Get growth statistics"""
        self._reset_daily_stats()
        return {
            'likes_today': self.stats['likes_today'],
            'follows_today': self.stats['follows_today'],
            'comments_today': self.stats['comments_today'],
            'like_limit': int(os.getenv('DAILY_LIKE_LIMIT', '100')),
            'follow_limit': int(os.getenv('DAILY_FOLLOW_LIMIT', '40')),
            'comment_limit': int(os.getenv('DAILY_COMMENT_LIMIT', '10'))
        }
