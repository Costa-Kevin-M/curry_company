import streamlit as st
from PIL import Image


st.set_page_config(
    page_title = 'Home',
    page_icon = ' '
)

imagem = Image.open('logo.png' )

st.sidebar.image( imagem , width = 120 )

st.sidebar.markdown( "# Curry Company ")
st.sidebar.markdown( "## Fastest Delivery in Town")
st.sidebar.markdown( """---""" )

st.write( '# Curry company growth dashboard' )

st.markdown(
   '''
    Growth Dashboard foi construido para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar o dashboard?
    - Visão Empresa:
        - Vião Gerencial: Métricas de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de localização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restuarantes.
    ### Ask for help
    - Kevin Mota da Costa
    - dacosta.kevin.m@gmail.com
    '''
)
