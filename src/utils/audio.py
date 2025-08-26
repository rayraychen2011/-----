"""
音效處理相關功能
"""
import pygame
from src.config.settings import BACKGROUND_MUSIC, EXPLOSION_SOUND, BELL_SOUND
from src.config.settings import MUSIC_VOLUME, EXPLOSION_VOLUME, BELL_VOLUME


class AudioManager:
    """音效管理器"""
    
    def __init__(self):
        self.music_playing = False
        self.explosion_sound = None
        self.bell_sound = None
        
        # 初始化音效系統
        self._init_audio()
    
    def _init_audio(self):
        """初始化音效系統"""
        # 初始化 mixer
        try:
            pygame.mixer.init()
        except Exception:
            pass
        
        # 載入背景音樂
        self._load_background_music()
        
        # 載入音效
        self._load_sound_effects()
    
    def _load_background_music(self):
        """載入背景音樂"""
        try:
            pygame.mixer.music.load(BACKGROUND_MUSIC)
            pygame.mixer.music.set_volume(MUSIC_VOLUME)
            pygame.mixer.music.play(-1)  # -1 表示無限循環
            self.music_playing = True
        except Exception as e:
            print(f"無法載入背景音樂: {e}")
            self.music_playing = False
    
    def _load_sound_effects(self):
        """載入音效檔案"""
        # 載入爆炸音效
        try:
            self.explosion_sound = pygame.mixer.Sound(EXPLOSION_SOUND)
            self.explosion_sound.set_volume(EXPLOSION_VOLUME)
        except Exception as e:
            print(f"無法載入爆炸音效: {e}")
            self.explosion_sound = None
        
        # 載入鈴鐺音效
        try:
            self.bell_sound = pygame.mixer.Sound(BELL_SOUND)
            self.bell_sound.set_volume(BELL_VOLUME)
        except Exception as e:
            print(f"無法載入鈴鐺音效: {e}")
            self.bell_sound = None
    
    def play_explosion_sound(self):
        """播放爆炸音效"""
        if self.explosion_sound is not None:
            try:
                self.explosion_sound.play()
            except Exception:
                # fallback: 嘗試用 music 播放短音檔（不循環）
                try:
                    pygame.mixer.music.load(EXPLOSION_SOUND)
                    pygame.mixer.music.play(0)
                except Exception:
                    pass
    
    def play_bell_sound(self):
        """播放鈴鐺音效"""
        if self.bell_sound is not None:
            try:
                self.bell_sound.play()
            except Exception:
                pass
    
    def stop_music(self):
        """停止背景音樂"""
        try:
            pygame.mixer.music.stop()
            self.music_playing = False
        except Exception:
            pass
    
    def resume_music(self):
        """恢復背景音樂"""
        if not self.music_playing:
            self._load_background_music()
    
    def set_music_volume(self, volume: float):
        """設定背景音樂音量 (0.0-1.0)"""
        try:
            pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))
        except Exception:
            pass
    
    def set_explosion_volume(self, volume: float):
        """設定爆炸音效音量 (0.0-1.0)"""
        if self.explosion_sound is not None:
            try:
                self.explosion_sound.set_volume(max(0.0, min(1.0, volume)))
            except Exception:
                pass
    
    def set_bell_volume(self, volume: float):
        """設定鈴鐺音效音量 (0.0-1.0)"""
        if self.bell_sound is not None:
            try:
                self.bell_sound.set_volume(max(0.0, min(1.0, volume)))
            except Exception:
                pass