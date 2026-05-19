"""
SNS 키워드 모니터링 봇
Twitter/X + Instagram → 텔레그램 알림
GitHub Actions에서 30분마다 실행
"""

import os
import logging
from monitors.twitter   import TwitterMonitor
from monitors.instagram import InstagramMonitor
from notifier.telegram  import TelegramNotifier
from storage.state      import StateManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main():
    keywords = [k.strip() for k in os.environ["KEYWORDS"].split(",") if k.strip()]
    logger.info(f"키워드 {len(keywords)}개: {keywords}")

    state    = StateManager(cache_dir=".cache")
    notifier = TelegramNotifier(
        bot_token=os.environ["TELEGRAM_BOT_TOKEN"],
        chat_id=os.environ["TELEGRAM_CHAT_ID"],
    )
    total_sent = 0

    # ── Twitter/X ──────────────────────────────────────────────
    twitter_token = os.environ.get("TWITTER_BEARER_TOKEN", "")
    if twitter_token:
        try:
            twitter   = TwitterMonitor(bearer_token=twitter_token)
            last_tw   = state.get_last_run("twitter")
            tw_posts  = []

            for kw in keywords:
                posts = twitter.search(kw, since=last_tw)
                logger.info(f"[Twitter] '{kw}' → {len(posts)}건")
                tw_posts.extend(posts)

            for post in tw_posts:
                if notifier.send(post):
                    total_sent += 1

            state.update_last_run("twitter")
        except Exception as e:
            logger.error(f"[Twitter] 오류: {e}")
    else:
        logger.warning("[Twitter] TWITTER_BEARER_TOKEN 없음 → 건너뜀")

    # ── Instagram ──────────────────────────────────────────────
    ig_user = os.environ.get("INSTAGRAM_USERNAME", "")
    ig_pass = os.environ.get("INSTAGRAM_PASSWORD", "")
    if ig_user and ig_pass:
        try:
            instagram = InstagramMonitor(
                username=ig_user,
                password=ig_pass,
                session_dir=".cache",
            )
            last_ig  = state.get_last_run("instagram")
            ig_posts = []

            for kw in keywords:
                tag   = kw.lstrip("#")
                posts = instagram.search_hashtag(tag, since=last_ig)
                logger.info(f"[Instagram] '#{tag}' → {len(posts)}건")
                ig_posts.extend(posts)

            for post in ig_posts:
                if notifier.send(post):
                    total_sent += 1

            state.update_last_run("instagram")
        except Exception as e:
            logger.error(f"[Instagram] 오류: {e}")
    else:
        logger.warning("[Instagram] 계정 정보 없음 → 건너뜀")

    logger.info(f"✅ 완료 — 텔레그램 발송 {total_sent}건")


if __name__ == "__main__":
    main()
