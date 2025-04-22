import mariadb
import sys
import os
from dotenv import load_dotenv, set_key

class DB:
    def __init__(self):
        
        load_dotenv()
        
        self.readConfig()
        self.connect()
    
    def readConfig(self):
        
        try:
            self.DATABASE_URL = os.getenv('DATABASE_URL')
            
            self.DB_USERNAME = os.getenv('DB_USERNAME')
            self.DB_PASSWORD = os.getenv('DB_PASSWORD')
            
            self.DB_PORT = os.getenv('DB_PORT')
            self.DB_DATABASE = os.getenv('DB_DATABASE')
        except Exception as e:
            print(f"Erro ao ler configurações do DB: {e}")

    def disconnect(self):
        try:
            self.conn.close()
        except Exception as e:
            print(f"erro ao encerrar conn DB: {e}")
     
    def connect(self):
        try:
            
            self.conn = mariadb.connect(
                user=self.DB_USERNAME,
                password=self.DB_PASSWORD,
                host=self.DATABASE_URL,
                port=int(self.DB_PORT),
                database=self.DB_DATABASE,
                autocommit=True

            )
            
            self.cur = self.conn.cursor()
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(1)
        
    def insert_notified(self, id, table='notified_itens'):
        try:
            
            affected_count = self.cur.execute(f"INSERT INTO {table} (id) VALUES ({id})")

            return True
            
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            return False
        finally:
            self.disconnect()
            
        
    def isNotified(self, id, table='notified_itens'):
        try:
            if id == None:
                return False
            
            self.cur.execute(f"SELECT id FROM {table} WHERE id={id}")
            print(f'cur == {self.cur}')
            
            for (data) in self.cur:
                
                print(f"{id} == {data[0]}")
                if(str(id) == str(data[0])):
                    return True
            
            return False            
        except Exception as e:
            
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(f"Error connecting to MariaDB Platform: {e} - {exc_tb.tb_lineno}")
            sys.exit(1)
        finally:
            self.disconnect()
