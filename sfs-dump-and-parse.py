import os
from datetime import datetime, timedelta
import time
import requests
import json
import pytz
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set the log level to INFO
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format with timestamp, log level, and message
    handlers=[
        logging.FileHandler("daily_concert_sync.log"),  # Append logs to a file named 'daily_concert_sync.log'
        logging.StreamHandler()  # Also log to console
    ]
)

# Calculate the current timestamp and the timestamp 3 months from now
current_date = datetime.now()
three_months_later = current_date + timedelta(days=90)  # Roughly 3 months

current_timestamp = int(time.mktime(current_date.timetuple()))
three_months_later_timestamp = int(time.mktime(three_months_later.timetuple()))

# The URL for the API request
url = "https://3zvewsxvk4-dsn.algolia.net/1/indexes/*/queries"

# Headers copied from the network tab
headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/x-www-form-urlencoded",
    "x-algolia-agent": "Algolia for JavaScript (4.5.1); Browser (lite); instantsearch.js (4.8.3); JS Helper (3.2.2)",
    "x-algolia-api-key": "e6c0617a0995d310c9dd600df5af93c2",
    "x-algolia-application-id": "3ZVEWSXVK4",
    "origin": "https://www.sfsymphony.org",
    "referer": "https://www.sfsymphony.org/",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}

# Update the payload to use the dynamic timestamps for 3 months range
payload = {
    "requests": [
        {
            "indexName": "prod_sfs_calendar",
            "params": f"hitsPerPage=30&facetFilters=%5B%5B%22excludeFromCalendar%3Afalse%22%5D%5D&query=&highlightPreTag=__ais-highlight__&highlightPostTag=__%2Fais-highlight__&maxValuesPerFacet=10000&page=0&facets=%5B%22startDate%22%2C%22composers%22%2C%22artists%22%2C%22conductors%22%2C%22Concert%20Type%22%5D&tagFilters=&numericFilters=%5B%22startDate%3E%3D{current_timestamp}%22%2C%22startDate%3C%3D{three_months_later_timestamp}%22%5D"
        },
        {
            "indexName": "prod_sfs_calendar",
            "params": f"hitsPerPage=1&facetFilters=%5B%5B%22excludeFromCalendar%3Afalse%22%5D%5D&query=&highlightPreTag=__ais-highlight__&highlightPostTag=__%2Fais-highlight__&maxValuesPerFacet=10000&page=0&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=startDate"
        }
    ]
}

# Make the POST request to the API with the updated JSON payload
response = requests.post(url, headers=headers, json=payload)

# Parse the JSON response
data = response.json()

# Define a list to hold parsed concert data
concerts = []

# Timezone for San Francisco (PST/PDT)
timezone = pytz.timezone('America/Los_Angeles')

# Function to parse concert data
def parse_concerts(data):
    # Loop through each concert entry in the JSON data
    for hit in data['results'][0]['hits']:
        # Extract the necessary information
        title = f'SFS: {hit.get('title', 'Unknown Title')}'
        performance_date = hit.get('performanceDate', None)
        venue = hit.get('venue', 'Unknown Venue')
        performance_url_suffix = hit.get('kenticoUrl', None)
        performance_url = f"https://www.sfsymphony.org{performance_url_suffix}" if performance_url_suffix else "N/A"

        # Convert performance date from string to datetime object
        if performance_date:
            date_time = datetime.fromisoformat(performance_date)
            # Localize to the specified timezone (includes offset)
            date_time_with_tz = timezone.localize(date_time)
            date = date_time_with_tz.date()
            time = date_time_with_tz.time()
        else:
            date = None
            time = None
        
        # Create a description from artists, composers, conductors, and works
        description_parts = [
            f"Performance URL: {performance_url}",
            f"Artists: {', '.join(hit.get('artists', []))}",
            f"Composers: {', '.join(hit.get('composers', []))}",
            f"Conductors: {', '.join(hit.get('conductors', []))}",
            f"Works: {', '.join(hit.get('works', []))}"
        ]
        description = "\n".join([part for part in description_parts if part.split(': ')[1]])

        # Append parsed data to the concerts list
        concerts.append({
            'title': title,
            'date': date_time_with_tz.isoformat() if date_time_with_tz else None,  # Serialize date with timezone
            'venue': venue,
            'description': description,
        })

# Parse the JSON data to get the list of concerts
parse_concerts(data)

# Create the 'events' directory if it doesn't exist
events_dir = 'events'
if not os.path.exists(events_dir):
    os.makedirs(events_dir)

# Save the parsed concerts data to a JSON file
json_file_path = os.path.join(events_dir, 'sfs_extracted_concerts_data.json')
with open(json_file_path, 'w', encoding='utf-8') as json_file:
    json.dump(concerts, json_file, ensure_ascii=False, indent=2)

logging.info(f"Parsed concert data ({len(concerts)} entries) has been saved to {json_file_path}")
