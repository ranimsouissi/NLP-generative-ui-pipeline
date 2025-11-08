"""
Générateur UI amélioré qui intègre les profils d'apprenants.
Version tolérante : fonctionne même sans torch (fallback).
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

# ---------- Gestion optionnelle de torch ----------
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    torch = None  # type: ignore
    TORCH_AVAILABLE = False
    logger.warning("Torch non disponible : le générateur utilisera le mode fallback (sans modèle).")

# ---------- Transformers (présents dans ton venv) ----------
try:
    from transformers import (
        T5Tokenizer,
        T5ForConditionalGeneration,
        GPT2LMHeadModel,
        GPT2Tokenizer,
    )
    HF_AVAILABLE = True
except ImportError:
    T5Tokenizer = T5ForConditionalGeneration = GPT2LMHeadModel = GPT2Tokenizer = None  # type: ignore
    HF_AVAILABLE = False
    logger.warning("transformers non disponible : le générateur utilisera le mode fallback.")


class EnhancedUIGenerator:
    """Générateur UI amélioré avec support des profils d'apprenants"""

    def __init__(self, model_type: str = "t5", model_name: str = "t5-small"):
        """
        Args:
            model_type: "t5" ou "gpt2"
            model_name: nom du modèle pré-entraîné
        """
        self.model_type = model_type
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.device = "cpu"
        self._load_model()

    # ---------- Chargement du modèle (ou fallback) ----------
    def _load_model(self):
        """Charge le modèle si torch + transformers dispos, sinon active le fallback."""
        if not TORCH_AVAILABLE or not HF_AVAILABLE:
            logger.info("Initialisation en mode fallback (pas de modèle chargé).")
            self.model = None
            self.tokenizer = None
            return

        try:
            if self.model_type == "t5":
                self.tokenizer = T5Tokenizer.from_pretrained(self.model_name)
                self.model = T5ForConditionalGeneration.from_pretrained(self.model_name)
            elif self.model_type == "gpt2":
                self.tokenizer = GPT2Tokenizer.from_pretrained(self.model_name)
                self.model = GPT2LMHeadModel.from_pretrained(self.model_name)
                self.tokenizer.pad_token = self.tokenizer.eos_token
            else:
                raise ValueError(f"Type de modèle non supporté: {self.model_type}")

            self.device = "cuda" if torch.cuda.is_available() else "cpu"  # type: ignore
            self.model.to(self.device)  # type: ignore
            logger.info(f"Modèle {self.model_name} chargé avec succès sur {self.device}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle ({e}), bascule en fallback.")
            self.model = None
            self.tokenizer = None

    # ---------- API principale ----------
    def generate_ui_config(
        self,
        prompt: str,
        learner_recommendations: Optional[Dict[str, Any]] = None,
        max_length: int = 512,
        temperature: float = 0.7,
        num_return_sequences: int = 1,
    ) -> Dict[str, Any]:
        """
        Génère une configuration UI à partir d'un prompt et de recommandations.
        Si le modèle n'est pas disponible, renvoie une config fallback structurée.
        """
        enhanced_prompt = self._enhance_prompt_with_recommendations(prompt, learner_recommendations)

        # Pas de modèle dispo -> fallback direct
        if self.model is None or self.tokenizer is None or not TORCH_AVAILABLE or not HF_AVAILABLE:
            return self._get_fallback_config(learner_recommendations)

        try:
            if self.model_type == "t5":
                generated_text = self._generate_with_t5(enhanced_prompt, max_length, temperature)
            else:
                generated_text = self._generate_with_gpt2(enhanced_prompt, max_length, temperature)

            config = self._post_process_generation(generated_text, learner_recommendations)
            return config

        except Exception as e:
            logger.error(f"Erreur lors de la génération UI, fallback utilisé: {e}")
            return self._get_fallback_config(learner_recommendations)

    # ---------- Enrichissement du prompt ----------
    def _enhance_prompt_with_recommendations(
        self,
        prompt: str,
        recommendations: Optional[Dict[str, Any]],
    ) -> str:
        if not recommendations:
            return prompt

        enhanced_prompt = prompt

        if "theme_preference" in recommendations:
            enhanced_prompt += f" Utiliser un thème {recommendations['theme_preference']}."
        if recommendations.get("layout_suggestions"):
            layout_text = ", ".join(recommendations["layout_suggestions"])
            enhanced_prompt += f" Inclure les éléments suivants: {layout_text}."
        if recommendations.get("interaction_patterns"):
            interaction_text = ", ".join(recommendations["interaction_patterns"])
            enhanced_prompt += f" Intégrer les interactions: {interaction_text}."
        if "navigation_style" in recommendations:
            enhanced_prompt += f" Utiliser une navigation de type {recommendations['navigation_style']}."

        return enhanced_prompt

    # ---------- Génération modèle (T5 / GPT2) ----------
    def _generate_with_t5(self, prompt: str, max_length: int, temperature: float) -> str:
        input_text = f"generate ui config: {prompt}"
        input_ids = self.tokenizer(
            input_text,
            return_tensors="pt",
            max_length=512,
            truncation=True,
            padding=True,
        ).input_ids.to(self.device)

        with torch.no_grad():  # type: ignore
            output_ids = self.model.generate(
                input_ids,
                max_length=max_length,
                temperature=temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )
        return self.tokenizer.decode(output_ids[0], skip_special_tokens=True)

    def _generate_with_gpt2(self, prompt: str, max_length: int, temperature: float) -> str:
        input_text = f"UI Configuration: {prompt}\nJSON:"
        input_ids = self.tokenizer(
            input_text,
            return_tensors="pt",
            max_length=400,
            truncation=True,
            padding=True,
        ).input_ids.to(self.device)

        with torch.no_grad():  # type: ignore
            output_ids = self.model.generate(
                input_ids,
                max_length=max_length,
                temperature=temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )
        generated_ids = output_ids[0][input_ids.shape[1]:]
        return self.tokenizer.decode(generated_ids, skip_special_tokens=True)

    # ---------- Post-traitement ----------
    def _post_process_generation(
        self,
        generated_text: str,
        recommendations: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        try:
            cleaned_text = self._clean_generated_text(generated_text)
            if cleaned_text.strip().startswith("{"):
                config = json.loads(cleaned_text)
            else:
                config = self._text_to_config(cleaned_text)
        except Exception as e:
            logger.warning(f"Impossible de parser la génération comme JSON: {e}")
            config = self._text_to_config(generated_text)

        if recommendations:
            config = self._merge_with_recommendations(config, recommendations)
        config = self._validate_and_complete_config(config)
        return config

    def _clean_generated_text(self, text: str) -> str:
        text = text.replace("generate ui config:", "").strip()
        text = text.replace("UI Configuration:", "").strip()
        text = text.replace("JSON:", "").strip()
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return text[start : end + 1]
        return text

    def _text_to_config(self, text: str) -> Dict[str, Any]:
        # Config par défaut raisonnable
        config: Dict[str, Any] = {
            "theme": "light",
            "layout": {
                "type": "standard",
                "sections": ["header", "content", "footer"],
            },
            "colors": {
                "primary": "#3498db",
                "secondary": "#2ecc71",
                "accent": "#e74c3c",
                "background": "#ffffff",
                "text": "#2c3e50",
            },
            "typography": {
                "font_family": "Arial, sans-serif",
                "font_sizes": {"h1": "2rem", "h2": "1.5rem", "body": "1rem"},
            },
            "interactions": [],
            "navigation": {"type": "horizontal", "position": "top"},
        }

        t = text.lower()
        if any(w in t for w in ["dark", "sombre"]):
            config["theme"] = "dark"
            config["colors"]["background"] = "#2c3e50"
            config["colors"]["text"] = "#ecf0f1"
        if any(w in t for w in ["high contrast", "contraste"]):
            config["theme"] = "high_contrast"
        if any(w in t for w in ["interactive", "interactif", "drag", "touch"]):
            config["interactions"] += ["drag_drop", "touch_friendly"]
        if any(w in t for w in ["help", "aide", "tooltip"]):
            config["interactions"] += ["help_tooltips", "contextual_assistance"]
        if any(w in t for w in ["linear", "linéaire", "étape"]):
            config["navigation"]["type"] = "linear"
        elif any(w in t for w in ["hierarchical", "hiérarchique"]):
            config["navigation"]["type"] = "hierarchical"

        return config

    def _merge_with_recommendations(
        self,
        config: Dict[str, Any],
        recommendations: Dict[str, Any],
    ) -> Dict[str, Any]:
        if "color_psychology" in recommendations:
            config.setdefault("colors", {}).update(recommendations["color_psychology"])
        if "theme_preference" in recommendations:
            config["theme"] = recommendations["theme_preference"]
        if "interaction_patterns" in recommendations:
            existing = config.get("interactions", [])
            config["interactions"] = list(set(existing + recommendations["interaction_patterns"]))
        if "navigation_style" in recommendations:
            config.setdefault("navigation", {})["type"] = recommendations["navigation_style"]
        if "layout_suggestions" in recommendations:
            config.setdefault("layout", {})["features"] = recommendations["layout_suggestions"]
        return config

    def _validate_and_complete_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        required = ["theme", "layout", "colors", "typography", "interactions", "navigation"]
        for k in required:
            config.setdefault(k, {} if k not in ("interactions",) else [])
        if not isinstance(config["colors"], dict):
            config["colors"] = {
                "primary": "#3498db",
                "secondary": "#2ecc71",
                "accent": "#e74c3c",
                "background": "#ffffff",
                "text": "#2c3e50",
            }
        if not isinstance(config["typography"], dict):
            config["typography"] = {
                "font_family": "Arial, sans-serif",
                "font_sizes": {"h1": "2rem", "h2": "1.5rem", "body": "1rem"},
            }
        config.setdefault("metadata", {})
        config["metadata"].update(
            {
                "generated_at": datetime.utcnow().isoformat(),
                "generator": "EnhancedUIGenerator",
                "version": "1.0",
                "fallback": self.model is None,
            }
        )
        return config

    def _get_fallback_config(self, recommendations: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Configuration simple mais propre quand aucun modèle n'est dispo."""
        config = {
            "theme": "light",
            "layout": {
                "type": "standard",
                "sections": ["header", "content", "footer"],
                "features": [],
            },
            "colors": {
                "primary": "#3498db",
                "secondary": "#2ecc71",
                "accent": "#e74c3c",
                "background": "#ffffff",
                "text": "#2c3e50",
            },
            "typography": {
                "font_family": "Arial, sans-serif",
                "font_sizes": {"h1": "2rem", "h2": "1.5rem", "body": "1rem"},
            },
            "interactions": ["basic_click", "hover_effects"],
            "navigation": {"type": "horizontal", "position": "top"},
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "generator": "EnhancedUIGenerator",
                "version": "1.0",
                "fallback": True,
            },
        }
        if recommendations:
            config = self._merge_with_recommendations(config, recommendations)
        return config


# ---------- Adaptateur fonctionnel pour unified_api / tests ----------

__GEN_SINGLETON: Optional[EnhancedUIGenerator] = None

def _get_generator() -> EnhancedUIGenerator:
    global __GEN_SINGLETON
    if __GEN_SINGLETON is None:
        __GEN_SINGLETON = EnhancedUIGenerator(model_type="t5", model_name="t5-small")
    return __GEN_SINGLETON

def generate_content(prompt: Dict[str, Any] | str) -> Dict[str, Any]:
    """
    Utilisé par unified_api et les tests.
    Retourne:
    {
      "summary": str,
      "examples": list,
      "quiz": list,
      "ui_config": dict
    }
    """
    gen = _get_generator()

    if isinstance(prompt, dict):
        text = str(prompt.get("text", ""))
        recs = prompt.get("recommendations")
    else:
        text = str(prompt)
        recs = None

    ui_cfg = gen.generate_ui_config(
        prompt=text,
        learner_recommendations=recs,
        max_length=512,
        temperature=0.7,
        num_return_sequences=1,
    )

    return {
        "summary": text[:400],  # mini-résumé basé sur le prompt
        "examples": [],
        "quiz": [],
        "ui_config": ui_cfg,
    }
