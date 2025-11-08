import json
import os
import sys

# S'assurer que le dossier courant est dans le PYTHONPATH
sys.path.insert(0, os.path.dirname(__file__))

from prompt_transformer import build_prompt_from_profiles
from enhanced_ui_generator import generate_content

profiles = {"VARK": "V", "MBTI": "INTJ"}
features = {"ls_visual": 0.7, "pers_intuition": 0.8}
ui = {"layout": "cards", "verbosity": "compact"}

prompt = build_prompt_from_profiles(
    goal="Expliquer Gradient Descent",
    lang="fr",
    level="L3",
    profiles=profiles,
    features=features,
    ui=ui
)

content = generate_content(prompt)

print("\n== CLEFS ==")
print(list(content.keys()))

print("\n== UI CONFIG ==")
print(json.dumps(content["ui_config"], indent=2, ensure_ascii=False))

with open("ui_config_sample.json", "w", encoding="utf-8") as f:
    json.dump(content, f, indent=2, ensure_ascii=False)
print("\nFichier écrit: ui_config_sample.json")
