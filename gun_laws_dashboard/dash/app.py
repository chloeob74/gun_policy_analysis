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


# %%
# Load markdown and css files
#
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
with open("intro.md", 'r') as file:
        md_intro = file.read()
with open("datasources.md", 'r') as file:
        md_data_sources = file.read()

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
df_raw = df.copy()


# %%
# Choloropleth Maps

# # Aggregate for multiple rows per state-year
# law_map = (
#     df_raw.copy().groupby(["year", "state"], as_index=False)["law_strength_score"]
#        .mean()
# )
# law_map["law_strength_score"] = law_map["law_strength_score"].round(2)

fig_map_lawstrength = px.choropleth(
    df,
    locations="state", 
    locationmode="USA-states",
    color="law_strength_score",
    animation_frame="year",
    scope="usa",
    color_continuous_scale="Viridis",
    range_color=(0, 70),
    labels={"law_strength_score": "Gun Law Strength Score"},
    title="Gun Law Strength by State Over Time (2014–2023)"
)

fig_map_deathrate = px.choropleth(
    df,
    locations="state", 
    locationmode="USA-states",
    color="rate",
    animation_frame="year",
    scope="usa",
    color_continuous_scale="Viridis",
    range_color=(0, 35),
    labels={"rate": "Gun Death Rate per 100,000"},
    title="Gun Death Rate by State Over Time (2014–2023)"
)


# %%
# Dash App Layout
#
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


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
                - *Key fields:* STATE`, `YEAR`, `RATE`(per 100K), `DEATHS`
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
                - per-class strength score (wide columns)
            - Outcome helpers
                - `rate_change`, `law_strength_change` (year-over-year within state)
                - `restrictive_ratio`, `permissive_ratio` = proportion of changes within year
                        
            '''),

        dcc.Markdown(md_intro)
    ]
) # End of tab_intro


tab_usmap = dcc.Tab(
    label = 'State Maps',
    children = [
        dcc.Graph(id='usmap_law', figure=fig_map_lawstrength),
        dcc.Graph(id='usmap_rate', figure=fig_map_deathrate)
    ]
) # End of tab_usmap


tab_holder1 = dcc.Tab(
    label = 'Placeholder 1',
    children = [
        dcc.Markdown("What do we want here?")
    ]
) # End of tab_placeholder1

tab_holder2 = dcc.Tab(
    label = 'Placeholder 2',
    children = [
        dcc.Markdown("What do we want here?")
    ]
) # End of tab_placeholder2

tab_data = dcc.Tab(
    label = 'Data Sources',
    children = [
        dcc.Markdown(md_data_sources)
    ]
) # End of tab_data


app.layout = html.Div([
    html.H1("U.S. Gun Law Effectiveness", style={'textAlign': 'center'}),
    html.H2('A State-Level Firearm Policy Analysis', style={'textAlign': 'center'}),
    dcc.Tabs(
        [
            tab_intro,
            tab_holder1,
            tab_usmap,
            tab_holder2,
            tab_data
        ]
    )
])

# %%
if __name__ == '__main__':
    app.run(debug=True)
# %%
