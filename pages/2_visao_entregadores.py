## import libraries
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static



st.set_page_config(
    page_title = 'Visão Entregadores',
    page_icon = ' ' ,
    layout = 'wide')


## Funções

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


def top_delivers( dataframe , crescente ):

    ''' Essa função tem a finalidade de retornar
    os top 10 entregadores (pelo tempo de entrega)
    do dataframe.
        
    input: dataframa, booleano
    output: dataframe
    '''

                
    top = ( dataframe[['Delivery_person_ID','Time_taken(min)', 'City']]
            .groupby(['City', 'Delivery_person_ID'])
            .mean()
            .sort_values(['City', 'Time_taken(min)'] , ascending = crescente)
            .reset_index()
          )
                
    top1 = top[ top['City'] == 'Metropolitian '].head(10)
    top2 = top[ top['City'] == 'Semi-Urban '].head(10)
    top3 = top[ top['City'] == 'Urban '].head(10)
                
    return pd.concat( [top1 , top2 , top3] ).reset_index(drop = True)

## data cleaning

df = pd.read_csv('./dataset/dataframe1.csv')

df = df_cleaning( df ) 

## sidebar

st.header('Marketplace - Visão Entregadores')
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

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '_','_'] )
with tab1:

    with st.container():

        st.title( 'Overall Metrics')
        col1, col2, col3, col4 = st.columns( 4, gap='large')
        with col1:   

            # A maior idade dos entregadores
            maior_idade = df[['Delivery_person_Age']].max()
            col1.metric( 'Maior idade', maior_idade )
            
        with col2:

            # A menor idade dos entregadores
            menor_idade = df[['Delivery_person_Age']].min()
            col2.metric( 'Menor idade', menor_idade )
            
        with col3:
            
            # A melhor condicao de veiculo
            melhor_condicao = df[['Vehicle_condition']].max()
            col3.metric( 'Melhor condição de veiculo', melhor_condicao )
            
        with col4:
            
            # A pior condicao de veiculo
            pior_condicao = df[['Vehicle_condition']].min()
            col4.metric( 'Pior condição de vehiculo', pior_condicao )
            
    with st.container():

        st.markdown( '''---''')        
        st.title( 'Avaliações')
        col1, col2 = st.columns(2)
        
        with col1:
            
            st.markdown('##### Avaliação média por entregador')

            avg_rating_per_deliver = ( df[['Delivery_person_ID','Delivery_person_Ratings']]
                                        .groupby(['Delivery_person_ID'])
                                        .mean()
                                        .reset_index()
                                     )
            st.dataframe( avg_rating_per_deliver )
        

        with col2:

            st.markdown('##### Avaliação média por transito')

            avg_rating_per_traffic = ( df[['Delivery_person_Ratings','Road_traffic_density']]
                                       .groupby(['Road_traffic_density'])
                                       .agg({'Delivery_person_Ratings': ['mean','std']})
                                       .reset_index()
                                     )
          
            avg_rating_per_traffic.columns = ['Road_traffic_density','mean','std' ]

            st.dataframe( avg_rating_per_traffic )
            st.markdown( '##### Avaliação média por clima')

            avg_rating_per_weather = ( df[['Delivery_person_Ratings','Weatherconditions']]
                                       .groupby(['Weatherconditions'])
                                       .agg({'Delivery_person_Ratings': ['mean','std']})
                                       .reset_index()
                                     )
          
            avg_rating_per_weather.columns = ['Weatherconditions','mean','std' ]

            st.dataframe( avg_rating_per_weather )

    with st.container():

        st.markdown( '''---''')
        st.title( 'Velocidade de entrega' )
        
        col1, col2 = st.columns(2)

        with col1:

            st.markdown( '##### Top entregadores mais rapidos' )
            fastest_derivers = top_delivers( df , True)
            st.dataframe( fastest_derivers )

        with col2:

            st.markdown( '##### Top entregadores mais lentos' )
            slowest_derivers = top_delivers( df , False)            
            st.dataframe( slowest_derivers )

        

            








