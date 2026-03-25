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
    
    # Global palette requested by user: #b32d24, #000000, #ffffff, #564d4d, #831010
    dark_stylesheet = """
    QMainWindow, QWidget {
        background-color: #171717;
        color: #f2f2f2;
    }
    QPushButton {
        background-color: #831010;
        color: #ffffff;
        border: 1px solid #564d4d;
        border-radius: 5px;
        padding: 5px 15px;
        min-height: 25px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #b32d24;
    }
    QPushButton:pressed {
        background-color: #564d4d;
    }
    QLineEdit {
        background-color: #564d4d;
        color: #ffffff;
        border: 1px solid #831010;
        border-radius: 3px;
        padding: 5px;
    }
    QListWidget {
        background-color: #000000;
        color: #ffffff;
        border: 1px solid #564d4d;
    }
    QListWidget::item {
        color: #ffffff;
    }
    QListWidget::item:selected {
        background-color: #831010;
        color: #ffffff;
    }
    QProgressBar {
        border: 1px solid #564d4d;
        border-radius: 5px;
        text-align: center;
        color: white;
    }
    QProgressBar::chunk {
        background-color: #b32d24;
    }
    QTextBrowser {
        background-color: #000000;
        color: #ffffff;
        border: 1px solid #564d4d;
    }
    QSplitter::handle {
        background-color: #564d4d;
    }
    QSlider::groove:horizontal {
        height: 6px;
        background: #564d4d;
        border-radius: 3px;
    }
    QSlider::handle:horizontal {
        background: #b32d24;
        width: 14px;
        margin-top: -4px;
        margin-bottom: -4px;
        border-radius: 7px;
    }
    QLabel {
        color: #ffffff;
    }
    QMessageBox {
        background-color: #000000;
        color: #ffffff;
    }
    QMessageBox QLabel {
        color: #ffffff;
    }
    QMessageBox QPushButton {
        background-color: #831010;
        min-width: 80px;
    }
    """
    app.setStyleSheet(dark_stylesheet)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
