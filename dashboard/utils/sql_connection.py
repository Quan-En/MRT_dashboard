import mysql.connector
from mysql.connector import Error
from typing import Union, Dict

def connectDatabase(connect_config):
    try:
        connection = mysql.connector.connect(**connect_config)
        if connection.is_connected():
            return connection
    except Error as e:
            print(f'連接到MySQL時發生錯誤：{e}')

def createTableQuery(name: str, cols_and_dtye: list):
    query = f"CREATE TABLE {name} ("
    for column_name, data_type in cols_and_dtye:
        query += f"{column_name} {data_type}, "
    query = query[:-2] + ")"
    return query

def createTable(connection, name: str, cols_and_dtye: list):
    query = createTableQuery(name, cols_and_dtye)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            connection.commit()
        print(f"成功創建名為: {name} 的資料庫表格")
    except Error as e:
        print(f"創建資料庫表格時發生錯誤：{e}")

def insertDataQuery(name: str, cols: list):
    query = f"INSERT INTO {name} ({', '.join(cols)}) VALUES ({', '.join(['%s'] * len(cols))})"
    return query

def insertData(connection, dataframe, name: str, cols: list):
    query = insertDataQuery(name, cols)
    try:
        with connection.cursor() as cursor:
            cursor.executemany(query, dataframe.to_records(index=False).tolist())
            connection.commit()
        print(f"成功將 DataFrame 數據存儲到 '{name}' 資料表中")
    except Error as e:
        print(f"存儲數據到資料表時發生錯誤：{e}")


def checkTableExists(connection, name: str):
    query = f"SHOW TABLES LIKE '{name}'"
    # 執行 SQL 語句並檢查結果
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchone()
            return True if result else False
    except Error as e:
        print(f"檢查表格時發生錯誤：{e}")

def getDataQuery(name: str, select_cols: Union[str, list[str]]="*", conditions: Dict[str, list[str]]={"AND":[], "OR":[]}):
    query = f"SELECT {f', '.join(select_cols)} FROM {name}"

    if len(conditions["AND"]) > 0 and len(conditions["OR"]) > 0:
        query += f" WHERE ({' AND '.join(conditions['AND'])}) AND ({' OR '.join(conditions['OR'])})"
    elif len(conditions["AND"]) > 0:
        query += f" WHERE ({' AND '.join(conditions['AND'])})"
    elif len(conditions["OR"]) > 0:
        query += f" WHERE ({' OR '.join(conditions['OR'])})"

    return query

def getData(connection, name: str, select_cols: Union[str, list[str]]="*", conditions: Dict[str, list[str]]={"AND":[], "OR":[]}):
    if not checkTableExists(connection, name):
        print(f"Table {name} not exists.")
        return []
    else:
        query = getDataQuery(name, select_cols, conditions)
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return result
        except Error as e:
            print(f"query data時發生錯誤：{e}")
            return []
