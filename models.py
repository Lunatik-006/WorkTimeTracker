# Data models for activities and timer configurations

class Activity:
    def __init__(self, name: str, duration: int):
        self.name = name
        self.duration = duration  # seconds

    def to_dict(self):
        return {"name": self.name, "duration": self.duration}

    @staticmethod
    def from_dict(data):
        return Activity(data["name"], data["duration"])


class TimerConfig:
    def __init__(self, name: str, description: str = "", sets: int = 1,
                 rest_activity: int = 5 * 60, rest_set: int = 15 * 60):
        self.name = name
        self.description = description
        self.activities = []  # list of Activity
        self.sets = sets
        self.rest_activity = rest_activity
        self.rest_set = rest_set

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "sets": self.sets,
            "rest_activity": self.rest_activity,
            "rest_set": self.rest_set,
            "activities": [a.to_dict() for a in self.activities],
        }

    @staticmethod
    def from_dict(data):
        cfg = TimerConfig(
            data["name"],
            data.get("description", ""),
            data.get("sets", 1),
            data.get("rest_activity", 300),
            data.get("rest_set", 900),
        )
        cfg.activities = [Activity.from_dict(a) for a in data.get("activities", [])]
        return cfg
