import os
import sys
import tempfile
import shutil
from selenium import webdriver
from selenium.webdriver.edge.service import Service
import time
from pkg_resources import resource_filename  # To extract resources from PyInstaller bundle

def extract_driver():
    if getattr(sys, 'frozen', False):
        # Running as a bundled executable
        driver_path_in_bundle = resource_filename(__name__, 'msedgedriver.exe')
    else:
        # Running as a script
        driver_path_in_bundle = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'msedgedriver.exe')

    # Extract to a temporary directory
    temp_dir = tempfile.mkdtemp()
    temp_driver_path = os.path.join(temp_dir, 'msedgedriver.exe')

    shutil.copy(driver_path_in_bundle, temp_driver_path)
    return temp_driver_path

def main():
    # Extract msedgedriver.exe from the bundled .exe (or from script directory)
    driver_path = extract_driver()

    # Create Service object with path to msedgedriver.exe
    service = Service(executable_path=driver_path)

    # Initialize Edge WebDriver with the Service
    driver = webdriver.Edge(service=service)

    try:
        # Open the HTML file (path should be adjusted accordingly)
        driver.get(r"file:C:\laragon\www\enquiry-scraping-selenium\htmltest.html")  # Adjust path if needed
        print("Opened HTML.")

        # Pause and allow the user to log in and click the button
        print("Please log in and click the 'Open Enquiry Page' button.")
        input("Press Enter once the new window has opened...")

        # Wait for the new window to open (adjust wait time if needed)
        time.sleep(2)  # Optional: Add a small delay before checking

        # Check if a new window has opened
        original_window = driver.current_window_handle
        new_window = None
        while new_window is None:
            time.sleep(1)  # Wait for new window to open
            # Check for a new window handle
            if len(driver.window_handles) > 1:
                new_window = [window for window in driver.window_handles if window != original_window][0]
        
        # Switch to the new window
        driver.switch_to.window(new_window)

        # Interact with the new window (e.g., check title)
        print(f"New window title: {driver.title}")

        # Wait for the results to load
        time.sleep(3)

        # Optional: print title of the page
        print("Current page title:", driver.title)

    finally:
        # Close the browser after the process is done
        print('Process Done.')
        driver.quit()  # Automatically close the browser

if __name__ == "__main__":
    main()
