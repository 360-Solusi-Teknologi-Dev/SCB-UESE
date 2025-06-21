from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QTextEdit, QMessageBox
from core.comparer import compare_excel_files
import os

class ComparingScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())

        self.label = QLabel("📊 Compare two Excel files")
        self.layout().addWidget(self.label)

        self.btn_load_file1 = QPushButton("Select Reference File (Excel)")
        self.btn_load_file1.clicked.connect(self.load_file1)
        self.layout().addWidget(self.btn_load_file1)

        self.btn_load_file2 = QPushButton("Select Target File (Excel)")
        self.btn_load_file2.clicked.connect(self.load_file2)
        self.layout().addWidget(self.btn_load_file2)

        self.compare_button = QPushButton("Compare Files")
        self.compare_button.clicked.connect(self.compare_files)
        self.compare_button.setEnabled(False)
        self.layout().addWidget(self.compare_button)

        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        self.layout().addWidget(self.result_area)

        self.file1_path = None
        self.file2_path = None

    def load_file1(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Reference Excel File", "", "Excel Files (*.xlsx *.xls)")
        if path:
            self.file1_path = path
            self.btn_load_file1.setText(f"✅ Reference: {os.path.basename(path)}")
            self.check_ready()

    def load_file2(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Target Excel File", "", "Excel Files (*.xlsx *.xls)")
        if path:
            self.file2_path = path
            self.btn_load_file2.setText(f"✅ Target: {os.path.basename(path)}")
            self.check_ready()

    def check_ready(self):
        self.compare_button.setEnabled(bool(self.file1_path and self.file2_path))

    def compare_files(self):
        try:
            output_path, log_text = compare_excel_files(self.file1_path, self.file2_path)
            self.result_area.setText(f"✅ Comparison completed.\n\n{log_text}")
            QMessageBox.information(self, "Success", f"Comparison result saved to:\n{output_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
