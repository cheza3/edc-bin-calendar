#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz
import re
import time

# EDC bin collection URL
URL = "https://www.eastdunbarton.gov.uk/services/a-z-of-services/bins-waste-and-recycling/bins-and-recycling/collections/?uprn=132020540"

tz = pytz.timezone("Europe/London")

# Selenium Chrome setup
options = Options()
options.headless = True
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.binary_location = "/usr/bin/google-chrome"  # official Chrome binary

driver = webdriver.Chrome(options=options)
driver.get(URL)
time.sleep(5)  # wait for JS content to load

# Create iCalendar
cal = Calendar()
cal.add('prodid', '-//EDC Bin Calendar//')
cal.add('version', '2.0')

# Extract <p> elements in main content
elements = driver.find_elements("css selector", "div#content p")

for el in elements:
    text = el.text.strip()
    # Match lines ending with weekday + date
    match = re.search(r"(.+?)\s+(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+(\d{2}\s+\w+\s+\d{4})$", text)
    if match:
        bin_name = match.group(1).strip()
        date_str = f"{match.group(2)}, {match.group(3)}"
        try:
            date_obj = datetime.strptime(date_str, "%A, %d %B %Y")
            date_obj = tz.localize(date_obj)
        except Exception as e:
            print(f"Skipping invalid date '{date_str}': {e}")
            continue

        event = Event()
        event.add('summary', f"{bin_name} collection")
        event.add('dtstart', date_obj.date())
        event.add('dtend', date_obj.date() + timedelta(days=1))
        event.add('dtstamp', datetime.now(tz))
        event.add('url', URL)
        cal.add_component(event)

# Write to bins.ics
with open("bins.ics", "wb") as f:
    f.write(cal.to_ical())

driver.quit()
print("bins.ics generated successfully!")
