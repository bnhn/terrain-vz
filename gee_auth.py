import ee
import streamlit as st
import json 
import os

@st.cache_resource
def terra_auth():
    """
    Earth Engine authentication flow
    """
    with open(st.secrets["cred_path"], "w") as file:
        json.dump(dict(**st.secrets["EARTH_ENGINE_CREDENTIALS"]), file)

    credentials = ee.ServiceAccountCredentials(st.secrets["sa_email"], st.secrets["cred_path"])
    ee.Initialize(credentials=credentials)

    with open(os.environ["cred_path"], "w") as file:
        json.dump(dict(), file)
