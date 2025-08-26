"""
遊戲實體類別定義
包含 Brick、Ball、Paddle 等遊戲物件
"""
import pygame
import math
import random
from typing import Tuple


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