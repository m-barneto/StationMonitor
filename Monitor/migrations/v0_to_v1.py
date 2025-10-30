def migrate(config: dict) -> dict:
    config["version"] = 1

    if "leds" in config:
        del config["leds"]
    
    if "reflectiveSensors" in config:
        del config["reflectiveSensors"]

    if "distanceSensors" in config:
        del config["distanceSensors"]

    for entry in config["longDistanceSensors"]:
        if "indicatorPin" in entry:
            del entry["indicatorPin"]
        if "pwmChannel" in entry:
            del entry["pwmChannel"]
    
    if "alarmDuration" in config:
        if config["alarmDuration"] != 1200:
            config["alarmDuration"] = 1200

    return config