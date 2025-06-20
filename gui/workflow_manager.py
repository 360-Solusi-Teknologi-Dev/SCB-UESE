from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout, QMessageBox, QDialog
from core.workflow import Workflow, WorkflowStep
from gui.step_editor import StepEditorDialog

class WorkflowManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Workflow Manager")
        self.workflow = Workflow(name="Default Workflow", steps=[])
        
        # Initialize the UI components
        self.step_list = QListWidget()
        self.add_btn = QPushButton("Add Step")
        self.edit_btn = QPushButton("Edit Step")
        self.delete_btn = QPushButton("Delete Step")
        self.save_btn = QPushButton("Save Workflow")
        self.move_up_btn = QPushButton("Move Up")
        self.move_down_btn = QPushButton("Move Down")


        layout = QVBoxLayout()
        layout.addWidget(self.step_list)
        
        # Create a horizontal layout for the buttons
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.move_up_btn)
        btn_layout.addWidget(self.move_down_btn)
        layout.addLayout(btn_layout)

        layout.addWidget(self.save_btn)
        self.setLayout(layout)
        
        # Connect buttons to their respective methods
        self.add_btn.clicked.connect(self.add_step)
        self.edit_btn.clicked.connect(self.edit_step)
        self.delete_btn.clicked.connect(self.delete_step)
        self.save_btn.clicked.connect(self.save_workflow)
        self.move_up_btn.clicked.connect(self.move_step_up)
        self.move_down_btn.clicked.connect(self.move_step_down)

        self.load_workflow()
    
    def load_workflow(self):
        try:
            self.workflow = Workflow.load_from_file("workflow.json")
            self._refresh_step_list()
        except Exception as e:
            QMessageBox.warning(self, "Load Error", f"Could not load workflow: {e}")
    
    
    def move_step_up(self):
        row = self.step_list.currentRow()
        if row > 0:
            self.workflow.steps[row - 1], self.workflow.steps[row] = self.workflow.steps[row], self.workflow.steps[row - 1]
            self._refresh_step_list()
            self.step_list.setCurrentRow(row - 1)

    def move_step_down(self):
        row = self.step_list.currentRow()
        if row < len(self.workflow.steps) - 1:
            self.workflow.steps[row + 1], self.workflow.steps[row] = self.workflow.steps[row], self.workflow.steps[row + 1]
            self._refresh_step_list()
            self.step_list.setCurrentRow(row + 1)



    def add_step(self):
        dialog = StepEditorDialog(self)
        if dialog.exec() == QDialog.Accepted:
            step = dialog.get_step()
            self.workflow.steps.append(step)
            self._refresh_step_list()

    def edit_step(self):
        row = self.step_list.currentRow()
        if row < 0:
            return

        old_step = self.workflow.steps[row]
        dialog = StepEditorDialog(self, old_step)
        if dialog.exec() == QDialog.Accepted:
            self.workflow.steps[row] = dialog.get_step()
            self._refresh_step_list()

    def delete_step(self):
        current = self.step_list.currentRow()
        if current >= 0:
            del self.workflow.steps[current]
            self.step_list.takeItem(current)
    
    def _refresh_step_list(self):
        self.step_list.clear()
        for i, step in enumerate(self.workflow.steps):
            self.step_list.addItem(f"{i+1}. {step.action} → {step.selector_key}")

    def save_workflow(self):
        self.workflow.save_to_file("workflow.json")
        QMessageBox.information(self, "Saved", "Workflow saved successfully!")
