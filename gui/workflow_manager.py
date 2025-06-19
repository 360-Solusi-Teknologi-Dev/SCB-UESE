from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout, QMessageBox, QDialog
from core.workflow import Workflow, WorkflowStep
from gui.step_editor import StepEditorDialog

class WorkflowManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Workflow Manager")
        self.workflow = Workflow(name="Default Workflow", steps=[])

        self.step_list = QListWidget()
        self.add_btn = QPushButton("Add Step")
        self.edit_btn = QPushButton("Edit Step")
        self.delete_btn = QPushButton("Delete Step")
        self.save_btn = QPushButton("Save Workflow")

        layout = QVBoxLayout()
        layout.addWidget(self.step_list)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        layout.addLayout(btn_layout)

        layout.addWidget(self.save_btn)
        self.setLayout(layout)

        self.add_btn.clicked.connect(self.add_step)
        self.edit_btn.clicked.connect(self.edit_step)
        self.delete_btn.clicked.connect(self.delete_step)
        self.save_btn.clicked.connect(self.save_workflow)

    def add_step(self):
        dialog = StepEditorDialog(self)
        if dialog.exec() == QDialog.Accepted:
            step = dialog.get_step()
            self.workflow.steps.append(step)
            self.step_list.addItem(f"{step.action} → {step.selector_key}")

    def edit_step(self):
        # TODO: Show dialog with selected step pre-filled
        pass

    def delete_step(self):
        current = self.step_list.currentRow()
        if current >= 0:
            del self.workflow.steps[current]
            self.step_list.takeItem(current)

    def save_workflow(self):
        self.workflow.save_to_file("data/workflow.json")
        QMessageBox.information(self, "Saved", "Workflow saved successfully!")
