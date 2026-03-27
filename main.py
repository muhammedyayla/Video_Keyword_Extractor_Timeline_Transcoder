import sys
import os
import ctypes

# Fix for PyInstaller and Torch DLLs on Windows (WinError 1114)
# This must happen BEFORE importing torch
if getattr(sys, 'frozen', False):
    # PyInstaller's internal path
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    # Add torch\lib to DLL search path
    for torch_lib_path in [
        os.path.join(base_path, "_internal", "torch", "lib"),
        os.path.join(base_path, "torch", "lib")
    ]:
        if os.path.exists(torch_lib_path):
            try:
                os.add_dll_directory(torch_lib_path)
            except Exception:
                pass

# Import whisper and torch FIRST to prevent DLL conflicts with PyQt6 on Windows
import torch
import whisper

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from ui.main_window import MainWindow

def main():
    # Fix Taskbar Icon on Windows
    try:
        myappid = 'muhammedyayla.video.keyword.extractor.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

    # Make sure transcriptions directory exists
    os.makedirs("transcriptions", exist_ok=True)
    
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("images/icon.jpg"))
    
    # Optional: Apply some basic styling for modern look
    app.setStyle("Fusion")
    
    # Global palette: #e50914 (Vibrant Red), #0a0a0a (Deep Black), #ffffff (White), #1f1f1f (Dark Gray), #888888 (Muted Gray)
    dark_stylesheet = """
    QMainWindow, QWidget {
        background-color: #0a0a0a;
        color: #f2f2f2;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    QPushButton {
        background-color: #e50914;
        color: #ffffff;
        border: none;
        border-radius: 4px;
        padding: 6px 16px;
        font-size: 13px;
        font-weight: 600;
    }
    QPushButton:hover {
        background-color: #ff1f29;
    }
    QPushButton:pressed {
        background-color: #b20710;
    }
    QPushButton:disabled {
        background-color: #333333;
        color: #888888;
    }
    QLineEdit {
        background-color: #1a1a1a;
        color: #ffffff;
        border: 1px solid #333333;
        border-radius: 4px;
        padding: 8px;
        selection-background-color: #e50914;
    }
    QLineEdit:focus {
        border: 1px solid #e50914;
    }
    QListWidget {
        background-color: #0d0d0d;
        color: #ffffff;
        border: 1px solid #1a1a1a;
        border-radius: 4px;
        outline: none;
    }
    QListWidget::item {
        padding: 2px;
    }
    QListWidget::item:selected {
        background-color: #1f1f1f;
        border-left: 3px solid #e50914;
    }
    QProgressBar {
        border: 1px solid #1a1a1a;
        border-radius: 10px;
        background-color: #1a1a1a;
        text-align: center;
        color: white;
        height: 12px;
        font-size: 10px;
    }
    QProgressBar::chunk {
        background-color: #e50914;
        border-radius: 9px;
    }
    QTextBrowser {
        background-color: #050505;
        color: #e0e0e0;
        border: 1px solid #1a1a1a;
        border-radius: 4px;
        selection-background-color: #e50914;
        selection-color: #ffffff;
    }
    QSplitter::handle {
        background-color: #1a1a1a;
    }
    QScrollBar:vertical {
        border: none;
        background: #0a0a0a;
        width: 10px;
        margin: 0px 0px 0px 0px;
    }
    QScrollBar::handle:vertical {
        background: #333333;
        min-height: 20px;
        border-radius: 5px;
    }
    QScrollBar::handle:vertical:hover {
        background: #e50914;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    QScrollBar:horizontal {
        border: none;
        background: #0a0a0a;
        height: 10px;
        margin: 0px 0px 0px 0px;
    }
    QScrollBar::handle:horizontal {
        background: #333333;
        min-width: 20px;
        border-radius: 5px;
    }
    QScrollBar::handle:horizontal:hover {
        background: #e50914;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }
    QSlider::groove:horizontal {
        height: 4px;
        background: #333333;
        border-radius: 2px;
    }
    QSlider::handle:horizontal {
        background: #e50914;
        border: none;
        width: 14px;
        height: 14px;
        margin: -5px 0;
        border-radius: 7px;
    }
    QSlider::handle:horizontal:hover {
        background: #ff1f29;
    }
    QMessageBox {
        background-color: #121212;
    }
    QMessageBox QLabel {
        color: #ffffff;
        font-size: 14px;
    }
    """
    app.setStyleSheet(dark_stylesheet)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
