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
import statsmodels.api as sm

import dash
from dash import dcc
from dash import html
from dash import dash_table
from dash.dash_table.Format import Format, Scheme
from dash.dependencies import Input, Output, State


# %%
# Load markdown and css files
#
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
with open("intro.md", 'r') as file:
        md_intro = file.read()
with open("datasources.md", 'r') as file:
        md_data_sources = file.read()

with open("research_q1.md", 'r') as file:           # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< START
        research_q1 = file.read()           
with open('research_q1_bottom.md', 'r') as file:
        research_q1_bottom = file.read()            # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< STOP

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

numeric_cols = df[['rate', 'deaths', 'law_strength_score', 'restrictive_laws', 
                'permissive_laws', 'total_law_changes', 'unique_law_classes', 
                'rate_change', 'law_strength_change', 'restrictive_ratio', 
                'permissive_ratio']]
df_subset = df[['year', 'state', 'state_name', 'rate', 'deaths', 'law_strength_score',
                'restrictive_laws', 'permissive_laws', 'total_law_changes', 'unique_law_classes',
                'rate_change', 'law_strength_change', 'restrictive_ratio', 'permissive_ratio']].copy()

# 
# Some useful subsets of the data
#

# Some analysis has problems with missing years, so exclude DC which has only 2022, 2023
noDC = df[df['state'] != 'District of Columbia']

# Identify law strength features (our primary predictors)
law_features = [col for col in df.columns if col.startswith('strength_')]
permissive_classes = [col for col in df.columns if col.startswith('class_permissive_')]
restrictive_classes = [col for col in df.columns if col.startswith('class_restrictive_')]
feature_classes = permissive_classes + restrictive_classes

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

def graph_strength_correlations(df):

     # Calculate correlations
    recent_data = df[df['year'] == df['year'].max()][['state_name', 'rate'] + law_features].dropna()
    correlations = recent_data[law_features + ['rate']].corr()['rate'].drop('rate')
    cor_df = pd.DataFrame({
        'Law Type': [f.replace('strength_', '').replace('_', ' ').title() for f in correlations.index],
        'Correlation': correlations.values
    }).sort_values('Correlation', key=abs, ascending=False)

    cor_df['pos'] = cor_df['Correlation'] > 0
    fig1a = px.bar(cor_df, x='Correlation', y='Law Type', orientation='h',
              color='pos',
              category_orders={"Law Type": cor_df["Law Type"].to_list()},
            title=f'Association of Each Law Strength with Firearm Death Rate',
              hover_name="Law Type", hover_data={'pos':False, 'Law Type':False, 'Correlation': True}
              )
    fig1a.update_yaxes(type='category')
    fig1a.update_yaxes({'gridcolor': 'white'})        
    fig1a.update_xaxes({'gridcolor': None, 'zerolinecolor': 'black', 'linecolor': None, 'zerolinewidth': 2})    
    fig1a.update_layout(xaxis_title='Correlation with Death Rate', showlegend=False, yaxis={'dtick': 1})
    
    return fig1a

fig_strength_correlations = graph_strength_correlations(df)


def graph_feature_correlations(df):
     
    # Calculate correlations with death rate
    # Exclude classes with zero variance since they have no predictive power, and therefore cause nans in the correlation matrix
    non_zero_v_feature_classes = df[feature_classes].std()[df[feature_classes].std() != 0].index.to_list()

    # Calculate correlations
    correlations = df[non_zero_v_feature_classes + ['rate']].corr()['rate'].drop('rate')
    cor2_df = pd.DataFrame({
        'Law Type': [f.replace('class_', '').replace('_', ' ').title() for f in correlations.index],
        'Correlation': correlations.values
    }).sort_values(by='Correlation', key=abs, ascending=False)

    cor2_df['pos'] = cor2_df['Correlation'] > 0
    fig2a = px.bar(cor2_df, x='Correlation', y='Law Type', orientation='h',
            color='pos',
            category_orders={"Law Type": cor2_df["Law Type"].to_list()},
            title=f'Association of Each Feature with Firearm Death Rate',
            hover_name="Law Type", hover_data={'pos':False, 'Law Type':False, 'Correlation': True}
            )
    fig2a.update_yaxes(type='category')            
    fig2a.update_yaxes({'gridcolor': 'white'})        
    fig2a.update_xaxes({'gridcolor': None, 'zerolinecolor': 'black', 'linecolor': None, 'zerolinewidth': 2})    
    fig2a.update_layout(xaxis_title='Correlation with Death Rate', yaxis_title='Feature', showlegend=False, yaxis={'dtick': 1})
    
    return fig2a

fig_feature_correlations = graph_feature_correlations(df)


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


# Apply formatting to float columns for DataTable
column_specs = [] 
for col in df_subset.columns: 
    if (pd.api.types.is_float_dtype(df_subset[col])):
        column_specs.append({"name": col, "id": col, 
                "type": "numeric", "format": Format(precision=2, scheme=Scheme.fixed)})
    else:
        column_specs.append({"name": col, "id": col})

tab_datatable = dcc.Tab(
     
    label = 'Data Table',
    children = [
          dash_table.DataTable(
              id='data_table',
              columns=column_specs,
              data=df_subset.to_dict('records'),

              filter_action='native',
              sort_action='native',
              sort_mode='multi',

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


                                                            ### <<<<<<<<<<<<<<<<<<<<<<<<< START

labels1 = ['Basic Multi-Linear Regression', 'Ridge Regression', 'PCA']
labels2 = ['Dataset 1', 'Dataset 2']

tab_predictive = dcc.Tab(                          
    label = 'Predicting Gun Violence',
    children = [
    
        dcc.Markdown(research_q1),
        
        html.Div([

            html.Div([
                html.H2('Model'),
                dcc.Dropdown(id='Model_drop',
                     options=[{'label': i, 'value': i} for i in labels1],
                     value='Basic Multi-Linear')
            ], style={'width':'48%', 'float':'left'}),
            
            html.Div([
                html.H2('Dataset'),
                dcc.Dropdown(id='Dataset_drop',
                    options=[{'label': i, 'value': i} for i in labels2],
                    value='Dataset1')
                    ], style = {'width':'48%', 'float':'right'})
        
        ], style = {'width':'100%', 'display':'inline-block'}), 


        html.Div([
            html.Div([
                dcc.Graph(id='model_graph'),
            ], style={'width':'60%', 'float':'left'}),

            html.Div([
                dcc.Graph(id='model_table')
            ], style={'width':'40%', 'float':'right'}),
        ], style = {'width':'100%', 'display':'inline-block'}),
        

        dcc.Markdown(research_q1_bottom)
    
    ]
) # End of tab_predictive

@app.callback([Output(component_id='model_graph', component_property='figure'),
               Output(component_id='model_table', component_property='figure')],
              [Input(component_id='Model_drop', component_property='value',),
               Input(component_id='Dataset_drop', component_property='value')])

def show_the_graph_and_table(mod_choice, data_choice):

    data = pd.DataFrame(index=['model_performance'])
    adj_r2 = 0
    rmse = 0

    if(data_choice == 'Dataset 1'):
        if mod_choice == 'PCA':
            data = pd.read_csv('pca_output_data1.csv')
            adj_r2 = '-1.481'
            rmse = '4.652'
        elif mod_choice == 'Ridge Regression':
            data = pd.read_csv('ridge_output_data1.csv')
            adj_r2 = '0.938'
            rmse = '1.280'
        else: # mod_choice = Basic Multi-Linear Regression
            data = pd.read_csv('basic_output_data1.csv')    
            adj_r2 = '0.946'
            rmse = '1.277'
    
    else: # data_choice = 'Dataset 2'
        if mod_choice == 'PCA':
            data = pd.read_csv('pca_output_data2.csv')
            adj_r2 = '-1.689'
            rmse = '4.280'
        elif mod_choice == 'Ridge Regression':
            data = pd.read_csv('ridge_output_data2.csv')
            adj_r2 = '0.893'
            rmse = '1.689'
        else: # mod_choice = Basic Multi-Linear Regression
            data = pd.read_csv('basic_output_data2.csv') 
            adj_r2 = '0.904'
            rmse = '1.597'

    df = pd.DataFrame({'Adjusted r^2': [adj_r2], 'RMSE': [rmse]})
    #df_1 = df.T.reset_index()
    #df_1=df_1.rename({'index': 'RMSE', 1:'Adjusted r^2'}, axis=1)

    out_graph = px.scatter(data, x='predicted', y='actual',
                           trendline='ols')
    out_table = ff.create_table(df)

    return [out_graph, out_table]

                                                    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< STOP
# End of tab_predictive


tab_effectiveness = dcc.Tab(
    label = 'Effectiveness Metrics',
    children = [
        dcc.Graph(id='strength_correlations', figure=fig_strength_correlations),
        dcc.Graph(id='feature_correlations', figure=fig_feature_correlations)
        ]
) # End of tab_effectiveness

style_center_image={'width':'80%', 'margin-left':'auto', 'margin-right':'auto', 'display':'block'}
tab_clusters = dcc.Tab(
    label = 'State Clusters',
    children = [
        html.Img(src=app.get_asset_url('kmeans_elbow.png'), style=style_center_image),
        html.Img(src=app.get_asset_url('ward_dendrogram.png'), style=style_center_image),
        html.Img(src=app.get_asset_url('pca_clusters.png'), style=style_center_image)
        ]
) # End of tab_clusters


tab_data = dcc.Tab(
    label = 'Data Sources',
    children = [
        dcc.Markdown(md_data_sources)
    ]
) # End of tab_data


app.layout = html.Div([
    html.H1("U.S. Gun Law Effectiveness", style={'textAlign': 'center'}),
    html.H3('A State-Level Firearm Policy Analysis', style={'textAlign': 'center'}),
    dcc.Tabs(
        [
            tab_intro,
            tab_datatable,
            tab_usmap,
            tab_predictive,
            tab_effectiveness,
            tab_clusters,
            tab_data
        ]
    )
])

# %%
if __name__ == '__main__':
    app.run(debug=True)
# %%