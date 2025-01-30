import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Загрузка данных с обработкой ошибок
try:
    df_checkups = pd.read_csv("data/Doctor_in_Adult_check-ups_daily.csv", parse_dates=["date"])
    df_therapist = pd.read_csv("data/Therapist_in_Adult_check-ups_daily.csv", parse_dates=["date"])
    
    # Объединяем данные из обеих клиник
    df_checkups = pd.concat([
        df_checkups.assign(clinic='deFactum'),
        df_therapist.assign(clinic='deFactum_Kids')
    ]).reset_index(drop=True)
except Exception as e:
    print(f"Ошибка при загрузке данных: {e}")
    df_checkups = pd.DataFrame(columns=["date", "checkups", "clinic"])

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

# Функция для получения номера недели
def get_week_number(date):
    try:
        return date.isocalendar()[1]
    except:
        return None

# Функция для получения начала и конца недели
def get_week_dates(date):
    try:
        start = date - timedelta(days=date.weekday())
        end = start + timedelta(days=6)
        return start, end
    except:
        today = datetime.now().date()
        return today, today

# Функция для расчета процентного изменения
def calculate_percentage_change(current, previous):
    try:
        if previous == 0:
            return 0
        return ((current - previous) / previous) * 100
    except:
        return 0

# Обновленный callback для общей статистики
@app.callback(
    Output('total-stats', 'children'),
    [Input('clinic-filter', 'value'),
     Input('date-filter', 'start_date'),
     Input('date-filter', 'end_date')]
)
def update_total_stats(selected_clinics, start_date, end_date):
    try:
        # Получаем текущую дату
        today = datetime.now().date()
        
        # Преобразуем строковые даты в datetime
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Получаем даты для текущей, прошлой и позапрошлой недель
        current_week_start, current_week_end = get_week_dates(today)
        last_week_start = current_week_start - timedelta(days=7)
        last_week_end = current_week_end - timedelta(days=7)
        prev_week_start = last_week_start - timedelta(days=7)
        prev_week_end = last_week_end - timedelta(days=7)
        
        # Фильтруем данные
        df_filtered = df_checkups[df_checkups["clinic"].isin(selected_clinics)]
        
        # Получаем количество чек-апов по неделям
        current_week_checkups = df_filtered[
            (df_filtered["date"].dt.date >= current_week_start) & 
            (df_filtered["date"].dt.date <= today)
        ]["checkups"].sum()
        
        last_week_checkups = df_filtered[
            (df_filtered["date"].dt.date >= last_week_start) & 
            (df_filtered["date"].dt.date <= last_week_end)
        ]["checkups"].sum()
        
        prev_week_checkups = df_filtered[
            (df_filtered["date"].dt.date >= prev_week_start) & 
            (df_filtered["date"].dt.date <= prev_week_end)
        ]["checkups"].sum()
        
        # Рассчитываем процент изменения
        percentage_change = calculate_percentage_change(last_week_checkups, prev_week_checkups)
        
        # Получаем общее количество чек-апов за выбранный период
        total_checkups = df_filtered[
            (df_filtered["date"].dt.date >= start_date) & 
            (df_filtered["date"].dt.date <= end_date)
        ]["checkups"].sum()
        
        return html.Div([
            html.Div([
                html.H4("Текущая неделя"),
                html.H2(f"{current_week_checkups}")
            ], style={'textAlign': 'center', 'margin': '10px'}),
            
            html.Div([
                html.H4("Прошлая неделя"),
                html.H2(f"{last_week_checkups}")
            ], style={'textAlign': 'center', 'margin': '10px'}),
            
            html.Div([
                html.H4("Изменение"),
                html.H2(f"{percentage_change:.2f}%")
            ], style={'textAlign': 'center', 'margin': '10px'}),
            
            html.Div([
                html.H4("Всего за период"),
                html.H2(f"{total_checkups}")
            ], style={'textAlign': 'center', 'margin': '10px'})
        ], style={'display': 'flex', 'justifyContent': 'space-around'})
    except Exception as e:
        print(f"Ошибка в update_total_stats: {e}")
        return html.Div("Ошибка при обновлении статистики")

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
