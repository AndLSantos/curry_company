# 1) Estrturação do Projeto
#    1.1) Importando as Bibliotecas
import pandas as pd
from geopy import distance
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static
import streamlit as st
from datetime import datetime
from PIL import Image

st.set_page_config(page_title = 'Visão Empresa', layout = 'wide')

# ===========================================
# =============== Funções ===================
# ===========================================

def clean_code(df):
    """ Esta função tem a responsabilidade de limpar o dataframe:
        Tipos de Limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Fromatação da coluna de datas
        5. Limpeza da coluna de tempo (Remoção do texto das variáveis numéricas)

        Input: DataFrame
        Output: Dataframe    

    """

    # 1.4) Limpeza de Dados
    # 1.4.1) Retirando os NaN
    df['Delivery_person_Age'].unique() # -> Identificando os valores únicos
    filtro = df.loc[:, 'Delivery_person_Age'] != 'NaN '
    # filtro.unique() -> Verificando que existe NaN no filtro (False)
    df = df.loc[filtro, :] # -> Salvando o DatFrame com as linhas filtradas
    #df['Delivery_person_Age'].unique() #-> Confirmando a retirada

    df['Delivery_person_Ratings'].unique()
    filtro = df.loc[:, 'Delivery_person_Ratings'] != 'NaN '
    df = df.loc[filtro, :]
    #df['Delivery_person_Ratings'].unique() # -> Confirmando a retirada

    df['Weatherconditions'].unique()
    filtro = df.loc[:, 'Weatherconditions'] != 'conditions NaN'
    df = df.loc[filtro, :]
    #print(df['Weatherconditions'].unique()) -> confirmando a retirada

    df['multiple_deliveries'].unique() #-> Verificando a presença de NaN
    filtro = df.loc[:, 'multiple_deliveries'] != 'NaN '
    df = df.loc[filtro, :]
    #print(df['multiple_deliveries'].unique())

    df['Festival'].unique() #-> Presença de Nan
    filtro = df.loc[:, 'Festival'] != 'NaN '
    df = df.loc[filtro, :]
    #print(df['Festival'].unique())

    df['City'].unique() #-. Verificando a presença de NaN
    filtro = df.loc[:, 'City'] != 'NaN '
    df = df.loc[filtro, : ]
    #print(df['City'].unique())

    # 1.4.2) Alterando os tipos
    #df.dtypes -> Verificando os tipos dos dados
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype(float)
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], format = '%d-%m-%Y')
    #df.dtypes -> Confirmando a alteração de fontes

    #   1.4.3) Retirando os espaços das strings
    # Como houve retiranda das linhas (Retirados os NaN): Necessidade de resetar os índices
    df = df.reset_index(drop = True)
    #df

    # df['ID'].unique()# -> Verificando a presença dos espaços
    df.loc[:, 'ID'] = df.loc[:, 'ID'].str.strip()
    df.loc[:, 'Delivery_person_ID'] = df.loc[:, 'Delivery_person_ID'].str.strip()
    df.loc[:, 'Road_traffic_density'] = df.loc[:, 'Road_traffic_density'].str.strip()
    df.loc[:, 'Type_of_order'] = df.loc[:, 'Type_of_order'].str.strip()
    df.loc[:, 'Type_of_vehicle'] = df.loc[:, 'Type_of_vehicle'].str.strip()
    df.loc[:, 'Festival'] = df.loc[:, 'Festival'].str.strip()
    df.loc[:, 'City'] = df.loc[:, 'City'].str.strip()
    #print(df.loc[0, 'ID']) -> Conferindo a retirada dos espaços

    # Problema na coluna time taken (min)
    #df['Time_taken(min)'].unique()
    df['Time_taken(min)'] = df['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    #df.dtypes
    df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)
    #print(df) -> Conferindo a mudança da configuraão
    
    return df


def order_metric(df):
    #   2.1) Quantidade de Pedidos por dia
        cols = ['Order_Date', 'ID']
        df_aux = (df.loc[:, cols].groupby('Order_Date')
                                 .count()
                                 .reset_index())
        #df_aux
        fig = px.bar(df_aux, x = 'Order_Date', y = 'ID')
        return fig

def traffic_order_share(df, cols):
    cols = ['City','Road_traffic_density', 'ID']
    df_aux = (df.loc[:,cols].groupby('Road_traffic_density')
                            .count()
                            .reset_index())
    df_aux['Porcentagem'] = ((df_aux['ID']/df_aux['ID'].sum())*100).round(2)
    fig = px.pie(df_aux, names = 'Road_traffic_density', values = 'Porcentagem')
    return fig

def traffic_order_city(df, cols):
    cols = ['City', 'Road_traffic_density', 'ID']
    df_aux = df.loc[:, cols].groupby(['City', 'Road_traffic_density']).count().reset_index()
    fig = px.scatter(df_aux, x = 'City', y = 'Road_traffic_density', size = 'ID', color = 'City')
    return fig


def order_by_week(df):
    df['week_of_year'] = df.loc[:, 'Order_Date'].dt.strftime('%U')
    cols = ['week_of_year', 'ID']
    df_aux = df.loc[:, cols].groupby('week_of_year').count().reset_index()
    fig = px.line(df_aux, x = 'week_of_year', y = 'ID')
    return fig


def order_share_by_week(df):
    cols1 = ['week_of_year', 'Delivery_person_ID']
    df_entreg_unicos_semana = df.loc[:, cols1].groupby('week_of_year').nunique().reset_index()
    #df_entreg_unicos_semana
    cols2 = ['week_of_year', 'ID']
    df_pedidos_semana = df.loc[:, cols2].groupby('week_of_year').count().reset_index()
    #df_pedidos_semana
    df_aux = pd.merge(df_entreg_unicos_semana, df_pedidos_semana, how = 'inner')
    df_aux['pedido_entregador'] = (df_aux['ID']/df_aux['Delivery_person_ID']).round(2)
    fig = px.line(df_aux, x = 'week_of_year', y = 'pedido_entregador')
    return fig


def country_maps(df):
    cols = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df_aux = df.loc[:, cols].groupby(['City','Road_traffic_density']).median().reset_index()
    mapa = folium.Map()
    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                    location_info['Delivery_location_longitude']],
                    popup = location_info[['City', 'Road_traffic_density']]).add_to(mapa)
    point_map = folium_static(mapa, width = 1024, height = 600 )
    return point_map


# ===========================================
# ========= Inicio do Projeto ===============
# ===========================================

#    1.2) Carregando o Arquivo
#dataset = pd.read_csv('C:/Users/Anderson/Comunidade_DS/Curso_FTC_Python/dataset/train.csv')
dataset = pd.read_csv('dataset/train.csv')
# ===========================================
# ================ Limpeza ==================
# ===========================================

df = clean_code(dataset)

# =============================================#
#       Estruturação do Layout no Streamlit
# =============================================#



# =============================================#
#                Barra Lateral
# =============================================#

# Barra do Lado - Colocando uma imagem
#image_path = ('imagem/marketplace.jpg')
imagem = Image.open('marketplace.jpg')
st.sidebar.image(imagem, width = 200)


# Barra Lateral Título e Subtítulo
st.header('Marketplace - Visão Cliente')
st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivat IndiaTown')
st.sidebar.markdown("""___""")

st.sidebar.markdown('## Selecione as opções desejadas')
date_slider = st.sidebar.slider('Até qual valor?', value=datetime(2022, 4, 6), min_value = datetime(2022, 2, 11), max_value= datetime(2022, 4, 6), format = 'DD-MM-YYYY')

#st.header(date_slider)


st.sidebar.markdown("""___""")
traffic_options = st.sidebar.multiselect('Selecione as condições de trânsito:',
                        ['Low', 'Medium', 'High', 'Jam'],
                        default = ['Low', 'Medium', 'High', 'Jam'])


st.sidebar.markdown("""___""")
city_options = st.sidebar.multiselect('Selecione as cidades:',
                        ['Metropolitian', 'Urban', 'Semi-Urban'],
                        default =  ['Metropolitian', 'Urban', 'Semi-Urban'])

st.sidebar.markdown("""___""")
weather_options = st.sidebar.multiselect('Selecione as condições climáticas:',
                                        ['conditions Cloudy','conditions Fog','conditions Sandstorms','conditions Stormy','conditions Sunny','conditions Windy'],
                                        default = ['conditions Cloudy','conditions Fog','conditions Sandstorms','conditions Stormy','conditions Sunny','conditions Windy'] )


st.sidebar.markdown("""___""")
# Criando uma Marca
#image_path = ('imagem/geospatial_analyst.png')
imagem = Image.open('geospatial_analyst.png')
st.sidebar.image(imagem, width = 120)
st.sidebar.markdown('##### Powered by Geospatial Analyst')


# =============================================#
#         Operacionalização dos Filtros
# =============================================#

# Filtro de Data
filtro_data = df['Order_Date'] <= date_slider # -> Seleção das datas no Dataframe pela selação do usuário no date_slider
df = df.loc[filtro_data, :]
#st.dataframe(df) # Para confirmar que a seleção está sendo feita

# Filtro de Trânsito
filtro_trafeg = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[filtro_trafeg,:]
#st.dataframe(df)# para confirmar que a seleção foi feita

# Filtro das Cidades
filtro_cidade = df['City'].isin(city_options)
df = df.loc[filtro_cidade,:]
#st.dataframe(df)# Para confirmar que as seleções estão sendo feitas

# Filtro das condições climáticas
filtro_clima = df['Weatherconditions'].isin(weather_options)
df = df.loc[filtro_clima,:]
#st.dataframe(df)# Para mostrar que as seleções estão funcionando

# =============================================#
#                Layout no Streamlit
# =============================================#

tab1, tab2, tab3 = st.tabs (['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1: # Identação tudo estará dentro do tab1 (Visão Geográfica)
    with st.container():# Criando o primeiro container -> Ver o plano do diagrame
        st.markdown('# Quantidade de Pedidos por dia')
        fig1 = order_metric(df) # Usa a função Order_Metric definida acima. A variável fig1 é resultado operacional da função
        st.plotly_chart(fig1, use_container_width = True)
           
    with st.container():
        # Criando colunas no Streamlit
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Distribuição dos Pedidos por Tráfego')
            fig2 = traffic_order_share(df,cols = ['Road_traffic_density', 'ID'] )
            st.plotly_chart(fig2, use_container_width = True)        
        
        with col2:
            st.markdown('##### Volume de pedidos por Cidade e Tipo de Tráfego')
            fig3 = traffic_order_city(df,cols = ['City', 'Road_traffic_density', 'ID'] )
            st.plotly_chart(fig3, use_container_width=True)

with tab2:
    with st.container():
        st.markdown('#### Quantidade de Pedidos por Semana')
        fig4 = order_by_week(df)
        st.plotly_chart(fig4, use_container_width=True)  
    
    with st.container():
        st.markdown('#### Quantidade de Pedidos por Entregador por Semana')
        fig5 = order_share_by_week(df)
        st.plotly_chart(fig5, use_container_width=True)           
        
with tab3:
    st.markdown('#### Localização Central da Entrega por Cidade e por Tipo de Tráfego')
    locaz_central = country_maps(df)