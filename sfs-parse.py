import json
from datetime import datetime

# Load the JSON data from the file
with open('concerts_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Define a list to hold parsed concert data
concerts = []

# Function to parse concert data
def parse_concerts(data):
    # Loop through each concert entry in the JSON data
    for hit in data['results'][0]['hits']:
        # Extract the necessary information
        title = hit.get('title', 'Unknown Title')
        performance_date = hit.get('performanceDate', None)
        venue = hit.get('venue', 'Unknown Venue')

        # Convert performance date from string to datetime object
        if performance_date:
            date_time = datetime.fromisoformat(performance_date)
            date = date_time.date()
            time = date_time.time()
        else:
            date = None
            time = None
        
        # Create a description from artists, composers, conductors, and works
        description_parts = [
            f"Works: {', '.join(hit.get('works', []))}",
            f"Composers: {', '.join(hit.get('composers', []))}",
            f"Conductors: {', '.join(hit.get('conductors', []))}",
            f"Artists: {', '.join(hit.get('artists', []))}",
        ]
        description = "\n".join([part for part in description_parts if part.split(': ')[1]])

        # Append parsed data to the concerts list
        concerts.append({
            'title': title,
            'date': date,
            'time': time,
            'venue': venue,
            'description': description,
        })

# Parse the JSON data to get the list of concerts
parse_concerts(data)

# Print parsed concerts for verification
for concert in concerts:
    print(concert)
