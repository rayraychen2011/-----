"""
物理計算和碰撞檢測邏輯
"""
import pygame
import math
from typing import List, Optional, Tuple
from .entities import Ball, Brick, Paddle


def predict_ball_landing_x(
    ball: Ball, 
    bricks: List[Brick], 
    width: int, 
    height: int, 
    paddle: Paddle, 
    start_paddle_x: int, 
    max_iter: int = 2000, 
    step: int = 6
) -> Optional[int]:
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


def predict_landing_x_trajectory(
    ball: Ball,
    bricks: List[Brick],
    width: int,
    height: int,
    paddle: Paddle,
    paddle_draw_x: int,
    max_bounces: int = 12,
    step: int = 6,
    max_iter: int = 3000,
) -> Optional[int]:
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


def aim_ball_at_brick(
    ball: Ball, 
    bricks_list: List[Brick], 
    prefer_above_y: Optional[int] = None, 
    speed: Optional[float] = None
) -> bool:
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

    return True


def check_wall_collision(ball: Ball, width: int, height: int) -> bool:
    """檢查球與牆壁的碰撞並處理反彈"""
    collided = False
    
    # 碰到左右牆壁
    if ball.x - ball.radius <= 0:
        ball.x = ball.radius
        ball.vx = -ball.vx
        collided = True
    elif ball.x + ball.radius >= width:
        ball.x = width - ball.radius
        ball.vx = -ball.vx
        collided = True

    # 碰到上方牆壁
    if ball.y - ball.radius <= 0:
        ball.y = ball.radius
        ball.vy = -ball.vy
        collided = True
    
    return collided


def check_paddle_collision(ball: Ball, paddle: Paddle, paddle_draw_x: int) -> bool:
    """檢查球與馬蹄鐵底板的碰撞"""
    if ball.vy <= 0:  # 只在球往下時檢查
        return False
        
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

    def _do_reflect(nx, ny):
        n_len = math.hypot(nx, ny)
        if n_len == 0:
            return False
        n_x = nx / n_len
        n_y = ny / n_len
        v_dot_n = ball.vx * n_x + ball.vy * n_y
        ball.vx = ball.vx - 2 * v_dot_n * n_x
        ball.vy = ball.vy - 2 * v_dot_n * n_y
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
            # 推開球以避免穿透
            overlap = ball.radius - dist
            if overlap > 0:
                n_len = math.hypot(nx, ny) or 1.0
                ball.x += (nx / n_len) * overlap
                ball.y += (ny / n_len) * overlap
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

    return collided


def check_brick_collision(ball: Ball, bricks: List[Brick]) -> Optional[Brick]:
    """檢查球與磚塊的碰撞，回傳被撞到的磚塊（如果有的話）"""
    for brick in bricks:
        if brick.hit:
            continue
        if ball.rect().colliderect(
            pygame.Rect(brick.x, brick.y, brick.width, brick.height)
        ):
            # 簡單根據球心與磚塊中心判定反彈方向
            if abs((brick.x + brick.width / 2) - ball.x) > abs(
                (brick.y + brick.height / 2) - ball.y
            ):
                ball.vx = -ball.vx
            else:
                ball.vy = -ball.vy
            return brick
    return None


def predict_trajectory(
    ball: Ball,
    bricks: List[Brick],
    width: int,
    height: int,
    paddle: Paddle,
    paddle_draw_x: int,
    max_bounces: int = 6,
    step: int = 6,
    delay_s: float = 0.5,
) -> List[Tuple[int, int]]:
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
            
            # 檢查底板碰撞
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
            if not collided:
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