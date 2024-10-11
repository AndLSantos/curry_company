# 1) Estrturação do Projeto
#    1.1) Importando as Bibliotecas
import pandas as pd
import numpy as np
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
        Output: Dataframe """

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

def distancia(df):
    cols = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
    df['Distance_km'] = df.loc[:, cols].apply(lambda x: distance.distance ((x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                                       (x['Delivery_location_latitude'],x['Delivery_location_longitude'])).km, axis =1 )
    cols = ['City', 'Distance_km']
    df_aux = df.loc[:, cols].groupby('City').agg({'Distance_km':['mean','std', 'median', 'max', 'min']})
    df_aux.columns = ['Distance_km_mean', 'Distance_km_std', 'Distance_km_median', 'Distance_km_max', 'Distance_km_min']
    df_aux = df_aux.reset_index()
    avg_distance = df_aux['Distance_km_mean'].mean()
    return avg_distance


def time_delivery (df, festival, op):
    '''
    Parâmetros:
    - df -> Dataframe
    - op -> Coluna do dataframe : time_mean ou time_std

    '''
    cols =['Festival', 'Time_taken(min)']
    df_aux = df.loc[:, cols].groupby('Festival').agg({'Time_taken(min)':['mean','std']})
    df_aux.columns = ['time_mean','time_std']
    df_aux = df_aux.reset_index()
    filtro_festival = df_aux['Festival'] == festival
    df_aux_festival = df_aux.loc[filtro_festival,:]
    df_aux = np.round(df_aux_festival[op],2)
    return df_aux
    #tempo_med_fest = f'{tempo_med_fest:.2f}'


def avg_std_time_graph(df):
    cols = ['City', 'Time_taken(min)']
    df_aux = df.loc[:, cols].groupby('City').agg({'Time_taken(min)':['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar (name = 'Control', x = df_aux['City'], y = df_aux['avg_time'], error_y = dict(type = 'data', array = df_aux['std_time'] )))
    fig.update_layout(barmode = 'group')
    return fig







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

st.markdown('# Visão Restaurantes')

# Criação de abas
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_','_'])

# Conteúdo da aba tab1 (Visão Gerencial)
with tab1:
    with st.container():
        st.markdown('#### Métricas Gerais')
        col1,col2,col3, col4, col5, col6 = st.columns(6)
        with col1:
            #st.markdown('##### Entregadores únicos')
            qtde_entreg_unicos = df['Delivery_person_ID'].nunique()
            col1.metric('Entregadores Únicos', qtde_entreg_unicos)
            # qtde_entreg_unicos = len(df['Delivery_person_ID'].unique())
    
        with col2:
            #st.markdown('###### Distância Média')
            avg_distance = distancia(df)
            avg_distance = f'{avg_distance:.2f}'
            col2.metric('Distância Média', avg_distance)
           
        with col3:
            #st.markdown('##### Tempo médio de entregas com festival')
            tempo_med_fest = time_delivery(df, festival = 'Yes', op = 'time_mean')
            col3.metric('Tempo Médio com Festival',tempo_med_fest)  

        with col4:
            #st.markdown('##### Desvio padrão de Entrega com Festival')
            desv_pd_fest = time_delivery(df, festival = 'Yes', op = 'time_std')
            col4.metric('Desvio-Padrão com Festival',desv_pd_fest)
  
        with col5:
            #st.markdown('##### Tempo de Entrega Médio sem Festival')
            tempo_med_sfest = time_delivery(df, festival = 'No', op = 'time_mean')
            col5.metric('Tempo Médio Sem Festival',tempo_med_sfest)
            
        with col6:
            #st.markdown('##### Desvio padrão das entregas sem Festival')
            desv_pd_sfest = time_delivery(df, festival = 'No', op = 'time_std')
            col6.metric('Desvio-Padrão com Festival',desv_pd_sfest)

    st.markdown('''___''')
    
    with st.container ():
        st.markdown('### Gráfico de Pizza: Tempo de Entrega Médio por Cidade')
        # Calcular a distância média, o desvio padrão, mediana, max e min por cidade
        cols = ['City', 'Distance_km']
        df_aux = df.loc[:, cols].groupby('City').agg({'Distance_km':['mean','std', 'median', 'max', 'min']})
        df_aux.columns = ['Distance_km_mean', 'Distance_km_std', 'Distance_km_median', 'Distance_km_max', 'Distance_km_min']
        df_aux = df_aux.reset_index()
        avg_distance = df_aux['Distance_km_mean'].mean().round(3)
        #print(avg_distance)

        # Gráfico de pizza
        cols = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
        df['Distance_km'] = df.loc[:, cols].apply(lambda x: distance.distance ((x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                                       (x['Delivery_location_latitude'],x['Delivery_location_longitude'])).km, axis =1 )
        avg_distances = df.loc[:, ['City', 'Distance_km']].groupby('City').mean().reset_index()
        #avg_distances['Distance_km'] = {avg_distances['Distance_km'].round(2)
        #avg_distances
        fig = go.Figure(data = [go.Pie(labels = avg_distances['City'], values = avg_distances['Distance_km'],texttemplate = '%{value:.2f}', textfont = dict(color = 'white'), pull = [0,0.1,0])])
        st.plotly_chart(fig)



    st.markdown('''___''')
   
    with st.container():
        st.markdown('### Gráfico Sunburst: Tempo médio por tipo de entrega') 
        # Dados para a tebala e para o Gráfico
        #df.head(5)
        cols = ['City','Road_traffic_density','Time_taken(min)']
        df_aux = df.loc[:, cols].groupby(['City','Road_traffic_density']).agg({'Time_taken(min)':['mean','std']})
        df_aux.columns = (['time_mean', 'time_std'])
        df_aux = df_aux.reset_index()
        #df_aux
        # Estrturação do Gráfico Sunburst
        #df_aux
        fig = px.sunburst (df_aux, path = ['City', 'Road_traffic_density'], values = 'time_mean',
                                                color = 'time_std', color_continuous_scale = 'RdBu_r',
                                                color_continuous_midpoint = np.average(df_aux['time_std']))
        st.plotly_chart(fig)






 
    with st.container():
        fig = avg_std_time_graph(df)
        st.plotly_chart(fig)

        
        



































