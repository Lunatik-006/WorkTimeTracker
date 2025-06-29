import json
import os

SETTINGS_FILE = "settings.json"


class Settings:
    def __init__(self, app_lang: str = "en", tts_lang: str = "en", voice: str | None = None, sound: str = "tts"):
        self.app_lang = app_lang
        self.tts_lang = tts_lang
        self.voice = voice
        self.sound = sound

    @classmethod
    def load(cls, path: str = SETTINGS_FILE):
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return cls(
                    data.get("app_lang", "en"),
                    data.get("tts_lang", "en"),
                    data.get("voice"),
                    data.get("sound", "tts")
                )
            except Exception:
                pass
        return cls()

    def save(self, path: str = SETTINGS_FILE):
        data = {
            "app_lang": self.app_lang,
            "tts_lang": self.tts_lang,
            "voice": self.voice,
            "sound": self.sound,
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass
