def migrate(config: dict) -> dict:
    config["version"] = 2

    # add led config that points from led_strip_id -> zone_id
    # add enabled? flag for led system
    

    return config