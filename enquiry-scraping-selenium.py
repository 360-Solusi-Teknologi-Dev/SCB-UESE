import sys
from PySide6.QtWidgets import QApplication
from gui.main_gui import MainGUI  # Import the Main GUI class

if __name__ == "__main__":
    app = QApplication(sys.argv)
    driver_path = "msedgedriver-135.exe"  # Path to the WebDriver executable
    window = MainGUI(driver_path)  # Initialize the Main GUI with the driver path
    window.show()  # Show the main window
    sys.exit(app.exec())  # Start the application event loop