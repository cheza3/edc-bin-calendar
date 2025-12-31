#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz

# Your EDC URL
URL = "https://www.eastdunbarton.gov.uk/services/a-z-of-services/bins-waste-and-recycling/bins-and-recycling/collections/?uprn=132020540"

tz = pytz.timezone("Europe/London")

res = requests.get(URL)
res.raise_for_status()

soup = BeautifulSoup(res.text, "html.parser")

cal = Calendar()
cal.add('prodid', '-//EDC Bin Calendar//')
cal.add('version', '2.0')

bins = soup.find_all("div", class_="bin-collection")

for bin_div in bins:
    bin_name_tag = bin_div.find("h3")
    date_tag = bin_div.find("p")
    
    if not bin_name_tag or not date_tag:
        continue
    
    bin_name = bin_name_tag.get_text(strip=True)
    date_str = date_tag.get_text(strip=True)
    
    try:
        date_obj = datetime.strptime(date_str, "%A, %d %B %Y")
        date_obj = tz.localize(date_obj)
    except Exception as e:
        print(f"Skipping invalid date: {date_str}")
        continue
    
    event = Event()
    event.add('summary', f"{bin_name} collection")
    event.add('dtstart', date_obj.date())
    event.add('dtend', date_obj.date() + timedelta(days=1))
    event.add('dtstamp', datetime.now(tz))
    cal.add_component(event)

with open("bins.ics", "wb") as f:
    f.write(cal.to_ical())

print("bins.ics generated successfully!")
