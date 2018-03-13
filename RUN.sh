#!/bin/bash

# Enter virtual environment
source env/bin/activate

# Run server
python3 run_server.py run

# Exit virtual environment
deactivate
