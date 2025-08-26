######################載入套件######################
"""
鈴鐺音效產生器\n
\n
此工具用於產生敲磚塊遊戲中使用的鈴鐺音效檔案。\n
\n
功能說明：\n
- 產生 880Hz 的正弦波基底音\n
- 加入指數衰減包絡模擬真實鈴聲\n
- 輸出為 16-bit 單聲道 WAV 檔案\n
- 自動儲存到 assets/sounds/ 目錄\n
\n
音效參數：\n
- 採樣率：44100 Hz\n
- 持續時間：0.12 秒\n
- 基頻：880 Hz (A5 音符)\n
- 衰減係數：5 (快速衰減模擬鈴聲特性)\n
"""
import wave
import math
import struct
import os

######################音效參數設定######################

# 音效基本參數
SAMPLE_RATE = 44100  # 採樣率（Hz）
DURATION = 0.12      # 音效持續時間（秒）
FREQUENCY = 880.0    # 基頻（Hz），對應 A5 音符
AMPLITUDE = 16000    # 音量振幅
DECAY_FACTOR = 5     # 衰減係數，數值越大衰減越快

# 計算總樣本數量
total_samples = int(SAMPLE_RATE * DURATION)

######################檔案路徑設定######################

# 取得專案根目錄
script_directory = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_directory)
output_path = os.path.join(project_root, "assets", "sounds", "bell.wav")

######################產生音效檔案######################

def generate_bell_sound():
    """
    產生鈴鐺音效檔案\n
    \n
    此函數使用數學模型來模擬真實鈴鐺的聲音特性：\n
    1. 使用正弦波產生基底音調\n
    2. 套用指數衰減包絡模擬鈴聲的自然衰減\n
    3. 轉換為 16-bit 整數格式\n
    4. 寫入 WAV 檔案\n
    \n
    數學公式：\n
    - 包絡函數：amplitude * exp(-decay_factor * time)\n
    - 音調函數：sin(2π * frequency * time)\n
    - 最終波形：envelope * tone\n
    """
    with wave.open(output_path, "w") as wave_file:
        # 設定 WAV 檔案格式
        wave_file.setnchannels(1)      # 單聲道
        wave_file.setsampwidth(2)      # 16-bit 樣本
        wave_file.setframerate(SAMPLE_RATE)  # 採樣率
        
        # 逐個樣本計算並寫入檔案
        for sample_index in range(total_samples):
            # 計算當前時間點（秒）
            current_time = sample_index / SAMPLE_RATE
            
            # 計算衰減包絡：模擬鈴聲逐漸變小的特性
            envelope = math.exp(-DECAY_FACTOR * current_time)
            
            # 計算正弦波音調
            sine_wave = math.sin(2 * math.pi * FREQUENCY * current_time)
            
            # 結合包絡與音調，轉換為整數格式
            sample_value = int(AMPLITUDE * envelope * sine_wave)
            
            # 寫入 16-bit 小端序格式
            wave_file.writeframes(struct.pack("<h", sample_value))

# 產生音效檔案
generate_bell_sound()
print(f"鈴鐺音效檔案已成功產生：{output_path}")
