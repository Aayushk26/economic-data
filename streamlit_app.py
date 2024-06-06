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

# Function to display events
def display_events(events):
    if not events:
        st.write("No upcoming events found.")
        return

    # Create a DataFrame to store the events
    df = pd.DataFrame(events)

    st.write("Upcoming Events:")
    st.dataframe(df)

# Function to send notification emails
def send_notification(event, email_list):
    subject = f"Reminder: Upcoming event '{event['event']}'"
    body = f"Upcoming event '{event['event']}' on {event['date']} in {event['country']}."
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = "your_email@example.com"
    msg['To'] = ", ".join(email_list)

    try:
        with smtplib.SMTP('smtp.example.com', 587) as server:
            server.starttls()
            server.login("your_email@example.com", "your_password")
            server.sendmail("your_email@example.com", email_list, msg.as_string())
            st.write(f"🔔 Email notification sent for event '{event['event']}' on {event['date']}")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

# Function to schedule notifications
def schedule_notifications(events, email_list):
    for event in events:
        event_date = datetime.strptime(event['date'], '%d/%m/%Y')
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
    today = datetime.today().strftime('%d/%m/%Y')
    to_date = (datetime.today() + timedelta(weeks=2)).strftime('%d/%m/%Y')

    # Fetch and display economic calendar data
    if countries:
        data = get_economic_calendar(countries, today, to_date)
        if data is not None:
            display_events(data)
            # No need to schedule notifications as we don't have specific times in this data

if __name__ == "__main__":
    main()
