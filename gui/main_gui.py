# gui/main_gui.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QPushButton, QFrame, QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from gui.screens.scraping_screen import ScrapingScreen
from gui.preset_manager import PresetManager
from core import presets


class MainGUIWithSidebar(QWidget):
    def __init__(self, driver_path):
        super().__init__()
        self.setWindowTitle("Universal Enquiry Scraping")
        self.setFixedSize(1000, 600)

        self.stack = QStackedWidget()

        # Screens
        self.scraping_screen = ScrapingScreen(driver_path)
        self.stack.addWidget(self.scraping_screen)  # index 0

        # Sidebar menu
        sidebar = QVBoxLayout()
        # Create vertical line separator
        vline = QFrame()
        vline.setFrameShape(QFrame.VLine)
        vline.setFrameShadow(QFrame.Sunken)
        vline.setLineWidth(1)
        # Add logo at the top
        logo_label = QLabel()
        pixmap = QPixmap("standard-chartered.png")  # Make sure this path is correct
        pixmap = pixmap.scaledToWidth(150)  # Resize to fit the sidebar width
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        sidebar.addWidget(logo_label)
        
        btn_scrape = QPushButton("🔍 Scraping")
        btn_scrape.clicked.connect(lambda: self.stack.setCurrentWidget(self.scraping_screen))
        sidebar.addWidget(btn_scrape)
        sidebar.addStretch()
        
        btn_presets = QPushButton("🛠️ Manage Presets")
        btn_presets.clicked.connect(self.open_preset_manager)
        sidebar.addWidget(btn_presets)


        sidebar_frame = QFrame()
        sidebar_frame.setFixedWidth(200)
        sidebar_frame.setLayout(sidebar)

        layout = QHBoxLayout(self)
        layout.addWidget(sidebar_frame)
        layout.addWidget(vline)
        layout.addWidget(self.stack)
    
    def open_preset_manager(self):
        dlg = PresetManager(self)
        dlg.exec()

        # Optional: refresh scraping screen team combo if necessary
        self.scraping_screen.team_combo.clear()
        self.scraping_screen.team_combo.addItems(presets.get_team_names())

