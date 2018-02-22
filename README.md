# datacleaner

## setup

### SQL server
first install the postgresql server:
> sudo apt-get install postgresql

then, create the user and db which we will use:
> sudo -u postgres createuser pdb  
> sudo -u postgres createdb pdb

then update pdb's password and give it privileges by entering the psql commandline as user postgres:
> sudo -u postgres psql  
> alter user pdb with encrypted password 'pdb';  
> grant all privileges on database pdb to pdb;

leave the commandline with \q

to enter the commandline interface as the user, enter the command
> psql -U pdb -h localhost

### Venv

initialize a venv with
> virtualenv .

activate the venv

> source bin/activate

All the requirements that python needs are in pip.txt, install them using ```pip install -r pip.txt```
