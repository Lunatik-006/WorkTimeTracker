# Data models for activities and timer configurations

class Activity:
    """Single activity entry inside a timer."""

    def __init__(self, name: str, duration: int):
        self.name = name
        # Duration of the activity in seconds
        self.duration = duration

    def to_dict(self):
        """Serialize the activity to a JSON compatible dict."""
        return {"name": self.name, "duration": self.duration}

    @staticmethod
    def from_dict(data):
        """Create Activity instance from dictionary representation."""
        return Activity(data["name"], data["duration"])


class TimerConfig:
    """Configuration of one Pomodoro timer preset."""

    def __init__(self, name: str, description: str = "", sets: int = 1,
                 rest_activity: int = 5 * 60, rest_set: int = 15 * 60):
        # Human readable name and optional description
        self.name = name
        self.description = description
        # Sequence of Activity objects
        self.activities = []
        self.sets = sets
        self.rest_activity = rest_activity
        self.rest_set = rest_set

    def to_dict(self):
        """Serialize the timer configuration to a JSON compatible dict."""
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
        """Create TimerConfig from dictionary data."""
        cfg = TimerConfig(
            data["name"],
            data.get("description", ""),
            data.get("sets", 1),
            data.get("rest_activity", 300),
            data.get("rest_set", 900),
        )
        cfg.activities = [Activity.from_dict(a) for a in data.get("activities", [])]
        return cfg
