from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QFormLayout
)
from PySide6.QtCore import Qt
from core.workflow import WorkflowStep
from core.presets import load_presets  # assumes this returns a dict

class StepEditorDialog(QDialog):
    def __init__(self, parent=None, step: WorkflowStep = None):
        super().__init__(parent)
        self.setWindowTitle("Step Editor")
        self.presets = load_presets()  # {team: {screen: {tab: {field: selector}}}}

        self.action_combo = QComboBox()
        self.action_combo.addItems(["click", "input", "wait", "extract"])
        self.team_combo = QComboBox()
        self.screen_combo = QComboBox()
        self.tab_combo = QComboBox()
        self.field_combo = QComboBox()
        self.param_input = QLineEdit()

        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")

        self._populate_team_combo()

        layout = QFormLayout()
        layout.addRow("Action", self.action_combo)
        layout.addRow("Team", self.team_combo)
        layout.addRow("Screen", self.screen_combo)
        layout.addRow("Tab", self.tab_combo)
        layout.addRow("Field", self.field_combo)
        layout.addRow("Parameter", self.param_input)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

        self._connect_signals()

        if step:
            self.load_step(step)

    def _connect_signals(self):
        self.team_combo.currentTextChanged.connect(self._populate_screen_combo)
        self.screen_combo.currentTextChanged.connect(self._populate_tab_combo)
        self.tab_combo.currentTextChanged.connect(self._populate_field_combo)
        self.action_combo.currentTextChanged.connect(self._update_param_field)
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def _populate_team_combo(self):
        self.team_combo.clear()
        self.team_combo.addItems(self.presets.keys())
        self._populate_screen_combo()

    def _populate_screen_combo(self):
        team = self.team_combo.currentText()
        screens = self.presets.get(team, {})
        self.screen_combo.clear()
        self.screen_combo.addItems(screens.keys())
        self._populate_tab_combo()

    def _populate_tab_combo(self):
        team = self.team_combo.currentText()
        screen = self.screen_combo.currentText()
        tabs = self.presets.get(team, {}).get(screen, {})
        self.tab_combo.clear()
        self.tab_combo.addItems(tabs.keys())
        self._populate_field_combo()

    def _populate_field_combo(self):
        team = self.team_combo.currentText()
        screen = self.screen_combo.currentText()
        tab = self.tab_combo.currentText()
        fields = self.presets.get(team, {}).get(screen, {}).get(tab, {})
        self.field_combo.clear()
        self.field_combo.addItems(fields.keys())

    def _update_param_field(self):
        action = self.action_combo.currentText()
        if action == "input":
            self.param_input.setPlaceholderText("Value to input")
            self.param_input.setEnabled(True)
        elif action == "wait":
            self.param_input.setPlaceholderText("Time in seconds")
            self.param_input.setEnabled(True)
        else:
            self.param_input.setText("")
            self.param_input.setEnabled(False)

    def get_step(self) -> WorkflowStep:
        action = self.action_combo.currentText()
        team = self.team_combo.currentText()
        screen = self.screen_combo.currentText()
        tab = self.tab_combo.currentText()
        field = self.field_combo.currentText()
        selector_key = f"{team}/{screen}/{tab}/{field}"
        params = {}

        if action == "input":
            params["value"] = self.param_input.text()
        elif action == "wait":
            params["seconds"] = float(self.param_input.text() or 0)

        return WorkflowStep(action=action, selector_key=selector_key, params=params)

    def load_step(self, step: WorkflowStep):
        self.action_combo.setCurrentText(step.action)
        parts = step.selector_key.split("/")
        if len(parts) == 4:
            team, screen, tab, field = parts
            self.team_combo.setCurrentText(team)
            self.screen_combo.setCurrentText(screen)
            self.tab_combo.setCurrentText(tab)
            self.field_combo.setCurrentText(field)
        if "value" in step.params:
            self.param_input.setText(step.params["value"])
        elif "seconds" in step.params:
            self.param_input.setText(str(step.params["seconds"]))
