from datetime import datetime, timedelta
import time
import requests
import json

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

# Define the file name and path to save the JSON data
file_name = "concerts_data.json"

# Save the JSON data to a file
with open(file_name, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"JSON data has been saved to {file_name}")