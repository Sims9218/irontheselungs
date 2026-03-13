import asyncio
from playwright.async_api import async_playwright
import datetime
import os

SHOW_URL = "https://in.bookmyshow.com/movies/mumbai/seat-layout/ET00490088/CSWO/4094/20260315"
LOG_FILE = "seat_tracking.csv"

async def track_seats():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print(f"Opening: {SHOW_URL}")
        await page.goto(SHOW_URL, wait_until="domcontentloaded")

        try:
            # 1. Handle "Terms and Conditions" popup
            # It usually has an 'Accept' or 'Proceed' button
            accept_button = page.locator("button:has-text('Accept'), #btn-accept, .btn-primary")
            if await accept_button.is_visible(timeout=5000):
                print("Clicking Accept button...")
                await accept_button.click()

            # 2. Wait for the seat layout to appear
            # We are now looking for the specific BMS seat class: '._available'
            print("Waiting for seat map...")
            await page.wait_for_selector("div._available, div._booked", timeout=15000)
            
            # 3. Count the seats
            booked_count = await page.locator("div._booked").count()
            available_count = await page.locator("div._available").count()
            total_seats = booked_count + available_count

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            
            # Log the data
            file_exists = os.path.isfile(LOG_FILE)
            with open(LOG_FILE, "a") as f:
                if not file_exists:
                    f.write("Timestamp,Total Seats,Booked Seats\n")
                f.write(f"{timestamp},{total_seats},{booked_count}\n")
            
            print(f"[{timestamp}] Success! Booked: {booked_count}/{total_seats}")

        except Exception as e:
            # Take a screenshot to see what went wrong (viewable in GitHub Action artifacts)
            await page.screenshot(path="error_screenshot.png")
            print(f"Failed to find seats. Saved screenshot to 'error_screenshot.png'. Error: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(track_seats())
