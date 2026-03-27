import os
import re
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextBrowser
from PyQt6.QtCore import pyqtSignal, QUrl

class TranscriptView(QWidget):
    timestamp_clicked = pyqtSignal(int) # milliseconds
    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenLinks(False)
        self.text_browser.anchorClicked.connect(self.on_link_clicked)
        # Apply modern styling to text browser
        self.text_browser.setStyleSheet("""
            QTextBrowser { 
                font-family: 'Segoe UI', Tahoma;
                font-size: 14px; 
                padding: 15px; 
                line-height: 1.6; 
                background-color: #050505;
                color: #e0e0e0;
                border: none;
            }
        """)
        
        layout.addWidget(self.text_browser)
        self.current_html = ""
        
    def load_transcript(self, txt_path):
        if not os.path.exists(txt_path):
            self.text_browser.setHtml(f"<p style='color: #888;'>Dosya bulunamadı: {txt_path}</p>")
            return
            
        with open(txt_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        html_lines = []
        # Support both [HH:MM:SS.mmm] and [MM:SS.mmm] or simply [HH:MM:SS]
        pattern = re.compile(r"\[(\d{2}):(\d{2}):(\d{2})(?:\.\d+)?\](.*)")
        
        for line in lines:
            match = pattern.match(line.strip())
            if match:
                h, m, s, text = match.groups()
                ms = int((float(h)*3600 + float(m)*60 + float(s)) * 1000)
                # Vibrant red link with bold weight
                link = f'<a href="{ms}" style="text-decoration:none; color:#ff1f29;"><b>[{h}:{m}:{s}]</b></a>'
                html_lines.append(f"<div style='margin-bottom: 8px;'>{link} <span style='color:#ffffff;'>{text}</span></div>")
            else:
                html_lines.append(f"<div style='margin-bottom: 8px; color:#ffffff;'>{line.strip()}</div>")
                
        self.current_html = f"<div style='padding: 5px;'>{''.join(html_lines)}</div>"
        self.text_browser.setHtml(self.current_html)
        self.current_search_query = ""
        self.current_search_index = 0
        self.total_search_matches = 0
        
    def on_link_clicked(self, url: QUrl):
        ms = int(url.toString())
        self.timestamp_clicked.emit(ms)
        
    def search_and_highlight(self, query):
        if not query:
            self.text_browser.setHtml(self.current_html)
            self.current_search_query = ""
            self.current_search_index = 0
            self.total_search_matches = 0
            return (0, 0)
            
        if query != getattr(self, "current_search_query", ""):
            # New search
            self.current_search_query = query
            self.text_browser.setHtml(self.current_html)
            
            # Count matches in plain text
            plain_text = self.text_browser.toPlainText().lower()
            self.total_search_matches = plain_text.count(query.lower())
            
            if self.total_search_matches > 0:
                self.current_search_index = 1
                self.text_browser.moveCursor(self.text_browser.textCursor().MoveOperation.Start)
                self.text_browser.find(query)
            else:
                self.current_search_index = 0
        else:
            # Find next
            if self.total_search_matches > 0:
                found = self.text_browser.find(query)
                if found:
                    self.current_search_index += 1
                else: 
                    # Wrap around to the start
                    self.text_browser.moveCursor(self.text_browser.textCursor().MoveOperation.Start)
                    self.text_browser.find(query)
                    self.current_search_index = 1

        return (self.current_search_index, self.total_search_matches)
