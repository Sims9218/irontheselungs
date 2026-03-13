import asyncio
from playwright.async_api import async_playwright
import datetime
import os

SHOW_URL = "https://in.bookmyshow.com/buytickets/iron-lung-mumbai/movie-mumbai-ET00490088-MT/20260315"
LOG_FILE = "seat_tracking.csv"

async def track_seats():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print(f"Navigating to {SHOW_URL}...")
        await page.goto(SHOW_URL, wait_until="networkidle")
        
        await page.wait_for_timeout(5000)

        booked_count = await page.locator("div._booked").count()
        available_count = await page.locator("div._available").count()
        total_seats = booked_count + available_count

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Write to file
        file_exists = os.path.isfile(LOG_FILE)
        with open(LOG_FILE, "a") as f:
            if not file_exists:
                f.write("Timestamp,Total Seats,Booked Seats\n")
            f.write(f"{timestamp},{total_seats},{booked_count}\n")
        
        print(f"[{timestamp}] Success: {booked_count} seats booked.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(track_seats())
