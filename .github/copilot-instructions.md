# 敲磚塊遊戲 - AI 助手指引

## 專案架構概述

這是一個基於 Pygame 的進階敲磚塊遊戲，採用模組化架構分離關注點：

- **主控制器**: `src/game/game_logic.py` - 遊戲狀態管理、事件處理與主循環
- **物理引擎**: `src/game/physics.py` - 碰撞檢測、軌跡預測與反射計算
- **遊戲實體**: `src/game/entities.py` - Ball、Brick、Paddle 物件定義
- **視覺效果**: `src/game/graphics.py` - 粒子系統、特效渲染與 UI 繪製
- **工具模組**: `src/utils/` - 顏色處理 (`colors.py`) 與音效管理 (`audio.py`)
- **設定檔**: `src/config/settings.py` - 集中式參數配置

## 核心設計模式

### 物件導向實體系統

每個遊戲物件繼承基本繪製介面，支援位置覆寫：

```python
brick.draw(surface, x=alt_x, y=alt_y)  # 臨時位置繪製
paddle.draw(surface, x=mouse_x)        # 動態位置更新
```

### 狀態管理模式

遊戲狀態透過布林旗標與數值狀態管理：

- `ball_attached`: 球是否附著在底板
- `paddle_auto_mode`: 自動底板模式
- `ball_boost_active`: 球加速狀態
- `show_physics/show_instructions`: UI 顯示狀態

### 分離的物理與視覺

物理計算與視覺效果完全分離，允許複雜特效而不影響遊戲邏輯。

## 關鍵技術實現

### 馬蹄鐵底板碰撞

底板採用複合幾何體（兩個矩形 + 一個半圓），碰撞檢測使用點到幾何體最近距離算法：

```python
# 矩形碰撞：找最近點
closest_x = max(rect.left, min(ball.x, rect.right))
# 圓形碰撞：中心距離檢查
distc = math.hypot(ball.x - cx, ball.y - cy)
```

### 軌跡預測系統

使用步進模擬 (`physics.py:predict_trajectory`) 預測球的未來路徑，支援：

- 多次反彈模擬 (`max_bounces`)
- 可調精度 (`step` 參數)
- 延遲顯示 (`delay_s`)

### 動態顏色系統

磚塊顏色採用基底色 + 動態變化模式：

- `base_color`: 原始漸層顏色
- `color`: 每幀動態計算的顯示顏色
- 使用 HSV 色彩空間進行互補色轉換

### 粒子效果系統

每個粒子為字典結構，包含物理狀態與視覺屬性：

```python
particle = {
    "x": float, "y": float, "vx": float, "vy": float,
    "r": int, "color": tuple, "start": int, "life": int
}
```

## 開發工作流程

### 執行與測試

```bash
python main.py                    # 執行遊戲
python tools/generate_bell.py     # 生成音效檔案
```

### 關鍵除錯按鍵

- `R`: 重新隨機化磚塊漸層
- `G`: 顯示漸層參數（console 輸出）
- `Q`: 切換操作說明顯示
- 中鍵: 切換物理面板顯示

### 常見修改模式

**調整遊戲參數**: 修改 `src/config/settings.py` 中的常數
**新增特效**: 在 `graphics.py` 中創建新的粒子生成函數
**修改物理**: 編輯 `physics.py` 中的碰撞檢測或反射邏輯
**新增遊戲物件**: 在 `entities.py` 中定義新類別，遵循現有 `draw()` 介面

### 特殊磚塊系統

特殊磚塊透過 `is_special` 屬性標記，擊中時觸發：

- 3x3 區域清除 (使用網格索引計算)
- 球體暫時放大效果
- 爆炸音效與增強粒子效果

## 檔案路徑慣例

- 資源檔案使用 `settings.py` 中的絕對路徑
- 音效檔案支援 `.wav` 與 `.mp3` 格式
- 圖片載入包含異常處理回退機制

## 效能考量

- 粒子系統使用單一 Surface 減少 blit 呼叫
- 磚塊碰撞使用預建 Rect 快取
- 軌跡預測有最大迭代限制避免無限迴圈

修改時請保持模組間的清晰界線，特別是物理計算與視覺效果的分離。
