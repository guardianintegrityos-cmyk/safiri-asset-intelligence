-- Alembic-style initial migration for Safiri
CREATE TABLE institutions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    country VARCHAR(64) NOT NULL
);

CREATE TABLE owners (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    national_id VARCHAR(64) UNIQUE
);

CREATE TABLE claims (
    id SERIAL PRIMARY KEY,
    asset_type VARCHAR(128) NOT NULL,
    asset_id VARCHAR(128) NOT NULL,
    claimant_name VARCHAR(255),
    created_at TIMESTAMP,
    owner_id INTEGER REFERENCES owners(id),
    institution_id INTEGER REFERENCES institutions(id)
);
