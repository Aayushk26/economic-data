import streamlit as st
import investpy
from datetime import datetime, timedelta
import pandas as pd

# Function to get economic calendar data
def get_economic_calendar(countries, from_date, to_date):
    try:
        data = investpy.news.economic_calendar(countries=countries, from_date=from_date, to_date=to_date)
        return data
    except Exception as e:
        st.error(f"Error fetching data for {countries}: {e}")
        return None

# Function to display events
def display_events(events):
    if events is None:
        st.write("No upcoming events found.")
        return

    if not events.empty:
        st.write("Upcoming Events:")
        st.dataframe(events)
    else:
        st.write("No upcoming events found.")

# Main function to run the Streamlit app
def main():
    st.title("Economic Calendar")

    # Manually list available countries
    available_countries = [
        "United States", "India", "Australia", "Brazil", "Canada", "China", "France",
        "Germany", "Italy", "Japan", "Mexico", "Russia", "South Korea", "Spain", 
        "Switzerland", "United Kingdom"
    ]
    
    countries = st.multiselect("Select countries:", available_countries, default=["United States", "India"])

    # Date range selection
    date_ranges = {
        "7 days from today": 7,
        "14 days from today": 14,
        "1 month from today": 30,
    }
    selected_range = st.selectbox("Select date range:", list(date_ranges.keys()), index=1)
    max_days = date_ranges[selected_range]
    today = datetime.today().strftime('%d/%m/%Y')
    to_date = (datetime.today() + timedelta(days=max_days)).strftime('%d/%m/%Y')

    # Fetch and display economic calendar data
    if countries:
        data = get_economic_calendar(countries, today, to_date)
        display_events(data)

if __name__ == "__main__":
    main()
