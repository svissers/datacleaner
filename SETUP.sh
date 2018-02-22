#!/bin/bash

# Create role for accessing website database
psql -c "CREATE ROLE flask WITH LOGIN PASSWORD 'flask'"
psql -c "ALTER ROLE flask CREATEDB"

# Create database for website
psql -c "CREATE DATABASE data_cleaner OWNER flask"

# Create virtual environment for dependencies and enter
virtualenv env
source env/bin/activate

# Install dependencies 
pip install -r env/REQUIREMENTS.txt

deactivate