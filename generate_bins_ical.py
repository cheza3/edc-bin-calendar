#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz
import re

URL = "https://www.eastdunbarton.gov.uk/services/a-z-of-services/bins-waste-and-recycling/bins-and-recycling/collections/?uprn=132020540"
tz = pytz.timezone("Europe/London")

cal = Calendar()
cal.add('prodid', '-//EDC Bin Calendar//')
cal.add('version', '2.0')

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL)
    
    # Wait for JS to render the collection dates
    page.wait_for_timeout(5000)  # 5 seconds should be enough
    
    # Grab all text in the main content area
    text = page.inner_text("main")
    browser.close()

# Parse each line that ends with weekday + date
for line in text.splitlines():
    line = line.strip()
    match = re.search(r"(.+?)\s+(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+(\d{2}\s+\w+\s+\d{4})", line)
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

# Write ICS
with open("bins.ics", "wb") as f:
    f.write(cal.to_ical())

print("bins.ics generated successfully!")
