import streamlit as st
import leafmap.foliumap as leafmap
import leafmap.kepler as leafmap_kep
st.set_page_config(layout="wide")

# Customize the sidebar
markdown = """
Find the code on [Github](https://github.com/bnhn/terrain-vz)
"""

st.sidebar.title("About")
st.sidebar.info(markdown)
logo = "https://i.imgur.com/UbOXYAU.png"
st.sidebar.image(logo)

# Customize page title
st.title("Rayy Benhin's Portfolio")

st.markdown(
    """
    Work In Progress
    """
)

m = leafmap.Map(minimap_control=True)
m.add_basemap("OpenTopoMap")
m.to_streamlit(height=500)