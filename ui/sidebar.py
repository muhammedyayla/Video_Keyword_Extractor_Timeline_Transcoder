import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget, QLabel, QListWidgetItem, QPushButton, QMessageBox
)
from PyQt6.QtCore import pyqtSignal, Qt

class HistoryItemWidget(QWidget):
    delete_requested = pyqtSignal(str, str) # video_path, txt_path

    def __init__(self, video_name, video_path, txt_path):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)
        
        self.label = QLabel(video_name)
        self.label.setStyleSheet("color: #e0e0e0; font-size: 13px; font-weight: 500;")
        self.label.setToolTip(video_path)
        layout.addWidget(self.label)
        
        layout.addStretch()
        
        self.del_btn = QPushButton("✕")
        self.del_btn.setFixedSize(24, 24)
        self.del_btn.setToolTip("Kaydı sil")
        self.del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.del_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: #555;
                font-size: 12px;
                font-weight: bold;
                border: 1px solid #333;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #e50914;
                color: white;
                border: none;
            }
        """)
        self.del_btn.clicked.connect(lambda: self.delete_requested.emit(video_path, txt_path))
        layout.addWidget(self.del_btn)

class Sidebar(QWidget):
    history_item_clicked = pyqtSignal(str, str) # video_path, txt_path

    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        
        # Allow enough width
        self.setMinimumWidth(250)
        self.setMaximumWidth(350)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        header_layout = QHBoxLayout()
        label = QLabel("Eski Deşifrelerim")
        label.setStyleSheet("font-weight: bold; font-size: 16px;")
        header_layout.addWidget(label)
        
        self.delete_all_btn = QPushButton("Tümünü Sil")
        self.delete_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: #888;
                border: 1px solid #333;
                border-radius: 4px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #333;
                color: #e50914;
                border: 1px solid #e50914;
            }
        """)
        self.delete_all_btn.clicked.connect(self.delete_all_confirm)
        header_layout.addWidget(self.delete_all_btn)
        
        layout.addLayout(header_layout)
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Geçmişte veya isimde ara...")
        self.search_bar.textChanged.connect(self.filter_history)
        layout.addWidget(self.search_bar)
        
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.on_item_clicked)
        self.history_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #564d4d;
                border-radius: 5px;
                background-color: #000000;
            }
            QListWidget::item {
                border-bottom: 1px solid #564d4d;
            }
            QListWidget::item:selected {
                background-color: #1a1a1a;
            }
        """)
        layout.addWidget(self.history_list)
        
        self.refresh_history()
        
    def refresh_history(self, filter_text=""):
        self.history_list.clear()
        records = self.data_manager.get_all_records()
        
        # Hide delete all button if no records
        self.delete_all_btn.setVisible(len(records) > 0)
        
        # reverse to show newest first
        for record in reversed(records):
            video_name = os.path.basename(record['video_path'])
            if filter_text.lower() in video_name.lower() or self.check_txt_content(record['txt_path'], filter_text):
                item = QListWidgetItem(self.history_list)
                item.setSizeHint(HistoryItemWidget(video_name, record['video_path'], record['txt_path']).sizeHint())
                
                # Store paths in UserRoles
                item.setData(32, record['video_path']) 
                item.setData(33, record['txt_path'])
                
                widget = HistoryItemWidget(video_name, record['video_path'], record['txt_path'])
                widget.delete_requested.connect(self.delete_record)
                
                self.history_list.addItem(item)
                self.history_list.setItemWidget(item, widget)
                
    def check_txt_content(self, txt_path, query):
        if not query: return True
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                return query.lower() in content
        except Exception:
            return False

    def filter_history(self, text):
        self.refresh_history(text)
        
    def on_item_clicked(self, item):
        video_path = item.data(32)
        txt_path = item.data(33)
        self.history_item_clicked.emit(video_path, txt_path)

    def delete_record(self, video_path, txt_path):
        reply = QMessageBox.question(self, "Silme Onayı", 
                                   f"{os.path.basename(video_path)} kaydını silmek istediğinize emin misiniz?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.data_manager.delete_record(video_path, txt_path)
            self.refresh_history(self.search_bar.text())

    def delete_all_confirm(self):
        reply = QMessageBox.question(self, "Tümünü Sil", 
                                   "Tüm geçmişi silmek istediğinize emin misiniz?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.data_manager.delete_all_records()
            self.refresh_history()
