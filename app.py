import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

# Загрузка данных с обработкой ошибок
try:
    # Указываем формат даты явно
    df_main = pd.read_csv("data/Main_Table_Clinics.csv")
    df_main['Date'] = pd.to_datetime(df_main['Date'], format='%m/%d/%y')
    df_doctors_adult = pd.read_csv("data/Doctor_in_Adult_check-ups_daily.csv")
    df_doctors_kids = pd.read_csv("data/Doctor_in_kids_check-ups_daily.csv")
except Exception as e:
    print(f"Ошибка при загрузке данных: {e}")
    df_main = pd.DataFrame(columns=["Date", "Day_of_the_week", "Number_of_the_week", "Name_of_clinic", "Count_of_chekups"])
    df_doctors_adult = pd.DataFrame()
    df_doctors_kids = pd.DataFrame()

# Создаём Dash-приложение с темой Bootstrap и пользовательскими ресурсами
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    assets_folder='assets',
    include_assets_files=True,
    suppress_callback_exceptions=True
)
server = app.server

# 📌 Общие фильтры для всех дашбордов
filters = html.Div([
    html.Div([
        # Фильтр клиник
        html.Div([
            html.Div([
                html.H4("Выбор клиники", className='text-xl font-semibold text-gray-800')
            ], className='h-8 flex items-center'),
            html.Div([
                dcc.Dropdown(
                    id='clinic-filter',
                    options=[{"label": c, "value": c} for c in df_main["Name_of_clinic"].unique()],
                    value=list(df_main["Name_of_clinic"].unique()),
                    multi=True,
                    clearable=False,
                    className='w-72'
                )
            ], className='h-10 flex items-center')
        ], className='flex flex-col justify-between'),
        
        # Фильтр дат
        html.Div([
            html.Div([
                html.H4("Выберите период", className='text-xl font-semibold text-gray-800')
            ], className='h-8 flex items-center'),
            html.Div([
                dcc.DatePickerRange(
                    id='date-filter',
                    start_date=df_main["Date"].min(),
                    end_date=df_main["Date"].max(),
                    min_date_allowed=df_main["Date"].min(),
                    max_date_allowed=df_main["Date"].max(),
                    initial_visible_month=df_main["Date"].max(),
                    first_day_of_week=1,
                    display_format='DD.MM.YYYY',
                    month_format='MMMM YYYY',
                    start_date_placeholder_text='От',
                    end_date_placeholder_text='До',
                    calendar_orientation='horizontal',
                    day_size=45,
                    with_portal=True,
                    clearable=False,
                    number_of_months_shown=2,
                    persistence=True,
                    persisted_props=['start_date', 'end_date'],
                    updatemode='bothdates',
                    style={'font-family': 'Arial', 'z-index': '100'}
                )
            ], className='h-10 flex items-center')
        ], className='flex flex-col justify-between')
    ], className='flex justify-center gap-8')
], className='m-5 mb-8')

# Интерфейс дашборда
app.layout = html.Div([
    html.H1("Аналитика медицинских чек-апов", className='text-3xl font-bold text-center my-6 text-gray-800'),
    filters,
    
    # Первый ряд дашбордов
    html.Div([
        # Дашборд 1: Общая статистика
        html.Div([
            html.H3("Общая статистика", className='text-2xl font-semibold text-center mb-6'),
            html.Div(id='total-stats')
        ], className='w-1/2 p-6 m-2 bg-white rounded-lg shadow-lg'),
        
        # Дашборд 2: График тренда
        html.Div([
            html.H3("Тренд чек-апов", className='text-2xl font-semibold text-center mb-6'),
            dcc.Graph(id='trend-graph')
        ], className='w-1/2 p-6 m-2 bg-white rounded-lg shadow-lg')
    ], className='flex mx-5 my-6'),
    
    # Второй ряд дашбордов
    html.Div([
        # Дашборд 3: Тепловая карта
        html.Div([
            html.H3("Тепловая карта загруженности", className='text-2xl font-semibold text-center mb-2'),
            dcc.Graph(id='heatmap')
        ], className='w-1/2 p-6 m-2 bg-white rounded-lg shadow-lg'),
        
        # Дашборд 4: Статистика по врачам
        html.Div([
            html.H3("Статистика по врачам", className='text-xl font-semibold text-center mb-1'),
            html.H4("Количество выполненых чек-апов по врачам", className='text-lg font-medium text-center mb-4'),
            dcc.Graph(id='doctors-stats')
        ], className='w-1/2 p-6 m-2 bg-white rounded-lg shadow-lg')
    ], className='flex mx-5 my-6'),
    
    # Третий ряд дашбордов
    html.Div([
        # Дашборд 5: Сравнение периодов
        html.Div([
            html.H3("Сравнение периодов", className='text-xl font-semibold text-center mb-4'),
            dcc.Graph(id='period-comparison')
        ], className='w-1/2 p-6 m-2 bg-white rounded-lg shadow-lg'),
        
        # Дашборд 6: Дополнительная аналитика
        html.Div([
            html.H3("Дополнительная аналитика", className='text-xl font-semibold text-center mb-4'),
            dcc.Graph(id='additional-analytics')
        ], className='w-1/2 p-6 m-2 bg-white rounded-lg shadow-lg')
    ], className='flex mx-5 my-6')
], className='min-h-screen bg-gray-50')

# Функция для получения номера недели
def get_week_number(date):
    try:
        return date.isocalendar()[1]
    except:
        return None

# Функция для получения начала и конца недели
def get_week_dates(date):
    try:
        # Получаем понедельник текущей недели
        start = date - timedelta(days=date.weekday())
        # Получаем воскресенье текущей недели
        end = start + timedelta(days=6)
        return start, end
    except:
        return date, date

# Функция для расчета процентного изменения
def calculate_percentage_change(current, previous):
    try:
        if previous == 0:
            return 0
        return ((current - previous) / previous) * 100
    except:
        return 0

# Добавим функцию форматирования чисел
def format_number(number):
    return f"{number:,}".replace(",", " ")

# Обновленный callback для общей статистики
@app.callback(
    Output('total-stats', 'children'),
    [Input('clinic-filter', 'value'),
     Input('date-filter', 'start_date'),
     Input('date-filter', 'end_date')]
)
def update_total_stats(selected_clinics, start_date, end_date):
    try:
        # Преобразуем даты
        end_date = pd.to_datetime(end_date).date()
        
        # Получаем даты для текущей недели (с понедельника по выбранную дату)
        current_week_start, _ = get_week_dates(end_date)
        
        # Получаем даты для прошлой недели
        last_week_start = current_week_start - timedelta(days=7)
        last_week_end = current_week_start - timedelta(days=1)
        
        # Получаем даты для позапрошлой недели
        prev_week_start = last_week_start - timedelta(days=7)
        prev_week_end = last_week_start - timedelta(days=1)
        
        # Фильтруем данные
        df_filtered = df_main[df_main["Name_of_clinic"].isin(selected_clinics)]
        
        # Получаем количество чек-апов за текущую неделю (с понедельника по выбранную дату)
        current_week_checkups = df_filtered[
            (df_filtered["Date"].dt.date >= current_week_start) & 
            (df_filtered["Date"].dt.date <= end_date)
        ]["Count_of_chekups"].sum()
        
        # Получаем количество чек-апов за прошлую неделю
        last_week_checkups = df_filtered[
            (df_filtered["Date"].dt.date >= last_week_start) & 
            (df_filtered["Date"].dt.date <= last_week_end)
        ]["Count_of_chekups"].sum()
        
        # Получаем количество чек-апов за позапрошлую неделю
        prev_week_checkups = df_filtered[
            (df_filtered["Date"].dt.date >= prev_week_start) & 
            (df_filtered["Date"].dt.date <= prev_week_end)
        ]["Count_of_chekups"].sum()
        
        # Рассчитываем процент изменения
        percentage_change = calculate_percentage_change(last_week_checkups, prev_week_checkups)
        
        # Получаем общее количество чек-апов за выбранный период
        total_checkups = df_filtered[
            (df_filtered["Date"].dt.date >= pd.to_datetime(start_date).date()) & 
            (df_filtered["Date"].dt.date <= end_date)
        ]["Count_of_chekups"].sum()
        
        return html.Div([
            # Карточка текущей недели
            html.Div([
                html.Div([
                    html.H4("Текущая неделя", className='text-lg font-medium text-gray-600 mb-auto'),
                    html.H2(format_number(current_week_checkups), className='text-3xl font-bold text-gray-800')
                ], className='flex flex-col justify-between h-full min-h-[100px]')
            ], className='bg-white rounded-lg shadow-md p-6'),
            
            # Карточка прошлой недели
            html.Div([
                html.Div([
                    html.H4("Прошлая неделя", className='text-lg font-medium text-gray-600 mb-auto'),
                    html.H2(format_number(last_week_checkups), className='text-3xl font-bold text-gray-800')
                ], className='flex flex-col justify-between h-full min-h-[100px]')
            ], className='bg-white rounded-lg shadow-md p-6'),
            
            # Карточка изменения
            html.Div([
                html.Div([
                    html.H4("Изменение", className='text-lg font-medium text-gray-600 mb-auto'),
                    html.H2(
                        f"{percentage_change:.2f}%",
                        className=f"text-3xl font-bold {'text-green-500' if percentage_change > 0 else 'text-red-500'}"
                    )
                ], className='flex flex-col justify-between h-full min-h-[100px]')
            ], className='bg-white rounded-lg shadow-md p-6'),
            
            # Карточка общего количества
            html.Div([
                html.Div([
                    html.H4("Всего за период", className='text-lg font-medium text-gray-600 mb-auto'),
                    html.H2(format_number(total_checkups), className='text-3xl font-bold text-gray-800')
                ], className='flex flex-col justify-between h-full min-h-[100px]')
            ], className='bg-white rounded-lg shadow-md p-6')
            
        ], className='grid grid-cols-4 gap-2 w-full px-2')
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
    try:
        df_filtered = df_main[
            (df_main["Name_of_clinic"].isin(selected_clinics)) &
            (df_main["Date"] >= pd.to_datetime(start_date)) &
            (df_main["Date"] <= pd.to_datetime(end_date))
        ]
        
        # Создаем словарь для переименования клиник
        clinic_names = {
            'deFactum': 'deFactum',
            'deFactum_Kids': 'deFactum Kids'
        }
        
        # Копируем датафрейм и заменяем названия клиник
        df_filtered = df_filtered.copy()
        df_filtered['Name_of_clinic'] = df_filtered['Name_of_clinic'].map(clinic_names)
        
        fig = px.line(
            df_filtered, 
            x="Date", 
            y="Count_of_chekups", 
            color="Name_of_clinic",
            title="Тренд количества чек-апов по клиникам",
            labels={
                "Date": "",
                "Count_of_chekups": "Количество чек-апов",
                "Name_of_clinic": ""
            }
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            title={
                'text': "Тренд количества чек-апов по клиникам",
                'x': 0.5,
                'y': 0.95,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': dict(size=16, family='Arial', color='#1f2937')
            },
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                font=dict(size=12, family='Arial'),
                bgcolor='rgba(255, 255, 255, 0.8)',
                bordercolor='rgba(0, 0, 0, 0.1)',
                borderwidth=1,
                itemwidth=80,
                itemsizing='constant'
            ),
            margin=dict(t=80, r=20, b=20, l=20),
            xaxis=dict(
                title=dict(text="", font=dict(size=12, family='Arial')),
                tickfont=dict(size=10, family='Arial'),
                tickformat='%b %d'  # Формат даты: месяц день (без года)
            ),
            yaxis=dict(
                title=dict(text="Количество чек-апов", font=dict(size=12, family='Arial')),
                tickfont=dict(size=10, family='Arial')
            )
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            title={
                'text': "Тренд количества чек-апов по клиникам",
                'x': 0.5,
                'y': 0.95,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': dict(size=16, family='Arial', color='#1f2937')
            },
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                font=dict(size=12, family='Arial'),
                bgcolor='rgba(255, 255, 255, 0.8)',
                bordercolor='rgba(0, 0, 0, 0.1)',
                borderwidth=1,
                itemwidth=80,
                itemsizing='constant'
            ),
            margin=dict(t=80, r=20, b=20, l=20),
            xaxis=dict(
                title=dict(text="", font=dict(size=12, family='Arial')),
                tickfont=dict(size=10, family='Arial'),
                tickformat='%b %d'  # Формат даты: месяц день (без года)
            ),
            yaxis=dict(
                title=dict(text="Количество чек-апов", font=dict(size=12, family='Arial')),
                tickfont=dict(size=10, family='Arial')
            )
        )
        
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgb(243, 244, 246)',
            showline=True,
            linewidth=1,
            linecolor='rgb(209, 213, 219)'
        )
        
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgb(243, 244, 246)',
            showline=True,
            linewidth=1,
            linecolor='rgb(209, 213, 219)'
        )
        
        # Обновляем цвета линий
        fig.update_traces(
            line=dict(width=2),
            selector=dict(type='scatter')
        )
        
        return fig
    except Exception as e:
        print(f"Ошибка в update_trend: {e}")
        return go.Figure()

# Обновляем callback для тепловой карты (теперь таблица)
@app.callback(
    Output('heatmap', 'figure'),
    [Input('clinic-filter', 'value'),
     Input('date-filter', 'start_date'),
     Input('date-filter', 'end_date')]
)
def update_heatmap(selected_clinics, start_date, end_date):
    try:
        # Фильтруем данные
        df_filtered = df_main[
            (df_main["Name_of_clinic"].isin(selected_clinics)) &
            (df_main["Date"] >= pd.to_datetime(start_date)) &
            (df_main["Date"] <= pd.to_datetime(end_date))
        ]

        # Переводим английские названия дней на русский с сокращениями
        day_translation = {
            'Monday': 'Пон',
            'Tuesday': 'Вт',
            'Wednesday': 'Ср',
            'Thursday': 'Чт',
            'Friday': 'Пт',
            'Saturday': 'Суб'
        }
        
        # Применяем перевод дней недели
        df_filtered['Day_of_the_week'] = df_filtered['Day_of_the_week'].map(day_translation)

        # Создаем сводную таблицу для тепловой карты
        pivot_data = df_filtered.pivot_table(
            values='Count_of_chekups',
            index='Number_of_the_week',
            columns='Day_of_the_week',
            aggfunc='sum',
            fill_value=0
        )

        # Определяем правильный порядок дней недели
        correct_order = ['Пон', 'Вт', 'Ср', 'Чт', 'Пт', 'Суб']
        pivot_data = pivot_data[correct_order]

        # Добавляем суммы по строкам
        pivot_data['Общий итог'] = pivot_data.sum(axis=1)

        # Добавляем суммы по столбцам и среднее
        total_row = pd.DataFrame(pivot_data.sum()).T
        total_row.index = ['Общий итог']
        
        # Рассчитываем среднее количество чек-апов для каждого дня
        avg_row = pd.DataFrame(pivot_data.mean()).T
        avg_row.index = ['Среднее']
        
        # Объединяем все строки
        pivot_data = pd.concat([pivot_data, avg_row, total_row])

        # Создаем тепловую карту с обновленным дизайном
        fig = go.Figure()

        # Добавляем основную тепловую карту
        fig.add_trace(go.Heatmap(
            z=pivot_data.values,
            x=pivot_data.columns,
            y=pivot_data.index,
            text=pivot_data.values.astype(int),
            texttemplate="%{text}",
            textfont={"size": 20, "family": "Arial", "weight": "bold"},
            colorscale=[
                [0, 'rgb(49, 54, 149)'],     # Темно-синий для минимальных значений
                [0.5, 'rgb(255, 255, 255)'],  # Белый для средних значений
                [1, 'rgb(165, 0, 38)']        # Темно-красный для максимальных значений
            ],
            showscale=True,
            colorbar=dict(
                title="Количество чек-апов",
                titleside="right",
                titlefont=dict(size=14),
                tickfont=dict(size=14)
            )
        ))

        # Вычисляем среднее количество чек-апов в день
        avg_checkups = int(df_filtered['Count_of_chekups'].mean())

        # Обновляем layout с новым дизайном
        fig.update_layout(
            # Добавляем подзаголовок и среднее значение
            annotations=[
                # Заголовок
                dict(
                    text='Среднее кол-во чек-апов в день',
                    xref='paper',
                    yref='paper',
                    x=0.5,
                    y=1.25,  # Поднимаем заголовок еще выше
                    showarrow=False,
                    font=dict(size=20, family='Arial', color='#1f2937'),
                    align='center'
                ),
                # Подзаголовок
                dict(
                    text='Горячая карта по кол-ву медицинских чек-апов<br>(позволяет узнать нагруженные дни)',
                    xref='paper',
                    yref='paper',
                    x=0.5,
                    y=1.2,  # Поднимаем подзаголовок выше
                    showarrow=False,
                    font=dict(size=14, family='Arial', color='#1f2937'),
                    align='center'
                ),
                # Среднее значение
                dict(
                    text=str(avg_checkups),
                    xref='paper',
                    yref='paper',
                    x=0.95,
                    y=1.25,  # Выравниваем с заголовком
                    showarrow=False,
                    font=dict(size=20, family='Arial', color='black'),
                    bgcolor='white',
                    bordercolor='black',
                    borderwidth=1,
                    borderpad=5,
                    align='center'
                )
            ],
            # Общие настройки
            paper_bgcolor='white',
            plot_bgcolor='white',
            margin=dict(t=200, r=100, b=20, l=70),  # Увеличиваем отступ сверху для поднятых элементов
            height=500,
            title=None  # Убираем старый заголовок
        )

        # Добавляем границы ячеек
        fig.update_traces(
            xgap=1,  # Отступ между столбцами
            ygap=1,  # Отступ между строками
        )

        return fig
    except Exception as e:
        print(f"Ошибка в update_heatmap: {e}")
        return go.Figure()

# Функция для получения цвета в зависимости от значения
def get_color_scale(value, vmin, vmax):
    if pd.isna(value):
        return '#f8f9fa'
    
    # Нормализуем значение от 0 до 1
    normalized = (value - vmin) / (vmax - vmin) if vmax > vmin else 0
    
    # Определяем цвета для градиента
    colors = [
        '#313695',  # Темно-синий для минимальных значений
        '#4575b4',  # Синий
        '#fee090',  # Светло-желтый для средних значений
        '#f46d43',  # Оранжевый
        '#a50026'   # Темно-красный для максимальных значений
    ]
    
    # Определяем индекс цвета
    color_index = int(normalized * (len(colors) - 1))
    
    # Возвращаем цвет
    return colors[color_index]

# Callback для статистики по врачам
@app.callback(
    Output('doctors-stats', 'figure'),
    [Input('clinic-filter', 'value'),
     Input('date-filter', 'start_date'),
     Input('date-filter', 'end_date')]
)
def update_doctors_stats(selected_clinics, start_date, end_date):
    try:
        # Загружаем данные
        df_doctors_kids = pd.read_csv("data/Doctor_in_kids_check-ups_daily.csv")
        
        # Преобразуем даты в datetime для корректного сравнения
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        # Создаем списки для хранения данных
        data_frames = []
        
        # Обрабатываем данные по детским врачам
        if 'deFactum_Kids' in selected_clinics:
            # Получаем все даты в выбранном диапазоне
            date_columns = [col for col in df_doctors_kids.columns if col not in ['Doctor', 'Sum']]
            selected_dates = [col for col in date_columns 
                            if start_date <= pd.to_datetime(col, format='%m/%d/%y') <= end_date]
            
            if selected_dates:
                df_kids = df_doctors_kids[['Doctor'] + selected_dates].copy()
                df_kids['Total'] = df_kids[selected_dates].sum(axis=1)
                df_kids = df_kids[df_kids['Doctor'] != 'Total']  # Исключаем строку Total
                df_kids['Clinic'] = 'deFactum_Kids'
                data_frames.append(df_kids[['Doctor', 'Total', 'Clinic']])
        
        # Если нет данных, возвращаем пустой график
        if not data_frames:
            return go.Figure()
        
        # Объединяем данные
        df_combined = pd.concat(data_frames, ignore_index=True)
        
        # Сортируем по количеству чек-апов
        df_combined = df_combined.sort_values('Total', ascending=True)
        
        # Создаем график
        fig = go.Figure()
        
        # Определяем цвета для клиник
        colors = {
            'deFactum_Kids': '#ff7f0e'  # Оранжевый
        }
        
        # Добавляем бары для каждой клиники
        for clinic in selected_clinics:
            if clinic == 'deFactum_Kids':  # Показываем только данные детской клиники
                df_clinic = df_combined[df_combined['Clinic'] == clinic]
                if not df_clinic.empty:
                    # Добавляем горизонтальные бары
                    fig.add_trace(go.Bar(
                        y=df_clinic['Doctor'],
                        x=df_clinic['Total'],
                        name='deFactum Kids',
                        orientation='h',
                        marker_color=colors[clinic]
                    ))
                    
                    # Добавляем текстовые метки в конце каждого бара
                    fig.add_trace(go.Scatter(
                        x=df_clinic['Total'],
                        y=df_clinic['Doctor'],
                        mode='text',
                        text=df_clinic['Total'].astype(int).astype(str),
                        textposition='outside',
                        textfont=dict(
                            size=12,
                            color='black'
                        ),
                        showlegend=False
                    ))
        
        # Обновляем layout
        fig.update_layout(
            barmode='group',
            plot_bgcolor='white',
            paper_bgcolor='white',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=12, family='Arial')
            ),
            height=max(600, len(df_combined['Doctor'].unique()) * 30),  # Увеличиваем высоту
            margin=dict(l=20, r=150, t=50, b=20),  # Увеличиваем правый отступ для значений
            xaxis=dict(
                title="Количество чек-апов",
                showgrid=True,
                gridcolor='lightgray',
                showline=True,
                linewidth=1,
                linecolor='black',
                tickfont=dict(size=12, family='Arial')
            ),
            yaxis=dict(
                title="",
                showgrid=True,
                gridcolor='lightgray',
                showline=True,
                linewidth=1,
                linecolor='black',
                tickfont=dict(size=12, family='Arial')
            )
        )
        
        return fig
    except Exception as e:
        print(f"Ошибка в update_doctors_stats: {e}")
        return go.Figure()

# Callback для сравнения периодов
@app.callback(
    Output('period-comparison', 'figure'),
    [Input('clinic-filter', 'value'),
     Input('date-filter', 'start_date'),
     Input('date-filter', 'end_date')]
)
def update_period_comparison(selected_clinics, start_date, end_date):
    try:
        # Получаем текущую дату
        today = datetime.now().date()
        
        # Получаем даты для прошлой и позапрошлой недель
        current_week_start, current_week_end = get_week_dates(today)
        last_week_start = current_week_start - timedelta(days=7)
        last_week_end = current_week_end - timedelta(days=7)
        prev_week_start = last_week_start - timedelta(days=7)
        prev_week_end = last_week_end - timedelta(days=7)
        
        # Фильтруем данные
        df_filtered = df_main[df_main["Name_of_clinic"].isin(selected_clinics)]
        
        # Получаем данные по неделям
        last_week_data = df_filtered[
            (df_filtered["Date"].dt.date >= last_week_start) & 
            (df_filtered["Date"].dt.date <= last_week_end)
        ].groupby(["Name_of_clinic", "Day_of_the_week"])["Count_of_chekups"].sum().reset_index()
        
        prev_week_data = df_filtered[
            (df_filtered["Date"].dt.date >= prev_week_start) & 
            (df_filtered["Date"].dt.date <= prev_week_end)
        ].groupby(["Name_of_clinic", "Day_of_the_week"])["Count_of_chekups"].sum().reset_index()
        
        # Добавляем метку периода
        last_week_data['Period'] = 'Прошлая неделя'
        prev_week_data['Period'] = 'Позапрошлая неделя'
        
        # Объединяем данные
        df_comparison = pd.concat([last_week_data, prev_week_data])
        
        # Определяем порядок дней недели
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        # Создаем график
        fig = px.bar(
            df_comparison,
            x="Day_of_the_week",
            y="Count_of_chekups",
            color="Period",
            barmode="group",
            facet_row="Name_of_clinic",
            category_orders={"Day_of_the_week": days_order},
            title="Сравнение количества чек-апов по неделям",
            labels={
                "Day_of_the_week": "День недели",
                "Count_of_chekups": "Количество чек-апов",
                "Name_of_clinic": "Клиника"
            }
        )
        
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            title_x=0.5,
            title_font_size=16,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        fig.update_xaxes(
            gridcolor='lightgray',
            showline=True,
            linewidth=1,
            linecolor='black'
        )
        
        fig.update_yaxes(
            gridcolor='lightgray',
            showline=True,
            linewidth=1,
            linecolor='black'
        )
        
        return fig
    except Exception as e:
        print(f"Ошибка в update_period_comparison: {e}")
        return go.Figure()

# Callback для дополнительной аналитики (лучевая диаграмма)
@app.callback(
    Output('additional-analytics', 'figure'),
    [Input('clinic-filter', 'value'),
     Input('date-filter', 'start_date'),
     Input('date-filter', 'end_date')]
)
def update_additional_analytics(selected_clinics, start_date, end_date):
    try:
        # Преобразуем даты
        start_date = pd.to_datetime(start_date).strftime('%m/%d/%y')
        end_date = pd.to_datetime(end_date).strftime('%m/%d/%y')
        
        # Получаем даты в выбранном диапазоне
        date_columns = [col for col in df_doctors_adult.columns if col != 'Doctor']
        selected_dates = [col for col in date_columns if start_date <= col <= end_date]
        
        # Обрабатываем данные по взрослым
        df_adult_metrics = df_doctors_adult[['Doctor'] + selected_dates].copy()
        df_adult_metrics['Total'] = df_adult_metrics[selected_dates].sum(axis=1)
        df_adult_metrics['Average'] = df_adult_metrics[selected_dates].mean(axis=1)
        df_adult_metrics['Max'] = df_adult_metrics[selected_dates].max(axis=1)
        df_adult_metrics['Type'] = 'Adult'
        
        # Обрабатываем данные по детям
        df_kids_metrics = df_doctors_kids[['Doctor'] + selected_dates].copy()
        df_kids_metrics['Total'] = df_kids_metrics[selected_dates].sum(axis=1)
        df_kids_metrics['Average'] = df_kids_metrics[selected_dates].mean(axis=1)
        df_kids_metrics['Max'] = df_kids_metrics[selected_dates].max(axis=1)
        df_kids_metrics['Type'] = 'Kids'
        
        # Создаем лучевую диаграмму
        fig = go.Figure()
        
        # Метрики для лучевой диаграммы
        metrics = ['Total', 'Average', 'Max']
        
        # Добавляем данные для взрослых
        adult_values = df_adult_metrics[metrics].mean().values.tolist()
        adult_values.append(adult_values[0])  # Замыкаем график
        
        fig.add_trace(go.Scatterpolar(
            r=adult_values,
            theta=metrics + [metrics[0]],
            fill='toself',
            name='Adult Checkups',
            line_color='rgb(31, 119, 180)'
        ))
        
        # Добавляем данные для детей
        kids_values = df_kids_metrics[metrics].mean().values.tolist()
        kids_values.append(kids_values[0])  # Замыкаем график
        
        fig.add_trace(go.Scatterpolar(
            r=kids_values,
            theta=metrics + [metrics[0]],
            fill='toself',
            name='Kids Checkups',
            line_color='rgb(255, 127, 14)'
        ))
        
        # Обновляем layout
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max(max(adult_values), max(kids_values))]
                )
            ),
            title={
                'text': 'Сравнение метрик взрослых и детских чек-апов',
                'x': 0.5,
                'font_size': 16
            },
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    except Exception as e:
        print(f"Ошибка в update_additional_analytics: {e}")
        return go.Figure()

if __name__ == '__main__':
    app.run_server(debug=True)
