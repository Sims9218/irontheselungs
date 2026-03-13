import asyncio
from playwright.async_api import async_playwright
import datetime
import os

# The URL from your screenshot
SHOW_URL = "https://in.bookmyshow.com/movies/mumbai/seat-layout/ET00490088/CSWO/4094/20260315"
LOG_FILE = "seat_tracking.csv"

async def track_seats():
    async with async_playwright() as p:
        # Launching with a wider viewport to ensure all popups are visible and clickable
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print(f"Navigating to layout...")
        await page.goto(SHOW_URL, wait_until="networkidle")

        try:
            # 1. Handle the "Select Number of Seats" popup (e.g., Select 2, 4, etc.)
            # We try to click 'Select Seats' or just click '2' then 'Select Seats'
            if await page.locator("#btn-accept").is_visible(timeout=5000):
                await page.click("#btn-accept")
                print("Accepted Terms.")
            
            # If the "How many seats" popup appears, we click '2' and 'Select Seats'
            qty_popup = page.locator("ul#qty-sel li").first
            if await qty_popup.is_visible(timeout=3000):
                await qty_popup.click()
                await page.click("#proceed-qty")
                print("Handled seat quantity popup.")

            # 2. Use a more generic selector for the seats
            # BMS seats often use 'a.seatR' or 'a.seatA' or have 'data-seat-type'
            print("Waiting for seat elements...")
            await page.wait_for_selector("a.seatR, a.seatA, ._available, ._booked", timeout=15000)
            
            # 3. Targeted counting using the classes typically found in the layout
            # Available seats are usually 'a.seatA', Booked are 'a.seatR' (Reserved)
            booked = await page.locator("a.seatR, ._booked").count()
            available = await page.locator("a.seatA, ._available").count()
            total = booked + available

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            
            # Write to CSV
            file_exists = os.path.isfile(LOG_FILE)
            with open(LOG_FILE, "a") as f:
                if not file_exists:
                    f.write("Timestamp,Total Seats,Booked Seats\n")
                f.write(f"{timestamp},{total},{booked}\n")
            
            print(f"[{timestamp}] SUCCESS: {booked}/{total} seats booked.")

        except Exception as e:
            # This is crucial: check the 'Actions' tab artifacts for this image if it fails!
            await page.screenshot(path="error_screenshot.png")
            print(f"Critical Error: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(track_seats())
