import os
import os.path
import shutil
import subprocess
import tempfile
import zipfile
import requests
from pathlib import Path

BUILD_DIRECTORY = Path.cwd() / "build"
BUILD_FOLDER = BUILD_DIRECTORY / "StationMonitor"
INTERFACE_DST = BUILD_FOLDER / "Interface"
MONITOR_DST = BUILD_FOLDER / "Monitor"

INTERFACE_SRC = Path.cwd() / "Interface"
MONITOR_SRC = Path.cwd() / "Monitor"

ZIP_BUILD = BUILD_DIRECTORY / "StationMonitor.zip"



# Clear out the interface and monitor folders
if Path.exists(INTERFACE_DST):
    shutil.rmtree(INTERFACE_DST, )
if Path.exists(MONITOR_DST):
    shutil.rmtree(MONITOR_DST)

os.makedirs(INTERFACE_DST)
os.makedirs(MONITOR_DST)

# copy only build stuff from interface to dst
shutil.copytree(INTERFACE_SRC / "build", INTERFACE_DST / "build")

# copy from monitor into the dst
for entry in os.listdir(MONITOR_SRC):
    entry_path = MONITOR_SRC / entry
    if os.path.isdir(entry_path):
        if "vscode" in entry:
            continue
        shutil.copytree(entry_path, MONITOR_DST / entry)
    else:
        print(entry_path, "file")
        if "gitignore" in entry:
            continue
        shutil.copy2(entry_path, MONITOR_DST)


#zip up build
with zipfile.ZipFile(ZIP_BUILD, "w", zipfile.ZIP_DEFLATED) as zipf:
    for file_path in BUILD_FOLDER.rglob("*"):
        if file_path.is_file():
            # Preserve folder structure inside the zip
            arcname = "StationMonitor" / file_path.relative_to(BUILD_FOLDER)
            zipf.write(file_path, arcname)

print(f"Zipped build to: {ZIP_BUILD}")