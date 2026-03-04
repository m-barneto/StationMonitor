from dataclasses import dataclass
from typing import Any, List
import json


@dataclass
class Stage:
    duration: int
    color: str
    label: str

    @staticmethod
    def from_dict(obj: Any) -> 'Stage':
        _duration = int(obj.get("duration"))
        _color = str(obj.get("color"))
        _label = str(obj.get("label"))
        return Stage(_duration, _color, _label)

    @staticmethod
    def to_dict(obj: 'Stage') -> dict:
        return {
            "duration": obj.duration,
            "color": obj.color,
            "label": obj.label
        }


@dataclass
class Guages:
    min: int
    max: int
    ticks: int
    segments: int
    window: int

    @staticmethod
    def from_dict(obj: Any) -> 'Guages':
        _min = int(obj.get("min"))
        _max = int(obj.get("max"))
        _ticks = int(obj.get("ticks"))
        _segments = int(obj.get("segments"))
        _window = int(obj.get("window"))
        return Guages(_min, _max, _ticks, _segments, _window)

    @staticmethod
    def to_dict(obj: 'Guages') -> dict:
        return {
            "min": obj.min,
            "max": obj.max,
            "ticks": obj.ticks,
            "segments": obj.segments,
            "window": obj.window
        }


@dataclass
class WebConfig:
    stages: List[Stage]
    guages: Guages

    @staticmethod
    def from_dict(obj: Any) -> 'WebConfig':
        _stages = [Stage.from_dict(s) for s in obj.get("stages", [])]
        _guages = Guages.from_dict(obj.get("guages"))
        return WebConfig(_stages, _guages)

    @staticmethod
    def to_dict(obj: 'WebConfig') -> dict:
        return {
            "stages": [Stage.to_dict(s) for s in obj.stages],
            "guages": Guages.to_dict(obj.guages)
        }


class WebConfigLoader:
    conf: WebConfig = None

    @staticmethod
    def get() -> WebConfig:
        if WebConfigLoader.conf is None:
            with open("./webconfig.json", encoding="utf-8") as f:
                WebConfigLoader.conf = WebConfig.from_dict(json.load(f))
        return WebConfigLoader.conf

    @staticmethod
    def save_config() -> None:
        with open("./webconfig.json", "w", encoding="utf-8") as f:
            json.dump(WebConfig.to_dict(WebConfigLoader.conf), f, indent=4)

    @staticmethod
    def reload_config() -> None:
        with open("./webconfig.json", encoding="utf-8") as f:
            WebConfigLoader.conf = WebConfig.from_dict(json.load(f))