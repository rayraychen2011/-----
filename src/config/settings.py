"""
遊戲設定配置
"""
import os

# 取得專案根目錄
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 視窗設定
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
WINDOW_TITLE = "敲磚塊遊戲"

# 磚塊牆設定
ROWS = 5
COLS = 10
BRICK_WIDTH = 60
BRICK_HEIGHT = 24
BRICK_GAP = 4

# 底板設定
PADDLE_WIDTH_MULTIPLIER = 1.8
PADDLE_Y_OFFSET = 48

# 球設定
BALL_RADIUS = 32
BALL_BOOST_MULTIPLIER = 5.0

# 平滑移動設定
PADDLE_MAX_STEP = 18.0
PADDLE_LERP = 0.28

# 資源路徑
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")

# 具體檔案路徑
BACKGROUND_IMAGE = os.path.join(IMAGES_DIR, "background.webp")
BALL_IMAGE = os.path.join(IMAGES_DIR, "ball.png")
BELL_SOUND = os.path.join(SOUNDS_DIR, "bell.wav")
EXPLOSION_SOUND = os.path.join(SOUNDS_DIR, "explosion.mp3")
BACKGROUND_MUSIC = os.path.join(SOUNDS_DIR, "background_music.mp3")

# 顏色設定
BACKGROUND_COLOR = (0, 0, 0)
PADDLE_COLOR = (255, 220, 60)
BALL_COLOR = (255, 200, 60)

# 字型設定
DEFAULT_FONT_SIZE = 28
PHYSICS_FONT_SIZE = 18
BIG_FONT_SIZE = 96
SMALL_FONT_SIZE = 24

# 音效設定
MUSIC_VOLUME = 0.5
EXPLOSION_VOLUME = 0.7
BELL_VOLUME = 0.6