import wave
import math
import struct
import os

sample_rate = 44100
duration = 0.12
freq = 880.0
amplitude = 16000
n_samples = int(sample_rate * duration)

# 取得專案根目錄
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
path = os.path.join(project_root, "assets", "sounds", "bell.wav")

with wave.open(path, "w") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(sample_rate)
    for i in range(n_samples):
        t = i / sample_rate
        env = math.exp(-5 * t)
        val = int(amplitude * env * math.sin(2 * math.pi * freq * t))
        wf.writeframes(struct.pack("<h", val))
print("bell.wav generated at", path)
