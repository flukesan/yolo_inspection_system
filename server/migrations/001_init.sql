# PostgreSQL Initial Schema

CREATE TABLE IF NOT EXISTS inspections (
    id SERIAL PRIMARY KEY,
    part_id VARCHAR(100) NOT NULL,
    result VARCHAR(10) NOT NULL CHECK (result IN ('OK', 'NG')),
    defect_class VARCHAR(50),
    station VARCHAR(50) DEFAULT 'Station-1',
    confidence REAL DEFAULT 0,
    error_code VARCHAR(10),
    image_id INTEGER,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_inspections_result ON inspections(result);
CREATE INDEX idx_inspections_timestamp ON inspections(timestamp);
CREATE INDEX idx_inspections_part_id ON inspections(part_id);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('operator', 'engineer')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO users (username, password_hash, role) VALUES
    ('engineer', '$2b$12$placeholder', 'engineer'),
    ('operator', '$2b$12$placeholder', 'operator')
ON CONFLICT (username) DO NOTHING;

CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    key_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    action VARCHAR(100) NOT NULL,
    resource VARCHAR(100),
    details JSONB,
    ip_address INET,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);
