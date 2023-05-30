import ee
import geemap.foliumap as geemap
import geopandas as gpd
import streamlit as st
import json
import os

from gee_auth import terra_auth

st.set_page_config(layout="wide")

st.title("Visualize Country Terrain")
col1, col2 = st.columns([4, 1])

if not ee.data._credentials:
     terra_auth()    
else:
        print("already authenticated")
        # ee.Initialize()

def get_country_names(fc, property):
    """
    Funtion returns a all values of a specified property in a earth engine feature collection

    Args:
        fc (ee.featurecollection.FeatureCollection): Earth Engine Feature Collection
        property (str): Property of values to be returned

    Returns:
        list: values returned
    """
    country_names = fc.aggregate_array(property)
    return country_names.getInfo()

@st.cache_data
def sort_country_names(country_names):
    """Returns a sorted list of countries with disputed regions filtered out

    Args:
        country_names (list): list of country names obtained from LSIB 2017
        (https://developers.google.com/earth-engine/datasets/catalog/USDOS_LSIB_2017)

    Returns:
        list: country names (str)
    """
    undisputed = list(filter(lambda x: "(disp)" not in x, country_names))
    return sorted(undisputed)

countries = ee.FeatureCollection("USDOS/LSIB/2017")
options = sort_country_names(get_country_names(countries, "COUNTRY_NA"))

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
        "palette": ["#0052ff",
                    "#7ba6ff",
                    "#F4F5F0",
                    "#ff3700",
                    "#ff7f59",
                    ],
    }

    styleParams = {
        "fillColor": "b5ffb4",
        "color": "00909F",
        "width": 1.0,
    }

    countries = countries.style(**styleParams)

    # m.addLayer(selected_country, {}, country_selection)
    m.addLayer(elevation, elevationVis, "Terrain")

    m.to_streamlit()