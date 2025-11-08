
from prefect import flow, task

@task
def extract():
    # TODO: charger JSON de conversations (disk/db/api)
    return []

@task
def preprocess(batch):
    # TODO: nettoyage, normalisation
    return batch

@task
def features(clean):
    # TODO: extraire features (linguistique, comportement)
    return [{"features": {}, "conversation": c} for c in clean]

@task
def profiles(items):
    # TODO: appeler vos classifieurs VARK/MBTI
    for it in items:
        it["profiles"] = {"VARK":"R","MBTI":"INTJ"}
    return items

@task
def prompts(items):
    # TODO: build prompt en fonction de profiles/features
    return items

@task
def generate(items):
    # TODO: appel modèle génératif (T5/GPT)
    return items

@task
def log(items):
    # TODO: persister outputs & métriques
    return True

@flow
def unified_pipeline():
    raw = extract()
    clean = preprocess(raw)
    feats = features(clean)
    prof = profiles(feats)
    pr = prompts(prof)
    gen = generate(pr)
    log(gen)

if __name__ == "__main__":
    unified_pipeline()
