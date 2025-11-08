
-- Feature store minimal
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    latest_mbti TEXT,
    latest_vark TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    course TEXT,
    lang TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS nlp_features (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    feature_key TEXT NOT NULL,
    feature_value TEXT,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    vark_label TEXT,
    vark_proba_json TEXT,
    mbti_label TEXT,
    mbti_conf REAL,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_features_session ON nlp_features(session_id);
CREATE INDEX IF NOT EXISTS idx_profiles_session ON profiles(session_id);

-- A/B testing events
CREATE TABLE IF NOT EXISTS ab_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    session_id TEXT,
    variant TEXT,
    metric_key TEXT,
    metric_value REAL,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
