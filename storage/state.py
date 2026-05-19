"""
마지막 실행 시각 관리 (로컬 JSON 파일)
GitHub Actions cache를 통해 실행 간 상태 유지
"""

import os
import json
import logging
from datetime import datetime, timezone, timedelta
from typing   import Optional

logger = logging.getLogger(__name__)


class StateManager:
    def __init__(self, cache_dir: str = ".cache"):
        os.makedirs(cache_dir, exist_ok=True)
        self.path   = os.path.join(cache_dir, "state.json")
        self._state = self._load()

    def _load(self) -> dict:
        try:
            with open(self.path, "r") as f:
                raw = json.load(f)
            # 문자열 → datetime (UTC aware) 변환
            return {k: datetime.fromisoformat(v) for k, v in raw.items()}
        except FileNotFoundError:
            logger.info("[State] 상태 파일 없음 → 초기화")
            return {}
        except Exception as e:
            logger.warning(f"[State] 로드 실패: {e} → 초기화")
            return {}

    def _save(self):
        with open(self.path, "w") as f:
            json.dump({k: v.isoformat() for k, v in self._state.items()}, f, indent=2)

    def get_last_run(self, platform: str) -> datetime:
        """마지막 실행 시각 반환 (없으면 30분 전)"""
        default = datetime.now(timezone.utc) - timedelta(minutes=30)
        return self._state.get(platform, default)

    def update_last_run(self, platform: str):
        """현재 시각으로 갱신 후 저장"""
        self._state[platform] = datetime.now(timezone.utc)
        self._save()
        logger.info(f"[State] '{platform}' 실행 시각 저장 완료")
