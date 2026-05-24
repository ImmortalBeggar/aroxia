from gtts import gTTS
import os
import io

class SpeechModule:
    def __init__(self, temp_dir="temp"):
        self.temp_dir = temp_dir
        os.makedirs(temp_dir, exist_ok=True)

    def text_to_speech(self, text, lang='en', slow=False):
        """Converts text to an OGG file with configurable language and speed."""
        tts = gTTS(text=text, lang=lang, slow=slow)
        mp3_path = os.path.join(self.temp_dir, "response.mp3")
        ogg_path = os.path.join(self.temp_dir, "response.ogg")
        
        tts.save(mp3_path)
        os.system(f"ffmpeg -i {mp3_path} -acodec libopus -y {ogg_path} > /dev/null 2>&1")
        return ogg_path

    def cleanup(self):
        for f in os.listdir(self.temp_dir):
            if f.startswith("response"):
                os.remove(os.path.join(self.temp_dir, f))
