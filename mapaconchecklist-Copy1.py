#!/usr/bin/env python
# coding: utf-8

# In[1]:


from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd

# Cargar los datos\ 
matricula = pd.read_csv("https://raw.githubusercontent.com/paulamielgo/Univaciada_data/refs/heads/main/matricula.csv")

# Crear la aplicación Dash
app = Dash(__name__)

server = app.server

# Crear el gráfico de mapa con MapLibre
def create_figure(selected_universities):
    # Filtrar los datos según las universidades seleccionadas
    filtered_data = matricula[matricula['universidad'].isin(selected_universities)]

    # Crear el scatter_mapbox para los datos de matrícula
    fig = px.scatter_mapbox(
        filtered_data,
        lat="lat_municipio_residencia",
        lon="lon_municipio_residencia",
        color="universidad",
        size="scaled_count",
        size_max=20,
        color_discrete_map={
            "uc3m": '#1f77b4', 
            "uva": '#ff7f0e', 
            "uam": '#2ca02c', 
            "ucm": '#d62728', 
            "urjc": '#9467bd'
        },
        hover_name="des_municipio_residencia",
        hover_data={"count": True, "lat_municipio_residencia": False, "lon_municipio_residencia": False},
        title="Estudiantes por universidad"
    )

    # Configuración del mapa
    fig.update_layout(
        mapbox_style="carto-positron",  # Usar OpenStreetMap como estilo base
        title="Estudiantes y Sedes de Universidades",
        autosize=True,
        showlegend=True,
        mapbox=dict(
            center=dict(
                lat=40.4168,  # Centro del mapa
                lon=-3.7038   # Centro del mapa
            ),
            zoom=5  # Nivel de zoom inicial
        )
    )
    return fig

# Layout del dashboard
app.layout = html.Div(style={'display': 'flex', 'flexDirection': 'column', 'height': '100vh'}, children=[
    dcc.Tabs(id='tabs', value='tab1', style={'height': '10%'}, children=[
        dcc.Tab(label='Pestaña 1', value='tab1'),
        dcc.Tab(label='Pestaña 2', value='tab2'),
        dcc.Tab(label='Pestaña 3', value='tab3'),
    ]),
    html.Div(id='content', style={'flex': '1', 'display': 'flex', 'height': '90%'})
])

@app.callback(
    Output('content', 'children'),
    [Input('tabs', 'value')]
)
def update_content(tab):
    if tab == 'tab1':
        return [
            html.Div(style={'flex': '1', 'border': '1px solid black', 'width': '60%'}, children=[
                dcc.Graph(
                    id='map',
                    figure=create_figure(['uc3m', 'uva', 'uam', 'ucm', 'urjc']),
                    config={'scrollZoom': True},
                    style={'height': '100%', 'width': '100%'}
                )
            ]),
            html.Div(style={'flex': '1', 'display': 'flex', 'flexDirection': 'column'}, children=[
                html.Div(style={'flex': '1', 'border': '1px solid black', 'height': '50%'}, children=[
                    html.H3("Selecciona Universidades", style={'margin': '0', 'textAlign': 'center'}),
                    dcc.Checklist(
                        id='university-checkbox',
                        options=[
                            {'label': 'UC3M', 'value': 'uc3m'},
                            {'label': 'UVA', 'value': 'uva'},
                            {'label': 'UAM', 'value': 'uam'},
                            {'label': 'UCM', 'value': 'ucm'},
                            {'label': 'URJC', 'value': 'urjc'}
                        ],
                        value=['uc3m', 'uva', 'uam', 'ucm', 'urjc'],
                        labelStyle={'display': 'block'}
                    ),
                ]),
                html.Div(style={'flex': '1', 'border': '1px solid black', 'height': '50%'}, children=[
                    html.H3("Panel Inferior Derecho - Pestaña 1", style={'margin': '0', 'textAlign': 'center'}),
                    dcc.Graph(
                        id='graph2',
                        figure=px.bar(x=["A", "B", "C"], y=[5, 3, 6], title="Ejemplo Gráfico 2"),
                        style={'height': '100%', 'width': '100%'}
                    )
                ])
            ])
        ]

@app.callback(
    Output('map', 'figure'),
    [Input('university-checkbox', 'value')]
)
def update_map(selected_universities):
    return create_figure(selected_universities)

if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=8050)


# In[ ]:




