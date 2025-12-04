#
# Published to https://cda296d2-afd5-4634-8d4c-1ae9fc74cee5.plotly.app/
#

#%%
# Imports
from pathlib import Path
import numpy as np
import pandas as pd

import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objs as go
#import plotly.plotly as py

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State

#%%
# Load Data
datafile = "firearm_data_cleaned.csv"
datadir = "Data/processed"
parents = 0
filepath = Path(datafile)
while not filepath.is_file() and parents < 4:
    filepath = Path("".join(["../"] * parents) + f"/{datadir}/{datafile}")
    parents += 1
df = pd.read_csv(filepath)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# %%
# Animated Choropleth Map
fig_state_rate = px.choropleth(df,
                    locations='state',
                    locationmode='USA-states',
                    color='rate',
                    color_continuous_scale='Purples',
                    range_color=[0,40],
                    animation_frame='year',
                    scope="usa",
                    labels={'rate':'Death per\n100,000'},
                    title='U.S. Firearm Death Rate by State'
                   )


# %%
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

#%%
@app.callback(
    Output('data-container', 'figure'),
    Input('data-button', 'n_clicks')
)
def load_data_for_tab(_):

    return [dcc.Graph(figure=ff.create_table(df))]


# Create each tab separately (to avoid heavy indentation in app.layout, and make rearranging easier)

tab_intro = dcc.Tab(
    label = 'Introduction',
    children = [
        dcc.Markdown('''
            ## DS 6021 Machine Learning Project
            Barnes, Chloe;
            Dallas, Ryan;
            Luedtke, Terry;
            Robinson, Shiraz;
            Threat, Tiandre

            ## Data Sources
            1. [CDC mortality](https://www.cdc.gov/nchs/state-stats/deaths/firearms.html):
                - *Description:*
                - *Key fields:* `STATE`, `YEAR`, `RATE`(per 100K), `DEATHS`
                - *File:* `data-table.csv`
            2. [RAND State Firearm Database](https://www.rand.org/pubs/tools/TLA243-2-v3.html)
                - *Key fields:* `Law ID`, `State`, `Law Class`, `Effect`(Restrictive/Permissive), `Type of Change(Implement/Modify/Repeal)`, `Effective Date Year`
                - *File:* `TL-A243-2-v3 State Firearm Law Database 5.0.xlsx` (sheet: `Database`)

            ## Feature Engineering Summary
            - Score Rules:
                - +1: `Effect == Restrictive` & `Type of Change ∈ {Implement, Modify}`
                - −1: `Effect == Permissive` & `Type of Change ∈ {Implement, Modify}`
                - **Repeal** flips sign accordingly (repeal restrictive -> −1; repeal permissive -> +1)
            - Annual roll-up:
                - `law_strength_score` (sum of scores per state-year)
                - counts: `restrictive_laws`, `permissive_laws`, `total_law_changes`
                - per-class strength and counts (wide columns)
            - Outcome helpers
                - `high_risk`: 1 if `rate >= 75th` percentile within year; else 0
                - `rate_change`, `law_strength_change` (year-over-year within state)
                - `restrictive_ratio`, `permissive_ratio` = proportion of changes within year
                        
            ''')
    ]
) # End of tab_intro


tab_usmap = dcc.Tab(
    label = 'Firearm Death Rate Map',
    children = [
        dcc.Graph(id = 'usmap', figure = fig_state_rate)
    ]
) # End of tab_usmap


tab_data = dcc.Tab(
    label = 'Data Sources',
    children = [
        html.Button('Load Data', id='data-button', n_clicks=0),
        dcc.Graph(id='data-container')
    ]
) # End of tab_data


app.layout = html.Div([
    html.H1("U.S. Gun Law Effectiveness", style={'textAlign': 'center'}),
    html.H2('A State-Level Firearm Policy Analysis'),
    dcc.Tabs(
        [
            tab_intro,
            tab_usmap,
            tab_data
        ]
    )
])

# %%
if __name__ == '__main__':
    app.run(debug=True)
# %%
