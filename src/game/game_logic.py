"""
主要的遊戲邏輯控制器
"""
import pygame
import sys
import random
import math
from typing import List, Optional

from src.config.settings import *
from src.game.entities import Brick, Ball, Paddle
from src.game.physics import (
    check_wall_collision, check_paddle_collision, check_brick_collision,
    predict_landing_x_trajectory, aim_ball_at_brick, predict_trajectory
)
from src.game.graphics import (
    spawn_particles, update_particles, draw_particles,
    create_paddle_edge_effect, draw_paddle_edge_effects,
    draw_trajectory, draw_count_circle, draw_auto_mode_status,
    draw_physics_panel, draw_game_over_screen
)
from src.utils.colors import (
    random_color, apply_gradient_to_bricks, shift_towards_complement
)
from src.utils.audio import AudioManager


class BrickBreakerGame:
    """敲磚塊遊戲主控制器"""
    
    def __init__(self):
        # 初始化 Pygame
        pygame.init()
        
        # 建立視窗
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        
        # 時鐘
        self.clock = pygame.time.Clock()
        
        # 載入資源
        self._load_resources()
        
        # 初始化遊戲狀態
        self._init_game_state()
        
        # 音效管理器
        self.audio_manager = AudioManager()
        
        # 初始化遊戲物件
        self._init_game_objects()
        
        # 運行狀態
        self.running = True
    
    def _load_resources(self):
        """載入遊戲資源"""
        # 載入背景圖
        try:
            self.bg_img = pygame.image.load(BACKGROUND_IMAGE).convert()
            self.bg_img = pygame.transform.smoothscale(self.bg_img, (WINDOW_WIDTH, WINDOW_HEIGHT))
        except Exception as e:
            print(f"無法載入背景圖片: {e}")
            self.bg_img = None
        
        # 載入字型
        try:
            self.font = pygame.font.SysFont("microsoftyahei", DEFAULT_FONT_SIZE)
        except:
            try:
                self.font = pygame.font.SysFont("microsoftyaheiui", DEFAULT_FONT_SIZE)
            except:
                self.font = pygame.font.Font(None, DEFAULT_FONT_SIZE)
        
        try:
            self.physics_font = pygame.font.SysFont("microsoftyahei", PHYSICS_FONT_SIZE)
        except:
            try:
                self.physics_font = pygame.font.SysFont("microsoftyaheiui", PHYSICS_FONT_SIZE)
            except:
                self.physics_font = pygame.font.Font(None, PHYSICS_FONT_SIZE)
        
        try:
            self.big_font = pygame.font.SysFont("microsoftyahei", BIG_FONT_SIZE)
        except:
            try:
                self.big_font = pygame.font.SysFont("microsoftyaheiui", BIG_FONT_SIZE)
            except:
                self.big_font = pygame.font.Font(None, BIG_FONT_SIZE)
        
        try:
            self.small_font = pygame.font.SysFont("microsoftyahei", SMALL_FONT_SIZE)
        except:
            try:
                self.small_font = pygame.font.SysFont("microsoftyaheiui", SMALL_FONT_SIZE)
            except:
                self.small_font = pygame.font.Font(None, SMALL_FONT_SIZE)
    
    def _init_game_state(self):
        """初始化遊戲狀態"""
        # 遊戲狀態旗標
        self.show_instructions = False
        self.show_physics = False
        self.paddle_auto_mode = False
        self.ball_attached = True
        
        # 球加速相關
        self.ball_boost_active = False
        self.ball_normal_vx = 0
        self.ball_normal_vy = 0
        
        # 底板平滑移動
        self.paddle_pos_x = float((WINDOW_WIDTH - int(BRICK_WIDTH * PADDLE_WIDTH_MULTIPLIER)) // 2)
        
        # 特效系統
        self.particles = []
        self.paddle_edge_effects = []
        
        # 漸層顏色設定
        self.start_color = random_color()
        self.end_color = random_color()
        self.direction = random.choice(["horizontal", "vertical", "diagonal"])
    
    def _init_game_objects(self):
        """初始化遊戲物件"""
        # 創建磚塊
        self._create_bricks()
        
        # 創建底板
        paddle_width = int(BRICK_WIDTH * PADDLE_WIDTH_MULTIPLIER)
        paddle_height = BRICK_HEIGHT
        paddle_y = WINDOW_HEIGHT - PADDLE_Y_OFFSET
        paddle_x = (WINDOW_WIDTH - paddle_width) // 2
        
        self.paddle = Paddle(x=paddle_x, y=paddle_y, width=paddle_width, color=PADDLE_COLOR)
        
        # 創建球
        ball_start_x = paddle_x + paddle_width // 2
        ball_start_y = paddle_y - BALL_RADIUS
        
        self.ball = Ball(
            x=ball_start_x,
            y=ball_start_y,
            radius=BALL_RADIUS,
            vx=0,
            vy=0,
            color=BALL_COLOR,
            image_path=BALL_IMAGE
        )
    
    def _create_bricks(self):
        """創建磚塊牆"""
        self.bricks = []
        
        # 計算磚牆位置
        total_width = COLS * BRICK_WIDTH + (COLS - 1) * BRICK_GAP
        x_offset = (WINDOW_WIDTH - total_width) // 2
        y_offset = 60
        
        # 建立磚塊清單
        for r in range(ROWS):
            for c in range(COLS):
                x = x_offset + c * (BRICK_WIDTH + BRICK_GAP)
                y = y_offset + r * (BRICK_HEIGHT + BRICK_GAP)
                brick = Brick(x=x, y=y, width=BRICK_WIDTH, height=BRICK_HEIGHT, color=(0, 0, 0))
                self.bricks.append(brick)
        
        # 套用漸層顏色
        apply_gradient_to_bricks(self.bricks, ROWS, COLS, self.start_color, self.end_color, self.direction)
        
        # 指定特殊磚塊
        self._assign_special_bricks(5)
    
    def _assign_special_bricks(self, count: int = 5):
        """從現有未被標記的磚塊中隨機選擇 count 個設為特殊磚塊"""
        # 先清除所有標記
        for b in self.bricks:
            b.is_special = False
        
        available = [b for b in self.bricks if not b.hit]
        if len(available) == 0:
            return
        
        count = min(count, len(available))
        chosen = random.sample(available, count)
        for b in chosen:
            b.is_special = True
        
        # 偵錯資訊
        try:
            info = []
            for b in chosen:
                idx = self.bricks.index(b)
                info.append(f"idx={idx}(x={b.x},y={b.y})")
            print(f"[DEBUG] special bricks: {', '.join(info)}")
        except Exception:
            pass
    
    def reset_bricks(self):
        """重置磚牆並重新隨機化漸層顏色"""
        self.start_color = random_color()
        self.end_color = random_color()
        self.direction = random.choice(["horizontal", "vertical", "diagonal"])
        
        for b in self.bricks:
            b.hit = False
        
        apply_gradient_to_bricks(self.bricks, ROWS, COLS, self.start_color, self.end_color, self.direction)
        self._assign_special_bricks(5)
        self.ball_attached = True
    
    def handle_events(self):
        """處理遊戲事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:  # 右鍵
                    self._launch_ball()
                elif event.button == 1:  # 左鍵
                    self.paddle_auto_mode = not self.paddle_auto_mode
                    print(f"[INFO] Paddle auto mode {'enabled' if self.paddle_auto_mode else 'disabled'}")
                elif event.button == 2:  # 中鍵
                    self.show_physics = not self.show_physics
                    
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # 重新隨機化漸層
                    self.start_color = random_color()
                    self.end_color = random_color()
                    self.direction = random.choice(["horizontal", "vertical", "diagonal"])
                    apply_gradient_to_bricks(self.bricks, ROWS, COLS, self.start_color, self.end_color, self.direction)
                elif event.key == pygame.K_g:
                    # 顯示漸層參數
                    print(f"Gradient: start={self.start_color}, end={self.end_color}, dir={self.direction}")
                elif event.key == pygame.K_SPACE:
                    self._launch_ball()
                elif event.key == pygame.K_q:
                    self.show_instructions = not self.show_instructions
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def _launch_ball(self):
        """發射球"""
        if self.ball_attached:
            self.ball_attached = False
            self.ball.vx = 5 * (1 if random.random() < 0.5 else -1)
            self.ball.vy = -5
            self.ball_normal_vx = self.ball.vx
            self.ball_normal_vy = self.ball.vy
            
            # 若為自動模式，調整速度朝向未被擊中的磚塊
            if self.paddle_auto_mode:
                aim_ball_at_brick(self.ball, self.bricks, prefer_above_y=self.paddle.y)
    
    def update_paddle(self):
        """更新底板位置"""
        mouse_x, _ = pygame.mouse.get_pos()
        paddle_draw_x = int(mouse_x - self.paddle.width / 2)
        
        # 自動模式預測
        if self.paddle_auto_mode and not self.ball_attached:
            try:
                landing_x = predict_landing_x_trajectory(
                    self.ball, self.bricks, WINDOW_WIDTH, WINDOW_HEIGHT, self.paddle, paddle_draw_x
                )
                if landing_x is not None:
                    paddle_draw_x = int(landing_x - self.paddle.width / 2)
            except Exception:
                pass
        
        # 限制底板不超出畫面
        if paddle_draw_x < 0:
            paddle_draw_x = 0
        elif paddle_draw_x > WINDOW_WIDTH - self.paddle.width:
            paddle_draw_x = WINDOW_WIDTH - self.paddle.width
        
        # 平滑移動
        try:
            diff = float(paddle_draw_x) - float(self.paddle_pos_x)
            if abs(diff) > PADDLE_MAX_STEP:
                step = PADDLE_MAX_STEP if diff > 0 else -PADDLE_MAX_STEP
                self.paddle_pos_x += step
            else:
                self.paddle_pos_x = self.paddle_pos_x + diff * PADDLE_LERP
            
            if self.paddle_pos_x < 0:
                self.paddle_pos_x = 0.0
            elif self.paddle_pos_x > WINDOW_WIDTH - self.paddle.width:
                self.paddle_pos_x = float(WINDOW_WIDTH - self.paddle.width)
        except Exception:
            self.paddle_pos_x = float(paddle_draw_x)
        
        return int(self.paddle_pos_x)
    
    def update_ball(self, paddle_draw_x: int):
        """更新球的狀態"""
        if self.ball_attached:
            self.ball.x = paddle_draw_x + self.paddle.width // 2
            self.ball.y = self.paddle.y - self.ball.radius
            self.ball.vx = 0
            self.ball.vy = 0
            return
        
        # 檢查加速按鍵
        keys = pygame.key.get_pressed()
        boost_key_pressed = keys[pygame.K_LSHIFT]
        
        # 處理球加速邏輯
        if boost_key_pressed and not self.ball_boost_active:
            self.ball_boost_active = True
            self.ball_normal_vx = self.ball.vx
            self.ball_normal_vy = self.ball.vy
            self.ball.vx *= BALL_BOOST_MULTIPLIER
            self.ball.vy *= BALL_BOOST_MULTIPLIER
        elif not boost_key_pressed and self.ball_boost_active:
            self.ball_boost_active = False
            self.ball.vx = self.ball_normal_vx
            self.ball.vy = self.ball_normal_vy
        
        # 更新球的位置
        self.ball.x += self.ball.vx
        self.ball.y += self.ball.vy
        
        # 更新暫時效果
        self.ball.update_powerups()
        
        # 碰撞檢測
        self._handle_collisions(paddle_draw_x)
    
    def _handle_collisions(self, paddle_draw_x: int):
        """處理所有碰撞"""
        # 牆壁碰撞
        if check_wall_collision(self.ball, WINDOW_WIDTH, WINDOW_HEIGHT):
            if self.ball_boost_active:
                self.ball_normal_vx = self.ball.vx / BALL_BOOST_MULTIPLIER
                self.ball_normal_vy = self.ball.vy / BALL_BOOST_MULTIPLIER
        
        # 球掉到底部
        if self.ball.y - self.ball.radius > WINDOW_HEIGHT:
            if self.paddle_auto_mode:
                # 自動模式：讓球反彈回來
                self.ball.y = WINDOW_HEIGHT - self.ball.radius - 1
                self.ball.vy = -abs(self.ball.vy) if self.ball.vy != 0 else -5
                if self.ball.x < self.ball.radius:
                    self.ball.x = self.ball.radius + 2
                elif self.ball.x > WINDOW_WIDTH - self.ball.radius:
                    self.ball.x = WINDOW_WIDTH - self.ball.radius - 2
            else:
                # 重置遊戲
                self.reset_bricks()
                self.ball_attached = True
                self.ball.x = paddle_draw_x + self.paddle.width // 2
                self.ball.y = self.paddle.y - self.ball.radius
                self.ball.vx = 0
                self.ball.vy = 0
                self.ball_boost_active = False
                self.ball_normal_vx = 0
                self.ball_normal_vy = 0
        
        # 底板碰撞
        if check_paddle_collision(self.ball, self.paddle, paddle_draw_x):
            if self.ball_boost_active:
                self.ball_normal_vx = self.ball.vx / BALL_BOOST_MULTIPLIER
                self.ball_normal_vy = self.ball.vy / BALL_BOOST_MULTIPLIER
            
            # 若為自動模式，反射後重新瞄準磚塊
            if self.paddle_auto_mode:
                aim_ball_at_brick(self.ball, self.bricks, prefer_above_y=self.paddle.y)
            
            # 創建底板反彈特效
            effect = create_paddle_edge_effect(int(self.ball.x), int(self.ball.y))
            self.paddle_edge_effects.append(effect)
        
        # 磚塊碰撞
        hit_brick = check_brick_collision(self.ball, self.bricks)
        if hit_brick is not None:
            hit_brick.hit = True
            
            if self.ball_boost_active:
                self.ball_normal_vx = self.ball.vx / BALL_BOOST_MULTIPLIER
                self.ball_normal_vy = self.ball.vy / BALL_BOOST_MULTIPLIER
            
            # 特殊磚塊處理
            if getattr(hit_brick, "is_special", False):
                self._handle_special_brick(hit_brick)
            else:
                # 普通磚塊
                self.audio_manager.play_bell_sound()
                new_particles = spawn_particles(
                    hit_brick.x + hit_brick.width // 2,
                    hit_brick.y + hit_brick.height // 2,
                    count=10,
                    color=(255, 220, 180),
                    speed=3.5,
                    spread=1.0,
                    life=500,
                )
                self.particles.extend(new_particles)
    
    def _handle_special_brick(self, brick):
        """處理特殊磚塊的效果"""
        # 球的暫時放大效果
        self.ball.apply_temporary_scale(2.0, 1000)
        
        # 播放爆炸音效
        self.audio_manager.play_explosion_sound()
        
        # 清除 3x3 區域
        try:
            idx = self.bricks.index(brick)
            r = idx // COLS
            c = idx % COLS
            cleared = []
            
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    nr = r + dr
                    nc = c + dc
                    if 0 <= nr < ROWS and 0 <= nc < COLS:
                        nidx = nr * COLS + nc
                        if not self.bricks[nidx].hit:
                            self.bricks[nidx].hit = True
                            cleared.append(f"idx={nidx}(r={nr},c={nc})")
            
            if cleared:
                print(f"[DEBUG] hit special brick idx={idx} cleared: {', '.join(cleared)}")
        except Exception:
            print("[DEBUG] hit special brick (index unknown)")
        
        # 創建粒子效果
        new_particles = spawn_particles(
            brick.x + brick.width // 2,
            brick.y + brick.height // 2,
            count=18,
            color=(255, 150, 80),
            speed=4.5,
            spread=1.2,
            life=700,
        )
        self.particles.extend(new_particles)
    
    def update_effects(self):
        """更新特效系統"""
        # 更新粒子
        self.particles = update_particles(self.particles)
        
        # 更新底板特效
        self.paddle_edge_effects = draw_paddle_edge_effects(self.screen, self.paddle_edge_effects)
    
    def render(self, paddle_draw_x: int):
        """渲染遊戲畫面"""
        # 背景
        if self.bg_img is not None:
            self.screen.blit(self.bg_img, (0, 0))
        else:
            self.screen.fill(BACKGROUND_COLOR)
        
        # 檢查遊戲結束
        remaining = sum(1 for b in self.bricks if not b.hit)
        if remaining == 0:
            self._render_game_over()
            return
        
        # 繪製遊戲物件
        self.paddle.draw(self.screen, x=paddle_draw_x)
        
        # 更新磚塊顏色並繪製
        total_bricks = ROWS * COLS
        ratio = remaining / total_bricks if total_bricks > 0 else 0
        t_vivid = min(max(1.0 - ratio, 0.0), 1.0)
        vivid_strength = 0.9
        
        for brick in self.bricks:
            if brick.hit:
                continue
            brick.color = shift_towards_complement(brick.base_color, t_vivid, vivid_strength)
            brick.draw(self.screen)
        
        self.ball.draw(self.screen)
        
        # 繪製軌跡預測
        if not self.ball_attached:
            traj_pts = predict_trajectory(
                self.ball, self.bricks, WINDOW_WIDTH, WINDOW_HEIGHT,
                self.paddle, paddle_draw_x, max_bounces=8, step=6, delay_s=0.5
            )
            draw_trajectory(self.screen, traj_pts)
        
        # 繪製特效
        draw_particles(self.screen, self.particles)
        
        # 繪製 UI
        draw_count_circle(self.screen, remaining, self.font)
        draw_auto_mode_status(self.screen, self.paddle_auto_mode, self.font)
        
        if self.show_physics:
            draw_physics_panel(self.screen, self.ball.vx, self.ball.vy, self.physics_font)
    
    def _render_game_over(self):
        """渲染遊戲結束畫面"""
        # 停止球
        self.ball.vx = 0
        self.ball.vy = 0
        
        # 繪製剩餘磚塊（理論上應該為0）
        for brick in self.bricks:
            if not brick.hit:
                brick.draw(self.screen)
        
        # 繪製遊戲結束畫面
        draw_game_over_screen(self.screen, self.big_font, self.small_font)
    
    def run(self):
        """主遊戲循環"""
        while self.running:
            self.clock.tick(FPS)
            
            # 事件處理
            self.handle_events()
            
            if not self.running:
                break
            
            # 更新遊戲狀態
            paddle_draw_x = self.update_paddle()
            self.update_ball(paddle_draw_x)
            self.update_effects()
            
            # 渲染
            self.render(paddle_draw_x)
            
            # 更新顯示
            pygame.display.update()
        
        # 清理
        pygame.quit()
        sys.exit()