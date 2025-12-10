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
from dash import dash_table
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
df_subset = df[['year', 'state', 'state_name', 'rate', 'deaths', 'law_strength_score',
                'restrictive_laws', 'permissive_laws', 'total_law_changes', 'unique_law_classes',
                'rate_change', 'law_strength_change', 'restrictive_ratio', 'permissive_ratio']]


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
    color_continuous_scale=px.colors.sequential.Viridis[::-1],
    range_color=(0, 70),
    labels={"year": "Year", 
            "law_strength_score": "Gun Law Strength Score"},
    title="Gun Law Strength by State Over Time (2014–2023)",
    hover_name="state_name",
    hover_data={
        "year": True,
        'state': False,
        'law_strength_score': True,}
)

fig_map_deathrate = px.choropleth(
    df,
    locations="state", 
    locationmode="USA-states",
    color="rate",
    animation_frame="year",
    scope="usa",
    color_continuous_scale=px.colors.sequential.Viridis[::-1],
    range_color=(0, 35),
    labels={'year': 'Year',
            'rate': 'Gun Death Rate per 100,000'},
    title="Gun Death Rate by State Over Time (2014–2023)",
    hover_name="state_name",
    hover_data={
        "year": True,
        'state': False,
        'rate': True,}
)


def generate_table (df, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in df.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(df.iloc[i][col]) for col in df.columns
            ]) for i in range(min(len(df), max_rows))
        ])
    ])


# %%
# Dash App Layout
#
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


# Create each tab separately (to avoid heavy indentation in app.layout, and make rearranging easier)

tab_intro = dcc.Tab(
    label = 'Introduction',
    children = [
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


tab_datatable = dcc.Tab(
    label = 'Data Table',
    children = [
          dash_table.DataTable(
              id='data_table',
              columns=[{"name": i, "id": i} for i in df_subset.columns],
              data=df_subset.to_dict('records'),

              filter_action='native',
              sort_action='native',
              sort_mode='multi',
              page_action='native',
              page_current=0,
              page_size=20,

              fixed_rows={'headers': True},
              style_table={'height': '500px', 
                           'overflowY': 'auto', 
                           'overflowX': 'auto'},

              style_cell={'textAlign': 'left', 
                          'padding': '5px', 
                          'minWidth': '180px', 
                          'width': '180px', 
                          'maxWidth': '200px'},
          )
    ]
) # End of tab_datatable

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
            tab_datatable,
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
