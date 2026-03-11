-- Sample data for Safiri Identity Graph

INSERT INTO identity_core (full_name, national_id, postal_address, phone, email, date_of_birth) VALUES
  ('John Ochieng', '12345678', 'P.O Box 123 Nairobi', '+254700123456', 'john@example.com', '1980-01-01'),
  ('Alice Wanjiku', '87654321', 'P.O Box 456 Nairobi', '+254700654321', 'alice@example.com', '1985-05-05');

INSERT INTO assets (identity_id, asset_type, institution, account_number, amount, status) VALUES
  (1, 'cash', 'Bank X', 'ACC001', 25000.00, 'active'),
  (1, 'shares', 'Company Y', 'SHA001', 120000.00, 'active'),
  (2, 'cash', 'Bank Z', 'ACC002', 50000.00, 'active');

INSERT INTO identity_alias (identity_id, name_variations, previous_addresses, alternative_ids) VALUES
  (1, 'Jon Ochieng, J. Ochieng', 'Old Address Nairobi', 'ALT123'),
  (2, 'A. Wanjiku', 'Previous Nairobi', 'ALT456');

INSERT INTO identity_links (identity_id, linked_identifier, identifier_type, confidence_score) VALUES
  (1, '+254700123456', 'phone', 1.0),
  (1, 'john@example.com', 'email', 1.0),
  (1, 'ACC001', 'account', 1.0),
  (2, '+254700654321', 'phone', 1.0),
  (2, 'alice@example.com', 'email', 1.0);