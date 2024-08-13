import streamlit as st
import pandas as pd
import requests
import os
import time
import json

API_URL = os.getenv("API_URL", "http://fastapi:8000")

# Function to fetch data from API with retry mechanism
@st.cache_data
def fetch_data_with_retry(endpoint, params=None, max_retries=5, delay=1):
    for attempt in range(max_retries):
        try:
            if endpoint == "devices" and params:
                params = {"filters": json.dumps(params)}
            response = requests.get(f"{API_URL}/{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                st.error(f"Failed to connect to the API after {max_retries} attempts. Please try again later.")
                st.stop()
            else:
                time.sleep(delay)
                delay *= 2  # Exponential backoff

# Fetch keys and their unique values
keys_and_values = fetch_data_with_retry("keys_and_values")

# Create dynamic filters
st.sidebar.title("Filters")
filters = {}
for key, values in keys_and_values.items():
    if len(values) > 1:  # Only for keys with more than one unique value
        filters[key] = st.sidebar.selectbox(f'Select {key}', ['All'] + sorted(values))

# Prepare parameters for API query
params = {k: v for k, v in filters.items() if v != 'All'}

# Fetch filtered data
devices = fetch_data_with_retry("devices", params=params)

# Display data
st.title("Device Filter Application")
st.write(f"Showing {len(devices)} devices")
df = pd.DataFrame(devices)

# Display table
st.dataframe(df)

# Add selectbox to choose a device
selected_hostname = st.selectbox("Select a device to see details", df['hostname'].tolist())

# Display details of the selected device
if selected_hostname:
    selected_device = df[df['hostname'] == selected_hostname].iloc[0]
    st.subheader(f"Details for {selected_hostname}")
    st.json(selected_device.to_dict())

st.info("Use the dropdown menu above to select a device and see its details.")