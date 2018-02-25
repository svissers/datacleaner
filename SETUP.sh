#!/bin/bash

# Create role for accessing website database
psql -c "CREATE ROLE flask WITH LOGIN PASSWORD 'flask'"
psql -c "ALTER ROLE flask CREATEDB"

# Init database for website
psql -c "CREATE DATABASE flask_db OWNER flask"
psql -c "GRANT ALL PRIVILEGES ON DATABASE flask_db TO flask"

# Create virtual environment for dependencies and enter
virtualenv env
source env/bin/activate

# Install dependencies 
pip install -r env/REQUIREMENTS.txt

deactivate