# src/routes/user.py

from flask import Blueprint, jsonify

user_bp = Blueprint("user", __name__)

# Route de test / santé (optionnelle)
@user_bp.get("/health")
def health():
    return jsonify({"status": "ok"}), 200
