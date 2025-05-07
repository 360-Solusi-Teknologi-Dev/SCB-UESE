import os
import sys
import time
import tempfile
import shutil
import threading
from core import presets
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pkg_resources import resource_filename

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QMessageBox, QFileDialog, QComboBox
)

from PySide6.QtCore import Qt, Signal


def extract_driver():
    if getattr(sys, 'frozen', False):
        driver_path_in_bundle = resource_filename(__name__, 'msedgedriver-135.exe')
    else:
        driver_path_in_bundle = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'msedgedriver-135.exe')

    temp_dir = tempfile.mkdtemp()
    temp_driver_path = os.path.join(temp_dir, 'msedgedriver-135.exe')
    shutil.copy(driver_path_in_bundle, temp_driver_path)
    return temp_driver_path


class EnquiryScraper(QWidget):
    enquiry_opened = Signal(str)
    enquiry_failed = Signal()

    def __init__(self):
        super().__init__()
        self.driver = None
        self.init_ui()

        # Connect signals to slots
        self.enquiry_opened.connect(self.on_enquiry_opened)
        self.enquiry_failed.connect(self.on_enquiry_failed)

    def init_ui(self):
        self.setWindowTitle("Enquiry Scraper")
        self.setFixedSize(400, 250)

        self.url_label = QLabel("Enter web app URL:")
        self.url_entry = QLineEdit()

        self.team_label = QLabel("Select Team Preset:")
        self.team_combo = QComboBox()
        self.team_combo.addItems(presets.get_team_names())

        self.start_button = QPushButton("Start")
        self.resume_button = QPushButton("Resume")
        self.resume_button.setEnabled(False)

        layout = QVBoxLayout()
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_entry)
        layout.addWidget(self.team_label)
        layout.addWidget(self.team_combo)
        layout.addWidget(self.start_button)
        layout.addWidget(self.resume_button)
        self.setLayout(layout)

        self.start_button.clicked.connect(self.start_browser)
        self.resume_button.clicked.connect(self.resume_scraping)

    def start_browser(self):
        url = self.url_entry.text().strip()
        if not url:
            QMessageBox.critical(self, "Input Error", "Please enter a valid URL.")
            return
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        self.start_button.setEnabled(False)
        self.resume_button.setEnabled(True)

        QMessageBox.information(
            self,
            "Next Step",
            "Please log in to your web app and open the Enquiry page.\n\nClick 'Resume' once the Enquiry window is fully opened."
        )

        threading.Thread(target=self._start_browser_thread, args=(url,), daemon=True).start()

    def _start_browser_thread(self, url):
        driver_path = extract_driver()
        service = Service(executable_path=driver_path)
        self.driver = webdriver.Edge(service=service)
        self.driver.get(url)
        print("Opened:", url)

    def resume_scraping(self):
        self.resume_button.setEnabled(False)
        self.selected_team = self.team_combo.currentText()
        self.fields = presets.get_fields_for_team(self.selected_team)
        threading.Thread(target=self._scrape_thread, daemon=True).start()

    def _scrape_thread(self):
        try:
            original_window = self.driver.current_window_handle
            new_window = None
            print("Waiting for new window...")
            for _ in range(20):
                time.sleep(1)
                if len(self.driver.window_handles) > 1:
                    new_window = [w for w in self.driver.window_handles if w != original_window][0]
                    break

            if new_window:
                self.driver.switch_to.window(new_window)
                title = self.driver.title
                print("New window title:", title)
                self.enquiry_opened.emit(title)
                self._relid_scraping_logic()
            else:
                print("No new window detected.")
                self.enquiry_failed.emit()
        except Exception as e:
            print("Error:", e)
        finally:
            self.driver.quit()
            print("Browser closed.")


    def _relid_scraping_logic(self):
        print(f"Scraping using preset for team: {self.selected_team}")
        try:
            # Wait up to 10 seconds for the frame to appear
            WebDriverWait(self.driver, 10).until(
                EC.frame_to_be_available_and_switch_to_it((By.NAME, "enqframe"))
            )
            print("Switched to 'enqframe'.")

            # Wait up to 10 seconds for the RELID input to be present
            relid_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "relationshipnotxt"))
            )
            relid_input.clear()
            relid_input.send_keys("RELSAMPLE123")
            self.driver.find_element(By.NAME, "Submit").click()

            time.sleep(2)

            if self.driver.find_elements(By.ID, "datatable"):
                print("Data table found.")
                for label, selector in self.fields.items():
                    try:
                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        print(f"{label}: {element.text.strip()}")
                    except Exception:
                        print(f"{label}: [NOT FOUND]")
            else:
                print("No data found for RELID.")

        except Exception as e:
            print("Error in RELID scraping logic:", e)

    # --- UI Slots ---
    def on_enquiry_opened(self, title):
        QMessageBox.information(self, "Success", f"Enquiry opened successfully at \"{title}\".")

    def on_enquiry_failed(self):
        QMessageBox.warning(self, "Failure", "No new window detected.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EnquiryScraper()
    window.show()
    sys.exit(app.exec())
