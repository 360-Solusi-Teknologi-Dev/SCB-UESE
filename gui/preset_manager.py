from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QMessageBox, QComboBox, QFormLayout, QDialogButtonBox
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
    def __init__(self, parent=None, team_name=None, fields=None):
        super().__init__(parent)
        self.setWindowTitle("Preset Form")
        self.setFixedSize(400, 300)

        self.team_name = team_name
        self.fields = fields or {}

        # Form layout
        form_layout = QFormLayout()

        # Team name
        self.team_name_input = QLineEdit(self)
        if team_name:
            self.team_name_input.setText(team_name)
        form_layout.addRow("Team Name:", self.team_name_input)

        # Field name
        self.field_name_input = QLineEdit(self)
        form_layout.addRow("Field Name:", self.field_name_input)

        # Field type
        self.field_type_combo = QComboBox(self)
        self.field_type_combo.addItems(["css", "table_lookup"])
        form_layout.addRow("Field Type:", self.field_type_combo)

        # CSS Selector or Table ID
        self.selector_input = QLineEdit(self)
        form_layout.addRow("CSS Selector / Table ID:", self.selector_input)

        # Label (for table_lookup)
        self.label_input = QLineEdit(self)
        form_layout.addRow("Label (for table_lookup):", self.label_input)

        # Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel, self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        # Main layout
        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

    def get_data(self):
        """Return the data entered in the form."""
        team_name = self.team_name_input.text().strip()
        field_name = self.field_name_input.text().strip()
        field_type = self.field_type_combo.currentText()
        selector = self.selector_input.text().strip()
        label = self.label_input.text().strip()

        field_data = {"type": field_type}
        if field_type == "css":
            field_data["selector"] = selector
        elif field_type == "table_lookup":
            field_data["table_id"] = selector
            field_data["label"] = label

        return team_name, field_name, field_data