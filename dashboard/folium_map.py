import folium
from dashboard.utils import mrt_info_utils as mrt_utils
from dashboard.load_elemt import station_color_list

map = folium.Map(
    location=[25.0, 121.52],
    tiles="Cartodb Positron", 
    zoom_start=11,
    min_zoom=10,
    max_zoom=12,
    min_lon=121.2,
    max_lon=121.8,
    min_lat=24.6,
    max_lat=25.3,
    max_bounds=True,
    width='100%',
    height='100%',
)

feature_group_dict = dict()
for color in ["BL", "BR", "G", "O", "R", "Y"]:
    feature_group_dict[color] = folium.FeatureGroup(
        name=f"<span style='color: {mrt_utils.color_map[color]};'>{color} - line</span>"
    )

for color_key, df in station_color_list.items():
    folium.PolyLine(
        df[["lat", "lon"]].values.tolist(),
        color=mrt_utils.color_map[color_key],
        weight=2.5,
        opacity=0.5,
    ).add_to(feature_group_dict[mrt_utils.linename_map[color_key]])

    for color, location, lon, lat, hover_color in df.values:
        folium.CircleMarker(
            location=[lat, lon], 
            radius=2, 
            popup=hover_color + " - " + location, 
            fill_color=mrt_utils.color_map[color_key], 
            color=mrt_utils.color_map[color_key],
            fill=True,
        ).add_to(feature_group_dict[mrt_utils.linename_map[color_key]])