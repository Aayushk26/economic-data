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

# Function to convert time to Indian Standard Time (IST)
def convert_to_ist(time_str):
    try:
        time_utc = datetime.strptime(time_str, "%H:%M").time()
        utc = pytz.utc.localize(datetime.combine(datetime.today(), time_utc))
        ist = utc.astimezone(pytz.timezone('Asia/Kolkata'))
        return ist.strftime('%H:%M')
    except Exception as e:
        return time_str

# Function to display events
def display_events(events):
    if events is None:
        st.write("No upcoming events found.")
        return

    if not events.empty:
        # Convert time to Indian Standard Time (IST) and rename column
        events['IST Time'] = events['time'].apply(convert_to_ist)

        # Add a column for the day of the event with respect to IST
        events['Day'] = pd.to_datetime(events['date'], format='%d/%m/%Y').dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata').dt.strftime('%A')

        # Remove id column
        events = events.drop(columns=['id'])

        # Rename 'zone' column to the corresponding country
        events = events.rename(columns={'zone': 'Country'})

        # Move IST Time and Day columns to the first two positions
        events = events[['IST Time', 'Day'] + [col for col in events.columns if col not in ['IST Time', 'Day']]]

        # Style the dataframe based on event importance
        def highlight_importance(val):
            if val == 'high':
                color = 'lightgreen'
            elif val == 'medium':
                color = 'lightblue'
            elif val == 'low':
                color = 'lightyellow'
            else:
                color = ''
            return f'background-color: {color}'

        events_styled = events.style.applymap(highlight_importance, subset=['importance'])

        # Display the legend
        st.markdown(
            "<div style='background-color:lightgreen;padding:8px;margin-bottom:8px;'>High Importance</div>"
            "<div style='background-color:lightblue;padding:8px;margin-bottom:8px;'>Medium Importance</div>"
            "<div style='background-color:lightyellow;padding:8px;margin-bottom:8px;'>Low Importance</div>",
            unsafe_allow_html=True
        )

        # Display the styled dataframe
        st.dataframe(events_styled, width=0)

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
