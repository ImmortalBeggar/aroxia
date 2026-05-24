import os
from PIL import Image
from pydub import AudioSegment
import io

class MultimodalHandler:
    def __init__(self, temp_dir="temp"):
        self.temp_dir = temp_dir
        os.makedirs(temp_dir, exist_ok=True)

    def process_image(self, file_bytes):
        img = Image.open(io.BytesIO(file_bytes))
        # Perform any necessary resizing or conversion
        return img

    def process_voice(self, file_bytes, file_name="voice.ogg"):
        # Convert OGG (Telegram default) to WAV for easier processing if needed
        ogg_path = os.path.join(self.temp_dir, file_name)
        wav_path = ogg_path.replace(".ogg", ".wav")
        
        with open(ogg_path, "wb") as f:
            f.write(file_bytes)
            
        audio = AudioSegment.from_ogg(ogg_path)
        audio.export(wav_path, format="wav")
        return wav_path

    def cleanup(self):
        for f in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, f))
