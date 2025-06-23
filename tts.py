try:
    import pyttsx3
except Exception:
    pyttsx3 = None

_engine = None


def speak(text: str) -> None:
    """Speak the provided text if TTS support is available."""
    global _engine
    if pyttsx3 is None:
        return
    if _engine is None:
        try:
            _engine = pyttsx3.init()
        except Exception:
            _engine = None
            return
    try:
        _engine.say(text)
        _engine.runAndWait()
    except Exception:
        pass
