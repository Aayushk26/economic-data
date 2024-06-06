import streamlit as st
import investpy
from datetime import datetime, timedelta
import pandas as pd
import pytz

# Function to get economic calendar data
def get_economic_calendar(countries, from_date, to_date):
    try:
        data = investpy.news.economic_calendar(countries=countries, from_date=from_date, to_date=to_date)
        return data
    except Exception as e:
        st.error(f"Error fetching data for {countries}: {e}")
        return None

# Function to convert time to Indian Standard Time (IST) for non-Indian events
def convert_to_ist(time_str, country):
    if country == "India" or pd.isna(time_str):
        return time_str  # Do not convert if the event is already in IST or time_str is NaN
    
    try:
        time_utc = datetime.strptime(time_str, "%H:%M").time()
        utc = pytz.utc.localize(datetime.combine(datetime.today(), time_utc))
        ist = utc.astimezone(pytz.timezone('Asia/Kolkata'))
        return ist.strftime('%H:%M')
    except Exception as e:
        return time_str

# Function to display events
def display_events(events):
    if events is None or events.empty:
        st.write("No upcoming events found.")
        return

    # Convert time to Indian Standard Time (IST) and add the Day column
    events['IST Time'] = events.apply(lambda row: convert_to_ist(row['time'], row['zone']), axis=1)
    events['Day'] = pd.to_datetime(events['date'], format='%d/%m/%Y').dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata').dt.strftime('%A')

    # Remove id column and rename 'zone' column to 'Country'
    events = events.drop(columns=['id']).rename(columns={'zone': 'Country'})

    # Move IST Time and Day columns to the first two positions
    events = events[['IST Time', 'Day'] + [col for col in events.columns if col not in ['IST Time', 'Day']]]

    # Calculate days from today and add as a new column
    events['Days from Today'] = (pd.to_datetime(events['date'], format='%d/%m/%Y') - pd.Timestamp('today')).dt.days

    # Filter out events with None importance
    events = events[events['importance'].notnull()]

    # Style the dataframe based on event importance
    def highlight_importance(val):
        if val == 'high':
            color = 'lightcoral'  # Light red for high importance
        elif val == 'medium':
            color = 'lightblue'
        elif val == 'low':
            color = 'lightgreen'
        else:
            color = ''
        return f'background-color: {color}'

    events_styled = events.style.applymap(highlight_importance, subset=['importance'])

    # Display the legend with subtle colors
    legend_style = "background-color: rgba(240, 240, 240, 0.7); padding: 8px; margin-bottom: 8px;"
    st.markdown(
        "<div style='" + legend_style + "'>"
        "<div style='background-color:lightcoral;padding:8px;margin-bottom:4px;'>High Importance</div>"
        "<div style='background-color:lightblue;padding:8px;margin-bottom:4px;'>Medium Importance</div>"
        "<div style='background-color:lightgreen;padding:8px;margin-bottom:4px;'>Low Importance</div>"
        "</div>",
        unsafe_allow_html=True
    )

    # Display the styled dataframe with larger size
    st.dataframe(events_styled, width=1000, height=600)

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
