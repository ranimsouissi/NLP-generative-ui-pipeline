🧠 NLP + Generative UI Pipeline
🚀 Description

Ce projet implémente un pipeline complet d’analyse conversationnelle combinant :

une analyse NLP (profil d’apprentissage et personnalité : VARK, MBTI),

une génération d’interface UI personnalisée,

et une API Flask unifiée permettant d’obtenir, pour une conversation donnée :

un profil cognitif et comportemental (/profile),

et une recommandation de contenu UI/UX adaptée (/recommend).

Le pipeline fusionne les modules d’analyse linguistique (ancien projet NLP) et de génération UI (ancien projet UI-Personalization) dans un même flux cohérent.
Pipeline/
│
├── main.py                         # Point d’entrée Flask
├── src/
│   ├── models/
│   │   ├── user.py                 # Modèle SQLAlchemy (User)
│   │   ├── profile_generator.py    # Génère profils VARK / MBTI
│   │   ├── prompt_transformer.py   # Construit le prompt contextuel
│   │   └── enhanced_ui_generator.py# Génère contenu UI personnalisé
│   └── routes/
│       └── unified_api.py          # Endpoint /profile et /recommend
│
├── integration_pack/               # Pack d’intégration (schemas, db, UI adapter)
│
├── database/                       # Base SQLite locale
├── requirements.txt                # Dépendances du projet
└── README.md
⚙️ Installation

1️⃣ Créer et activer un environnement virtuel :
python -m venv .venv
.\.venv\Scripts\activate
2️⃣ Installer les dépendances :
pip install -r requirements.txt
3️⃣ Lancer le serveur Flask :
python main.py
Le serveur tourne sur :
👉 http://127.0.0.1:5000
🧪 Tests API
✅ Obtenir un profil
$body = @"
{
  "user_id": "u1",
  "session_id": "s1",
  "turns": [
    { "role": "user", "text": "Explique moi la regression lineaire" }
  ]
}
"@

Invoke-RestMethod `
  -Uri "http://127.0.0.1:5000/profile" `
  -Method POST `
  -ContentType "application/json; charset=utf-8" `
  -Body $body
✅ Obtenir une recommandation UI
$body = @"
{
  "conversation": {
    "user_id": "u1",
    "session_id": "s1",
    "turns": [
      { "role": "user", "text": "Explique gradient descent" }
    ]
  },
  "context": {
    "goal": "Expliquer gradient descent",
    "lang": "fr",
    "level": "L3"
  }
}
"@

Invoke-RestMethod `
  -Uri "http://127.0.0.1:5000/recommend" `
  -Method POST `
  -ContentType "application/json; charset=utf-8" `
  -Body $body
📦 Résultats attendus

/profile → renvoie les labels VARK/MBTI + scores.

/recommend → renvoie une configuration UI complète avec :

layout, couleurs, polices, interactions,

résumé et exemples générés à partir du prompt.

🧠 Technologies

Python 3.11+

Flask / Flask-CORS / Flask-SQLAlchemy

Transformers / RapidFuzz / Numpy

JsonSchema / SQLite .
