
import os 
import re
import sqlite3
from dbml_sqlite import toSQLite
import pandas as pd


class Database:
    def __init__(self,dbname:str,dbml_path:str,build:bool):
        self.dbname = dbname
        self.build = build
        self.dbml_path = dbml_path
        
    
    def create_database(self):

        if self.build:
            if self.dbname in os.listdir('./'):
                os.remove(self.dbname)
                
            ddl = toSQLite(self.dbml_path)
            con = self.connection()
            with con:
                con.executescript(ddl)
                #self._insert_data(files)


    def connection(self):
        
        return sqlite3.connect(self.dbname)

    def list_tables(self):
        cursor = self.connection().cursor() 
        cursor.execute("select name from sqlite_master where type == 'table'")
        return cursor.fetchall()

    def insert_data(self, files_path:str):
        files = os.listdir(files_path)
        files.sort()

        for file in files:
            df_ = pd.read_csv(f'{files_path}{file}')
            table_name = re.sub(r'\d_','',file)
            table_name = table_name.replace('.csv','')
            if 'id' in df_.columns:
                df_.drop(['id'], axis=1, inplace=True)

            df_.to_sql(table_name, self.connection(), if_exists="append",index=False)
