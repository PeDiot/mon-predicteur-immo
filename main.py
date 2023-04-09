# to avoid any version conflict: 
# update to python 3.10 https://stackoverflow.com/questions/73530174/streamlit-protocols-cannot-be-instantiated
# pip install --upgrade streamlit==1.0.0
# if needed: pip uninstall NumExpr

# streamlit run main.py returns: 
# Local URL: http://localhost:8501
# Network URL: http://192.168.0.28:8501


import streamlit as st
import pandas as pd
import numpy as np


st.set_page_config(layout="wide")

header = st.container()
dataset = st.container()
features = st.container()
prediction = st.container()
map = st.container()

with header:
    st.title("Business Data Challenge")
    st.markdown("###### This is a web app to forecast real estate prices.")
    st.markdown("## Please provide the following information:")

with features:
    type = st.radio("Select the type of property:", ('House', 'Flat'), key = 'type')
    if type:    
        st.markdown(f"*Encoded Type:* {type}")
        
    street_number = st.number_input("Enter Street Number:", key = 'street_number', step=1, min_value= 1)
    if street_number:
        st.markdown(f"*Encoded Street Number: * {street_number}")
        
    street_name = st.text_input("Enter Street Name: " , key = 'nom_rue')
    if street_name:
        st.write("Encoded Street Name: ", street_name)
        
    zip_code = st.number_input("Enter Zip Code:", key = 'zip_code', step=1, min_value= 1)
    if zip_code and len(str(zip_code)) == 5:
        st.markdown(f"*Encoded Zip Code: * {zip_code}")
    else:
        st.markdown("Please enter a 5 digits zip code")

    surface_terrain = st.slider("Enter a land surface", min_value=0, max_value = 1000, step=10, key = 'land_surface')
    if surface_terrain:
        st.write(f"Encoded Surface: {surface_terrain} m²")
    
    #if format ok:
    #    st.markdown(f"### Encoded adress: {street_number}, {street_name}")
    #else:
    #    st.markdown("### Please check formats")

# store input in a dict:

input_dict = {'type': type, 'street_number': street_number, 'street_name': street_name, 
              'surface_terrain': surface_terrain}

# add lib functions here to get predicted price, mape and other features. 

with prediction: 
    prediction = 100000 # fictive value
    mape = 0.11 # fictive value
    
    st.markdown("## Predicted price of the property:")
    col1, col2 = st.columns(2)

    with col1: 
        st.write(f"#### Predicted price of the property: {prediction} €")
    
    with col2:
        st.write(f"#### MAPE associated {mape}")
    
with map:
    df = pd.DataFrame(np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4], columns=['lat', 'lon'])
    st.map(data=None, zoom=None, use_container_width=True)
    # utiliser folium sinon
