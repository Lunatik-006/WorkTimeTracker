import tkinter as tk
from tkinter import ttk

from core.settings import Settings
from core.tts import list_voices
from core.i18n import tr, set_language


class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, settings: Settings):
        super().__init__(parent)
        self.parent = parent
        self.settings = settings
        self.title(tr("Settings"))
        self.resizable(False, False)

        ttk.Label(self, text=tr("Application language")).grid(row=0, column=0, sticky="w")
        self.var_app = tk.StringVar(value=settings.app_lang)
        self.combo_app = ttk.Combobox(self, textvariable=self.var_app, values=["ru", "en", "cn"], state="readonly")
        self.combo_app.grid(row=1, column=0, padx=5, pady=2, sticky="we")

        ttk.Label(self, text=tr("Speech language")).grid(row=2, column=0, sticky="w")
        self.var_tts_lang = tk.StringVar(value=settings.tts_lang)
        self.combo_tts = ttk.Combobox(self, textvariable=self.var_tts_lang, values=["ru", "en", "cn"], state="readonly")
        self.combo_tts.grid(row=3, column=0, padx=5, pady=2, sticky="we")
        self.combo_tts.bind("<<ComboboxSelected>>", self.update_voices)

        ttk.Label(self, text=tr("Notification sound")).grid(row=4, column=0, sticky="w")
        self._sound_map = {
            tr("None"): "none",
            tr("Beep"): "beep",
            tr("Horn"): "horn",
            tr("VoiceTTS"): "tts",
        }
        inv = {v: k for k, v in self._sound_map.items()}
        self.var_sound = tk.StringVar(value=inv.get(settings.sound, tr("None")))
        self.combo_sound = ttk.Combobox(self, textvariable=self.var_sound,
                                        values=list(self._sound_map.keys()), state="readonly")
        self.combo_sound.grid(row=5, column=0, padx=5, pady=2, sticky="we")
        self.combo_sound.bind("<<ComboboxSelected>>", self._sound_changed)

        ttk.Label(self, text=tr("Voice")).grid(row=6, column=0, sticky="w")
        self.var_voice = tk.StringVar(value=settings.voice or "")
        self.combo_voice = ttk.Combobox(self, textvariable=self.var_voice, state="readonly")
        self.combo_voice.grid(row=7, column=0, padx=5, pady=2, sticky="we")

        btn = ttk.Frame(self)
        btn.grid(row=8, column=0, pady=5, sticky="e")
        ttk.Button(btn, text=tr("OK"), command=self.on_ok).grid(row=0, column=0, padx=2)
        ttk.Button(btn, text=tr("Cancel"), command=self.destroy).grid(row=0, column=1, padx=2)

        self.columnconfigure(0, weight=1)
        self.update_voices()
        self._sound_changed()
        self.grab_set()
        self.transient(parent)
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def update_voices(self, event=None):
        lang = self.var_tts_lang.get()
        voices = list_voices(lang)
        names = [v[1] for v in voices]
        ids = [v[0] for v in voices]
        self.combo_voice['values'] = names
        if self.settings.voice in ids:
            idx = ids.index(self.settings.voice)
            self.var_voice.set(names[idx])
        elif names:
            self.var_voice.set(names[0])
            self.settings.voice = ids[0]
        else:
            self.var_voice.set("")
            self.settings.voice = None
        self._voice_map = dict(zip(names, ids))
        
    def _sound_changed(self, event=None):
        mode = self._sound_map.get(self.var_sound.get(), "none")
        state = "readonly" if mode == "tts" else "disabled"
        self.combo_voice.configure(state=state)

    def on_ok(self):
        self.settings.app_lang = self.var_app.get()
        self.settings.tts_lang = self.var_tts_lang.get()
        self.settings.sound = self._sound_map.get(self.var_sound.get(), "none")
        selected = self.var_voice.get()
        if selected:
            self.settings.voice = self._voice_map.get(selected)
        self.settings.save()
        set_language(self.settings.app_lang)
        if hasattr(self.parent, "apply_i18n"):
            self.parent.apply_i18n()
        self.destroy()
