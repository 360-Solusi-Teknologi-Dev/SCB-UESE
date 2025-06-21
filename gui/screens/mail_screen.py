# gui/screens/mail_screen.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QFileDialog, QMessageBox, QTextEdit
)
import os
from core.mailer import generate_letters_from_excel  # ✅ ini sudah benar

class MailGenerationScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())

        self.excel_path = None
        self.template_path = None
        self.output_dir = None

        self.label = QLabel("📩 Generate Word Letters from Excel + Template")
        self.layout().addWidget(self.label)

        self.btn_select_excel = QPushButton("Select Excel File (e.g. Comparison_Result.xlsx)")
        self.btn_select_excel.clicked.connect(self.select_excel)
        self.layout().addWidget(self.btn_select_excel)

        self.btn_select_template = QPushButton("Select Word Template (.docx)")
        self.btn_select_template.clicked.connect(self.select_template)
        self.layout().addWidget(self.btn_select_template)

        self.btn_select_output = QPushButton("Select Output Folder")
        self.btn_select_output.clicked.connect(self.select_output_dir)
        self.layout().addWidget(self.btn_select_output)

        self.btn_generate = QPushButton("Generate Letters")
        self.btn_generate.clicked.connect(self.generate_letters)
        self.btn_generate.setEnabled(False)
        self.layout().addWidget(self.btn_generate)

        self.result_log = QTextEdit()
        self.result_log.setReadOnly(True)
        self.layout().addWidget(self.result_log)

    def select_excel(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Excel File", "", "Excel Files (*.xlsx *.xls)")
        if path:
            self.excel_path = path
            self.btn_select_excel.setText(f"✅ Excel: {os.path.basename(path)}")
            self.check_ready()

    def select_template(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Word Template", "", "Word Files (*.docx)")
        if path:
            self.template_path = path
            self.btn_select_template.setText(f"✅ Template: {os.path.basename(path)}")
            self.check_ready()

    def select_output_dir(self):
        path = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if path:
            self.output_dir = path
            self.btn_select_output.setText(f"📁 Output: {path}")
            self.check_ready()

    def check_ready(self):
        self.btn_generate.setEnabled(
            bool(self.excel_path and self.template_path and self.output_dir)
        )

    def generate_letters(self):
        try:
            msg = generate_letters_from_excel(
                self.excel_path,
                self.template_path,
                self.output_dir
            )
            self.result_log.setText("✅ Success:\n" + msg)
            QMessageBox.information(self, "Done", msg)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
