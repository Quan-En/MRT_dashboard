import sqlalchemy
from typing import Union, Dict, List

def checkTableExists(engine: sqlalchemy.engine, table_name: str, schema_name: str):
    inspector = sqlalchemy.inspect(engine)
    return inspector.has_table(table_name=table_name, schema=schema_name)

def getDataQueryStatement(table_name: str, select_cols: Union[str, list[str]]="*", and_conditions: List[str]=[], or_conditions: List[str]=[]):
    query = f"SELECT {f', '.join(select_cols)} FROM {table_name}"

    if len(and_conditions) > 0 or len(or_conditions) > 0:
        query += " WHERE "
        query += f"({' AND '.join(and_conditions)})" if len(and_conditions) > 0 else ""
        query += " AND " if len(and_conditions) > 0 and len(or_conditions) > 0 else " "
        query += f"({' OR '.join(or_conditions)})" if len(or_conditions) > 0 else ""

    return query