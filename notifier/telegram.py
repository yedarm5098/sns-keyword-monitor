"""
텔레그램 봇 알림 발송
- 토큰 만료 없음, 무료, 설정 5분
- Bot API: https://core.telegram.org/bots/api#sendmessage
"""

import logging
import requests
from monitors import Post

logger = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str):
        self.url     = TELEGRAM_API.format(token=bot_token)
        self.chat_id = chat_id

    def send(self, post: Post) -> bool:
        """
        텔레그램 메시지 발송. 성공 시 True 반환.
        MarkdownV2 형식 사용 (굵기, 링크 지원)
        """
        text = self._build_message(post)
        try:
            resp = requests.post(
                self.url,
                json={
                    "chat_id":    self.chat_id,
                    "text":       text,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": False,
                },
                timeout=10,
            )
            data = resp.json()
            if data.get("ok"):
                logger.info(f"[Telegram] 발송 완료: {post.platform} / {post.keyword}")
                return True
            else:
                logger.error(f"[Telegram] 발송 실패: {data.get('description')}")
                return False
        except requests.RequestException as e:
            logger.error(f"[Telegram] 요청 오류: {e}")
            return False

    @staticmethod
    def _build_message(post: Post) -> str:
        platform_emoji = {"Twitter/X": "🐦", "Instagram": "📸"}.get(post.platform, "🔔")
        time_str = post.created_at.strftime("%m/%d %H:%M") if post.created_at else ""

        # 본문 미리보기 (100자)
        preview = post.text[:100] + ("..." if len(post.text) > 100 else "")

        return (
            f"{platform_emoji} <b>[{post.platform}] 키워드 감지</b>\n"
            f"🔑 키워드: <code>{post.keyword}</code>\n"
            f"✍️ 작성자: {post.author}\n"
            f"🕐 시각: {time_str}\n"
            f"\n"
            f"{preview}\n"
            f"\n"
            f'<a href="{post.url}">👉 원문 보기</a>'
        )
