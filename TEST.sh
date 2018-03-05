#!/bin/bash

# Enter virtual environment
source env/bin/activate

# Run server
cd src
python tests.py
cd ..

# Exit virtual environment
deactivate