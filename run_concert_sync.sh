#!/bin/bash

# Change to the directory where this script is located
cd "$(dirname "${BASH_SOURCE[0]}")"

# Run the first Python script and log output
python3 sfs-dump-and-parse.py

# Run the second Python script and log output
python3 cal-performances-dump-and-parse.py

# Run the second Python script and log output
python3 sync-to-gcal.py
