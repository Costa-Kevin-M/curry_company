## import dataset
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static


st.set_page_config(
    page_title = 'Visão Empresa',
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


def order_metric(dataframe):

    ''' Essa função tem a finalidade de criar um gráfico
        de barras de quantidade de pedidos por dia

    input: dataframa
    output: figura
    '''
    
    cols = ['ID', 'Order_Date']
    dataframe = dataframe.loc[:, cols].groupby(['Order_Date'])
    dataframe = dataframe.count().reset_index()
                    
    return px.bar(dataframe, x = 'Order_Date', y = 'ID')

def traffic_order_share( dataframe ):

    ''' Essa função tem a finalidade de criar um gráfico
        de pizza com a distribuição das densidades de tráfego

    input: dataframa
    output: figura
    '''
                
    cols = ['ID', 'Road_traffic_density']
    
    dataframe = dataframe.loc[:, cols].groupby(['Road_traffic_density'])
                
    dataframe = dataframe.count().reset_index()
    dataframe['entregas_perc'] = dataframe['ID'] / dataframe['ID'].sum()
                
    return px.pie( dataframe, values='entregas_perc', names = 'Road_traffic_density')

def traffic_order_city(dataframe):

    ''' Essa função tem a finalidade de criar um gráfico
        de bolhas com a quantidade de entregas por cidade
        e densidade de tráfego

    input: dataframa
    output: figura
    '''
                
    cols = ['ID', 'City', 'Road_traffic_density']
                
    dataframe = dataframe.loc[:, cols].groupby(['City', 'Road_traffic_density'])
                
    dataframe = dataframe.count().reset_index()
                
    return px.scatter(dataframe, x='City', y = 'Road_traffic_density', size = 'ID', color = 'City')

def order_by_week( dataframe ):

    ''' Essa função tem a finalidade de criar um gráfico
        de linha com a quantidade de entregas semana

    input: dataframa
    output: figura
    '''

    dataframe['week_of_year'] = dataframe['Order_Date'].dt.strftime('%U')
        
    dataframe = dataframe.loc[:, ['ID', 'week_of_year']].groupby(['week_of_year']).count().reset_index()
            
    return px.line( dataframe, y = 'ID', x = 'week_of_year')

def order_share_by_week( dataframe ):

    ''' Essa função tem a finalidade de criar um gráfico
        de linha com a quantidade de entregas/entregador
        (entregas por entregador) por semana

    input: dataframa
    output: figura
    '''

    selecao1 = dataframe.loc[:, ['ID', 'week_of_year']].groupby(['week_of_year']).count().reset_index()
            
    selecao2 = dataframe.loc[:, ['Delivery_person_ID','week_of_year']].groupby(['week_of_year']).nunique().reset_index()
            
    selecao3 = pd.merge( selecao1 , selecao2 , how = 'inner')
            
    selecao3['order_by_delivery'] = selecao3['ID'] / selecao3['Delivery_person_ID']
            
    return px.line(selecao3, x='week_of_year', y='order_by_delivery')
    
def restaurant_map( dataframe ):

    ''' Essa função tem a finalidade de criar um mapa
    com a localização dos restauranes e informações de
    nome da cidade e densidade de tráfego

    input: dataframa
    output: figura
    '''

    dataframe = ( dataframe.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']]
                           .groupby(['City', 'Road_traffic_density'])
                           .median()
                           .reset_index()

                )
    
    map = folium.Map()
    
    for index, location_info in dataframe.iterrows():
      ( folium.Marker( [ location_info['Delivery_location_latitude'], location_info['Delivery_location_longitude']],
                     popup = location_info[['City','Road_traffic_density']])
              .add_to(map)
      )
    return map

## data cleaning

df = pd.read_csv('./dataset/dataframe1.csv')

df = df_cleaning( df ) 


## sidebar
st.header('Marketplace - Visão Empresa')


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
    format = 'DD-MM-YYYY')


st.sidebar.markdown( """---""" )


traffic_options = st.sidebar.multiselect(
    'Quais as condições de trânsito?',
    ['Low','Medium','High','Jam'],
    default = ['Low','Medium','High','Jam'])

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

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'] )

with tab1:
    # Order Metric

    with st.container():

        st.markdown( '# Orders by day')

        fig = order_metric( df )
        st.plotly_chart( fig , use_container_width = True)

    with st.container():
        
        col1, col2 = st.columns(2)
    
        with col1:
            st.markdown( '# Traffic Order Share')

            fig = traffic_order_share(df)

            st.plotly_chart( fig , use_container = True)
            
        with col2:
            st.markdown( '# Traffic Order City') 

            fig = traffic_order_city( df)
            st.plotly_chart( fig , use_container = True)

with tab2:

    with st.container():
        
        st.markdown('# Order by Week')
        fig = order_by_week( df )
        st.plotly_chart( fig , use_container = True)

    with st.container():

        st.markdown('# Order share by Week')
        fig = order_share_by_week( df)
        st.plotly_chart( fig , use_container = True)



with tab3:
    st.markdown('# Restaurant Maps')

    # A localização central de cada restuarante por tipo de trafego

    map = restaurant_map( df)

    folium_static( map, width = 1024, height = 600)
    








