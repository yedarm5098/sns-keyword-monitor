"""
Twitter/X 키워드 모니터링
- Twitter API v2 Free tier (Bearer Token)
- 무료 한도: 월 500,000건 읽기, 검색 15분당 1회
- 한 번에 최대 10건 수집
"""

import logging
import tweepy
from datetime import datetime, timezone, timedelta
from typing   import Optional
from monitors import Post

logger = logging.getLogger(__name__)


class TwitterMonitor:
    def __init__(self, bearer_token: str):
        self.client = tweepy.Client(
            bearer_token=bearer_token,
            wait_on_rate_limit=True,
        )

    def search(self, keyword: str, since: Optional[datetime] = None,
               max_results: int = 10) -> list[Post]:
        """
        keyword 포함 한국어 트윗 검색.
        since: 이 시각 이후 게시물만 반환 (None이면 30분 전부터)
        """
        if since is None:
            since = datetime.now(timezone.utc) - timedelta(minutes=30)

        # 리트윗·답글 제외, 한국어 우선
        query = f'"{keyword}" -is:retweet -is:reply lang:ko'

        try:
            resp = self.client.search_recent_tweets(
                query=query,
                start_time=since,
                max_results=max(10, min(max_results, 100)),
                tweet_fields=["created_at", "author_id", "text"],
                expansions=["author_id"],
                user_fields=["username"],
            )
        except tweepy.TweepyException as e:
            logger.error(f"[Twitter] API 오류: {e}")
            return []

        if not resp.data:
            return []

        users = {u.id: u.username for u in (resp.includes.get("users") or [])}
        posts = []
        for tweet in resp.data:
            username = users.get(tweet.author_id, "unknown")
            posts.append(Post(
                platform="Twitter/X",
                author=f"@{username}",
                text=tweet.text,
                url=f"https://x.com/i/web/status/{tweet.id}",
                keyword=keyword,
                created_at=tweet.created_at,
            ))
        return posts
