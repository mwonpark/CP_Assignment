# 🎮 비트 바이트 (Beat Byte) 
> **AI 협업 기반 하이브리드 리듬 스네이크 게임**

## 1. 프로젝트 개요
- **교과목명:** Python 프로그래밍 팀 프로젝트
- **개발 기간:** 2026.05.28 ~ 2026.06.04 (1주일 단기 스프린트)
- **팀원 구성:** - 메인 개발(Back-end): 박안석
  - 서브 개발(Front-end/UI): 박명원, 서민우
  - QA 및 문서 정리: 이우성, 김동우

## 2. 게임 특징 및 독자적 변형 요소
- **리듬과 아케이드의 결합:** 클래식 스네이크 문법을 뒤집어, BGM의 BPM(박자) 타이밍에 맞춰 방향키를 입력해야만 정상 이동 및 음식 섭취가 가능한 하이브리드 액션 퍼즐.
- **실시간 글로벌 리더보드:** 로컬 파일 저장에 그치지 않고, 외부 클라우드 파이썬 서버(Render)와 REST API 통신을 수행하여 전 세계 플레이어의 상위 10등 순위를 실시간 동기화.
- **동적 난이도 스케일링:** 스테이지가 올라갈수록 BPM이 빨라지며 판정 허용 오차 범위가 좁아지는 하드코어 모드 탑재.

## 3. 기술 스택 및 인프라 구조
- **Language:** Python 3.10+
- **Client UI:** Pygame
- **Server:** Flask (Deployed on Render)
- **Database:** JSON-based persistent architecture

## 4. 실행 방법 (How to Run)
```bash
# 1. 저장소 클론
git clone [https://github.com/your-username/beat-byte.git](https://github.com/your-username/beat-byte.git)
cd beat-byte

# 2. 필수 패키지 설치
pip install -r requirements.txt

# 3. 게임 실행
python main_ui.py
