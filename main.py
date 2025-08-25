###################### 載入套件與模組 ######################
import pygame
import sys
import random
from typing import Tuple
import math

# 說明：
# 這個檔案使用 Pygame 建立一個最簡單的敲磚塊畫面範例。
# 目前包含：
# - 定義一個磚塊類別 `Brick`，可繪製在畫面上並支援被擊中（消失）狀態
# - 建立一個矩形磚塊牆（rows x cols），並使用 `gap` 參數產生方塊間的間距
# - 簡單的主迴圈處理視窗事件與繪製
# 注意：本範例未實作球、底板與碰撞偵測，僅示範磚塊排列與繪製


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


class Ball:
    """簡單的球物件（圓形）

    屬性：x,y (中心), radius, vx, vy, color
    方法：draw(surface)
    """

    def __init__(self, x, y, radius=10, vx=5, vy=-5, color=(255, 255, 255)):
        self.x = float(x)
        self.y = float(y)
        self.radius = radius
        self.vx = float(vx)
        self.vy = float(vy)
        self.color = color

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

    def rect(self):
        return pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            int(self.radius * 2),
            int(self.radius * 2),
        )


class Paddle:
    """半圓形底板（上方為圓弧，底部為平面）

    屬性：x(左上繪製用)、width(直徑)、radius、y(頂端座標)、color
    draw(surface, x): 在指定 x 座標繪製半圓（不改變物件內 x）
    """

    def __init__(self, x, y, width, color=(240, 240, 240)):
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.radius = int(self.width // 2)
        self.color = color

    def draw(self, surface, x=None):
        draw_x = self.x if x is None else int(x)
        cx = int(draw_x + self.width // 2)
        cy = int(self.y + self.radius)
        # 畫整個圓，再用背景色蓋掉下半部，留下上半圓
        pygame.draw.circle(surface, self.color, (cx, cy), self.radius)
        # 用背景色遮住下半圓，產生半圓效果
        bg_rect = (draw_x, cy, self.width, self.radius)
        pygame.draw.rect(surface, (0, 0, 0), bg_rect)


###################### 初始化 Pygame 與主要資源 ######################

# 初始化 Pygame（啟動所有模組）
pygame.init()

# 建立 Pygame 時鐘物件，用來在主迴圈控制 FPS
clock = pygame.time.Clock()

# 視窗尺寸設定（可依需求調整）
width = 800
height = 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("敲磚塊遊戲")
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
    ball_attached = True


# ====== 底板 (使用 Brick 表示) ======
# 底板寬度比單顆磚塊寬（例如 1.8 倍），高度可比磚塊略高或相同
paddle_width = int(brick_width * 1.8)
paddle_height = brick_height
# 固定 y 值（距離畫面底部一定距離）
paddle_y = height - 48
# 初始 x 放在畫面中央
paddle_x = (width - paddle_width) // 2
# 底板顏色（白色）
paddle_color = (240, 240, 240)
# 使用 Paddle 類別建立半圓底板物件（不加入 bricks 清單）
paddle = Paddle(x=paddle_x, y=paddle_y, width=paddle_width, color=paddle_color)

# ====== 球物件實例初始化 ======
# 初始放在底板中點上方
ball_start_x = paddle_x + paddle_width // 2
ball_start_y = paddle_y - 12
ball = Ball(x=ball_start_x, y=ball_start_y, radius=10, vx=0, vy=0, color=(255, 200, 60))
# 球是否附著在底板（等待空白鍵發射）
ball_attached = True
# 操作守則顯示旗標（預設關閉，按 Q 可以切換）
show_instructions = False


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
        # 滑鼠按鍵處理：右鍵按下時若球附著則發射
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # 參考 Pygame 的按鍵編號：1=左鍵, 2=中鍵, 3=右鍵
            if event.button == 3:
                if "ball_attached" in globals() and ball_attached:
                    ball_attached = False
                    # 與空白鍵相同的發射行為：左右隨機、向上
                    ball.vx = 5 * (1 if random.random() < 0.5 else -1)
                    ball.vy = -5
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
            # 按 Q 顯示/隱藏操作守則
            elif event.key == pygame.K_q:
                show_instructions = not show_instructions
            # 按 ESC 離開遊戲
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    # 清除畫面（背景填色）。由於磚塊之間使用 gap 顯示背景，
    # 因此背景顏色也會當作方塊間的間隔顏色。
    screen.fill((0, 0, 0))  # 使用黑色背景

    # 在左上角顯示方塊剩餘數量（不包含已被擊中的磚塊）
    remaining = sum(1 for b in bricks if not b.hit)
    count_text = f"{remaining}"
    text_surf = font.render(count_text, True, (255, 255, 255))
    screen.blit(text_surf, (8, 8))

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
    # 限制底板不超出畫面
    if paddle_draw_x < 0:
        paddle_draw_x = 0
    elif paddle_draw_x > width - paddle.width:
        paddle_draw_x = width - paddle.width
    # 使用 Paddle.draw 的參數 x 來繪製移動中的半圓底板（不修改物件本身座標）
    paddle.draw(screen, x=paddle_draw_x)

    # 若球附著在底板上，讓球跟隨底板位置並跳過物理更新，等待空白鍵發射
    if "ball_attached" in globals() and ball_attached:
        ball.x = paddle_draw_x + paddle.width // 2
        ball.y = paddle.y - 12
        ball.vx = 0
        ball.vy = 0
        # 繪製球與磚塊，並立即更新畫面後繼續下一循環
        ball.draw(screen)
        # 同樣在等待時也要根據剩餘磚塊數調整顏色
        total_bricks = rows * cols
        ratio = (
            sum(1 for b in bricks if not b.hit) / total_bricks
            if total_bricks > 0
            else 0
        )
        t_dark = min(max(1.0 - ratio, 0.0), 1.0)
        dark_strength = 0.9
        t_effect = t_dark * dark_strength
        for brick in bricks:
            if brick.hit:
                continue
            brick.color = lerp_color(brick.base_color, (0, 0, 0), t_effect)
            brick.draw(screen)
        pygame.display.update()
        continue

    # ===== 球的移動與碰撞處理 =====
    # 更新球的位置
    ball.x += ball.vx
    ball.y += ball.vy

    # 碰到左右牆壁
    if ball.x - ball.radius <= 0:
        ball.x = ball.radius
        ball.vx = -ball.vx
    elif ball.x + ball.radius >= width:
        ball.x = width - ball.radius
        ball.vx = -ball.vx

    # 碰到上方牆壁
    if ball.y - ball.radius <= 0:
        ball.y = ball.radius
        ball.vy = -ball.vy

    # 碰到底部（簡單處理：重置球到底板上方）
    if ball.y - ball.radius > height:
        # 重置磚牆
        reset_bricks()
        # 將球附著到底板，等待玩家按空白鍵發射
        ball_attached = True
        ball.x = paddle_draw_x + paddle.width // 2
        ball.y = paddle.y - 12
        ball.vx = 0
        ball.vy = 0

    # 球與半圓底板碰撞（圓形幾何 + 向量反射）
    # 計算半圓圓心：
    cx = paddle_draw_x + paddle.width // 2
    cy = paddle.y + paddle.radius
    # 只在球向下（vy>0）時判斷碰撞
    if ball.vy > 0:
        nx = ball.x - cx
        ny = ball.y - cy
        dist = math.hypot(nx, ny)
        # 只有當球位於半圓上方（y <= cy）或接近邊界時才視為有效碰撞
        if dist <= (paddle.radius + ball.radius) and ball.y <= cy + 1:
            # 法向量（從圓心指向球心）
            if dist == 0:
                n_x, n_y = 0.0, -1.0
            else:
                n_x, n_y = nx / dist, ny / dist
            # 投影並反射速度向量
            v_dot_n = ball.vx * n_x + ball.vy * n_y
            ball.vx = ball.vx - 2 * v_dot_n * n_x
            ball.vy = ball.vy - 2 * v_dot_n * n_y
            # 將球微幅推離以避免穿透
            overlap = paddle.radius + ball.radius - dist
            if overlap > 0:
                ball.x += n_x * overlap
                ball.y += n_y * overlap

    # 球與磚塊碰撞：檢查每個磚塊是否碰撞，若碰撞則將磚塊設為 hit 並反轉球的 vy
    for brick in bricks:
        if brick.hit:
            continue
        if ball.rect().colliderect(
            pygame.Rect(brick.x, brick.y, brick.width, brick.height)
        ):
            brick.hit = True
            # 簡單根據球心與磚塊中心判定反彈方向
            if abs((brick.x + brick.width / 2) - ball.x) > abs(
                (brick.y + brick.height / 2) - ball.y
            ):
                ball.vx = -ball.vx
            else:
                ball.vy = -ball.vy
            break

    # 繪製球
    ball.draw(screen)

    # 繪製所有磚塊：若某個 Brick 的 .hit 為 True，draw() 會跳過它
    # 動態調整磚塊顏色：當剩餘磚塊越少，磚塊顏色越接近黑色（變暗）
    total_bricks = rows * cols
    # ratio = 剩餘 / 總數；當 ratio 越小 -> t 越大（越暗）
    ratio = remaining / total_bricks if total_bricks > 0 else 0
    # 轉換為插值參數 t，range 0.0 (所有磚) 到 1.0 (沒磚)
    t_dark = min(max(1.0 - ratio, 0.0), 1.0)
    # 可以調整 dark_strength 來控制變暗的程度（0.0 不變，1.0 完全黑）
    dark_strength = 0.9

    for brick in bricks:
        if brick.hit:
            continue
        # 將 base_color 線性插值到黑色
        # 使用 t_effect = t_dark * dark_strength 來微調強度
        t_effect = t_dark * dark_strength
        brick.color = lerp_color(brick.base_color, (0, 0, 0), t_effect)
        brick.draw(screen)

    # 操作守則功能已移除

    # 更新整個顯示畫面。可改為 pygame.display.flip()，兩者功能相近。
    pygame.display.update()
