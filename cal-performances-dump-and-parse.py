import requests
import json
import re
from datetime import datetime, timedelta
import calendar

# Base URL for the request
url = "https://calperformances.org/wp-admin/admin-ajax.php"

# Function to generate a list of months to query
def generate_months_to_query():
    """Generate a list of months (YYYY-MM) for the current and next 3 months."""
    current_date = datetime.now()
    months_to_query = []

    # Generate current and next 3 months
    for i in range(4):
        month = (current_date.month + i - 1) % 12 + 1  # Calculate the month
        year = current_date.year + (current_date.month + i - 1) // 12  # Calculate the year if month exceeds December
        query_month = datetime(year, month, 1)  # Create a datetime object for the first day of the month
        months_to_query.append(query_month.strftime("%Y-%m"))  # Format to YYYY-MM and add to the list
    
    return months_to_query

# List of months to query
months_to_query = generate_months_to_query()

# Headers for the request (Replicating from the original request)
headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
    "referer": "https://calperformances.org/2023-24-season/?month=2023-11",
    "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "macOS",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "cookie": "PHPSESSID=761a8244591b020681c2994c2ff636ec; _gcl_au=1.1.2064543363.1725254278; _ga=GA1.1.1424595057.1725254278; _rollupGA=GA1.2.1424595057.1725254278; _rollupGA_gid=GA1.2.918962077.1725254278; _fbp=fb.1.1725254278558.986412769526700993; _ga_MTY88SHZS1=GS1.1.1725254278.1.1.1725254335.3.0.386280866; _gat_UA-532457-1=1"
}

# List to hold all concerts across all months
all_concerts = []

for month in months_to_query:
    # Query string parameters for the request for each month
    params = {
        "action": "cpcustom_eventfilter_ajax_request",
        "search": "",
        # "season": "233",  # The season value might need to be updated based on the current year
        "month": month,  # The current and next 3 months
        "genre": "",
        "nonce": "c61fa603ec"  # The nonce might change; it usually has a validity period
    }

    # Make the GET request
    response = requests.get(url, headers=headers, params=params)

    # Check the status of the response
    if response.status_code == 200:
        print(f"Request successful for {month}!")

        # Parse the response content to a Python dictionary
        response_data = json.loads(response.text)

        # Extract the HTML content from the response
        html_content = response_data['html']

        # Use a regex pattern to extract all JSON-LD script tags
        json_ld_pattern = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.DOTALL)
        json_ld_matches = json_ld_pattern.findall(html_content)

        # Parse each JSON-LD script content
        for json_ld in json_ld_matches:
            # Split multiple JSON objects if concatenated together
            json_objects = re.findall(r'\{.*?\}(?=\{|\Z)', json_ld)

            for json_object in json_objects:
                try:
                    # Convert the escaped JSON string back to proper JSON format
                    event_data = json.loads(json_object.replace('\\/', '/'))
                    
                    # Extract required fields
                    title = event_data.get('name', 'Unknown Title')
                    date_str = event_data.get('startDate', '')
                    date_time = None
                    
                    # Convert date to ISO 8601 format
                    if date_str:
                        date_time = datetime.strptime(date_str, "%m/%d/%YT%H:%M").isoformat()

                    # Construct the description with additional details
                    performance_url = event_data.get('url', 'N/A')
                    description = (
                        f"Performance URL: {performance_url}\n"
                        f"Description: {event_data.get('description', '')}\n"
                        f"Image: {event_data.get('image', '')}\n"
                        f"Organizer: {event_data.get('organizer', {}).get('name', 'Cal Performances')}"
                    )

                    # Extract venue information
                    venue = event_data.get('location', {}).get('url', 'Unknown Venue')
                    venue_name = venue.split('#')[-1].replace('-', ' ').title()

                    # Add to concerts list
                    all_concerts.append({
                        'title': f'Cal Performances: {title}',
                        'date': date_time,
                        'venue': venue_name,
                        'description': description
                    })
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON-LD content: {e}")
    else:
        print(f"Request failed with status code {response.status_code} for {month}")

# Save the parsed concerts data to a JSON file
output_file = 'events/cal_performances_concerts_data.json'
with open(output_file, 'w', encoding='utf-8') as json_file:
    json.dump(all_concerts, json_file, ensure_ascii=False, indent=2)

print(f"Parsed concert data has been saved to {output_file}")
