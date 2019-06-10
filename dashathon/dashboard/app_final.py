"""This module creates an interactive dashboard that allows users to explore
marathon finisher data and compare their own split times to the finishers'."""

import pandas as pd
import numpy as np
import plotly.graph_objs as go
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_functions

SECONDS = 60.0

EXTERNAL_STYLESHEETS = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=EXTERNAL_STYLESHEETS)

df = pd.read_csv("bostonnycchicago.csv")

# pull the list of demographic variables from the data itself
# include 'all' so user can view data without slicing it
genders = df["gender"].unique()
genders = np.append(genders, ["all"])
ages = df["age_range"].unique()
ages = np.append(ages, ["all"])


app.layout = html.Div(
    [
        html.H3("DASHATHON"),
        html.H6("Average Pace at Each Split for Selected Demographic"),
        html.Div(
            [
                html.P(
                    "Select a gender or age group to see information about that demographic. All runners are selected by default."
                ),
                html.P(
                    "Please enter your own split times below in HH:MM:SS or MM:SS format. If you enter your own split data, your fatigue zone will be highlighted in blue."
                ),
                html.Div(
                    [
                        dcc.Dropdown(
                            id="gender_select",
                            options=[{"label": g, "value": g} for g in genders],
                            value="all",
                        )
                    ],
                    style={"width": "48%", "display": "inline-block"},
                ),
                html.Div(
                    [
                        dcc.Dropdown(
                            id="age_select",
                            options=[{"label": a, "value": a} for a in ages],
                            value="all",
                        )
                    ],
                    style={"width": "48%", "float": "right", "display": "inline-block"},
                ),
                dcc.Input(id="5k-input", type="text", value="5k split", size="6"),
                dcc.Input(id="10k-input", type="text", value="10k split", size="6"),
                dcc.Input(id="15k-input", type="text", value="15k split", size="6"),
                dcc.Input(id="20k-input", type="text", value="20k split", size="6"),
                dcc.Input(id="half-input", type="text", value="half split", size="6"),
                dcc.Input(id="25k-input", type="text", value="25k split", size="6"),
                dcc.Input(id="30k-input", type="text", value="30k split", size="6"),
                dcc.Input(id="35k-input", type="text", value="35k split", size="6"),
                dcc.Input(id="40k-input", type="text", value="40k split", size="6"),
                dcc.Input(
                    id="full-input", type="text", value="full marathon", size="6"
                ),
                html.Button(id="submit-button", n_clicks=0, children="Submit"),
                html.Div(id="output-state"),
            ]
        ),
        dcc.Graph(id="indicator-graphic"),
        html.H6("Distribution of Split Ratios for Selected Demographic"),
        html.P(
            "A Split Ratio is the time spent running the second half of a to the time spent running the first half."
        ),
        html.P(
            "If you enter half and full marathon times, you will see your split ratio marked below in blue."
        ),
        dcc.Graph(id="split-hist"),
    ]
)


@app.callback(
    Output("indicator-graphic", "figure"),
    [Input("submit-button", "n_clicks")],
    [
        State("gender_select", "value"),
        State("age_select", "value"),
        State("5k-input", "value"),
        State("10k-input", "value"),
        State("15k-input", "value"),
        State("20k-input", "value"),
        State("half-input", "value"),
        State("25k-input", "value"),
        State("30k-input", "value"),
        State("35k-input", "value"),
        State("40k-input", "value"),
        State("full-input", "value"),
    ],
)
def update_graph(
    n_clicks,
    gender_,
    age_,
    user5k,
    user10k,
    user15k,
    user20k,
    userhalf,
    user25k,
    user30k,
    user35k,
    user40k,
    userfull,
):
    """
    This function updates the line graph based on user's demographic selection.
    Parameters:
    n_clicks (dash state): introduces pressed-state of submit button to the
    function; must be passed as input or function will not update.
    gender_ (dash state): user's selectio in the gender drop-down menu
    age_ (dash state): user's age group selectio in age drop-down menu
    user5k (string): user 5k split if entered
    user10k (string): user 10k split if entered
    user15k (string): user 15k split if entered
    user20k (string): user 20k split if entered
    userhalf (string): user half marathon split if entered
    user25k (string): user 25k split if entered
    user30k (string): user 30k split if entered
    user35k (string): user 35k split if entered
    user40k (string): user 40k split if entered
    userfull (string): user full marathon finish time if entered
    Returns:
    updates the line graph
    """
    # subset the data based on user's age and gender selection
    subset = dash_functions.get_subset(df, age_, gender_)

    # select the top performers from the selected demographic
    subset_winners = dash_functions.get_top(subset, 0.1)

    # create variables needed to interpret user's split data
    split_list = [
        "5k",
        "10k",
        "15k",
        "20k",
        "half",
        "25k",
        "30k",
        "35k",
        "40k",
        "official_time",
    ]

    user_paces = [
        user5k,
        user10k,
        user15k,
        user20k,
        userhalf,
        user25k,
        user30k,
        user35k,
        user40k,
        userfull,
    ]

    # take user's splits as text input, interpret numerically, and report
    # pace in minutes per km
    user_numeric = dash_functions.get_user_paces(user_paces)
    
    # find the user's "fatigue zone", the split they ran the slowest
    fatigue_zone = dash_functions.get_fatigue_zone(user_numeric, split_list)

    # find the mean pace for each split for the selected demographic
    mean_paces = dash_functions.get_mean_pace(subset, split_list)
    # and for the top performers in that demographic
    mean_paces_w = dash_functions.get_mean_pace(subset_winners, split_list)

    # create a trace for the selected demographic
    trace_historic_data = go.Scatter(
        x=split_list,
        y=mean_paces,
        name="Selected Demographic Average Paces",
        mode="lines+markers",
        line=dict(color="yellowgreen", width=2),
    )

    # create a trace for the top performers in the selected demographic
    trace_historic_winners = go.Scatter(
        x=split_list,
        y=mean_paces_w,
        name="Top 10% of Selcted Demographic Average Paces",
        mode="lines+markers",
        line=dict(color="gold", width=2),
    )

    # create a trace for the user submitted data
    trace_user_data = go.Scatter(
        x=split_list,
        y=user_numeric,
        name="User Paces",
        mode="lines+markers",
        line=dict(color="skyblue", width=2),
    )

    # create a second trace for the user to connect submitted splits
    # across distances which do not have data; display dashed line
    trace_user_data_extrap = go.Scatter(
        x=split_list,
        y=user_numeric,
        name="User Paces",
        mode="lines+markers",
        connectgaps=True,
        showlegend=False,
        line=dict(color="skyblue", width=2, dash="dot"),
    )

    return {
        # display all traces on the shared, fixed axes
        "data": [
            trace_historic_data,
            trace_historic_winners,
            trace_user_data,
            trace_user_data_extrap,
        ],
        "layout": go.Layout(
            xaxis={"title": "splits"},
            yaxis=dict(range=[10, 3], title="Average Pace in Minutes/km"),
            margin={"l": 40, "b": 40, "t": 10, "r": 0},
            hovermode="closest",
            shapes=[
                {
                    "type": "rect",
                    "xref": "x",
                    "yref": "paper",
                    "x0": fatigue_zone,
                    "x1": fatigue_zone,
                    "y0": 0,
                    "y1": 7,
                    "opacity": 0.2,
                    "line": {"color": "skyblue", "width": 15},
                }
            ],
            annotations=[
                    dict(
                        x=fatigue_zone,
                        y=9.5,
                        xref="x",
                        yref="y",
                        text='Fatigue Zone',
                        showarrow=False,
                        arrowhead=7,
                        ax=0,
                        ay=-40
                    )
            ]
        ),
    }
        
@app.callback(
    Output("split-hist", "figure"),
    [Input("submit-button", "n_clicks")],
    [
        State("gender_select", "value"),
        State("age_select", "value"),
        State("5k-input", "value"),
        State("10k-input", "value"),
        State("15k-input", "value"),
        State("20k-input", "value"),
        State("half-input", "value"),
        State("25k-input", "value"),
        State("30k-input", "value"),
        State("35k-input", "value"),
        State("40k-input", "value"),
        State("full-input", "value"),
    ],
)
def update_hist(
    n_clicks,
    gender_,
    age_,
    user5k,
    user10k,
    user15k,
    user20k,
    userhalf,
    user25k,
    user30k,
    user35k,
    user40k,
    userfull,
):
    """
    This function updates the histograms based on user's demographic selection
    and input half and full marathon times when the submit button is pressed.
    Parameters:
    n_clicks (dash state): introduces pressed-state of submit button to the
    function; must be passed as input or function will not update.
    gender_ (dash state): user's selectio in the gender drop-down menu
    age_ (dash state): user's age group selectio in age drop-down menu
    user5k (string): user 5k split if entered
    user10k (string): user 10k split if entered
    user15k (string): user 15k split if entered
    user20k (string): user 20k split if entered
    userhalf (string): user half marathon split if entered
    user25k (string): user 25k split if entered
    user30k (string): user 30k split if entered
    user35k (string): user 35k split if entered
    user40k (string): user 40k split if entered
    userfull (string): user full marathon finish time if entered
    Returns:
    updates the histogram
    """
    # subset the data based on user's age and gender selection
    subset = dash_functions.get_subset(df, age_, gender_)

    # select the top performers from the selected demographic (top 10%)
    subset_winners = dash_functions.get_top(subset, 0.1)

    # find the split ratios for the selected demographic and top performers
    subset = dash_functions.get_split_ratio(subset)
    subset_winners = dash_functions.get_split_ratio(subset_winners)

    # create variables needed to interpret user's split data
    user_paces = [
        user5k,
        user10k,
        user15k,
        user20k,
        userhalf,
        user25k,
        user30k,
        user35k,
        user40k,
        userfull,
    ]

    # take user's splits as text input, interpret numerically, and find
    # total times in seconds
    user_numeric_time = dash_functions.get_user_times(user_paces)

    # find the user's split ratio only if they have provided a full marathon
    # time and a half marathon time
    try:
        user_first_half = user_numeric_time[4]
        user_second_half = user_numeric_time[9] - user_first_half
        user_x = float(user_second_half / user_first_half)
        user_y = 3000
    except:
        user_x = 0
        user_y = 0

    # create a histogram for split ratios of the selected demographic
    trace_demo_hist = go.Histogram(
        x=subset["split_ratio"],
        opacity=0.5,
        name="Selcted Demographic",
        marker=dict(color="yellowgreen"),
        histnorm="probability",
    )

    # create a histogram for split ratios of the top performers
    trace_winners_hist = go.Histogram(
        x=subset_winners["split_ratio"],
        opacity=0.5,
        name="Top 10% of Selcted Demographic",
        marker=dict(color="gold"),
        histnorm="probability",
    )
    
    # create a trace of nothing to add an extra entry to the key
    trace_fake = go.Scatter(
        x=[],
        y=[],
        name="User Split Ratio",
        mode="lines+markers",
        line=dict(color="skyblue", width=2),
        showlegend=True,
    )

    # display both histograms and a vertical line giving the user's split ratio
    # on shared, unfixed axes
    return {
        "data": [trace_demo_hist, trace_winners_hist, trace_fake],
        "layout": go.Layout(
            xaxis=dict(title="Split Ratio Distribution for Selected Demographic", range=[0, 2]),
            yaxis=dict(title="Proportion of Group"),
            barmode="overlay",
            shapes=[
                {
                    "type": "line",
                    "xref": "x",
                    "yref": "paper",
                    "x0": user_x,
                    "x1": user_x,
                    "y0": 0,
                    "y1": user_y,
                    "line": {"color": "skyblue", "width": 3},
                }
            ],
        ),
    }


if __name__ == "__main__":
    app.run_server(debug=False)
