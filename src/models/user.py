# src/models/user.py

from flask_sqlalchemy import SQLAlchemy

# Instance globale de la DB utilisée par main.py
db = SQLAlchemy()

# Optionnel : un modèle User minimal si besoin plus tard
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(120), unique=True, nullable=False)
