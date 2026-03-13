import requests
from bs4 import BeautifulSoup
import datetime
import os

SHOW_URL = "https://in.bookmyshow.com/movies/mumbai/iron-lung/buytickets/ET00490088/20260315"
LOG_FILE = "seat_tracking.csv"

def track_seats():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    
    response = requests.get(SHOW_URL, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch page: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    booked_seats = len(soup.find_all(class_='_booked')) 
    total_seats = len(soup.find_all(class_='_available')) + booked_seats
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, "a") as f:
        if not file_exists:
            f.write("Timestamp,Total Seats,Booked Seats\n")
        f.write(f"{timestamp},{total_seats},{booked_seats}\n")
    
    print(f"[{timestamp}] Booked: {booked_seats}/{total_seats}")

if __name__ == "__main__":
    track_seats()
