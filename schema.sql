DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

DROP TABLE IF EXISTS translation_history;

CREATE TABLE translation_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    image_filename TEXT,
    recognized_text TEXT NOT NULL,
    translated_text TEXT NOT NULL,
    target_language TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- INSERT INTO users (username, password) VALUES ('testuser', 'password');

CREATE INDEX idx_user_id_timestamp ON translation_history (user_id, timestamp DESC);