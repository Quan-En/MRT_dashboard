import os
import copy
import tempfile
from io import StringIO

import pandas as pd
import plotly.io as pio
import sqlalchemy

from dashboard import app, db
from dashboard.models import User
from dashboard.load_elemt import *
# from dashboard import folium_map

from dashboard.utils import sql_utils
from dashboard.utils import func_utils
from dashboard.utils import forms

import folium
from folium.plugins import HeatMapWithTime

from flask import render_template, url_for, redirect, request, send_file, flash
from flask_login import login_user, logout_user, login_required

FigDict = copy.deepcopy(func_utils.FigDict)

@app.route('/', methods=['GET', 'POST'])
def home_page():
    # Convert the figure to HTML
    div = pio.to_html(fig, config={'displayModeBar': False, 'scrollZoom':False}, div_id="mrt-map-graph", default_width="95%", full_html=False)
    return render_template("index.html", graph_div=div)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        return redirect(url_for('home_page'))
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = forms.LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('home_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))

@app.route('/<color>-line', methods=['GET', 'POST'])
@login_required
def line_stations_page(color):
    query_data_form = forms.queryDataForm()
    if request.method == "POST":
        selectedDateDict[color.upper()] = request.form.get("query_data")

        global FigDict

        if selectedDateDict[color.upper()] == "":

            FigDict[color.upper()]["inFlow"] = copy.deepcopy(func_utils.FigDict[color.upper()]["inFlow"])
            FigDict[color.upper()]["outFlow"] = copy.deepcopy(func_utils.FigDict[color.upper()]["outFlow"])

        if selectedDateDict[color.upper()] != "":

            # query_statement = sql_utils.getDataQueryStatement(
            #     table_name=f"table_{selectedDateDict[color.upper()].replace('-', '_')}",
            #     select_cols=["進站", "出站", "人次"],
            #     and_conditions=["時段=0"]
            # )
            query_statement = sql_utils.getDataQueryStatement(
                table_name=f"summary_table_{selectedDateDict[color.upper()].replace('-', '_')}",
                select_cols=["日期", "時段", "車站", "進站人次", "出站人次"],
            )
            with engine.connect() as connection:
                result = connection.execute(sqlalchemy.text(query_statement))
                rows = result.fetchall()
                keys = result.keys()
                query_result = pd.DataFrame(data=rows, columns=keys).replace(".*板橋", "板橋", regex=True)
            inFlowGraphData = func_utils.createFlowGraphData(data=query_result, isin=True, color=color)
            outFlowGraphData = func_utils.createFlowGraphData(data=query_result, isin=False, color=color)
            
            FigDict = func_utils.updateFlowFig(FigDict, [inFlowGraphData, outFlowGraphData], color)

        divOfInFlow = pio.to_html(FigDict[color.upper()]["inFlow"], div_id="mrt-station-inflow", full_html=False)
        divOfOutFlow = pio.to_html(FigDict[color.upper()]["outFlow"], div_id="mrt-station-outflow", full_html=False)

        return redirect(url_for('line_stations_page', color=color))

    if request.method == "GET":
        copied_fig = copy.deepcopy(fig_without_marker)
        for i in range(len(copied_fig.data)):
            if copied_fig.data[i].mode in ['lines', 'markers'] and copied_fig.data[i].name == color.upper():
                copied_fig.data[i].visible = None

        divOfRoadMapGraph = pio.to_html(copied_fig, config={'displayModeBar': False, 'scrollZoom':False}, div_id="mrt-map-graph", full_html=False)

        divOfInFlow = pio.to_html(FigDict[color.upper()]["inFlow"], div_id="mrt-station-inflow", full_html=False)
        divOfOutFlow = pio.to_html(FigDict[color.upper()]["outFlow"], div_id="mrt-station-outflow", full_html=False)

        return render_template(
            "line.html",
            color=color,
            selectedDate=selectedDateDict[color.upper()],
            query_data_form=query_data_form, 
            divOfRoadMapGraph=divOfRoadMapGraph,
            divOfInFlow=divOfInFlow,
            divOfOutFlow=divOfOutFlow
        )

@app.route('/data', methods=['GET', 'POST'])
@login_required
def data_page():
    download_data_form = forms.downloadDataForm()
    if request.method == "POST":

        start_date = request.form["hidden-tag-start-date"]
        end_date = request.form["hidden-tag-end-date"]
        date_seq = func_utils.getDateSequence(start_date, end_date)

        df_list = []
        for date in date_seq:
            query_statement = sql_utils.getDataQueryStatement(
                table_name=f"table_{date.replace('-', '_')}",
                select_cols=["日期", "時段", "進站", "出站", "人次"],
                and_conditions=[],
                or_conditions=[]
            )
            
            try:
                with engine.connect() as connection:
                    result = connection.execute(sqlalchemy.text(query_statement))
                    rows = result.fetchall()
                    keys = result.keys()
                df_list.append(pd.DataFrame(data=rows, columns=keys))
            except:
                pass
        outputDF = pd.concat(df_list)

        # Create a StringIO object as a buffer
        buffer = StringIO()

        # Write the DataFrame to the buffer as CSV
        outputDF.to_csv(buffer, index=False)

        # Get the CSV content from the buffer
        csv_content = buffer.getvalue()

        # Close the buffer
        buffer.close()


        temp_dir = tempfile.mkdtemp()

        # Define the path to the temporary CSV file
        temp_file_path = os.path.join(temp_dir, 'data.csv')
        with open(temp_file_path, 'w', newline='') as file:
            file.write(csv_content)

        return send_file(
            temp_file_path,
            mimetype='text/csv',
            as_attachment=True,
            download_name='data.csv'
        )

    if request.method == "GET":
        return render_template(
            "data.html", 
            header=example_table_header, 
            data=example_data,
            download_data_form=download_data_form
        )

@app.route('/heatmap', methods=['GET', 'POST'])
@login_required
def heatmap_page():
    query_data_form = forms.queryDataForm()
    if request.method == "POST":
        selectedDateForHeatMap = request.form.get("query_data").replace('-', '_')

        if selectedDateForHeatMap == "":
            redirect(url_for('heatmap'))

        if selectedDateForHeatMap != "":
            query_statement = sql_utils.getDataQueryStatement(
                table_name=f"summary_table_{selectedDateForHeatMap}",
                select_cols=["日期", "時段", "車站", "進站人次", "出站人次"],
            )

            with engine.connect() as connection:
                result = connection.execute(sqlalchemy.text(query_statement))
                rows = result.fetchall()
                keys = result.keys()
                summary_result = pd.DataFrame(data=rows, columns=keys)

            temp_df = pd.merge(
                left=summary_result.rename(columns={"車站":"station"}).replace("大橋頭.*", "大橋頭", regex=True),
                right=station_location_result[["station", "lat", "lon"]].drop_duplicates(ignore_index=True),
                on="station", how="left"
            )
            temp_df["時段"] = temp_df["時段"].astype(str).str.zfill(2)

            empty_df = temp_df[["日期", "station", "lat", "lon"]].drop_duplicates()
            empty_df[["進站人次", "出站人次"]] = 0
            empty_df.insert(loc=1, column="時段", value=None)

            temp_in_df_list = []
            temp_out_df_list = []
            time_index_list = []

            for i in range(24):
                sub_df = temp_df.query(f"時段 == '{i:02d}'").reset_index(drop=True)
                if len(sub_df) == 0:
                    empty_df["時段"] = f"{i:02d}"
                    sub_df = empty_df.copy(deep=True)
                time_index_list.append((sub_df["日期"].astype(str) + " " + sub_df["時段"].astype(str).str.zfill(2)).unique().item())
                temp_in_df_list.append(list(map(list, sub_df[["lat", "lon", "進站人次"]].itertuples(index=False))))
                temp_out_df_list.append(list(map(list, sub_df[["lat", "lon", "出站人次"]].itertuples(index=False))))

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
            
            # Create the map
            my_map = folium.Map(
                location=[25.05, 121.52],
                tiles="Cartodb Positron", 
                zoom_start=11,
                min_zoom=10,
                max_zoom=12,
                min_lon=121.2,
                max_lon=121.8,
                min_lat=24.8,
                max_lat=25.3,
                max_bounds=True,
                width='100%',
                height='100%',
            )

            for key, val in feature_group_dict.items():
                val.add_to(my_map)
            
            gradient = {.33: 'green', .66: 'brown', 1: 'red'}
            HeatMapWithTime(
                data=temp_in_df_list,
                index=time_index_list,
                auto_play=True,
                use_local_extrema=True,
                name="inFlow",
                min_opacity=0,
                blur=1.0,
                radius=20,
                gradient=gradient,
            ).add_to(my_map)

            HeatMapWithTime(
                data=temp_out_df_list,
                index=time_index_list,
                auto_play=True,
                use_local_extrema=True,
                name="outFlow",
                blur=1.0,
                min_opacity=0,
                radius=20,
                gradient=gradient,
            ).add_to(my_map)

            folium.LayerControl(collapsed=False).add_to(my_map)
            my_map.get_root().height = "450px"
            return render_template(
                "heatmap.html",
                body_html=my_map.get_root()._repr_html_(),
                query_data_form=query_data_form,
            )

    if request.method == "GET":

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
        
        # Create the map
        my_map = folium.Map(
            location=[25.05, 121.52],
            tiles="Cartodb Positron", 
            zoom_start=11,
            min_zoom=10,
            max_zoom=12,
            min_lon=121.2,
            max_lon=121.8,
            min_lat=24.8,
            max_lat=25.3,
            max_bounds=True,
            width='100%',
            height='100%',
        )

        for key, val in feature_group_dict.items():
            val.add_to(my_map)

        folium.LayerControl(collapsed=False).add_to(my_map)
        my_map.get_root().height = "450px"
        return render_template(
            "heatmap.html",
            body_html=my_map.get_root()._repr_html_(),
            query_data_form=query_data_form,
        )