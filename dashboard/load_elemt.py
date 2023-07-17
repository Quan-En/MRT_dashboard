import pickle
import pandas as pd
import sqlalchemy

from dashboard.utils import sql_utils
from dashboard.utils import mrt_info_utils as mrt_utils
from dashboard.connect_mysql import *

with open("./dashboard/static/images/mrt_road_map.pickle", "rb") as file:
    fig = pickle.load(file)

with open("./dashboard/static/images/mrt_road_map_without_line_and_marker.pickle", "rb") as file:
    fig_without_marker = pickle.load(file)
    fig_without_marker.update_layout(height=550)


selectedDateDict = {
    line:"" for line in ["BL", "BR", "G", "O", "R", "Y"]
}

example_table_header = ["日期", "時段", "進站", "出站", "人次"]

with engine.connect() as connection:
    example_query_statement = sql_utils.getDataQueryStatement(
        table_name="table_2023_03_01",
        select_cols=example_table_header,
        and_conditions=["時段=0"]
    )
    example_query_statement += " LIMIT 100"

    result = connection.execute(sqlalchemy.text(example_query_statement))
    rows = result.fetchall()
    keys = result.keys()
    example_data = pd.DataFrame(data=rows, columns=keys).replace(".*板橋", "板橋", regex=True).values.tolist()
    del example_query_statement, result, rows, keys

station_color_list = dict()
for color in mrt_utils.lines_color:
    query_statement = sql_utils.getDataQueryStatement(table_name=f"{color.lower()}_line_station", select_cols=["color", "station", "lon", "lat"])
    with engine.connect() as connection:
        result = connection.execute(sqlalchemy.text(query_statement))
        rows = result.fetchall()
        keys = result.keys()
        station_color_list[color] = pd.DataFrame(data=rows, columns=keys)