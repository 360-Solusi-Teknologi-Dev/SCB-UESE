import json
import os

PRESET_FILE = "presets.json"
WORKFLOW_PATH = "workflow.json"

def load_presets():
    if not os.path.exists(PRESET_FILE):
        return []
    with open(PRESET_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def load_workflows():
    with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
    
def get_fields(team, screen, tab):
    presets = load_presets()
    try:
        return presets[team][screen][tab]
    except KeyError:
        return {}

def save_presets(presets):
    with open(PRESET_FILE, "w", encoding="utf-8") as f:
        json.dump(presets, f, indent=4)

def get_workflow(team, screen, tab):
    workflows = load_workflows()
    for wf in workflows:
        if wf["team"] == team and wf["screen"] == screen and wf["tab"] == tab:
            return wf["steps"]
    return []

def get_team_names():
    presets = load_presets()
    return list(presets.keys())


def get_available_teams():
    return list(load_presets().keys())

def get_screens_for_team(team):
    return list(load_presets().get(team, {}).keys())

def get_tabs_for_screen(team, screen):
    return list(load_presets().get(team, {}).get(screen, {}).keys())
