#Data Access Object pattern: see http://best-practice-software-engineering.ifs.tuwien.ac.at/patterns/dao.html
#For clean separation of concerns, create separate data layer that abstracts all data access to/from RDBM
#
#Depends on psycopg2 librarcy: see (tutor) https://wiki.postgresql.org/wiki/Using_psycopg2_with_PostgreSQL
import psycopg2

class DBConnection:
    def __init__(self,dbname,dbuser,dbpass,dbhost):
        try:
            self.conn = psycopg2.connect("dbname='{}' user='{}' host='{}' password='{}'".format(dbname,dbuser,dbhost, dbpass))
        except:
            print('ERROR: Unable to connect to database')
            raise Exception('Unable to connect to database')

    def close(self):
        self.conn.close()

    def get_connection(self):
        return self.conn

    def get_cursor(self):
        return self.conn.cursor()

    def commit(self):
        return self.conn.commit()

    def rollback(self):
        return self.conn.rollback()
