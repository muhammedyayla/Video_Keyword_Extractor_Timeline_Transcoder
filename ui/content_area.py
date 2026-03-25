import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
from .video_player import VideoPlayer
from .transcript_view import TranscriptView

class DragDropArea(QLabel):
    file_dropped = pyqtSignal(list) # emits a list of file paths
    
    def __init__(self):
        super().__init__()
        self.setText("Sürükle bırak yaparak veya 'Dosya Yükle' ile deşifreye başlayın\n\n(Drag & Drop Video Here)")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #564d4d; 
                border-radius: 10px; 
                font-size: 16px; 
                color: #ffffff;
                background-color: #000000;
            }
        """)
        self.setAcceptDrops(True)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QLabel {
                    border: 2px dashed #b32d24; 
                    border-radius: 10px; 
                    font-size: 16px; 
                    color: #b32d24; 
                    background-color: #2b0404;
                }
            """)
            
    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #564d4d; 
                border-radius: 10px; 
                font-size: 16px; 
                color: #ffffff;
                background-color: #000000;
            }
        """)

    def dropEvent(self, event):
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #564d4d; 
                border-radius: 10px; 
                font-size: 16px; 
                color: #ffffff;
                background-color: #000000;
            }
        """)
        urls = event.mimeData().urls()
        files = []
        for url in urls:
            path = url.toLocalFile()
            if os.path.isfile(path) and path.lower().endswith(('.mp4', '.mkv', '.avi', '.mov')):
                files.append(path)
            elif os.path.isdir(path):
                for f in os.listdir(path):
                    if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov')):
                        files.append(os.path.join(path, f))
        if files:
            self.file_dropped.emit(files)


class ContentArea(QWidget):
    file_dropped = pyqtSignal(list)
    fullscreen_requested = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.drag_area = DragDropArea()
        self.drag_area.file_dropped.connect(self.file_dropped.emit)
        
        # Splitter for transcript and video
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.transcript_view = TranscriptView()
        self.video_player = VideoPlayer()
        
        # Bubble up signal
        self.video_player.fullscreen_requested.connect(self.fullscreen_requested.emit)
        
        # Give specific stretch indices so text view gets space
        self.splitter.addWidget(self.transcript_view)
        self.splitter.addWidget(self.video_player)
        self.splitter.setSizes([300, 400])
        
        # Connect clicks on transcript to seek video
        self.transcript_view.timestamp_clicked.connect(self.video_player.seek_to)
        
        self.layout.addWidget(self.drag_area)
        self.layout.addWidget(self.splitter)
        
        self.splitter.setVisible(False)
        
    def load_content(self, video_path, txt_path):
        self.drag_area.setVisible(False)
        self.splitter.setVisible(True)
        self.video_player.load_video(video_path)
        self.transcript_view.load_transcript(txt_path)
        
    def search_text(self, query):
        if self.splitter.isVisible():
            return self.transcript_view.search_and_highlight(query)
        return (0, 0)
        
    def set_fullscreen_layout(self, is_fs):
        if is_fs:
            self.transcript_view.setVisible(False)
        else:
            self.transcript_view.setVisible(True)
