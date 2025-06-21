import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from gui.main_gui import MainGUIWithSidebar  # Import the Main GUI class

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("scb-logo.ico"))  # Set the application icon
    driver_path = "msedgedriver.exe"  # Path to the WebDriver executable
    window = MainGUIWithSidebar(driver_path)  # Initialize the Main GUI with the driver path
    window.show()  # Show the main window
    sys.exit(app.exec())  # Start the application event loop