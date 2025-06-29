try:
    import pyttsx3
except Exception:
    pyttsx3 = None

_engine = None


def _init_engine():
    """Initialise the pyttsx3 engine lazily."""
    global _engine
    if pyttsx3 is None:
        return None
    if _engine is None:
        try:
            _engine = pyttsx3.init()
        except Exception:
            _engine = None
    return _engine


def list_voices(language: str | None = None):
    """Return available voices as (id, name) tuples filtered by language."""
    engine = _init_engine()
    if engine is None:
        return []
    voices = []
    for v in engine.getProperty("voices"):
        langs = getattr(v, "languages", [])
        langs = [l.decode() if isinstance(l, bytes) else str(l) for l in langs]
        if language is None or any(language in l for l in langs):
            voices.append((v.id, v.name))
    return voices


def speak(text: str, voice_id: str | None = None) -> None:
    """Speak the provided text if TTS support is available."""
    engine = _init_engine()
    if engine is None:
        return
    if voice_id:
        try:
            engine.setProperty("voice", voice_id)
        except Exception:
            pass
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception:
        pass
