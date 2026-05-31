from pathlib import Path
from PIL import Image, ImageDraw

def create_game_assets():
    # 1. 저장 경로 확인 및 생성
    output_dir = Path("C:\\Users\\atom0\\Desktop\\2026 학교\\컴퓨터 프로그래밍\\assets\\images")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    size = (30, 30)
    transparent_bg = (0, 0, 0, 0)

    # ----------------------------------------------------
    # [1] 뱀 머리 (snake_head.png)
    # 네온 블루(#00B4FF) 사각형 + 우측 끝 노란색 눈 2개
    # ----------------------------------------------------
    head = Image.new("RGBA", size, transparent_bg)
    draw_head = ImageDraw.Draw(head)
    
    # 메인 사각형 몸체 (약간의 여백을 두어 꽉 찬 느낌과 경계를 처리)
    draw_head.rectangle([2, 2, 27, 27], fill=(0, 180, 255, 255))
    
    # 오른쪽에 배치할 노란색 눈 2개 (2x2 크기)
    draw_head.rectangle([22, 6, 24, 8], fill=(255, 255, 0, 255))
    draw_head.rectangle([22, 21, 24, 23], fill=(255, 255, 0, 255))
    
    head.save(output_dir / "snake_head.png")

    # ----------------------------------------------------
    # [2] 뱀 몸통 (snake_body.png)
    # 짙은 사이언 블루(#0078DC) 둥근 사각형
    # ----------------------------------------------------
    body = Image.new("RGBA", size, transparent_bg)
    draw_body = ImageDraw.Draw(body)
    
    # 테두리가 부드럽게 마감된 사각형 (둥근 모서리 반경 5px 적용)
    draw_body.rounded_rectangle([3, 3, 26, 26], radius=5, fill=(0, 120, 220, 255))
    
    body.save(output_dir / "snake_body.png")

    # ----------------------------------------------------
    # [3] 일반 음식 (food_normal.png)
    # 네온 레드(#FF3232) 다이아몬드(마름모) 형태
    # ----------------------------------------------------
    food = Image.new("RGBA", size, transparent_bg)
    draw_food = ImageDraw.Draw(food)
    
    # 30x30 내에서 균형 잡힌 다이아몬드 꼭짓점 좌표 지정
    diamond_coords = [(15, 2), (27, 15), (15, 27), (3, 15)]
    draw_food.polygon(diamond_coords, fill=(255, 50, 50, 255))
    
    food.save(output_dir / "food_normal.png")

    # ----------------------------------------------------
    # [4] 물약 아이템 (item_potion.png)
    # 네온 그린(#32FF32) 체력 회복 물약 병 모양
    # ----------------------------------------------------
    potion = Image.new("RGBA", size, transparent_bg)
    draw_potion = ImageDraw.Draw(potion)
    
    # 물약 병의 외곽 형태 다각형 좌표 (좁은 목 부분과 퍼지는 아래 부분)
    bottle_coords = [
        (11, 6), (18, 6),       # 목 위쪽
        (18, 11), (24, 15),     # 어깨 부분
        (24, 26), (5, 26),      # 바닥 부분
        (5, 15), (11, 11)       # 왼쪽 어깨 및 목
    ]
    draw_potion.polygon(bottle_coords, fill=(50, 255, 50, 255))
    
    # 물약 마개 디테일 추가 (밝은 녹색/민트색 뚜껑)
    draw_potion.rectangle([10, 3, 19, 5], fill=(200, 255, 200, 255))
    
    potion.save(output_dir / "item_potion.png")

    # ----------------------------------------------------
    # [5] 코인 아이템 (item_coin.png)
    # 황금색(#FFD700) 원형 동전 형태
    # ----------------------------------------------------
    coin = Image.new("RGBA", size, transparent_bg)
    draw_coin = ImageDraw.Draw(coin)
    
    # 동전 외곽 원
    draw_coin.ellipse([3, 3, 26, 26], fill=(255, 215, 0, 255))
    # 동전 입체감을 위한 내부 어두운 테두리 선
    draw_coin.ellipse([6, 6, 23, 23], fill=(184, 134, 11, 255))
    # 동전 내부 밝은 안쪽 영역
    draw_coin.ellipse([9, 9, 20, 20], fill=(255, 215, 0, 255))
    
    coin.save(output_dir / "item_coin.png")

    print("[알림] 모든 30x30 임시 게임용 이미지 에셋이 'assets/images/' 폴더에 안전하게 생성되었습니다.")

if __name__ == "__main__":
    create_game_assets()