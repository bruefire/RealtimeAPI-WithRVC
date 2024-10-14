import pyaudio
import threading
from collections import deque


# 録音クラス
class ContinuousRecorder:
    # オーディオ設定
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 24000
    CHUNK = 1024
    MAX_REC_SEC = 10

    def __init__(self, interrupted):
        self.p = pyaudio.PyAudio()
        
        self.stream = self.p.open(
            format=self.FORMAT, 
            channels=self.CHANNELS, 
            rate=self.RATE, 
            input=True, 
            frames_per_buffer=self.CHUNK)
        
        self.frames = deque(maxlen=int(self.RATE / self.CHUNK * self.MAX_REC_SEC))  # 最大MAX_REC_SEC秒分のフレームを保持するバッファ
        self.running = False
        self.isInterrupted = interrupted

    def start_recording(self):
        self.running = True
        self.recording_thread = threading.Thread(target=self._record)
        self.recording_thread.start()

    def _record(self):
        while self.running:
            data = self.stream.read(self.CHUNK)
            self.frames.append(data)

            if self.isInterrupted[0]:
                self.stop_recording()
                break

    def stop_recording(self):
        self.running = False
        self.recording_thread.join()
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

    def get_audio(self):
        audio_data = b''.join(list(self.frames))
        self.frames.clear()
        return audio_data
