"""
Script de test pour valider le système unifié de profilage d'apprenants et de personnalisation UI.
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
from src.enhanced_ui_generator import EnhancedUIGenerator


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
    
    # Conversation d'un apprenant analytique et organisé
    analytical_organized_data = [
        {
            "user_input": "Pouvez-vous analyser les données de performance et me donner un rapport structuré ?",
            "bot_response": "Voici une analyse détaillée des métriques...",
            "timestamp": (datetime.now() - timedelta(minutes=20)).isoformat(),
            "session_id": "analytical_org_003"
        },
        {
            "user_input": "Excellent. Pouvez-vous organiser ces informations par catégories logiques ?",
            "bot_response": "Voici une classification systématique...",
            "timestamp": (datetime.now() - timedelta(minutes=18)).isoformat(),
            "session_id": "analytical_org_003"
        },
        {
            "user_input": "Je veux comparer ces résultats avec les objectifs planifiés. Avez-vous une méthode ?",
            "bot_response": "Voici une approche méthodologique pour la comparaison...",
            "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat(),
            "session_id": "analytical_org_003"
        },
        {
            "user_input": "Parfait. Je pense que cette approche rationnelle est la meilleure.",
            "bot_response": "Je suis d'accord, cette méthode est très efficace...",
            "timestamp": (datetime.now() - timedelta(minutes=12)).isoformat(),
            "session_id": "analytical_org_003"
        }
    ]
    
    return {
        "visual_extrovert": visual_extrovert_data,
        "kinesthetic_struggling": kinesthetic_struggling_data,
        "analytical_organized": analytical_organized_data
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
        print(f"  Suggestions de layout: {recommendations['layout_suggestions'][:3]}...")  # Afficher les 3 premiers
        print(f"  Style de navigation: {recommendations['navigation_style']}")


def test_ui_generation(profiles):
    """Test la génération de configurations UI"""
    
    print("\n=== Test de Génération UI ===")
    
    # Initialiser les composants
    prompt_transformer = PromptTransformer()
    ui_generator = EnhancedUIGenerator(model_type="t5", model_name="t5-small")
    
    for profile_type, profile in profiles.items():
        print(f"\nGénération UI pour: {profile_type}")
        
        try:
            # Générer le prompt et les recommandations
            prompt = prompt_transformer.profile_to_prompt(profile)
            recommendations = prompt_transformer.generate_ui_recommendations(profile)
            
            # Générer la configuration UI
            ui_config = ui_generator.generate_ui_config(
                prompt=prompt,
                learner_recommendations=recommendations,
                temperature=0.5
            )
            
            print(f"  Configuration générée avec succès")
            print(f"  Thème: {ui_config.get('theme', 'N/A')}")
            print(f"  Couleur primaire: {ui_config.get('colors', {}).get('primary', 'N/A')}")
            print(f"  Type de navigation: {ui_config.get('navigation', {}).get('type', 'N/A')}")
            print(f"  Interactions: {len(ui_config.get('interactions', []))} éléments")
            
        except Exception as e:
            print(f"  Erreur lors de la génération: {e}")


def test_full_pipeline():
    """Test du pipeline complet"""
    
    print("\n=== Test du Pipeline Complet ===")
    
    # Créer des données de test
    test_data = create_test_conversation_data()
    
    # Initialiser tous les composants
    profile_generator = ProfileGenerator()
    prompt_transformer = PromptTransformer()
    ui_generator = EnhancedUIGenerator(model_type="t5", model_name="t5-small")
    
    for profile_type, conversation_data in test_data.items():
        print(f"\nPipeline complet pour: {profile_type}")
        
        try:
            # Étape 1: Analyser la conversation
            df = pd.DataFrame(conversation_data)
            profile = profile_generator.generate_profile(df)
            print(f"  ✓ Profil généré")
            
            # Étape 2: Transformer en prompt
            prompt = prompt_transformer.profile_to_prompt(profile)
            recommendations = prompt_transformer.generate_ui_recommendations(profile)
            print(f"  ✓ Prompt et recommandations générés")
            
            # Étape 3: Générer la configuration UI
            ui_config = ui_generator.generate_ui_config(
                prompt=prompt,
                learner_recommendations=recommendations,
                temperature=0.5
            )
            print(f"  ✓ Configuration UI générée")
            
            # Sauvegarder les résultats
            result = {
                "profile": _profile_to_dict(profile),
                "prompt": prompt,
                "recommendations": recommendations,
                "ui_config": ui_config
            }
            
            with open(f"test_result_{profile_type}.json", "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"  ✓ Résultats sauvegardés dans test_result_{profile_type}.json")
            
        except Exception as e:
            print(f"  ✗ Erreur dans le pipeline: {e}")


def validate_recommendations_quality():
    """Valide la qualité des recommandations générées"""
    
    print("\n=== Validation de la Qualité des Recommandations ===")
    
    # Charger les résultats de test
    test_files = ["test_result_visual_extrovert.json", 
                  "test_result_kinesthetic_struggling.json", 
                  "test_result_analytical_organized.json"]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\nValidation de {test_file}:")
            
            with open(test_file, "r", encoding="utf-8") as f:
                result = json.load(f)
            
            profile = result["profile"]
            ui_config = result["ui_config"]
            
            # Validation basée sur le style d'apprentissage
            learning_style = profile["learning_style"]
            dominant_style = max(learning_style, key=learning_style.get)
            
            print(f"  Style dominant détecté: {dominant_style}")
            
            # Vérifications spécifiques
            if dominant_style == "visual":
                if "visual" in str(ui_config).lower() or "image" in str(ui_config).lower():
                    print("  ✓ Configuration adaptée aux apprenants visuels")
                else:
                    print("  ⚠ Configuration pourrait mieux s'adapter aux apprenants visuels")
            
            elif dominant_style == "kinesthetic":
                if "interactive" in str(ui_config).lower() or "touch" in str(ui_config).lower():
                    print("  ✓ Configuration adaptée aux apprenants kinesthésiques")
                else:
                    print("  ⚠ Configuration pourrait mieux s'adapter aux apprenants kinesthésiques")
            
            # Vérifier la cohérence des couleurs
            colors = ui_config.get("colors", {})
            if colors and "primary" in colors:
                print(f"  ✓ Palette de couleurs définie: {colors['primary']}")
            else:
                print("  ⚠ Palette de couleurs manquante ou incomplète")
            
            # Vérifier la présence d'éléments essentiels
            required_elements = ["theme", "layout", "colors", "navigation"]
            missing_elements = [elem for elem in required_elements if elem not in ui_config]
            
            if not missing_elements:
                print("  ✓ Tous les éléments essentiels sont présents")
            else:
                print(f"  ⚠ Éléments manquants: {missing_elements}")


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
    
    print("Démarrage des tests du système unifié...")
    print("=" * 50)
    
    try:
        # Test 1: Génération de profils
        profiles = test_profile_generation()
        
        # Test 2: Transformation en prompts
        test_prompt_transformation(profiles)
        
        # Test 3: Génération UI
        test_ui_generation(profiles)
        
        # Test 4: Pipeline complet
        test_full_pipeline()
        
        # Test 5: Validation de la qualité
        validate_recommendations_quality()
        
        print("\n" + "=" * 50)
        print("Tests terminés avec succès !")
        
    except Exception as e:
        print(f"\nErreur lors des tests: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

