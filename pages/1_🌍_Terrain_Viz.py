import ee
import geemap.foliumap as geemap
import geopandas as gpd
import streamlit as st
import json
import os

st.set_page_config(layout="wide")

st.title("Visualize Country Terrain")
col1, col2 = st.columns([4, 1])

@st.cache_resource
def terra_auth():
        with open(st.secrets["cred_path"], "w") as file:
            json.dump(dict(**st.secrets["EARTH_ENGINE_CREDENTIALS"]), file)

        credentials = ee.ServiceAccountCredentials(st.secrets["sa_email"], st.secrets["cred_path"])
        ee.Initialize(credentials=credentials)

        with open(os.environ["cred_path"], "w") as file:
            json.dump(dict(), file)

if not ee.data._credentials:
     terra_auth()    
else:
        print("already authenticated")
        # ee.Initialize()

@st.cache_data
def get_country_names(fc):
    country_names = fc.aggregate_array("COUNTRY_NA")
    return country_names.getInfo()

countries = ee.FeatureCollection("USDOS/LSIB/2017")
options = get_country_names(countries)

with col2:
    country_selection = st.selectbox("Select a country:", options, index=0)
    basemap = "TERRAIN"


with col1:
    m = geemap.Map()
    m.add_basemap(basemap)
    
    selected_country = countries.filter(ee.Filter.eq("COUNTRY_NA", country_selection))

    m.centerObject(selected_country, 6)

    elevation = ee.Image("USGS/GMTED2010").select("be75").clip(selected_country)

    min_max = elevation.reduceRegion(
        ee.Reducer.minMax(), selected_country, bestEffort=True
    ).getInfo()
    elevationVis = {
        "min": min_max["be75_min"],
        "max": min_max["be75_max"],
        # 'gamma': 3.5,
        "palette": ["#0052ff", "#7ba6ff", "#ff7f59", "#ff3700", "#F4F5F0"],
    }

    styleParams = {
        "fillColor": "b5ffb4",
        "color": "00909F",
        "width": 1.0,
    }

    countries = countries.style(**styleParams)

    m.addLayer(selected_country, {}, country_selection)
    m.addLayer(elevation, elevationVis, "Terrain")

    m.to_streamlit()