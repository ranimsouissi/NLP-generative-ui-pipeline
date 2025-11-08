# feature_extractor.py
def extract_features(conversation: dict) -> dict:
    turns = conversation.get("turns", [])
    texts = [t.get("text","") for t in turns if isinstance(t, dict)]
    n = max(1, len(texts))
    return {
        "avg_turn_len": sum(len(t) for t in texts)/n,
        "question_ratio": sum(1 for t in texts if "?" in t)/n
    }
