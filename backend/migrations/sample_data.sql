-- Sample data for Safiri (Kenya + Nigeria)

INSERT INTO institutions (name, country) VALUES
  ('UFAA', 'Kenya'),
  ('CBN', 'Nigeria'),
  ('Equity Bank', 'Kenya'),
  ('GTBank', 'Nigeria');

INSERT INTO owners (name, national_id) VALUES
  ('Alice Mwangi', 'KEN123456'),
  ('John Otieno', 'KEN654321'),
  ('Chinedu Okeke', 'NGA987654'),
  ('Ngozi Eze', 'NGA456789');

INSERT INTO claims (asset_type, asset_id, claimant_name, created_at, owner_id, institution_id) VALUES
  ('Bank Account', 'EQK001', 'Alice Mwangi', '2026-03-09', 1, 3),
  ('Insurance Policy', 'UFAA002', 'John Otieno', '2026-03-09', 2, 1),
  ('Bank Account', 'GTN003', 'Chinedu Okeke', '2026-03-09', 3, 4),
  ('Insurance Policy', 'CBN004', 'Ngozi Eze', '2026-03-09', 4, 2);