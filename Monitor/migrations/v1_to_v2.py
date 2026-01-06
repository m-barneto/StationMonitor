def migrate(config: dict) -> dict:
    config["version"] = 2

    # add led config that points from led_strip_id -> zone_id
    # add enabled? flag for led system
    config["ledStrips"] = [
        {
            "ledStrip": 0,
            "zone": "A"
        },
        {
            "ledStrip": 1,
            "zone": "B"
        }
    ]


    return config