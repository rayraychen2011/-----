"""
顏色處理相關工具函數
"""
import random
import colorsys
from typing import Tuple, List


def lerp(a: int, b: int, t: float) -> int:
    """線性插值"""
    return int(a + (b - a) * t)


def lerp_color(
    c1: Tuple[int, int, int], c2: Tuple[int, int, int], t: float
) -> Tuple[int, int, int]:
    """顏色線性插值"""
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


def random_color(min_v: int = 30, max_v: int = 225) -> Tuple[int, int, int]:
    """生成隨機顏色"""
    return (
        random.randint(min_v, max_v),
        random.randint(min_v, max_v),
        random.randint(min_v, max_v),
    )


def generate_gradient_brick_colors(
    rows: int, 
    cols: int, 
    start_color: Tuple[int, int, int], 
    end_color: Tuple[int, int, int], 
    direction: str = "horizontal"
) -> List[Tuple[int, int, int]]:
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
    bricks_list: List, 
    rows: int, 
    cols: int, 
    start_color: Tuple[int, int, int], 
    end_color: Tuple[int, int, int], 
    direction: str = "horizontal"
):
    """將漸層顏色應用到磚塊清單"""
    gradient = generate_gradient_brick_colors(
        rows, cols, start_color, end_color, direction
    )
    for idx, brick in enumerate(bricks_list):
        # 保存原始漸層色為 base_color，並將當前繪製色設為相同
        brick.base_color = gradient[idx]
        brick.color = gradient[idx]