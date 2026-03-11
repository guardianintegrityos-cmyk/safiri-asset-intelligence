-- Identity Graph Tables for Safiri Asset Matcher
CREATE TABLE identity_core (
    identity_id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    national_id VARCHAR(64) UNIQUE,
    postal_address TEXT,
    phone VARCHAR(64),
    email VARCHAR(255),
    date_of_birth DATE
);

CREATE TABLE assets (
    asset_id SERIAL PRIMARY KEY,
    identity_id INTEGER REFERENCES identity_core(identity_id),
    asset_type VARCHAR(128) NOT NULL, -- cash, shares, safe_deposit
    institution VARCHAR(255) NOT NULL,
    account_number VARCHAR(128),
    amount DECIMAL(15,2),
    status VARCHAR(64)
);

CREATE TABLE identity_alias (
    alias_id SERIAL PRIMARY KEY,
    identity_id INTEGER REFERENCES identity_core(identity_id),
    name_variations TEXT,
    previous_addresses TEXT,
    alternative_ids TEXT
);

CREATE TABLE identity_links (
    link_id SERIAL PRIMARY KEY,
    identity_id INTEGER REFERENCES identity_core(identity_id),
    linked_identifier VARCHAR(255) NOT NULL,
    identifier_type VARCHAR(64) NOT NULL, -- phone, email, account
    confidence_score DECIMAL(3,2) DEFAULT 1.0
);
