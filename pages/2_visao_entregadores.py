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

st.set_page_config(page_title = 'Visão Entregadores', layout = 'wide')

# ===========================================
# =============== Funções ===================
# ===========================================


def clean_code(df):

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


    #  1.4.2) Alterando os tipos
    #df.dtypes -> Verificando os tipos dos dados
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype(float)
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], format = '%d-%m-%Y')
    #df.dtypes -> Confirmando a alteração de fontes


    #  1.4.3) Retirando os espaços das strings
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

def avaliacao_stats (df, col, cols):
    
    df_aux = df.loc[:, cols].groupby(col).agg({'Delivery_person_Ratings':['mean','std']}).round(2)
    df_aux.columns = ['Ratings_mean', 'Ratings_std']
    df_aux = df_aux.reset_index()
    return df_aux
                

def top_delivers(df, top_asc):
    cols = ['City', 'Delivery_person_ID','Delivery_person_Ratings','Time_taken(min)']
    filtro = df['City'] == 'Urban'
    df_urban = df.loc[filtro, cols].sort_values(by = ['Time_taken(min)', 'Delivery_person_Ratings'], ascending = top_asc).head(10)
    #df_mais_lentos_urban

    filtro = df['City'] == 'Metropolitian'
    df_metrop = df.loc[filtro, cols].sort_values(by = ['Time_taken(min)', 'Delivery_person_Ratings'], ascending = top_asc).head(10)
    #df_mais_lentos_metrop

    filtro = df['City'] == 'Semi-Urban'
    df_semiurban = df.loc[filtro, cols].sort_values(by = ['Time_taken(min)', 'Delivery_person_Ratings'], ascending = top_asc).head(10)
    #df_mais_lentos_semiurban

    df_rank = pd.concat([df_urban, df_metrop, df_semiurban]).reset_index(drop=True)
    return df_rank










# ===========================================
# ========= Inicio do Projeto ===============
# ===========================================


#  1.2) Carregando o Arquivo
#dataset = pd.read_csv('C:/Users/Anderson/Comunidade_DS/Curso_FTC_Python/dataset/train.csv')
dataset = pd.read_csv('dataset/train.csv')

# ===========================================
# ================ Limpeza ==================
# ===========================================


#df = dataset.copy()
df = clean_code(dataset)


# =============================================#
#       Estruturação do Layout no Streamlit
# =============================================#



# =============================================#
#                Barra Lateral
# =============================================#

# Barra lateral - Colocando uma imagem
#image_path = ('imagem/marketplace.jpg')
imagem = Image.open('marketplace.jpg')
st.sidebar.image(imagem, width = 200)

# Barra Lateral - Título e Subtítulo 
st.sidebar.markdown('# Marketplace - Visão Entregadores')
st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery at India')
st.sidebar.markdown("""___""")

# Barra Lateral - Estruturação dos Filtros
st.sidebar.markdown('## Selecione  as opções abaixo:')

# Seleção da data
date_slider = st.sidebar.slider('Selecione a data:', value = datetime(2022,4,6),
                   min_value = datetime (2022,2,11), max_value = datetime(2022,4,6),
                     format = 'DD-MM-YYYY')
#st.header(date_slider)# -> Para mostrar que o slider funciona
st.sidebar.markdown("""___""")

# Seleção das Condições de Trânsito
traffic_options = st.sidebar.multiselect('Selecione as condições de trânsito:',
                         ['Low','Medium','High','Jam'],
                         default =['Low','Medium','High','Jam'])

#st.header(traffic_options)# -> Verificar que o multiselecct funciona
st.sidebar.markdown("""___""")

# Seleção de Cidades
city_options = st.sidebar.multiselect('Selecione as cidades:',
                        ['Metropolitian', 'Urban', 'Semi-Urban'],
                        default =  ['Metropolitian', 'Urban', 'Semi-Urban'])
#st.header(city_options) #-> Verificando que o multiselect funciona
st.sidebar.markdown("""___""")

# Seleção das Condições Climáticas
weather_options = st.sidebar.multiselect('Selecione as condições climáticas:',
                                        ['conditions Cloudy','conditions Fog','conditions Sandstorms','conditions Stormy','conditions Sunny','conditions Windy'],
                                        default = ['conditions Cloudy','conditions Fog','conditions Sandstorms','conditions Stormy','conditions Sunny','conditions Windy'] )

#st.header(weather_options) #-> Verificando que o multiselect funciona
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

st.markdown('# Visão Entregadores')

# Criação de abas
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_','_'])

# Conteúdo da aba tab1 (Visão Gerencial)
with tab1:
    with st.container():
        st.markdown('### Métricas Gerais')
        col1,col2,col3, col4 = st.columns(4, gap = 'large')
        with col1:
            # Maior idade dos entregadores
            df_maior_idade = df.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior Idade (anos)', df_maior_idade)
        with col2:
            # Menor idade dos entregadores
            df_menor_idade = df.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor Idade (anos)', df_menor_idade)
        with col3:
            # Melhor Condição do Veículo
            melhor_cond = df.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor Condição do Veículo:', melhor_cond)
        with col4:
            # Pior Condição do Veículo
            pior_cond = df.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior Condição do Veículo:', pior_cond)
    st.markdown('''___''')
    
    with st.container ():
        st.markdown('### Avaliações')
        col5, col6 = st.columns(2)
        with col5:
            st.markdown('Avaliação Média por Entregador')
            cols = ['Delivery_person_ID', 'Delivery_person_Ratings']
            df_aux = df.loc[:, cols].groupby('Delivery_person_ID').mean().round(2).reset_index()
            st.dataframe(df_aux)
       
        with col6:
            with st.container():
                st.markdown('Avaliação Média por Trânsito')
                aval_media_traffic = avaliacao_stats(df, col = 'Road_traffic_density', cols = ['Road_traffic_density', 'Delivery_person_Ratings'])
                st.dataframe(aval_media_traffic)

            st.markdown('''___''')
            with st.container():
                st.markdown('Avaliação Média por Condições Climáticas')
                aval_media_weather = avaliacao_stats(df, col = 'Weatherconditions', cols = ['Weatherconditions', 'Delivery_person_Ratings'] )
                st.dataframe(aval_media_weather)
          

    st.markdown('''___''')
   
    with st.container():
        st.markdown('### Velocidade de Entrega')
        col7,col8 = st.columns(2)
        with col7:
            st.markdown('Entregadores mais rápidos')
            df_rank_mais_rapido = top_delivers(df, top_asc = [True, False])
            st.dataframe(df_rank_mais_rapido)

        with col8:
            st.markdown('Entregadores mais lentos')
            df_rank_mais_lento = top_delivers(df, top_asc = [False, True])
            st.dataframe(df_rank_mais_lento)

            
                





































