######################載入套件######################
"""
遊戲實體類別定義\n
\n
此模組包含敲磚塊遊戲中所有可見物件的類別定義：\n
- Brick: 磚塊物件，可被球擊中並產生特效\n
- Ball: 球物件，具有物理運動和視覺特效\n
- Paddle: 底板物件，採用馬蹄鐵造型設計\n
\n
所有物件都遵循統一的繪製介面，支援位置覆寫功能。\n
"""
import pygame
import math
import random
from typing import Tuple

######################磚塊類別######################

class Brick:
    """
    磚塊物件 - 敲磚塊遊戲的主要目標\n
    \n
    每個磚塊代表遊戲中一個可被擊中的目標，具有以下特性：\n
    1. 位置與尺寸資訊\n
    2. 顏色管理（基底色與顯示色分離）\n
    3. 擊中狀態追蹤\n
    4. 特殊磚塊標記\n
    \n
    屬性說明:\n
    x, y (int): 磚塊左上角座標（像素）\n
    width, height (int): 磚塊的寬與高（像素）\n
    base_color (tuple): 原始漸層顏色，不受動態效果影響\n
    color (tuple): 當前顯示顏色，可能被特效系統調整\n
    hit (bool): 是否已被擊中（True 表示已消失）\n
    is_special (bool): 是否為特殊磚塊（擊中時有額外效果）\n
    """

    def __init__(self, x, y, width, height, color, hit=False):
        """
        初始化磚塊物件\n
        \n
        參數:\n
        x (int): 左上角 X 座標\n
        y (int): 左上角 Y 座標\n
        width (int): 磚塊寬度\n
        height (int): 磚塊高度\n
        color (tuple): 初始顏色 (R, G, B)\n
        hit (bool): 初始擊中狀態，預設為 False\n
        """
        # 儲存磚塊的位置與大小
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # 顏色管理：分離基底色與顯示色
        self.base_color = color    # 原始漸層色（不隨特效變化）
        self.color = color         # 實際繪製用顏色（會被動態調整）
        
        # 狀態追蹤
        self.hit = hit            # 是否被擊中（True 表示已消失）
        self.is_special = False   # 是否為特殊磚塊（撞到會有額外效果）

    def draw(self, surface, x=None, y=None):
        """
        在畫面上繪製磚塊\n
        \n
        參數:\n
        surface (pygame.Surface): 要繪製到的表面\n
        x (int, optional): 覆寫 X 座標，不改變物件本身位置\n
        y (int, optional): 覆寫 Y 座標，不改變物件本身位置\n
        \n
        繪製邏輯:\n
        1. 如果磚塊已被擊中，直接跳過繪製\n
        2. 使用提供的座標或物件本身座標\n
        3. 繪製填充矩形作為磚塊主體\n
        4. 如果是特殊磚塊，加上金色邊框標記\n
        \n
        位置覆寫功能:\n
        允許在不改變物件狀態的情況下在其他位置繪製，\n
        常用於軌跡預測或測試繪製。\n
        """
        # 已被擊中的磚塊不需要繪製
        if self.hit:
            return

        # 決定繪製位置：使用提供的座標或物件本身的座標
        draw_x = self.x if x is None else x
        draw_y = self.y if y is None else y

        # 建立矩形並繪製磚塊主體
        rect = (int(draw_x), int(draw_y), int(self.width), int(self.height))
        pygame.draw.rect(surface, self.color, rect)
        
        # 特殊磚塊加上金色邊框以示區別
        if getattr(self, "is_special", False):
            try:
                # 金色邊框，線寬 3 像素
                pygame.draw.rect(surface, (255, 215, 0), rect, 3)
            except Exception:
                # 如果邊框繪製失敗，不影響主要繪製
                pass

######################球類別######################

class Ball:
    """
    球物件 - 遊戲的核心移動元素\n
    \n
    球是遊戲中最重要的物件，具有以下特性：\n
    1. 物理運動（位置、速度）\n
    2. 視覺效果（旋轉、光暈、放大特效）\n
    3. 圖片支援（可載入圖片或使用純色圓形）\n
    4. 臨時特效（放大效果）\n
    \n
    屬性說明:\n
    x, y (float): 球心座標\n
    radius (int): 球的半徑\n
    vx, vy (float): X 和 Y 方向的速度分量\n
    color (tuple): 球的顏色（當沒有圖片時使用）\n
    image_original (Surface): 原始圖片（如果有載入）\n
    """

    def __init__(
        self, x, y, radius=10, vx=5, vy=-5, color=(255, 255, 255), image_path=None
    ):
        """
        初始化球物件\n
        \n
        參數:\n
        x, y (float): 球心初始座標\n
        radius (int): 球的半徑，預設 10\n
        vx, vy (float): 初始速度分量\n
        color (tuple): 球的顏色 (R, G, B)\n
        image_path (str): 球圖片檔案路徑，可選\n
        """
        # 基本物理屬性
        self.x = float(x)
        self.y = float(y)
        self.radius = int(radius)
        self.vx = float(vx)
        self.vy = float(vy)
        self.color = color

        # 圖片載入：如果提供路徑就嘗試載入並縮放
        self.image_original = None
        if image_path is not None:
            try:
                # 載入圖片並轉換格式以支援透明度
                img = pygame.image.load(image_path).convert_alpha()
                # 縮放到適合的尺寸（直徑大小）
                img = pygame.transform.smoothscale(
                    img, (self.radius * 2, self.radius * 2)
                )
                self.image_original = img
            except Exception as e:
                print(f"無法載入球的圖片 '{image_path}': {e}")
                self.image_original = None

        # 旋轉動畫設定
        self.rotation_period_ms = 3000  # 旋轉週期：3 秒轉 360 度
        self._rot_start = pygame.time.get_ticks()  # 旋轉起始時間
        
        # 臨時放大特效
        self._powerup_scale = 1.0      # 當前放大倍數
        self._powerup_end_time = 0     # 特效結束時間戳

    def draw(self, surface):
        """
        繪製球物件 - 包含複雜的視覺特效\n
        \n
        繪製包含以下元素：\n
        1. 藍色光暈效果（放射狀光線）\n
        2. 球本體（圖片或純色圓形）\n
        3. 旋轉動畫（如果有圖片）\n
        4. 放大特效（臨時效果）\n
        \n
        光暈設計理念：\n
        使用多層半透明圓形和放射線創造動態光暈，\n
        讓球看起來更有能量感和科幻感。\n
        """
        # 加入藍色光暈：在球底下繪製多層半透明圓做為暈染
        try:
            # 計算當前顯示半徑（考慮放大特效）
            draw_radius = int(self.radius * self._powerup_scale)
            
            # 光暈半徑比球本體大，創造發散效果
            glow_radius = max(draw_radius * 2, draw_radius + 12)
            glow_diam = glow_radius * 2
            
            # 建立專門的光暈表面，支援透明度
            glow_surf = pygame.Surface((glow_diam, glow_diam), pygame.SRCALPHA)
            
            # 基礎藍色光暈顏色
            blue = (80, 160, 255)
            
            # 取得當前時間用於動畫計算
            now = pygame.time.get_ticks()
            
            # 放射線數量與動畫相位
            rays = 18
            phase = (now % 2000) / 2000.0 * math.tau  # 2 秒一個完整相位
            cx = glow_radius  # 光暈中心 X
            cy = glow_radius  # 光暈中心 Y
            
            # 畫底層柔和圓形當作光暈基底
            try:
                pygame.draw.circle(
                    glow_surf,
                    (blue[0], blue[1], blue[2], 60),  # 淡藍色，alpha 60
                    (cx, cy),
                    int(glow_radius * 0.75),
                )
            except Exception:
                pass
            
            # 繪製放射狀光線，創造動態效果
            for i in range(rays):
                # 計算每條光線的角度，加上相位動畫
                ang = (i / rays) * math.tau + phase * 0.6
                
                # 光線長度帶有細微擾動讓效果更生動
                length = int(glow_radius * (0.9 + 0.25 * math.sin(ang * 2.3 + i)))
                
                # 基底透明度
                base_alpha = 200
                
                # 計算線寬：外層寬內層細，創造柔和邊緣
                outer_w = max(2, int(glow_radius * 0.18))
                inner_w = max(1, int(glow_radius * 0.08))
                
                # 光線終點座標
                ex = int(cx + math.cos(ang) * length)
                ey = int(cy + math.sin(ang) * length)
                
                # 繪製三層光線：外層柔和、中層半亮、內層亮點
                
                # 外層（最柔和）
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
                
                # 中層（半亮）
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
                
                # 內層（亮點）
                try:
                    pygame.draw.line(
                        glow_surf,
                        (255, 255, 255, int(base_alpha * 0.9)),  # 白色亮點
                        (
                            int(cx + math.cos(ang) * (length * 0.6)),
                            int(cy + math.sin(ang) * (length * 0.6)),
                        ),
                        (ex, ey),
                        1,
                    )
                except Exception:
                    pass
            
            # 將光暈置中到球的位置並繪製到主表面
            gx = int(self.x - glow_radius)
            gy = int(self.y - glow_radius)
            try:
                surface.blit(glow_surf, (gx, gy), special_flags=0)
            except Exception:
                pass

            # 繪製球本體
            if self.image_original is not None:
                # 如果有圖片，使用旋轉圖片繪製
                
                # 計算旋轉角度（基於時間的連續旋轉）
                elapsed = pygame.time.get_ticks() - self._rot_start
                angle = (
                    (elapsed % self.rotation_period_ms) / self.rotation_period_ms * 360
                )
                
                # 處理放大特效
                scale = self._powerup_scale
                if scale != 1.0:
                    # 如果有放大特效，先縮放圖片
                    target_size = (
                        int(self.radius * 2 * scale),
                        int(self.radius * 2 * scale),
                    )
                    img = pygame.transform.smoothscale(self.image_original, target_size)
                else:
                    img = self.image_original
                
                # 旋轉圖片（負角度讓旋轉方向符合直覺）
                rotated = pygame.transform.rotate(img, -angle)
                
                # 置中繪製旋轉後的圖片
                rect = rotated.get_rect(center=(int(self.x), int(self.y)))
                surface.blit(rotated, rect)
            else:
                # 如果沒有圖片，畫純色圓形
                pygame.draw.circle(
                    surface, self.color, (int(self.x), int(self.y)), draw_radius
                )
        except Exception:
            # 如果複雜繪製出問題，退回為簡單圓形
            try:
                pygame.draw.circle(
                    surface, self.color, (int(self.x), int(self.y)), int(self.radius)
                )
            except Exception:
                # 連簡單繪製都失敗就放棄
                pass

    def update_powerups(self):
        """
        更新特效狀態 - 檢查臨時特效是否到期\n
        \n
        此方法應該在每幀被呼叫，用來：\n
        1. 檢查放大特效是否到期\n
        2. 重置到正常狀態\n
        """
        # 檢查放大特效是否到期
        if self._powerup_end_time and pygame.time.get_ticks() >= self._powerup_end_time:
            # 重置為正常大小
            self._powerup_scale = 1.0
            self._powerup_end_time = 0

    def apply_temporary_scale(self, scale: float, duration_ms: int):
        """
        套用臨時放大效果 - 讓球暫時變大\n
        \n
        參數:\n
        scale (float): 放大倍數，1.0 為正常大小\n
        duration_ms (int): 持續時間（毫秒）\n
        \n
        用途:\n
        特殊磚塊被擊中時，球會暫時放大增加擊中範圍。\n
        """
        self._powerup_scale = float(scale)
        self._powerup_end_time = pygame.time.get_ticks() + int(duration_ms)

    def rect(self):
        """
        取得球的碰撞矩形 - 用於碰撞檢測\n
        \n
        回傳:\n
        pygame.Rect: 包圍球的矩形，左上角為 (x-radius, y-radius)\n
        """
        return pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            int(self.radius * 2),
            int(self.radius * 2),
        )

######################底板類別######################

class Paddle:
    """
    馬蹄鐵底板 - 創新的 U 形底板設計\n
    \n
    不同於傳統的矩形底板，此底板採用馬蹄鐵造型：\n
    - 左右兩根垂直支柱\n
    - 底部半圓連接\n
    - 開口朝上面向磚塊\n
    \n
    設計優勢:\n
    1. 提供更有趣的反彈角度\n
    2. 增加遊戲的技巧性\n
    3. 視覺上更具特色\n
    \n
    屬性說明:\n
    x, y (int): 底板左上角座標\n
    width (int): 整體外徑寬度（外圓直徑）\n
    height (int): 支柱高度（從頂端到半圓頂端）\n
    color (tuple): 底板顏色\n
    """

    def __init__(self, x, y, width, height=None, color=(240, 240, 240)):
        """
        初始化馬蹄鐵底板\n
        \n
        參數:\n
        x, y (int): 底板左上角座標\n
        width (int): 整體寬度\n
        height (int): 支柱高度，若未提供則自動計算為寬度的四分之一\n
        color (tuple): 底板顏色，預設為淺灰色\n
        """
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        # 支柱高度：若未提供，預設為寬度的四分之一，最小 8 像素
        self.height = (
            int(height) if height is not None else max(8, int(self.width // 4))
        )
        self.color = color

    def draw(self, surface, x=None):
        """
        繪製馬蹄鐵底板 - 複合幾何圖形繪製\n
        \n
        參數:\n
        surface (pygame.Surface): 繪製目標表面\n
        x (int, optional): 覆寫 X 座標，不改變物件本身位置\n
        \n
        繪製結構:\n
        1. 左側支柱矩形\n
        2. 右側支柱矩形\n
        3. 底部半圓\n
        4. 金色內部填充\n
        5. 黑色邊框描邊\n
        \n
        顏色方案:\n
        - 內部：金黃色填充\n
        - 邊緣：黑色描邊\n
        """
        # 決定繪製位置
        draw_x = self.x if x is None else int(x)
        
        # 計算幾何參數
        outer_r = float(self.width) / 2.0     # 外圓半徑
        leg_h = float(self.height)            # 支柱高度
        thickness = max(8, int(self.width * 0.18))  # 支柱厚度
        total_h = int(leg_h + outer_r * 2.0)  # 總高度

        # 建立透明表面方便繪製複合圖形
        surf = pygame.Surface((int(self.width), total_h), pygame.SRCALPHA)

        # 顏色設定
        inner_color = self.color if self.color is not None else (255, 220, 60)  # 金黃色
        edge_color = (0, 0, 0)  # 黑色邊緣
        outline_w = max(3, int(thickness * 0.5))  # 邊框寬度
        
        try:
            # 繪製內部填充（金黃色）
            
            # 左支柱
            pygame.draw.rect(surf, inner_color, (0, 0, thickness, total_h))
            # 右支柱
            pygame.draw.rect(
                surf, inner_color, (int(self.width) - thickness, 0, thickness, total_h)
            )
            # 底部半圓
            center = (int(self.width / 2), int(leg_h + outer_r))
            pygame.draw.circle(surf, inner_color, center, int(outer_r))
            
            # 繪製黑色邊緣（描邊）
            try:
                # 左支柱邊框
                pygame.draw.rect(
                    surf, edge_color, (0, 0, thickness, total_h), outline_w
                )
                # 右支柱邊框
                pygame.draw.rect(
                    surf,
                    edge_color,
                    (int(self.width) - thickness, 0, thickness, total_h),
                    outline_w,
                )
            except Exception:
                # 邊框繪製失敗不影響主體
                pass
            
            try:
                # 半圓邊框
                pygame.draw.circle(surf, edge_color, center, int(outer_r), outline_w)
            except Exception:
                pass
                
        except Exception:
            # 如果複雜繪製失敗，退回為簡單矩形底板
            try:
                pygame.draw.rect(surf, inner_color, (0, 0, int(self.width), total_h))
                pygame.draw.rect(
                    surf, edge_color, (0, 0, int(self.width), total_h), outline_w
                )
            except Exception:
                # 連簡單繪製都失敗就放棄
                pass

        # 將繪製好的底板貼到主表面
        surface.blit(surf, (draw_x, self.y))