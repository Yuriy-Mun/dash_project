import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 📌 Загрузка данных
df_checkups = pd.read_csv("checkups_data.csv", parse_dates=["date"])

# Создаём Dash-приложение
app = dash.Dash(__name__)
server = app.server

# 📌 Общие фильтры для всех дашбордов
filters = html.Div([
    html.Div([
        dcc.Dropdown(
            id='clinic-filter',
            options=[{"label": c, "value": c} for c in df_checkups["clinic"].unique()],
            value=list(df_checkups["clinic"].unique()),
            multi=True,
            clearable=False,
            style={
                'width': '280px',
                'height': '42px',
                'font-size': '16px',
            }
        ),
        dcc.DatePickerRange(
            id='date-filter',
            start_date=df_checkups["date"].min(),
            end_date=df_checkups["date"].max(),
            display_format='YYYY-MM-DD',
            style={'width': '400px'}
        )
    ], style={'display': 'flex', 'gap': '20px', 'justify-content': 'center'})
], style={'margin': '20px'})

# 📌 Интерфейс дашборда
app.layout = html.Div([
    html.H1("Аналитика медицинских чек-апов", style={'textAlign': 'center'}),
    filters,
    
    # Первый ряд дашбордов
    html.Div([
        # Дашборд 1: Общая статистика
        html.Div([
            html.H3("Общая статистика", style={'textAlign': 'center'}),
            html.Div(id='total-stats')
        ], style={'width': '48%', 'margin': '1%', 'padding': '20px', 'boxShadow': '0px 0px 10px rgba(0,0,0,0.1)'}),
        
        # Дашборд 2: График тренда
        html.Div([
            html.H3("Тренд чек-апов", style={'textAlign': 'center'}),
            dcc.Graph(id='trend-graph')
        ], style={'width': '48%', 'margin': '1%', 'padding': '20px', 'boxShadow': '0px 0px 10px rgba(0,0,0,0.1)'})
    ], style={'display': 'flex', 'margin': '20px 0'}),
    
    # Второй ряд дашбордов
    html.Div([
        # Дашборд 3: Тепловая карта
        html.Div([
            html.H3("Тепловая карта загруженности", style={'textAlign': 'center'}),
            dcc.Graph(id='heatmap')
        ], style={'width': '48%', 'margin': '1%', 'padding': '20px', 'boxShadow': '0px 0px 10px rgba(0,0,0,0.1)'}),
        
        # Дашборд 4: Статистика по врачам
        html.Div([
            html.H3("Статистика по врачам", style={'textAlign': 'center'}),
            dcc.Graph(id='doctors-stats')
        ], style={'width': '48%', 'margin': '1%', 'padding': '20px', 'boxShadow': '0px 0px 10px rgba(0,0,0,0.1)'})
    ], style={'display': 'flex', 'margin': '20px 0'}),
    
    # Третий ряд дашбордов
    html.Div([
        # Дашборд 5: Сравнение периодов
        html.Div([
            html.H3("Сравнение периодов", style={'textAlign': 'center'}),
            dcc.Graph(id='period-comparison')
        ], style={'width': '48%', 'margin': '1%', 'padding': '20px', 'boxShadow': '0px 0px 10px rgba(0,0,0,0.1)'}),
        
        # Дашборд 6: Дополнительная аналитика
        html.Div([
            html.H3("Дополнительная аналитика", style={'textAlign': 'center'}),
            dcc.Graph(id='additional-analytics')
        ], style={'width': '48%', 'margin': '1%', 'padding': '20px', 'boxShadow': '0px 0px 10px rgba(0,0,0,0.1)'})
    ], style={'display': 'flex', 'margin': '20px 0'})
])

# Callback для общей статистики
@app.callback(
    Output('total-stats', 'children'),
    [Input('clinic-filter', 'value'),
     Input('date-filter', 'start_date'),
     Input('date-filter', 'end_date')]
)
def update_total_stats(selected_clinics, start_date, end_date):
    df_filtered = df_checkups[
        (df_checkups["clinic"].isin(selected_clinics)) &
        (df_checkups["date"] >= start_date) &
        (df_checkups["date"] <= end_date)
    ]
    
    total_checkups = df_filtered["checkups"].sum()
    avg_daily = df_filtered.groupby("date")["checkups"].sum().mean()
    
    return html.Div([
        html.P(f"Всего чек-апов: {total_checkups}"),
        html.P(f"Среднее в день: {avg_daily:.1f}")
    ])

# Callback для графика тренда
@app.callback(
    Output('trend-graph', 'figure'),
    [Input('clinic-filter', 'value'),
     Input('date-filter', 'start_date'),
     Input('date-filter', 'end_date')]
)
def update_trend(selected_clinics, start_date, end_date):
    df_filtered = df_checkups[
        (df_checkups["clinic"].isin(selected_clinics)) &
        (df_checkups["date"] >= start_date) &
        (df_checkups["date"] <= end_date)
    ]
    
    fig = px.line(df_filtered, x="date", y="checkups", color="clinic")
    return fig

# Здесь нужно добавить остальные callbacks для других графиков
# Я могу их реализовать после того, как вы уточните требования к каждому дашборду

if __name__ == '__main__':
    app.run_server(debug=True)
