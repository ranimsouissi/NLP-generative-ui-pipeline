
# Integration Pack (schemas + adapter + flow + DDL)

## Ce que contient
- `data_contracts/*.schema.json` : Schémas JSON (entrées/sorties)
- `apps/gen/ui_adapter.py` : mapping VARK/MBTI -> UI
- `orchestration/flows.py` : pipeline Prefect (stub)
- `feature_store/ddl.sql` : tables minimales (users/sessions/features/profiles/ab_events)

## Intégration
1. Validez vos payloads contre `data_contracts/*.schema.json` (jsonschema).
2. Branchez votre `profile_generator.py` pour produire `profiles` (VARK/MBTI).
3. Utilisez `ui_adapter.ui_from_profile` dans votre générateur UI.
4. Créez les tables (ex: SQLite) avec `feature_store/ddl.sql`.
5. Orquestrez via `orchestration/flows.py` (Prefect).
