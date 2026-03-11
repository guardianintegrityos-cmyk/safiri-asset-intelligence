-- Owners
CREATE TABLE IF NOT EXISTS owners (
    owner_id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    id_number VARCHAR(50) UNIQUE,
    dob DATE,
    phone VARCHAR(20),
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Assets
CREATE TABLE IF NOT EXISTS assets (
    asset_id SERIAL PRIMARY KEY,
    owner_id INT REFERENCES owners(owner_id),
    asset_type VARCHAR(100),
    institution VARCHAR(100),
    balance NUMERIC(20,2),
    status VARCHAR(50) DEFAULT 'Unclaimed',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Claims
CREATE TABLE IF NOT EXISTS claims (
    claim_id SERIAL PRIMARY KEY,
    asset_id INT REFERENCES assets(asset_id),
    claimed_by VARCHAR(255),
    status VARCHAR(50) DEFAULT 'Pending',
    submission_date TIMESTAMP DEFAULT NOW(),
    approval_date TIMESTAMP
);

-- Audit trail
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id SERIAL PRIMARY KEY,
    action VARCHAR(255),
    user VARCHAR(255),
    timestamp TIMESTAMP DEFAULT NOW(),
    details JSONB
);
