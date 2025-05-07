import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service

def run_browser_automation(driver_path):
    service = Service(executable_path=driver_path)
    driver = webdriver.Edge(service=service)

    try:
        driver.get(r"file:C:\laragon\www\enquiry-scraping-selenium\htmltest.html")
        print("Opened HTML.")
        print("Please log in and click the 'Open Enquiry Page' button.")
        input("Press Enter once the new window has opened...")

        time.sleep(2)
        original_window = driver.current_window_handle
        new_window = None
        while new_window is None:
            time.sleep(1)
            if len(driver.window_handles) > 1:
                new_window = [w for w in driver.window_handles if w != original_window][0]

        driver.switch_to.window(new_window)
        print(f"New window title: {driver.title}")
        time.sleep(3)
        print("Current page title:", driver.title)

    finally:
        print('Process Done.')
        driver.quit()
