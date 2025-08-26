"""
圖形渲染和特效處理
"""
import pygame
import math
import random
from typing import List, Tuple, Dict, Any


def spawn_particles(
    x: float, 
    y: float, 
    count: int = 12, 
    color: Tuple[int, int, int] = (255, 200, 60), 
    speed: float = 4.0, 
    spread: float = 0.8, 
    life: int = 600
) -> List[Dict[str, Any]]:
    """在 (x,y) 產生 count 個粒子，回傳粒子清單。"""
    particles = []
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
    return particles


def update_particles(particles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """更新粒子狀態，回傳存活的粒子清單"""
    now = pygame.time.get_ticks()
    new_parts = []
    for p in particles:
        age = now - p.get("start", 0)
        life = p.get("life", 600)
        if age >= life:
            continue
        # 更新運動：簡單重力與空氣阻力
        p["vy"] += 0.18  # gravity
        p["vx"] *= 0.995
        p["vy"] *= 0.995
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        new_parts.append(p)
    return new_parts


def draw_particles(surface: pygame.Surface, particles: List[Dict[str, Any]]):
    """繪製粒子系統"""
    if not particles:
        return
        
    part_surf = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
    now = pygame.time.get_ticks()
    
    for p in particles:
        age = now - p.get("start", 0)
        life = p.get("life", 600)
        if age >= life:
            continue
        t = age / life
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
    
    surface.blit(part_surf, (0, 0))


def create_paddle_edge_effect(x: int, y: int, radius: int = 16, duration: int = 350) -> Dict[str, Any]:
    """創建底板邊緣反彈效果"""
    return {
        "x": int(x),
        "y": int(y),
        "start": pygame.time.get_ticks(),
        "duration": duration,
        "max_r": max(8, radius),
    }


def draw_paddle_edge_effects(surface: pygame.Surface, effects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """繪製底板邊緣反彈效果，回傳存活的效果清單"""
    if not effects:
        return []
        
    effect_surf = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
    now = pygame.time.get_ticks()
    alive = []
    
    for ef in effects:
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
    
    surface.blit(effect_surf, (0, 0))
    return alive


def draw_trajectory(surface: pygame.Surface, trajectory_points: List[Tuple[int, int]]):
    """繪製球的軌跡預測線"""
    if not trajectory_points:
        return
        
    trail_surf = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
    # 漸層起訖色 (RGBA)：改為藍色系做光暈效果
    start_col = (120, 190, 255, 220)
    end_col = (180, 220, 255, 24)
    
    try:
        n = len(trajectory_points)
        if n >= 2:
            # 逐段畫線，使用線段索引作為 t
            # 為了呈現光暈，先畫粗的半透明藍，再畫較細亮的內層
            for i in range(n - 1):
                t = i / max(1, n - 1)
                r = _lerp(start_col[0], end_col[0], t)
                g = _lerp(start_col[1], end_col[1], t)
                b = _lerp(start_col[2], end_col[2], t)
                a = _lerp(start_col[3], end_col[3], t)
                # 外層 glow：較大半透明線條
                w_outer = max(6, int(18 * (1.0 - t)))
                color_outer = (r, g, b, int(a * 0.35))
                try:
                    pygame.draw.line(
                        trail_surf,
                        color_outer,
                        trajectory_points[i],
                        trajectory_points[i + 1],
                        w_outer,
                    )
                except Exception:
                    pass
                # 內層亮線：較細但較亮
                w_inner = max(2, int(8 * (1.0 - t)))
                color_inner = (
                    min(255, r + 40),
                    min(255, g + 40),
                    min(255, b + 40),
                    int(a * 0.8),
                )
                try:
                    pygame.draw.line(
                        trail_surf,
                        color_inner,
                        trajectory_points[i],
                        trajectory_points[i + 1],
                        w_inner,
                    )
                except Exception:
                    pass
    except Exception:
        pass
    
    surface.blit(trail_surf, (0, 0))


def draw_count_circle(surface: pygame.Surface, count: int, font: pygame.font.Font):
    """在左上角繪製剩餘磚塊數量的圓圈顯示"""
    count_text = f"{count}"
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
                    surface.blit(
                        glow_surf,
                        (cx - gx, cy - gy),
                        special_flags=pygame.BLEND_RGBA_ADD,
                    )
                except Exception:
                    # fallback: 直接 blit
                    surface.blit(glow_surf, (cx - gx, cy - gy))
            except Exception:
                pass

            # 畫實心圓、邊框與文字（置中）
            pygame.draw.circle(surface, circle_fill_color, (cx, cy), circle_radius)
            pygame.draw.circle(
                surface, circle_border_color, (cx, cy), circle_radius, circle_border_w
            )
            txt_rect = text_surf.get_rect(center=(cx, cy))
            surface.blit(text_surf, txt_rect)
        except Exception:
            # 若繪製圓失敗則 fallback 為直接繪製文字
            surface.blit(text_surf, (circle_margin_left, circle_margin_top))
    except Exception:
        # 最後回退：如果任何步驟失敗，簡單繪製文字在左上角
        try:
            surface.blit(text_surf, (8, 8))
        except Exception:
            pass


def draw_auto_mode_status(surface: pygame.Surface, paddle_auto_mode: bool, font: pygame.font.Font):
    """在右上角顯示底板自動模式狀態"""
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
        box_rect.topright = (surface.get_width() - 8, 8)
        surface.blit(box_surf, box_rect)
    except Exception:
        pass


def draw_physics_panel(surface: pygame.Surface, ball_vx: float, ball_vy: float, physics_font: pygame.font.Font):
    """繪製物理參數面板"""
    try:
        # 計算速度大小與分量
        vx = float(ball_vx)
        vy = float(ball_vy)
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
        center_x = (surface.get_width() - box_w) // 2
        center_y = (surface.get_height() - box_h) // 2
        surface.blit(box_surf, (center_x, center_y))
    except Exception:
        pass


def draw_game_over_screen(surface: pygame.Surface, big_font: pygame.font.Font, small_font: pygame.font.Font):
    """繪製遊戲結束畫面"""
    width = surface.get_width()
    height = surface.get_height()
    
    # 大紅字（帶陰影）
    big_text = "你學廢了嗎"
    red = (220, 20, 20)
    # 陰影先畫一層黑色偏移，再畫紅色
    shadow = big_font.render(big_text, True, (0, 0, 0))
    shadow_rect = shadow.get_rect(center=(width // 2 + 4, height // 2 + 4))
    surface.blit(shadow, shadow_rect)
    big_surf = big_font.render(big_text, True, red)
    big_rect = big_surf.get_rect(center=(width // 2, height // 2))
    surface.blit(big_surf, big_rect)

    # 反射定律說明文字（多行，置中排列）
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
            surface.blit(surf, rect)
        # 空行也要佔用行高，但不渲染任何內容


def _lerp(a: int, b: int, t: float) -> int:
    """線性插值輔助函數"""
    return int(a + (b - a) * t)