def migrate(config: dict) -> dict:
    config["version"] = 2

    # add led config that points from led_strip_id -> zone_id
    # add enabled? flag for led system
    idx = 0
    for sensor in config["longDistanceSensors"]:
        if "ledStripIndex" not in sensor:
            sensor["ledStripIndex"] = idx
            idx += 1
    
    if "ledsEnabled" not in config:
        config["ledsEnabled"] = False

    return config