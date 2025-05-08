from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QComboBox, QMessageBox, QHBoxLayout, QToolButton
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal
from core.scraper import Scraper
from core import presets
from gui.preset_manager import PresetManager  # Import the Preset Manager
import threading

class MainGUI(QWidget):
    enquiry_opened = Signal(str)
    enquiry_failed = Signal()

    def __init__(self, driver_path):
        super().__init__()
        self.driver_path = driver_path
        self.scraper = Scraper(driver_path)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Enquiry Scraper")
        self.setFixedSize(400, 300)

        # URL input
        self.url_label = QLabel("Enter web app URL:")
        self.url_entry = QLineEdit()

        # Team preset dropdown
        self.team_label = QLabel("Select Team Preset:")
        self.team_combo = QComboBox()
        self.team_combo.addItems(presets.get_team_names())

        # Buttons
        self.start_button = QPushButton("Start")
        self.resume_button = QPushButton("Resume")
        self.resume_button.setEnabled(False)
        self.reset_button = QPushButton("Reset")

        # Cog icon button for Preset Manager
        self.settings_button = QToolButton()
        self.settings_button.setIcon(QIcon("cog_icon.png"))  # Replace with the path to your cog icon
        self.settings_button.setToolTip("Manage Presets")
        self.settings_button.clicked.connect(self.open_preset_manager)

        # Layout for the cog icon (top-right corner)
        top_layout = QHBoxLayout()
        top_layout.addStretch()  # Push the cog icon to the right
        top_layout.addWidget(self.settings_button)

        # Main layout
        layout = QVBoxLayout()
        layout.addLayout(top_layout)  # Add the top layout with the cog icon
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_entry)
        layout.addWidget(self.team_label)
        layout.addWidget(self.team_combo)
        layout.addWidget(self.start_button)
        layout.addWidget(self.resume_button)
        layout.addWidget(self.reset_button)
        self.setLayout(layout)

        # Connect buttons to their respective methods
        self.start_button.clicked.connect(self.start_browser)
        self.resume_button.clicked.connect(self.resume_scraping)
        self.reset_button.clicked.connect(self.reset_app)

    def open_preset_manager(self):
        """Open the Preset Manager."""
        preset_manager = PresetManager(self)
        preset_manager.exec()
        # Reload team presets in the combo box after changes
        self.team_combo.clear()
        self.team_combo.addItems(presets.get_team_names())

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

        threading.Thread(target=self.scraper.start_browser, args=(url,), daemon=True).start()

    def resume_scraping(self):
        self.resume_button.setEnabled(False)
        self.selected_team = self.team_combo.currentText()
        self.fields = presets.get_fields_for_team(self.selected_team)

        def scrape_thread():
            title = self.scraper.wait_for_new_window()
            if title:
                self.enquiry_opened.emit(title)
                self.scraper.scrape_data(self.fields)
            else:
                self.enquiry_failed.emit()
            self.scraper.close_browser()
            
            # Reset the app after the process is done
            self.reset_app()

        threading.Thread(target=scrape_thread, daemon=True).start()
    
    def reset_app(self):
        # Reset GUI elements
        self.url_entry.clear()
        self.team_combo.setCurrentIndex(0)
        self.start_button.setEnabled(True)
        self.resume_button.setEnabled(False)

        # Reinitialize the scraper
        if self.scraper.driver:
            self.scraper.close_browser()
        self.scraper = Scraper(self.driver_path)

        print("Application has been reset.")