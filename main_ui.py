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
        except Exception:
            self.font_small = pygame.font.Font(None, 24)
            self.font_main = pygame.font.Font(None, 30)
            self.font_large = pygame.font.Font(None, 60)
            self.font_judgment = pygame.font.Font(None, 80)

        self.engine = GameEngine(grid_width=20, grid_height=20, base_bpm=120.0)

        self.images: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, Optional[pygame.mixer.Sound]] = {}
        self._load_assets()

        self.current_scene: UIScene = UIScene.READY
        self.start_ticks: int = 0
        self.countdown_start_ticks: int = 0
        
        self.judgment_text: str = ""
        self.judgment_color: tuple[int, int, int] = COLORS["TEXT_WHITE"]
        self.judgment_timer: float = 0.0
        
        self.player_name_input: str = ""
        self.leaderboard_data: List[Dict[str, Any]] = []

    def _load_assets(self) -> None:
        try:
            base_dir = Path(__file__).resolve().parent
        except NameError:
            base_dir = Path.cwd()
            
        base_asset_dir = base_dir / "assets"
        
        if not base_asset_dir.exists():
            fallback_path_1 = Path(r"C:\Users\atom0\Desktop\2026 학교\컴퓨터프로그래밍\assets")
            fallback_path_2 = Path(r"C:\Users\atom0\Desktop\2026 학교\컴퓨터 프로그래밍\assets")
            
            if fallback_path_1.exists(): base_asset_dir = fallback_path_1
            elif fallback_path_2.exists(): base_asset_dir = fallback_path_2

        print(f"[시스템] 에셋 로딩 경로: {base_asset_dir}")

        img_dir = base_asset_dir / "images"
        sound_dir = base_asset_dir / "sounds"
         
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
        self.screen.fill(COLORS["BACKGROUND"])
        
        if self.current_scene == UIScene.READY:
            self._draw_ready_screen()
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
        title_surf = self.font_large.render("RHYTHM SNAKE", True, COLORS["PERFECT"])
        self.screen.blit(title_surf, title_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50)))
        
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            prompt_surf = self.font_main.render("Press SPACE to Start", True, COLORS["TEXT_WHITE"])
            self.screen.blit(prompt_surf, prompt_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50)))

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