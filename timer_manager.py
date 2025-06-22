import json
import os
from models import TimerConfig

CONFIG_DIR = "timers"


class TimerManager:
    """Load and store timer configurations from disk."""

    def __init__(self, directory: str = CONFIG_DIR):
        self.directory = directory
        os.makedirs(directory, exist_ok=True)
        self.timers = {}
        self.load_timers()

    def _path(self, name: str) -> str:
        return os.path.join(self.directory, f"{name}.json")

    def load_timers(self):
        self.timers = {}
        if not os.path.exists(self.directory):
            return
        for fn in os.listdir(self.directory):
            if fn.endswith(".json"):
                with open(os.path.join(self.directory, fn), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    cfg = TimerConfig.from_dict(data)
                    self.timers[cfg.name] = cfg

    def save_timer(self, timer: TimerConfig):
        with open(self._path(timer.name), "w", encoding="utf-8") as f:
            json.dump(timer.to_dict(), f, indent=2)
        self.timers[timer.name] = timer

    def delete_timer(self, name: str):
        if name in self.timers:
            path = self._path(name)
            if os.path.exists(path):
                os.remove(path)
            del self.timers[name]

    def rename_timer(self, old_name: str, new_name: str):
        if old_name == new_name:
            return
        timer = self.timers.pop(old_name)
        timer.name = new_name
        old_path = self._path(old_name)
        new_path = self._path(new_name)
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
        self.save_timer(timer)
