from dataclasses import dataclass, field, asdict
from typing import List
import json

@dataclass
class WorkflowStep:
    action: str  # e.g., "click", "input", "wait", "extract"
    selector_key: str  # e.g., "EUC/Relationship Individual/Main/RELID"
    params: dict = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data):
        return WorkflowStep(
            action=data["action"],
            selector_key=data["selector_key"],
            params=data.get("params", {})
        )

@dataclass
class Workflow:
    name: str
    steps: List[WorkflowStep] = field(default_factory=list)

    def to_dict(self):
        return {
            "name": self.name,
            "steps": [step.to_dict() for step in self.steps]
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name", "Unnamed Workflow"),
            steps=[WorkflowStep.from_dict(step) for step in data.get("steps", [])]
        )

    def save_to_file(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_file(cls, path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)
