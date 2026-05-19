# 🔍 SNS 키워드 모니터링 봇 (무료 버전)
Twitter/X · Instagram → 텔레그램 알림 | GitHub Actions 기반 | 비용 $0

---

## 📐 전체 구조

```
GitHub Actions (30분마다 자동 실행)
        │
        ▼
    main.py
    ├── TwitterMonitor   → Twitter API v2 Free (월 500,000건)
    ├── InstagramMonitor → instaloader 해시태그 크롤링
    └── TelegramNotifier → 텔레그램 봇 메시지 발송
         │
         ▼
    📱 텔레그램 메시지
```

---

## 🚀 세팅 순서 (총 4단계)

### 1단계 — 텔레그램 봇 만들기 (5분)

1. 텔레그램에서 **@BotFather** 검색 → `/newbot`
2. 봇 이름 입력 (예: `MyKeywordBot`)
3. 발급된 **Bot Token** 복사 (예: `7123456789:AAF...`)
4. 본인 채팅방 ID 확인:
   - 봇에게 아무 메시지 전송
   - 브라우저에서 아래 URL 접속:
     ```
     https://api.telegram.org/bot{토큰}/getUpdates
     ```
   - 응답에서 `"id"` 값 복사 (예: `123456789`)

---

### 2단계 — Twitter API 키 발급 (선택, 10분)

> Twitter를 모니터링 안 해도 됩니다. INSTAGRAM만 써도 작동합니다.

1. https://developer.twitter.com → **Sign up** → 앱 생성
2. **Free 플랜** 선택 (무료, 신용카드 불필요)
3. 앱 설정 → **Keys and Tokens** → **Bearer Token** 복사

---

### 3단계 — GitHub 저장소 생성 및 코드 업로드

```bash
# 저장소 초기화
git init
git add .
git commit -m "init: SNS keyword monitor"

# GitHub에 저장소 생성 후 push
git remote add origin https://github.com/YOUR_USERNAME/sns-monitor.git
git push -u origin main
```

---

### 4단계 — GitHub Secrets 등록

GitHub 저장소 → **Settings → Secrets and variables → Actions → New repository secret**

| Secret 이름 | 값 | 필수 여부 |
|---|---|---|
| `KEYWORDS` | `스타트업,AI,투자` (쉼표 구분) | ✅ 필수 |
| `TELEGRAM_BOT_TOKEN` | `7123456789:AAF...` | ✅ 필수 |
| `TELEGRAM_CHAT_ID` | `123456789` | ✅ 필수 |
| `TWITTER_BEARER_TOKEN` | Twitter Bearer Token | 선택 |
| `INSTAGRAM_USERNAME` | 인스타 계정 아이디 | 선택 |
| `INSTAGRAM_PASSWORD` | 인스타 계정 비밀번호 | 선택 |

등록 후 **Actions 탭 → 워크플로우 선택 → Run workflow**로 즉시 테스트 가능합니다.

---

## 💬 알림 메시지 예시

```
🐦 [Twitter/X] 키워드 감지
🔑 키워드: 스타트업
✍️ 작성자: @example_user
🕐 시각: 05/19 14:30

국내 AI 스타트업이 시리즈B 투자 유치에 성공했습니다...

👉 원문 보기
```

---

## ⚠️ 무료 사용 시 제한 사항

| | 내용 |
|---|---|
| Twitter 무료 플랜 | 월 500,000 읽기, 검색 15분당 1회 |
| Instagram | 비공식 크롤링 → 과도한 호출 시 일시 차단 가능 |
| GitHub Actions | 무료 계정 2,000분/월 (30분 간격이면 약 1,440분/월 사용) |

---

## 🛠️ 자주 발생하는 문제

**Instagram 차단 시**
- 인스타그램이 크롤링을 감지하면 일시적으로 막을 수 있습니다
- 해결: 전용 계정 사용, 30분 간격 유지

**Twitter 검색 결과 없음**
- 키워드가 영어라면 `lang:ko` 필터 때문에 결과가 없을 수 있습니다
- `monitors/twitter.py`의 query에서 `lang:ko` 제거 후 테스트

**GitHub Actions 2,000분 초과**
- 실행 간격을 30분 → 1시간으로 늘리면 절반으로 줄어듭니다
- `.github/workflows/monitor.yml`에서 `*/30` → `0 * * * *`으로 변경
