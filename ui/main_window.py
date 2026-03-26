import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QLineEdit, QFileDialog, QProgressBar, QMessageBox, QLabel
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, pyqtSignal
from .sidebar import Sidebar
from .content_area import ContentArea
from core.transcriber import TranscriptionWorker
from core.data_manager import DataManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Keyword Extractor - Deşifre Programı | Developed by Muhammet Yayla")
        self.setWindowIcon(QIcon("images/icon.jpg"))
        self.resize(1200, 800)
        
        self.data_manager = DataManager()
        
        # Main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Sub-sections
        self.sidebar = Sidebar(self.data_manager)
        self.content_area = ContentArea()
        
        # Right layout (Top bar + Content)
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(10, 10, 10, 10)
        
        # Top bar
        # Top bar container
        self.top_bar_container = QWidget()
        top_bar_main_layout = QHBoxLayout(self.top_bar_container)
        top_bar_main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.btn_upload_file = QPushButton("Dosya Yükle")
        self.btn_upload_file.setMinimumHeight(35)
        
        self.btn_upload_folder = QPushButton("Klasör Yükle")
        self.btn_upload_folder.setMinimumHeight(35)
        
        self.search_bar_top = QLineEdit()
        self.search_bar_top.setPlaceholderText("Şu an açılan deşifre metninde kelime ara...")
        self.search_bar_top.setMinimumHeight(35)
        
        self.search_button = QPushButton("Ara / Sonraki")
        self.search_button.setMinimumHeight(35)
        
        self.search_result_label = QLabel("")
        self.search_result_label.setStyleSheet("color: #ffffff; padding: 0 10px; font-weight: bold;")
        
        top_bar_main_layout.addWidget(self.btn_upload_file)
        top_bar_main_layout.addWidget(self.btn_upload_folder)
        top_bar_main_layout.addSpacing(20)
        top_bar_main_layout.addWidget(self.search_bar_top, stretch=1)
        top_bar_main_layout.addWidget(self.search_result_label)
        top_bar_main_layout.addWidget(self.search_button)
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMinimumHeight(25)
        
        right_layout.addWidget(self.top_bar_container)
        right_layout.addWidget(self.progress_bar)
        right_layout.addWidget(self.content_area, stretch=1)
        
        # Add to main layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(right_container, stretch=1)
        
        # Connections
        self.btn_upload_file.clicked.connect(self.upload_file)
        self.btn_upload_folder.clicked.connect(self.upload_folder)
        self.content_area.file_dropped.connect(self.start_transcription)
        self.content_area.fullscreen_requested.connect(self.toggle_fullscreen_mode)
        self.sidebar.history_item_clicked.connect(self.load_history_item)
        self.search_button.clicked.connect(self.search_current_text)
        self.search_bar_top.returnPressed.connect(self.search_current_text)
        
        # Worker thread reference
        self.worker = None
        self.pending_queue = [] # for folder uploading
        
    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Video Seç", "", "Video Dosyaları (*.mp4 *.mkv *.mxf *.avi *.mov)")
        if file_path:
            self.start_transcription([file_path])
            
    def upload_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Klasör Seç")
        if folder_path:
            video_files = []
            for f in os.listdir(folder_path):
                if f.lower().endswith(('.mp4', '.mkv', '.mxf', '.avi', '.mov')):
                    video_files.append(os.path.join(folder_path, f))
            if video_files:
                self.start_transcription(video_files)
            else:
                QMessageBox.information(self, "Bilgi", "Seçilen klasörde desteklenen video dosyası bulunamadı.")
                
    def start_transcription(self, files):
        if not files: return
        self.pending_queue.extend(files)
        # Notify user if multiple files were added
        if len(files) > 1:
            QMessageBox.information(self, "Bilgi", f"{len(files)} adet video sıraya eklendi. Sırayla deşifre edilecekler.")
        
        self.process_next_in_queue()
        
    def process_next_in_queue(self):
        if self.worker is not None and self.worker.isRunning():
            return # Already running
            
        if not self.pending_queue:
            self.progress_bar.setVisible(False)
            return
            
        video_path = self.pending_queue.pop(0)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat(f"Deşifre ediliyor: {os.path.basename(video_path)}... %p%")
        
        self.worker = TranscriptionWorker(video_path, self.data_manager)
        self.worker.progress_updated.connect(self.progress_bar.setValue)
        self.worker.transcription_finished.connect(self.on_transcription_finished)
        self.worker.error_occurred.connect(self.on_transcription_error)
        self.worker.start()
        
    def on_transcription_finished(self, video_path, txt_path):
        self.sidebar.refresh_history()
        self.load_playback_view(video_path, txt_path)
        
        if self.pending_queue:
            self.process_next_in_queue()
        else:
            QMessageBox.information(self, "Tamamlandı", "Tüm videoların deşifre işlemi tamamlandı!")
            self.progress_bar.setVisible(False)
            
    def on_transcription_error(self, error_msg):
        QMessageBox.critical(self, "Hata", f"Deşifre sırasında hata oluştu:\n{error_msg}")
        self.process_next_in_queue()
        
    def load_history_item(self, video_path, txt_path):
        self.load_playback_view(video_path, txt_path)
        
    def load_playback_view(self, video_path, txt_path):
        self.content_area.load_content(video_path, txt_path)
        
    def search_current_text(self):
        query = self.search_bar_top.text()
        if query:
            current, total = self.content_area.search_text(query)
            if total > 0:
                self.search_result_label.setText(f"{current} / {total}")
            else:
                self.search_result_label.setText("Bulunamadı")
        else:
            self.search_result_label.setText("")
            
    def toggle_fullscreen_mode(self, is_fs):
        if is_fs:
            self.sidebar.setVisible(False)
            self.top_bar_container.setVisible(False)
            self.content_area.set_fullscreen_layout(True)
            self.showFullScreen()
        else:
            self.sidebar.setVisible(True)
            self.top_bar_container.setVisible(True)
            self.content_area.set_fullscreen_layout(False)
            self.showNormal()
