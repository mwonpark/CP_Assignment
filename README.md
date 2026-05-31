# 🎮 비트 바이트 (Beat Byte)

> **BPM 기반 리듬 판정 알고리즘과 외부 클라우드 REST API가 결합한 하이브리드 아케이드 스네이크 게임**
> 
> 본 프로젝트는 클래식 아케이드 게임인 스네이크(Snake)의 규칙을 뒤집어, 음악의 비트 타이밍에 맞춰 방향을 전환해야 하는 **리듬 동기화 액션 퍼즐 게임**입니다. 생성형 AI(Gemini 1.5 Pro)와의 긴밀한 페어 프로그래밍(Pair Programming)을 통해 유기적인 MVC 아키처 설계, 실시간 외부 클라우드 서버 배포, 견고한 방어적 코딩을 달성했습니다.

---

## 🌟 주요 특징 및 기술적 차별점 (Key Features)

1. **프레임 독립형 리듬 싱크 무브먼트 (BPM Synchronization)**
   - 단순 FPS 프레임 기반 이동이 아닌, `time.time()` 절대 시간 연산을 통한 **BPM 매칭 알고리즘** 구현.
   - BGM의 비트 오차를 소수점 아래 세 자리까지 정밀하게 계산하여 `PERFECT`, `GOOD`, `MISS` 판정 부여.
   - 스테이지가 올라갈수록 BPM이 동적으로 빨라지며 판정 허용 범위(Window)가 좁아지는 유기적 난이도 조절 시스템.

2. **실시간 외부 클라우드 글로벌 리더보드 (REST API)**
   - 로컬 파일 저장을 넘어 외부 클라우드 플랫폼 **Render.com**에 파이썬 Flask 기반 중앙 웹 서버 배포 완료.
   - 게임 오버 시 클라이언트와 서버 간의 비동기 GET/POST REST API 통신을 통해 전 세계 플레이어의 실시간 상위 10등 순위판 정렬 및 동기화 렌더링.

3. **엔지니어링 기반의 방어적 코딩 (Robust Architecture)**
   - **에셋 폴백(Fallback) 시스템:** 이미지 및 사운드 리소스가 누락되거나 에러가 발생해도 게임이 크래시되지 않고 시스템 내장 기본 도형 렌더링으로 자동 대체 구동.
   - **네트워크 장애 방어:** 외부 서버 점검 또는 네트워크 단절 시 게임 멈춤(Freezing) 현상을 막기 위한 `3.0s Timeout` 설정 및 하이브리드 로컬 백업 시스템(`data/highscore.json`)으로의 자동 전환.
   - **자동 환경 인프라 구축:** 프로그램 구동 시 데이터 저장 폴더(`data/`)가 없으면 런타임에서 자동으로 감지하여 개설하는 자가 복구형 입출력 로직 반영.

---

## 🛠️ 기술 스택 (Tech Stack)

- **Language:** Python 3.11 ~ 3.13
- **Client GUI / Audio Core:** Pygame 2.6.0+
- **Database & Serialization:** JSON Persistent Data Architecture
- **Web API Server:** Flask 3.0.3+ (Deployed on Render Cloud)
- **Asset Generation Engine:** Pillow (PIL) 10.3.0+

---

## 📁 프로젝트 폴더 구조 (Directory Structure)

```text
CP_Assignment/                       # 프로젝트 루트 폴더 (Client)
│
├── data/                            # 로컬 데이터 영속성 폴더
│   └── highscore.json               # 오프라인 백업 및 로컬 최고 점수 저장 파일 (자동 생성)
│
├── assets/                          # 게임 멀티미디어 소스 폴더
│   ├── images/                      # 뱀 스킨, 아이템, 음식 네온 .png 타일 에셋 폴더
│   └── sounds/                      # 인게임 BGM(.mp3) 및 판정별 효과음(.wav) 폴더
│
├── backend_engine.py                # [Core] 게임 규칙, 박자 판정, REST API 클라이언트 엔진
├── main_ui.py                       # [View/Controller] Pygame 기반 GUI 렌더링 및 믹서 루프
├── generate_assets.py               # [Utility] Pillow 라이브러리 기반 30x30 임시 이미지 에셋 자동 생성기
├── requirements.txt                 # 프로젝트 통합 의존성 환경 명세서
└── README.md                        # 본 프로젝트 매뉴얼 파일

🚀 시작하기 및 실행 방법 (How to Run)
1. 저장소 클론 및 폴더 이동
Bash
git clone [https://github.com/Xerenia/CP_Assignment.git](https://github.com/Xerenia/CP_Assignment.git)
cd CP_Assignment
2. 필수 의존성 라이브러리 일괄 설치
Bash
pip install -r requirements.txt
3. 임시 네온 이미지 에셋 생성 스크립트 실행
외부 에셋 사이트를 이용하지 않고, 파이썬 그래픽 연산을 통해 assets/images/ 폴더 내에 규격에 맞는 30x30 임시 이미지 파일들을 즉석에서 자동 제작합니다.

Bash
python generate_assets.py
(주의: assets/sounds/ 폴더에 배경음악용 bgm.mp3 파일을 넣어두면 온전한 리듬 플레이가 가능합니다.)

4. 메인 게임 클라이언트 실행
Bash
python main_ui.py
🕹️ 게임 플레이 방법 및 판정 규칙 (Gameplay Rules)
이동 방식: 뱀은 BGM의 120 BPM(0.5초당 1비트) 박자에 맞춰 스스로 한 칸씩 전진합니다.

조작 및 판정: 정박 타이밍에 맞춰 방향키(↑, ↓, ←, →)를 누르면 박자 오차를 계산하여 판정을 내립니다.

🟢 PERFECT: 박자와 일치하게 누를 시 콤보 누적 및 대폭 스코어 상승, 스네이크 방향 전환 성공.

🟡 GOOD: 미세한 박자 오차 발생 시 스코어 상승, 콤보 리셋, 스네이크 방향 전환 성공.

🔴 MISS: 박자를 놓치거나 무리하게 연타할 시 라이프(LIVES) 1 차감, 콤보 리셋, 방향 전환 실패.

아이템 종류:

🍎 일반 음식 (Food): 몸길이 1 증가, 200점 획득. (5개 섭취 시 다음 스테이지로 진입하며 BPM 상승)

🧪 생명 물약 (Potion): 라이프 1 회복 (최대 5개 제한).

🪙 보너스 코인 (Coin): 보너스 점수 500점 즉시 획득.

게임 오버 및 등록: 라이프가 0이 되면 게임 오버 팝업이 뜨며, 키보드로 닉네임을 입력 후 엔터(Enter)를 누르면 클라우드 중앙 서버로 데이터가 전송되어 실시간 GLOBAL TOP 10 순위표가 출력됩니다. 리더보드 화면에서 R 키를 누르면 게임이 리셋되어 재시작합니다.

🤖 AI 협업 및 프로그래밍 로그 (AI Collaboration Log)
본 프로젝트는 무분별한 AI 소스코드 복사-붙여넣기를 지양하고, 시스템 설계자(안석)가 AI에게 명확한 객체지향 시스템 지침(System Instructions)을 바인딩한 뒤 단계별로 리팩토링 및 인프라 구축을 유도해 낸 'AI 페어 프로그래밍의 표준 모범 사례'입니다.

[핵심 프롬프트 아키텍처 흐름]
1단계 (모듈화 독립 설계): UI 드로잉 요소와 순수 데이터 물리 법칙을 완벽히 격리하는 백엔드 엔진 클래스 구조 유도.

2단계 (예외 처리 고도화): 런타임 테스트 중 발생한 변수 매개변수 충돌(AttributeError) 및 시간 오차 연산 로그를 AI에게 피드백하여 수정본 도출.

3단계 (클라우드 인프라 확장): 중앙 웹 서버 배포를 위해 Flask REST API 엔드포인트를 개설하고, urllib.request 타임아웃 설정을 통한 네트워크 프리징 차단 방어벽 설계 유도.

4단계 (에셋 자가 복구): Pillow 내장 라이브러리를 역이용해 디자이너 에셋 수집 전 런타임에서 임시 도트 에셋 파일들을 스스로 생성해 내는 자동화 스크립트 기능 추가.

👥 팀원 및 역할 (Team Members)
메인 아키텍트 & 개발 총괄 (Back-end / Cloud Infrastructure): 박안석

프론트엔드 GUI 및 이벤트 인터럽트 제어 (Front-end): 박명원, 서민우

품질 보증 및 시스템 구현 명세서 작성 (QA / Documentation): 이우성, 김동우
