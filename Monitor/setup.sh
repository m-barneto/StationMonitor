#!/bin/bash
#comment
#apt-get install python3-dev
#apt install -y python3.10-venv
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
