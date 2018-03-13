#!/bin/bash

# Enter virtual environment
source env/bin/activate

# Run server
python tests.py

# Exit virtual environment
deactivate
