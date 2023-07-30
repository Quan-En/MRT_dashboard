import pandas as pd
from dashboard.utils import mrt_info_utils as mrt_utils
import plotly.express as px
from typing import List
from datetime import datetime, timedelta

def plotEmptyInFlowBarChart():
    inFlowBarFig = px.bar(
        pd.DataFrame({"進站":[], "人次":[]}),
        x="進站", y="人次", hover_data={"進站":False, "人次":False},
        custom_data=["進站", "人次"],
    )
    inFlowBarFig.update_traces(
        marker_line_color='rgb(8,48,107)',
        marker_line_width=1.5, opacity=0.8, 
        showlegend=False,
        hovertemplate="%{customdata[0]}<Br> %{customdata[1]}<extra></extra>",
    )
    inFlowBarFig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=250, plot_bgcolor='lightgray')
    return inFlowBarFig

def plotEmptyOutFlowBarChart():
    outFlowBarFig = px.bar(
        pd.DataFrame({"出站":[], "人次":[]}),
        x="出站", y="人次", hover_data={"出站":False, "人次":False},
        custom_data=["出站", "人次"],
    )
    outFlowBarFig.update_traces(
        marker_line_color='rgb(8,48,107)',
        marker_line_width=1.5, opacity=0.8, 
        showlegend=False,
        hovertemplate="%{customdata[0]}<Br> %{customdata[1]}<extra></extra>",
    )
    outFlowBarFig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=250, plot_bgcolor='lightgray')
    return outFlowBarFig

# def createFlowGraphData(data: pd.DataFrame, isin: bool, color: str):
#     state = "進站" if isin else "出站"
#     FlowGraphData = (
#         data[[state, "人次"]]
#         .groupby([state])
#         .sum()
#         .reset_index()
#         .query(f"{state} == @mrt_utils.lineStationDict['{color.upper()}']")
#     )
#     FlowGraphData[state] = pd.Categorical(FlowGraphData[state], categories=mrt_utils.lineStationDict[color.upper()], ordered=True)
#     FlowGraphData = FlowGraphData.sort_values(state, ignore_index=True)
#     FlowGraphData[state] = FlowGraphData[state].astype(object)
#     return FlowGraphData

def createFlowGraphData(data: pd.DataFrame, isin: bool, color: str):
    state = "進站" if isin else "出站"
    FlowGraphData = (
        data[["車站", f"{state}人次"]]
        .groupby(["車站"])
        .sum()
        .reset_index()
        .query(f"車站 in @mrt_utils.lineStationDict['{color.upper()}']")
    )
    FlowGraphData["車站"] = pd.Categorical(
        FlowGraphData["車站"],
        categories=mrt_utils.lineStationDict[color.upper()],
        ordered=True,
    )

    FlowGraphData = FlowGraphData.sort_values("車站", ignore_index=True)
    FlowGraphData["車站"] = FlowGraphData["車站"].astype(object)
    return FlowGraphData.rename(columns={"車站":state, f"{state}人次":"人次"})

FigDict = {
    line:{
        "inFlow":plotEmptyInFlowBarChart(),
        "outFlow":plotEmptyOutFlowBarChart(),
    }
    for line in ["BL", "BR", "G", "O", "R", "Y"]
}

def updateFlowFig(fig_dict:dict, update_data_list: List[pd.DataFrame], color: str):
    """
    update_data_list[0]: inflow
    update_data_list[1]: outflow
    """
    fig_dict[color.upper()]["inFlow"].update_traces(marker_color=mrt_utils.color_map[color.upper()])
    fig_dict[color.upper()]["outFlow"].update_traces(marker_color=mrt_utils.color_map[color.upper()])

    fig_dict[color.upper()]["inFlow"].data[0].x = update_data_list[0]["進站"].values
    fig_dict[color.upper()]["inFlow"].data[0].y = update_data_list[0]["人次"].values
    fig_dict[color.upper()]["inFlow"].data[0].customdata = update_data_list[0].values

    fig_dict[color.upper()]["outFlow"].data[0].x = update_data_list[1]["出站"].values
    fig_dict[color.upper()]["outFlow"].data[0].y = update_data_list[1]["人次"].values
    fig_dict[color.upper()]["outFlow"].data[0].customdata = update_data_list[1].values
    return fig_dict



def getDateSequence(start_date_str:str, end_date_str:str):
    
    if start_date_str == end_date_str:
        return [start_date_str]
    
    # Convert the date strings to datetime objects
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    # Calculate the number of days between the start and end dates
    num_days = (end_date - start_date).days

    # Generate the date sequence
    date_sequence = [start_date + timedelta(days=i) for i in range(num_days + 1)]

    # Convert the datetime objects back to date strings
    date_sequence_str = [date.strftime("%Y-%m-%d") for date in date_sequence]

    return date_sequence_str