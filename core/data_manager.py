import json
import os

class DataManager:
    def __init__(self, db_file="transcriptions/metadata.json"):
        self.db_file = db_file
        self.records = []
        os.makedirs(os.path.dirname(os.path.abspath(self.db_file)), exist_ok=True)
        self.load()
        
    def load(self):
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    self.records = json.load(f)
            except Exception:
                self.records = []
        else:
            self.records = []
            
    def save(self):
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.records, f, ensure_ascii=False, indent=4)
            
    def add_record(self, video_path, txt_path):
        # Prevent exact duplicates
        for r in self.records:
            if r['video_path'] == video_path and r['txt_path'] == txt_path:
                return
        self.records.append({'video_path': video_path, 'txt_path': txt_path})
        self.save()
        
    def get_all_records(self):
        return self.records
