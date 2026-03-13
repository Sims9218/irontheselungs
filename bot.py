import requests
import datetime
import os
import json

API_URL = "https://www.district.in/gw/consumer/movies/v1/select-seat?version=3&site_id=1&channel=mweb&child_site_id=1&platform=district"

HEADERS = {
    "accept": "application/json",
    "api_source": "district",
    "content-type": "application/json; charset=utf-8",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 OPR/128.0.0.0",
    "x-app-type": "ed_mweb",
    "x-guest-token": "1773420604139_116858561187815570_6i942lkptu7",
    "cookie": "AKA_A2=A; ak_bmsc=F1ABAF671DC5A6C818EAA044B3B68A0~000000000000000000000000000000; bm_sv=8C12712797DAD958FE7A1A18830AB719~YAAQLXZFF3AHk7aQAAGbMa6B/QryCQQvGV8Yu0+qntJltBt6nyMquJrUax5zl574YSHN43yUZEePTl3Z+yp1rJAM8n0s+Kd58aZACRFEFHninvhqkgY20XxGI+kTd4ghyh/G5WOp6SRzO/fTBiDrEzhqL2FEYXEKO79Eg/GQ4GybyxDkw1AgoAz/oGXDpksBGCOboXFcEMOnfpTKki7qPkc2ih5nT6g5u7vXxUDRK6o/eFBHdh3dhHrknwcSTvKGIA==~1; _dd_s=rum=0&expire=1773421504137"
}

PAYLOAD = {
    "cinemaId": "57700",
    "sessionId": "4094",
    "providerId": "335",
    "screenOnTop": True,
    "freeSeating": False,
    "screenFormat": "2D",
    "moviecode": "OB87P3",
    "config": {"socialDistancing": 1},
    "contentId": "215565"
}

LOG_FILE = "seat_tracking.csv"

def track_seats():
    response = requests.post(API_URL, headers=HEADERS, json=PAYLOAD)
    
    if response.status_code != 200:
        print(f"API Error {response.status_code}: {response.text}")
        return

    data = response.json()
    booked_count = 0
    total_seats = 0

    def find_seats(obj):
        nonlocal booked_count, total_seats
        if isinstance(obj, dict):
            if "status" in obj and ("seatId" in obj or "name" in obj):
                total_seats += 1
                if obj["status"] != 0:
                    booked_count += 1
            for value in obj.values():
                find_seats(value)
        elif isinstance(obj, list):
            for item in obj:
                find_seats(item)

    find_seats(data)

    if total_seats == 0:
        print("Error: No seats found in the JSON response. The layout structure might have changed.")
        print(json.dumps(data, indent=2)[:500]) 
        return

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, "a") as f:
        if not file_exists:
            f.write("Timestamp,Total Seats,Booked Seats\n")
        f.write(f"{timestamp},{total_seats},{booked_count}\n")
    
    print(f"[{timestamp}] Successfully found {total_seats} seats. {booked_count} are booked.")

if __name__ == "__main__":
    track_seats()
