from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QComboBox, QFormLayout, QDialogButtonBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QListWidget, QListWidgetItem
)

from core import presets  # Import the presets module for managing preset data

class PresetManager(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Presets")
        self.setFixedSize(600, 400)

        # List of presets
        self.preset_list = QListWidget()
        self.load_presets()

        # Buttons for managing presets
        self.add_button = QPushButton("Add Preset")
        self.edit_button = QPushButton("Edit Preset")
        self.delete_button = QPushButton("Delete Preset")

        # Layout for buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)

        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Presets:"))
        layout.addWidget(self.preset_list)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Connect buttons to their respective methods
        self.add_button.clicked.connect(self.add_preset)
        self.edit_button.clicked.connect(self.edit_preset)
        self.delete_button.clicked.connect(self.delete_preset)

    def load_presets(self):
        """Load presets into the list widget."""
        self.preset_list.clear()
        for team_name in presets.get_team_names():
            self.preset_list.addItem(team_name)

    def add_preset(self):
        """Add a new preset."""
        form = PresetForm(self)
        if form.exec() == QDialog.Accepted:
            team_name, field_name, field_data = form.get_data()
            presets.add_or_update_team(team_name, {field_name: field_data})
            self.load_presets()

    def edit_preset(self):
        """Edit an existing preset."""
        selected_item = self.preset_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Error", "Please select a preset to edit.")
            return

        team_name = selected_item.text()
        fields = presets.get_fields_for_team(team_name)

        form = PresetForm(self, team_name, fields)
        if form.exec() == QDialog.Accepted:
            team_name, field_name, field_data = form.get_data()
            presets.update_field(team_name, field_name, field_data)
            self.load_presets()

    def delete_preset(self):
        """Delete a preset."""
        selected_item = self.preset_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Error", "Please select a preset to delete.")
            return

        team_name = selected_item.text()
        confirm = QMessageBox.question(
            self, "Confirm Delete", f"Are you sure you want to delete the preset '{team_name}'?"
        )
        if confirm == QMessageBox.Yes:
            presets.remove_team(team_name)
            self.load_presets()


class PresetForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preset Form")
        self.setMinimumSize(600, 500)

        self.team_input = QLineEdit()
        self.screen_input = QLineEdit()
        self.tab_input = QLineEdit()
        self.iframe_selector_input = QLineEdit()

        form_layout = QFormLayout()
        form_layout.addRow("Team:", self.team_input)
        form_layout.addRow("Screen:", self.screen_input)
        form_layout.addRow("Tab:", self.tab_input)
        form_layout.addRow("Iframe Selector (optional):", self.iframe_selector_input)

        # Field Table
        self.fields_table = QTableWidget(0, 3)
        self.fields_table.setHorizontalHeaderLabels(["Field Name", "Type", "Selector"])
        self.fields_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.fields_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.fields_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Field buttons
        self.add_field_button = QPushButton("Add Field")
        self.edit_field_button = QPushButton("Edit Selected")
        self.remove_field_button = QPushButton("Remove Selected")

        field_buttons_layout = QHBoxLayout()
        field_buttons_layout.addWidget(self.add_field_button)
        field_buttons_layout.addWidget(self.edit_field_button)
        field_buttons_layout.addWidget(self.remove_field_button)

        self.add_field_button.clicked.connect(self.add_field)
        self.edit_field_button.clicked.connect(self.edit_selected_field)
        self.remove_field_button.clicked.connect(self.remove_selected_field)

        # Dialog buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        # Assemble layout
        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(QLabel("Fields:"))
        layout.addWidget(self.fields_table)
        layout.addLayout(field_buttons_layout)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

    def add_field(self):
        from PySide6.QtWidgets import QDialog, QFormLayout, QDialogButtonBox

        dialog = QDialog(self)
        dialog.setWindowTitle("Add Field")
        layout = QFormLayout(dialog)

        field_name = QLineEdit()
        field_type = QComboBox()
        field_type.addItems(["css", "table_lookup"])
        field_selector = QLineEdit()
        label_input = QLineEdit()

        layout.addRow("Field Name:", field_name)
        layout.addRow("Type:", field_type)
        layout.addRow("Selector / Table ID:", field_selector)
        layout.addRow("Label (only for table_lookup):", label_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)

        def accept():
            name = field_name.text().strip()
            type_ = field_type.currentText()
            selector = field_selector.text().strip()
            label = label_input.text().strip()

            if not name or not selector:
                QMessageBox.warning(dialog, "Input Error", "Field name and selector are required.")
                return

            row = self.fields_table.rowCount()
            self.fields_table.insertRow(row)
            self.fields_table.setItem(row, 0, QTableWidgetItem(name))
            self.fields_table.setItem(row, 1, QTableWidgetItem(type_))
            self.fields_table.setItem(row, 2, QTableWidgetItem(selector if type_ == "css" else f"{selector} | {label}"))

            dialog.accept()

        buttons.accepted.connect(accept)
        buttons.rejected.connect(dialog.reject)

        dialog.exec()

    def edit_selected_field(self):
        selected = self.fields_table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Selection Error", "Please select a field to edit.")
            return

        name = self.fields_table.item(selected, 0).text()
        type_ = self.fields_table.item(selected, 1).text()
        raw_selector = self.fields_table.item(selected, 2).text()

        selector = raw_selector
        label = ""

        if type_ == "table_lookup" and " | " in raw_selector:
            selector, label = raw_selector.split(" | ", 1)

        # Reuse add dialog but prefill
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Field")
        layout = QFormLayout(dialog)

        field_name = QLineEdit(name)
        field_type = QComboBox()
        field_type.addItems(["css", "table_lookup"])
        field_type.setCurrentText(type_)
        field_selector = QLineEdit(selector)
        label_input = QLineEdit(label)

        layout.addRow("Field Name:", field_name)
        layout.addRow("Type:", field_type)
        layout.addRow("Selector / Table ID:", field_selector)
        layout.addRow("Label (only for table_lookup):", label_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)

        def accept():
            new_name = field_name.text().strip()
            new_type = field_type.currentText()
            new_selector = field_selector.text().strip()
            new_label = label_input.text().strip()

            if not new_name or not new_selector:
                QMessageBox.warning(dialog, "Input Error", "Field name and selector are required.")
                return

            self.fields_table.setItem(selected, 0, QTableWidgetItem(new_name))
            self.fields_table.setItem(selected, 1, QTableWidgetItem(new_type))
            sel_value = new_selector if new_type == "css" else f"{new_selector} | {new_label}"
            self.fields_table.setItem(selected, 2, QTableWidgetItem(sel_value))

            dialog.accept()

        buttons.accepted.connect(accept)
        buttons.rejected.connect(dialog.reject)
        dialog.exec()

    def remove_selected_field(self):
        selected = self.fields_table.currentRow()
        if selected >= 0:
            self.fields_table.removeRow(selected)

    def get_data(self):
        """Return all entered data in JSON-compatible format."""
        team = self.team_input.text().strip()
        screen = self.screen_input.text().strip()
        tab = self.tab_input.text().strip()
        iframe_selector = self.iframe_selector_input.text().strip()

        if not team or not screen or not tab:
            QMessageBox.warning(self, "Input Error", "Team, Screen, and Tab are required.")
            return None

        fields = {}
        for row in range(self.fields_table.rowCount()):
            name = self.fields_table.item(row, 0).text()
            type_ = self.fields_table.item(row, 1).text()
            raw = self.fields_table.item(row, 2).text()

            if type_ == "css":
                fields[name] = {"type": "css", "selector": raw}
            elif type_ == "table_lookup":
                if " | " in raw:
                    table_id, label = raw.split(" | ", 1)
                else:
                    table_id, label = raw, ""
                fields[name] = {"type": "table_lookup", "table_id": table_id, "label": label}

        if iframe_selector:
            fields["iframe"] = {"type": "css", "selector": iframe_selector}

        return {
            "team": team,
            "screen": screen,
            "tab": tab,
            "fields": fields
        }