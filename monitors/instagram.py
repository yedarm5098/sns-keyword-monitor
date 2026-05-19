"""
Instagram 해시태그 모니터링
- instaloader 라이브러리 (비공식 방식)
- 세션 파일을 .cache/ 에 보관해 반복 로그인 최소화
- 과도한 호출 방지: 키워드당 최대 10건, 30분 간격 권장
"""

import os
import logging
import instaloader
from datetime import datetime, timezone, timedelta
from typing   import Optional
from monitors import Post

logger = logging.getLogger(__name__)


class InstagramMonitor:
    def __init__(self, username: str, password: str, session_dir: str = ".cache"):
        os.makedirs(session_dir, exist_ok=True)
        self.session_file = os.path.join(session_dir, f"ig_{username}.session")

        self.L = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            quiet=True,
        )
        self._login(username, password)

    def _login(self, username: str, password: str):
        try:
            self.L.load_session_from_file(username, self.session_file)
            logger.info("[Instagram] 세션 파일 로드 완료")
        except (FileNotFoundError, instaloader.exceptions.BadCredentialsException):
            logger.info("[Instagram] 새로 로그인 중...")
            self.L.login(username, password)
            self.L.save_session_to_file(self.session_file)
            logger.info("[Instagram] 로그인 및 세션 저장 완료")

    def search_hashtag(self, hashtag: str, since: Optional[datetime] = None,
                       max_posts: int = 10) -> list[Post]:
        """
        hashtag 최신 게시물 수집 (# 없이 전달)
        since: 이 시각 이후 게시물만 반환 (None이면 30분 전부터)
        """
        if since is None:
            since = datetime.now(timezone.utc) - timedelta(minutes=30)
        if since.tzinfo is None:
            since = since.replace(tzinfo=timezone.utc)

        try:
            tag = instaloader.Hashtag.from_name(self.L.context, hashtag)
        except Exception as e:
            logger.error(f"[Instagram] 해시태그 '{hashtag}' 조회 실패: {e}")
            return []

        posts = []
        try:
            for post in tag.get_posts():
                created = post.date_utc.replace(tzinfo=timezone.utc)
                if created < since:
                    break
                if len(posts) >= max_posts:
                    break

                caption = (post.caption or "").replace("\n", " ")[:200]
                posts.append(Post(
                    platform="Instagram",
                    author=f"@{post.owner_username}",
                    text=caption,
                    url=f"https://www.instagram.com/p/{post.shortcode}/",
                    keyword=f"#{hashtag}",
                    created_at=created,
                ))
        except Exception as e:
            logger.error(f"[Instagram] 게시물 수집 중 오류: {e}")

        return posts
