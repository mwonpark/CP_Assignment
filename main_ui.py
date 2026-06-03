import sys
import os
import pygame
import time
from enum import Enum, auto
from pathlib import Path
from typing import Optional, Dict, Any, List

from backend_engine import GameEngine, Direction, Judgment, GameState, ItemType

# ==========================================
# 1. 상수 및 설정 (Constants & Config)
# ==========================================
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 720  
GRID_SIZE = 30  
FPS = 60

COLORS = {
    "BACKGROUND": (25, 25, 35),
    "GRID_LINE": (40, 40, 50),
    "TEXT_WHITE": (240, 240, 240),
    "TEXT_GRAY": (150, 150, 150),
    "PERFECT": (0, 255, 0),
    "GOOD": (255, 255, 0),
    "MISS": (255, 0, 0),
    "POPUP_BG": (40, 40, 50),
    "TABLE_HEADER": (60, 60, 80),
    "TABLE_ROW": (45, 45, 55),
    "FOOD_COIN": (255, 215, 0),    
    "FOOD_NORMAL": (255, 100, 100),  
    "FOOD_POTION": (100, 100, 255),  
    "SNAKE_HEAD": (0, 255, 150),
    "SNAKE_BODY": (0, 200, 100),
}

class UIScene(Enum):
    READY = auto()            
    COUNTDOWN = auto()        
    PLAYING = auto()          
    GAME_OVER_POPUP = auto()  
    LEADERBOARD = auto()      
    DIFFICULTY = auto()

# ==========================================
# 3. 메인 UI 클래스
# ==========================================
class RhythmSnakeUI:
    def __init__(self) -> None:
        pygame.init()
        
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.set_num_channels(16)
        except Exception as e:
            print(f"[경고] 오디오 초기화 실패: {e}")

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("비트 바이트 (Rhythm Snake) - Official Client")
        self.clock = pygame.time.Clock()

        try:
            self.font_small = pygame.font.SysFont("malgungothic", 20, bold=True)
            self.font_main = pygame.font.SysFont("malgungothic", 24, bold=True)
            self.font_large = pygame.font.SysFont("malgungothic", 48, bold=True)
            self.font_judgment = pygame.font.SysFont("malgungothic", 64, bold=True)
            # 난이도 카드 제목(EASY/NORMAL/HARD)은 큰 폰트보다 살짝 작게 사용
            # (NORMAL 글씨가 카드 테두리에 닿지 않게 여유 확보)
            self.font_card_title = pygame.font.SysFont("malgungothic", 42, bold=True)
        except Exception:
            self.font_small = pygame.font.Font(None, 24)
            self.font_main = pygame.font.Font(None, 30)
            self.font_large = pygame.font.Font(None, 60)
            self.font_judgment = pygame.font.Font(None, 80)
            self.font_card_title = pygame.font.Font(None, 54)

        self.engine = GameEngine(grid_width=20, grid_height=20, base_bpm=120.0)

        self.images: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, Optional[pygame.mixer.Sound]] = {}
        self.background_surface: Optional[pygame.Surface] = None
        self._load_assets()

        self.current_scene: UIScene = UIScene.READY
        self.start_ticks: int = 0
        self.countdown_start_ticks: int = 0
        
        self.judgment_text: str = ""
        self.judgment_color: tuple[int, int, int] = COLORS["TEXT_WHITE"]
        self.judgment_timer: float = 0.0
        
        self.player_name_input: str = ""
        self.leaderboard_data: List[Dict[str, Any]] = []
        # READY(시작) 화면에서 보여줄 버튼들의 위치는 매 프레임 계산해서 그립니다.
        # (나중에 기능을 붙일 때도 이 Rect들을 그대로 재사용할 수 있게 저장만 해둡니다.)
        self.ready_button_rects: Dict[str, pygame.Rect] = {}
        self.difficulty_card_rects: Dict[str, pygame.Rect] = {}
        self.selected_difficulty: str = "NORMAL"

    def _load_assets(self) -> None:
        try:
            base_dir = Path(__file__).resolve().parent
        except NameError:
            base_dir = Path.cwd()
            
        base_asset_dir = base_dir / "assets"
        base_bg_dir = base_dir / "assets-images"
        
        if not base_asset_dir.exists():
            fallback_path_1 = Path(r"C:\Users\atom0\Desktop\2026 학교\컴퓨터프로그래밍\assets")
            fallback_path_2 = Path(r"C:\Users\atom0\Desktop\2026 학교\컴퓨터 프로그래밍\assets")
            
            if fallback_path_1.exists(): base_asset_dir = fallback_path_1
            elif fallback_path_2.exists(): base_asset_dir = fallback_path_2

        print(f"[시스템] 에셋 로딩 경로: {base_asset_dir}")

        img_dir = base_asset_dir / "images"
        sound_dir = base_asset_dir / "sounds"

        # 배경 이미지(메인 화면 + 게임 화면의 격자 외부)
        # 사용자가 말한 assets-images 폴더를 우선으로 찾고,
        # 없으면 기존 assets/images 폴더에서도 background.* 를 찾아봅니다.
        bg_candidates: list[Path] = []
        for ext in ("png", "jpg", "jpeg", "webp"):
            bg_candidates.append(base_bg_dir / f"background.{ext}")
        for ext in ("png", "jpg", "jpeg", "webp"):
            bg_candidates.append(img_dir / f"background.{ext}")

        for bg_path in bg_candidates:
            try:
                if bg_path.exists():
                    bg_img = pygame.image.load(str(bg_path)).convert()
                    self.background_surface = pygame.transform.smoothscale(bg_img, (WINDOW_WIDTH, WINDOW_HEIGHT))
                    print(f"[시스템] 배경 이미지 로드 성공: {bg_path}")
                    break
            except Exception as e:
                print(f"[시스템 경고] 배경 이미지 로드 실패: {bg_path} ({e})")
         
        try:
            if (img_dir / "snake_head.png").exists(): self.images['head'] = pygame.image.load(str(img_dir / "snake_head.png")).convert_alpha()
            if (img_dir / "snake_body.png").exists(): self.images['body'] = pygame.image.load(str(img_dir / "snake_body.png")).convert_alpha()
            if (img_dir / "food_normal.png").exists(): self.images['food'] = pygame.image.load(str(img_dir / "food_normal.png")).convert_alpha()
            if (img_dir / "item_potion.png").exists(): self.images['potion'] = pygame.image.load(str(img_dir / "item_potion.png")).convert_alpha()
            if (img_dir / "item_coin.png").exists(): self.images['coin'] = pygame.image.load(str(img_dir / "item_coin.png")).convert_alpha()
            
            for key in self.images:
                self.images[key] = pygame.transform.scale(self.images[key], (GRID_SIZE, GRID_SIZE))
        except Exception as e:
            print(f"[시스템 경고] 이미지 파일 로드 실패: {e}")

        # 💡 [BGM 디버깅] BGM 로드 상태를 터미널에 명확히 출력
        try:
            bgm_path = sound_dir / "bgm.mp3"
            if bgm_path.exists():
                pygame.mixer.music.load(str(bgm_path))
                pygame.mixer.music.set_volume(0.4)
                print("[시스템] BGM 파일(bgm.mp3) 로드 성공!")
            else:
                print(f"[경고] BGM 파일을 찾을 수 없습니다. 경로를 확인하세요: {bgm_path}")
        except Exception as e:
            print(f"[경고] BGM 로드 중 오류 발생 (파일 손상 또는 포맷 미지원): {e}")

        sfx_files = {"perfect": "perfect.wav", "good": "good.wav", "miss": "miss.wav", "gameover": "gameover.wav"}
        for key, filename in sfx_files.items():
            path = sound_dir / filename
            try:
                if path.exists():
                    self.sounds[key] = pygame.mixer.Sound(str(path))
                    self.sounds[key].set_volume(1.0)
                else:
                    self.sounds[key] = None
            except Exception:
                self.sounds[key] = None

    def play_sound(self, sound_key: str) -> None:
        sound = self.sounds.get(sound_key)
        if sound:
            channel = pygame.mixer.find_channel()
            if channel: channel.play(sound)
            else: sound.play()

    def get_elapsed_time(self) -> float:
        return (pygame.time.get_ticks() - self.start_ticks) / 1000.0

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.current_scene == UIScene.READY:
                    self._handle_ready_button_click(event.pos)
                elif self.current_scene == UIScene.DIFFICULTY:
                    self._handle_difficulty_card_click(event.pos)

            if event.type == pygame.KEYDOWN:
                if self.current_scene == UIScene.READY:
                    if event.key == pygame.K_SPACE:
                        self.current_scene = UIScene.COUNTDOWN
                        self.countdown_start_ticks = pygame.time.get_ticks()

                elif self.current_scene == UIScene.PLAYING:
                    direction_map = {
                        pygame.K_UP: Direction.UP, pygame.K_DOWN: Direction.DOWN,
                        pygame.K_LEFT: Direction.LEFT, pygame.K_RIGHT: Direction.RIGHT
                    }
                    if event.key in direction_map:
                        current_time = self.get_elapsed_time()
                        judgment = self.engine.process_player_input(direction_map[event.key], current_time)
                        self._process_judgment(judgment, current_time)

                elif self.current_scene == UIScene.GAME_OVER_POPUP:
                    if event.key == pygame.K_RETURN and len(self.player_name_input) > 0:
                        self._transition_to_leaderboard()
                    elif event.key == pygame.K_BACKSPACE:
                        self.player_name_input = self.player_name_input[:-1]
                    else:
                        if event.unicode.isalnum() and len(self.player_name_input) < 8:
                            self.player_name_input += event.unicode.upper()

                elif self.current_scene == UIScene.LEADERBOARD:
                    if event.key == pygame.K_r:
                        self.current_scene = UIScene.READY
                        self.player_name_input = ""
                        try: pygame.mixer.music.stop()
                        except Exception: pass
                elif self.current_scene == UIScene.DIFFICULTY:
                    if event.key == pygame.K_ESCAPE:
                        self.current_scene = UIScene.READY

    def _handle_ready_button_click(self, mouse_pos: tuple[int, int]) -> None:
        # READY 화면 버튼 클릭 처리
        # 기능이 정해진 버튼부터 순차적으로 동작을 붙입니다.
        for label, rect in self.ready_button_rects.items():
            if rect.collidepoint(mouse_pos):
                if label == "난이도 설정":
                    self.current_scene = UIScene.DIFFICULTY
                    break
                if label == "게임 종료":
                    pygame.quit()
                    sys.exit()
                break

    def _handle_difficulty_card_click(self, mouse_pos: tuple[int, int]) -> None:
        # 난이도 선택 화면 카드 클릭 처리
        # 카드 클릭 시 메인 화면(READY)로 돌아갑니다.
        for key, rect in self.difficulty_card_rects.items():
            if rect.collidepoint(mouse_pos):
                self.selected_difficulty = key

                # (선택사항) 이미지에 있는 BPM처럼 기본 BPM을 바꿔둡니다.
                # 실제 게임 시작 시 reset_game()에서 이 base_bpm이 사용됩니다.
                bpm_map = {"EASY": 100.0, "NORMAL": 130.0, "HARD": 170.0}
                self.engine.base_bpm = bpm_map.get(key, 130.0)

                self.current_scene = UIScene.READY
                break

    def _process_judgment(self, judgment: Judgment, current_time: float) -> None:
        if judgment == Judgment.IGNORED: return
        self.judgment_timer = current_time + 0.3 
        if judgment == Judgment.PERFECT:
            self.judgment_text, self.judgment_color = "PERFECT!", COLORS["PERFECT"]
            self.play_sound("perfect")
        elif judgment == Judgment.GOOD:
            self.judgment_text, self.judgment_color = "GOOD", COLORS["GOOD"]
            self.play_sound("good")
        elif judgment == Judgment.MISS:
            self.judgment_text, self.judgment_color = "MISS!", COLORS["MISS"]
            self.play_sound("miss")

    def _transition_to_leaderboard(self) -> None:
        self._draw_loading_screen()
        self.engine.send_score_to_server(self.player_name_input)
        self.engine.register_local_score(self.player_name_input)
        self.leaderboard_data = self.engine.fetch_server_leaderboard()
        if not self.leaderboard_data:
            self.leaderboard_data = self.engine.local_leaderboard
        self.current_scene = UIScene.LEADERBOARD

    def update(self) -> None:
        if self.current_scene == UIScene.COUNTDOWN:
            elapsed_countdown = (pygame.time.get_ticks() - self.countdown_start_ticks) / 1000.0
            if elapsed_countdown >= 3.0:
                self.current_scene = UIScene.PLAYING
                self.engine.reset_game()  
                self.start_ticks = pygame.time.get_ticks()  
                
                # 💡 [BGM 디버깅] 재생 시도 및 결과 출력
                try: 
                    pygame.mixer.music.play(-1)  
                    print("[시스템] BGM 재생 시작!")
                except Exception as e: 
                    print(f"[경고] BGM 재생 실패: {e}")

        elif self.current_scene == UIScene.PLAYING:
            current_time = self.get_elapsed_time()
            self.engine.update(current_time)

            if self.engine.state == GameState.GAME_OVER:
                self.current_scene = UIScene.GAME_OVER_POPUP
                try: pygame.mixer.music.fadeout(1000)
                except Exception: pass
                self.play_sound("gameover")

    def draw(self) -> None:
        # 배경 이미지가 있으면 먼저 깔고, 없으면 단색 배경 사용
        if self.background_surface:
            self.screen.blit(self.background_surface, (0, 0))
        else:
            self.screen.fill(COLORS["BACKGROUND"])
        
        if self.current_scene == UIScene.READY:
            self._draw_ready_screen()
        elif self.current_scene == UIScene.DIFFICULTY:
            self._draw_difficulty_screen()
        elif self.current_scene == UIScene.COUNTDOWN:
            self._draw_game_board() 
            self._draw_countdown_screen()
        elif self.current_scene in (UIScene.PLAYING, UIScene.GAME_OVER_POPUP):
            self._draw_game_board()
            
        if self.current_scene == UIScene.GAME_OVER_POPUP:
            self._draw_game_over_popup()
        elif self.current_scene == UIScene.LEADERBOARD:
            self._draw_leaderboard()
            
        pygame.display.flip()

    def _draw_ready_screen(self) -> None:
        # ------------------------------
        # 1) 타이틀/안내 문구 위치(요구사항 반영)
        # - 타이틀: 창 위에서 "글씨 높이의 2배"만큼 띄우기
        # - 안내 문구: 창 하단에서 "글씨 높이"만큼 띄우기
        # ------------------------------
        title_text = "RHYTMN SNAKE"
        prompt_text = "Play space to start"

        title_surf = self.font_large.render(title_text, True, COLORS["PERFECT"])
        title_h = title_surf.get_height()
        title_margin_top = title_h * 2
        title_center_y = int(title_margin_top + (title_h / 2))
        self.screen.blit(title_surf, title_surf.get_rect(center=(WINDOW_WIDTH // 2, title_center_y)))

        # 깜빡임 유지(기존 동작 유지)
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            prompt_surf = self.font_main.render(prompt_text, True, COLORS["TEXT_WHITE"])
            prompt_h = prompt_surf.get_height()
            prompt_margin_bottom = prompt_h
            prompt_center_y = int(WINDOW_HEIGHT - prompt_margin_bottom - (prompt_h / 2))
            self.screen.blit(prompt_surf, prompt_surf.get_rect(center=(WINDOW_WIDTH // 2, prompt_center_y)))

        # ------------------------------
        # 2) 중앙에서 살짝 아래에 버튼 3개(세로 배열)
        # - 게임 방법 / 난이도 설정 / 게임 종료
        # - 기능은 나중에 할당 예정이므로 지금은 그리기만 합니다.
        # ------------------------------
        labels = ["게임 방법", "난이도 설정", "게임 종료"]
        button_w = 320
        button_h = 56
        gap = 16

        total_h = button_h * len(labels) + gap * (len(labels) - 1)
        center_x = WINDOW_WIDTH // 2
        center_y = (WINDOW_HEIGHT // 2) + 80  # "중앙에서 살짝 아래"
        start_y = int(center_y - total_h / 2)

        self.ready_button_rects = {}

        mouse_pos = pygame.mouse.get_pos()
        for i, label in enumerate(labels):
            rect = pygame.Rect(0, 0, button_w, button_h)
            rect.center = (center_x, start_y + i * (button_h + gap) + button_h // 2)
            self.ready_button_rects[label] = rect

            is_hover = rect.collidepoint(mouse_pos)
            bg_color = (70, 70, 95) if is_hover else (55, 55, 75)
            border_color = COLORS["TEXT_WHITE"] if is_hover else COLORS["TEXT_GRAY"]
            
            # 버튼 배경 투명도 70% (255 * 0.7 = 178.5 ≈ 179)
            button_surface = pygame.Surface((button_w, button_h), pygame.SRCALPHA)
            button_surface.fill((0, 0, 0, 0))
            pygame.draw.rect(button_surface, (*bg_color, 179), button_surface.get_rect(), border_radius=10)
            self.screen.blit(button_surface, rect.topleft)
            pygame.draw.rect(self.screen, border_color, rect, width=2, border_radius=10)

            text_surf = self.font_main.render(label, True, COLORS["TEXT_WHITE"])
            self.screen.blit(text_surf, text_surf.get_rect(center=rect.center))

        # 현재 선택된 난이도 표시(작게)
        diff_surf = self.font_small.render(f"난이도: {self.selected_difficulty}", True, COLORS["TEXT_GRAY"])
        self.screen.blit(diff_surf, diff_surf.get_rect(center=(WINDOW_WIDTH // 2, center_y + total_h // 2 + 50)))

    def _draw_difficulty_screen(self) -> None:
        # ------------------------------
        # 난이도 선택 화면(이미지 레이아웃 참고)
        # - 상단: "난이도 선택"
        # - 하단: EASY / NORMAL / HARD 카드형 버튼(가로 배치)
        # ------------------------------
        self.difficulty_card_rects = {}

        # 상단 타이틀 바(네온 느낌을 간단 도형으로 흉내)
        title = "난이도 선택"
        title_surf = self.font_large.render(title, True, (240, 240, 255))
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, 90))

        bar_padding_x = 60
        bar_padding_y = 18
        bar_rect = pygame.Rect(0, 0, title_rect.width + bar_padding_x * 2, title_rect.height + bar_padding_y * 2)
        bar_rect.center = title_rect.center

        # 바 배경(약간 투명)
        bar_surface = pygame.Surface((bar_rect.width, bar_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(bar_surface, (90, 60, 140, 120), bar_surface.get_rect(), border_radius=14)
        pygame.draw.rect(bar_surface, (170, 120, 255, 200), bar_surface.get_rect(), width=3, border_radius=14)
        self.screen.blit(bar_surface, bar_rect.topleft)
        self.screen.blit(title_surf, title_rect)

        # 카드 설정(색상은 이미지의 느낌: 민트/노랑/핑크)
        cards = [
            ("EASY",   (80, 255, 210), 100, "여유로움", 1),
            ("NORMAL", (255, 220, 90), 130, "보통",     2),
            ("HARD",   (255, 120, 140),170, "까다로움", 3),
        ]

        card_w = 210
        card_h = 420
        gap = 45
        total_w = card_w * 3 + gap * 2
        start_x = (WINDOW_WIDTH - total_w) // 2
        top_y = 160

        mouse_pos = pygame.mouse.get_pos()
        for idx, (name, accent, bpm, desc, stars) in enumerate(cards):
            rect = pygame.Rect(start_x + idx * (card_w + gap), top_y, card_w, card_h)
            self.difficulty_card_rects[name] = rect

            hover = rect.collidepoint(mouse_pos)
            selected = (self.selected_difficulty == name)

            # 카드 배경(어두운 반투명) + 테두리(네온 색)
            card_surface = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            pygame.draw.rect(card_surface, (10, 10, 20, 160), card_surface.get_rect(), border_radius=18)

            border_alpha = 255 if (hover or selected) else 190
            pygame.draw.rect(card_surface, (*accent, border_alpha), card_surface.get_rect(), width=4, border_radius=18)

            # 상단 제목
            name_surf = self.font_card_title.render(name, True, accent)
            card_surface.blit(name_surf, name_surf.get_rect(center=(card_w // 2, 75)))

            # 별(간단히 텍스트로 표현)
            star_text = "★" * stars
            star_surf = self.font_main.render(star_text, True, accent)
            card_surface.blit(star_surf, star_surf.get_rect(center=(card_w // 2, 150)))

            # BPM
            bpm_left = self.font_main.render("BPM", True, COLORS["TEXT_WHITE"])
            bpm_val = self.font_large.render(str(bpm), True, accent)
            card_surface.blit(bpm_left, bpm_left.get_rect(midleft=(40, 250)))
            card_surface.blit(bpm_val, bpm_val.get_rect(midleft=(95, 252)))

            # 하단 설명
            sub1 = self.font_small.render("판정 기준", True, COLORS["TEXT_GRAY"])
            sub2 = self.font_main.render(desc, True, accent)
            card_surface.blit(sub1, sub1.get_rect(center=(card_w // 2, 330)))
            card_surface.blit(sub2, sub2.get_rect(center=(card_w // 2, 370)))

            # 선택 표시 점은 요청에 따라 사용하지 않습니다.

            self.screen.blit(card_surface, rect.topleft)

    def _draw_countdown_screen(self) -> None:
        elapsed = (pygame.time.get_ticks() - self.countdown_start_ticks) / 1000.0
        remain = max(1, 3 - int(elapsed))
        
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150)) 
        self.screen.blit(overlay, (0, 0))
        
        count_surf = self.font_judgment.render(str(remain), True, COLORS["FOOD_COIN"])
        self.screen.blit(count_surf, count_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)))

    def _draw_game_board(self) -> None:
        game_area_width = self.engine.grid_width * GRID_SIZE
        game_area_height = self.engine.grid_height * GRID_SIZE
        offset_x = (WINDOW_WIDTH - game_area_width) // 2
        offset_y = 40

        pygame.draw.rect(self.screen, (15, 15, 22), (offset_x, offset_y, game_area_width, game_area_height))
        
        for x in range(self.engine.grid_width + 1):
            pygame.draw.line(self.screen, COLORS["GRID_LINE"], (offset_x + x * GRID_SIZE, offset_y), (offset_x + x * GRID_SIZE, offset_y + game_area_height))
        for y in range(self.engine.grid_height + 1):
            pygame.draw.line(self.screen, COLORS["GRID_LINE"], (offset_x, offset_y + y * GRID_SIZE), (offset_x + game_area_width, offset_y + y * GRID_SIZE))

        for item in self.engine.items:
            ix, iy = item.position
            pos_rect = pygame.Rect(offset_x + ix * GRID_SIZE, offset_y + iy * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            
            img = None
            if item.item_type == ItemType.NORMAL_FOOD: img = self.images.get('food')
            elif item.item_type == ItemType.LIFE_POTION: img = self.images.get('potion')
            elif item.item_type == ItemType.BONUS_COIN: img = self.images.get('coin')
            
            if img:
                self.screen.blit(img, pos_rect)
            else:
                color = COLORS["FOOD_NORMAL"]
                if item.item_type == ItemType.LIFE_POTION: color = COLORS["FOOD_POTION"]
                elif item.item_type == ItemType.BONUS_COIN: color = COLORS["FOOD_COIN"]
                pygame.draw.circle(self.screen, color, pos_rect.center, GRID_SIZE // 2 - 2)

        for i, (sx, sy) in enumerate(self.engine.snake.body):
            pos_rect = pygame.Rect(offset_x + sx * GRID_SIZE, offset_y + sy * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            
            img = self.images.get('head') if i == 0 else self.images.get('body')
            if img:
                self.screen.blit(img, pos_rect)
            else:
                color = COLORS["SNAKE_HEAD"] if i == 0 else COLORS["SNAKE_BODY"]
                pygame.draw.rect(self.screen, color, pos_rect.inflate(-2, -2), border_radius=4)

        ui_top = offset_y + game_area_height + 15
        ui_text = f"SCORE: {self.engine.score}    COMBO: {self.engine.combo}    STAGE: {self.engine.stage}"
        self.screen.blit(self.font_main.render(ui_text, True, COLORS["TEXT_WHITE"]), (offset_x, ui_top))
        
        lives_surf = self.font_main.render(f"LIVES: {'❤' * max(0, self.engine.lives)}", True, (255, 100, 100))
        self.screen.blit(lives_surf, (offset_x, ui_top + 30))

        bpm_surf = self.font_main.render(f"BPM: {int(self.engine.rhythm.current_bpm)}", True, COLORS["PERFECT"])
        self.screen.blit(bpm_surf, (offset_x + game_area_width - bpm_surf.get_width(), ui_top))

        if self.current_scene == UIScene.PLAYING and self.get_elapsed_time() < self.judgment_timer:
            judg_surf = self.font_judgment.render(self.judgment_text, True, self.judgment_color)
            self.screen.blit(judg_surf, judg_surf.get_rect(center=(WINDOW_WIDTH // 2, (offset_y + game_area_height) // 2)))

    def _draw_game_over_popup(self) -> None:
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        popup_rect = pygame.Rect(0, 0, 450, 300)
        popup_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        pygame.draw.rect(self.screen, COLORS["POPUP_BG"], popup_rect, border_radius=15)
        pygame.draw.rect(self.screen, COLORS["TEXT_WHITE"], popup_rect, width=3, border_radius=15)

        go_surf = self.font_large.render("GAME OVER", True, COLORS["MISS"])
        self.screen.blit(go_surf, go_surf.get_rect(center=(WINDOW_WIDTH // 2, popup_rect.top + 50)))

        score_surf = self.font_main.render(f"Final Score: {self.engine.score}", True, COLORS["PERFECT"])
        self.screen.blit(score_surf, score_surf.get_rect(center=(WINDOW_WIDTH // 2, popup_rect.top + 110)))

        prompt_surf = self.font_small.render("Enter Nickname (Max 8) and press ENTER", True, COLORS["TEXT_GRAY"])
        self.screen.blit(prompt_surf, prompt_surf.get_rect(center=(WINDOW_WIDTH // 2, popup_rect.top + 160)))

        input_rect = pygame.Rect(0, 0, 250, 50)
        input_rect.center = (WINDOW_WIDTH // 2, popup_rect.top + 220)
        pygame.draw.rect(self.screen, (20, 20, 30), input_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLORS["TEXT_GRAY"], input_rect, width=2, border_radius=8)

        cursor_visible = (pygame.time.get_ticks() // 500) % 2 == 0
        display_text = self.player_name_input + ("|" if cursor_visible else "")
        name_surf = self.font_main.render(display_text, True, COLORS["TEXT_WHITE"])
        self.screen.blit(name_surf, name_surf.get_rect(center=input_rect.center))

    def _draw_loading_screen(self) -> None:
        loading_surf = self.font_main.render("Connecting to Render Server...", True, COLORS["GOOD"])
        self.screen.blit(loading_surf, loading_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 180)))
        pygame.display.flip()

    def _draw_leaderboard(self) -> None:
        title_surf = self.font_large.render("GLOBAL LEADERBOARD", True, COLORS["PERFECT"])
        self.screen.blit(title_surf, title_surf.get_rect(center=(WINDOW_WIDTH // 2, 80)))

        table_width = 500
        start_x = (WINDOW_WIDTH - table_width) // 2
        start_y = 150
        row_height = 40

        pygame.draw.rect(self.screen, COLORS["TABLE_HEADER"], (start_x, start_y, table_width, row_height))
        headers = [("RANK", start_x + 50), ("NAME", start_x + 250), ("SCORE", start_x + 450)]
        for text, cx in headers:
            h_surf = self.font_main.render(text, True, COLORS["TEXT_WHITE"])
            self.screen.blit(h_surf, h_surf.get_rect(center=(cx, start_y + row_height // 2)))

        for i, data in enumerate(self.leaderboard_data[:10]):
            y_pos = start_y + row_height + (i * row_height)
            bg_color = COLORS["TABLE_ROW"] if i % 2 == 0 else COLORS["BACKGROUND"]
            pygame.draw.rect(self.screen, bg_color, (start_x, y_pos, table_width, row_height))

            rank_color = COLORS["TEXT_WHITE"]
            if i == 0: rank_color = COLORS["FOOD_COIN"]
            elif i == 1: rank_color = (192, 192, 192)
            elif i == 2: rank_color = (205, 127, 50)

            rank_surf = self.font_main.render(f"#{i+1}", True, rank_color)
            name_surf = self.font_main.render(str(data.get("name", "UNKNOWN")), True, COLORS["TEXT_WHITE"])
            score_surf = self.font_main.render(str(data.get("score", 0)), True, COLORS["PERFECT"])

            self.screen.blit(rank_surf, rank_surf.get_rect(center=(start_x + 50, y_pos + row_height // 2)))
            self.screen.blit(name_surf, name_surf.get_rect(center=(start_x + 250, y_pos + row_height // 2)))
            self.screen.blit(score_surf, score_surf.get_rect(center=(start_x + 450, y_pos + row_height // 2)))

        if (pygame.time.get_ticks() // 600) % 2 == 0:
            restart_surf = self.font_main.render("Press 'R' to Restart", True, COLORS["GOOD"])
            self.screen.blit(restart_surf, restart_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50)))

    def run(self) -> None:
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    app = RhythmSnakeUI()
    app.run()
