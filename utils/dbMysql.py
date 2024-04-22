import pymysql
from config.config import dbConfig
from utils.dataInfo import DataInfo
import json

class DBMysql():
    def __init__(self) -> None:
        self.conn = pymysql.connect(host=dbConfig['host'], user=dbConfig['user'], password=dbConfig['password'], database=dbConfig['database'])
        self.cursor = self.conn.cursor()
    
    def __del__(self) -> None:
        self.conn.close()
    

    def insertData(self, _data:DataInfo):
        table_name = _data.getTable()
        insert_sql = "INSERT INTO {} (".format(table_name)
        insert_value = ""
        for key_name in _data.keys():
            if insert_value == "":
                insert_sql += "{}".format(key_name)
                insert_value = "(%s"
            else:
                insert_sql += ", {}".format(key_name)
                insert_value += ", %s"
        insert_sql += ")"
        insert_value += ")"
        insert_sql += " VALUES {};".format(insert_value)
        self.cursor.execute(insert_sql,[json.dumps(v) if isinstance(v, dict) or isinstance(v, list) else v for v in _data.values()])
        self.conn.commit()
    
    def insertDataEx(self, _table, _data:DataInfo):
        table_name = _table
        insert_sql = "INSERT INTO {} (".format(table_name)
        insert_value = ""
        for key_name in _data.keys():
            if insert_value == "":
                insert_sql += "{}".format(key_name)
                insert_value = "(%s"
            else:
                insert_sql += ", {}".format(key_name)
                insert_value += ", %s"
        insert_sql += ")"
        insert_value += ")"
        insert_sql += " VALUES {};".format(insert_value)
        self.cursor.execute(insert_sql,[json.dumps(v) if isinstance(v, dict) or isinstance(v, list) else v for v in _data.values()])
        self.conn.commit()
    
    def queryData(self, _table:str, _item:dict):
        query_sql = "SELECT * FROM {} WHERE {}=%s;".format(_table, list(_item.keys())[0])
        self.cursor.execute(query_sql,(list(_item.values())[0],))
        fields = [field[0] for field in self.cursor.description]
        return (fields, self.cursor.fetchall())
    
    def query(self, _sql, values):
        if values is None:
            self.cursor.execute(_sql)
        else:
            self.cursor.execute(_sql,values)
        fields = [field[0] for field in self.cursor.description]
        return (fields, self.cursor.fetchall())
    
    def execute(self, _sql, values):
        self.cursor.execute(_sql,values)
        self.conn.commit()
    
    def checkTableExist(self, _table:str):
        self.cursor.execute("SHOW TABLES LIKE %s;", (_table, ))
        if self.cursor.rowcount > 0:
            return True
        else:
            return False
        
    def createTable(self, _table:str, _items:dict, uniques:list = [], indexs:list = []):
        if self.checkTableExist(_table):
            return
        sql = "CREATE TABLE {} ( index_id INT AUTO_INCREMENT PRIMARY KEY".format(_table)
        for key, value in _items.items():
            sql += ", {}".format(key)
            for _i in value:
                sql += " {}".format(_i)
        
        for value in uniques:
            sql += ", UNIQUE KEY ({})".format(value)
        
        for value in indexs:
            sql += ", INDEX ({})".format(value)
        
        sql += " ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
        self.cursor.execute(sql)
        self.conn.commit()
