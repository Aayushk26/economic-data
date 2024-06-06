import streamlit as st
import investpy
from datetime import datetime, timedelta
import schedule
import time
import threading
import smtplib
from email.mime.text import MIMEText

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
    for event in events:
        st.write(f"Event: {event['event']}, Date: {event['date']}, Country: {event['country']}")

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

    # Country selection
    available_countries = investpy.news.economic_calendar_countries()
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
