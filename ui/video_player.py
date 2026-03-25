import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel, QStyle
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        
        # Adjust volume down a bit by default
        self.audio_output.setVolume(0.5)
        
        self.video_widget = QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        
        # Give video widget some min height
        self.video_widget.setMinimumHeight(300)
        layout.addWidget(self.video_widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        self.play_btn = QPushButton()
        self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_btn.clicked.connect(self.toggle_play)
        
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)
        
        self.time_label = QLabel("00:00:00 / 00:00:00")
        
        controls_layout.addWidget(self.play_btn)
        controls_layout.addWidget(self.slider)
        controls_layout.addWidget(self.time_label)
        
        layout.addLayout(controls_layout)
        
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
