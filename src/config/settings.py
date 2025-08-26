######################載入套件######################
"""
遊戲設定配置\n
\n
此檔案包含敲磚塊遊戲的所有設定參數，包括：\n
- 視窗與顯示設定\n
- 遊戲物件尺寸與位置\n
- 資源檔案路徑\n
- 顏色與字型設定\n
- 音效音量設定\n
"""
import os

######################路徑設定######################

# 取得專案根目錄：從當前檔案位置往上三層
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

######################視窗設定######################

WINDOW_WIDTH = 800    # 遊戲視窗寬度（像素）
WINDOW_HEIGHT = 600   # 遊戲視窗高度（像素）
FPS = 60             # 遊戲幀率（每秒幀數）
WINDOW_TITLE = "敲磚塊遊戲"  # 視窗標題

######################磚塊牆設定######################

ROWS = 5             # 磚塊牆的行數
COLS = 10            # 磚塊牆的列數
BRICK_WIDTH = 60     # 單個磚塊的寬度（像素）
BRICK_HEIGHT = 24    # 單個磚塊的高度（像素）
BRICK_GAP = 4        # 磚塊之間的間隔（像素）

######################底板設定######################

PADDLE_WIDTH_MULTIPLIER = 1.8  # 底板寬度倍數（相對於磚塊寬度）
PADDLE_Y_OFFSET = 48           # 底板距離視窗底部的距離（像素）

######################球設定######################

BALL_RADIUS = 32              # 球的半徑（像素）
BALL_BOOST_MULTIPLIER = 5.0   # 球加速時的速度倍數

######################平滑移動設定######################

PADDLE_MAX_STEP = 18.0  # 底板每幀最大移動距離（像素）
PADDLE_LERP = 0.28      # 底板移動的線性插值係數（0-1，越小越平滑）

######################資源路徑######################

# 資源根目錄
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")

# 圖片檔案路徑
BACKGROUND_IMAGE = os.path.join(IMAGES_DIR, "background.webp")  # 背景圖片
BALL_IMAGE = os.path.join(IMAGES_DIR, "ball.png")              # 球的圖片

# 音效檔案路徑
BELL_SOUND = os.path.join(SOUNDS_DIR, "bell.wav")              # 鈴鐺音效
EXPLOSION_SOUND = os.path.join(SOUNDS_DIR, "explosion.mp3")    # 爆炸音效
BACKGROUND_MUSIC = os.path.join(SOUNDS_DIR, "background_music.mp3")  # 背景音樂

######################顏色設定######################

BACKGROUND_COLOR = (0, 0, 0)      # 背景顏色（黑色）
PADDLE_COLOR = (255, 220, 60)     # 底板顏色（金黃色）
BALL_COLOR = (255, 200, 60)       # 球的顏色（偏橘金色）

######################字型設定######################

DEFAULT_FONT_SIZE = 28   # 預設字型大小
PHYSICS_FONT_SIZE = 18   # 物理面板字型大小
BIG_FONT_SIZE = 96       # 大字型大小（用於遊戲結束畫面）
SMALL_FONT_SIZE = 24     # 小字型大小

######################音效設定######################

MUSIC_VOLUME = 0.5      # 背景音樂音量（0.0-1.0）
EXPLOSION_VOLUME = 0.7  # 爆炸音效音量（0.0-1.0）
BELL_VOLUME = 0.6       # 鈴鐺音效音量（0.0-1.0）