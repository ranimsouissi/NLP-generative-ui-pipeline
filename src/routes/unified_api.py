# src/routes/unified_api.py

import json
import pathlib
import sqlite3

from flask import Blueprint, request, jsonify
from jsonschema import validate, ValidationError
from importlib.machinery import SourceFileLoader

# ================== DÉTECTION ROBUSTE DU PROJECT_ROOT ==================

CURRENT = pathlib.Path(__file__).resolve()

# On remonte et on cherche un dossier qui contient "integration_pack"
PROJECT_ROOT = None
for p in CURRENT.parents:
    if (p / "integration_pack").exists():
        PROJECT_ROOT = p
        break

if PROJECT_ROOT is None:
    # Fallback: on suppose que le repo est deux niveaux au-dessus
    PROJECT_ROOT = CURRENT.parents[2]

PACK = PROJECT_ROOT / "integration_pack"
SCHEMAS = PACK / "data_contracts"

# ================== CHARGEMENT DES SCHÉMAS ==================

SCHEMA_CONV = json.loads((SCHEMAS / "conversations.schema.json").read_text(encoding="utf-8"))
SCHEMA_NLP = json.loads((SCHEMAS / "nlp_features.schema.json").read_text(encoding="utf-8"))
SCHEMA_REC = json.loads((SCHEMAS / "recommendation.schema.json").read_text(encoding="utf-8"))

# ================== UI ADAPTER (depuis integration_pack) ==================

ui_adapter = SourceFileLoader(
    "ui_adapter",
    str(PACK / "apps" / "gen" / "ui_adapter.py")
).load_module()
ui_from_profile = ui_adapter.ui_from_profile

# ================== IMPORTS VERS TON CODE ==================

# Profiling
try:
    from src.models.profile_generator import get_profiles_for_conversation
except ImportError:
    from profile_generator import get_profiles_for_conversation

# Prompt builder
try:
    from src.models.prompt_transformer import build_prompt_from_profiles
except ImportError:
    from prompt_transformer import build_prompt_from_profiles

# Generative UI
try:
    from src.models.enhanced_ui_generator import generate_content
except ImportError:
    from enhanced_ui_generator import generate_content

# Feature extractor (optionnel)
try:
    from src.models.feature_extractor import extract_features
except ImportError:
    try:
        from feature_extractor import extract_features
    except ImportError:
        extract_features = None

# ================== INIT FEATURE STORE (SQLite) ==================

DDL = (PACK / "feature_store" / "ddl.sql").read_text(encoding="utf-8")


def init_db(db_path=str(PROJECT_ROOT / "feature_store.db")):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.executescript(DDL)
    con.commit()
    con.close()


init_db()

# ================== BLUEPRINT ==================

unified_bp = Blueprint("unified_api", __name__)

# ================== UTILS ==================

def validate_json(payload, schema):
    try:
        validate(payload, schema)
        return True, None
    except ValidationError as e:
        return False, f"Schema error: {e.message}"


def _extract_features_stub(conv: dict) -> dict:
    turns = conv.get("turns", [])
    texts = [t.get("text", "") for t in turns if isinstance(t, dict)]
    n = max(1, len(texts))
    return {
        "avg_turn_len": sum(len(t) for t in texts) / n,
        "question_ratio": sum(1 for t in texts if "?" in t) / n,
    }


def _normalize_labels(profiles: dict):
    v = profiles.get("VARK")
    m = profiles.get("MBTI")

    if isinstance(v, dict):
        vark = v.get("label")
    else:
        vark = v

    if isinstance(m, dict):
        mbti = m.get("label")
    else:
        mbti = m

    return vark, mbti


def nlp_pipeline(conv: dict) -> dict:
    ok, err = validate_json(conv, SCHEMA_CONV)
    if not ok:
        raise ValueError(err)

    feats = extract_features(conv) if extract_features else _extract_features_stub(conv)
    prof = get_profiles_for_conversation(feats)

    out = {
        "user_id": conv["user_id"],
        "session_id": conv["session_id"],
        "features": feats,
        "profiles": prof,
    }

    ok, err = validate_json(out, SCHEMA_NLP)
    if not ok:
        raise ValueError(err)

    return out

# ================== ROUTES ==================

@unified_bp.post("/profile")
def profile():
    conv = request.get_json(force=True) or {}

    try:
        nlp_out = nlp_pipeline(conv)
        vark, mbti = _normalize_labels(nlp_out["profiles"])
        return jsonify({
            "VARK": vark,
            "MBTI": mbti,
            "scores": nlp_out["profiles"].get("scores", {})
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@unified_bp.post("/recommend")
def recommend():
    payload = request.get_json(force=True) or {}
    conv = payload.get("conversation", {})
    context = payload.get("context", {}) or {}

    try:
        # 1) NLP (features + profils)
        nlp_out = nlp_pipeline(conv)
        vark, mbti = _normalize_labels(nlp_out["profiles"])

        # 2) UI adaptée au profil
        ui = ui_from_profile(vark, mbti)

        # 3) Prompt enrichi
        prompt = build_prompt_from_profiles(
            goal=context.get("goal", "Explain topic"),
            lang=context.get("lang", "fr"),
            level=context.get("level", "L3"),
            profiles={"VARK": vark, "MBTI": mbti},
            features=nlp_out["features"],
            ui=ui
        )

        # 4) Génération de contenu + ui_config
        content = generate_content(prompt)

        # 5) Payload final
        rec = {
            "user_id": conv.get("user_id"),
            "ui": ui,
            "content": content
        }

        ok, err = validate_json(rec, SCHEMA_REC)
        if not ok:
            return jsonify({"error": err, "payload": rec}), 500

        return jsonify(rec)

    except Exception as e:
        return jsonify({"error": str(e)}), 400
