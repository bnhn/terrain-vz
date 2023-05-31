import ee
import streamlit as st
import geemap.foliumap as geemap
from gee_auth import terra_auth

st.set_page_config(
   page_title="Terrain Vz",
   page_icon="🌍",
   layout="wide",
   initial_sidebar_state="expanded",
)

# Customize the sidebar
markdown = """
Find the code on [Github](https://github.com/bnhn/terrain-vz)
"""

st.sidebar.title("About")
st.sidebar.info(markdown)
logo = "https://i.imgur.com/kpKpktZ.png"#"https://i.imgur.com/UbOXYAU.png"
st.sidebar.image(logo)

# Customize page title
st.title("Terrain Viz")

st.markdown(
    """
    
    """
)

if not ee.data._credentials:
     terra_auth()    
else:
    print("already authenticated")
    # ee.Initialize()

m = geemap.Map()
m.add_basemap("Stamen.TonerBackground")
m.to_streamlit(height=500)