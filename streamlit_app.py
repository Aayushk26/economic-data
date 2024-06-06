import streamlit as st
import investpy
from datetime import datetime, timedelta
import schedule
import time
import threading
import smtplib
from email.mime.text import MIMEText
import pandas as pd

# Function to get economic calendar data
def get_economic_calendar(countries, from_date, to_date):
    try:
        data = investpy.news.economic_calendar(countries=countries, from_date=from_date, to_date=to_date)
        return data
    except Exception as e:
        st.error(f"Error fetching data for {countries}: {e}")
        return None

# Function to filter events occurring within the next two weeks
def filter_upcoming_events(data):
    upcoming_events = []
    today = datetime.today()
    two_weeks_from_now = today + timedelta(weeks=2)

    for index, row in data.iterrows():
        event_date = datetime.strptime(row['date'], '%d/%m/%Y')
        if today <= event_date <= two_weeks_from_now:
            upcoming_events.append(row)
    
    return upcoming_events

# Function to display events
def display_events(events):
    if not events:
        st.write("No upcoming events found.")
        return

    # Create a DataFrame to store the events
    df = pd.DataFrame(events, columns=['Event', 'Date', 'Country'])

    # Calculate days from today
    today = datetime.today()
    df['Days from Today'] = (pd.to_datetime(df['Date'], format='%d/%m/%Y') - today).dt.days

    st.write("Upcoming Events:")
    st.dataframe(df)

# Function to send notification emails
def send_notification(event, email_list):
    subject = f"Reminder: Upcoming event '{event['Event']}'"
    body = f"Upcoming event '{event['Event']}' on {event['Date']} in {event['Country']}."
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = "your_email@example.com"
    msg['To'] = ", ".join(email_list)

    try:
        with smtplib.SMTP('smtp.example.com', 587) as server:
            server.starttls()
            server.login("your_email@example.com", "your_password")
            server.sendmail("your_email@example.com", email_list, msg.as_string())
            st.write(f"🔔 Email notification sent for event '{event['Event']}' on {event['Date']}")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

# Function to schedule notifications
def schedule_notifications(events, email_list):
    for event in events:
        event_date = datetime.strptime(event['Date'], '%d/%m/%Y')
        notification_time = event_date - timedelta(weeks=2)
        schedule_time = datetime.combine(notification_time, datetime.min.time()) + timedelta(hours=9)

        if schedule_time > datetime.now():
            schedule.every().day.at("09:00").do(send_notification, event, email_list)

# Function to run the scheduler
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Main function to run the Streamlit app
def main():
    st.title("Economic Calendar Notifications")

    # Manually list available countries
    available_countries = [
        "United States", "India", "Australia", "Brazil", "Canada", "China", "France",
        "Germany", "Italy", "Japan", "Mexico", "Russia", "South Korea", "Spain", 
        "Switzerland", "United Kingdom"
    ]
    
    countries = st.multiselect("Select countries:", available_countries, default=["United States", "India"])

    # Date range selection
    date_ranges = {
        "1 Week from Today": 7,
        "2 Weeks from Today": 14,
        "1 Month from Today": 30,
        "2 Months from Today": 60
    }
    selected_ranges = st.multiselect("Select date ranges:", list(date_ranges.keys()), default=["2 Weeks from Today"])
    max_days = max([date_ranges[range] for range in selected_ranges], default=0)

    # User input for email addresses
    email_list = st.text_area("Enter email addresses (comma-separated):").split(',')
    email_list = [email.strip() for email in email_list if email.strip()]

    # Fetch and display economic calendar data
    if countries and max_days > 0:
        today = datetime.today()
        from_date = today.strftime('%d/%m/%Y')
        to_date = (today + timedelta(days=max_days)).strftime('%d/%m/%Y')

        all_events = []
        data = get_economic_calendar(countries, from_date, to_date)
        if data is not None:
            upcoming_events = filter_upcoming_events(data)
            all_events.extend(upcoming_events)

        if all_events:
            display_events(all_events)
            schedule_notifications(all_events, email_list)
            
            # Start the scheduler in a separate thread
            scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
            scheduler_thread.start()
        else:
            st.write("No upcoming events found for the selected criteria.")

if __name__ == "__main__":
    main()
