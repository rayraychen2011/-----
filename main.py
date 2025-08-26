###################### 載入套件與模組 ######################
import pygame
import sys
import random
from typing import Tuple
import math
import colorsys

# 說明：
# 這個檔案使用 Pygame 建立一個敲磚塊遊戲。
# 目前包含：
# - 定義一個磚塊類別 `Brick`，可繪製在畫面上並支援被擊中（消失）狀態
# - 建立一個矩形磚塊牆（rows x cols），並使用 `gap` 參數產生方塊間的間距
# - 球、底板與完整的碰撞偵測系統
# - 球加速功能：按住左Shift鍵可讓球短暫加速移動
#
# 操作說明：
# - 空白鍵或右鍵：發射球
# - 滑鼠移動：控制底板位置
# - 左Shift鍵：按住時球會加速移動，放開時恢復正常速度
# - R鍵：重新隨機化磚塊漸層顏色
# - Q鍵：顯示/隱藏操作說明
# - ESC鍵：退出遊戲
# - 建立一個矩形磚塊牆（rows x cols），並使用 `gap` 參數產生方塊間的間距
# - 球、底板與完整的碰撞偵測系統
# - 球加速功能與繁體中文顯示支援
# 注意：當所有磚塊被消除時會顯示反射定律說明與遊戲結束訊息


###################### 物件類別：Brick ######################


class Brick:
    """磚塊物件（單一顆磚塊）

    屬性說明：
    - x, y: 磚塊左上角座標（像素）
    - width, height: 磚塊的寬與高（像素）
    - color: (R, G, B) 的三元素 tuple，定義磚塊顏色
    - hit: 布林值，代表磚塊是否被擊中（True 表示已被擊中並應該不再繪製）

    方法：
    - draw(surface, x=None, y=None): 在指定的 `surface` 上繪製磚塊；
      若傳入 x,y 則以傳入值取代物件內的座標，用於臨時移動或測試繪製位置。
    """

    def __init__(self, x, y, width, height, color, hit=False):
        # 儲存位置與大小
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        # 儲存顏色 (R, G, B)
        # base_color: 原始漸層色（不隨磚塊數量變化）
        self.base_color = color
        # color: 實際繪製用顏色（會在每一幀可能被動態調整）
        self.color = color
        # 是否被擊中（True 表示已消失）
        self.hit = hit
        # 是否為特殊磚塊（撞到會給予球體效果）
        self.is_special = False
        # 是否為特殊磚塊（撞到會給予球體效果）

    def draw(self, surface, x=None, y=None):
        """在畫面上繪製磚塊。

        行為說明：
        - 若 `self.hit` 為 True，代表磚塊已被擊中，跳過繪製。
        - 若提供 `x` 或 `y`，則以參數位置繪製（不改變物件內的座標屬性）。
        - 使用整數座標與尺寸繪製矩形，以避免 sub-pixel 模糊。
        """

        # 已被擊中則不繪製
        if self.hit:
            return

        # 使用傳入座標（若有）或物件內座標
        draw_x = self.x if x is None else x
        draw_y = self.y if y is None else y

        # 建立整數化的矩形（left, top, width, height）並繪製
        rect = (int(draw_x), int(draw_y), int(self.width), int(self.height))
        pygame.draw.rect(surface, self.color, rect)
        # 若為特殊磚，畫一層金色邊框以示標記
        if getattr(self, "is_special", False):
            try:
                pygame.draw.rect(surface, (255, 215, 0), rect, 3)
            except Exception:
                pass


class Ball:
    """簡單的球物件（圓形）

    屬性：x,y (中心), radius, vx, vy, color
    方法：draw(surface)
    """

    def __init__(
        self, x, y, radius=10, vx=5, vy=-5, color=(255, 255, 255), image_path=None
    ):
        self.x = float(x)
        self.y = float(y)
        self.radius = int(radius)
        self.vx = float(vx)
        self.vy = float(vy)
        self.color = color

        # 圖像支援（若提供路徑則載入並縮放到直徑大小）
        self.image_original = None
        if image_path is not None:
            try:
                img = pygame.image.load(image_path).convert_alpha()
                img = pygame.transform.smoothscale(
                    img, (self.radius * 2, self.radius * 2)
                )
                self.image_original = img
            except Exception as e:
                print(f"無法載入球的圖片 '{image_path}': {e}")
                self.image_original = None

        # 旋轉週期（ms）：3 秒轉 360 度
        self.rotation_period_ms = 3000
        # 旋轉起始時間（用來計算角度）
        self._rot_start = pygame.time.get_ticks()
        # 暫時放大效果（放大倍數與結束時間戳）
        self._powerup_scale = 1.0
        self._powerup_end_time = 0

    def draw(self, surface):
        # 加入藍色光暈：在球底下繪製多層半透明圓做為暈染
        try:
            draw_radius = int(self.radius * self._powerup_scale)
            # 光暈半徑會比球本體大一些
            glow_radius = max(draw_radius * 2, draw_radius + 12)
            glow_diam = glow_radius * 2
            glow_surf = pygame.Surface((glow_diam, glow_diam), pygame.SRCALPHA)
            # 基礎藍色（你可以調整成你喜歡的藍色）
            blue = (80, 160, 255)
            # 繪製發散光線（放射狀）：多條半透明射線 + 底層柔和圓形作基底
            now = pygame.time.get_ticks()
            # 放射線數量與參數
            rays = 18
            phase = (now % 2000) / 2000.0 * math.tau  # 2 秒一個完整相位
            cx = glow_radius
            cy = glow_radius
            # 畫底層柔和圓形當作光暈基底（較淡）
            try:
                pygame.draw.circle(
                    glow_surf,
                    (blue[0], blue[1], blue[2], 60),
                    (cx, cy),
                    int(glow_radius * 0.75),
                )
            except Exception:
                pass
            # 繪製多條放射狀射線，每條使用數層不同 alpha 與寬度以達到柔邊效果
            for i in range(rays):
                ang = (i / rays) * math.tau + phase * 0.6
                # 長度帶有細微擾動讓光線看起來更生動
                length = int(glow_radius * (0.9 + 0.25 * math.sin(ang * 2.3 + i)))
                # 基底顏色 alpha
                base_alpha = 200
                # 外圍使用較低 alpha 的寬線，內層用較高 alpha 的細線
                outer_w = max(2, int(glow_radius * 0.18))
                inner_w = max(1, int(glow_radius * 0.08))
                ex = int(cx + math.cos(ang) * length)
                ey = int(cy + math.sin(ang) * length)
                # 畫外層（柔和）
                try:
                    pygame.draw.line(
                        glow_surf,
                        (blue[0], blue[1], blue[2], int(base_alpha * 0.22)),
                        (cx, cy),
                        (ex, ey),
                        outer_w,
                    )
                except Exception:
                    pass
                # 畫中層（半亮）
                try:
                    pygame.draw.line(
                        glow_surf,
                        (blue[0], blue[1], blue[2], int(base_alpha * 0.45)),
                        (
                            int(cx + math.cos(ang) * (length * 0.45)),
                            int(cy + math.sin(ang) * (length * 0.45)),
                        ),
                        (ex, ey),
                        max(1, inner_w),
                    )
                except Exception:
                    pass
                # 畫頂層（亮點）
                try:
                    pygame.draw.line(
                        glow_surf,
                        (255, 255, 255, int(base_alpha * 0.9)),
                        (
                            int(cx + math.cos(ang) * (length * 0.6)),
                            int(cy + math.sin(ang) * (length * 0.6)),
                        ),
                        (ex, ey),
                        1,
                    )
                except Exception:
                    pass
            # 將光暈置中到球的位置
            gx = int(self.x - glow_radius)
            gy = int(self.y - glow_radius)
            try:
                surface.blit(glow_surf, (gx, gy), special_flags=0)
            except Exception:
                pass

            # 若有圖像，使用旋轉圖像繪製（以中心為座標）
            if self.image_original is not None:
                elapsed = pygame.time.get_ticks() - self._rot_start
                angle = (
                    (elapsed % self.rotation_period_ms) / self.rotation_period_ms * 360
                )
                scale = self._powerup_scale
                if scale != 1.0:
                    target_size = (
                        int(self.radius * 2 * scale),
                        int(self.radius * 2 * scale),
                    )
                    img = pygame.transform.smoothscale(self.image_original, target_size)
                else:
                    img = self.image_original
                rotated = pygame.transform.rotate(img, -angle)
                rect = rotated.get_rect(center=(int(self.x), int(self.y)))
                surface.blit(rotated, rect)
            else:
                # 畫球本體（在光暈之上）
                pygame.draw.circle(
                    surface, self.color, (int(self.x), int(self.y)), draw_radius
                )
        except Exception:
            # 若出問題，退回為簡單繪製
            try:
                pygame.draw.circle(
                    surface, self.color, (int(self.x), int(self.y)), int(self.radius)
                )
            except Exception:
                pass

    def update_powerups(self):
        if self._powerup_end_time and pygame.time.get_ticks() >= self._powerup_end_time:
            self._powerup_scale = 1.0
            self._powerup_end_time = 0

    def apply_temporary_scale(self, scale: float, duration_ms: int):
        self._powerup_scale = float(scale)
        self._powerup_end_time = pygame.time.get_ticks() + int(duration_ms)

    def rect(self):
        return pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            int(self.radius * 2),
            int(self.radius * 2),
        )


class Paddle:
    """馬蹄鐵 (U) 形底板。

    視覺上由左右兩條豎柱與底部半圓組成，預設開口朝上（面向畫面上方／磚塊方向）。
    - `width`: 整體外徑寬度（外圓直徑）
    - `height`: 兩條豎柱從頂端到半圓頂端的高度

    draw(surface, x): 在指定 x 座標繪製 U 形（不改變物件本身座標）。
    """

    def __init__(self, x, y, width, height=None, color=(240, 240, 240)):
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        # leg height：若未提供，預設為寬度的四分之一
        self.height = (
            int(height) if height is not None else max(8, int(self.width // 4))
        )
        self.color = color

    def draw(self, surface, x=None):
        draw_x = self.x if x is None else int(x)
        outer_r = float(self.width) / 2.0
        leg_h = float(self.height)
        # 桿子厚度（視覺與碰撞用）：占整體寬度的一小部分
        thickness = max(8, int(self.width * 0.18))

        total_h = int(leg_h + outer_r * 2.0)
        # 使用透明 surface 方便繪製複合圖形
        surf = pygame.Surface((int(self.width), total_h), pygame.SRCALPHA)

        # 繪製：內部為黃色，邊緣為黑色
        inner_color = self.color if self.color is not None else (255, 220, 60)
        edge_color = (0, 0, 0)
        outline_w = max(3, int(thickness * 0.5))
        try:
            # 先畫內部填充（黃色）
            pygame.draw.rect(surf, inner_color, (0, 0, thickness, total_h))
            pygame.draw.rect(
                surf, inner_color, (int(self.width) - thickness, 0, thickness, total_h)
            )
            center = (int(self.width / 2), int(leg_h + outer_r))
            pygame.draw.circle(surf, inner_color, center, int(outer_r))
            # 再畫黑色邊緣（描邊）
            try:
                pygame.draw.rect(
                    surf, edge_color, (0, 0, thickness, total_h), outline_w
                )
                pygame.draw.rect(
                    surf,
                    edge_color,
                    (int(self.width) - thickness, 0, thickness, total_h),
                    outline_w,
                )
            except Exception:
                pass
            try:
                pygame.draw.circle(surf, edge_color, center, int(outer_r), outline_w)
            except Exception:
                pass
        except Exception:
            # 若繪製出錯，退回為簡單矩形底板（黃色內、黑邊）
            try:
                pygame.draw.rect(surf, inner_color, (0, 0, int(self.width), total_h))
                pygame.draw.rect(
                    surf, edge_color, (0, 0, int(self.width), total_h), outline_w
                )
            except Exception:
                pass

        surface.blit(surf, (draw_x, self.y))


###################### 初始化 Pygame 與主要資源 ######################

# 初始化 Pygame（啟動所有模組）
pygame.init()

# 背景音樂：嘗試初始化 mixer、載入並循環播放 mp3
try:
    # 若系統尚未初始化 mixer，可先呼叫 init
    try:
        pygame.mixer.init()
    except Exception:
        # 若已初始化會拋例外，忽略之
        pass
    pygame.mixer.music.load("Roman P - On My Way.mp3")
    pygame.mixer.music.set_volume(0.5)  # 預設音量，可調
    pygame.mixer.music.play(-1)  # -1 表示無限循環
    music_playing = True
except Exception as e:
    print(f"無法載入背景音樂: {e}")
    music_playing = False

# 載入特殊撞擊音效（爆炸、低頻加強）
try:
    try:
        explosion_sound = pygame.mixer.Sound("explosion-sound-effect-bass-boosted.mp3")
        explosion_sound.set_volume(0.7)
    except Exception:
        # 若無法建立 Sound 物件就嘗試直接使用 mixer.music.play 作為後備
        explosion_sound = None
except Exception:
    explosion_sound = None

# 載入一般撞擊（鈴鐺）音效，建議放一個短的 `bell.wav` 或 `bell.ogg` 在專案目錄
try:
    try:
        # 優先嘗試載入 wav/ogg（較低延遲），若不存在再嘗試 mp3
        try:
            bell_sound = pygame.mixer.Sound("bell.wav")
        except Exception:
            try:
                bell_sound = pygame.mixer.Sound("bell.mp3")
            except Exception:
                bell_sound = None
        if bell_sound is not None:
            bell_sound.set_volume(0.6)
    except Exception:
        bell_sound = None
except Exception:
    bell_sound = None

# 建立 Pygame 時鐘物件，用來在主迴圈控制 FPS
clock = pygame.time.Clock()

# 視窗尺寸設定（可依需求調整）
width = 800
height = 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("敲磚塊遊戲")
# 背景圖路徑（放在 image 資料夾）
background_path = "image/assets_task_01k3gmrx28egpa7rn2b9nz4cxv_1756126663_img_0.webp"
try:
    bg_img = pygame.image.load(background_path).convert()
    # 縮放到視窗大小
    bg_img = pygame.transform.smoothscale(bg_img, (width, height))
except Exception as e:
    print(f"無法載入背景圖片 '{background_path}': {e}")
    bg_img = None
# 字型：用來繪製畫面上的文字（例如方塊剩餘數量）
# 使用支援繁體中文的字型
try:
    # 嘗試使用微軟正黑體
    font = pygame.font.SysFont("microsoftyahei", 28)
except:
    try:
        # 備用：使用微軟正黑體UI
        font = pygame.font.SysFont("microsoftyaheiui", 28)
    except:
        # 最後備用：使用預設字型
        font = pygame.font.Font(None, 28)

# 用於顯示物理計算的較小字型
try:
    physics_font = pygame.font.SysFont("microsoftyahei", 18)
except:
    try:
        physics_font = pygame.font.SysFont("microsoftyaheiui", 18)
    except:
        physics_font = pygame.font.Font(None, 18)

###################### 磚塊牆配置（Rows x Cols） ######################

# 參數說明：
# - rows, cols: 磚牆的行列數
# - brick_width, brick_height: 每個磚塊的寬/高
# - gap: 磚塊之間的間距（像素）。關鍵點是：在計算每個磚塊的 x,y 時
#   我們會使用 `(brick_width + gap)` 與 `(brick_height + gap)` 作為格距，
#   這樣每個磚塊之間會留出 `gap` 大小的空白（背景色會顯示為間隔）。

rows = 5
cols = 10
brick_width = 60
brick_height = 24
gap = 4  # 你可以調整這個數字來改變方塊之間的間距

# 計算整體磚牆所佔的寬度：
# 每列有 cols 個磚塊，每個磚塊寬度為 brick_width；
# 在 cols 個磚塊之間有 cols-1 段間距，每段間距為 gap
total_width = cols * brick_width + (cols - 1) * gap

# 使用水平置中：計算左側起點 x_offset
x_offset = (width - total_width) // 2

# y_offset 決定磚牆距離畫面頂端的起始高度
y_offset = 60

# 建立磚塊清單，清單裡每個元素都是一個 Brick 實例
bricks = []


def lerp(a: int, b: int, t: float) -> int:
    return int(a + (b - a) * t)


def lerp_color(
    c1: Tuple[int, int, int], c2: Tuple[int, int, int], t: float
) -> Tuple[int, int, int]:
    return (lerp(c1[0], c2[0], t), lerp(c1[1], c2[1], t), lerp(c1[2], c2[2], t))


def increase_contrast(
    color: Tuple[int, int, int], t: float, strength: float = 0.9
) -> Tuple[int, int, int]:
    """根據 t (0.0-1.0) 與 strength 增加顏色對比度。

    實作：以中灰 128 為中點，將每個通道移動到更遠處：
      new = 128 + (c - 128) * (1 + t * strength)
    並 clamp 到 0-255。
    """

    def clamp(v: float) -> int:
        return max(0, min(255, int(round(v))))

    factor = 1.0 + float(t) * float(strength)
    r = clamp(128 + (color[0] - 128) * factor)
    g = clamp(128 + (color[1] - 128) * factor)
    b = clamp(128 + (color[2] - 128) * factor)
    return (r, g, b)


def shift_towards_complement(
    color: Tuple[int, int, int], t: float, strength: float = 0.9
) -> Tuple[int, int, int]:
    """將顏色朝其互補色偏移。

    使用 HSV 色彩空間來計算互補色：將色相 (h) 加上 0.5 (等於 180 度)，
    保留原本的飽和度與明度 (s, v)。之後在原色與互補色之間做線性插值。

    參數 t (0.0-1.0) 為基礎強度，strength 調整最終插值幅度。
    """
    # guard t 範圍
    tt = min(max(float(t) * float(strength), 0.0), 1.0)

    # 轉換到 0..1 範圍並使用 colorsys
    r_f = color[0] / 255.0
    g_f = color[1] / 255.0
    b_f = color[2] / 255.0
    try:
        h, s, v = colorsys.rgb_to_hsv(r_f, g_f, b_f)
    except Exception:
        # 若轉換失敗，直接回傳原色
        return color

    comp_h = (h + 0.5) % 1.0
    cr_f, cg_f, cb_f = colorsys.hsv_to_rgb(comp_h, s, v)
    comp_color = (
        int(round(cr_f * 255)),
        int(round(cg_f * 255)),
        int(round(cb_f * 255)),
    )

    return lerp_color(color, comp_color, tt)


def random_color(min_v=30, max_v=225) -> Tuple[int, int, int]:
    return (
        random.randint(min_v, max_v),
        random.randint(min_v, max_v),
        random.randint(min_v, max_v),
    )


def generate_gradient_brick_colors(
    rows, cols, start_color, end_color, direction="horizontal"
):
    """根據 rows x cols 產生對應的顏色陣列（list），方向可為 horizontal/vertical/diagonal。"""
    colors = []
    for r in range(rows):
        for c in range(cols):
            if direction == "horizontal":
                denom = max(cols - 1, 1)
                t = c / denom
            elif direction == "vertical":
                denom = max(rows - 1, 1)
                t = r / denom
            else:  # diagonal
                denom_r = max(rows - 1, 1)
                denom_c = max(cols - 1, 1)
                t = (r / denom_r + c / denom_c) / 2

            # 中間加一點小隨機性讓漸層不那麼死板
            jitter = random.uniform(-0.03, 0.03)
            t = min(max(t + jitter, 0.0), 1.0)
            colors.append(lerp_color(start_color, end_color, t))
    return colors


def apply_gradient_to_bricks(
    bricks_list, rows, cols, start_color, end_color, direction="horizontal"
):
    gradient = generate_gradient_brick_colors(
        rows, cols, start_color, end_color, direction
    )
    for idx, brick in enumerate(bricks_list):
        # 保存原始漸層色為 base_color，並將當前繪製色設為相同
        brick.base_color = gradient[idx]
        brick.color = gradient[idx]


# 初次隨機產生漸層起訖色與方向
start_color = random_color()
end_color = random_color()
direction = random.choice(["horizontal", "vertical", "diagonal"])

# 建立並使用漸層顏色的磚塊清單
for r in range(rows):
    for c in range(cols):
        x = x_offset + c * (brick_width + gap)
        y = y_offset + r * (brick_height + gap)
        # 預先放一個佔位顏色，之後會用漸層覆寫
        bricks.append(
            Brick(x=x, y=y, width=brick_width, height=brick_height, color=(0, 0, 0))
        )

# 套用漸層到剛剛建立的磚塊
apply_gradient_to_bricks(bricks, rows, cols, start_color, end_color, direction)


def reset_bricks():
    """重置磚牆顯示（將所有brick.hit 設為 False）並重新隨機化漸層顏色。"""
    global start_color, end_color, direction
    # 當磚牆重製時，讓球回到底板上等待發射
    global ball_attached
    start_color = random_color()
    end_color = random_color()
    direction = random.choice(["horizontal", "vertical", "diagonal"])
    for b in bricks:
        b.hit = False
    apply_gradient_to_bricks(bricks, rows, cols, start_color, end_color, direction)
    # 指定特殊磚（重置時也隨機 5 個）
    assign_special_bricks(5)
    ball_attached = True


def assign_special_bricks(count=5):
    """從現有未被標記的磚塊中隨機選擇 `count` 個設為特殊磚塊。"""
    # 先清除所有標記
    for b in bricks:
        b.is_special = False
    available = [b for b in bricks if not b.hit]
    if len(available) == 0:
        return
    count = min(count, len(available))
    chosen = random.sample(available, count)
    for b in chosen:
        b.is_special = True
    # 印出偵錯資訊：列出被標記的磚塊索引與位置
    try:
        info = []
        for b in chosen:
            idx = bricks.index(b)
            info.append(f"idx={idx}(x={b.x},y={b.y})")
        print(f"[DEBUG] special bricks: {', '.join(info)}")
    except Exception:
        pass


# 初始呼叫（在函式定義後呼叫一次，確保存在特殊磚）
assign_special_bricks(5)


# ====== 底板 (使用 Brick 表示) ======
# 底板寬度比單顆磚塊寬（例如 1.8 倍），高度可比磚塊略高或相同
paddle_width = int(brick_width * 1.8)
paddle_height = brick_height
# 固定 y 值（距離畫面底部一定距離）
paddle_y = height - 48
# 初始 x 放在畫面中央
paddle_x = (width - paddle_width) // 2
# 底板顏色：亮黃色（較醒目）
paddle_color = (255, 220, 60)
# 使用 Paddle 類別建立半圓底板物件（不加入 bricks 清單）
paddle = Paddle(x=paddle_x, y=paddle_y, width=paddle_width, color=paddle_color)

# 平滑底板位置（實際繪製用），初始化為起始位置
paddle_pos_x = float(paddle_x)

# 平滑移動參數：每幀最大位移（像素），與插值係數（0-1）
PADDLE_MAX_STEP = 18.0
PADDLE_LERP = 0.28

# 用於儲存底板邊緣反彈的視覺效果（短暫高亮）
paddle_edge_effects = []

# 粒子系統
particles = []


def spawn_particles(
    x, y, count=12, color=(255, 200, 60), speed=4.0, spread=0.8, life=600
):
    """在 (x,y) 產生 count 個粒子，回傳不需要但會加入全域 particles。"""
    now = pygame.time.get_ticks()
    for i in range(count):
        angle = random.uniform(0, math.tau) * spread + random.uniform(-0.4, 0.4)
        # 速度沿隨機方向
        vx = math.cos(angle) * random.uniform(0.2 * speed, speed)
        vy = math.sin(angle) * random.uniform(0.2 * speed, speed) - abs(
            random.uniform(0, speed * 0.2)
        )
        particle = {
            "x": float(x),
            "y": float(y),
            "vx": vx,
            "vy": vy,
            "r": random.randint(2, 6),
            "color": color,
            "start": now,
            "life": int(life),
        }
        particles.append(particle)


# ====== 球物件實例初始化 ======
# 初始放在底板中點上方
ball_start_x = paddle_x + paddle_width // 2
# 將球放在底板上方，半徑放大為 32（原本 16 -> 現在 2 倍）
ball_start_y = paddle_y - 32
# 使用圖片作為球的外觀（檔案位於 image/卡皮.png），半徑設定為 32
ball_image_path = "image/卡皮.png"
ball = Ball(
    x=ball_start_x,
    y=ball_start_y,
    radius=32,
    vx=0,
    vy=0,
    color=(255, 200, 60),
    image_path=ball_image_path,
)
# 球是否附著在底板（等待空白鍵發射）
ball_attached = True
# 操作守則顯示旗標（預設關閉，按 Q 可以切換）
show_instructions = False
# 物理公式顯示旗標（預設關閉，按 M 可以切換）
show_physics = False

# ====== 球加速功能相關變數 ======
ball_boost_active = False  # 是否正在加速
ball_boost_multiplier = 5.0  # 加速倍數（使用者要求：五倍加速）
ball_normal_vx = 0  # 儲存正常的 x 速度
ball_normal_vy = 0  # 儲存正常的 y 速度
# 底板自動模式（按左鍵啟用，永久）
paddle_auto_mode = False


def predict_ball_landing_x(
    ball, bricks, width, height, paddle, start_paddle_x, max_iter=2000, step=6
):
    """模擬球的未來運動並回傳預計第一次碰到底板（paddle.y）時的 x 座標（球心位置）。

    此函式會考慮牆壁與磚塊碰撞，模擬到球向下並到達底板 y 座標時回傳 x。
    若模擬中球落出畫面底部或超過 iter 則回傳 None。
    """
    # 複製狀態
    x = float(ball.x)
    y = float(ball.y)
    vx = float(ball.vx)
    vy = float(ball.vy)
    r = int(ball.radius * getattr(ball, "_powerup_scale", 1.0))

    if vx == 0 and vy == 0:
        return None

    # 準備磚塊矩形快取
    brick_rects = [
        (i, pygame.Rect(b.x, b.y, b.width, b.height))
        for i, b in enumerate(bricks)
        if not b.hit
    ]

    it = 0
    bounces = 0
    while it < max_iter:
        it += 1
        speed = math.hypot(vx, vy)
        if speed == 0:
            break
        steps = max(1, int(math.ceil(speed / step)))
        dx = vx / steps
        dy = vy / steps
        for s in range(steps):
            x += dx
            y += dy

            # 牆壁碰撞
            if x - r <= 0:
                x = r
                vx = -vx
                bounces += 1
                continue
            elif x + r >= width:
                x = width - r
                vx = -vx
                bounces += 1
                continue
            if y - r <= 0:
                y = r
                vy = -vy
                bounces += 1
                continue

            # 若球到達或超過底板 y（球往下）就回傳當前 x
            # 使用 paddle.y 作為接收高度參考（球心到達此 y 表示會被底板接住）
            if vy > 0 and y + r >= paddle.y:
                return int(x)

            # 磚塊碰撞（簡單矩形相交判定）
            ball_future_rect = pygame.Rect(
                int(x - r), int(y - r), int(2 * r), int(2 * r)
            )
            hit_rect = None
            for idx, rect in brick_rects:
                if ball_future_rect.colliderect(rect):
                    hit_rect = rect
                    break
            if hit_rect is not None:
                # 根據與磚塊中心相對位置反轉主要分量
                cx = hit_rect.centerx
                cy = hit_rect.centery
                if abs(cx - x) > abs(cy - y):
                    vx = -vx
                else:
                    vy = -vy
                bounces += 1
                # 碰到磚塊後繼續模擬
                continue

            # 若球直接落出畫面底部，視為無法接住
            if y - r > height:
                return None

    return None


def aim_ball_at_brick(ball, bricks_list, prefer_above_y=None, speed=None):
    """讓球朝向一個尚未被擊中的磚塊中心。

    - prefer_above_y: 若提供，會優先選擇 y < prefer_above_y 的磚塊（通常是底板 y），
      以確保球朝上方飛行擊中磚塊。
    - speed: 若提供，使用此速度大小（像素/帧），否則使用球當前速度大小或預設 6.
    回傳 True 表示有選中並調整速度，False 則表示未調整（沒有可用磚塊）。
    """
    # 選出還沒被 hit 的磚塊
    candidates = [b for b in bricks_list if not b.hit]
    if not candidates:
        return False

    # 優先考量在 prefer_above_y 之上的磚塊
    if prefer_above_y is not None:
        above = [b for b in candidates if (b.y + b.height / 2.0) < prefer_above_y]
        if above:
            candidates = above

    # 選擇最靠近球心的磚塊中心作為目標（簡單又穩定）
    best = None
    best_dist = None
    for b in candidates:
        bx = b.x + b.width / 2.0
        by = b.y + b.height / 2.0
        d = math.hypot(bx - ball.x, by - ball.y)
        if best is None or d < best_dist:
            best = (bx, by)
            best_dist = d

    if best is None:
        return False

    tx, ty = best
    # 計算方向向量
    dx = float(tx - ball.x)
    dy = float(ty - ball.y)
    # 若目標在球下方，強制把目標 y 設為在球上方一點，避免朝下直接出界
    if prefer_above_y is not None and ty >= prefer_above_y:
        dy = min(dy, -abs(dy) - 1.0)

    mag = math.hypot(dx, dy)
    if mag == 0:
        return False

    # 決定速度大小
    if speed is None:
        cur_speed = math.hypot(float(ball.vx), float(ball.vy))
        if cur_speed <= 0.001:
            cur_speed = 6.0
    else:
        cur_speed = float(speed)

    nx = dx / mag
    ny = dy / mag
    ball.vx = nx * cur_speed
    ball.vy = ny * cur_speed

    # 若有儲存正常速度的變數（用於 boost 還原），同步更新
    try:
        globals()["ball_normal_vx"] = ball.vx
        globals()["ball_normal_vy"] = ball.vy
    except Exception:
        pass

    return True


def predict_landing_x_trajectory(
    ball,
    bricks,
    width,
    height,
    paddle,
    paddle_draw_x,
    max_bounces=12,
    step=6,
    max_iter=3000,
):
    """使用步進模擬球的未來運動並回傳球第一次接觸到底板高度時的 x 座標（球心）。

    這個函式複製並簡化了畫面內軌跡模擬的邏輯，專門回傳落點 x，供自動底板使用。
    若模擬中球落出畫面底部或超過最大步數則回傳 None。
    """
    x = float(ball.x)
    y = float(ball.y)
    vx = float(ball.vx)
    vy = float(ball.vy)
    r = int(ball.radius * getattr(ball, "_powerup_scale", 1.0))

    if vx == 0 and vy == 0:
        return None

    # 建立未被擊中的磚塊快取
    brick_rects = [
        pygame.Rect(b.x, b.y, b.width, b.height) for b in bricks if not b.hit
    ]

    it = 0
    bounces = 0
    while it < max_iter and bounces <= max_bounces:
        it += 1
        speed = math.hypot(vx, vy)
        if speed == 0:
            break
        steps = max(1, int(math.ceil(speed / step)))
        dx = vx / steps
        dy = vy / steps
        for s in range(steps):
            x += dx
            y += dy

            # 牆壁碰撞
            if x - r <= 0:
                x = r
                vx = -vx
                bounces += 1
                continue
            elif x + r >= width:
                x = width - r
                vx = -vx
                bounces += 1
                continue
            if y - r <= 0:
                y = r
                vy = -vy
                bounces += 1
                continue

            # 若球往下且到達或超過底板 y，回傳當前 x
            if vy > 0 and y + r >= paddle.y:
                return int(x)

            # 磚塊碰撞檢查
            ball_future_rect = pygame.Rect(
                int(x - r), int(y - r), int(2 * r), int(2 * r)
            )
            hit = None
            for rect in brick_rects:
                if ball_future_rect.colliderect(rect):
                    hit = rect
                    break
            if hit is not None:
                cx = hit.centerx
                cy = hit.centery
                if abs(cx - x) > abs(cy - y):
                    vx = -vx
                else:
                    vy = -vy
                bounces += 1
                continue

            # 若球已經落出畫面底部
            if y - r > height:
                return None

    return None


###################### 主程式（遊戲迴圈） ######################

while True:
    # 限制迴圈頻率到 60 FPS，保持遊戲速度穩定
    clock.tick(60)

    # 事件處理：例如視窗關閉事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # 正確關閉 Pygame 與 Python 程式
            pygame.quit()
            sys.exit()
        # 滑鼠按鍵處理：右鍵按下時若球附著則發射；左鍵按下切換物理顯示
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # 參考 Pygame 的按鍵編號：1=左鍵, 2=中鍵, 3=右鍵
            if event.button == 3:
                if "ball_attached" in globals() and ball_attached:
                    ball_attached = False
                    # 與空白鍵相同的發射行為：左右隨機、向上
                    ball.vx = 5 * (1 if random.random() < 0.5 else -1)
                    ball.vy = -5
                    # 初始化正常速度
                    ball_normal_vx = ball.vx
                    ball_normal_vy = ball.vy
                    # 若為自動模式，調整速度朝向未被擊中的磚塊
                    try:
                        if paddle_auto_mode:
                            aim_ball_at_brick(ball, bricks, prefer_above_y=paddle.y)
                    except Exception:
                        pass
            elif event.button == 1:
                # 左鍵：切換底板自動模式（toggle）
                try:
                    paddle_auto_mode = not paddle_auto_mode
                    if paddle_auto_mode:
                        print("[INFO] Paddle auto mode enabled")
                    else:
                        print("[INFO] Paddle auto mode disabled")
                except Exception:
                    paddle_auto_mode = True
                    print("[INFO] Paddle auto mode enabled")
            elif event.button == 2:
                # 中鍵：切換物理計算面板顯示
                if "show_physics" in globals():
                    show_physics = not show_physics
        elif event.type == pygame.KEYDOWN:
            # 按 R 鍵重新隨機化漸層
            if event.key == pygame.K_r:
                start_color = random_color()
                end_color = random_color()
                direction = random.choice(["horizontal", "vertical", "diagonal"])
                apply_gradient_to_bricks(
                    bricks, rows, cols, start_color, end_color, direction
                )
            # 按 G 顯示目前漸層參數（輸出到主控台）
            elif event.key == pygame.K_g:
                print(
                    f"Gradient: start={start_color}, end={end_color}, dir={direction}"
                )
            # 空白鍵：若球附著在底板則發射
            elif event.key == pygame.K_SPACE:
                if "ball_attached" in globals() and ball_attached:
                    ball_attached = False
                    # 朝上發射，左右方向隨機
                    ball.vx = 5 * (1 if random.random() < 0.5 else -1)
                    ball.vy = -5
                    # 初始化正常速度
                    ball_normal_vx = ball.vx
                    ball_normal_vy = ball.vy
                    # 若為自動模式，讓球朝向未被擊中的磚塊
                    try:
                        if paddle_auto_mode:
                            aim_ball_at_brick(ball, bricks, prefer_above_y=paddle.y)
                    except Exception:
                        pass
            # 按 Q 顯示/隱藏操作守則
            elif event.key == pygame.K_q:
                show_instructions = not show_instructions
            # (M 鍵已移除，左鍵切換物理解說)
            # 按 ESC 離開遊戲
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    # 繪製背景圖或填色（磚塊之間的 gap 會顯示此背景）
    if bg_img is not None:
        try:
            screen.blit(bg_img, (0, 0))
        except Exception:
            screen.fill((0, 0, 0))
    else:
        screen.fill((0, 0, 0))  # 使用黑色背景

    # 在左上角顯示方塊剩餘數量（數字置於圓圈中央）
    remaining = sum(1 for b in bricks if not b.hit)
    count_text = f"{remaining}"
    # 可調整的圓圈與文字設定
    circle_margin_left = 8
    circle_margin_top = 8
    circle_fill_color = (30, 40, 60)  # 圓圈填色，可改
    circle_border_color = (255, 255, 255)  # 邊框顏色
    circle_border_w = 3

    # 先渲染文字以取得尺寸，之後把文字置中在圓圈
    text_surf = font.render(count_text, True, (255, 255, 255))
    try:
        # 計算圓半徑，確保文字可以放入圓中（帶一點內距 padding）
        padding = 8
        text_w = text_surf.get_width()
        text_h = text_surf.get_height()
        # 半徑至少要容納文字寬度/高度的一半，再加上 padding
        circle_radius = max(16, int(max(text_w, text_h) // 2 + padding))

        # 中心座標（左上角 margin + 半徑）
        cx = circle_margin_left + circle_radius
        cy = circle_margin_top + circle_radius

        # 畫圓（填色 + 邊框）並把文字置中
        try:
            # 光暈（glow）設定：建立一個透明 surface，畫多層半透明圓再用加色混合疊回主畫面
            glow_color = (100, 160, 255)  # 光暈顏色（可調）
            glow_layers = 10
            glow_strength = 0.9
            # glow surface 大小：以圓半徑為基準放大
            glow_pad = max(8, int(circle_radius * 1.8))
            glow_surf_size = circle_radius * 2 + glow_pad * 2
            try:
                glow_surf = pygame.Surface(
                    (glow_surf_size, glow_surf_size), pygame.SRCALPHA
                )
                gx = glow_surf_size // 2
                gy = glow_surf_size // 2
                for i in range(glow_layers, 0, -1):
                    t = i / float(glow_layers)
                    r = int(circle_radius + (1.0 - t) * circle_radius * 1.6)
                    alpha = int(180 * (t ** (0.8 / max(0.01, glow_strength))))
                    try:
                        pygame.draw.circle(
                            glow_surf,
                            (glow_color[0], glow_color[1], glow_color[2], alpha),
                            (gx, gy),
                            r,
                        )
                    except Exception:
                        pass
                # 使用加色混合疊回主畫面以產生輕微發光效果
                try:
                    screen.blit(
                        glow_surf,
                        (cx - gx, cy - gy),
                        special_flags=pygame.BLEND_RGBA_ADD,
                    )
                except Exception:
                    # fallback: 直接 blit
                    screen.blit(glow_surf, (cx - gx, cy - gy))
            except Exception:
                pass

            # 畫實心圓、邊框與文字（置中）
            pygame.draw.circle(screen, circle_fill_color, (cx, cy), circle_radius)
            pygame.draw.circle(
                screen, circle_border_color, (cx, cy), circle_radius, circle_border_w
            )
            txt_rect = text_surf.get_rect(center=(cx, cy))
            screen.blit(text_surf, txt_rect)
        except Exception:
            # 若繪製圓失敗則 fallback 為直接繪製文字
            screen.blit(text_surf, (circle_margin_left, circle_margin_top))
    except Exception:
        # 最後回退：如果任何步驟失敗，簡單繪製文字在左上角
        try:
            screen.blit(text_surf, (8, 8))
        except Exception:
            pass

    # 右上角顯示物理公式與計算（按 M 切換）
    # 右上角顯示底板自動模式狀態（Auto: ON/OFF）
    try:
        auto_text = "Auto: ON" if paddle_auto_mode else "Auto: OFF"
        auto_color = (120, 255, 140) if paddle_auto_mode else (200, 80, 80)
        auto_surf = font.render(auto_text, True, auto_color)
        pad = 8
        box_w = auto_surf.get_width() + pad * 2
        box_h = auto_surf.get_height() + pad * 2
        box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        try:
            pygame.draw.rect(
                box_surf, (10, 12, 20, 190), (0, 0, box_w, box_h), border_radius=8
            )
        except Exception:
            box_surf.fill((10, 12, 20, 190))
        # 畫文字於 box 內
        box_surf.blit(auto_surf, (pad, pad))
        box_rect = box_surf.get_rect()
        box_rect.topright = (width - 8, 8)
        screen.blit(box_surf, box_rect)
    except Exception:
        pass
    if "show_physics" in globals() and show_physics:
        try:
            # 計算速度大小與分量
            vx = float(ball.vx)
            vy = float(ball.vy)
            speed = math.hypot(vx, vy)
            # 假設質量 m = 1，計算動能 KE = 0.5 * m * v^2
            m = 1.0
            ke = 0.5 * m * (speed**2)
            # 入射角（相對於法線）。若用水平為基準，入射角可用 atan2
            # 這裡展示入射角（degrees）相對於垂直法線：theta = atan2(vx, -vy)
            # 當球向上時 vy < 0，入射角為正表示偏右
            theta_rad = 0.0
            try:
                theta_rad = math.atan2(vx, -vy)
            except Exception:
                theta_rad = 0.0
            theta_deg = math.degrees(theta_rad)

            # 準備多行文字
            lines = []
            lines.append("物理解說：")
            lines.append(f"速度大小 |v| = {speed:.2f} px/frame")
            lines.append(f"速度分量 vx = {vx:.2f}, vy = {vy:.2f}")
            lines.append(f"動能 KE = 0.5*m*v^2 (m=1) = {ke:.2f}")
            lines.append(f"入射角 θ (相對法線) = {theta_deg:.1f}°")
            lines.append("反射角 θ' = θ (反射定律)")

            # 繪製背景方塊以利閱讀
            pad = 8
            line_h = physics_font.get_linesize()
            box_w = 320
            box_h = line_h * len(lines) + pad * 2
            box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            # 半透明深色背景
            try:
                pygame.draw.rect(
                    box_surf, (8, 8, 20, 180), (0, 0, box_w, box_h), border_radius=6
                )
            except Exception:
                box_surf.fill((8, 8, 20, 180))

            for i, ln in enumerate(lines):
                try:
                    txt = physics_font.render(ln, True, (240, 240, 240))
                    box_surf.blit(txt, (pad, pad + i * line_h))
                except Exception:
                    pass

            # 放在畫面正中央
            center_x = (width - box_w) // 2
            center_y = (height - box_h) // 2
            screen.blit(box_surf, (center_x, center_y))
        except Exception:
            pass

    # 當剩餘磚塊為 0 時，隱藏球並顯示反射定律說明與大紅字
    if remaining == 0:
        # 停止並隱藏球（避免看到移動）
        try:
            ball.vx = 0
            ball.vy = 0
        except Exception:
            pass

        # 繪製（若有剩餘磚塊會顯示，但理論上 remaining==0 所有磚塊都已被 hit）
        for brick in bricks:
            if brick.hit:
                continue
            brick.draw(screen)

        # 大紅字（帶陰影）
        try:
            # 嘗試使用微軟正黑體
            big_font = pygame.font.SysFont("microsoftyahei", 96)
        except:
            try:
                # 備用：使用微軟正黑體UI
                big_font = pygame.font.SysFont("microsoftyaheiui", 96)
            except:
                # 最後備用：使用預設字型
                big_font = pygame.font.Font(None, 96)
        big_text = "你學廢了嗎"
        red = (220, 20, 20)
        # 陰影先畫一層黑色偏移，再畫紅色
        shadow = big_font.render(big_text, True, (0, 0, 0))
        shadow_rect = shadow.get_rect(center=(width // 2 + 4, height // 2 + 4))
        screen.blit(shadow, shadow_rect)
        big_surf = big_font.render(big_text, True, red)
        big_rect = big_surf.get_rect(center=(width // 2, height // 2))
        screen.blit(big_surf, big_rect)

        # 反射定律說明文字（多行，置中排列）
        try:
            # 嘗試使用微軟正黑體
            small_font = pygame.font.SysFont("microsoftyahei", 24)  # 稍微縮小字體
        except:
            try:
                # 備用：使用微軟正黑體UI
                small_font = pygame.font.SysFont("microsoftyaheiui", 24)
            except:
                # 最後備用：使用預設字型
                small_font = pygame.font.Font(None, 24)

        # 文字換行函數
        def wrap_text(text, font, max_width):
            """將文字按寬度分割成多行，支援中文"""
            lines = []
            current_line = ""

            for char in text:
                test_line = current_line + char
                text_width = font.size(test_line)[0]

                if text_width <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                        current_line = char
                    else:
                        # 單個字符就超寬，強制加入
                        lines.append(char)
                        current_line = ""

            if current_line:
                lines.append(current_line)

            return lines

        explan_texts = [
            "入射角反射角公式是反射定律，其核心是入射角（θi）等於反射角（θr），即 θi = θr。",
            "公式的意義與應用：",
            "θi (入射角)：入射光線與界面法線之間的夾角。",
            "θr (反射角)：反射光線與界面法線之間的夾角。",
            "法線：與反射面垂直的一條假想線，在反射點上垂直於界面。",
            "反射定律：入射角等於反射角 (θi = θr)。",
            "折射定律（區別）：n1*sin(θ1) = n2*sin(θ2)。",
        ]

        # 處理所有文字行，進行自動換行
        all_lines = []
        max_text_width = width - 40  # 左右各留20像素邊距

        for text in explan_texts:
            wrapped_lines = wrap_text(text, small_font, max_text_width)
            all_lines.extend(wrapped_lines)
            # 在段落間增加空行
            if text != explan_texts[-1]:  # 最後一段不加空行
                all_lines.append("")  # 空行

        start_y = big_rect.bottom + 18
        line_height = 26
        for i, line in enumerate(all_lines):
            if line:  # 非空行才渲染
                surf = small_font.render(line, True, (255, 255, 255))
                rect = surf.get_rect(center=(width // 2, start_y + i * line_height))
                screen.blit(surf, rect)
            # 空行也要佔用行高，但不渲染任何內容

        pygame.display.update()
        continue

    # 更新並繪製底板：讓底板的中心跟隨滑鼠的 x 座標，y 固定
    mouse_x, _ = pygame.mouse.get_pos()
    # 將滑鼠 x 轉換成底板左上角 x（讓滑鼠位於底板中點）
    paddle_draw_x = int(mouse_x - paddle.width / 2)
    # 若啟用自動模式且球不附著，嘗試預測球落點並讓底板移動到該位置
    if paddle_auto_mode and not ball_attached:
        try:
            # 優先使用基於軌跡的模擬預測落點，若失敗則 fallback 到舊的預測函式
            landing_x = predict_landing_x_trajectory(
                ball, bricks, width, height, paddle, paddle_draw_x
            )
            if landing_x is None:
                landing_x = predict_ball_landing_x(
                    ball, bricks, width, height, paddle, paddle_draw_x
                )
            if landing_x is not None:
                # 將底板中心放在 landing_x，轉為左上角 x
                paddle_draw_x = int(landing_x - paddle.width / 2)
        except Exception:
            pass
    # 限制底板不超出畫面
    if paddle_draw_x < 0:
        paddle_draw_x = 0
    elif paddle_draw_x > width - paddle.width:
        paddle_draw_x = width - paddle.width
    # 平滑移動：將顯示位置 paddle_pos_x 緩慢移向目標 paddle_draw_x
    try:
        # 計算差距
        diff = float(paddle_draw_x) - float(paddle_pos_x)
        # 限制每幀最大移動距離
        if abs(diff) > PADDLE_MAX_STEP:
            step = PADDLE_MAX_STEP if diff > 0 else -PADDLE_MAX_STEP
            paddle_pos_x += step
        else:
            # 使用簡單線性內插以產生平滑感
            paddle_pos_x = paddle_pos_x + diff * PADDLE_LERP
        # 確保邊界
        if paddle_pos_x < 0:
            paddle_pos_x = 0.0
        elif paddle_pos_x > width - paddle.width:
            paddle_pos_x = float(width - paddle.width)
    except Exception:
        paddle_pos_x = float(paddle_draw_x)

    # 使用 Paddle.draw 的參數 x 來繪製移動中的半圓底板（不修改物件本身座標）
    paddle.draw(screen, x=int(paddle_pos_x))

    # 若球附著在底板上，讓球跟隨底板位置並跳過物理更新，等待空白鍵發射
    if "ball_attached" in globals() and ball_attached:
        ball.x = paddle_draw_x + paddle.width // 2
        ball.y = paddle.y - ball.radius
        ball.vx = 0
        ball.vy = 0
        # 繪製球與磚塊，並立即更新畫面後繼續下一循環
        ball.draw(screen)
        # 同樣在等待時也要根據剩餘磚塊數調整顏色（剩越少 -> 顏色越鮮豔）
        total_bricks = rows * cols
        ratio = (
            sum(1 for b in bricks if not b.hit) / total_bricks
            if total_bricks > 0
            else 0
        )
        # 當剩餘越少 (ratio 越小)，t_vivid 越大 -> 越靠近白色（更鮮豔）
        t_vivid = min(max(1.0 - ratio, 0.0), 1.0)
        vivid_strength = 0.9
        t_effect = t_vivid * vivid_strength
        for brick in bricks:
            if brick.hit:
                continue
            # 依 t_effect 與 vivid_strength 將色系偏向互補色
            brick.color = shift_towards_complement(
                brick.base_color, t_vivid, vivid_strength
            )
            brick.draw(screen)
        pygame.display.update()
        continue

    # ===== 球的移動與碰撞處理 =====

    # 檢查加速按鍵狀態（使用 LSHIFT 左Shift鍵）
    keys = pygame.key.get_pressed()
    boost_key_pressed = keys[pygame.K_LSHIFT]

    # 處理球加速邏輯
    if not ball_attached:  # 只有在球不附著底板時才處理加速
        if boost_key_pressed and not ball_boost_active:
            # 按下加速鍵，開始加速
            ball_boost_active = True
            ball_normal_vx = ball.vx
            ball_normal_vy = ball.vy
            ball.vx *= ball_boost_multiplier
            ball.vy *= ball_boost_multiplier
        elif not boost_key_pressed and ball_boost_active:
            # 放開加速鍵，恢復正常速度
            ball_boost_active = False
            ball.vx = ball_normal_vx
            ball.vy = ball_normal_vy

    # 更新球的位置
    ball.x += ball.vx
    ball.y += ball.vy

    # 更新任何暫時效果（例如放大）
    try:
        ball.update_powerups()
    except Exception:
        pass

    # 碰到左右牆壁
    if ball.x - ball.radius <= 0:
        ball.x = ball.radius
        ball.vx = -ball.vx
        # 更新正常速度
        if ball_boost_active:
            ball_normal_vx = -ball_normal_vx
    elif ball.x + ball.radius >= width:
        ball.x = width - ball.radius
        ball.vx = -ball.vx
        # 更新正常速度
        if ball_boost_active:
            ball_normal_vx = -ball_normal_vx

    # 碰到上方牆壁
    if ball.y - ball.radius <= 0:
        ball.y = ball.radius
        ball.vy = -ball.vy
        # 更新正常速度
        if ball_boost_active:
            ball_normal_vy = -ball_normal_vy

    # 碰到底部（簡單處理：重置球到底板上方）
    if ball.y - ball.radius > height:
        if paddle_auto_mode:
            # 自動模式：不要重來，直接讓球反彈回來（模擬被底板成功接住）
            try:
                # 將球移回畫面內並反向 y 速度
                ball.y = height - ball.radius - 1
                ball.vy = -abs(ball.vy) if ball.vy != 0 else -5
                # 嘗試微調 x 使球位於畫面內
                if ball.x < ball.radius:
                    ball.x = ball.radius + 2
                elif ball.x > width - ball.radius:
                    ball.x = width - ball.radius - 2
            except Exception:
                pass
        else:
            # 重置磚牆
            reset_bricks()
            # 將球附著到底板，等待玩家按空白鍵發射
            ball_attached = True
            ball.x = paddle_draw_x + paddle.width // 2
            ball.y = paddle.y - ball.radius
            ball.vx = 0
            ball.vy = 0
            # 重置加速狀態
            ball_boost_active = False
            ball_normal_vx = 0
            ball_normal_vy = 0

    # 球與馬蹄鐵底板碰撞：左右豎柱 (rect) 與底部半圓 (circle)
    if ball.vy > 0:
        outer_r = float(paddle.width) / 2.0
        leg_h = float(paddle.height)
        thickness = max(8, int(paddle.width * 0.18))
        total_h = int(leg_h + outer_r * 2.0)

        # 矩形 (left / right)
        left_rect = pygame.Rect(paddle_draw_x, paddle.y, thickness, total_h)
        right_rect = pygame.Rect(
            paddle_draw_x + paddle.width - thickness, paddle.y, thickness, total_h
        )

        collided = False

        # 內聯的反射計算（避免 nonlocal 問題）
        def _do_reflect(nx, ny):
            n_len = math.hypot(nx, ny)
            if n_len == 0:
                return False
            n_x = nx / n_len
            n_y = ny / n_len
            v_dot_n = ball.vx * n_x + ball.vy * n_y
            ball.vx = ball.vx - 2 * v_dot_n * n_x
            ball.vy = ball.vy - 2 * v_dot_n * n_y
            if ball_boost_active:
                global ball_normal_vx, ball_normal_vy
                normal_v_dot_n = ball_normal_vx * n_x + ball_normal_vy * n_y
                ball_normal_vx = ball_normal_vx - 2 * normal_v_dot_n * n_x
                ball_normal_vy = ball_normal_vy - 2 * normal_v_dot_n * n_y
            return True

        # 檢查左右矩形碰撞（找到矩形上最接近球心的點）
        for rect in (left_rect, right_rect):
            closest_x = max(rect.left, min(ball.x, rect.right))
            closest_y = max(rect.top, min(ball.y, rect.bottom))
            dist = math.hypot(ball.x - closest_x, ball.y - closest_y)
            if dist <= ball.radius:
                # 法線由碰撞點指向球心
                nx = ball.x - closest_x
                ny = ball.y - closest_y
                if dist == 0:
                    nx, ny = 0.0, -1.0
                    dist = 1.0
                did = _do_reflect(nx, ny)
                if did:
                    collided = True
                    # 若啟用自動模式，反射後重新瞄準磚塊
                    try:
                        if paddle_auto_mode:
                            aim_ball_at_brick(ball, bricks, prefer_above_y=paddle.y)
                    except Exception:
                        pass
                # 推開球以避免穿透
                overlap = ball.radius - dist
                if overlap > 0:
                    n_len = math.hypot(nx, ny) or 1.0
                    ball.x += (nx / n_len) * overlap
                    ball.y += (ny / n_len) * overlap
                try:
                    paddle_edge_effects.append(
                        {
                            "x": int(closest_x),
                            "y": int(closest_y),
                            "start": pygame.time.get_ticks(),
                            "duration": 350,
                            "max_r": max(8, ball.radius),
                        }
                    )
                except Exception:
                    pass
                break

        # 若尚未碰撞，檢查底部半圓
        if not collided:
            cx = paddle_draw_x + paddle.width / 2.0
            cy = paddle.y + leg_h + outer_r
            distc = math.hypot(ball.x - cx, ball.y - cy)
            if distc <= (outer_r + ball.radius):
                # 球與圓相交：法線為球心指向圓心的反向（圓對外法線）
                nx = ball.x - cx
                ny = ball.y - cy
                if distc == 0:
                    nx, ny = 0.0, -1.0
                    distc = 1.0
                did = _do_reflect(nx, ny)
                if did:
                    collided = True
                # 推開球
                overlap = (outer_r + ball.radius) - distc
                if overlap > 0:
                    n_len = math.hypot(nx, ny) or 1.0
                    ball.x += (nx / n_len) * overlap
                    ball.y += (ny / n_len) * overlap
                try:
                    # 在圓邊上的最近點
                    closest_x = cx + (nx / (math.hypot(nx, ny) or 1.0)) * outer_r
                    closest_y = cy + (ny / (math.hypot(nx, ny) or 1.0)) * outer_r
                    paddle_edge_effects.append(
                        {
                            "x": int(closest_x),
                            "y": int(closest_y),
                            "start": pygame.time.get_ticks(),
                            "duration": 350,
                            "max_r": max(8, ball.radius),
                        }
                    )
                except Exception:
                    pass

    # 球與磚塊碰撞：檢查每個磚塊是否碰撞，若碰撞則將磚塊設為 hit 並反轉球的 vy
    for brick in bricks:
        if brick.hit:
            continue
        if ball.rect().colliderect(
            pygame.Rect(brick.x, brick.y, brick.width, brick.height)
        ):
            brick.hit = True
            # 若為特殊磚塊，給予球暫時放大效果（2倍，持續 1000ms = 1s）
            if getattr(brick, "is_special", False):
                try:
                    # 放大球的暫時效果
                    ball.apply_temporary_scale(2.0, 1000)
                    # 播放特殊磚塊音效（若有載入）
                    try:
                        if (
                            "explosion_sound" in globals()
                            and explosion_sound is not None
                        ):
                            explosion_sound.play()
                    except Exception:
                        try:
                            # fallback: 嘗試用 music 播放短音檔（不循環）
                            pygame.mixer.music.load(
                                "explosion-sound-effect-bass-boosted.mp3"
                            )
                            pygame.mixer.music.play(0)
                        except Exception:
                            pass
                    try:
                        idx = bricks.index(brick)
                        # 計算該磚在 rows x cols 中的 r, c
                        r = idx // cols
                        c = idx % cols
                        cleared = []
                        # 清除以該磚為中心的 3x3 區塊
                        for dr in (-1, 0, 1):
                            for dc in (-1, 0, 1):
                                nr = r + dr
                                nc = c + dc
                                if 0 <= nr < rows and 0 <= nc < cols:
                                    nidx = nr * cols + nc
                                    if not bricks[nidx].hit:
                                        bricks[nidx].hit = True
                                        cleared.append(f"idx={nidx}(r={nr},c={nc})")
                        if cleared:
                            print(
                                f"[DEBUG] hit special brick idx={idx} at ({brick.x},{brick.y}) cleared: {', '.join(cleared)}"
                            )
                        else:
                            print(
                                f"[DEBUG] hit special brick idx={idx} at ({brick.x},{brick.y}) but nothing new to clear"
                            )
                    except Exception:
                        print("[DEBUG] hit special brick (index unknown)")
                except Exception:
                    pass
                try:
                    spawn_particles(
                        brick.x + brick.width // 2,
                        brick.y + brick.height // 2,
                        count=18,
                        color=(255, 150, 80),
                        speed=4.5,
                        spread=1.2,
                        life=700,
                    )
                except Exception:
                    pass
            else:
                # 普通磚塊被打到，播放鈴鐺音效（若已載入）
                try:
                    if "bell_sound" in globals() and bell_sound is not None:
                        bell_sound.play()
                except Exception:
                    pass
                try:
                    spawn_particles(
                        brick.x + brick.width // 2,
                        brick.y + brick.height // 2,
                        count=10,
                        color=(255, 220, 180),
                        speed=3.5,
                        spread=1.0,
                        life=500,
                    )
                except Exception:
                    pass
            # 簡單根據球心與磚塊中心判定反彈方向
            if abs((brick.x + brick.width / 2) - ball.x) > abs(
                (brick.y + brick.height / 2) - ball.y
            ):
                ball.vx = -ball.vx
                # 更新正常速度
                if ball_boost_active:
                    ball_normal_vx = -ball_normal_vx
            else:
                ball.vy = -ball.vy
                # 更新正常速度
                if ball_boost_active:
                    ball_normal_vy = -ball_normal_vy
            break

    # (GIF / 貓圖示已移除)

    # 繪製球
    ball.draw(screen)

    # 繪製並更新底板邊緣反彈效果
    if paddle_edge_effects:
        effect_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        now = pygame.time.get_ticks()
        alive = []
        for ef in paddle_edge_effects:
            elapsed = now - ef.get("start", 0)
            dur = ef.get("duration", 300)
            if elapsed > dur:
                continue
            t = elapsed / dur
            alpha = int(200 * (1.0 - t))
            r = int(ef.get("max_r", 16) * (0.6 + 0.8 * (1.0 - t)))
            color = (255, 200, 60, alpha)
            try:
                pygame.draw.circle(effect_surf, color, (ef["x"], ef["y"]), r)
            except Exception:
                pass
            alive.append(ef)
        # 更新列表
        paddle_edge_effects[:] = alive
        # 把效果疊加到主畫面
        screen.blit(effect_surf, (0, 0))

    # 更新並繪製粒子系統
    if particles:
        part_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        now = pygame.time.get_ticks()
        new_parts = []
        for p in particles:
            age = now - p.get("start", 0)
            life = p.get("life", 600)
            if age >= life:
                continue
            t = age / life
            # 更新運動：簡單重力與空氣阻力
            p["vy"] += 0.18  # gravity
            p["vx"] *= 0.995
            p["vy"] *= 0.995
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            # alpha 跟著壽命遞減
            alpha = int(255 * (1.0 - t))
            r = max(1, int(p.get("r", 3) * (1.0 - 0.4 * t)))
            col = p.get("color", (255, 200, 60))
            try:
                pygame.draw.circle(
                    part_surf,
                    (col[0], col[1], col[2], alpha),
                    (int(p["x"]), int(p["y"])),
                    r,
                )
            except Exception:
                pass
            new_parts.append(p)
        particles[:] = new_parts
        screen.blit(part_surf, (0, 0))

    # 軌跡預測功能：模擬未來位置（考慮牆壁與磚塊碰撞），繪製黃色軌跡
    def predict_trajectory(
        ball,
        bricks,
        width,
        height,
        paddle,
        paddle_draw_x,
        max_bounces=6,
        step=6,
        delay_s=0.5,
    ):
        """使用簡單的步進模擬來預測球的軌跡。

        - ball: Ball 物件（函式不會修改原物件，而是複製速度/座標）
        - bricks: Brick 清單（會考慮未被擊中的磚塊）
        - max_bounces: 最多模擬反彈次數
        - step: 每次模擬移動的像素距離（較小更精準，但較慢）
        - delay_s: 只回傳距離球體大約 delay_s 秒後的軌跡點

        回傳一個由 (x,y) tuple 組成的點清單，用於繪製軌跡（若沒有超過 delay，回傳空清單）。
        """
        pts = []
        # 複製狀態
        x = float(ball.x)
        y = float(ball.y)
        vx = float(ball.vx)
        vy = float(ball.vy)
        r = int(ball.radius * getattr(ball, "_powerup_scale", 1.0))

        if vx == 0 and vy == 0:
            return pts

        pts.append((int(x), int(y)))
        bounces = 0

        # 建立磚塊矩形的快取（只包含未被擊中的）
        brick_rects = [
            (i, pygame.Rect(b.x, b.y, b.width, b.height))
            for i, b in enumerate(bricks)
            if not b.hit
        ]

        # 最大模擬步數避免死迴圈
        max_iter = 2000
        it = 0
        while bounces <= max_bounces and it < max_iter:
            it += 1
            # 根據速度方向切分步進數量
            speed = math.hypot(vx, vy)
            if speed == 0:
                break
            # 將步長標準化到指定的像素步進
            steps = max(1, int(math.ceil(speed / step)))
            dx = vx / steps
            dy = vy / steps
            collided = False
            for s in range(steps):
                x += dx
                y += dy
                pts.append((int(x), int(y)))

                # 檢查左右牆壁
                if x - r <= 0:
                    x = r
                    vx = -vx
                    bounces += 1
                    collided = True
                    break
                elif x + r >= width:
                    x = width - r
                    vx = -vx
                    bounces += 1
                    collided = True
                    break
                # 檢查上方牆
                if y - r <= 0:
                    y = r
                    vy = -vy
                    bounces += 1
                    collided = True
                    break

                # 檢查磚塊碰撞（使用球的邊界矩形與每個磚塊矩形相交）
                ball_future_rect = pygame.Rect(
                    int(x - r), int(y - r), int(2 * r), int(2 * r)
                )
                hit_idx = None
                hit_rect = None
                # --- 檢查底板碰撞（左右兩個矩形與底部半圓） ---
                try:
                    # 只在球往下的時候考慮與底板碰撞（與實際遊戲邏輯一致）
                    if float(vy) > 0:
                        outer_r = float(paddle.width) / 2.0
                        leg_h = float(paddle.height)
                        thickness = max(8, int(paddle.width * 0.18))
                        total_h = int(leg_h + outer_r * 2.0)

                        left_rect = pygame.Rect(
                            paddle_draw_x, paddle.y, thickness, total_h
                        )
                        right_rect = pygame.Rect(
                            paddle_draw_x + paddle.width - thickness,
                            paddle.y,
                            thickness,
                            total_h,
                        )

                        # 檢查左右矩形
                        for rect in (left_rect, right_rect):
                            closest_x = max(rect.left, min(x, rect.right))
                            closest_y = max(rect.top, min(y, rect.bottom))
                            dist = math.hypot(x - closest_x, y - closest_y)
                            if dist <= r:
                                # 法線由碰撞點指向球心
                                nx = x - closest_x
                                ny = y - closest_y
                                if dist == 0:
                                    nx, ny = 0.0, -1.0
                                    dist = 1.0
                                n_len = math.hypot(nx, ny) or 1.0
                                n_x = nx / n_len
                                n_y = ny / n_len
                                v_dot_n = vx * n_x + vy * n_y
                                vx = vx - 2 * v_dot_n * n_x
                                vy = vy - 2 * v_dot_n * n_y
                                # 推開以避免穿透
                                overlap = r - dist
                                if overlap > 0:
                                    x += (nx / n_len) * overlap
                                    y += (ny / n_len) * overlap
                                bounces += 1
                                collided = True
                                break

                        # 若尚未碰撞，檢查底部半圓
                        if not collided:
                            cx = paddle_draw_x + paddle.width / 2.0
                            cy = paddle.y + leg_h + outer_r
                            distc = math.hypot(x - cx, y - cy)
                            if distc <= (outer_r + r):
                                nx = x - cx
                                ny = y - cy
                                if distc == 0:
                                    nx, ny = 0.0, -1.0
                                    distc = 1.0
                                n_len = math.hypot(nx, ny) or 1.0
                                n_x = nx / n_len
                                n_y = ny / n_len
                                v_dot_n = vx * n_x + vy * n_y
                                vx = vx - 2 * v_dot_n * n_x
                                vy = vy - 2 * v_dot_n * n_y
                                # 推開
                                overlap = (outer_r + r) - distc
                                if overlap > 0:
                                    x += (nx / n_len) * overlap
                                    y += (ny / n_len) * overlap
                                bounces += 1
                                collided = True
                except Exception:
                    pass

                # 若未被底板碰撞，再檢查磚塊碰撞
                for idx, rect in brick_rects:
                    if ball_future_rect.colliderect(rect):
                        hit_idx = idx
                        hit_rect = rect
                        break
                if hit_rect is not None:
                    # 根據與磚塊中心的相對距離判定主要反彈方向
                    cx = hit_rect.centerx
                    cy = hit_rect.centery
                    if abs(cx - x) > abs(cy - y):
                        vx = -vx
                    else:
                        vy = -vy
                    bounces += 1
                    collided = True
                    break

                # 若到底部則結束（不再模擬）
                if y - r > height:
                    collided = True
                    break

            if not collided:
                # 若這次整段步進沒有任何碰撞，繼續下一段
                continue
            # 若碰撞並且仍有反彈次數，繼續模擬
            if bounces > max_bounces:
                break

        # 根據 delay_s 過濾：只回傳距離球體約 delay_s 秒後的點
        speed0 = math.hypot(float(ball.vx), float(ball.vy))
        if speed0 <= 0:
            return []
        dist_threshold = speed0 * float(delay_s)
        cum = 0.0
        out_pts = []
        prev = (float(pts[0][0]), float(pts[0][1]))
        for p in pts[1:]:
            cur = (float(p[0]), float(p[1]))
            seg = math.hypot(cur[0] - prev[0], cur[1] - prev[1])
            cum += seg
            prev = cur
            if cum >= dist_threshold:
                out_pts.append((int(cur[0]), int(cur[1])))

        return out_pts

    # 繪製黃色軌跡（預測）：在一個透明 Surface 上繪製，再疊回主畫面
    try:
        traj_pts = predict_trajectory(
            ball,
            bricks,
            width,
            height,
            paddle,
            paddle_draw_x,
            max_bounces=8,
            step=6,
            delay_s=0.5,
        )
        if traj_pts:
            trail_surf = pygame.Surface((width, height), pygame.SRCALPHA)
            # 漸層起訖色 (RGBA)：改為藍色系做光暈效果
            start_col = (120, 190, 255, 220)
            end_col = (180, 220, 255, 24)
            try:
                n = len(traj_pts)
                if n >= 2:
                    # 逐段畫線，使用線段索引作為 t
                    # 為了呈現光暈，先畫粗的半透明藍，再畫較細亮的內層
                    for i in range(n - 1):
                        t = i / max(1, n - 1)
                        r = lerp(start_col[0], end_col[0], t)
                        g = lerp(start_col[1], end_col[1], t)
                        b = lerp(start_col[2], end_col[2], t)
                        a = lerp(start_col[3], end_col[3], t)
                        # 外層 glow：較大半透明線條
                        w_outer = max(6, int(18 * (1.0 - t)))
                        color_outer = (r, g, b, int(a * 0.35))
                        try:
                            pygame.draw.line(
                                trail_surf,
                                color_outer,
                                traj_pts[i],
                                traj_pts[i + 1],
                                w_outer,
                            )
                        except Exception:
                            pass
                        # 內層亮線：細且更不透明
                        w_inner = max(2, int(6 * (1.0 - t)))
                        color_inner = (r, g, b, int(a * 1.0))
                        try:
                            pygame.draw.line(
                                trail_surf,
                                color_inner,
                                traj_pts[i],
                                traj_pts[i + 1],
                                w_inner,
                            )
                        except Exception:
                            pass

                    # 畫小圓點以強調路徑（每隔幾點畫一個），大小也跟隨漸層
                    # 在路徑上畫一些微光點（外層淡藍 + 內層亮點）
                    step_dot = 6
                    for idx, p in enumerate(traj_pts[::step_dot]):
                        i = idx * step_dot
                        t = i / max(1, n - 1)
                        r = lerp(start_col[0], end_col[0], t)
                        g = lerp(start_col[1], end_col[1], t)
                        b = lerp(start_col[2], end_col[2], t)
                        a = lerp(start_col[3], end_col[3], t)
                        # 外層柔和圓
                        try:
                            pygame.draw.circle(
                                trail_surf,
                                (r, g, b, int(a * 0.35)),
                                p,
                                max(5, int(10 * (1.0 - t))),
                            )
                        except Exception:
                            pass
                        # 內層亮點
                        try:
                            pygame.draw.circle(
                                trail_surf,
                                (255, 255, 255, int(a)),
                                p,
                                max(2, int(4 * (1.0 - t))),
                            )
                        except Exception:
                            pass
            except Exception:
                pass
            screen.blit(trail_surf, (0, 0))
    except Exception:
        pass

    # 繪製所有磚塊：若某個 Brick 的 .hit 為 True，draw() 會跳過它
    # 動態調整磚塊顏色：當剩餘磚塊越少，磚塊顏色越接近白色（變得更鮮豔）
    total_bricks = rows * cols
    # ratio = 剩餘 / 總數；當 ratio 越小 -> t 越大（越暗）
    ratio = remaining / total_bricks if total_bricks > 0 else 0
    # 轉換為插值參數 t，range 0.0 (所有磚) 到 1.0 (沒磚)
    t_vivid = min(max(1.0 - ratio, 0.0), 1.0)
    # 可以調整 vivid_strength 來控制鮮豔強度（0.0 不變，1.0 完全白）
    vivid_strength = 0.9

    for brick in bricks:
        if brick.hit:
            continue
        # 根據 t_vivid 與 vivid_strength 將色系偏向互補色
        brick.color = shift_towards_complement(
            brick.base_color, t_vivid, vivid_strength
        )
        brick.draw(screen)

    # 操作守則功能已移除

    # 更新整個顯示畫面。可改為 pygame.display.flip()，兩者功能相近。
    pygame.display.update()
