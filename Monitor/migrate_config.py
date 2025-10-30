import importlib
import json
import json5
from pathlib import Path

LATEST_VERSION = 1

INSTALL_DIR = Path.home() / "StationMonitor"
MONITOR = INSTALL_DIR / "Monitor"
CONFIG_PATH = MONITOR / "config.json"
BACKUP_CONFIG = Path.home() / "config_backup.json"

def load_config(path: Path):
    with open(path, "r") as f:
        return json5.load(f)

def save_config(path: Path, config):
    with open(path, "w") as f:
        json.dump(config, f, indent=4)

def migrate_config():
    config = load_config(BACKUP_CONFIG)
    version = config.get("version", 0)

    while version < LATEST_VERSION:
        next_version = version + 1
        migration_module = f"migrations.v{version}_to_v{next_version}"
        print(f"Applying migration: {migration_module}")

        mod = importlib.import_module(migration_module)
        config = mod.migrate(config)
        version = config["version"]

    save_config(CONFIG_PATH, config)
    print(f"Config migrated to version {version}.")

if __name__ == "__main__":
    migrate_config()