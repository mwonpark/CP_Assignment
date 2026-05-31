# 🎮 비트 바이트 (Beat Byte)

> **BPM 기반 리듬 판정 알고리즘과 외부 클라우드 REST API가 결합한 하이브리드 아케이드 스네이크 게임**
> 
> 본 프로젝트는 클래식 아케이드 게임인 스네이크(Snake)의 규칙을 뒤집어, 음악의 비트 타이밍에 맞춰 방향을 전환해야 하는 **리듬 동기화 액션 퍼즐 게임**입니다. 생성형 AI(Gemini 1.5 Pro)와의 긴밀한 페어 프로그래밍(Pair Programming)을 통해 유기적인 MVC 아키처 설계, 실시간 외부 클라우드 서버 배포, 견고한 방어적 코딩을 달성했습니다.

---

## 📌 목차 (Table of Contents)
1. [🌟 주요 특징 및 기술적 차별점](#-주요-특징-및-기술적-차별점-key-features)
2. [🛠️ 기술 스택](#️-기술-스택-tech-stack)
3. [📁 프로젝트 폴더 구조](#-프로젝트-폴더-구조-directory-structure)
4. [🚀 시작하기 및 실행 방법](#-시작하기-및-실행-방법-how-to-run)
5. [🕹️ 게임 플레이 및 판정 규칙](#-게임-플레이-및-판정-규칙-gameplay-rules)
6. [📑 [기술 보고서] 시스템 아키텍처 명세](#-기술-보고서-시스템-아키텍처-명세)
7. [💻 [개발자 가이드] 핵심 소스코드 해설](#-개발자-가이드-핵심-소스코드-해설)
8. [🤖 AI 협업 및 로그](#-ai-협업-및-프로그래밍-로그-ai-collaboration-log)
9. [👥 팀원 및 역할](#-팀원-및-역할-team-members)

---

## 🌟 주요 특징 및 기술적 차별점 (Key Features)

- **프레임 독립형 리듬 싱크 무브먼트 (BPM Synchronization)**
  - 단순 FPS 프레임 기반 이동이 아닌, `time.time()` 절대 시간 연산을 통한 **BPM 매칭 알고리즘** 구현.
  - BGM의 비트 오차를 소수점 아래 세 자리까지 정밀하게 계산하여 `PERFECT`, `GOOD`, `MISS` 판정 부여.
  - 스테이지가 올라갈수록 BPM이 동적으로 빨라지며 판정 허용 범위(Window)가 좁아지는 유기적 난이도 조절 시스템.

- **실시간 외부 클라우드 글로벌 리더보드 (REST API)**
  - 로컬 파일 저장을 넘어 외부 클라우드 플랫폼 **Render.com**에 파이썬 Flask 기반 중앙 웹 서버 배포 완료.
  - 게임 오버 시 클라이언트와 서버 간의 비동기 GET/POST REST API 통신을 통해 전 세계 플레이어의 실시간 상위 10등 순위판 정렬 및 동기화 렌더링.

- **엔지니어링 기반의 방어적 코딩 (Robust Architecture)**
  - **에셋 폴백(Fallback) 시스템:** 이미지 및 사운드 리소스가 누락되거나 에러가 발생해도 게임이 크래시되지 않고 시스템 내장 기본 도형 렌더링으로 자동 대체 구동.
  - **네트워크 장애 방어:** 외부 서버 점검 또는 네트워크 단절 시 게임 멈춤(Freezing) 현상을 막기 위한 `3.0s Timeout` 설정 및 하이브리드 로컬 백업 시스템(`data/highscore.json`)으로의 자동 전환.
  - **자동 환경 인프라 구축:** 프로그램 구동 시 데이터 저장 폴더 (`data/`)가 없으면 런타임에서 자동으로 감지하여 개설하는 자가 복구형 입출력 로직 반영.

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
```

---

## 🚀 시작하기 및 실행 방법 (How to Run)

### 1. 저장소 클론 및 폴더 이동
```bash
git clone [https://github.com/Xerenia/CP_Assignment.git](https://github.com/Xerenia/CP_Assignment.git)
cd CP_Assignment
```

### 2. 필수 의존성 라이브러리 일괄 설치
```bash
pip install -r requirements.txt
```

### 3. 임시 네온 이미지 에셋 생성 스크립트 실행
외부 에셋 사이트를 이용하지 않고, 파이썬 그래픽 연산을 통해 `assets/images/` 폴더 내에 규격에 맞는 30x30 임시 이미지 파일들을 즉석에서 자동 제작합니다.
```bash
python generate_assets.py
```
*(주의: `assets/sounds/` 폴더에 배경음악용 `bgm.mp3` 파일을 넣어두면 온전한 리듬 플레이가 가능합니다.)*

### 4. 메인 게임 클라이언트 실행
```bash
python main_ui.py
```

---

## 🕹️ 게임 플레이 방법 및 판정 규칙 (Gameplay Rules)

- **이동 방식:** 뱀은 BGM의 **120 BPM(0.5초당 1비트)** 박자에 맞춰 스스로 한 칸씩 전진합니다.
- **조작 및 판정:** 정박 타이밍에 맞춰 방향키 (`↑`, `↓`, `←`, `→`)를 누르면 박자 오차를 계산하여 판정을 내립니다.
  - 🟢 **PERFECT:** 박자와 일치하게 누를 시 콤보 누적 및 스코어 대폭 상승, 방향 전환 성공.
  - 🟡 **GOOD:** 미세한 박자 오차 발생 시 스코어 상승, 콤보 리셋, 방향 전환 성공.
  - 🔴 **MISS:** 박자를 놓치거나 무리하게 연타할 시 라이프(`LIVES`) 1 차감, 콤보 리셋, 방향 전환 실패.

### 🎁 아이템 종류
- 🍎 **일반 음식 (Food):** 몸길이 1 증가, 200점 획득. (5개 섭취 시 다음 스테이지로 진입하며 BPM 상승)
- 🧪 **생명 물약 (Potion):** 라이프 1 회복 (최대 5개 제한).
- 🪙 **보너스 코인 (Coin):** 보너스 점수 500점 즉시 획득.

> **게임 오버 시:** 라이프가 0이 되면 게임 오버 팝업이 뜨며, 키보드로 닉네임을 입력 후 엔터(Enter)를 누르면 클라우드 중앙 서버로 데이터가 전송되어 실시간 **GLOBAL TOP 10** 순위표가 출력됩니다. 리더보드 화면에서 `R` 키를 누르면 게임이 리셋되어 재시작합니다.

---

## 📑 [기술 보고서] 시스템 아키텍처 명세

### 1. 시스템 아키텍처 흐름
소프트웨어 공학의 **MVC(Model-View-Controller) 디자인 패턴**을 엄격히 준수하여 독립적인 모듈화를 달성하였으며, 로컬 데이터 persistence 층과 외부 클라우드 플랫폼(Render) 기반의 REST API 서버를 동기화하여 전 세계 유저와 실시간 랭킹을 공유하는 분산 시스템을 구축했습니다.

```text
[프론트엔드: main_ui.py] ──(방향/입력시간 던짐)──> [백엔드: backend_engine.py]
         │                                                    │
   (화면/음향 재생)                                      (로컬 데이터 백업)
         │                                                    │
         ▼                                                    ▼
  [Pygame GUI 화면]                                   [data/highscore.json]
         │
         └───(REST API 통신: GET/POST)───> [중앙 서버: server.py (Render 클라우드)]
                                                      │
                                             [global_leaderboard.json]
```

### 2. 핵심 파일별 세부 명세
- **`backend_engine.py` (Model):** 게임 규칙 알고리즘 제어 및 박자 판정, 데이터 직렬화(Serialization)를 전담합니다. 열거형(`Enum`)을 통한 상태 무결성을 보장하며 `deque` 자료구조로 뱀 몸통 좌표 관리 및 충돌을 감지합니다.
- **`main_ui.py` (View/Controller):** 하드웨어 이벤트 입출력 가로채기(Interrupt), 멀티미디어 렌더링을 제어합니다. 상태 머신 패턴을 도입하여 인게임, 닉네임 입력 팝업, 글로벌 리더보드 간의 화면 전환을 매끄럽게 연출합니다.
- **`server.py` (Cloud API):** 중앙 집중형 데이터 취합 및 정렬을 담당하는 Flask REST API 서버입니다. 외부 IP 개방(`0.0.0.0`) 및 리눅스 배포용 고성능 게이트웨이(`gunicorn`) 기반으로 가동 중입니다.

---

## 💻 [개발자 가이드] 핵심 소스코드 해설

### 1. 프레임 독립형 박자 판정 공식
- **소스 위치:** `backend_engine.py` ➔ `RhythmManager.evaluate_input()`

```python
beat_count = round(input_time / self.sec_per_beat)
if beat_count == self.last_evaluated_beat:
    return Judgment.IGNORED
self.last_evaluated_beat = beat_count
nearest_beat_time = beat_count * self.sec_per_beat
time_diff = abs(input_time - nearest_beat_time)

if time_diff <= self.perfect_window: return Judgment.PERFECT
elif time_diff <= self.good_window: return Judgment.GOOD
else: return Judgment.MISS
```
사용자가 키를 입력한 시점(`input_time`)을 초당 비트 소요 시간(`sec_per_beat`)으로 나누어 반올림(`round`)함으로써 정수형 박자 레이블을 땁니다. 그 후 가장 가까운 정박 시간과의 절대 오차(`time_diff`)를 비교 판정합니다. 중복 입력을 막기 위한 `last_evaluated_beat` 추적 메커니즘이 포함되어 연타 핵(Cheat)을 방어합니다.

### 2. 실행 환경 독립을 위한 자동 추적 경로 매핑
- **소스 위치:** `main_ui.py` ➔ `RhythmSnakeUI._load_assets()`

```python
base_asset_dir = Path(__file__).parent / "assets"
img_dir = base_asset_dir / "images"
sound_dir = base_asset_dir / "sounds"
```
하드코딩된 절대 경로 방식은 개발자 개인 PC 환경에서만 작동하므로 배포 시 타 사용자 컴퓨터에서 크래시가 납니다. 이를 극복하기 위해 파이썬 시스템 예약 변수인 `__file__`을 호출하여 현재 실행 중인 파일의 실제 디렉토리를 실시간 추적하고, 그 기준으로 하위 `assets/` 경로를 조준하는 유연한 경로 바인딩 기법을 적용했습니다.

---

## 🤖 AI 협업 및 프로그래밍 로그 (AI Collaboration Log)

본 프로젝트는 무분별한 AI 소스코드 복사-붙여넣기를 지양하고, 시스템 설계자가 AI에게 명확한 객체지향 시스템 지침(System Instructions)을 바인딩한 뒤 단계별로 리팩토링 및 인프라 구축을 유도해 낸 **'AI 페어 프로그래밍의 표준 모범 사례'**입니다.

1. **1단계 (모듈화 독립 설계):** UI 드로잉 요소와 순수 데이터 물리 법칙을 완벽히 격리하는 백엔드 엔진 클래스 구조 유도.
2. **2단계 (예외 처리 고도화):** 런타임 테스트 중 발생한 변수 매개변수 충돌(`AttributeError`) 및 시간 오차 연산 로그를 AI에게 피드백하여 수정본 도출.
3. **3단계 (클라우드 인프라 확장):** 중앙 웹 서버 배포를 위해 Flask REST API 엔드포인트를 개설하고, `urllib.request` 타임아웃 설정을 통한 네트워크 프리징 차단 방어벽 설계 유도.
4. **4단계 (에셋 자가 복구):** `Pillow` 내장 라이브러리를 역이용해 디자이너 에셋 수집 전 런타임에서 임시 도트 에셋 파일들을 스스로 생성해 내는 자동화 스크립트 기능 추가.

---

## 👥 팀원 및 역할 (Team Members)

- **메인 아키텍트 & 개발 총괄 (Back-end / Cloud Infrastructure):** 박안석
- **프론트엔드 GUI 및 이벤트 인터럽트 제어 (Front-end):** 박명원, 서민우
- **품질 보증 및 시스템 구현 명세서 작성 (QA / Documentation):** 이우성, 김동우
