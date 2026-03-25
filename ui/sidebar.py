import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QListWidget, QLabel, QListWidgetItem
)
from PyQt6.QtCore import pyqtSignal

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
        
        label = QLabel("Eski Deşifrelerim")
        label.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 5px;")
        layout.addWidget(label)
        
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
                padding: 10px;
                border-bottom: 1px solid #564d4d;
                color: #ffffff;
            }
            QListWidget::item:selected {
                background-color: #831010;
                color: #ffffff;
            }
        """)
        layout.addWidget(self.history_list)
        
        self.refresh_history()
        
    def refresh_history(self, filter_text=""):
        self.history_list.clear()
        records = self.data_manager.get_all_records()
        # reverse to show newest first if app saves sequentially
        for record in reversed(records):
            video_name = os.path.basename(record['video_path'])
            if filter_text.lower() in video_name.lower() or self.check_txt_content(record['txt_path'], filter_text):
                item = QListWidgetItem(video_name)
                # Store paths in UserRoles
                item.setData(32, record['video_path']) # Qt.ItemDataRole.UserRole represents 32
                item.setData(33, record['txt_path'])
                item.setToolTip(record['video_path'])
                self.history_list.addItem(item)
                
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
