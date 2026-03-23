import pandas as pd 
import folium
from geopy.geocoders import Nominatim
from geopy.extra.rate.limiter import RateLimiter

# SETUP
file_path = 'https://docs.google.com/spreadsheets/d/1Myzcaf08GQzNApCD_gnoi4e60GlRiWLbCaXVfZiEfoU/edit?gid=874322643#gid=874322643'