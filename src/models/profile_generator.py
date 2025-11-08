# profile_generator.py
from __future__ import annotations

import json
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Dict, List, Tuple, Optional

import numpy as np


# ========== Data classes ==========
@dataclass
class LearningStyle:
    visual: float = 0.25
    auditory: float = 0.25
    reading: float = 0.25
    kinesthetic: float = 0.25


@dataclass
class PersonalityProfile:
    # Big-4 mappés aux axes MBTI (E/I, N/S, T/F, J/P) via seuils simples
    extraversion: float = 0.5  # E vs I
    intuition: float = 0.5     # N vs S
    thinking: float = 0.5      # T vs F
    judging: float = 0.5       # J vs P


@dataclass
class CognitiveProfile:
    processing_speed: float = 0.5
    working_memory: float = 0.5
    analytical_thinking: float = 0.5
    creative_thinking: float = 0.5
    attention_span: float = 0.5


@dataclass
class BehavioralProfile:
    engagement_level: float = 0.5
    persistence: float = 0.5
    help_seeking: float = 0.5
    collaboration_preference: float = 0.5
    self_regulation: float = 0.5


@dataclass
class LearnerProfile:
    learner_id: str
    learning_style: LearningStyle = field(default_factory=LearningStyle)
    personality: PersonalityProfile = field(default_factory=PersonalityProfile)
    cognitive: CognitiveProfile = field(default_factory=CognitiveProfile)
    behavioral: BehavioralProfile = field(default_factory=BehavioralProfile)

    difficulty_areas: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    recommended_strategies: List[str] = field(default_factory=list)

    confidence_level: float = 0.6
    last_updated: datetime = field(default_factory=datetime.utcnow)


# ========== Utils ==========
def _clip01(x: float) -> float:
    return float(max(0.0, min(1.0, x)))


def _merge_learning_style(existing: LearningStyle, new: LearningStyle, weight: float) -> LearningStyle:
    return LearningStyle(
        visual=_clip01(existing.visual * (1 - weight) + new.visual * weight),
        auditory=_clip01(existing.auditory * (1 - weight) + new.auditory * weight),
        reading=_clip01(existing.reading * (1 - weight) + new.reading * weight),
        kinesthetic=_clip01(existing.kinesthetic * (1 - weight) + new.kinesthetic * weight),
    )


def _infer_vark_from_learning_style(ls: LearningStyle) -> Tuple[str, Dict[str, float]]:
    scores = {
        "V": _clip01(ls.visual),
        "A": _clip01(ls.auditory),
        "R": _clip01(ls.reading),
        "K": _clip01(ls.kinesthetic),
    }
    label = max(scores.items(), key=lambda kv: kv[1])[0]
    return label, scores


def _infer_mbti_from_personality(pers: PersonalityProfile) -> Tuple[str, Dict[str, float]]:
    """
    Heuristique simple sur 4 axes [0..1].
    - extraversion >= .5 -> E sinon I
    - intuition    >= .5 -> N sinon S
    - thinking     >= .5 -> T sinon F
    - judging      >= .5 -> J sinon P
    """
    E = _clip01(pers.extraversion)
    N = _clip01(pers.intuition)
    T = _clip01(pers.thinking)
    J = _clip01(pers.judging)

    mbti = ""
    mbti += "E" if E >= 0.5 else "I"
    mbti += "N" if N >= 0.5 else "S"
    mbti += "T" if T >= 0.5 else "F"
    mbti += "J" if J >= 0.5 else "P"

    scores = {
        "E": E, "I": 1 - E,
        "N": N, "S": 1 - N,
        "T": T, "F": 1 - T,
        "J": J, "P": 1 - J,
    }
    return mbti, scores


# ========== Générateur/Cache ==========
class ProfileGenerator:
    """
    - Gère un cache de profils apprenants
    - Fusionne de nouveaux signaux (pondération)
    - Exporte
    - Trouve des apprenants similaires
    """
    def __init__(self):
        self.profile_cache: Dict[str, LearnerProfile] = {}

    # ---------- CRUD Cache ----------
    def get(self, learner_id: str) -> Optional[LearnerProfile]:
        return self.profile_cache.get(learner_id)

    def set(self, profile: LearnerProfile) -> None:
        profile.last_updated = datetime.utcnow()
        self.profile_cache[profile.learner_id] = profile

    # ---------- Fusion ----------
    def merge_profiles(self, existing: LearnerProfile, new: LearnerProfile, weight: float = 0.5) -> LearnerProfile:
        weight = _clip01(weight)

        # Learning style
        merged_learning_style = _merge_learning_style(existing.learning_style, new.learning_style, weight)

        # Personality
        merged_personality = PersonalityProfile(
            extraversion=_clip01(existing.personality.extraversion * (1 - weight) + new.personality.extraversion * weight),
            intuition=_clip01(existing.personality.intuition * (1 - weight) + new.personality.intuition * weight),
            thinking=_clip01(existing.personality.thinking * (1 - weight) + new.personality.thinking * weight),
            judging=_clip01(existing.personality.judging * (1 - weight) + new.personality.judging * weight),
        )

        # Cognitive
        merged_cognitive = CognitiveProfile(
            processing_speed=_clip01(existing.cognitive.processing_speed * (1 - weight) + new.cognitive.processing_speed * weight),
            working_memory=_clip01(existing.cognitive.working_memory * (1 - weight) + new.cognitive.working_memory * weight),
            analytical_thinking=_clip01(existing.cognitive.analytical_thinking * (1 - weight) + new.cognitive.analytical_thinking * weight),
            creative_thinking=_clip01(existing.cognitive.creative_thinking * (1 - weight) + new.cognitive.creative_thinking * weight),
            attention_span=_clip01(existing.cognitive.attention_span * (1 - weight) + new.cognitive.attention_span * weight),
        )

        # Behavioral
        merged_behavioral = BehavioralProfile(
            engagement_level=_clip01(existing.behavioral.engagement_level * (1 - weight) + new.behavioral.engagement_level * weight),
            persistence=_clip01(existing.behavioral.persistence * (1 - weight) + new.behavioral.persistence * weight),
            help_seeking=_clip01(existing.behavioral.help_seeking * (1 - weight) + new.behavioral.help_seeking * weight),
            collaboration_preference=_clip01(existing.behavioral.collaboration_preference * (1 - weight) + new.behavioral.collaboration_preference * weight),
            self_regulation=_clip01(existing.behavioral.self_regulation * (1 - weight) + new.behavioral.self_regulation * weight),
        )

        # Listes (dédupliquées mais ordonnées)
        def _dedup_keep_order(seq: List[str]) -> List[str]:
            seen = set(); out = []
            for x in seq:
                if x not in seen:
                    out.append(x); seen.add(x)
            return out

        merged_strengths = _dedup_keep_order(existing.strengths + new.strengths)
        merged_difficulties = _dedup_keep_order(existing.difficulty_areas + new.difficulty_areas)
        merged_recommendations = _dedup_keep_order(existing.recommended_strategies + new.recommended_strategies)

        # Confiance
        merged_confidence = _clip01(existing.confidence_level * (1 - weight) + new.confidence_level * weight)

        lp = LearnerProfile(
            learner_id=existing.learner_id,
            learning_style=merged_learning_style,
            personality=merged_personality,
            cognitive=merged_cognitive,
            behavioral=merged_behavioral,
            difficulty_areas=merged_difficulties,
            strengths=merged_strengths,
            recommended_strategies=merged_recommendations,
            confidence_level=merged_confidence,
        )
        lp.last_updated = datetime.utcnow()
        return lp

    # ---------- Export ----------
    def export_profile(self, learner_id: str, fmt: str = "json") -> str:
        if learner_id not in self.profile_cache:
            return ""
        profile = self.profile_cache[learner_id]
        if fmt.lower() == "json":
            d = asdict(profile)
            # dataclasses -> isoformat pour la date
            d["last_updated"] = profile.last_updated.isoformat()
            return json.dumps(d, indent=2, ensure_ascii=False)
        return ""

    # ---------- Similarité ----------
    def _calculate_profile_similarity(self, p1: LearnerProfile, p2: LearnerProfile) -> float:
        # Learning style
        ls1 = np.array([p1.learning_style.visual, p1.learning_style.auditory, p1.learning_style.reading, p1.learning_style.kinesthetic], dtype=float)
        ls2 = np.array([p2.learning_style.visual, p2.learning_style.auditory, p2.learning_style.reading, p2.learning_style.kinesthetic], dtype=float)
        ls_sim = 1.0 - np.linalg.norm(ls1 - ls2) / 2.0  # 4 dims max dist = 2

        # Personality
        pr1 = np.array([p1.personality.extraversion, p1.personality.intuition, p1.personality.thinking, p1.personality.judging], dtype=float)
        pr2 = np.array([p2.personality.extraversion, p2.personality.intuition, p2.personality.thinking, p2.personality.judging], dtype=float)
        pr_sim = 1.0 - np.linalg.norm(pr1 - pr2) / 2.0  # 4 dims max dist = 2

        # Cognitive (5 dims)
        cg1 = np.array([p1.cognitive.processing_speed, p1.cognitive.working_memory, p1.cognitive.analytical_thinking, p1.cognitive.creative_thinking, p1.cognitive.attention_span], dtype=float)
        cg2 = np.array([p2.cognitive.processing_speed, p2.cognitive.working_memory, p2.cognitive.analytical_thinking, p2.cognitive.creative_thinking, p2.cognitive.attention_span], dtype=float)
        cg_sim = 1.0 - np.linalg.norm(cg1 - cg2) / np.sqrt(5)

        # Behavioral (5 dims)
        bh1 = np.array([p1.behavioral.engagement_level, p1.behavioral.persistence, p1.behavioral.help_seeking, p1.behavioral.collaboration_preference, p1.behavioral.self_regulation], dtype=float)
        bh2 = np.array([p2.behavioral.engagement_level, p2.behavioral.persistence, p2.behavioral.help_seeking, p2.behavioral.collaboration_preference, p2.behavioral.self_regulation], dtype=float)
        bh_sim = 1.0 - np.linalg.norm(bh1 - bh2) / np.sqrt(5)

        overall = (0.30 * ls_sim) + (0.25 * pr_sim) + (0.25 * cg_sim) + (0.20 * bh_sim)
        return float(max(0.0, min(1.0, overall)))

    def get_similar_learners(self, learner_id: str, n_similar: int = 5) -> List[str]:
        if learner_id not in self.profile_cache or len(self.profile_cache) < 2:
            return []
        target = self.profile_cache[learner_id]
        sims: List[Tuple[str, float]] = []
        for other_id, other_prof in self.profile_cache.items():
            if other_id == learner_id:
                continue
            sims.append((other_id, self._calculate_profile_similarity(target, other_prof)))
        sims.sort(key=lambda x: x[1], reverse=True)
        return [lid for lid, _ in sims[:n_similar]]


# ========== Entrée contractuelle pour l’API ==========
def get_profiles_for_conversation(features: Dict) -> Dict:
    """
    Fonction appelée par /profile et /recommend (unified_api).
    Sortie SCHÉMA-COMPATIBLE :
    {
      "VARK": {"label": "V|A|R|K", "proba": {...}},
      "MBTI": {"label": "INTJ|... ", "conf": <0..1>},
      "scores": {...}
    }
    """
    # A) Si vous avez un cache de LearnerProfile, vous pouvez le recharger ici
    #    et inférer VARK/MBTI depuis les objets (voir _infer_* ci-dessous).
    #
    # B) Fallback à partir de features scalaires (extraits par votre NLP)
    ls = LearningStyle(
        visual=float(features.get("ls_visual", features.get("visual", 0.25))),
        auditory=float(features.get("ls_auditory", features.get("auditory", 0.25))),
        reading=float(features.get("ls_reading", features.get("reading", 0.25))),
        kinesthetic=float(features.get("ls_kinesthetic", features.get("kinesthetic", 0.25))),
    )
    pers = PersonalityProfile(
        extraversion=float(features.get("pers_extraversion", features.get("extraversion", 0.5))),
        intuition=float(features.get("pers_intuition", features.get("intuition", 0.5))),
        thinking=float(features.get("pers_thinking", features.get("thinking", 0.5))),
        judging=float(features.get("pers_judging", features.get("judging", 0.5))),
    )

    vark_label, vark_scores = _infer_vark_from_learning_style(ls)
    mbti_label, mbti_scores = _infer_mbti_from_personality(pers)

    # scores combinés (facultatif mais utile à l’UI/explicabilité)
    combined_scores: Dict[str, float] = {
        **{f"VARK_{k}": v for k, v in vark_scores.items()},
        **{f"MBTI_{k}": v for k, v in mbti_scores.items()},
    }

    return {
        "VARK": {"label": vark_label, "proba": vark_scores},
        "MBTI": {"label": mbti_label, "conf": max(mbti_scores.values())},
        "scores": combined_scores,
    }


# ========== Petit test manuel ==========
if __name__ == "__main__":
    feats = {
        "ls_visual": 0.7, "ls_auditory": 0.1, "ls_reading": 0.15, "ls_kinesthetic": 0.05,
        "pers_extraversion": 0.3, "pers_intuition": 0.8, "pers_thinking": 0.6, "pers_judging": 0.55,
    }
    print(json.dumps(get_profiles_for_conversation(feats), indent=2))
