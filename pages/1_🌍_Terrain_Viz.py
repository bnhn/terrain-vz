import ee
import geemap.foliumap as geemap
import streamlit as st

from gee_auth import terra_auth

st.set_page_config(layout="wide")

st.title("Visualize Country Terrain")
col1, col2 = st.columns([4, 1])

if not ee.data._credentials:
    print("Authenticating")
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

# TO DO: add session state to persist selection

# st.write(st.session_state)
with col2:
    country_selection = st.selectbox("Select a country:", options, index=0)
    basemap = "TERRAIN"

palette = ["#386641", "#6a994e", "#a7c957", "#fdf7d6", "#ffffff"]
palette_a = [
    # "#0052ff",
    # "#7ba6ff",
    "#ff3700",
    "#ff7f59",
    "#F4F5F0",
]
palette_b = ["#07f547","#45c467","#579c69","#9bd1a9","#ffffff"]

with col1:
    m = geemap.Map()
    m.add_basemap(basemap)

    selected_country = countries.filter(ee.Filter.eq("COUNTRY_NA", country_selection))

    m.centerObject(selected_country, 6)

    elevation = ee.Image("USGS/GMTED2010").select("be75").clip(selected_country)

    min_max = elevation.reduceRegion(
        ee.Reducer.minMax(), selected_country, bestEffort=True
    ).getInfo()

    # future update
    # # multidirectional hillshade
    # N = ee.Terrain.hillshade(elevation, 0, 36).multiply(0)
    # NE = ee.Terrain.hillshade(elevation, 45, 44).multiply(0)
    # E = ee.Terrain.hillshade(elevation, 90, 56).multiply(0)
    # SE = ee.Terrain.hillshade(elevation, 135, 68).multiply(0)
    # S = ee.Terrain.hillshade(elevation, 180, 80).multiply(0.1)
    # SW = ee.Terrain.hillshade(elevation, 225, 68).multiply(0.2)
    # W = ee.Terrain.hillshade(elevation, 270, 56).multiply(0.2)
    # NW = ee.Terrain.hillshade(elevation, 315, 44).multiply(0.5)

    # MULTI_HILLSHADE = (
    #     N.add(NE)
    #     .add(E)
    #     .add(SE)
    #     .add(S)
    #     .add(SW)
    #     .add(W)
    #     .add(NW)
    #     .visualize(**{"min": min_max["be75_min"],"max": min_max["be75_max"],"palette": ["000000","ffffff"]})
    #     .resample("bicubic")
    #     .updateMask(0.4)
    # )

    # SLOPE = (
    #     ee.Terrain.slope(elevation)
    #     .multiply(5)
    #     .visualize(**{"min": 100,"max": 180, "palette": ["ffffff","000000"]})
    #     .resample("bicubic")
    #     .updateMask(1)
    # )

    # SHADED_RELIEF = (
    #     ee.ImageCollection([SLOPE, MULTI_HILLSHADE])
    #     .mosaic()
    #     .reduce(ee.Reducer.median())
    #     .updateMask(1)
    # )

    hillshade = ee.Terrain.hillshade(elevation.multiply(2.5))

    elevationVis = {"min": min_max["be75_min"],"max": min_max["be75_max"],"palette": palette,}

    ELEVATION = elevation.visualize(**elevationVis).resample("bilinear").updateMask(1)

    # m.addLayer(SHADED_RELIEF, {}, "Shaded Relief", True)
    m.addLayer(ELEVATION, {}, "Terrain")
    m.addLayer(hillshade.updateMask(0.4), {}, "Hillshade")

    legend_keys = [min_max["be75_min"],min_max["be75_max"]]
    # colorS can be defined using either hex code or RGB (0-255, 0-255, 0-255)
    legend_colors = palette

    m.add_colorbar(elevationVis, label="Elevation (m)")
    m.to_streamlit()
