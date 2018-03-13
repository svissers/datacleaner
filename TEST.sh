#!/bin/bash

# Enter virtual environment
source env/bin/activate

# Run server
python3 tests.py

# Exit virtual environment
deactivate