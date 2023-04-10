import folium
import streamlit as st
from streamlit_folium import folium_static

import numpy as np 

from lib.inference import Prediction
from lib.enums import AVAILABLE_GEO_AREAS, AVAILABLE_GEO_AREAS_COORDS

# Functions

def format_zip_code(zip_code: str) -> int: 
    """Description. Format zip code to correct format."""

    if zip_code.startswith("0"): 
        zip_code = zip_code[1:]
    
    return int(zip_code)

@st.cache_data 
def generate_geo_areas_map():
    """Description. Generate a map with all available geo areas and add to cache."""    

    map = folium.Map(location=[46.2276, 2.2137], zoom_start=6)

    for geo_area, coords in AVAILABLE_GEO_AREAS_COORDS.items():
            
            msg = f"{geo_area.capitalize()} : "

            if geo_area in AVAILABLE_GEO_AREAS["flats"] and geo_area in AVAILABLE_GEO_AREAS["houses"]:
                msg += "Appartements & Maisons"
                color = "blue"

            elif geo_area in AVAILABLE_GEO_AREAS["flats"]:
                msg += "Appartements"
                color = "green"

            elif geo_area in AVAILABLE_GEO_AREAS["houses"]:
                msg += "Maisons"
                color = "orange"
    
            # add a marker on the map
            folium.Marker(
                location=coords,
                popup=msg,
                icon=folium.Icon(color=color, icon="info-sign")
            ).add_to(map)

    folium_static(map, width=725, height=600)

# Set title and caption 

APP_TITLE = "Mon Prédicteur Immo"
ICON = ":house_with_garden:"
APP_CAPTION = "Estimez le prix de votre bien immobilier en quelques clics à l'aide de notre modèle de Machine Learning."

st.set_page_config(page_title=APP_TITLE, page_icon=ICON)

st.title(f"{ICON} {APP_TITLE}")
st.caption(APP_CAPTION)

# Sidebar with user input widgets & contact information

st.sidebar.title("Pouvez-vous décrire votre bien ?")

columns = st.sidebar.columns(2)

with columns[0]:
    property_type = st.selectbox("Type de Bien", ["Appartement", "Maison"], index=0)
    num_rooms = st.number_input("Nombre de Pièces", min_value=1, value=2)
    surface = st.number_input("Surface (m²)", min_value=0, value=30)
    field_surface = st.number_input("Surface du Terrain (m²)", min_value=0, value=0)
    dependance = st.selectbox("Dépendance", ["Oui", "Non"], index=1)

with columns[1]:
    street_number = st.number_input("Numéro de Rue", min_value=0, value=11)
    street_name = st.text_input("Nom de Rue", value="Rue des Halles")
    zip_code = st.text_input("Code Postal", value="75001")
    city = st.text_input("Ville", value="Paris")

st.sidebar.markdown("")
st.sidebar.markdown("")
check_prediction_widget = st.sidebar.button("Estimer mon bien !")

for _ in range(7):
    st.sidebar.markdown("")

authors = ["**[Florentin](https://github.com/FlorentinLavaud)**", "**[Pierre-Emmanuel](https://github.com/PeDiot)**"]
authors = " & ".join(authors)
st.sidebar.markdown(f"**Contact** : {authors}")

# Display map of available geographical areas 

if not check_prediction_widget:

    st.markdown("")
    st.subheader("Les zones géographiques disponibles")

    map = generate_geo_areas_map()
    # st.pydeck_chart(map)

# Use inputs to predict the price of the real estate

if check_prediction_widget:

    # Create a dictionary with user input
    user_args = {
        "property_type": "houses" if property_type == "Maison" else "flats",
        "street_number": street_number,
        "street_name":  street_name,
        "zip_code": format_zip_code(zip_code),
        "city" : city,
        "num_rooms": num_rooms,
        "surface": surface,
        "field_surface": field_surface,
        "dependance": 1. if dependance == "Oui" else 0.
    }

    # Create a Prediction object with user input
    prediction = Prediction(user_args)

    if prediction.geo_area is None:
        st.warning("L'outil de prédiction ne couvre pas encore cette zone.")

    else: 

        # Load data and model
        prediction.load_data(data_dir="./data/")
        prediction.load_model(model_dir="./backup/models/")

        if prediction.model_loader is None:
            st.warning("L'outil de prédiction ne couvre pas encore cette zone.")

        else:
            # Predict the price
            pred_price = prediction.predict()

            # Display predicted price and model error
            st.subheader("Notre estimation")
            st.caption("L'estimation est basée sur les données de vente de biens similaires dans votre zone géographique.")
            
            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    label="Prix estimé :moneybag:",
                    value=f"{int(pred_price):,}€"
                )

            with col2: 
                mape = prediction.fecth_mape()   
                st.metric(  
                    label="Marge d'erreur:chart_with_upwards_trend:",
                    value=f"{round(100 * mape, 2)}%"
                )

            n_close_properties = len(prediction.close_properties)
            
            # Display map with close properties and user property
            if n_close_properties > 0:

                median_price = prediction.close_properties.valeur_fonciere.median()

                st.subheader("Près de chez vous")
                st.caption(f"Les {property_type.lower()}s les plus proches de votre bien présents dans notre base de données. **Le prix médian est de {int(median_price):,}€**.")
            
                user_location = [
                    prediction.user_args["latitude"], prediction.user_args["longitude"]
                ]
                

                map = folium.Map(
                    location=user_location, 
                    zoom_start=13
                )

                folium.Marker(
                    location=user_location,
                    popup=f"Votre bien estimé à {int(pred_price):,}€ (2023)",
                    icon=folium.Icon(color="black", icon="home")
                ).add_to(map)

                if len(prediction.close_properties) > 20: 
                    prediction.close_properties = prediction.close_properties.sample(20)

                for _, row in prediction.close_properties.iterrows():
                    surface = np.exp(row["l_surface_reelle_bati"])
                    year = row.date_mutation.split("-")[0]
                    label = f"{int(surface):,} m² à {int(row.valeur_fonciere):,}€ ({year})"

                    folium.Marker(
                        location=[row["latitude"], row["longitude"]],
                        popup=label,
                        icon=folium.Icon(color="blue", icon="info-sign")
                    ).add_to(map)

                folium_static(map, width=725, height=400)

