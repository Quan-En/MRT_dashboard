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

from dashboard.utils import sql_utils
from dashboard.utils import func_utils
from dashboard.utils import forms

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

            query_statement = sql_utils.getDataQueryStatement(
                table_name=f"table_{selectedDateDict[color.upper()].replace('-', '_')}",
                select_cols=["進站", "出站", "人次"],
                and_conditions=["時段=0"]
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

