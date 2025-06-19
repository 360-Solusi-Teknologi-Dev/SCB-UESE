@dataclass
class WorkflowStep:
    action: str  # "click", "input", "wait", "extract"
    selector_key: str  # E.g., "EUC/Relationship Individual/Main/RELID"
    params: dict = field(default_factory=dict)

@dataclass
class Workflow:
    name: str
    steps: List[WorkflowStep]

    def to_dict(self): ...
    @classmethod
    def from_dict(cls, data): ...
    def save_to_file(self, path): ...
    @classmethod
    def load_from_file(cls, path): ...
