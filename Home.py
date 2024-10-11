import streamlit as st
from PIL import Image


st.set_page_config(
    page_title = 'Home')


# Barra do Lado - Colocando uma imagem
#image_path = ('imagem/marketplace.jpg')
imagem = Image.open('marketplace.jpg')
st.sidebar.image(imagem, width = 200)


# Barra Lateral Título e Subtítulo
st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery IndiaTown')
st.sidebar.markdown("""___""")

st.write('# Curry Company Growth Dashboard')

st.markdown(
    """ 
    Growth Dashboard foi construído para acompanhar as métricas de crescimento do entregadores e restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas Gerais de Comportamento
        - Visão Tática: Indicadores Semanais de crescimento
        - Visão Geográfica: Insights de Geolocalização
    - Visão Entregador:
        - Acompanhamento dos Indicadores Semanais de Crescimento
    - Visão Restautante:
        - Indicadores Semanais de Crescimento dos Restaurantes
    ### Ask for Help
    - Data GeoScience Company Team
    ### Última Atualização:
    - 10/10/2024

""")

#image_path = ('imagem/geospatial_analyst.png')
imagem = Image.open('geospatial_analyst.png')
st.sidebar.image(imagem, width = 120)
st.sidebar.markdown('##### Powered by Geospatial Analyst')