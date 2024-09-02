# Bay Area Classical Concert Sync

This project automates the synchronization of classical concert events from the San Francisco Symphony and Cal Performances websites to a Google Calendar. It consists of two Python scripts: `sfs-dump-and-parse.py` to fetch and parse concert data, and `sync-to-gcal.py` to update the events in Google Calendar.

NOTE: You do NOT need to run this yourself, I run this daily and keep a public Google Calendar up to date. You can view the calendar int he brwoser by [clicking here](https://calendar.google.com/calendar/embed?src=c_b816af4191ec6450b0be043156234fe75768489d1b660fce6d8fd745012dd2b9%40group.calendar.google.com&ctz=America%2FLos_Angeles), and you can add it as an overlay to your own Google Calendar by [clicking here](https://calendar.google.com/calendar/u/1?cid=Y19iODE2YWY0MTkxZWM2NDUwYjBiZTA0MzE1NjIzNGZlNzU3Njg0ODlkMWI2NjBmY2U2ZDhmZDc0NTAxMmRkMmI5QGdyb3VwLmNhbGVuZGFyLmdvb2dsZS5jb20).

## Project Overview

1. **sfs-dump-and-parse.py**: This script fetches concert data from the SF Symphony website, parses the data to extract relevant event details, and saves the events as JSON files in the `events` directory.
   
2. **sync-to-gcal.py**: This script reads the JSON files from the `events` directory and syncs the concert events to a Google Calendar. It creates new events or updates existing ones based on the parsed data.

3. **Logging**: Both scripts are configured to log their output to `daily_concert_sync.log` for easy monitoring and troubleshooting.

## Prerequisites

- Python 3.x
- `pip` for managing Python packages
- Google Cloud project with the Google Calendar API enabled
- OAuth 2.0 credentials (`credentials.json`) for Google Calendar API

## Setup Instructions

### 1. Clone the Repository

```
git clone https://github.com/yourusername/bay-area-classical-concerts.git
cd bay-area-classical-concerts
```

### 2. Install Required Python Packages

Ensure you have the necessary Python packages installed:

```
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client requests pytz
```

### 3. Configure Google Calendar API Credentials

1. Obtain your `credentials.json` from the [Google Cloud Console](https://console.developers.google.com/).
2. Place `credentials.json` in the root directory of the project.

### 4. Set Up Logging

Both scripts are configured to log to `daily_concert_sync.log`. Ensure this file exists and is writable by the user running the scripts.

### 5. Set Up the Cron Job

Schedule the cron job to run daily at 9 AM:

1. Open the crontab configuration file:

   ```
   crontab -e
   ```

2. Add the following line:

   ```
   0 9 * * * /path/to/your/scripts/run_concert_sync.sh >> /path/to/your/scripts/daily_concert_sync.log 2>&1
   ```

### 6. Verify the Cron Job

Check your cron job configuration:

```
crontab -l
```

## Usage

After setting up the cron job, the scripts will automatically run daily at 9 AM, fetching the latest concert data and syncing it to your Google Calendar. You can view the logs in `daily_concert_sync.log` to verify that the scripts are running correctly and troubleshoot any issues.

## Troubleshooting

- **Logs**: Check `daily_concert_sync.log` for detailed logs of each run, including any errors or warnings.
- **Google Calendar Authentication**: If you encounter authentication issues, make sure your `credentials.json` is correct and up-to-date. You may need to delete `token.json` to re-authenticate.
- **Cron Job Not Running**: Ensure that the cron job is set up correctly and that the user running the cron job has the necessary permissions.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the SF Symphony and Cal Performances for providing access to their concert data.
- Built using the Google Calendar API for seamless event synchronization.
