-- SQLite Edge Buffer Schema
-- Used when Redis/PostgreSQL are unavailable

CREATE TABLE IF NOT EXISTS inspection_buffer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    part_id TEXT NOT NULL,
    result TEXT NOT NULL CHECK (result IN ('OK', 'NG')),
    defect_class TEXT,
    station TEXT DEFAULT 'Station-1',
    confidence REAL DEFAULT 0,
    error_code TEXT,
    timestamp TEXT DEFAULT (datetime('now')),
    synced INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_buffer_synced ON inspection_buffer(synced);

PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
