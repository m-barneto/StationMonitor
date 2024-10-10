from typing import Any
import pyjson5


class Config:
    __conf = None

    @staticmethod
    def get() -> Any:
        if Config.__conf is None:
            with open("./config.jsonc", encoding="utf-8") as f:
                Config.__conf = pyjson5.load(f)
        return Config.__conf
