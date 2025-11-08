"""
Test simplifié du système unifié sans dépendances lourdes.
"""

import json
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(__file__))

from src.models.profile_generator import ProfileGenerator
from src.prompt_transformer import PromptTransformer


def create_test_conversation_data():
    """Crée des données de conversation de test"""
    
    # Conversation d'un apprenant visuel et extraverti
    visual_extrovert_data = [
        {
            "user_input": "Bonjour, pouvez-vous me montrer un schéma de ce concept ?",
            "bot_response": "Bien sûr, voici un diagramme explicatif...",
            "timestamp": (datetime.now() - timedelta(minutes=10)).isoformat(),
            "session_id": "visual_extrovert_001"
        },
        {
            "user_input": "C'est parfait ! J'aimerais partager cela avec mon équipe. Avez-vous d'autres images ?",
            "bot_response": "Voici quelques visualisations supplémentaires...",
            "timestamp": (datetime.now() - timedelta(minutes=8)).isoformat(),
            "session_id": "visual_extrovert_001"
        },
        {
            "user_input": "Excellent ! Pouvons-nous collaborer sur un projet ensemble ?",
            "bot_response": "Certainement, nous pouvons organiser une session collaborative...",
            "timestamp": (datetime.now() - timedelta(minutes=6)).isoformat(),
            "session_id": "visual_extrovert_001"
        },
        {
            "user_input": "Je vois bien le concept maintenant. Merci pour les graphiques colorés !",
            "bot_response": "Je suis ravi que les visualisations vous aient aidé...",
            "timestamp": (datetime.now() - timedelta(minutes=4)).isoformat(),
            "session_id": "visual_extrovert_001"
        }
    ]
    
    # Conversation d'un apprenant kinesthésique avec difficultés
    kinesthetic_struggling_data = [
        {
            "user_input": "Euh... je ne comprends pas bien. Puis-je essayer de faire quelque chose ?",
            "bot_response": "Bien sûr, voici un exercice pratique...",
            "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat(),
            "session_id": "kinesthetic_struggle_002"
        },
        {
            "user_input": "Hmm... pouvez-vous m'aider ? Je n'arrive pas à manipuler cet élément.",
            "bot_response": "Je vais vous guider étape par étape...",
            "timestamp": (datetime.now() - timedelta(minutes=12)).isoformat(),
            "session_id": "kinesthetic_struggle_002"
        },
        {
            "user_input": "Aidez-moi s'il vous plaît, je suis perdu. Comment faire cette action ?",
            "bot_response": "Pas de problème, essayons une approche différente...",
            "timestamp": (datetime.now() - timedelta(minutes=10)).isoformat(),
            "session_id": "kinesthetic_struggle_002"
        },
        {
            "user_input": "Euh... je pense que je commence à comprendre en pratiquant.",
            "bot_response": "C'est parfait ! La pratique est la clé...",
            "timestamp": (datetime.now() - timedelta(minutes=8)).isoformat(),
            "session_id": "kinesthetic_struggle_002"
        },
        {
            "user_input": "Pouvez-vous m'expliquer encore ? Je veux être sûr de bien faire.",
            "bot_response": "Bien sûr, reprenons ensemble...",
            "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat(),
            "session_id": "kinesthetic_struggle_002"
        }
    ]
    
    return {
        "visual_extrovert": visual_extrovert_data,
        "kinesthetic_struggling": kinesthetic_struggling_data
    }


def test_profile_generation():
    """Test la génération de profils d'apprenants"""
    
    print("=== Test de Génération de Profils ===")
    
    # Créer les données de test
    test_data = create_test_conversation_data()
    
    # Initialiser le générateur de profils
    profile_generator = ProfileGenerator()
    
    results = {}
    
    for profile_type, conversation_data in test_data.items():
        print(f"\nTest du profil: {profile_type}")
        
        # Convertir en DataFrame
        df = pd.DataFrame(conversation_data)
        
        # Générer le profil
        profile = profile_generator.generate_profile(df)
        
        # Afficher les résultats
        print(f"  Learner ID: {profile.learner_id}")
        print(f"  Style d'apprentissage dominant: {_get_dominant_learning_style(profile.learning_style)}")
        print(f"  Traits de personnalité: Extraversion={profile.personality.extraversion:.2f}, Analytique={profile.personality.thinking:.2f}")
        print(f"  Niveau de confiance: {profile.confidence_level:.2f}")
        print(f"  Forces: {profile.strengths}")
        print(f"  Difficultés: {profile.difficulty_areas}")
        
        results[profile_type] = profile
    
    return results


def test_prompt_transformation(profiles):
    """Test la transformation de profils en prompts"""
    
    print("\n=== Test de Transformation en Prompts ===")
    
    prompt_transformer = PromptTransformer()
    
    for profile_type, profile in profiles.items():
        print(f"\nTransformation du profil: {profile_type}")
        
        # Générer le prompt
        prompt = prompt_transformer.profile_to_prompt(profile)
        print(f"  Prompt généré: {prompt}")
        
        # Générer les recommandations
        recommendations = prompt_transformer.generate_ui_recommendations(profile)
        print(f"  Thème recommandé: {recommendations['theme_preference']}")
        print(f"  Suggestions de layout: {recommendations['layout_suggestions'][:3] if len(recommendations['layout_suggestions']) > 3 else recommendations['layout_suggestions']}")
        print(f"  Style de navigation: {recommendations['navigation_style']}")
        
        # Sauvegarder les résultats
        result = {
            "profile": _profile_to_dict(profile),
            "prompt": prompt,
            "recommendations": recommendations
        }
        
        with open(f"test_result_{profile_type}.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"  ✓ Résultats sauvegardés dans test_result_{profile_type}.json")


def validate_profile_quality(profiles):
    """Valide la qualité des profils générés"""
    
    print("\n=== Validation de la Qualité des Profils ===")
    
    for profile_type, profile in profiles.items():
        print(f"\nValidation du profil: {profile_type}")
        
        # Vérifier la cohérence du style d'apprentissage
        learning_style = profile.learning_style
        total_style = learning_style.visual + learning_style.auditory + learning_style.reading + learning_style.kinesthetic
        
        if abs(total_style - 1.0) < 0.1:  # Tolérance de 10%
            print("  ✓ Styles d'apprentissage normalisés correctement")
        else:
            print(f"  ⚠ Styles d'apprentissage non normalisés: total = {total_style:.2f}")
        
        # Vérifier les traits de personnalité
        personality = profile.personality
        if all(0 <= trait <= 1 for trait in [personality.extraversion, personality.intuition, personality.thinking, personality.judging]):
            print("  ✓ Traits de personnalité dans les limites valides")
        else:
            print("  ⚠ Certains traits de personnalité hors limites")
        
        # Vérifier la présence de forces et difficultés
        if profile.strengths:
            print(f"  ✓ Forces identifiées: {len(profile.strengths)} éléments")
        else:
            print("  ⚠ Aucune force identifiée")
        
        if profile.difficulty_areas:
            print(f"  ✓ Difficultés identifiées: {len(profile.difficulty_areas)} éléments")
        else:
            print("  ⚠ Aucune difficulté identifiée")
        
        # Vérifier la cohérence avec les données d'entrée
        if profile_type == "visual_extrovert":
            if learning_style.visual > 0.3:  # Seuil raisonnable
                print("  ✓ Style visuel correctement détecté")
            else:
                print(f"  ⚠ Style visuel faiblement détecté: {learning_style.visual:.2f}")
            
            if personality.extraversion > 0.5:
                print("  ✓ Extraversion correctement détectée")
            else:
                print(f"  ⚠ Extraversion faiblement détectée: {personality.extraversion:.2f}")
        
        elif profile_type == "kinesthetic_struggling":
            if learning_style.kinesthetic > 0.3:
                print("  ✓ Style kinesthésique correctement détecté")
            else:
                print(f"  ⚠ Style kinesthésique faiblement détecté: {learning_style.kinesthetic:.2f}")
            
            if "aide" in " ".join(profile.difficulty_areas).lower() or "hésitation" in " ".join(profile.difficulty_areas).lower():
                print("  ✓ Difficultés liées à la demande d'aide détectées")
            else:
                print("  ⚠ Difficultés spécifiques non détectées")


def create_mock_ui_config(prompt, recommendations):
    """Crée une configuration UI simulée basée sur le prompt et les recommandations"""
    
    # Configuration de base
    ui_config = {
        "theme": recommendations.get("theme_preference", "light"),
        "layout": {
            "type": "standard",
            "sections": ["header", "content", "footer"],
            "features": recommendations.get("layout_suggestions", [])
        },
        "colors": recommendations.get("color_psychology", {
            "primary": "#3498db",
            "secondary": "#2ecc71",
            "accent": "#e74c3c",
            "background": "#ffffff",
            "text": "#2c3e50"
        }),
        "typography": {
            "font_family": "Arial, sans-serif",
            "font_sizes": {
                "h1": "2rem",
                "h2": "1.5rem",
                "body": "1rem"
            }
        },
        "interactions": recommendations.get("interaction_patterns", []),
        "navigation": {
            "type": recommendations.get("navigation_style", "standard"),
            "position": "top"
        },
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "generator": "MockUIGenerator",
            "version": "1.0",
            "prompt_based": True
        }
    }
    
    return ui_config


def test_mock_ui_generation(profiles):
    """Test la génération UI simulée"""
    
    print("\n=== Test de Génération UI Simulée ===")
    
    prompt_transformer = PromptTransformer()
    
    for profile_type, profile in profiles.items():
        print(f"\nGénération UI simulée pour: {profile_type}")
        
        # Générer le prompt et les recommandations
        prompt = prompt_transformer.profile_to_prompt(profile)
        recommendations = prompt_transformer.generate_ui_recommendations(profile)
        
        # Créer une configuration UI simulée
        ui_config = create_mock_ui_config(prompt, recommendations)
        
        print(f"  ✓ Configuration UI simulée générée")
        print(f"  Thème: {ui_config['theme']}")
        print(f"  Couleur primaire: {ui_config['colors']['primary']}")
        print(f"  Type de navigation: {ui_config['navigation']['type']}")
        print(f"  Nombre d'interactions: {len(ui_config['interactions'])}")
        
        # Mettre à jour le fichier de résultats
        result_file = f"test_result_{profile_type}.json"
        if os.path.exists(result_file):
            with open(result_file, "r", encoding="utf-8") as f:
                result = json.load(f)
            
            result["ui_config"] = ui_config
            
            with open(result_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"  ✓ Configuration ajoutée à {result_file}")


def _get_dominant_learning_style(learning_style):
    """Retourne le style d'apprentissage dominant"""
    styles = {
        'visual': learning_style.visual,
        'auditory': learning_style.auditory,
        'reading': learning_style.reading,
        'kinesthetic': learning_style.kinesthetic
    }
    return max(styles, key=styles.get)


def _profile_to_dict(profile):
    """Convertit un LearnerProfile en dictionnaire"""
    return {
        "learner_id": profile.learner_id,
        "learning_style": {
            "visual": profile.learning_style.visual,
            "auditory": profile.learning_style.auditory,
            "reading": profile.learning_style.reading,
            "kinesthetic": profile.learning_style.kinesthetic
        },
        "personality": {
            "extraversion": profile.personality.extraversion,
            "intuition": profile.personality.intuition,
            "thinking": profile.personality.thinking,
            "judging": profile.personality.judging
        },
        "cognitive": {
            "processing_speed": profile.cognitive.processing_speed,
            "working_memory": profile.cognitive.working_memory,
            "analytical_thinking": profile.cognitive.analytical_thinking,
            "creative_thinking": profile.cognitive.creative_thinking,
            "attention_span": profile.cognitive.attention_span
        },
        "behavioral": {
            "engagement_level": profile.behavioral.engagement_level,
            "persistence": profile.behavioral.persistence,
            "help_seeking": profile.behavioral.help_seeking,
            "collaboration_preference": profile.behavioral.collaboration_preference,
            "self_regulation": profile.behavioral.self_regulation
        },
        "strengths": profile.strengths,
        "difficulty_areas": profile.difficulty_areas,
        "recommended_strategies": profile.recommended_strategies,
        "confidence_level": profile.confidence_level,
        "last_updated": profile.last_updated.isoformat()
    }


def main():
    """Fonction principale de test"""
    
    print("Démarrage des tests simplifiés du système unifié...")
    print("=" * 60)
    
    try:
        # Test 1: Génération de profils
        profiles = test_profile_generation()
        
        # Test 2: Transformation en prompts
        test_prompt_transformation(profiles)
        
        # Test 3: Validation de la qualité des profils
        validate_profile_quality(profiles)
        
        # Test 4: Génération UI simulée
        test_mock_ui_generation(profiles)
        
        print("\n" + "=" * 60)
        print("Tests simplifiés terminés avec succès !")
        print("\nFichiers générés:")
        for profile_type in profiles.keys():
            print(f"  - test_result_{profile_type}.json")
        
    except Exception as e:
        print(f"\nErreur lors des tests: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

