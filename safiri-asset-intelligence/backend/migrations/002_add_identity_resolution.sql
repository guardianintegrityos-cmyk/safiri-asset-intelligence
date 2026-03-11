-- Identity Resolution Engine (IRE) Tables
-- Extends the identity graph with clustering capabilities

CREATE TABLE identity_clusters (
    cluster_id SERIAL PRIMARY KEY,
    representative_name VARCHAR(255) NOT NULL,
    representative_address TEXT,
    cluster_size INTEGER NOT NULL DEFAULT 1,
    confidence_score DECIMAL(3,2) NOT NULL DEFAULT 0.0,
    country VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    validated BOOLEAN DEFAULT FALSE
);

CREATE TABLE cluster_members (
    member_id SERIAL PRIMARY KEY,
    cluster_id INTEGER REFERENCES identity_clusters(cluster_id) ON DELETE CASCADE,
    identity_id INTEGER REFERENCES identity_core(identity_id),
    source_table VARCHAR(64) NOT NULL, -- identity_core, identity_alias, etc.
    source_record_id INTEGER NOT NULL,
    similarity_score DECIMAL(3,2) NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE identity_resolution_log (
    log_id SERIAL PRIMARY KEY,
    query_hash VARCHAR(64) NOT NULL,
    query_params JSONB,
    resolved_cluster_id INTEGER REFERENCES identity_clusters(cluster_id),
    confidence_score DECIMAL(3,2),
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_identity_clusters_country ON identity_clusters(country);
CREATE INDEX idx_identity_clusters_confidence ON identity_clusters(confidence_score DESC);
CREATE INDEX idx_cluster_members_cluster_id ON cluster_members(cluster_id);
CREATE INDEX idx_cluster_members_identity_id ON cluster_members(identity_id);
CREATE INDEX idx_resolution_log_query_hash ON identity_resolution_log(query_hash);
CREATE INDEX idx_resolution_log_created_at ON identity_resolution_log(created_at DESC);

-- Update trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_identity_clusters_updated_at
    BEFORE UPDATE ON identity_clusters
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();