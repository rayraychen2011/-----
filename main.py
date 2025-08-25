###################### 載入套件與模組 ######################
import pygame
import sys
import random
from typing import Tuple

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
# 使用 None 代表預設字型，大小 28
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
# 使用 Brick 類別建立底板物件（不加入 bricks 清單）
paddle = Brick(
    x=paddle_x, y=paddle_y, width=paddle_width, height=paddle_height, color=paddle_color
)

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
    count_text = f"方塊剩餘: {remaining}"
    text_surf = font.render(count_text, True, (255, 255, 255))
    screen.blit(text_surf, (8, 8))

    # 更新並繪製底板：讓底板的中心跟隨滑鼠的 x 座標，y 固定
    mouse_x, _ = pygame.mouse.get_pos()
    # 將滑鼠 x 轉換成底板左上角 x（讓滑鼠位於底板中點）
    paddle_draw_x = int(mouse_x - paddle.width / 2)
    # 限制底板不超出畫面
    if paddle_draw_x < 0:
        paddle_draw_x = 0
    elif paddle_draw_x > width - paddle.width:
        paddle_draw_x = width - paddle.width
    # 使用 Brick.draw 的參數 x,y 來繪製移動中的底板（不修改物件本身座標）
    paddle.draw(screen, x=paddle_draw_x, y=paddle.y)

    # 若球附著在底板上，讓球跟隨底板位置並跳過物理更新，等待空白鍵發射
    if "ball_attached" in globals() and ball_attached:
        ball.x = paddle_draw_x + paddle.width // 2
        ball.y = paddle.y - 12
        ball.vx = 0
        ball.vy = 0
        # 繪製球與磚塊，並立即更新畫面後繼續下一循環
        ball.draw(screen)
        for brick in bricks:
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

    # 球與底板碰撞（使用矩形近似）
    if (
        ball.rect().colliderect(
            pygame.Rect(paddle_draw_x, paddle.y, paddle.width, paddle.height)
        )
        and ball.vy > 0
    ):
        # 反轉 y 方向
        ball.vy = -abs(ball.vy)
        # 根據碰撞位置稍微改變 vx（讓反彈有角度）
        offset = (ball.x - (paddle_draw_x + paddle.width / 2)) / (paddle.width / 2)
        ball.vx += offset * 2

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
    for brick in bricks:
        brick.draw(screen)

    # 操作守則功能已移除

    # 更新整個顯示畫面。可改為 pygame.display.flip()，兩者功能相近。
    pygame.display.update()
