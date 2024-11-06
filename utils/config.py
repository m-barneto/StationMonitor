from typing import Any
import pyjson5


class Config:
    conf = None

    @staticmethod
    def get() -> Any:
        if Config.conf is None:
            with open("./config.jsonc", encoding="utf-8") as f:
                Config.conf = pyjson5.load(f)
        return Config.conf
