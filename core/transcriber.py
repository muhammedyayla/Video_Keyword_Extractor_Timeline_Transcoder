import os
from PyQt6.QtCore import QThread, pyqtSignal

class TranscriptionWorker(QThread):
    progress_updated = pyqtSignal(int)
    transcription_finished = pyqtSignal(str, str) # video_path, txt_path
    error_occurred = pyqtSignal(str)
    
    def __init__(self, video_path, data_manager):
        super().__init__()
        self.video_path = video_path
        self.data_manager = data_manager
        
    def run(self):
        try:
            self.progress_updated.emit(5) # Loading model
            import warnings
            warnings.filterwarnings("ignore") # Ignore FP16 warnings on CPU
            
            # Use 'base' or 'tiny' for reasonable speed on average CPUs, or 'small' if better quality
            import whisper
            model = whisper.load_model("base") 
            self.progress_updated.emit(20) # Model loaded, starting
            
            # Using prompt to help with Turkish? Whisper auto-detects.
            result = model.transcribe(self.video_path, verbose=False)
            self.progress_updated.emit(90) # Transcribed, saving
            
            # format and save
            base_name = os.path.splitext(os.path.basename(self.video_path))[0]
            # Ensure transcriptions directory exists
            os.makedirs("transcriptions", exist_ok=True)
            txt_path = os.path.join("transcriptions", f"{base_name}.txt")
            
            # Prevent overwriting if file already exists with same name? Just append _v2 if needed, or overwrite.
            # We'll just overwrite for simplicity given the requirements.
            
            with open(txt_path, 'w', encoding='utf-8') as f:
                for segment in result["segments"]:
                    start = segment['start']
                    text = segment['text']
                    
                    # format start time HH:MM:SS
                    s_total = int(start)
                    m, s = divmod(s_total, 60)
                    h, m = divmod(m, 60)
                    
                    stamp = f"[{h:02d}:{m:02d}:{s:02d}.000]"
                    f.write(f"{stamp} {text.strip()}\n")
                    
            self.data_manager.add_record(self.video_path, txt_path)
            
            self.progress_updated.emit(100)
            self.transcription_finished.emit(self.video_path, txt_path)
            
        except Exception as e:
            self.error_occurred.emit(str(e))
