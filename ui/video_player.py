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

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            p = self.parent()
            while p is not None:
                if hasattr(p, "toggle_play"):
                    p.toggle_play()
                    return
                p = p.parent()
        super().mousePressEvent(event)

class VideoPlayer(QWidget):
    fullscreen_requested = pyqtSignal(bool)
    
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.fullscreen_requested.emit(False)
        elif event.key() == Qt.Key.Key_Space:
            self.toggle_play()
        elif event.key() == Qt.Key.Key_Right:
            self.seek_relative(10000) # +10s
        elif event.key() == Qt.Key.Key_Left:
            self.seek_relative(-10000) # -10s
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
        # Optimization: Opaque paint event and no system background can help performance
        self.video_widget.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)
        self.video_widget.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        
        self.media_player.setVideoOutput(self.video_widget)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        
        # Give video widget some min height
        self.video_widget.setMinimumHeight(400)
        self.layout.addWidget(self.video_widget)
        
        # Controls Container
        self.controls_container = QWidget()
        self.controls_container.setFixedHeight(60)
        self.controls_container.setStyleSheet("background-color: rgba(10,10,10,230); border-top: 1px solid #1a1a1a;")
        controls_layout = QHBoxLayout(self.controls_container)
        controls_layout.setContentsMargins(15, 0, 15, 0)
        controls_layout.setSpacing(15)
        
        self.play_btn = QPushButton()
        self.play_btn.setFixedSize(40, 40)
        self.play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        # Making the play button stand out with a solid red circle or specific styling
        self.play_btn.setStyleSheet("""
            QPushButton {
                background-color: #e50914;
                border-radius: 20px;
                border: none;
            }
            QPushButton:hover {
                background-color: #ff1f29;
            }
        """)
        self.play_btn.clicked.connect(self.toggle_play)
        
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.setCursor(Qt.CursorShape.PointingHandCursor)
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: none;
                height: 4px;
                background: #333333;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #e50914;
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }
            QSlider::handle:horizontal:hover {
                background: #ffffff;
            }
        """)
        self.slider.sliderMoved.connect(self.set_position)
        
        self.time_label = QLabel("00:00:00 / 00:00:00")
        self.time_label.setStyleSheet("color: #ffffff; font-weight: bold; font-family: 'Consolas'; font-size: 13px;")
        
        # Volume Box
        volume_layout = QHBoxLayout()
        volume_layout.setSpacing(5)
        
        vol_icon = QLabel("🔊")
        vol_icon.setStyleSheet("color: #888; font-size: 14px;")
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setFixedWidth(80)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(int(self.audio_output.volume() * 100))
        self.volume_slider.setCursor(Qt.CursorShape.PointingHandCursor)
        self.volume_slider.setToolTip("Ses")
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #333333;
                height: 4px;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            QSlider::handle:horizontal:hover {
                background: #e50914;
            }
        """)
        self.volume_slider.valueChanged.connect(self.set_volume)
        
        volume_layout.addWidget(vol_icon)
        volume_layout.addWidget(self.volume_slider)
        
        self.fullscreen_btn = QPushButton("🗖") 
        self.fullscreen_btn.setFixedSize(36, 36)
        self.fullscreen_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.fullscreen_btn.setToolTip("Tam Ekran (ESC or Çift Tık)")
        self.fullscreen_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ffffff;
                font-size: 18px;
                border: 1px solid #333333;
                border-radius: 18px;
            }
            QPushButton:hover {
                background-color: #1f1f1f;
                border: 1px solid #e50914;
                color: #e50914;
            }
        """)
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        
        controls_layout.addWidget(self.play_btn)
        controls_layout.addWidget(self.slider)
        controls_layout.addWidget(self.time_label)
        controls_layout.addLayout(volume_layout)
        controls_layout.addWidget(self.fullscreen_btn)
        
        self.layout.addWidget(self.controls_container)
        
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)
        
    def load_video(self, video_path):
        if os.path.exists(video_path):
            self.media_player.setSource(QUrl.fromLocalFile(video_path))
            self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            # Set focus to capture keys
            self.setFocus()
            
    def toggle_play(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
            self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        else:
            self.media_player.play()
            self.play_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
            
    def position_changed(self, position):
        if not self.slider.isSliderDown():
            self.slider.setValue(position)
        self.update_time_label()
        
    def duration_changed(self, duration):
        self.slider.setRange(0, duration)
        self.update_time_label()
        
    def set_position(self, position):
        self.media_player.setPosition(position)
        
    def set_volume(self, volume):
        self.audio_output.setVolume(volume / 100.0)
        
    def seek_relative(self, ms):
        new_pos = self.media_player.position() + ms
        if new_pos < 0: new_pos = 0
        if new_pos > self.media_player.duration(): new_pos = self.media_player.duration()
        self.media_player.setPosition(new_pos)
        
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
