def migrate(config: dict) -> dict:
    config["version"] = 3

    config["standalone"] = {
        "pruneHours": 48,
        "pruneFrequencyMins": 60,
        "maxCacheEvents": 10000 #TBD
    }

    return config