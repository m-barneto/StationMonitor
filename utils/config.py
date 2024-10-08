import pyjson5

class Config:
    __conf = None
    
    @staticmethod
    def get():
        if Config.__conf is None:
            with open("./config.jsonc") as f:
                Config.__conf = pyjson5.load(f)
                print(Config.__conf)
        return Config.__conf