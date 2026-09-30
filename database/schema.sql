-- =====================================================
-- Swachh-Seva — SQLite Schema
-- All timestamps stored as UTC ISO 8601 strings.
-- Foreign keys must be enabled at connection level.
-- =====================================================

PRAGMA foreign_keys = ON;

-- =============== USERS ===============
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL CHECK (role IN ('CITIZEN','WORKER','ADMIN')),
    is_active     INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0,1)),
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL,
    last_login_at TEXT
);

-- =============== WARDS ===============
CREATE TABLE IF NOT EXISTS wards (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    code        TEXT NOT NULL UNIQUE,
    description TEXT,
    is_active   INTEGER NOT NULL DEFAULT 1,
    created_at  TEXT NOT NULL
);

-- =============== PROFILES ===============
CREATE TABLE IF NOT EXISTS profiles (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL UNIQUE,
    full_name     TEXT NOT NULL,
    phone         TEXT,
    address       TEXT,
    city          TEXT,
    ward_id       INTEGER,
    profile_image TEXT,
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (ward_id) REFERENCES wards(id)
);

-- =============== COMPLAINTS ===============
CREATE TABLE IF NOT EXISTS complaints (
    id                     INTEGER PRIMARY KEY AUTOINCREMENT,
    citizen_id             INTEGER NOT NULL,
    category               TEXT NOT NULL,
    description            TEXT NOT NULL,
    latitude               REAL,
    longitude              REAL,
    address                TEXT,
    ward_id                INTEGER,
    priority               TEXT NOT NULL DEFAULT 'MEDIUM',
    status                 TEXT NOT NULL DEFAULT 'SUBMITTED',
    ai_category_suggestion TEXT,
    ai_priority_suggestion TEXT,
    duplicate_status       TEXT NOT NULL DEFAULT 'NOT_CHECKED',
    created_at             TEXT NOT NULL,
    updated_at             TEXT NOT NULL,
    verified_at            TEXT,
    closed_at              TEXT,
    FOREIGN KEY (citizen_id) REFERENCES users(id),
    FOREIGN KEY (ward_id)    REFERENCES wards(id)
);

-- =============== COMPLAINT IMAGES ===============
CREATE TABLE IF NOT EXISTS complaint_images (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id      INTEGER NOT NULL,
    file_path         TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    mime_type         TEXT NOT NULL,
    file_size         INTEGER NOT NULL,
    uploaded_at       TEXT NOT NULL,
    FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE CASCADE
);

-- =============== COMPLAINT STATUS HISTORY ===============
CREATE TABLE IF NOT EXISTS complaint_status_history (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id INTEGER NOT NULL,
    old_status   TEXT,
    new_status   TEXT NOT NULL,
    changed_by   INTEGER NOT NULL,
    reason       TEXT,
    created_at   TEXT NOT NULL,
    FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by)   REFERENCES users(id)
);

-- =============== PICKUP REQUESTS ===============
CREATE TABLE IF NOT EXISTS pickup_requests (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    citizen_id     INTEGER NOT NULL,
    waste_type     TEXT NOT NULL,
    description    TEXT,
    latitude       REAL,
    longitude      REAL,
    address        TEXT,
    preferred_date TEXT,
    status         TEXT NOT NULL DEFAULT 'SUBMITTED',
    created_at     TEXT NOT NULL,
    updated_at     TEXT NOT NULL,
    FOREIGN KEY (citizen_id) REFERENCES users(id)
);

-- =============== TASKS ===============
CREATE TABLE IF NOT EXISTS tasks (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id      INTEGER,
    pickup_request_id INTEGER,
    worker_id         INTEGER NOT NULL,
    assigned_by       INTEGER NOT NULL,
    status            TEXT NOT NULL DEFAULT 'ASSIGNED',
    assigned_at       TEXT NOT NULL,
    accepted_at       TEXT,
    started_at        TEXT,
    completed_at      TEXT,
    verified_at       TEXT,
    created_at        TEXT NOT NULL,
    updated_at        TEXT NOT NULL,
    FOREIGN KEY (complaint_id)      REFERENCES complaints(id),
    FOREIGN KEY (pickup_request_id) REFERENCES pickup_requests(id),
    FOREIGN KEY (worker_id)         REFERENCES users(id),
    FOREIGN KEY (assigned_by)       REFERENCES users(id),
    CHECK (complaint_id IS NOT NULL OR pickup_request_id IS NOT NULL)
);

-- =============== TASK PROOFS ===============
CREATE TABLE IF NOT EXISTS task_proofs (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id           INTEGER NOT NULL,
    uploaded_by       INTEGER NOT NULL,
    file_path         TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    mime_type         TEXT NOT NULL,
    file_size         INTEGER NOT NULL,
    latitude          REAL,
    longitude         REAL,
    uploaded_at       TEXT NOT NULL,
    FOREIGN KEY (task_id)     REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES users(id)
);

-- =============== TOKEN WALLETS ===============
CREATE TABLE IF NOT EXISTS token_wallets (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL UNIQUE,
    balance         INTEGER NOT NULL DEFAULT 0,
    lifetime_earned INTEGER NOT NULL DEFAULT 0,
    lifetime_spent  INTEGER NOT NULL DEFAULT 0,
    updated_at      TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =============== TOKEN TRANSACTIONS ===============
CREATE TABLE IF NOT EXISTS token_transactions (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    wallet_id        INTEGER NOT NULL,
    user_id          INTEGER NOT NULL,
    transaction_type TEXT NOT NULL,
    amount           INTEGER NOT NULL,
    source_type      TEXT NOT NULL,
    source_id        INTEGER,
    description      TEXT,
    created_at       TEXT NOT NULL,
    FOREIGN KEY (wallet_id) REFERENCES token_wallets(id),
    FOREIGN KEY (user_id)   REFERENCES users(id)
);

-- =============== NOTIFICATIONS ===============
CREATE TABLE IF NOT EXISTS notifications (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL,
    type                TEXT NOT NULL,
    title               TEXT NOT NULL,
    message             TEXT NOT NULL,
    related_entity_type TEXT,
    related_entity_id   INTEGER,
    is_read             INTEGER NOT NULL DEFAULT 0,
    created_at          TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =============== AI CONVERSATIONS ===============
CREATE TABLE IF NOT EXISTS ai_conversations (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    title      TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =============== AI MESSAGES ===============
CREATE TABLE IF NOT EXISTS ai_messages (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    sender_type     TEXT NOT NULL CHECK (sender_type IN ('USER','AI','SYSTEM')),
    message         TEXT NOT NULL,
    created_at      TEXT NOT NULL,
    FOREIGN KEY (conversation_id) REFERENCES ai_conversations(id) ON DELETE CASCADE
);

-- =============== AUDIT LOGS ===============
CREATE TABLE IF NOT EXISTS audit_logs (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    actor_user_id INTEGER,
    action        TEXT NOT NULL,
    entity_type   TEXT,
    entity_id     INTEGER,
    old_value     TEXT,
    new_value     TEXT,
    ip_address    TEXT,
    created_at    TEXT NOT NULL,
    FOREIGN KEY (actor_user_id) REFERENCES users(id)
);

-- =============== SYSTEM SETTINGS ===============
CREATE TABLE IF NOT EXISTS system_settings (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_key   TEXT NOT NULL UNIQUE,
    setting_value TEXT NOT NULL,
    description   TEXT,
    updated_at    TEXT NOT NULL
);

-- =============== INDEXES ===============
CREATE INDEX IF NOT EXISTS idx_complaints_citizen          ON complaints(citizen_id);
CREATE INDEX IF NOT EXISTS idx_complaints_status           ON complaints(status);
CREATE INDEX IF NOT EXISTS idx_complaints_ward             ON complaints(ward_id);
CREATE INDEX IF NOT EXISTS idx_complaints_location         ON complaints(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_tasks_worker                ON tasks(worker_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status                ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_notifications_user          ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_read          ON notifications(user_id, is_read);
CREATE INDEX IF NOT EXISTS idx_token_transactions_user     ON token_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_messages_conversation    ON ai_messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity           ON audit_logs(entity_type, entity_id);