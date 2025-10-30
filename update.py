import shutil
import subprocess
import tempfile
import zipfile
import requests
from pathlib import Path

# ========== CONFIG ==========
SERVICE_NAME = "stationmonitor"
GITHUB_REPO = "m-barneto/StationMonitor"
INSTALL_DIR = Path.home() / "StationMonitor"
BACKUP_FILE = Path.home() / "config_backup.json"
MONITOR = INSTALL_DIR / "Monitor"
SETUP_SCRIPT = MONITOR / "setup.sh"
MIGRATION_SCRIPT = MONITOR / "migrate_config.py"
ORIGINAL_CONFIG = MONITOR / "config.json"
# ============================

EXPECTED_PATHS = [
    INSTALL_DIR,
    SETUP_SCRIPT,
    MIGRATION_SCRIPT,
    ORIGINAL_CONFIG
]

def run(cmd, check=False):
    """Run a shell command with logging."""
    print(f"$ {' '.join(cmd)}")
    subprocess.run(cmd, check=check)

def download_latest_release(tmp_dir):
    print("=== 3. Downloading latest release from GitHub ===")
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    response = requests.get(api_url, timeout=15)
    response.raise_for_status()
    data = response.json()

    zip_url = next((a["browser_download_url"] for a in data["assets"] if a["browser_download_url"].endswith(".zip")), None)
    if not zip_url:
        raise RuntimeError("No .zip asset found in latest release.")

    zip_path = Path(tmp_dir) / "latest.zip"
    print(f"Downloading {zip_url}")
    with requests.get(zip_url, stream=True) as r:
        r.raise_for_status()
        with open(zip_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"Downloaded to {zip_path}")
    return zip_path

def extract_zip(zip_path):
    print("=== 5. Extracting new release ===")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(Path.home())
        # assume the zip contains a single root folder
        root_name = zf.namelist()[0].split("/")[0]
        src_dir = Path.home() / root_name
        if src_dir != INSTALL_DIR:
            shutil.move(str(src_dir), INSTALL_DIR)
    print(f"Extracted to {INSTALL_DIR}")

def preflight_check():
    missing = []

    # Check if expected paths exist
    for path in EXPECTED_PATHS:
        if not path.exists():
            missing.append(path)

    # Check if systemd service exists
    service_check = subprocess.run(
        ["systemctl", "list-unit-files", f"{SERVICE_NAME}.service"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    if SERVICE_NAME not in service_check.stdout.decode():
        print(f"Systemd service '{SERVICE_NAME}' not found!")

    # Network check for GitHub API access
    try:
        requests.get("https://api.github.com", timeout=5)
    except Exception:
        print("Cannot reach GitHub.")
        missing.append("network access")

    # Final validation
    if missing:
        print("\nPre-Update check failed. Missing access to:")
        for m in missing:
            print(f"   - {m}")
        print("Aborting update.")
        exit(1)

    print("Preflight check passed")

def main():
    preflight_check()
    with tempfile.TemporaryDirectory() as tmp_dir:
        try:
            # Stop service
            run(["sudo", "systemctl", "stop", SERVICE_NAME])

            # Copy config to backup config path. Overwrite it if exists
            shutil.copy2(ORIGINAL_CONFIG, BACKUP_FILE)
            print(f"Config backed up to {BACKUP_FILE}")
            
            # Download to zip
            zip_path = download_latest_release(tmp_dir)
            
            # Delete old install
            shutil.rmtree(INSTALL_DIR)
            INSTALL_DIR.mkdir(parents=True, exist_ok=True)

            extract_zip(zip_path)
            
            # Run setup script for virtual environment
            run(["bash", str(SETUP_SCRIPT)])

            # Migrate old config to new version
            if MIGRATION_SCRIPT.exists():
                run(["python3", str(MIGRATION_SCRIPT)])
            else:
                print("Migration script not found - skipping.")


            run(["sudo", "systemctl", "start", SERVICE_NAME])
            print("Update complete!")
        except Exception as e:
            print(f"Update failed: {e}")
            raise

if __name__ == "__main__":
    main()
