import asyncio
from collections import deque
from datetime import datetime, timedelta
import json
from pathlib import Path
from utils.sensor_event import EventData
from utils.config import Config

class CacheManager:
    event_cache: deque[EventData]
    cache_path: Path = Path("cache.json")
    def __init__(self):
        # load from disk if file is there
        if (CacheManager.cache_path.exists()):
            # load it into the queue
            with CacheManager.cache_path.open("r", encoding="utf-8") as f:
                CacheManager.event_cache = deque(json.load(f), Config.get().standalone.maxCacheEvents)
            
            # Delete file
            CacheManager.cache_path.unlink()
        else:
            CacheManager.event_cache = deque(maxlen=Config.get().standalone.maxCacheEvents)

    @staticmethod
    def save_cache():
        if CacheManager.cache_path.exists():
            CacheManager.cache_path.unlink()
            
        with CacheManager.cache_path.open("w", encoding="utf-8") as f:
            json.dump(list(CacheManager.event_cache), f, ensure_ascii=False, indent=4)

    @staticmethod
    def prune_events():
        # loop through the event cache backwards and remove events that are older than x hours.
        #TODO this should be hours not minutes
        cutoff = datetime.now() - timedelta(minutes=Config.get().standalone.pruneHours)
        while CacheManager.event_cache:
            start_time = datetime.fromisoformat(CacheManager.event_cache[0].body.startTime)
            print("Cache looking at time: ", start_time)
            if start_time >= cutoff:
                print("Time is >= cutoff, breaking now")
                break
            print("Popping off the queue")
            CacheManager.event_cache.popleft()

    async def loop(self) -> None:
        #Prune every x minutes
        while True:
            # Prune at startup if we're loading from disk
            print("Pruning")
            CacheManager.prune_events()
            await asyncio.sleep(Config.get().standalone.pruneFrequencyMins * 60)