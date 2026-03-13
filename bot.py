import requests
import datetime
import os
import json


API_URL = "https://www.district.in/gw/consumer/movies/v1/select-seat?version=3&site_id=1&channel=mweb&child_site_id=1&platform=district"


HEADERS = {
    "accept": "application/json",
    "accept-language": "en-US,en;q=0.9",
    "api_source": "district",
    "content-type": "application/json; charset=utf-8",
    "origin": "https://www.district.in",
    "referer": "https://www.district.in/movies/seat-layout/6hxsglxlg~?encsessionid=57700-4094-ob87p3-57700&fromdate=2026-03-15&freeseating=false&fromsessions=true&type=MOVIES&contentid=215565",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 OPR/128.0.0.0",
    "x-app-type": "ed_mweb",
    "x-guest-token": "1773421845350_356665642271753660_loxxv36wcge",
    "cookie": "AKA_A2=A; ak_bmsc=F1ABAF671DC5A6C818EAA0A44B3B68A0~000000000000000000000000000000~YAAQb/naF6JSwuScAQAAoNkX6B8p/ITPHOzkolWe+OhZJKYS07plCa+sMlNOV1f8BBECmSWhj7YZ6ONGmjf7ZrdbrhdbbuMzwt7Safvp5QcwYt/JkVzHhoALGPcFmtaWKmlXLdj2f4uQsZ8oTvoij0+jVXsHqoqFGgrCI8RcN/Zqjao64heCJHM+Pt7SdsWaMeA3baps212CIQn70sEE6jX90yDLnHSKadQ82JoClFn5taFcWf9+mWSN7b1Py8GTYtGXCoXE1mhDSlFGidQTQ+2BmJ3pf4LP0vusMxzchvgDklSZlnaMPCpu786+mepV8KNu9242v/r1tC3pFfqMTFNinC9l2IXx9gMYmv3EazxpsMvySb+b6Ul++tCclNgNemNzoXdLNR8doJkAcKfaRtuLIGK0VO24iBVi/8FBfR9ji6wk; x-device-id=d635e0ac-f62e-43d9-8545-f510c09b8ccd; location=%7B%22id%22%3A3%2C%22title%22%3A%22Navi%20Mumbai%22%2C%22lat%22%3A19.085665233278235%2C%22long%22%3A73.03309068051662%2C%22subtitle%22%3A%22Maharashtra%22%2C%22cityId%22%3A3%2C%22cityName%22%3A%22Mumbai%22%2C%22pCityId%22%3A%2236%22%2C%22pCityKey%22%3A%22navi-mumbai%22%2C%22pCityName%22%3A%22Navi%20Mumbai%22%2C%22pStateKey%22%3A%22maharashtra%22%2C%22pStateName%22%3A%22Maharashtra%22%2C%22placeType%22%3A%22GOOGLE_PLACE%22%2C%22placeId%22%3A%22ChIJOwU1MQnB5zsRaa0Zd31qCvY%22%2C%22countryId%22%3A%221%22%2C%22subzoneId%22%3A%222126%22%7D; bm_sv=8C12712797DAD958FE7E1A18830AB719~YAAQzvQ3F5F8nOOcAQAAs9ot6B8m1wNuDK/lteYN4vSIrzWcd61dPSnfoRoJtgZ9OlG94p3BsxoTupGPU7UZS/Faq7oJDZQr6Hrs0p0lWFhwkX4ed2VFn8M4cD6jYszBBu9Tf2GIgfVXrPxY258FPlHtBjy36jVTwPWXDqk3o7eVZfIiFedU4RiI4vseDw2Jnx67Gw02KEWSmVusHg+sNxqwofy8xzv0Dwb3d/l5Y2Xs5pMNTwC295N4y3q2pnBNNB8=~1"
}


PAYLOAD = {
    "cinemaId": 57700,
    "sessionId": "4094",
    "providerId": 335,
    "screenOnTop": True,
    "freeSeating": "false",
    "screenFormat": "2D",
    "moviecode": "OB87P3",
    "config": {"socialDistancing": 1},
    "retrieve": False,
    "contentId": "215565"
}

LOG_FILE = "seat_tracking.csv"

def track_seats():
    try:
        print(f"[{datetime.datetime.now()}] Fetching live seat data...")
        response = requests.post(API_URL, headers=HEADERS, json=PAYLOAD)
        
        if response.status_code != 200:
            print(f"API Error: {response.status_code}")
            return

        data = response.json()
        
        areas = data.get("data", {}).get("seatLayout", {}).get("colAreas", {}).get("objArea", [])
        
        booked_count = 0
        total_seats = 0

        for area in areas:
            rows = area.get("objRow", [])
            for row in rows:
                seats = row.get("objSeat", [])
                for seat in seats:
                    if seat.get("SeatName") or seat.get("GridSeatNum"):
                        total_seats += 1
                        if str(seat.get("status")) != "0":
                            booked_count += 1

        if total_seats == 0:
            print("Warning: No seats found. Check if the JSON structure has changed again.")
            return

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        file_exists = os.path.isfile(LOG_FILE)
        with open(LOG_FILE, "a") as f:
            if not file_exists:
                f.write("Timestamp,Total Seats,Booked Seats\n")
            f.write(f"{timestamp},{total_seats},{booked_count}\n")
        
        print(f"Update Successful! Booked: {booked_count}/{total_seats}")

    except Exception as e:
        print(f"Error encountered: {e}")

if __name__ == "__main__":
    track_seats()
