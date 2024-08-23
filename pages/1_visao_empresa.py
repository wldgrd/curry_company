### Libraries ###
from datetime import datetime
from haversine import haversine
import pandas as pd
import re
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image #import PIL.Image as imgpil
import folium
from streamlit_folium import folium_static
### Import dataset ###
df = pd.read_csv('train.csv')

df1 = df.copy()
#############################################################################
#Excluindo as linhas nulas
linhasSelecionadas = df1['Delivery_person_Age'] != 'NaN '
df1 = df1.loc[linhasSelecionadas, :].copy()

linhasSelecionadas = df1['Road_traffic_density'] != 'NaN '
df1 = df1.loc[linhasSelecionadas, :].copy()

linhasSelecionadas = df1['City'] != 'NaN '
df1 = df1.loc[linhasSelecionadas, :].copy()

linhasSelecionadas = df1['Festival'] != 'NaN '
df1 = df1.loc[linhasSelecionadas, :].copy()

linhasSelecionadas = df1['Weatherconditions'] != 'conditions NaN'
df1 = df1.loc[linhasSelecionadas, :].copy()
############## Convertendo os tipos das colunas #####################

#convertendo 'Delivery_person_Age' para int

df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

#convertendo 'Delivery_person_Ratings' para float
df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

#convertendo 'Order_Date' para Datetime
df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format = '%d-%m-%Y')

#convertendo 'multiple_deliveries' para int
linhas_selecionadas = df1['multiple_deliveries'] != 'NaN '
df1 = df1.loc[linhas_selecionadas, :]
df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

#######################################################################

#### Resetando os índices ####
df1 = df1.reset_index(drop = True) ##Drop = True; para não criar coluna adicional

#### Removendo os espaços das strings ####
#for i in range( len(df1) ):
#    df1.loc[i,'ID'] = df1.loc[i, 'ID'].strip()
#    df1.loc[i, 'Delivery_person_ID'] = df1.loc[i, 'Delivery_person_ID'].strip()
df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

#### Limpando a coluna time taken ####

df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split('(min) ')[1])
df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )

#===================================================
#Layout no Streamlit
#===================================================

#===================================================
#Barra Lateral
#===================================================


st.header('Marketplace - Visão Clientes')

image_path = 'logoCDS.png'
image = Image.open( image_path )
st.sidebar.image( image, width = 150 )

st.sidebar.markdown( '# Curry Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """---""" )

st.sidebar.markdown( '## Selecione uma data limite' )
date_slider = st.sidebar.slider(
    'Até qual valor',
    value = datetime(2022, 4, 13 ),
    min_value = datetime(2022, 2 , 11),
    max_value = datetime(2022, 4, 6),
    format = 'DD-MM-YYYY' )

st.header(date_slider)
st.sidebar.markdown( """---""" )

traffic_options = st.sidebar.multiselect(
        'Quais as condições de trânsito?',
        ['Low', 'Medium', 'High', 'Jam'],
        default = ['Low', 'Medium', 'High', 'Jam']
        )

st.sidebar.markdown( """---""" )
st.sidebar.markdown( '### Powered by Comunidade DS' )


#Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]


#filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

#st.dataframe(df1)
#===================================================
#Layout no Streamlit
#===================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'] ) 
#------------------------------------
with tab1:
    with st.container():
        #order metric
        #1. Quantidade de pedidos por dia.
        df_aux = df1.loc[:, ['ID', 'Order_Date']].groupby(['Order_Date']).count().reset_index()
        #df_aux
        st.markdown('# Orders by Day')
        #desenhar o gráfico de linhas
        #matplotlib
        #Seaborn
        #Bokeh
        #Plotly
        fig = px.bar(df_aux, x = 'Order_Date', y = 'ID' )
        st.plotly_chart (fig, use_container_width = True) ## MOSTRAR GRÁFICOS

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.header('Traffic Order Share')
            #3. Distribuição dos pedidos por tipo de tráfego.
            df_aux = df1.loc[:, ['ID',      'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
            df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
            df_aux['entregas_perc'] = df_aux['ID']/df_aux['ID'].sum()
            df_aux['entregas_perc'] = round(df_aux['entregas_perc']*100, 2)
            #df_aux.head()
            fig = px.pie(df_aux, values = 'entregas_perc', names = 'Road_traffic_density')
            st.plotly_chart(fig, use_container_width = True)

        with col2:
            st.header('Traffic Order City')
            #4. Comparação do volume de pedidos por cidade e tipo de tráfego.
            #gráfico de bolha
            
            df_aux = df1.loc[: , ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
            df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
            df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
            
            fig = px.scatter(df_aux, x = 'City', y = 'Road_traffic_density', size = 'ID', color = 'City')
            st.plotly_chart(fig, use_container_width = True)

with tab2:
    with st.container():
        st.markdown ( "# Orders by Week ")
        #2. Quantidade de pedidos por semana.
    
        #criar a coluna de semana
        df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
        df_aux = df1.loc[:,['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
        
        fig = px.line(df_aux, x = 'week_of_year', y = 'ID')
        st.plotly_chart(fig, use_container_width = True)

    with st.container():
        #quantidade de pedidos por semana/ número único de entregadores por semana
        df_aux01 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
        df_aux02 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()
        
        df_aux = pd.merge(df_aux01, df_aux02, how = 'inner')
        df_aux['order_by_deliver'] = df_aux['ID']/df_aux['Delivery_person_ID']
        
        fig = px.line (df_aux, x='week_of_year', y = 'order_by_deliver')
        st.plotly_chart(fig, user_container_width = True)



with tab3:
    st.markdown( '# Country Maps' )
    #5. A localização central de cada cidade por tipo de tráfego.
    
    df_aux = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City','Road_traffic_density']).median().reset_index()
    df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
    
    map = folium.Map()
    
    for index, location_info in df_aux.iterrows():
      folium.Marker( [location_info['Delivery_location_latitude'],
                      location_info['Delivery_location_longitude']],
                     popup=location_info[['City', 'Road_traffic_density']] ).add_to(map)
    
    #for index, location_info in df_aux.iterrows():
    #  folium.Marker([df_aux.loc[0, 'Delivery_location_latitude'],
    #                df_aux.loc[0, 'Delivery_location_longitude']]).add_to(map)
    
    folium_static( map, width = 1024 , height = 600 )


























