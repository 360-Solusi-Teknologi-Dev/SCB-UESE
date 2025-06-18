from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QComboBox, QFormLayout, QDialogButtonBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,QTreeWidget, QTreeWidgetItem
)



from core import presets  # Import the presets module for managing preset data

class PresetManager(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Presets")
        self.setFixedSize(800, 500)

        # Tree widget for Team > Screen > Tab
        self.preset_tree = QTreeWidget()
        self.preset_tree.setHeaderLabels(["Team / Screen / Tab"])
        self.preset_tree.setColumnCount(1)

        self.load_presets()

        # Buttons
        self.add_button = QPushButton("Add Preset")
        self.edit_button = QPushButton("Edit Preset")
        self.delete_button = QPushButton("Delete Preset")

        # Field Table (initially empty)
        self.fields_table = QTableWidget(0, 4)
        self.fields_table.setHorizontalHeaderLabels(["Field Name", "Type", "Selector", "Use?"])
        self.fields_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.fields_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Layouts
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Preset Navigator:"))
        layout.addWidget(self.preset_tree)
        layout.addLayout(button_layout)
        layout.addWidget(QLabel("Fields:"))
        layout.addWidget(self.fields_table)
        self.setLayout(layout)

        # Connections
        self.preset_tree.itemClicked.connect(self.on_tree_item_clicked)
        self.add_button.clicked.connect(self.add_preset)
        self.edit_button.clicked.connect(self.edit_preset)
        self.delete_button.clicked.connect(self.delete_preset)

    def load_presets(self):
        self.preset_tree.clear()
        all_presets = presets.load_presets()

        for team, screens in all_presets.items():
            team_item = QTreeWidgetItem([team])
            for screen, tabs in screens.items():
                screen_item = QTreeWidgetItem([screen])
                for tab in tabs:
                    tab_item = QTreeWidgetItem([tab])
                    screen_item.addChild(tab_item)
                team_item.addChild(screen_item)
            self.preset_tree.addTopLevelItem(team_item)

    def on_tree_item_clicked(self, item):
        """When user selects a tab node, load its fields."""
        if not item.parent() or not item.parent().parent():
            return  # Only proceed if it's a tab level node

        tab = item.text(0)
        screen = item.parent().text(0)
        team = item.parent().parent().text(0)

        fields = presets.get_fields(team, screen, tab)
        self.populate_fields_table(fields)

    def populate_fields_table(self, fields):
        self.fields_table.setRowCount(0)
        for name, data in fields.items():
            if name == "iframe":
                continue  # Skip iframe selector
            row = self.fields_table.rowCount()
            self.fields_table.insertRow(row)
            self.fields_table.setItem(row, 0, QTableWidgetItem(name))
            self.fields_table.setItem(row, 1, QTableWidgetItem(data.get("type", "")))

            if data.get("type") == "css":
                selector = data.get("selector", "")
            elif data.get("type") == "table_lookup":
                selector = f"{data.get('table_id', '')} | {data.get('label', '')}"
            else:
                selector = ""
            self.fields_table.setItem(row, 2, QTableWidgetItem(selector))

            use_item = QTableWidgetItem()
            use_item.setCheckState(Qt.Checked if data.get("enabled", True) else Qt.Unchecked)
            self.fields_table.setItem(row, 3, use_item)

    
    def add_preset(self):
        form = PresetForm(self)
        if form.exec() == QDialog.Accepted:
            data = form.get_data()
            if not data:
                return  # Validation failed in form

            team = data["team"]
            screen = data["screen"]
            tab = data["tab"]
            fields = data["fields"]

            all_presets = presets.load_presets()

            if team not in all_presets:
                all_presets[team] = {}
            if screen not in all_presets[team]:
                all_presets[team][screen] = {}
            if tab in all_presets[team][screen]:
                QMessageBox.warning(self, "Preset Exists", f"{team} > {screen} > {tab} already exists.")
                return

            all_presets[team][screen][tab] = fields
            presets.save_presets(all_presets)
            self.load_presets()
            QMessageBox.information(self, "Success", f"Preset for {team} > {screen} > {tab} added.")


    
    def edit_preset(self):
        item = self.preset_tree.currentItem()
        if not item or not item.parent() or not item.parent().parent():
            QMessageBox.warning(self, "Selection Error", "Please select a tab to edit.")
            return

        tab = item.text(0)
        screen = item.parent().text(0)
        team = item.parent().parent().text(0)

        existing_fields = presets.get_fields(team, screen, tab)

        form = PresetForm(self)
        form.team_input.setText(team)
        form.screen_input.setText(screen)
        form.tab_input.setText(tab)
        form.team_input.setDisabled(True)
        form.screen_input.setDisabled(True)
        form.tab_input.setDisabled(True)

        # Load existing fields
        for name, data in existing_fields.items():
            row = form.fields_table.rowCount()
            form.fields_table.insertRow(row)
            form.fields_table.setItem(row, 0, QTableWidgetItem(name))
            form.fields_table.setItem(row, 1, QTableWidgetItem(data.get("type", "")))

            if data.get("type") == "css":
                selector = data.get("selector", "")
            elif data.get("type") == "table_lookup":
                selector = f"{data.get('table_id', '')} | {data.get('label', '')}"
            else:
                selector = ""

            form.fields_table.setItem(row, 2, QTableWidgetItem(selector))

        if form.exec() == QDialog.Accepted:
            data = form.get_data()
            if data is None:
                return

            # Save updated fields
            presets.add_or_update_fields(team, screen, tab, data["fields"])
            QMessageBox.information(self, "Success", f"Preset updated for {team} > {screen} > {tab}")
            self.load_presets()

        
    def delete_preset(self):
        QMessageBox.information(self, "Not Implemented", "Deleting presets will be implemented next.")





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

            # Duplicate field name check
            for r in range(self.fields_table.rowCount()):
                if self.fields_table.item(r, 0).text() == name:
                    QMessageBox.warning(dialog, "Duplicate Field", f"Field '{name}' already exists.")
                    return

            row = self.fields_table.rowCount()
            self.fields_table.insertRow(row)
            self.fields_table.setItem(row, 0, QTableWidgetItem(name))
            self.fields_table.setItem(row, 1, QTableWidgetItem(type_))
            self.fields_table.setItem(row, 2, QTableWidgetItem(
                selector if type_ == "css" else f"{selector} | {label}"
            ))

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