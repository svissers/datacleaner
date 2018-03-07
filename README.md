# Data Cleaner

## Requirements
	
1. PostgreSQL: [Download & Install](https://www.postgresql.org/download/)
2. Python 3.3 or higher: [Download & Install](https://www.python.org/downloads/)
3. Pip: [Download & Install](https://pip.pypa.io/en/stable/installing/)
4. VirtualEnv [Download & Install](https://virtualenv.pypa.io/en/stable/installation/)

## Setup

You can run SETUP.sh to setup the environment for this project or do the following manually:

Create role for accessing website database:
> psql -c "CREATE ROLE flask WITH LOGIN PASSWORD 'flask'"  
> psql -c "ALTER ROLE flask CREATEDB"

Initialize website database:
> psql -c "CREATE DATABASE flask_db OWNER flask"  
> psql -c "GRANT ALL PRIVILEGES ON DATABASE flask_db TO flask"

Create virtual environment to install dependencies:
> virtualenv env

Install dependencies from env/REQUIREMENTS.txt:
> source env/bin/activate  
> pip install -r env/REQUIREMENTS.txt  
> deactivate


## Run

You can do the following manually or make your life easier by letting RUN.sh do the work for you:

Enter virtual environmnent created during setup:
> source env/bin/activate

Run server:
> cd src  
> python app.py  
