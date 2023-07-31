import pickle
import pandas as pd
import sqlalchemy

from dashboard.utils import sql_utils
from dashboard.utils import mrt_info_utils as mrt_utils
from dashboard.connect_mysql import *

# import folium

with open("./dashboard/static/images/mrt_road_map.pickle", "rb") as file:
    fig = pickle.load(file)

with open("./dashboard/static/images/mrt_road_map_without_line_and_marker.pickle", "rb") as file:
    fig_without_marker = pickle.load(file)
    fig_without_marker.update_layout(height=500)


selectedDateDict = {
    line:"" for line in ["BL", "BR", "G", "O", "R", "Y"]
}

selectedDateForHeatMap = ""

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

query_statement = sql_utils.getDataQueryStatement(
    table_name="mrt_location_color",
    select_cols=["station", "lat", "lon", "color", "hover_color"],
)

with engine.connect() as connection:
    result = connection.execute(sqlalchemy.text(query_statement))
    rows = result.fetchall()
    keys = result.keys()
    station_location_result = pd.DataFrame(data=rows, columns=keys)

for color_key in station_color_list.keys():
    station_color_list[color_key] = pd.merge(
        left=station_color_list[color_key],
        right=station_location_result[["station", "hover_color"]],
        on="station",
    )

# map = folium.Map(
#     location=[25.0, 121.52],
#     tiles="Cartodb Positron", 
#     zoom_start=11,
#     min_zoom=10,
#     max_zoom=12,
#     min_lon=121.2,
#     max_lon=121.8,
#     min_lat=24.6,
#     max_lat=25.3,
#     max_bounds=True,
#     width='100%',
#     height='100%',
# )

# feature_group_dict = dict()
# for color in ["BL", "BR", "G", "O", "R", "Y"]:
#     feature_group_dict[color] = folium.FeatureGroup(
#         name=f"<span style='color: {mrt_utils.color_map[color]};'>{color} - line</span>"
#     )

# for color_key, df in station_color_list.items():
#     folium.PolyLine(
#         df[["lat", "lon"]].values.tolist(),
#         color=mrt_utils.color_map[color_key],
#         weight=2.5,
#         opacity=0.5,
#     ).add_to(feature_group_dict[mrt_utils.linename_map[color_key]])

#     for color, location, lon, lat, hover_color in df.values:
#         folium.CircleMarker(
#             location=[lat, lon], 
#             radius=2, 
#             popup=hover_color + " - " + location, 
#             fill_color=mrt_utils.color_map[color_key], 
#             color=mrt_utils.color_map[color_key],
#             fill=True,
#         ).add_to(feature_group_dict[mrt_utils.linename_map[color_key]])