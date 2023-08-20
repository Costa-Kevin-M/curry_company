## import libraries
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static
from haversine import haversine
import numpy as np
import plotly.graph_objects as go


st.set_page_config(
    page_title = 'Visão Restaurantes',
    page_icon = ' ' ,
    layout = 'wide')

## Funções

def plot_pizza( dataframe ):

    ''' Essa função tem a finalidade de plotar um gráfico
    de pizza com a distancia média entre o local de entrega
    e o restaurante por cidade

    input: dataframe
    output: figura
    '''

    
    dataframe = dataframe[['Delivery_location_latitude', 'Delivery_location_longitude', "Restaurant_longitude", 'Restaurant_latitude','City']]
    col = ['Delivery_location_latitude', 'Delivery_location_longitude', "Restaurant_longitude", 'Restaurant_latitude']
    dataframe['distance'] = ( dataframe[col].apply( lambda x: haversine( (x['Delivery_location_longitude'],  x['Delivery_location_latitude']),
                                                                 ( x["Restaurant_longitude"], x['Restaurant_latitude']) ),
                                                                 axis = 1 )
                                    .values
                         )
    dataframe = dataframe[['City','distance']].groupby(['City']).agg({'distance': ['mean']}).reset_index()
    dataframe.columns = ['City', 'avg_distance']
    figure = go.Figure( data = [ go.Pie( labels = dataframe['City'], values = dataframe['avg_distance'] , pull = [0,0.1,0] )])

    return figure


def plot_sunburst( dataframe ):

    ''' Essa função tem a finalidade de plotar um gráfico
    sunburst com a média e o desvio padrão do tempo de
    entrega por cidade e por densidade de trânsito

    input: dataframe
    output: figura
    '''
    
    dataframe = ( dataframe[['City','Time_taken(min)', 'Road_traffic_density']]
               .groupby(['City', 'Road_traffic_density'])
               .agg({'Time_taken(min)': ['mean','std']})
               .reset_index()
             )
    
    dataframe.columns = ['City', 'Road_traffic_density', 'mean_time', 'std_time']
    figure = px.sunburst( dataframe,
                       path = ['City', 'Road_traffic_density'],
                       values = 'mean_time',
                       color = 'std_time',
                       color_continuous_scale = 'RdBu',
                      color_continuous_midpoint = np.average( dataframe['std_time'] )
                     )
    return figure


def avg_std_time_bar( dataframe ):

    ''' Essa função tem a finalidade de plotar um gráfico
    de barras com a média e o desvio padrão do tempo de
    entrega por cidade

    input: dataframe
    output: figura
    '''
    
    
    dataframe = ( dataframe[['City','Time_taken(min)']].groupby(['City'])
                                                       .agg({'Time_taken(min)': ['mean','std']})
                                                       .reset_index()
                )
    
    dataframe.columns = ['City', 'mean_time', 'std']
    figure = go.Figure()
    figure.add_trace( go.Bar( name = 'Control',
                            x = dataframe['City'],
                            y = dataframe['mean_time'],
                            error_y = dict( type = 'data', array= dataframe['std'])
                         )
                 )
    return figure


def metric_time_festival(df, festival, metric):

    ''' Essa função tem a finalidade de calcular a
    média ou o desvio padrão quando ocorre os festivais
    e quando não ocorre

    input: dataframe, bolano, string
    output: float
    '''
    
    std_time_festival = df[['Festival', 'Time_taken(min)']].groupby(['Festival'])
                        
    if (metric == 'std'):
        std_time_festival = ( std_time_festival.std()
                                           .reset_index()
                                           .iloc[int(festival),1]
                        )
        
    if (metric == 'mean'):
        std_time_festival = ( std_time_festival.mean()
                                           .reset_index()
                                           .iloc[int(festival),1]
                        )
    
    return round(std_time_festival,2)

def distancia_media( df ): 

    ''' Essa função tem a finalidade de calcular a
    distancia do restaurante e o local de entrega
    dadas as latitudes e calcular a distancia média

    input: dataframa
    output: float
    '''
    
    cols = ['Delivery_location_latitude', 'Delivery_location_longitude', "Restaurant_longitude", 'Restaurant_latitude']
    avg_distance= df[cols] 
    avg_distance = np.round( avg_distance[cols]
                             .apply( lambda x: haversine( 
                                                         ( x['Delivery_location_longitude'],  x['Delivery_location_latitude']) , 
                                                         ( x["Restaurant_longitude"], x['Restaurant_latitude']) ),
                                    axis = 1 )
                             .values
                             .mean(),
                            2
                           )
    return avg_distance



def df_cleaning( dataframe ):
    ''' Essa função tem a finalidade de limpar o dataframe
        Processo de limpeza:

        - Remoção de espaços nos nomes de algumas colunas
        - Remoção de celulas com NaN
        - Conversão de tipos de variáveis
        - Formatação da coluna de datas
        - Remoção do texto das variáveis da coluna 'Time_taken(min)'
        
    input: dataframa
    output: dataframe
    '''
    for i in [0,1,12,14,15,17,17]:
      dataframe.iloc[:,i] = dataframe.iloc[:,i].str.strip()
    dataframe = dataframe[(dataframe['Delivery_person_Age'] != 'NaN ')].copy()
    dataframe.reset_index()
    dataframe['Delivery_person_Age'] = dataframe['Delivery_person_Age'].astype( int )
    dataframe['Delivery_person_Ratings'] = dataframe['Delivery_person_Ratings'].astype( float)
    pd.to_datetime(dataframe['Order_Date'], format = '%d-%m-%Y')
    dataframe['Order_Date'] = pd.to_datetime(dataframe['Order_Date'], format = '%d-%m-%Y')
    dataframe = dataframe[(dataframe['multiple_deliveries'] != 'NaN ' )]
    dataframe = dataframe.loc[dataframe['Road_traffic_density'] != 'NaN', :]
    dataframe = dataframe[(dataframe['City'] != 'NaN ' )]
    dataframe = dataframe[(dataframe['Festival'] != 'NaN' )]
    dataframe['multiple_deliveries'] = dataframe['multiple_deliveries'].astype( int)
    dataframe.reset_index()
    dataframe['Time_taken(min)'] = dataframe['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1] ).astype( int )

    return dataframe

## data cleaning

df = pd.read_csv('./dataset/dataframe1.csv')

df = df_cleaning( df ) 

## sidebar

st.header('Marketplace - Visão Restaurantes')
image = Image.open( 'logo.png' )
st.sidebar.image( image, width=120)
st.sidebar.markdown( "# Curry Company ")
st.sidebar.markdown( "## Fastest Delivery in Town")
st.sidebar.markdown( """---""" )
st.sidebar.markdown( '## Selecione uma data limite')
data_slider = st.sidebar.slider(
    
    'Até qual valor',
    value = datetime( 2022,4,13 ),
    min_value = datetime(2022,2,11),
    max_value = datetime(2022,4,6),
    format = 'DD-MM-YYYY'

)
st.sidebar.markdown( """---""" )
traffic_options = st.sidebar.multiselect(
    
    'Quais as condições de trânsito?',
    ['Low','Medium','High','Jam'],
    default = ['Low','Medium','High','Jam']

)
st.sidebar.markdown( """---""" )
weather_options = st.sidebar.multiselect(
    
    'Quais as condições de clima?',
    ['conditions Cloudy','conditions Fog','conditions Sandstorms','conditions Stormy', 'conditions Sunny', 'conditions Windy'],
    default = ['conditions Cloudy','conditions Fog','conditions Sandstorms','conditions Stormy', 'conditions Sunny', 'conditions Windy']

)
st.sidebar.markdown( """---""")
st.sidebar.markdown( '### Powered by Kevin Costa')

# Filtro de data

df = df.loc[(df['Order_Date'] < data_slider) , :]

# Filtro de trânsito

df = df.loc[ df['Road_traffic_density'].isin( traffic_options ),:]

# Filtro de clima

df = df.loc[ df['Weatherconditions'].isin( weather_options ),:]

## streamlit layout

tab1, tab2, tab3 = st.tabs( [ 'Visão Gerencial', '_', '_'] )

with tab1:

    with st.container():

        st.title( 'Overall Metrics' )
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            unique_delivers =  ( df['Delivery_person_ID']
                                 .nunique()
                               )
            col1.metric( 'Entregadores Unicos', unique_delivers)
            
        with col2:

            avg_distance = distancia_media( df )
            col2.metric( 'Distancia média das entregas', avg_distance )                              

        with col3:
            avg_time_festival = metric_time_festival(df, True, 'mean') 
            col3.metric( 'Tempo Festival' , avg_time_festival)

        with col4:
                
            std_time_festival = metric_time_festival(df, True, 'std')    
            col4.metric( 'Desvio Festival' , std_time_festival)

        with col5:

            avg_time_no_festival = metric_time_festival(df, False, 'mean')
            
            col5.metric( 'Tempo s/Festival' , avg_time_no_festival)

        with col6:
            std_time_no_festival = metric_time_festival(df, False, 'std')
            col6.metric( 'Desvio s/Festival' , std_time_no_festival)
            
    st.markdown( '''---''') 
    with st.container():
        
        col1, col2 = st.columns(2)
        with col1:

            st.title( 'Tempo médio e desvio padrão de entrega por cidade' )
            fig = avg_std_time_bar( df )
            st.plotly_chart( fig )
            
        with col2:
            st.title( 'Tempo médio de entrega por cidade/transito' )
            
            df_aux = ( df[['City','Time_taken(min)', 'Road_traffic_density']]
                      .groupby(['City', 'Road_traffic_density'])
                      .agg({'Time_taken(min)': ['mean','std']})
                      .reset_index() 
                     )
            
            df_aux.columns = ['City','Road_traffic_density', 'mean_time', 'std_time'] 
            st.dataframe(df_aux)

    with st.container():

        st.markdown( '''---''')
        st.title( 'Distribuição do tempo' )
        col1, col2 = st.columns(2)

        with col1:

            fig = plot_pizza( df )
            st.plotly_chart( fig)
            
        with col2:

            fig = plot_sunburst( df )
            st.plotly_chart( fig )










