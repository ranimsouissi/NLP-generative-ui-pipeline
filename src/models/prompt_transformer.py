"""
Module de transformation de profil d'apprenant en prompt pour l'IA générative.
Ce module fait le lien entre le système de profilage NLP et le système de personnalisation UI.
"""

from typing import Dict, List, Any
from dataclasses import asdict

from .profile_generator import (
    LearnerProfile,
    LearningStyle,
    PersonalityProfile,
    CognitiveProfile,
    BehavioralProfile,
)



class PromptTransformer:
    """Transforme un LearnerProfile en prompt textuel pour l'IA générative"""
    
    def __init__(self):
        self.vark_descriptions = {
            'visual': 'visuel',
            'auditory': 'auditif', 
            'reading': 'lecture/écriture',
            'kinesthetic': 'kinesthésique'
        }
        
        self.mbti_descriptions = {
            'extraversion': ('extraverti', 'introverti'),
            'intuition': ('intuitif', 'concret'),
            'thinking': ('analytique', 'empathique'),
            'judging': ('organisé', 'flexible')
        }
    
    def profile_to_prompt(self, profile: LearnerProfile) -> str:
        """
        Convertit un LearnerProfile en prompt textuel structuré pour l'IA générative.
        """
        learning_style_text = self._get_dominant_learning_style(profile.learning_style)
        personality_text = self._get_personality_traits(profile.personality)
        cognitive_text = self._get_cognitive_characteristics(profile.cognitive)
        behavioral_text = self._get_behavioral_patterns(profile.behavioral)
        strengths_text = self._format_strengths(profile.strengths)
        difficulties_text = self._format_difficulties(profile.difficulty_areas)
        
        prompt = self._build_comprehensive_prompt(
            learning_style_text,
            personality_text,
            cognitive_text,
            behavioral_text,
            strengths_text,
            difficulties_text,
            profile.confidence_level
        )
        return prompt
    
    def _get_dominant_learning_style(self, learning_style: LearningStyle) -> str:
        styles = {
            'visual': learning_style.visual,
            'auditory': learning_style.auditory,
            'reading': learning_style.reading,
            'kinesthetic': learning_style.kinesthetic
        }
        sorted_styles = sorted(styles.items(), key=lambda x: x[1], reverse=True)
        dominant_style = sorted_styles[0][0]
        secondary_styles = [s for s, score in sorted_styles[1:] if score > 0.2]

        text = f"apprenant principalement {self.vark_descriptions[dominant_style]}"
        if secondary_styles:
            secondary_desc = [self.vark_descriptions[s] for s in secondary_styles]
            text += f" avec des tendances {' et '.join(secondary_desc)}"
        return text
    
    def _get_personality_traits(self, personality: PersonalityProfile) -> str:
        traits = []
        if personality.extraversion > 0.6:
            traits.append("extraverti")
        elif personality.extraversion < 0.4:
            traits.append("introverti")
        if personality.intuition > 0.6:
            traits.append("intuitif")
        elif personality.intuition < 0.4:
            traits.append("concret")
        if personality.thinking > 0.6:
            traits.append("analytique")
        elif personality.thinking < 0.4:
            traits.append("empathique")
        if personality.judging > 0.6:
            traits.append("organisé")
        elif personality.judging < 0.4:
            traits.append("flexible")
        if traits:
            return f"de personnalité {', '.join(traits)}"
        return "de personnalité équilibrée"
    
    def _get_cognitive_characteristics(self, cognitive: CognitiveProfile) -> str:
        characteristics = []
        if cognitive.processing_speed > 0.7:
            characteristics.append("traitement rapide")
        elif cognitive.processing_speed < 0.3:
            characteristics.append("traitement réfléchi")
        if cognitive.working_memory > 0.7:
            characteristics.append("bonne mémoire de travail")
        elif cognitive.working_memory < 0.3:
            characteristics.append("mémoire de travail limitée")
        if cognitive.analytical_thinking > 0.7:
            characteristics.append("forte capacité analytique")
        if cognitive.creative_thinking > 0.7:
            characteristics.append("pensée créative développée")
        if cognitive.attention_span > 0.7:
            characteristics.append("bonne capacité d'attention")
        elif cognitive.attention_span < 0.3:
            characteristics.append("attention limitée")
        if characteristics:
            return f"avec {', '.join(characteristics)}"
        return "avec des capacités cognitives moyennes"
    
    def _get_behavioral_patterns(self, behavioral: BehavioralProfile) -> str:
        patterns = []
        if behavioral.engagement_level > 0.7:
            patterns.append("très engagé")
        elif behavioral.engagement_level < 0.3:
            patterns.append("engagement faible")
        if behavioral.persistence > 0.7:
            patterns.append("persistant")
        elif behavioral.persistence < 0.3:
            patterns.append("abandonne facilement")
        if behavioral.help_seeking > 0.7:
            patterns.append("demande souvent de l'aide")
        elif behavioral.help_seeking < 0.3:
            patterns.append("autonome")
        if behavioral.collaboration_preference > 0.7:
            patterns.append("préfère le travail collaboratif")
        elif behavioral.collaboration_preference < 0.3:
            patterns.append("préfère le travail individuel")
        if behavioral.self_regulation > 0.7:
            patterns.append("bonne autorégulation")
        elif behavioral.self_regulation < 0.3:
            patterns.append("autorégulation faible")
        if patterns:
            return f"Il est {', '.join(patterns)}"
        return "Il présente des comportements d'apprentissage équilibrés"
    
    def _format_strengths(self, strengths: List[str]) -> str:
        if strengths:
            return f"Ses forces incluent : {', '.join(strengths).lower()}"
        return ""
    
    def _format_difficulties(self, difficulties: List[str]) -> str:
        if difficulties:
            return f"Ses difficultés incluent : {', '.join(difficulties).lower()}"
        return ""
    
    def _build_comprehensive_prompt(
        self,
        learning_style: str,
        personality: str,
        cognitive: str,
        behavioral: str,
        strengths: str,
        difficulties: str,
        confidence: float
    ) -> str:
        base_prompt = (
            f"Générer une configuration UI/UX personnalisée pour un "
            f"{learning_style} {personality} {cognitive}. {behavioral}."
        )
        context_parts = []
        if strengths:
            context_parts.append(strengths)
        if difficulties:
            context_parts.append(difficulties)
        if context_parts:
            base_prompt += f" {' '.join(context_parts)}."
        if confidence < 0.3:
            base_prompt += " Privilégier une interface simple et rassurante avec des guides étape par étape."
        elif confidence > 0.7:
            base_prompt += " Permettre une interface avancée avec des options de personnalisation étendues."
        base_prompt += (
            " La configuration doit inclure le thème, la mise en page, la palette de couleurs "
            "et les éléments interactifs recommandés."
        )
        return base_prompt
    
    # -------- Recos structurées (inchangé) --------
    def generate_ui_recommendations(self, profile: LearnerProfile) -> Dict[str, Any]:
        return {
            "theme_preference": self._get_theme_preference(profile),
            "layout_suggestions": self._get_layout_suggestions(profile),
            "interaction_patterns": self._get_interaction_patterns(profile),
            "color_psychology": self._get_color_recommendations(profile),
            "navigation_style": self._get_navigation_style(profile),
        }
    
    def _get_theme_preference(self, profile: LearnerProfile) -> str:
        if profile.learning_style.visual > 0.5:
            return "high_contrast"
        if profile.personality.extraversion < 0.4:
            return "dark"
        return "light"
    
    def _get_layout_suggestions(self, profile: LearnerProfile) -> List[str]:
        suggestions: List[str] = []
        if profile.learning_style.visual > 0.5:
            suggestions += ["visual_hierarchy", "image_heavy", "infographics"]
        if profile.learning_style.kinesthetic > 0.5:
            suggestions += ["interactive_elements", "drag_drop", "touch_friendly"]
        if profile.cognitive.attention_span < 0.4:
            suggestions += ["minimal_design", "focused_content", "progress_indicators"]
        if profile.personality.judging > 0.6:
            suggestions += ["structured_layout", "clear_sections", "navigation_breadcrumbs"]
        return suggestions
    
    def _get_interaction_patterns(self, profile: LearnerProfile) -> List[str]:
        patterns: List[str] = []
        if profile.personality.extraversion > 0.6:
            patterns += ["social_features", "collaboration_tools", "sharing_options"]
        if profile.behavioral.help_seeking > 0.6:
            patterns += ["help_tooltips", "contextual_assistance", "tutorial_mode"]
        if profile.behavioral.self_regulation < 0.4:
            patterns += ["guided_workflow", "automatic_save", "reminder_system"]
        return patterns
    
    def _get_color_recommendations(self, profile: LearnerProfile) -> Dict[str, str]:
        colors = {
            "primary": "#3498db",
            "secondary": "#2ecc71",
            "accent": "#e74c3c",
            "background": "#ffffff",
            "text": "#2c3e50",
        }
        if profile.personality.extraversion > 0.6:
            colors["accent"] = "#f39c12"
        if profile.cognitive.creative_thinking > 0.6:
            colors["secondary"] = "#9b59b6"
        if profile.behavioral.engagement_level < 0.4:
            colors["primary"] = "#27ae60"
        return colors
    
    def _get_navigation_style(self, profile: LearnerProfile) -> str:
        if profile.cognitive.attention_span < 0.4:
            return "linear"
        if profile.personality.judging < 0.4:
            return "free_form"
        if profile.personality.judging > 0.6:
            return "hierarchical"
        return "standard"


# ================== ADAPTATEUR POUR unified_api ==================

def _vark_to_learning_style(vark_label: str, base: LearningStyle | None = None) -> LearningStyle:
    ls = base or LearningStyle()
    label = (vark_label or "").upper()
    boost = 0.65
    rest = (1.0 - boost) / 3.0
    if label == "V":
        ls.visual, ls.auditory, ls.reading, ls.kinesthetic = boost, rest, rest, rest
    elif label == "A":
        ls.visual, ls.auditory, ls.reading, ls.kinesthetic = rest, boost, rest, rest
    elif label == "R":
        ls.visual, ls.auditory, ls.reading, ls.kinesthetic = rest, rest, boost, rest
    elif label == "K":
        ls.visual, ls.auditory, ls.reading, ls.kinesthetic = rest, rest, rest, boost
    return ls

def _mbti_to_personality(mbti: str, base: PersonalityProfile | None = None) -> PersonalityProfile:
    p = base or PersonalityProfile()
    code = (mbti or "").upper()
    p.extraversion = 0.75 if code[:1] == "E" else 0.25
    p.intuition    = 0.75 if code[1:2] == "N" else 0.25
    p.thinking     = 0.75 if code[2:3] == "T" else 0.25
    p.judging      = 0.75 if code[3:4] == "J" else 0.25
    return p

def build_prompt_from_profiles(
    goal: str,
    lang: str,
    level: str,
    profiles: Dict[str, Any],
    features: Dict[str, Any],
    ui: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Utilisé par unified_api.py :
    construi un prompt textuel + recommandations UI à partir de VARK/MBTI + features + contraintes UI.
    """
    vark = profiles.get("VARK")
    mbti = profiles.get("MBTI")

    vark_label = vark.get("label") if isinstance(vark, dict) else vark
    mbti_label = mbti.get("label") if isinstance(mbti, dict) else mbti

    ls = _vark_to_learning_style(vark_label or "R")
    pers = _mbti_to_personality(mbti_label or "INTJ")

    # Hydratation avec features si présents
    ls.visual = float(features.get("ls_visual", ls.visual))
    ls.auditory = float(features.get("ls_auditory", ls.auditory))
    ls.reading = float(features.get("ls_reading", ls.reading))
    ls.kinesthetic = float(features.get("ls_kinesthetic", ls.kinesthetic))

    pers.extraversion = float(features.get("pers_extraversion", pers.extraversion))
    pers.intuition = float(features.get("pers_intuition", pers.intuition))
    pers.thinking = float(features.get("pers_thinking", pers.thinking))
    pers.judging = float(features.get("pers_judging", pers.judging))

    cog = CognitiveProfile()  # neutre, adaptable plus tard
    beh = BehavioralProfile()

    lp = LearnerProfile(
        learner_id="temp",
        learning_style=ls,
        personality=pers,
        cognitive=cog,
        behavioral=beh,
        strengths=features.get("strengths", []),
        difficulty_areas=features.get("difficulties", []),
        confidence_level=float(features.get("confidence", 0.6)),
    )

    transformer = PromptTransformer()
    prompt_text = transformer.profile_to_prompt(lp)
    recs = transformer.generate_ui_recommendations(lp)

    header = f"[BUT] {goal} | [LANG] {lang} | [NIVEAU] {level}"
    ui_constraints = f"[UI CONSTRAINTS] {ui}"

    final_text = f"{header}\n{prompt_text}\n{ui_constraints}"

    return {
        "text": final_text,
        "recommendations": recs,
        "context": {"goal": goal, "lang": lang, "level": level},
        "profiles": {"VARK": vark_label, "MBTI": mbti_label},
        "ui": ui,
    }
