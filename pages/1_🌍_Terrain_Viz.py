import ee
import geemap.foliumap as geemap
import geopandas as gpd
import streamlit as st

st.set_page_config(layout="wide")

if not ee.data._credentials:
    print("authenticating")
    service_account = st.secrets.sa_credentials.email
    credentials = ee.ServiceAccountCredentials(
        service_account, st.secrets.sa_credentials.credentials
    )
    ee.Initialize(credentials=credentials)

else:
    print("already authenticated")
    # ee.Initialize()

st.title("Visualize Country Terrain")

col1, col2 = st.columns([4, 1])


@st.cache_data
def get_country_names(url):
    countries_gdf = gpd.read_file(url)
    return countries_gdf["NAME"].sort_values().to_numpy()


options = get_country_names(geemap.examples.datasets.countries_geojson)

with col2:
    country_selection = st.selectbox("Select a country:", options, index=0)
    basemap = "TERRAIN"


with col1:
    m = geemap.Map()
    m.add_basemap(basemap)

    countries = ee.FeatureCollection("FAO/GAUL/2015/level0")
    selected_country = countries.filter(ee.Filter.eq("ADM0_NAME", country_selection))

    m.centerObject(selected_country, 6)

    elevation = ee.Image("USGS/GMTED2010").select("be75").clip(selected_country)

    min_max = elevation.reduceRegion(ee.Reducer.minMax(),selected_country, bestEffort=True).getInfo()
    elevationVis = {
    'min': min_max["be75_min"],
    'max': min_max["be75_max"],
    # 'gamma': 3.5,
    'palette':['#0052ff','#7ba6ff', '#ff7f59', '#ff3700','#F4F5F0'],
    }

    styleParams = {
        "fillColor": "b5ffb4",
        "color": "00909F",
        "width": 1.0,
    }

    countries = countries.style(**styleParams)

    m.addLayer(selected_country, {}, country_selection)
    m.addLayer(elevation,elevationVis,"Terrain")
    m.to_streamlit()
