import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd

app = dash.Dash(__name__)

df = pd.DataFrame({
    "Категория": ["A", "B", "C", "D"],
    "Значение": [10, 20, 30, 40]
})

fig = px.bar(df, x="Категория", y="Значение", title="Пример графика")

app.layout = html.Div([
    html.H1("Пример Dash"),
    dcc.Graph(figure=fig)
])

if __name__ == '__main__':
    app.run_server(debug=True)
