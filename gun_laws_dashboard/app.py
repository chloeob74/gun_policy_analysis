from dash import Dash, html
import dash_ag_grid as dag
import pandas as pd

df = pd.read_csv("../Data/processed/firearm_data_cleaned.csv")

app = Dash(__name__)

app.layout = [
    html.Div(children="Gun Laws Dashboard"),
    dag.AgGrid(
        rowData=df.to_dict("records"),
        columnDefs=[{"field": col} for col in df.columns]
    )
]

if __name__ == '__main__':
    app.run(debug=True)