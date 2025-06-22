from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel
import cv2
import pyaudio

class VideoWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)
        self.setAlignment(Qt.AlignCenter)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            bytes_per_line = ch * w
            img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pix = QPixmap.fromImage(img).scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(pix)

class RecordAudio:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100

    def start_recording(self):
        self.stream = self.p.open(format=self.format,
                                  channels=self.channels,
                                  rate=self.rate,
                                  frames_per_buffer=self.chunk,
                                  input=True)
        print("Started recording")
    
    def read_data(self):
        if self.stream is not None:
            data = self.stream.read(self.chunk)
            return data
        else:
            print("Stream not started")

    def stop_recording(self):
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            print("Stopped recording")
    
    def terminate(self):
        self.p.terminate()
        print("Audio process terminated")