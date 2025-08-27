import streamlit as st
import requests
import pandas as pd
import os
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="IP & Location Tracker", page_icon="🌍")

st.title("🌍 Your IP Address and Location")

st.write("We automatically detected your IP and location:")

try:
    # Fetch IP and location using ipinfo.io
    response = requests.get("https://ipinfo.io/json")
    data = response.json()

    ip = data.get("ip", "Unknown")
    city = data.get("city", "Unknown")
    region = data.get("region", "Unknown")
    country = data.get("country", "Unknown")
    loc = data.get("loc", "Unknown")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # -------------------------
    # Display only to the visitor
    # -------------------------
    st.success("Here are your details:")
    st.write(f"**IP Address:** {ip}")
    st.write(f"**City:** {city}")
    st.write(f"**Region:** {region}")
    st.write(f"**Country:** {country}")
    st.write(f"**Coordinates:** {loc}")
    st.write(f"**Time:** {timestamp}")

    if loc != "Unknown":
        lat, lon = map(float, loc.split(","))
        st.map({"lat": [lat], "lon": [lon]})

    # -------------------------
    # Log silently in the background
    # -------------------------
    # Local CSV log
    filename = "visitors_log.csv"
    new_entry = pd.DataFrame([{
        "Timestamp": timestamp,
        "IP": ip,
        "City": city,
        "Region": region,
        "Country": country,
        "Coordinates": loc
    }])

    if os.path.exists(filename):
        df = pd.read_csv(filename)
        df = pd.concat([df, new_entry], ignore_index=True)
    else:
        df = new_entry

    df.to_csv(filename, index=False)

    # Google Sheets log
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open("Visitor_Logs").sheet1
    sheet.append_row([timestamp, ip, city, region, country, loc])

except Exception as e:
    st.error("Could not fetch location details.")
