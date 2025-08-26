######################載入套件######################
"""
音效處理相關功能\n
\n
此模組提供完整的遊戲音效管理功能，包括：\n
- 背景音樂播放與控制\n
- 音效載入與播放\n
- 音量調整\n
- 錯誤處理與備援機制\n
\n
支援的音效格式：\n
- 背景音樂：MP3\n
- 音效：WAV, MP3\n
"""
import pygame
from src.config.settings import BACKGROUND_MUSIC, EXPLOSION_SOUND, BELL_SOUND
from src.config.settings import MUSIC_VOLUME, EXPLOSION_VOLUME, BELL_VOLUME

######################音效管理器類別######################

class AudioManager:
    """
    音效管理器 - 統一管理遊戲中的所有音效\n
    \n
    此類別負責：\n
    1. 初始化 Pygame 音效系統\n
    2. 載入並管理背景音樂\n
    3. 載入並播放各種音效\n
    4. 提供音量控制功能\n
    5. 處理音效載入失敗的情況\n
    \n
    屬性:\n
    music_playing (bool): 背景音樂是否正在播放\n
    explosion_sound (pygame.mixer.Sound): 爆炸音效物件\n
    bell_sound (pygame.mixer.Sound): 鈴鐺音效物件\n
    """
    
    def __init__(self):
        """
        初始化音效管理器\n
        \n
        設定所有音效相關的初始狀態，並嘗試載入音效檔案。\n
        如果某些音效載入失敗，會印出錯誤訊息但不會中斷遊戲。\n
        """
        # 音效播放狀態
        self.music_playing = False
        self.explosion_sound = None
        self.bell_sound = None
        
        # 開始初始化所有音效系統
        self._init_audio()
    
    def _init_audio(self):
        """
        初始化音效系統 - 設定 Pygame mixer 並載入所有音效\n
        \n
        執行步驟：\n
        1. 初始化 Pygame mixer 模組\n
        2. 載入背景音樂並開始播放\n
        3. 載入各種音效檔案\n
        \n
        錯誤處理：\n
        如果 mixer 初始化失敗，會默默跳過但不會影響遊戲運行。\n
        """
        # 初始化 Pygame 的音效播放模組
        try:
            pygame.mixer.init()
        except Exception:
            # 如果音效系統初始化失敗，遊戲還是可以繼續跑，只是沒聲音
            pass
        
        # 開始載入背景音樂
        self._load_background_music()
        
        # 載入各種音效檔案
        self._load_sound_effects()
    
    def _load_background_music(self):
        """
        載入背景音樂 - 設定音樂檔案並開始循環播放\n
        \n
        背景音樂特性：\n
        - 使用 pygame.mixer.music 模組（專門處理長音樂檔案）\n
        - 設定為無限循環播放 (-1 參數)\n
        - 音量設定為配置檔中指定的數值\n
        \n
        錯誤處理：\n
        如果音樂檔案載入失敗，會印出錯誤訊息並設定狀態為未播放。\n
        """
        try:
            # 載入背景音樂檔案
            pygame.mixer.music.load(BACKGROUND_MUSIC)
            # 設定音樂音量
            pygame.mixer.music.set_volume(MUSIC_VOLUME)
            # 開始播放，-1 表示無限循環
            pygame.mixer.music.play(-1)
            # 記錄音樂正在播放
            self.music_playing = True
        except Exception as e:
            # 如果背景音樂載入失敗，就沒有背景音樂，但遊戲還是可以玩
            print(f"無法載入背景音樂: {e}")
            self.music_playing = False
    
    def _load_sound_effects(self):
        """
        載入音效檔案 - 準備各種遊戲音效\n
        \n
        載入的音效包括：\n
        - 爆炸音效：磚塊被擊中時播放\n
        - 鈴鐺音效：特殊事件時播放\n
        \n
        音效載入特性：\n
        - 使用 pygame.mixer.Sound（適合短音效）\n
        - 預先載入到記憶體，播放時反應更快\n
        - 可以同時播放多個音效\n
        """
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

######################音效播放方法######################
    
    def play_explosion_sound(self):
        """
        播放爆炸音效 - 當磚塊被擊中時呼叫\n
        \n
        播放邏輯：\n
        1. 優先使用預載的 Sound 物件播放\n
        2. 如果 Sound 播放失敗，嘗試用 music 模組播放\n
        3. 如果都失敗就默默跳過\n
        \n
        備援機制：\n
        Sound 物件播放失敗時，會嘗試用背景音樂通道播放，\n
        雖然會暫停背景音樂，但確保音效能夠播放。\n
        """
        if self.explosion_sound is not None:
            try:
                # 使用預載的音效物件播放，這是最理想的方式
                self.explosion_sound.play()
            except Exception:
                # 如果 Sound 播放失敗，嘗試用音樂通道播放
                try:
                    pygame.mixer.music.load(EXPLOSION_SOUND)
                    pygame.mixer.music.play(0)  # 播放一次，不循環
                except Exception:
                    # 如果都失敗就算了，遊戲繼續進行
                    pass
    
    def play_bell_sound(self):
        """
        播放鈴鐺音效 - 特殊事件時呼叫\n
        \n
        比爆炸音效簡單，因為鈴鐺音效不是必要的，\n
        失敗了就直接跳過，不會有備援機制。\n
        """
        if self.bell_sound is not None:
            try:
                # 直接播放鈴鐺音效
                self.bell_sound.play()
            except Exception:
                # 播放失敗就算了，不是重要音效
                pass

######################音樂控制方法######################
    
    def stop_music(self):
        """
        停止背景音樂 - 暫停音樂播放\n
        \n
        用途：\n
        - 遊戲暫停時停止音樂\n
        - 播放重要音效時避免干擾\n
        - 玩家選擇關閉音樂時\n
        """
        try:
            pygame.mixer.music.stop()
            self.music_playing = False
        except Exception:
            # 停止音樂失敗通常不會有問題，直接忽略
            pass
    
    def resume_music(self):
        """
        恢復背景音樂 - 重新開始播放音樂\n
        \n
        只有在音樂目前沒在播放時才會重新載入，\n
        避免重複播放造成音效重疊。\n
        """
        if not self.music_playing:
            # 重新載入並播放背景音樂
            self._load_background_music()

######################音量控制方法######################
    
    def set_music_volume(self, volume: float):
        """
        設定背景音樂音量\n
        \n
        參數:\n
        volume (float): 音量大小，範圍 0.0-1.0，0.0 為靜音，1.0 為最大音量\n
        \n
        自動修正：\n
        如果傳入的音量超出範圍，會自動修正到有效範圍內。\n
        """
        try:
            # 確保音量在有效範圍內，然後設定
            pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))
        except Exception:
            # 設定音量失敗通常不影響遊戲，直接忽略
            pass
    
    def set_explosion_volume(self, volume: float):
        """
        設定爆炸音效音量\n
        \n
        參數:\n
        volume (float): 音量大小，範圍 0.0-1.0\n
        """
        if self.explosion_sound is not None:
            try:
                self.explosion_sound.set_volume(max(0.0, min(1.0, volume)))
            except Exception:
                pass
    
    def set_bell_volume(self, volume: float):
        """
        設定鈴鐺音效音量\n
        \n
        參數:\n
        volume (float): 音量大小，範圍 0.0-1.0\n
        """
        if self.bell_sound is not None:
            try:
                self.bell_sound.set_volume(max(0.0, min(1.0, volume)))
            except Exception:
                pass