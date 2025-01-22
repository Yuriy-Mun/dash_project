import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd

# Создаем приложение Dash
app = dash.Dash(__name__)

# Данные для графика
df = pd.DataFrame({
    "Категория": ["A", "B", "C", "D"],
    "Значение": [10, 20, 30, 40]
})

# Создаем график
fig = px.bar(df, x="Категория", y="Значение", title="Пример графика")

# Определяем макет приложения
app.layout = html.Div([
    html.H1("Пример Dash"),
    dcc.Graph(figure=fig)
])

# Это необходимо для Gunicorn
server = app.server  

# Запуск сервера локально
if __name__ == "__main__":
    app.run_server(debug=True)
