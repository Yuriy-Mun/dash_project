import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px

# 📌 Загрузка данных
df = pd.read_csv("checkups_data.csv", parse_dates=["date"])

# 📌 Функция для загрузки данных из CSV
def load_data():
    """
    Функция загружает CSV-файл и преобразует столбец даты в формат datetime.
    """
    df = pd.read_csv("checkups_data.csv", parse_dates=["date"])  # Загружаем CSV-файл
    return df

# Загружаем данные при запуске
df_checkups = load_data()

# Создаём Dash-приложение
app = dash.Dash(__name__)
server = app.server  # Для деплоя

# 📌 Интерфейс дашборда
app.layout = html.Div([
    html.H1("Аналитика медицинских чек-апов", style={'textAlign': 'center'}),

    # 🔹 Фильтры: выбор клиник и даты
    html.Div([
        dcc.Dropdown(
            id='clinic-filter',
            options=[{"label": c, "value": c} for c in df_checkups["clinic"].unique()],
            value=list(df_checkups["clinic"].unique()),  # Значение по умолчанию — все клиники
            multi=True,  # Позволяет выбирать несколько клиник
            clearable=False,
            style={
                'width': '280px',
                'height': '42px',
                'font-size': '16px',
                'text-align': 'center',
                'border': '1px solid #ccc',
                'border-radius': '5px',
                'box-shadow': 'none',
                'outline': 'none',
                'box-sizing': 'border-box',
                'vertical-align': 'middle'
            }
        ),
        dcc.DatePickerRange(
            id='date-filter',
            start_date=df_checkups["date"].min(),
            end_date=df_checkups["date"].max(),
            display_format='YYYY-MM-DD',
            style={
                'height': '42px',
                'font-size': '16px',
                'border': '1px solid #ccc',
                'border-radius': '5px',
                'padding': '5px',
                'box-shadow': 'none',
                'outline': 'none',
                'box-sizing': 'border-box',
                'vertical-align': 'middle'
            }
        )
    ], style={'display': 'flex', 'gap': '10px', 'justify-content': 'center', 'align-items': 'center'}),

    # 🔹 Блок сравнения количества чек-апов за текущую и прошлую неделю
    html.Div([
        html.H3("Сравнение чек-апов за текущую и прошлую неделю", style={'textAlign': 'center'}),
        html.Div([
            html.Div([
                html.H4("Текущая неделя"),
                html.P(id="current-week-checkups", style={"fontSize": "20px", "fontWeight": "bold"})
            ], style={"width": "50%", "textAlign": "center"}),

            html.Div([
                html.H4("Прошлая неделя"),
                html.P(id="previous-week-checkups", style={"fontSize": "20px", "fontWeight": "bold"})
            ], style={"width": "50%", "textAlign": "center"})
        ], style={"display": "flex", "justifyContent": "center"}),

        html.P(id="percentage-change", style={"textAlign": "center", "fontSize": "18px", "marginTop": "10px"})
    ], style={"marginBottom": "20px"}),

    # 🔹 Блок горячей карты чек-апов
    html.Div([
        html.H3("Горячая карта чек-апов", style={'textAlign': 'center'}),
        dcc.Graph(id="heatmap-checkups")
    ], style={"marginBottom": "20px"}),

    # 🔹 Среднее количество чек-апов за день
    html.Div([
        html.H3("Среднее число чек-апов в день", style={"textAlign": "center"}),
        html.P(id="avg-checkups", style={"fontSize": "20px", "textAlign": "center", "fontWeight": "bold"})
    ]),

    # 🔹 График динамики чек-апов
    dcc.Graph(id='checkup-trend')
])

# 📌 Callback для обновления графика
@app.callback(
    Output("checkup-trend", "figure"),
    [Input("clinic-filter", "value"), Input("date-filter", "start_date"), Input("date-filter", "end_date")]
)
def update_graph(selected_clinics, start_date, end_date):
    """
    Функция обновляет график на основе выбранных клиник и дат.
    """
    df_checkups = load_data()

    df_filtered = df_checkups[
        (df_checkups["clinic"].isin(selected_clinics)) &
        (df_checkups["date"] >= start_date) &
        (df_checkups["date"] <= end_date)
    ]

    df_filtered = df_filtered[df_filtered["date"].dt.dayofweek != 6]  # Удаляем воскресенья

    data = []
    for clinic in selected_clinics:
        df_clinic = df_filtered[df_filtered["clinic"] == clinic]
        data.append({
            "x": df_clinic["date"],
            "y": df_clinic["checkups"],
            "type": "line",
            "name": clinic
        })

    figure = {
        "data": data,
        "layout": {
            "title": "Динамика медицинских чек-апов",
            "xaxis": {"tickformat": "%Y-%m-%d", "tickangle": -45},
            "yaxis": {"title": "Чек-апы"}
        }
    }
    return figure

# 📌 Callback для расчета среднего количества чек-апов (без учета воскресений)
@app.callback(
    Output("avg-checkups", "children"),
    [Input("clinic-filter", "value"), Input("date-filter", "start_date"), Input("date-filter", "end_date")]
)
def update_avg_checkups(selected_clinics, start_date, end_date):
    df_checkups = load_data()

    df_filtered = df_checkups[
        (df_checkups["clinic"].isin(selected_clinics)) & 
        (df_checkups["date"] >= start_date) & 
        (df_checkups["date"] <= end_date)
    ]

    df_filtered = df_filtered[df_filtered["date"].dt.dayofweek != 6]  # Убираем воскресенья

    if df_filtered.empty:
        return "Нет данных"

    avg_checkups = df_filtered["checkups"].sum() / df_filtered["date"].nunique()
    return f"{avg_checkups:.2f} чек-апов в день"

# 📌 Запуск приложения
if __name__ == '__main__':
    app.run_server(debug=True)
