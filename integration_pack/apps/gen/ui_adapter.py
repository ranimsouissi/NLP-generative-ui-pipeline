
# Mapping profils -> contraintes UI/UX
from copy import deepcopy

VARK_UI = {
    "V": {"layout": "two_column_visual_first", "components": ["diagram", "stepper"]},
    "A": {"layout": "single_column", "components": ["audio_hint", "recap"]},
    "R": {"layout": "single_column", "components": ["definitions", "table"]},
    "K": {"layout": "lab_mode", "components": ["checklist", "mini_project"]},
}

def ui_from_profile(vark: str, mbti: str):
    base = deepcopy(VARK_UI.get(vark, VARK_UI["R"]))
    base["verbosity"] = "high" if mbti.startswith("EN") else "medium"
    base["tone"] = "supportive" if "F" in mbti else "concise"
    return base
