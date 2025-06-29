import tkinter as tk
from tkinter import ttk

from core.settings import Settings
from core.tts import list_voices


class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, settings: Settings):
        super().__init__(parent)
        self.settings = settings
        self.title("Settings")
        self.resizable(False, False)

        ttk.Label(self, text="Application language").grid(row=0, column=0, sticky="w")
        self.var_app = tk.StringVar(value=settings.app_lang)
        self.combo_app = ttk.Combobox(self, textvariable=self.var_app, values=["ru", "en", "cn"], state="readonly")
        self.combo_app.grid(row=1, column=0, padx=5, pady=2, sticky="we")

        ttk.Label(self, text="Speech language").grid(row=2, column=0, sticky="w")
        self.var_tts_lang = tk.StringVar(value=settings.tts_lang)
        self.combo_tts = ttk.Combobox(self, textvariable=self.var_tts_lang, values=["ru", "en", "cn"], state="readonly")
        self.combo_tts.grid(row=3, column=0, padx=5, pady=2, sticky="we")
        self.combo_tts.bind("<<ComboboxSelected>>", self.update_voices)

        ttk.Label(self, text="Voice").grid(row=4, column=0, sticky="w")
        self.var_voice = tk.StringVar(value=settings.voice or "")
        self.combo_voice = ttk.Combobox(self, textvariable=self.var_voice, state="readonly")
        self.combo_voice.grid(row=5, column=0, padx=5, pady=2, sticky="we")

        btn = ttk.Frame(self)
        btn.grid(row=6, column=0, pady=5, sticky="e")
        ttk.Button(btn, text="OK", command=self.on_ok).grid(row=0, column=0, padx=2)
        ttk.Button(btn, text="Cancel", command=self.destroy).grid(row=0, column=1, padx=2)

        self.columnconfigure(0, weight=1)
        self.update_voices()
        self.grab_set()
        self.transient(parent)

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

    def on_ok(self):
        self.settings.app_lang = self.var_app.get()
        self.settings.tts_lang = self.var_tts_lang.get()
        selected = self.var_voice.get()
        if selected:
            self.settings.voice = self._voice_map.get(selected)
        self.settings.save()
        self.destroy()
