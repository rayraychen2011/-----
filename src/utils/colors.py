######################載入套件######################
"""
顏色處理相關工具函數\n
\n
此模組提供各種顏色計算與處理功能，包括：\n
- 顏色線性插值與混合\n
- 對比度調整\n
- 互補色計算\n
- 隨機顏色產生\n
- 漸層顏色生成\n
- 磚塊顏色應用\n
\n
使用 RGB 與 HSV 色彩空間進行計算，支援複雜的顏色變換效果。\n
"""
import random
import colorsys
from typing import Tuple, List

######################基本顏色運算函式######################

def lerp(a: int, b: int, t: float) -> int:
    """
    線性插值計算 - 在兩個數值之間進行平滑過渡\n
    \n
    參數:\n
    a (int): 起始數值，範圍通常 0-255\n
    b (int): 結束數值，範圍通常 0-255\n
    t (float): 插值係數，範圍 0.0-1.0，0.0 回傳 a，1.0 回傳 b\n
    \n
    回傳:\n
    int: 插值結果，會四捨五入為整數\n
    \n
    計算公式:\n
    result = a + (b - a) * t\n
    """
    # 用簡單的數學公式算出兩個數字之間的中間值
    return int(a + (b - a) * t)


def lerp_color(
    c1: Tuple[int, int, int], c2: Tuple[int, int, int], t: float
) -> Tuple[int, int, int]:
    """
    顏色線性插值 - 在兩個顏色之間平滑混合\n
    \n
    參數:\n
    c1 (tuple): 起始顏色 (R, G, B)，每個分量 0-255\n
    c2 (tuple): 結束顏色 (R, G, B)，每個分量 0-255\n
    t (float): 混合係數，0.0 為純 c1，1.0 為純 c2\n
    \n
    回傳:\n
    tuple: 混合後的顏色 (R, G, B)\n
    \n
    使用範例:\n
    紅色 = (255, 0, 0)\n
    藍色 = (0, 0, 255)\n
    紫色 = lerp_color(紅色, 藍色, 0.5)  # 結果約為 (128, 0, 128)\n
    """
    # 分別對 R、G、B 三個顏色分量做插值計算
    return (lerp(c1[0], c2[0], t), lerp(c1[1], c2[1], t), lerp(c1[2], c2[2], t))

######################顏色特效函式######################

def increase_contrast(
    color: Tuple[int, int, int], t: float, strength: float = 0.9
) -> Tuple[int, int, int]:
    """
    增加顏色對比度 - 讓顏色更鮮明突出\n
    \n
    此函數以中灰色 (128, 128, 128) 為中心點，將顏色推向更極端的值。\n
    亮的顏色會變得更亮，暗的顏色會變得更暗。\n
    \n
    參數:\n
    color (tuple): 原始顏色 (R, G, B)，每個分量 0-255\n
    t (float): 對比度強度係數，0.0-1.0，越大對比越強\n
    strength (float): 最大對比度倍數，預設 0.9\n
    \n
    回傳:\n
    tuple: 調整對比度後的顏色 (R, G, B)\n
    \n
    數學原理:\n
    以 128 為中心點，如果顏色分量大於 128 就往 255 推，\n
    小於 128 就往 0 推，推的程度由 t 和 strength 決定。\n
    """

    def clamp(v: float) -> int:
        # 確保顏色值在 0-255 範圍內，超出範圍就修正回來
        return max(0, min(255, int(round(v))))

    # 計算要加強多少對比度
    factor = 1.0 + float(t) * float(strength)
    
    # 對每個顏色分量進行對比度調整
    # 128 是灰色的中心點，距離這個中心越遠，調整幅度越大
    r = clamp(128 + (color[0] - 128) * factor)
    g = clamp(128 + (color[1] - 128) * factor)
    b = clamp(128 + (color[2] - 128) * factor)
    return (r, g, b)


def shift_towards_complement(
    color: Tuple[int, int, int], t: float, strength: float = 0.9
) -> Tuple[int, int, int]:
    """
    顏色朝互補色偏移 - 創造色彩對比效果\n
    \n
    互補色是色環上相對 180 度的顏色，例如紅色的互補色是青色。\n
    此函數計算原色的互補色，然後在兩者之間進行混合。\n
    \n
    參數:\n
    color (tuple): 原始顏色 (R, G, B)，每個分量 0-255\n
    t (float): 偏移強度係數，0.0-1.0，0.0 為原色，1.0 為完全互補色\n
    strength (float): 最大偏移倍數，預設 0.9\n
    \n
    回傳:\n
    tuple: 偏移後的顏色 (R, G, B)\n
    \n
    色彩理論:\n
    使用 HSV 色彩空間計算互補色，將色相 (Hue) 加上 0.5 (180度)，\n
    保持原本的飽和度 (Saturation) 與明度 (Value) 不變。\n
    """
    # 限制 t 的範圍，避免計算錯誤
    tt = min(max(float(t) * float(strength), 0.0), 1.0)

    # 將 RGB (0-255) 轉換成 HSV (0.0-1.0) 來方便計算互補色
    r_f = color[0] / 255.0
    g_f = color[1] / 255.0
    b_f = color[2] / 255.0
    try:
        h, s, v = colorsys.rgb_to_hsv(r_f, g_f, b_f)
    except Exception:
        # 如果顏色轉換出問題，就直接回傳原來的顏色
        return color

    # 計算互補色：色相加上 0.5 (相當於 180 度)
    comp_h = (h + 0.5) % 1.0  # 用 % 1.0 確保在 0-1 範圍內
    
    # 將互補色的 HSV 轉回 RGB
    cr_f, cg_f, cb_f = colorsys.hsv_to_rgb(comp_h, s, v)
    comp_color = (
        int(round(cr_f * 255)),
        int(round(cg_f * 255)),
        int(round(cb_f * 255)),
    )

    # 在原色和互補色之間做混合
    return lerp_color(color, comp_color, tt)

######################隨機顏色產生######################

def random_color(min_v: int = 30, max_v: int = 225) -> Tuple[int, int, int]:
    """
    產生隨機顏色 - 避免過暗或過亮的極端值\n
    \n
    參數:\n
    min_v (int): 各顏色分量的最小值，預設 30 (避免太暗)\n
    max_v (int): 各顏色分量的最大值，預設 225 (避免太亮)\n
    \n
    回傳:\n
    tuple: 隨機產生的顏色 (R, G, B)\n
    \n
    設計考量:\n
    避免純黑 (0,0,0) 和純白 (255,255,255)，\n
    確保產生的顏色有足夠的視覺對比度。\n
    """
    # 為每個顏色分量 (R, G, B) 分別產生隨機數值
    return (
        random.randint(min_v, max_v),
        random.randint(min_v, max_v),
        random.randint(min_v, max_v),
    )

######################漸層顏色系統######################

def generate_gradient_brick_colors(
    rows: int, 
    cols: int, 
    start_color: Tuple[int, int, int], 
    end_color: Tuple[int, int, int], 
    direction: str = "horizontal"
) -> List[Tuple[int, int, int]]:
    """
    產生磚塊漸層顏色陣列 - 依據方向建立平滑的顏色過渡\n
    \n
    參數:\n
    rows (int): 磚塊牆的行數，範圍 > 0\n
    cols (int): 磚塊牆的列數，範圍 > 0\n
    start_color (tuple): 漸層起始顏色 (R, G, B)\n
    end_color (tuple): 漸層結束顏色 (R, G, B)\n
    direction (str): 漸層方向，可選 'horizontal'/'vertical'/'diagonal'\n
    \n
    回傳:\n
    list: 依序對應每個磚塊位置的顏色清單\n
    \n
    漸層計算方式:\n
    - horizontal: 從左到右的水平漸層\n
    - vertical: 從上到下的垂直漸層\n
    - diagonal: 對角線漸層（左上到右下）\n
    \n
    特殊處理:\n
    加入微小的隨機擾動避免漸層過於規律單調。\n
    """
    colors = []
    # 逐行逐列計算每個磚塊的顏色
    for r in range(rows):
        for c in range(cols):
            # 根據漸層方向計算插值係數 t
            if direction == "horizontal":
                # 水平漸層：從左到右，列數決定顏色
                denom = max(cols - 1, 1)  # 避免除以零
                t = c / denom
            elif direction == "vertical":
                # 垂直漸層：從上到下，行數決定顏色
                denom = max(rows - 1, 1)
                t = r / denom
            else:  # diagonal
                # 對角線漸層：行數和列數都有影響
                denom_r = max(rows - 1, 1)
                denom_c = max(cols - 1, 1)
                t = (r / denom_r + c / denom_c) / 2

            # 加入一點小隨機性讓漸層看起來更自然，不會太死板
            jitter = random.uniform(-0.03, 0.03)
            t = min(max(t + jitter, 0.0), 1.0)  # 確保 t 在 0-1 範圍內
            
            # 計算這個位置的顏色並加入清單
            colors.append(lerp_color(start_color, end_color, t))
    return colors


def apply_gradient_to_bricks(
    bricks_list: List, 
    rows: int, 
    cols: int, 
    start_color: Tuple[int, int, int], 
    end_color: Tuple[int, int, int], 
    direction: str = "horizontal"
):
    """
    將漸層顏色套用到磚塊清單 - 更新每個磚塊的顏色屬性\n
    \n
    參數:\n
    bricks_list (list): 磚塊物件清單，每個物件需有 base_color 和 color 屬性\n
    rows (int): 磚塊牆的行數\n
    cols (int): 磚塊牆的列數\n
    start_color (tuple): 漸層起始顏色 (R, G, B)\n
    end_color (tuple): 漸層結束顏色 (R, G, B)\n
    direction (str): 漸層方向\n
    \n
    功能說明:\n
    1. 產生對應的漸層顏色陣列\n
    2. 將每個顏色指派給對應位置的磚塊\n
    3. 同時設定 base_color (原始色) 和 color (顯示色)\n
    \n
    磚塊顏色系統:\n
    - base_color: 儲存原始漸層顏色，不會動態改變\n
    - color: 實際繪製用顏色，可能會有動態效果調整\n
    """
    # 先產生對應的漸層顏色陣列
    gradient = generate_gradient_brick_colors(
        rows, cols, start_color, end_color, direction
    )
    
    # 將顏色逐一指派給每個磚塊
    for idx, brick in enumerate(bricks_list):
        # 保存原始漸層色為 base_color，這個不會被動態效果改變
        brick.base_color = gradient[idx]
        # 設定當前顯示色為相同，這個可能會被特效系統調整
        brick.color = gradient[idx]