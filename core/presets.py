import json
import os

PRESET_FILE = "presets.json"

def load_presets():
    if not os.path.exists(PRESET_FILE):
        return []
    with open(PRESET_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_presets(presets):
    with open(PRESET_FILE, "w", encoding="utf-8") as f:
        json.dump(presets, f, indent=4)

def get_team_names():
    presets = load_presets()
    return [preset["preset_name"] for preset in presets]

def get_fields_for_team(team_name):
    presets = load_presets()
    for preset in presets:
        if preset["preset_name"] == team_name:
            return preset.get("fields", {})
    return {}

def get_table_config_for_team(team_name):
    presets = load_presets()
    for preset in presets:
        if preset["preset_name"] == team_name:
            return preset.get("table", {})
    return {}

def add_or_update_team(team_name, fields_dict, table_dict=None):
    presets = load_presets()
    for preset in presets:
        if preset["preset_name"] == team_name:
            preset["fields"] = fields_dict
            if table_dict:
                preset["table"] = table_dict
            save_presets(presets)
            return
    # If not found, add new
    new_preset = {
        "preset_name": team_name,
        "fields": fields_dict,
        "table": table_dict or {}
    }
    presets.append(new_preset)
    save_presets(presets)

def remove_team(team_name):
    presets = load_presets()
    new_presets = [preset for preset in presets if preset["preset_name"] != team_name]
    if len(new_presets) != len(presets):
        save_presets(new_presets)
        return True
    return False

def update_field(team_name, field_name, css_selector):
    presets = load_presets()
    for preset in presets:
        if preset["preset_name"] == team_name:
            preset.setdefault("fields", {})[field_name] = css_selector
            save_presets(presets)
            return True
    return False

def remove_field(team_name, field_name):
    presets = load_presets()
    for preset in presets:
        if preset["preset_name"] == team_name and field_name in preset.get("fields", {}):
            del preset["fields"][field_name]
            save_presets(presets)
            return True
    return False
