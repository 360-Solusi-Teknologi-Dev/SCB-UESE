from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QComboBox,
    QMessageBox, QHBoxLayout, QToolButton, QFormLayout, QSpacerItem, QSizePolicy, QGroupBox
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal
from core.scraper import Scraper
from core import presets
from gui.preset_manager import PresetManager
import threading

class ScrapingScreen(QWidget):
    enquiry_opened = Signal(str)
    enquiry_failed = Signal()

    def __init__(self, driver_path):
        super().__init__()
        self.driver_path = driver_path
        self.scraper = Scraper(driver_path)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Enquiry Scraper")
        self.setMaximumHeight(350)  # Slight limit to avoid extra vertical space

        # === TOP RIGHT SETTINGS BUTTON ===
        self.settings_button = QToolButton()
        self.settings_button.setIcon(QIcon("settings.png"))  # Path to cog icon
        self.settings_button.setToolTip("Manage Presets")
        self.settings_button.clicked.connect(self.open_preset_manager)

        top_bar = QHBoxLayout()
        top_bar.addStretch()
        top_bar.addWidget(self.settings_button)

        # === FORM INPUTS ===
        self.url_entry = QLineEdit()
        self.team_combo = QComboBox()
        self.team_combo.addItems(presets.get_team_names())
        
        # Interchangeable input layout for other screens
        form_layout = QFormLayout()
        form_layout.addRow("Web App URL:", self.url_entry)        # <-- Interchangeable: URL input
        form_layout.addRow("Team Preset:", self.team_combo)       # <-- Interchangeable: Team selector

        # Input File browse
        self.file_path_entry = QLineEdit()
        self.file_path_entry.setReadOnly(True)
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_file)

        file_layout = QHBoxLayout()
        file_layout.addWidget(self.file_path_entry)
        file_layout.addWidget(self.browse_button)
        form_layout.addRow("Input File:", file_layout)
        
        # === ACTION BUTTONS ===
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.resume_button = QPushButton("Resume")
        self.reset_button = QPushButton("Reset")
        self.resume_button.setEnabled(False)

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.resume_button)
        button_layout.addWidget(self.reset_button)
        
        # Test Workflow button
        self.test_button = QPushButton("Test Workflow")
        self.test_button.setToolTip("Load the URL and test the selected team's workflow")
        button_layout.addWidget(self.test_button)
        self.test_button.clicked.connect(self.test_workflow)


        # GroupBox for visual grouping (optional but helps with modularity)
        input_group = QGroupBox("Scraping Configuration")  # <-- Interchangeable: Rename for other screens
        input_group.setLayout(form_layout)

        # === MAIN LAYOUT ===
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_bar)
        main_layout.addWidget(input_group)
        main_layout.addLayout(button_layout)
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))  # Pushes UI up
        self.setLayout(main_layout)

        # === BUTTON CONNECTIONS ===
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

    def browse_file(self):
        from PySide6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*.*)")
        if file_path:
            self.file_path_entry.setText(file_path)
    
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
            self.reset_app()

        threading.Thread(target=scrape_thread, daemon=True).start()
        
    def test_workflow(self):
        url = self.url_entry.text().strip()
        if not url:
            QMessageBox.critical(self, "Input Error", "Please enter a valid URL.")
            return
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url  # use http for local test

        team = self.team_combo.currentText()
        screen = "Test Screen"  # hardcoded for now, or use a dropdown later
        tab = "Tab 1"

        from core import presets
        steps = presets.get_workflow(team, screen, tab)
        preset_data = presets.load_presets()  # ✅ THIS LINE FIXES THE ERROR

        print(f"Testing workflow for Team: '{team}', Screen: '{screen}', Tab: '{tab}'")
        print(f"URL: {url}")
        print(f"Loaded {len(steps)} workflow steps.")

        if not steps:
            QMessageBox.warning(self, "No Workflow", f"No workflow defined for team '{team}' / screen '{screen}' / tab '{tab}'.")
            return

        def test_thread():
            print("Starting test thread...")
            self.test_button.setEnabled(False)
            print("Starting browser...")
            self.scraper.start_browser(url)
            self.scraper.driver.implicitly_wait(2)

            from core.automation_runner import run_workflow
            try:
                results = run_workflow(
                    driver=self.scraper.driver,
                    workflow=steps,
                    context={},
                    presets=preset_data,  # ✅ PASS THE LOADED PRESETS HERE
                    team=team,
                    screen=screen,
                    tab=tab
                )
                print("Workflow run completed, processing results...")
                result_msg = "\n".join(f"{k}: {v}" for k, v in results.items())
            except Exception as e:
                print(f"Error during workflow run: {e}")
                result_msg = f"Error: {str(e)}"

            def show_results():
                print("Workflow extracted results:", results if 'results' in locals() else 'No results')
                QMessageBox.information(self, "Test Results", result_msg)
                self.test_button.setEnabled(True)

            print("Quitting browser...")
            self.scraper.driver.quit()
            self.scraper.driver = None
            self.scraper = Scraper(self.driver_path)

            self.call_in_main(show_results)

        threading.Thread(target=test_thread, daemon=True).start()





    def call_in_main(self, func):
        # Utility to call a UI function from thread
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, func)

    
    def reset_app(self):
        self.url_entry.clear()
        self.team_combo.setCurrentIndex(0)
        self.start_button.setEnabled(True)
        self.resume_button.setEnabled(False)

        if self.scraper.driver:
            self.scraper.close_browser()
        self.scraper = Scraper(self.driver_path)

        print("Application has been reset.")
