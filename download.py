import json
import datetime
import requests
from time import time, sleep
import sqlite3
import RPi.GPIO as GPIO

ledPin = 7

def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(ledPin, GPIO.OUT)

class SMSHandler:
    def __init__(self, api_url):
        self.api_url = api_url

    def downloadAndSave(self):
        setup()
        while True:
            # Set LED to indicate script is contacting API
            GPIO.output(ledPin, 1)
            sleep(0.1)
            GPIO.output(ledPin, 0)

            response = self.download_data(self.api_url)

            if response is not None and response.status_code == 200:
                try:
                    data = json.loads(response.text)
                    prev_recipient = ""
                    prev_msg = ""
                    for item in data["topLevel"]:
                        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        recipient = item["recipient"]
                        msg = item["message"]
                        if recipient != "null" and recipient != prev_recipient and msg != prev_msg:
                            self.saveToDatabase(recipient, msg, timestamp)
                            print(f"Downloaded: {recipient} - {msg} at {timestamp}")
                            print("**********")
                            sleep(1)  # Wait before next download attempt
                except (json.JSONDecodeError, KeyError) as e:
                    print("Error parsing response: " + str(e))
            elif response is not None:
                print("Error retrieving data from server. Status code:", response.status_code)

            sleep(1)
        GPIO.cleanup()

    def saveToDatabase(self, recipient, message, downloaded_at):
        # Connect to the SQLite database
        conn = sqlite3.connect('/home/pi/smser-pi/sms_data.db')
        cursor = conn.cursor()

        # Create outgoing_sms table if not exists
        cursor.execute('''CREATE TABLE IF NOT EXISTS outgoing_sms (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            recipient TEXT,
                            message TEXT,
                            downloaded_at DATETIME,
                            sent_at DATETIME
                        )''')
        conn.commit()

        # Insert the SMS data into the outgoing_sms table
        cursor.execute('''INSERT INTO outgoing_sms (recipient, message, downloaded_at)
                          VALUES (?, ?, ?)''', (recipient, message, downloaded_at))
        conn.commit()

        # Close the database connection
        conn.close()

    def download_data(self, url, max_retries=3, retry_delay=5):
        setup()
        last_error_message = None

        for attempt in range(1, max_retries + 1):
            try:
                response = requests.get(url)
                response.raise_for_status()

                if last_error_message:
                    connected_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"Back online 😊 [{connected_at}]\n")
                    last_error_message = None
                return response
            except requests.exceptions.RequestException as e:
                if "RemoteDisconnected" in str(e):
                    # Suppress the specific error message for RemoteDisconnected
                    if last_error_message != "Lost connection. Retrying...":
                        lost_connection_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        print(f"Connection dropped. Retrying... [{lost_connection_at}]\n")
                        last_error_message = "Lost connection. Retrying..."
                else:
                    # Print other error messages
                    error_message = "Connection dropped."
                    if last_error_message != error_message:
                        print(error_message)
                        last_error_message = error_message

                if attempt < max_retries:
                    sleep(retry_delay)
                else:
                    max_retrying_reached_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"Why not checking internet connection? [{max_retrying_reached_at}]\n")
                    return None

# Main execution
if __name__ == "__main__":
    api_url = "https://smser.benax.rw/services/nesa/api.php"
    sms_handler = SMSHandler(api_url)
    sms_handler.downloadAndSave()
