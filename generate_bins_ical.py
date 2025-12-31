from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz

URL = "https://www.eastdunbarton.gov.uk/services/a-z-of-services/bins-waste-and-recycling/bins-and-recycling/collections/?uprn=132020540"

tz = pytz.timezone("Europe/London")

options = Options()
options.headless = True
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)

driver.get(URL)

# Wait a few seconds if needed for JS to load
driver.implicitly_wait(5)

# Find the collection table
# Example: get all rows in table (update the selector to match page)
rows = driver.find_elements("css selector", "div.collection-table__row")

cal = Calendar()
cal.add('prodid', '-//EDC Bin Calendar//')
cal.add('version', '2.0')

for row in rows:
    try:
        bin_name = row.find_element("css selector", "div.collection-table__bin").text
        date_str = row.find_element("css selector", "div.collection-table__date").text
        date_obj = datetime.strptime(date_str, "%A, %d %B %Y")
        date_obj = tz.localize(date_obj)
        
        event = Event()
        event.add('summary', f"{bin_name} collection")
        event.add('dtstart', date_obj.date())
        event.add('dtend', date_obj.date() + timedelta(days=1))
        event.add('dtstamp', datetime.now(tz))
        event.add('url', URL)
        cal.add_component(event)
    except Exception as e:
        print("Skipping row:", e)

with open("bins.ics", "wb") as f:
    f.write(cal.to_ical())

driver.quit()
print("bins.ics generated successfully!")
