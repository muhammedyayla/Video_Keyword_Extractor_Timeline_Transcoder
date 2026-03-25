import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel, QStyle
)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QKeyEvent, QMouseEvent
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget

class FullScreenVideoWidget(QVideoWidget):
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        p = self.parent()
        while p is not None:
            if hasattr(p, "toggle_fullscreen"):
                p.toggle_fullscreen()
                return
            p = p.parent()
        super().mouseDoubleClickEvent(event)

class VideoPlayer(QWidget):
    fullscreen_requested = pyqtSignal(bool)
    
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.fullscreen_requested.emit(False)
        else:
            super().keyPressEvent(event)
            
    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Black background for fallback
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.GlobalColor.black)
        self.setPalette(palette)
        
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        
        # Adjust volume down a bit by default
        self.audio_output.setVolume(0.5)
        
        self.video_widget = FullScreenVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        
        # Give video widget some min height
        self.video_widget.setMinimumHeight(400)
        self.layout.addWidget(self.video_widget)
        
        # Controls Container (to keep them in one layout)
        self.controls_container = QWidget()
        self.controls_container.setFixedHeight(50)
        self.controls_container.setStyleSheet("background-color: rgba(0,0,0,180);")
        controls_layout = QHBoxLayout(self.controls_container)
        controls_layout.setContentsMargins(10, 0, 10, 0)
        
        self.play_btn = QPushButton()
        self.play_btn.setFixedWidth(40)
        self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_btn.clicked.connect(self.toggle_play)
        
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)
        
        self.time_label = QLabel("00:00:00 / 00:00:00")
        self.time_label.setStyleSheet("color: white; font-weight: bold;")
        
        self.fullscreen_btn = QPushButton("🗖") 
        self.fullscreen_btn.setFixedWidth(40)
        self.fullscreen_btn.setToolTip("Tam Ekran (ESC or Çift Tık)")
        self.fullscreen_btn.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        
        controls_layout.addWidget(self.play_btn)
        controls_layout.addWidget(self.slider)
        controls_layout.addWidget(self.time_label)
        controls_layout.addWidget(self.fullscreen_btn)
        
        self.layout.addWidget(self.controls_container)
        
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)
        
    def load_video(self, video_path):
        if os.path.exists(video_path):
            self.media_player.setSource(QUrl.fromLocalFile(video_path))
            self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            
    def toggle_play(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
            self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        else:
            self.media_player.play()
            self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
            
    def position_changed(self, position):
        self.slider.setValue(position)
        self.update_time_label()
        
    def duration_changed(self, duration):
        self.slider.setRange(0, duration)
        self.update_time_label()
        
    def set_position(self, position):
        self.media_player.setPosition(position)
        
    def toggle_fullscreen(self):
        # Notify main window to toggle
        is_fs = self.window().isFullScreen()
        self.fullscreen_requested.emit(not is_fs)
        
    def seek_to(self, ms):
        self.media_player.setPosition(ms)
        self.media_player.play()
        self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        
    def update_time_label(self):
        pos = self.media_player.position()
        dur = self.media_player.duration()
        self.time_label.setText(f"{self.format_time(pos)} / {self.format_time(dur)}")
        
    def format_time(self, ms):
        if ms < 0: ms = 0
        s = ms // 1000
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"
