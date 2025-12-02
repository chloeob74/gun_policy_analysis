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
from dash.dependencies import Input, Output

#%%
# Load Data
datafile = "firearm_data_cleaned.csv"
datadir = "Data/processed"
parents = 0
filepath = Path(datafile)
while filepath.is_file() == False and parents < 4:
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
fig_state_rate.show()

# %%
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    html.H1("U.S. Gun Law Effectiveness", style={'textAlign': 'center'}),
    dcc.Graph(figure=fig_state_rate)
])

# %%
if __name__ == '__main__':
    app.run(debug=True)
# %%
