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
    .marker-control {
        position: absolute;
        top: 10px;
        right: 10px;
        z-index: 1000;
        background: white;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0 0 10px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# App title
st.markdown('<p class="title">NY TAXI FARE PREDICTOR</p>', unsafe_allow_html=True)

# Initialize session state for all variables
if 'pickup_coords' not in st.session_state:
    st.session_state.pickup_coords = [40.7128, -74.0060]  # Default NYC
if 'dropoff_coords' not in st.session_state:
    st.session_state.dropoff_coords = [40.7128, -73.9960]  # Slightly east
if 'active_marker' not in st.session_state:
    st.session_state.active_marker = 'pickup'
if 'show_prediction' not in st.session_state:
    st.session_state.show_prediction = False
if 'prediction_result' not in st.session_state:
    st.session_state.prediction_result = None

# Create Folium map with custom controls
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

    # Add route if prediction exists
    if st.session_state.show_prediction and st.session_state.prediction_result:
        folium.PolyLine(
            locations=[st.session_state.pickup_coords, st.session_state.dropoff_coords],
            color="green",
            weight=5,
            opacity=0.7
        ).add_to(m)

    # Add custom HTML for marker control
    marker_control = f"""
    <div class="marker-control">
        <button onclick="setActiveMarker('pickup')"
                style="background-color: {'#FF5733' if st.session_state.active_marker == 'pickup' else '#ccc'};
                       color: white; border: none; padding: 5px 10px; margin-right: 5px; border-radius: 3px;">
            Set Pickup
        </button>
        <button onclick="setActiveMarker('dropoff')"
                style="background-color: {'#4287f5' if st.session_state.active_marker == 'dropoff' else '#ccc'};
                       color: white; border: none; padding: 5px 10px; border-radius: 3px;">
            Set Dropoff
        </button>
    </div>
    <script>
    function setActiveMarker(type) {{
        parent.window.postMessage({{type: 'setActiveMarker', markerType: type}}, '*');
    }}
    </script>
    """
    m.get_root().html.add_child(folium.Element(marker_control))

    return m

# Display the map
map_data = st_folium(
    create_map(),
    width=1200,
    height=500,
    returned_objects=["last_clicked"]
)

# Handle map clicks and marker changes
if map_data.get("last_clicked"):
    clicked_coords = [map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]]
    if st.session_state.active_marker == 'pickup':
        st.session_state.pickup_coords = clicked_coords
    else:
        st.session_state.dropoff_coords = clicked_coords
    st.session_state.show_prediction = False  # Reset prediction when locations change
    st.experimental_rerun()

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
        st.session_state.prediction_result = response.json().get('fare', 0)
        st.session_state.show_prediction = True
        st.experimental_rerun()

    except Exception as e:
        st.error(f"Error getting prediction: {e}")
        st.session_state.show_prediction = False
        st.markdown('''
            **Note:** If you want to use your own API instead of Le Wagon's,
            replace the URL variable with your API endpoint.
            ''')

# Display prediction if available
if st.session_state.show_prediction and st.session_state.prediction_result is not None:
    st.success(f"### Predicted Fare: ${st.session_state.prediction_result:.2f}")

    # Show map with route
    m = folium.Map(
        location=[40.7128, -74.0060],
        zoom_start=12,
        control_scale=True
    )

    # Add markers
    folium.Marker(
        st.session_state.pickup_coords,
        popup="Pickup Location",
        icon=folium.Icon(color="red", icon="car", prefix="fa")
    ).add_to(m)

    folium.Marker(
        st.session_state.dropoff_coords,
        popup="Dropoff Location",
        icon=folium.Icon(color="blue", icon="flag", prefix="fa")
    ).add_to(m)

    # Add route line
    folium.PolyLine(
        locations=[st.session_state.pickup_coords, st.session_state.dropoff_coords],
        color="green",
        weight=5,
        opacity=0.7
    ).add_to(m)

    st_folium(m, width=1200, height=500)
