#!/usr/bin/env python
# coding: utf-8

# In[1]:


from dash import Dash, html, dcc, Input, Output, State
import plotly.express as px
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json
import requests

# Cargar los datos
matricula = pd.read_csv("https://raw.githubusercontent.com/paulamielgo/Univaciada_data/refs/heads/main/matricula.csv")
matricula["scaled_count"]= 0.1
# Calcular el máximo global de estudiantes en el conjunto de datos
global_max_count = matricula['count'].max()
available_courses = ['2017-18', '2018-19', '2019-20', '2020-21', '2021-22', '2022-23']
density_categories = matricula['poblacion'].unique()
# Crear el slider con índices para los cursos
course_marks = {i: course for i, course in enumerate(available_courses)}
current_center = dict(lat=40.4168, lon=-3.7038)

#CREAMOS MAPA pestaña 1
# Función para crear el mapa
def create_figure(selected_university, selected_courses, selected_densities, current_zoom, current_center):
    filtered_data = matricula[(matricula['universidad'] == selected_university) &
                              (matricula['curso_academico'].isin(selected_courses)) &
                              (matricula['poblacion'].isin(selected_densities))]

    fig = px.scatter_mapbox(
        filtered_data,
        lat="lat_municipio_residencia",
        lon="lon_municipio_residencia",
        color="log_count",
        size_max=20,
        opacity=0.8,
        color_continuous_scale=px.colors.sequential.Bluered,
        hover_name="municipio",
        hover_data={"count": True},
    )

    global_min_log = np.log(1)
    global_max_log = np.log(global_max_count)
    tick_vals = np.linspace(global_min_log, global_max_log, num=5)
    tick_texts = [str(int(round(np.exp(v)))) for v in tick_vals]

    fig.update_layout(
        coloraxis_colorbar=dict(
            title="Estudiantes\n",
            tickvals=tick_vals,
            ticktext=tick_texts,
        ),
        coloraxis=dict(
            cmin=global_min_log,
            cmax=global_max_log
        ),
        mapbox_style="carto-positron",
        autosize=True,
        showlegend=False,
        mapbox=dict(
            center=current_center,
            zoom=current_zoom
        )
    )

    points_size = 15
    fig.update_traces(marker={'size': points_size})
    return fig


#CREAMOS DIAGRAMA DE SECTORES pestaña 1
def create_pie_chart(selected_university, selected_course):
    # Filtrar los datos según la universidad y curso seleccionados
    filtered_data = matricula[(matricula['universidad'] == selected_university) &
                              (matricula['curso_academico'] == selected_course)]
    
    # Agrupar los datos por población y sumar los valores de la columna 'count'
    pie_data = filtered_data.groupby('poblacion', as_index=False)['count'].sum()
    
    # Definir el orden fijo de los grupos
    population_order = ['Muy densa', 'Densa', 'Moderadamente densa', 'Poco densa', 'Muy poco densa']
    
    # Asegurar que los datos sigan este orden
    pie_data['poblacion'] = pd.Categorical(pie_data['poblacion'], categories=population_order, ordered=True)
    pie_data = pie_data.sort_values('poblacion')  # Ordenar explícitamente
    
    # Definir una paleta de colores fija
    color_palette = {
        'Muy densa': '#1f77b4',
        'Densa': '#ff7f0e',
        'Moderadamente densa': '#2ca02c',
        'Poco densa': '#9467bd',
        'Muy poco densa': '#d62728'  # Ajusta los colores y los nombres de los grupos según tu dataset
    }
    
    # Crear el gráfico de pastel con colores fijos y orden predefinido
    pie_chart = px.pie(
        pie_data,
        values='count',  # Usar los valores sumados
        names='poblacion',
        title=f"Distribución de población en la {selected_university.upper()} curso {selected_course}",
        color='poblacion',  # Vincular colores al grupo de población
        color_discrete_map=color_palette,  # Asignar colores fijos
        category_orders={'poblacion': population_order}  # Definir el orden fijo
    )
    
    # Ajustar el diseño del gráfico
    pie_chart.update_layout(
        autosize=True,
        title={
            'text': f"Distribución de población en la {selected_university.upper()} curso {selected_course}",
            'y': 0.99,  # Ajusta la posición vertical
            'x': 0.00,  # Alineación a la izquierda
            'xanchor': 'left',
            'yanchor': 'top',
            'font': {
                'family': 'Arial, sans-serif',
                'size': 18,  # Tamaño de fuente en píxeles
                'color': '#333',  # Color del texto
                'weight': 'bold'
            }
        }
    )
    
    return pie_chart


#MAPA COMUNIDADES pestaña 2
# Carga el archivo GeoJSON
geojson_url = "https://raw.githubusercontent.com/ufoe/d3js-geojson/refs/heads/master/Spain.json"
response = requests.get(geojson_url)
geojson_data = response.json()

# Filtra las comunidades autónomas (puede que necesites ajustar esta parte según los datos)
comunidades_geojson = {
    "type": "FeatureCollection",
    "features": [
        feature for feature in geojson_data["features"]
        if feature["properties"].get("type_en") == "Autonomous Community"
    ]
}

# Crear lista de comunidades autónomas
comunidades = [feature["properties"]["name"] for feature in comunidades_geojson["features"]]





# Crear la aplicación Dash
app = Dash(__name__)
#CAMBIAR A ESTA
#app = Dash(__name__, suppress_callback_exceptions=True)

#PESTAÑAS
#PM este heigth es el de la pestaña izquierda (porque solo es una)
app.layout = html.Div(style={'display': 'flex', 'flexDirection': 'column', 'height': '97vh'}, children=[
    dcc.Tabs(id='tabs', value='tab1', style={'height': '10%'}, children=[
        dcc.Tab(label='Pestaña 1', value='tab1'),
        dcc.Tab(label='Pestaña 2', value='tab2'),
        dcc.Tab(label='Pestaña 3', value='tab3'),
    ]),
    html.Div(id='content', style={'flex': '1', 'display': 'flex', 'height': '90%'}),
    #Añadido
    dcc.Store(id='store-zoom', data={'zoom': 5.4, 'center': dict(lat=40.0168, lon=-3.0038)})
])


@app.callback(
    Output('content', 'children'),
    [Input('tabs', 'value')]
)
def update_content(tab):
    print("Entra a actualizar el contenido, valor de tab es ")
    print(tab)
    #PESTAÑA 1
    if tab == 'tab1':
        return [
            #MAPA ESPAÑA
            html.Div(style={'flex': '1', 'border': '1px solid #ccc', 'borderRadius': '10px', 'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)', 'padding': '5px', 'width': '90%', 'display': 'flex', 'flexDirection': 'column'}, children=[
                html.Div(style={'padding': '10px'}, children=[
                    html.H3("Municipio de origen de los estudiantes", style={'margin': '0','textAlign': 'left','color': '#333','font-family': 'Arial, sans-serif','font-size': '1.5rem','font-weight': 'bold','padding-bottom': '10px'  
            }),
                     html.P("Selecciona la Universidad y el curso académico deseado en las ventanas situadas a la derecha.", style={}),
                     html.P("También puedes filtrar por densidad poblacional: ", style={}),
                    
                    dcc.Checklist(
                        id='density-checkbox',
                        options=[{'label': density, 'value': density} for density in density_categories],
                        value=list(density_categories),
                        labelStyle={'display': 'inline-block', 'fontSize': '14px', 'marginBottom': '10px','marginRight': '50px'},
                        inline=True,
                        style={'padding': '10px'}
                    ),
                ]),
                dcc.Graph(
                    id='map',
                    figure=create_figure('uc3m', ['2017-18'], density_categories,5.4,dict(lat=40.0168, lon=-3.0038)),
                    config={'scrollZoom': True},
                    style={'height': '100%', 'width': '100%','flexGrow': 1}
                ),
                dcc.Store(id='store-zoom', data={'zoom': 5.4, 'center': dict(lat=40.0168, lon=-3.0038)}),
            ]),
            #FILTROS
           html.Div(style={'flex': '1', 'display': 'flex', 'flexDirection': 'column', 'padding': '0px', 'gap': '10px',  'marginLeft': '10px','marginRight': '10px'}, children=[
               #UNIVERSIDAD
                html.Div(
                    style={
                        'flex': '1',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'padding': '10px',
                        'gap': '20px',
                        'border': '1px solid #ccc',
                        'borderRadius': '10px',
                        'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)'
                    },
                    children=[
                        # UNIVERSIDAD
                        html.Div(
                            style={'marginBottom': '20px'},
                            children=[
                                html.H3("Selecciona Universidad", style={'margin': '0','textAlign': 'left','color': '#333','font-family': 'Arial, sans-serif','font-size': '1.1rem','padding-bottom': '10px'}),
                                dcc.RadioItems(
                                    id='university-radio',
                                    options=[
                                        {'label': 'UC3M', 'value': 'uc3m'},
                                        {'label': 'UVA', 'value': 'uva'},
                                        {'label': 'UAM', 'value': 'uam'},
                                        {'label': 'UCM', 'value': 'ucm'},
                                        {'label': 'URJC', 'value': 'urjc'}
                                    ],
                                    value='uc3m',
                                    labelStyle={'display': 'inline-block', 'fontSize': '14px', 'marginBottom': '10px','marginRight': '50px'},
                                    style={'padding': '10px'}
                                ),
                            ]
                        ),
                        # CURSO ACADÉMICO
                        html.Div(
                            children=[
                                html.H3("Selecciona Curso Académico", style={'margin': '0','textAlign': 'left','color': '#333','font-family': 'Arial, sans-serif','font-size': '1.1rem','padding-bottom': '20px'}),
                                dcc.Slider(
                                    id='course-slider',
                                    min=0,
                                    max=len(available_courses) - 1,
                                    step=1,
                                    marks=course_marks,
                                    included=False,
                                    value=0
                                ),
                            ])
                        ]),        
               
                html.Div(style={'flex': '1', 'border': '1px solid #ccc', 'borderRadius': '10px', 'padding': '10px', 'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)'}, children=[
                    html.H3("Ventana Superior", style={'margin': '0','textAlign': 'left','color': '#333','font-family': 'Arial, sans-serif','font-size': '1.1rem','padding-bottom': '20px'}),
                    html.P("Contenido de la ventana superior", style={'padding': '10px'}),
                    html.P("Contenido de la ventana superior", style={'padding': '10px'}),
                    html.P("Contenido de la ventana superior", style={'padding': '10px'}),
                ]),
                html.Div(style={'flex': '1', 'border': '1px solid #ccc', 'borderRadius': '10px', 'padding': '10px', 'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)'}, children=[
                    #html.H3("Ventana Inferior", style={'margin': '0', 'textAlign': 'center', 'color': '#333'}),
                     dcc.Graph(
                        id='pie-chart',
                        style={
                            'display': 'flex',
                            'justify-content': 'flex-start',
                            'align-items': 'flex-start',
                            #'height': '100vh'  # Esto asegura que el gráfico ocupe toda la altura de la pantalla
                        }
)
                ])
            ])
        ]
    elif tab == 'tab2':
            return [
            #MAPA ESPAÑA
            html.Div(style={'flex': '1', 'border': '1px solid #ccc', 'borderRadius': '10px', 'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)', 'padding': '5px', 'width': '90%', 'display': 'flex', 'flexDirection': 'column'}, children=[
                html.Div(style={'padding': '10px'}, children=[
                    html.H3("Mapa Interactivo de España por Provincias", style={'margin': '0','textAlign': 'left','color': '#333','font-family': 'Arial, sans-serif','font-size': '1.5rem','font-weight': 'bold','padding-bottom': '10px'  
            }),
                     
                ]),
                dcc.Loading(
                         id="loading-mapa",
                         type="circle",
                         children=[
                             dcc.Graph(id="mapa", config={'scrollZoom': True}, 
                                       style={'height': '100%', 'width': '100%', 'flexGrow': 1}),
                         ]
                     ),
                html.Div([
                    html.H3("Provincia seleccionada:"),
                    html.Div(id="comunidad-seleccionada", style={"fontSize": "20px", "fontWeight": "bold"})
                ])
               
            ]),
            #FILTROS
           html.Div(style={'flex': '1', 'display': 'flex', 'flexDirection': 'column', 'padding': '0px', 'gap': '10px',  'marginLeft': '10px','marginRight': '10px'}, children=[
               #UNIVERSIDAD
                html.Div(
                    style={
                        'flex': '1',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'padding': '10px',
                        'gap': '20px',
                        'border': '1px solid #ccc',
                        'borderRadius': '10px',
                        'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)'
                    },
                    children=[
                        # UNIVERSIDAD
                        html.Div(
                            style={'marginBottom': '20px'},
                            children=[
                                html.H3("Selecciona Universidad", style={'margin': '0','textAlign': 'left','color': '#333','font-family': 'Arial, sans-serif','font-size': '1.1rem','padding-bottom': '10px'}),
                        
                            ]
                        ),
                       
                        
                        ]),        
               
                html.Div(style={'flex': '1', 'border': '1px solid #ccc', 'borderRadius': '10px', 'padding': '10px', 'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)'}, children=[
                    html.H3("Ventana Superior", style={'margin': '0','textAlign': 'left','color': '#333','font-family': 'Arial, sans-serif','font-size': '1.1rem','padding-bottom': '20px'}),
                    html.P("Contenido de la ventana superior", style={'padding': '10px'}),
                    html.P("Contenido de la ventana superior", style={'padding': '10px'}),
                    html.P("Contenido de la ventana superior", style={'padding': '10px'}),
                ]),
                html.Div(style={'flex': '1', 'border': '1px solid #ccc', 'borderRadius': '10px', 'padding': '10px', 'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)'}, children=[
                    #html.H3("Ventana Inferior", style={'margin': '0', 'textAlign': 'center', 'color': '#333'}),
                     
                ])
            ])
        ]
          
        
#ZOOM de la pestaña 1
@app.callback(
    Output('store-zoom', 'data'),
    [Input('map', 'relayoutData')],
    [State('store-zoom', 'data')]
)
def update_zoom(relayout_data, current_data):
    if relayout_data and 'mapbox.zoom' in relayout_data:
        current_data['zoom'] = relayout_data['mapbox.zoom']
    if relayout_data and 'mapbox.center' in relayout_data:
        current_data['center'] = relayout_data['mapbox.center']
    return current_data

#MAPA de la pestaña 1
@app.callback(
    Output('map', 'figure'),
    [Input('university-radio', 'value'),
     Input('course-slider', 'value'),
     Input('density-checkbox', 'value')],
    [State('store-zoom', 'data')]
)
def update_map(selected_university, selected_course_index, selected_densities, zoom_data):
    current_zoom = zoom_data['zoom']
    current_center = zoom_data['center']
    selected_course = [available_courses[selected_course_index]]
    return create_figure(selected_university, selected_course, selected_densities, current_zoom, current_center)

#Gráfico de sectores de la pestaña 1
@app.callback(
    Output('pie-chart', 'figure'),
    [Input('university-radio', 'value'),
     Input('course-slider', 'value')]
)
def update_pie_chart(selected_university, selected_course_index):
    selected_course = available_courses[selected_course_index]
    print("actualiza")
    return create_pie_chart(selected_university, selected_course)

# Mapa pestaña 2 con indicador de carga
@app.callback(
    Output("mapa", "figure"),
    Output("comunidad-seleccionada", "children"),
    Input("mapa", "clickData")
)
def actualizar_mapa(click_data):
    # Comunidad seleccionada
    comunidad_seleccionada = click_data["points"][0]["location"] if click_data else None

    # Crear el mapa
    figC = px.choropleth_mapbox(
        geojson=comunidades_geojson,
        locations=[feature["properties"]["name"] for feature in comunidades_geojson["features"]],
        featureidkey="properties.name",
        color_discrete_sequence=["cyan"],  # Cambiar a azul
        mapbox_style="carto-positron",
        center={"lat": 40.4168, "lon": -3.7038},  # Centro de España
        zoom=4.5,
        opacity=0.8  # Ajustar la opacidad
    )
    
    # Actualizar el layout del mapa y eliminar texto adicional en hover
    figC.update_traces(
        hovertemplate="<b>Provincia:</b> %{location}<extra></extra>"
    )
    
    figC.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        clickmode="event+select",
        showlegend=False
    )

    return figC, comunidad_seleccionada or "Selecciona una comunidad autónoma"



if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=8050)

