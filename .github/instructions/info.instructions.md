---
applyTo: "**"
---

# 程式碼開發風格指南

## 開發流程

- 需要先使用 #todos 工具來進行規劃，規劃完成才能開始撰寫程式碼。

## 程式碼風格規範

### 命名規則

- **變數名稱**：使用小寫字母配合底線分隔（snake_case）
  - 例如：`bg_x`, `bg_y`, `ball_radius`, `bricks_row`
- **類別名稱**：使用駝峰式命名（PascalCase）
  - 例如：`Brick`, `Ball`
- **函數名稱**：使用小寫字母配合底線分隔（snake_case）
  - 例如：`check_collision`, `draw`, `move`
- **常數**：使用全大寫字母配合底線分隔
  - 例如：`FPS`

### 註解風格

- **區塊註解**：使用 `######################` 作為區塊分隔符

  - 例如：`######################載入套件######################`

- **文檔字串**：使用三引號（`"""`）撰寫類別和函數說明

  - **必須包含**：功能描述、參數說明、回傳值說明、使用範例（複雜函數）
  - 函數參數使用 `\n` 進行換行說明，包含參數類型和有效範圍
  - 格式範例：

  ```python
  def check_collisions(self, screen_width, screen_height, paddle, bricks):
      """
      統一的碰撞偵測方法 - 處理球與各種物件的碰撞\n
      \n
      此方法按順序檢查：\n
      1. 牆壁碰撞（左右上邊界）\n
      2. 底板碰撞（包含角度調整算法）\n
      3. 磚塊碰撞（每次只處理一個，避免重複計分）\n
      \n
      參數:\n
      screen_width (int): 螢幕寬度，範圍 > 0\n
      screen_height (int): 螢幕高度，範圍 > 0\n
      paddle (Paddle): 底板物件，包含位置和尺寸資訊\n
      bricks (list): 磚塊陣列，包含所有未被擊中的磚塊\n
      \n
      回傳:\n
      dict: {\n
          'game_over': bool - 是否觸發遊戲結束（球掉到底部）\n
          'bricks_hit': int - 本次碰撞擊中的磚塊數量（0或1）\n
      }\n
      \n
      算法說明:\n
      - 底板碰撞角度調整：根據撞擊位置計算反彈角度\n
      - 磚塊碰撞方向判斷：比較 dx、dy 決定水平或垂直反彈\n
      - 速度限制：防止球速過快或過慢影響遊戲體驗\n
      """
  ```

- **行內註解**：使用 `#` 符號，內容使用繁體中文

  - **註解用詞原則**：使用簡單易懂的白話文，避免過於技術性的術語
  - **重要步驟**：每個關鍵動作都要用簡單的話說明在做什麼
  - **數字計算**：用日常用語解釋為什麼要這樣算，而不是複雜的數學術語
  - **條件判斷**：用「如果...就...」的方式說明判斷的原因
  - **重複動作**：說明「要重複做什麼事」和「什麼時候停止」
  - 範例：

  ```python
  # 算出球打到底板的哪個位置（-1 是最左邊，1 是最右邊）
  hit_pos = (self.x - (paddle.x + paddle.width / 2)) / (paddle.width / 2)

  # 根據撞到的位置改變球的左右速度，撞到邊邊會彈得比較斜
  self.velocity_x += hit_pos * 3.5

  # 不讓球跑太快，免得玩家跟不上
  self.velocity_x = max(-10, min(10, self.velocity_x))

  # 球如果左右移動太慢會變成垂直彈跳，很無聊，所以給它最小速度
  if abs(self.velocity_x) < 1.5:
      self.velocity_x = 1.5 if self.velocity_x >= 0 else -1.5
  ```

- **異常處理註解**：詳細說明錯誤處理邏輯

  ```python
  try:
      # 試著載入球的圖片檔案
      ball_image = pygame.image.load(BALL_IMAGE_PATH).convert_alpha()
      ball_image = pygame.transform.scale(ball_image, BALL_IMAGE_SIZE)
      return ball_image
  except pygame.error as e:
      # 如果圖片檔案壞了或找不到，就畫一個簡單的圓形代替
      print(f"載入球圖片失敗: {e}")
      # 創建一個圓形，這樣遊戲還是可以玩
      ball_surface = pygame.Surface(BALL_IMAGE_SIZE, pygame.SRCALPHA)
      pygame.draw.circle(ball_surface, BALL_COLOR, center, BALL_RADIUS)
      return ball_surface
  ```

- **所有註解**：統一使用繁體中文撰寫

### 程式結構

- **區塊組織**：使用明確的區塊分段，包含：
  - 載入套件
  - 物件類別
  - 定義函式區
  - 初始化設定
  - 主程式
- **縮排**：統一使用 4 個空格進行縮排
- **空行**：適當使用空行分隔不同功能區塊
- **主程式執行**：任何模組都不需要使用 `if __name__ == "__main__":` 慣例，直接呼叫 `main()` 函數即可

### 類別設計

- 類別方法應包含清楚的參數說明
- 使用 `self` 作為實例方法的第一個參數
- 類別屬性初始化應在 `__init__` 方法中完成

### 變數使用

- 允許使用全域變數（如 `score`），但應謹慎使用
- 變數名稱應具有描述性，清楚表達其用途
- 布林值變數使用 `is_` 前綴（如 `is_moving`）

### 程式碼品質

- 保持程式邏輯清晰，適當分段
- 函數應具有單一職責
- 避免行末多餘空格
- 使用有意義的變數和函數名稱

### 詳細註解要求

#### 函數和方法註解

- **所有 public 方法**：必須包含完整的文檔字串
- **複雜邏輯函數**：需要詳細說明算法步驟和數學公式
- **參數驗證**：說明參數的有效範圍和邊界條件
- **副作用說明**：如果函數會修改物件狀態或全域變數，必須註解說明

#### 業務邏輯註解

- **條件分支**：每個 if-else 都要用簡單的話說明為什麼要這樣判斷
- **迴圈邏輯**：說明「要重複做什麼事」、「什麼時候停止」和「想要達成什麼目標」
- **數值計算**：用日常用語解釋為什麼要這樣算，避免複雜的數學術語
- **狀態變更**：物件狀態改變時用簡單的話說明原因和會產生什麼影響

#### 特殊情況註解

- **錯誤處理**：用簡單的話說明可能出什麼錯、怎麼處理
- **性能考量**：如果程式碼有特殊寫法是為了跑得更快，要解釋為什麼
- **相依性說明**：如果程式碼需要按照特定順序執行，要說明原因
- **TODO 和 FIXME**：還沒做完或需要改進的地方要清楚標記

#### 類別設計註解

- **類別職責**：用簡單的話說明這個類別是用來做什麼的
- **屬性說明**：重要屬性要說明用途和可能的數值範圍
- **方法分組**：把相關的方法用註解分組，像是「畫圖用的方法」、「移動用的方法」
- **設計模式**：如果用了特別的設計方法，要用簡單的話解釋

#### 範例：完整註解的函數

```python
def calculate_ball_bounce_angle(self, collision_object, collision_point):
    """
    計算球碰撞後的反彈角度 - 物理引擎核心算法\n
    \n
    此方法實現彈性碰撞的物理計算，考慮：\n
    1. 入射角度和法線向量\n
    2. 物體表面的摩擦係數\n
    3. 能量損失和速度衰減\n
    \n
    參數:\n
    collision_object (GameObject): 碰撞目標物件，必須有 surface_normal 屬性\n
    collision_point (tuple): 碰撞點座標 (x, y)，座標系原點為螢幕左上角\n
    \n
    回傳:\n
    tuple: (new_velocity_x, new_velocity_y) 新的速度向量\n
    \n
    物理公式:\n
    - 反射向量 = 入射向量 - 2 * (入射向量 · 法線) * 法線\n
    - 摩擦力 = μ * 法向力 * 接觸時間\n
    - 能量損失 = 0.95 * 原始動能（模擬非完全彈性碰撞）\n
    \n
    異常情況:\n
    - 如果碰撞物件無 surface_normal 屬性，使用預設垂直法線\n
    - 速度過小時設定最小值，避免球靜止\n
    """
    try:
        # 獲取碰撞物件的表面法線向量，預設為垂直向上
        normal = getattr(collision_object, 'surface_normal', (0, -1))

        # 計算入射角度（當前速度向量與法線的夾角）
        incident_angle = math.atan2(self.velocity_y, self.velocity_x)

        # 計算法線角度
        normal_angle = math.atan2(normal[1], normal[0])

        # 應用反射定律：出射角 = 入射角（相對於法線）
        reflection_angle = 2 * normal_angle - incident_angle

        # 計算碰撞前的速率（用於能量損失計算）
        speed = math.sqrt(self.velocity_x**2 + self.velocity_y**2)

        # 應用能量損失係數（模擬非完全彈性碰撞）
        energy_retention = 0.95
        new_speed = speed * energy_retention

        # 計算新的速度分量
        new_velocity_x = new_speed * math.cos(reflection_angle)
        new_velocity_y = new_speed * math.sin(reflection_angle)

        # 防止速度過小導致球停止移動
        min_speed = 2.0
        if new_speed < min_speed:
            # 保持方向，但提升到最小速度
            scale_factor = min_speed / new_speed
            new_velocity_x *= scale_factor
            new_velocity_y *= scale_factor

        return (new_velocity_x, new_velocity_y)

    except (AttributeError, ZeroDivisionError) as e:
        # 碰撞計算失敗時的降級處理：簡單速度反轉
        print(f"碰撞角度計算失敗，使用簡化處理: {e}")
        return (-self.velocity_x * 0.9, -self.velocity_y * 0.9)
```
