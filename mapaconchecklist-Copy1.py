#!/usr/bin/env python
# coding: utf-8

# In[7]:


from dash import Dash, html, dcc, Input, Output, State
import plotly.express as px
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json
import requests
from dash import dash_table
import dash_bootstrap_components as dbc

# Cargar los datos
#MATRICULA
matricula = pd.read_csv("https://raw.githubusercontent.com/paulamielgo/Univaciada_data/refs/heads/main/matricula.csv")
matricula["scaled_count"]= 0.1
# Calcular el máximo global de estudiantes en el conjunto de datos
global_max_count = matricula['count'].max()
available_courses = ['2017-18', '2018-19', '2019-20', '2020-21', '2021-22', '2022-23']
available_courses2 = ['2017-18', '2018-19', '2019-20', '2020-21', '2021-22', '2022-23', '2023-24']
density_categories = matricula['poblacion'].unique()
# Crear el slider con índices para los cursos
#course_marks = {i: course for i, course in enumerate(available_courses)}
course_marks = {
    i: {'label': course, 'style': {'color': 'black',"fontFamily": "Arial, sans-serif"}}
    for i, course in enumerate(available_courses)
}
course_marks2 = {
    i: {'label': course, 'style': {'color': 'black',"fontFamily": "Arial, sans-serif"}}
    for i, course in enumerate(available_courses2)
}
#course_marks2 = {i: course for i, course in enumerate(available_courses2)}
current_center = dict(lat=40.4168, lon=-3.7038)


#ACCESO
medias = pd.read_csv("https://raw.githubusercontent.com/paulamielgo/Univaciada_data/refs/heads/main/medias.csv")
notas = pd.read_csv("https://raw.githubusercontent.com/paulamielgo/Univaciada_data/refs/heads/main/notas.csv")
top5_df = pd.read_csv("https://raw.githubusercontent.com/paulamielgo/Univaciada_data/refs/heads/main/top5.csv")
matriculasG2 = pd.read_csv("https://raw.githubusercontent.com/paulamielgo/Univaciada_data/refs/heads/main/matriculaG2.csv")


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
    global_max_log = np.log(26000)
    tick_vals = np.linspace(global_min_log, global_max_log, num=10)
    tick_texts = [str(int(round(np.exp(v)))) for v in tick_vals]

    fig.update_layout(
        coloraxis_colorbar=dict(
            title="Estudiantes",
            tickvals=tick_vals,
            ticktext=tick_texts,
            tickangle=0
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
        ),
        margin=dict(l=15, r=0, t=0, b=15)
    )

    points_size = 15
    fig.update_traces(
        marker={'size': points_size},
        hovertemplate=(
            "<b>%{hovertext} </b><br>" +
            "Matriculados: %{customdata[0]}<extra></extra>"
        )
    )
    #fig.update_traces(marker={'size': points_size})
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
            'text': f"Universidad {selected_university.upper()}, curso {selected_course}",
            'y': 0.3,  # Posición vertical del título
            'x': 1.0,  # Posición horizontal del título (a la derecha)
            'xanchor': 'right',  # Anclar el título a la derecha
            'yanchor': 'middle',
            'font': {
                'family': 'Arial, sans-serif',
                'size': 16,  # Tamaño de fuente
                'color': 'black',
            }
        },
        margin={
            'l': 10,  # Margen izquierdo
            'r': 10,  # Margen derecho
            't': 10,  # Margen superior
            'b': 10   # Margen inferior
        }
    )
    pie_chart.update_traces(
        hovertemplate=(
            "<b>%{label} </b><br>" +
            "Matriculados: %{value}<extra></extra>"
        )
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
        #if feature["properties"].get("type_en") == "Autonomous Community"
        if feature["properties"].get("type_en") in ["Autonomous Community", "Autonomous City"]
    ]
}

# Crear lista de comunidades autónomas
comunidades = [feature["properties"]["name"] for feature in comunidades_geojson["features"]]
print("Cargando provincias y ciudades autónomas")
print(comunidades)

#Crear mapa 2
def crear_mapa(comunidades_geojson, customdata=None):
    figC = px.choropleth_mapbox(
        geojson=comunidades_geojson,
        locations=[feature["properties"]["name"] for feature in comunidades_geojson["features"]],
        featureidkey="properties.name",
        color_discrete_sequence=["cyan"],  # Cambiar a azul
        mapbox_style="carto-positron",
        center={"lat": 40.4168, "lon": -3.7038},  # Centro de España
        zoom=5.0,
        opacity=0.8  # Ajustar la opacidad
    )

    # Si hay customdata, asignarlo al mapa
    if customdata:
        figC.data[0].customdata = customdata

    # Actualizar el layout del mapa
    figC.update_traces(
        hovertemplate=(
            "<b>%{location}</b><br>" +
            "Nota media: %{customdata:.2f}<extra></extra>"
        )
    )
    figC.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        clickmode="event+select",
        showlegend=False
    )

    return figC


#Crear caja y bigote
#Crear caja y bigote
def create_caja(selected_course, df):
    import plotly.graph_objects as go
    import pandas as pd

    # Definir el orden deseado de las categorías
    category_order = ["Muy poco densa", "Poco densa", "Moderadamente densa", "Densa", "Muy densa"]
    
    # Ordenar el DataFrame en función de este orden
    df["poblacion"] = pd.Categorical(df["poblacion"], categories=category_order, ordered=True)
    df = df.sort_values("poblacion")
    
    # Crear la figura
    fig = go.Figure()
    leyenda_usada = set()  # Para rastrear qué elementos ya han aparecido en la leyenda
    
    # Añadir las cajas, una por categoría y provincia
    for provincia, group in df.groupby("des_provincia_centro_sec"):
        
        color = "blue" if provincia == "Global" else "red"
        
        # Filtrar los datos donde haya valores NaN
        group_clean = group.dropna(subset=["percentil_25", "percentil_50", "percentil_75", "nota_minima", "nota_maxima"])
        group_nan = group[group[["percentil_25", "percentil_50", "percentil_75", "nota_minima", "nota_maxima"]].isna().any(axis=1)]
        
        # Añadir trazo para los registros limpios
        fig.add_trace(go.Box(
            name=provincia,  # Nombre en la leyenda
            x=group_clean["poblacion"],  # Categorías del eje X
            q1=group_clean["percentil_25"], 
            median=group_clean["percentil_50"], 
            q3=group_clean["percentil_75"], 
            lowerfence=group_clean["nota_minima"], 
            upperfence=group_clean["nota_maxima"], 
            boxpoints=False,
            marker_color=color,
            legendgroup=provincia,  # Agrupar por provincia
            showlegend=provincia not in leyenda_usada,  # Mostrar solo la primera vez
            #customdata=group_clean[["nota_maxima", "percentil_50"]],  # Añadir datos personalizados
            #hovertemplate="Máximo: %{customdata[0]}<br>Mediana: %{customdata[1]}<extra></extra>",  # Personalizar el hover

        ))
        
        # Añadir trazo para los registros con NaN, pintados de blanco
        #if not group_nan.empty:
        #    fig.add_trace(go.Box(
        #        name=f"Sin valores",  # Nombre diferente para los NaN
        #        x=group_nan["poblacion"],  # Categorías del eje X
        #        q1=group_nan["percentil_25"], 
        #        median=group_nan["percentil_50"], 
        #        q3=group_nan["percentil_75"], 
        #        lowerfence=group_nan["nota_minima"], 
        #        upperfence=group_nan["nota_maxima"], 
        #        boxpoints=False,
        #        marker_color="rgba(255, 255, 255, 0)",  #Transparente, así guarda el hueco
        #        legendgroup=provincia,  # Agrupar por provincia
        #        showlegend=provincia not in leyenda_usada,  # Mostrar solo la primera vez
        #    ))

        leyenda_usada.add(provincia)

    # Ajustar el diseño
    if(provincia!="Global"):
        fig.update_layout(
            title=f"Curso {selected_course} en {provincia}")
    else:
        fig.update_layout(
            title=f"Curso {selected_course}")
    fig.update_layout(
        #title=f"Diagrama de caja para {selected_course} y {provincia}",
        yaxis_title="Nota de acceso",
        xaxis=dict(
            #title="Categorías",
            tickmode="array",
            tickvals=category_order,
        ),
        boxmode="group",  # Agrupación horizontal de las cajas
        plot_bgcolor="white",
        yaxis=dict(
            gridcolor="lightgrey",
            zerolinecolor="grey",
            zerolinewidth=1,
            range=[0, 14]
        ),
        margin=dict(l=40, r=40, t=40, b=40),
    )
    
    return fig

#Tabla top 5
def create_top_5_table(top_5_df):
    data=top_5_df.to_dict('records')
    print("Data")
    print(data)
    return dash_table.DataTable(
        columns=[
            {"name": "Orden", "id": "orden"},
            {"name": "Titulación", "id": "des_titulacion"},
            {"name": "Matriculados", "id": "count"}
        ],
        data=top_5_df.to_dict('records'),
        style_table={
            "overflowX": "auto", 
            "margin": "20px", 
            "width": "95%",  # Para hacer que la tabla ocupe todo el espacio disponible en su contenedor
            "borderLeft": "1px solid #ccc",  # Borde izquierdo
            "borderRight": "1px solid #ccc"  # Borde derecho
        },
        style_cell={
            "textAlign": "center", 
            "padding": "5px", 
            "fontFamily": "Arial, sans-serif"
        },
        style_header={
            "fontWeight": "bold", 
            "backgroundColor": "#f4f4f4", 
            "textAlign": "center"
        },
    )


# Crear la aplicación Dash
app = Dash(__name__)
#CAMBIAR A ESTA
#app = Dash(__name__, suppress_callback_exceptions=True)

#PESTAÑAS
#PM este height es el de la pestaña izquierda (porque solo es una)
app.layout = html.Div(style={'display': 'flex', 'flexDirection': 'column', 'height': '97vh'}, children=[
    dcc.Tabs(id='tabs', value='tab1', style={'height': '10%'}, children=[
        dcc.Tab(label='Pestaña 1', value='tab1'),
        dcc.Tab(label='Pestaña 2', value='tab2'),
        dcc.Tab(label='Pestaña 3', value='tab3'),
    ]),
    html.Div(id='content', style={'flex': '1', 'display': 'flex', 'height': '90%'}),
    #Añadido
    dcc.Store(id='store-zoom', data={'zoom': 5.0, 'center': dict(lat=40.0168, lon=-3.0038)})
])


@app.callback(
    Output('content', 'children'),
    [Input('tabs', 'value')]
)
def update_content(tab):
    #PESTAÑA 1
    if tab == 'tab1':
        return [
            #MAPA ESPAÑA
            html.Div(style={'flex': '1', 'border': '1px solid #ccc', 'borderRadius': '10px', 'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)', 'padding': '5px', 'width': '90%', 'display': 'flex', 'flexDirection': 'column','height': '90vh'}, children=[
                html.Div(style={'padding': '10px'}, children=[
                    html.H3("Municipio de origen de los estudiantes", style={'margin': '0','textAlign': 'left','color': '#333','font-family': 'Arial, sans-serif','font-size': '1.5rem','font-weight': 'bold','padding-bottom': '10px'}),
                    html.P("Selecciona la Universidad y el curso académico deseado en las ventanas situadas a la derecha.", style={'font-family': 'Arial, sans-serif','font-size': '1.2rem'}),
                    html.Div([
                        html.P("También puedes filtrar el mapa por densidad poblacional. ", style={'font-family': 'Arial, sans-serif','font-size': '1.2rem'}),
                        html.Button('?', id='btn', style={'backgroundColor': '#009ad5','color': 'black','borderRadius': '50%','width': '25px','height': '25px','border': '2px solid black','fontSize': '14px','font-weight': 'bold','cursor': 'pointer','textAlign': 'center','lineHeight': '15px','marginLeft': '10px'}),          
                        dbc.Tooltip(html.Div([
                            html.P("Muy poco densa 1-5.000 habitantes", style={'marginLeft': '65px','marginTop': '0px','marginBottom': '0px'}),
                            html.P("Poco densa 5.001-25.000 habitantes", style={'marginLeft': '70px','marginTop': '0px','marginBottom': '0px'}),
                            html.P("Moderadamente densa 25.001-100.000 habitantes", style={'marginLeft': '0px','marginTop': '0px','marginBottom': '0px'}),
                            html.P("Densa 100.001-500.000 habitantes", style={'marginLeft': '85px','marginTop': '0px','marginBottom': '0px'}),
                            html.P("Muy densa +500.001 habitantes", style={'marginLeft': '103px','marginTop': '0px','marginBottom': '0px'})
                        ]),target="btn",style={'backgroundColor': '#333','color': 'white','borderRadius': '5px','fontSize': '14px','padding': '5px 10px','boxShadow': '0 4px 6px rgba(0, 0, 0, 0.2)'}),
                   ], style={'display': 'flex', 'alignItems': 'center'}),
                    dcc.Checklist(
                        id='density-checkbox',
                        options=[{'label': density, 'value': density} for density in density_categories],
                        value=list(density_categories),
                        labelStyle={'display': 'inline-block', 'font-family': 'Arial, sans-serif','font-size': '1.2rem', 'marginBottom': '10px','marginRight': '20px'},
                        inline=True,
                        style={'padding': '10px'}
                    ),
                    html.P("Municipio de origen de estudiantes por universidad, curso y densidad poblacional seleccionada: ", style={'font-family': 'Arial, sans-serif','font-size': '1.2rem'}),
                    
                ]),      
                dcc.Graph(
                    id='map',
                    figure=create_figure('uc3m', ['2017-18'], density_categories,5.4,dict(lat=40.0168, lon=-3.0038)),
                    config={'scrollZoom': True},
                    style={'height': '100%', 'width': '100%','flexGrow': 1}
                ),
                dcc.Store(id='store-zoom', data={'zoom': 5.0, 'center': dict(lat=40.0168, lon=-3.0038)}),
            ]),
            #FILTROS
           html.Div(style={'flex': '1', 'display': 'flex', 'flexDirection': 'column', 'padding': '0px', 'gap': '10px',  'marginLeft': '10px','marginRight': '10px','height': '91vh'}, children=[
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
                            style={'marginBottom': '0px'},
                            children=[
                                html.H3("Filtros para las figuras", style={'margin': '0','textAlign': 'left','color': '#333','font-family': 'Arial, sans-serif','font-size': '1.1rem','padding-bottom': '0px'}),
                                html.P("Selecciona la Universidad.", style={'font-family': 'Arial, sans-serif','font-size': '1.2rem'}),
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
                                    labelStyle={'display': 'inline-block', 'font-family': 'Arial, sans-serif','font-size': '1.0rem', 'marginBottom': '0px','marginRight': '50px'},
                                    style={'padding': '0px'}
                                ),
                            ]
                        ),
                        # CURSO ACADÉMICO
                        html.Div(
                            children=[
                                html.P("Selecciona el curso académico.", style={'font-family': 'Arial, sans-serif','font-size': '1.2rem','marginTop':'0px'}),
                                html.Div(
                                    children=[
                                        dcc.Slider(
                                            id='course-slider',
                                            min=0,
                                            max=len(available_courses) - 1,
                                            step=1,
                                            marks=course_marks,
                                            included=False,
                                            value=0
                                        )
                                    ],
                                    style={'width': '95%', 'margin': '0','white-space': 'nowrap', 'padding':'0px'}  # Contenedor con el 80% del ancho de la ventana
                                ),
                                
                            ],style={'marginBottom': '0px'})
                        ]),        
               
                html.Div(style={'flex': '1', 'border': '1px solid #ccc', 'borderRadius': '10px', 'padding': '10px', 'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)'}, children=[
                    html.H3("Estudiantes por grupo poblacional", style={'margin': '0','textAlign': 'left','color': '#333','font-family': 'Arial, sans-serif','font-size': '1.1rem','padding-bottom': '0px','marginBottom': '0px'}),
                    dcc.Loading(
                         id="loading-mapa",
                         type="circle",
                         children=[dcc.Graph(id="line-graph",style={'height': '28vh','marginTop':'0px'})])
                ]),
                html.Div(style={'height': '33vh', 'overflow': 'hidden' , 'flex': '1', 'border': '1px solid #ccc', 'borderRadius': '10px', 'padding': '10px', 'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)'}, children=[
                    html.H3("Distribución de estudiantes por universidad y curso", style={'margin': '0','marginBottom':'0px','textAlign': 'left','color': '#333','font-family': 'Arial, sans-serif','font-size': '1.1rem','padding-bottom': '10px'}),
                    dcc.Loading(
                         id="loading-pie",
                         type="circle",
                         children=[
                             dcc.Graph(
                                id='pie-chart',
                                style={
                                    #'width': '100%',  # Hace que ocupe todo el ancho del contenedor
        'height':'22vh',  # Ajusta la altura al contenedor
        'display': 'flex',
        'justify-content': 'flex-start',
        'align-items': 'flex-start', 'marginTop':'0px','marginBottom':'0px'                        
                                }
)
                         ]
                     ),
                    
                ])
               
            ])
        ]
    elif tab == 'tab2':
            return [
            #MAPA ESPAÑA
            html.Div(style={'flex': '1', 'border': '1px solid #ccc', 'borderRadius': '10px', 'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)', 'padding': '5px', 'width': '90%', 'display': 'flex', 'flexDirection': 'column','height': '90vh'}, children=[
                html.Div(style={'padding': '10px'}, children=[
                    html.H3("Nota media de acceso a la universidad por provincias y ciudades autónomas", style={'margin': '0','textAlign': 'left','color': '#333','font-family': 'Arial, sans-serif','font-size': '1.5rem','font-weight': 'bold','padding-bottom': '10px'  
            }),html.P("Selecciona el curso académico.", style={'font-family': 'Arial, sans-serif','font-size': '1.2rem','marginTop':'20px'}),
                                
                    html.Div(
                                    children=[
                                        dcc.Slider(
                                            id='course-slider2',
                                            min=0,
                                            max=len(available_courses2) - 1,
                                            step=1,
                                            marks=course_marks2,
                                            included=False,
                                            value=0
                                        )
                                    ],
                                    style={'width': '95%', 'margin': '0 auto','white-space': 'nowrap','marginTop':'30px'}  # Contenedor con el 80% del ancho de la ventana
                                ) 
                ]),
                html.Div([
                    #html.H3("Seleccionado:"),
                    html.Div(id="comunidad-seleccionada", style={'font-family': 'Arial, sans-serif','font-size': '1.2rem','marginTop':'10px','marginBottom':'20px','marginLeft':'10px'}),
                ]),
                dcc.Loading(
                         id="loading-mapa",
                         type="circle",
                         children=[
                             dcc.Graph(id="mapa", config={'scrollZoom': True}, 
                                       style={'marginTop':'10px','marginBottom':'10px','marginLeft':'10px','marginRigth':'10px','flexGrow': 1,'height': '60vh','widht':'50%'}),#,'height': '100%', 'width': '100%',}),
                         ]
                     )
                
               
            ]),
            #FILTROS
           html.Div(style={'flex': '1', 'display': 'flex', 'flexDirection': 'column', 'padding': '0px', 'gap': '10px',  'marginLeft': '10px','marginRight': '10px','height': '91vh'}, children=[             
               
                html.Div(style={'flex': '1', 'border': '1px solid #ccc', 'borderRadius': '10px', 'padding': '10px', 'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)'}, children=[
                    html.H3("Medidas estadísticas por grupos poblacionales", style={'margin': '0','textAlign': 'left','color': '#333','font-family': 'Arial, sans-serif','font-size': '1.1rem','padding-bottom': '20px'}),
                    dcc.Loading(
                         id="loading-mapa",
                         type="circle",
                         children=[
                             dcc.Graph(
                        id='caja-bigote',
                        style={
                            'display': 'flex',
                            'justify-content': 'flex-start',
                            'align-items': 'flex-start',
                            #'height': '50%'  # Esto asegura que el gráfico ocupe toda la altura de la pantalla
                        }
                    ),
                         ]
                     ),
                    
                ]),
                html.Div(style={'flex': '1', 'border': '1px solid #ccc', 'borderRadius': '10px', 'padding': '10px', 'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)'}, children=[
                    html.H3("Top 5 titulaciones por curso y grupo poblacional", style={'margin': '0','marginBottom':'0px','textAlign': 'left','color': '#333','font-family': 'Arial, sans-serif','font-size': '1.1rem','padding-bottom': '10px'}),
                    dcc.RadioItems(
                                    id='poblacion-radio',
                                    options=[
                                        {'label': 'Muy poco densa', 'value': 'Muy poco densa'},
                                        {'label': 'Poco densa', 'value': 'Poco densa'},
                                        {'label': 'Moderadamente densa', 'value': 'Moderadamente densa'},
                                        {'label': 'Densa', 'value': 'Densa'},
                                        {'label': 'Muy densa', 'value': 'Muy densa'}
                                    ],
                                    value='Muy poco densa',
                                    labelStyle={'display': 'inline-block', 'font-family': 'Arial, sans-serif','font-size': '1.0rem', 'marginBottom': '0px','marginRight': '30px'},
                        style={'padding': '10px'}
                                ),
            
                    html.Div(id="top-5-table-container",style={'marginBottom':'0px','marginTop':'0px'}),
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
    Input("mapa", "clickData"),
    Input('course-slider2', 'value'),
)
def actualizar_mapa(click_data,selected_course_index):
    # Comunidad seleccionada
    comunidad_seleccionada = click_data["points"][0]["location"] if click_data else None
    #curso
    selected_course = [available_courses2[selected_course_index]]
    print(selected_course)
    df_filtrado = medias[medias["curso_academico"] == selected_course[0]]  # Filtrar por el curso
    medias_por_provincia = df_filtrado.set_index("des_provincia_centro_sec")["nota_media"].to_dict()

    customdata = [
        medias_por_provincia.get(feature["properties"]["name"], None)
        for feature in comunidades_geojson["features"]
    ]

    figC = crear_mapa(comunidades_geojson, customdata)
    mensaje = (
        f"Ha seleccionado {comunidad_seleccionada}" if comunidad_seleccionada 
        else "Selecciona una provincia o ciudad autónoma"
    )


    return figC, mensaje

#Gráfico caja y bigote
@app.callback(
    Output('caja-bigote', 'figure'),
    [Input("mapa", "clickData"),
        Input('course-slider2', 'value')]
)
def update_caja_bigote(click_data,selected_course_index):
    # Comunidad seleccionada
    comunidad_seleccionada = click_data["points"][0]["location"] if click_data else None
    selected_course = available_courses2[selected_course_index]
    print(selected_course)
    print(comunidad_seleccionada)
    
    notas_filtrado = notas[notas["curso_academico"] == selected_course]  # Filtrar por el curso
    if (click_data!= None):
        notas_filtrado = notas_filtrado[(notas_filtrado["des_provincia_centro_sec"] == comunidad_seleccionada) | (notas_filtrado["des_provincia_centro_sec"] == "Global")]  # Filtrar por el curso
    else:
        notas_filtrado = notas_filtrado[notas_filtrado["des_provincia_centro_sec"] == "Global"]
    return create_caja(selected_course,notas_filtrado)

# Callback para actualizar la tabla según los filtros seleccionados
@app.callback(
    Output("top-5-table-container", "children"),
    [Input('poblacion-radio', 'value'),
     Input('course-slider2', 'value')]
)
def update_table(poblacion,course_index):
    curso = available_courses2[course_index]
    print("actualiza tabla")
    top5_df_filtered = top5_df[top5_df["poblacion"]==poblacion]
    top5_df_filtered = top5_df_filtered[top5_df_filtered["curso_academico"]==curso]
    print(top5_df_filtered)
    return create_top_5_table(top5_df_filtered)

@app.callback(
    Output("line-graph", "figure"),
    Input('university-radio', 'value')
)
def update_graph(universidad):
    # Filtrar datos según los valores seleccionados
    max_value = matriculasG2["porcentaje_todos"].max()
    filtered_df = matriculasG2[matriculasG2["universidad"] == universidad]
    # Definir los colores de las líneas para cada población
    color_map = {
        'Muy densa': '#1f77b4',
        'Densa': '#ff7f0e',
        'Moderadamente densa': '#2ca02c',
        'Poco densa': '#9467bd',
        'Muy poco densa': '#d62728'
    }
    population_order = ['Muy densa', 'Densa', 'Moderadamente densa', 'Poco densa', 'Muy poco densa']

    # Crear el gráfico de líneas
    fig = px.line(
        filtered_df, 
        x="curso_academico", 
        y="porcentaje_todos", 
        color="poblacion", 
        #title=f"Universidad {universidad.upper()}",
        labels={"porcentaje_todos": "Estudiantes"},
        line_shape="linear",
        color_discrete_map=color_map,  # Usar el color_map predefinido
        category_orders={'poblacion': population_order}  # Definir el orden fijo
        )
    fig.update_layout(
          plot_bgcolor="white",  # Fondo blanco para el gráfico
          yaxis=dict(
              gridcolor="lightgrey",  # Cuadrículas ligeras
              #zerolinecolor="grey",  # Línea del cero en gris
              #zerolinewidth=1,       # Grosor de la línea del cero
              range=[0, max_value + 0.0001],  # Ajuste del rango del eje Y
              tickformat=".2%"
          ),
          xaxis=dict(
              title=None,
              gridcolor="lightgrey",  # Cuadrículas ligeras en el eje X
              automargin=True,
              #ticklabelposition="inside",
          ),
          margin=dict(l=40, r=40, t=40, b=40),  # Márgenes uniformes
          font=dict(
              family="Arial, sans-serif",
              size=14,
              #color="#333333"
          ),
          title={
            'text': f"Universidad {universidad.upper()}",
            'y': 0.3,  # Posición vertical del título
            'x': 0.94,  # Posición horizontal del título (a la derecha)
            'xanchor': 'right',  # Anclar el título a la derecha
            'yanchor': 'middle',
            'font': {
                'family': 'Arial, sans-serif',
                'size': 16,  # Tamaño de fuente
                'color': 'black',
            }
        },
         
        legend=dict(
            title=dict(text=""),)
    )
    return fig
    

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)


# In[ ]:




