import streamlit as st
import folium
from streamlit_folium import st_folium
from datetime import datetime, date, time
import requests

# Set page config (must be first Streamlit command)
st.set_page_config(page_title="NY Taxi Fare Estimator", page_icon="🚖", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    .big-font {
        font-size:24px !important;
        font-weight: bold;
    }
    .title {
        font-size:32px !important;
        font-weight: bold;
        color: #FF5733;
        text-align: center;
        margin-bottom: 30px;
    }
    .stButton>button {
        background-color: #FF5733;
        color: white;
        font-weight: bold;
        width: 100%;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# App title
st.markdown('<p class="title">NY TAXI FARE PREDICTOR</p>', unsafe_allow_html=True)

# Initialize session state for locations
if 'pickup_coords' not in st.session_state:
    st.session_state.pickup_coords = [40.7128, -74.0060]  # Default NYC
if 'dropoff_coords' not in st.session_state:
    st.session_state.dropoff_coords = [40.7128, -73.9960]  # Slightly east
if 'active_marker' not in st.session_state:
    st.session_state.active_marker = 'pickup'

# Create Folium map
def create_map():
    m = folium.Map(
        location=[40.7128, -74.0060],  # NYC
        zoom_start=12,
        control_scale=True
    )

    # Add pickup marker
    folium.Marker(
        st.session_state.pickup_coords,
        popup="Pickup Location",
        icon=folium.Icon(color="red", icon="car", prefix="fa")
    ).add_to(m)

    # Add dropoff marker
    folium.Marker(
        st.session_state.dropoff_coords,
        popup="Dropoff Location",
        icon=folium.Icon(color="blue", icon="flag", prefix="fa")
    ).add_to(m)

    return m

# Display the map with click handler
map_output = st_folium(
    create_map(),
    width=1200,
    height=500,
    returned_objects=["last_clicked"]
)

# Handle map clicks
if map_output["last_clicked"]:
    clicked_coords = [map_output["last_clicked"]["lat"], map_output["last_clicked"]["lng"]]
    if st.session_state.active_marker == 'pickup':
        st.session_state.pickup_coords = clicked_coords
    else:
        st.session_state.dropoff_coords = clicked_coords

# Marker selection buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("Set Pickup Location", type="primary"):
        st.session_state.active_marker = 'pickup'
with col2:
    if st.button("Set Dropoff Location"):
        st.session_state.active_marker = 'dropoff'

# Display coordinates (read-only)
st.markdown("### Selected Coordinates")
coord_col1, coord_col2 = st.columns(2)
with coord_col1:
    st.markdown('<p class="big-font">Pickup Location</p>', unsafe_allow_html=True)
    st.text_input("Pickup Latitude", value=st.session_state.pickup_coords[0], key="pickup_lat", disabled=True)
    st.text_input("Pickup Longitude", value=st.session_state.pickup_coords[1], key="pickup_lng", disabled=True)

with coord_col2:
    st.markdown('<p class="big-font">Drop-off Location</p>', unsafe_allow_html=True)
    st.text_input("Dropoff Latitude", value=st.session_state.dropoff_coords[0], key="dropoff_lat", disabled=True)
    st.text_input("Dropoff Longitude", value=st.session_state.dropoff_coords[1], key="dropoff_lng", disabled=True)

# Date and time input
st.markdown("### Trip Details")
col_date, col_time = st.columns(2)
with col_date:
    selected_date = st.date_input(
        "Pickup date",
        value=date.today(),
        min_value=date.today()
    )
with col_time:
    selected_time = st.time_input(
        "Pickup time",
        value=time(11, 42, 6)
    )

# Combine date and time
selected_datetime = datetime.combine(selected_date, selected_time)

# Passenger count
passenger_count = st.selectbox("Number of passengers", [1, 2, 3, 4, 5, 6, 7, 8], index=0)

# API URL
url = 'https://taxifare.lewagon.ai/predict'

# Fare estimate button
if st.button("Get Fare Prediction", type="primary"):
    # Prepare API parameters
    params = {
        "pickup_datetime": selected_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        "pickup_longitude": st.session_state.pickup_coords[1],
        "pickup_latitude": st.session_state.pickup_coords[0],
        "dropoff_longitude": st.session_state.dropoff_coords[1],
        "dropoff_latitude": st.session_state.dropoff_coords[0],
        "passenger_count": passenger_count
    }

    try:
        # Make API request
        response = requests.get(url, params=params)
        prediction = response.json().get('fare', 0)

        # Display prediction
        st.success(f"### Predicted Fare: ${prediction:.2f}")






    except :
        st.error(f"Error getting prediction: ")
        st.markdown('''
            **Note:** If you want to use your own API instead of Le Wagon's,
            replace the URL variable with your API endpoint.
            ''')
