-- Real ISO/IEC 27001:2022 catalog — Annex A. Part 1: 16 representative
-- controls across the 4 themes (93 controls total). Uses the same
-- "copilots" schema already created for SOC2 (Repositorio dos Agentes/01.../schema.sql).
-- English-only content — international market product.

SET search_path TO copilots;

INSERT INTO frameworks (id, nome, versao) VALUES
  ('iso27001', 'ISO/IEC 27001', '2022 (Annex A)') ON CONFLICT (id) DO NOTHING;

INSERT INTO controles (id, framework_id, categoria, nome, descricao, obrigatorio) VALUES
('ISO-5.1', 'iso27001', 'Organizational', 'Policies for Information Security', 'Information security policy approved by management and communicated.', true),
('ISO-5.2', 'iso27001', 'Organizational', 'Information Security Roles and Responsibilities', 'Security roles and responsibilities clearly defined.', true),
('ISO-5.3', 'iso27001', 'Organizational', 'Segregation of Duties', 'Segregation of duties for conflicting tasks.', true),
('ISO-5.15', 'iso27001', 'Organizational', 'Access Control', 'Formal role-based access control policy.', true),
('ISO-5.23', 'iso27001', 'Organizational', 'Information Security for Use of Cloud Services', 'Security evaluation of cloud providers.', true),
('ISO-5.24', 'iso27001', 'Organizational', 'Information Security Incident Management Planning', 'Security incident response plan.', true),
('ISO-6.3', 'iso27001', 'People', 'Information Security Awareness, Education and Training', 'Periodic security awareness training.', true),
('ISO-6.7', 'iso27001', 'People', 'Remote Working', 'Formal remote work policy.', false),
('ISO-7.1', 'iso27001', 'Physical', 'Physical Security Perimeters', 'Physical security perimeters defined and protected.', true),
('ISO-7.2', 'iso27001', 'Physical', 'Physical Entry', 'Physical access control to secure areas.', true),
('ISO-8.7', 'iso27001', 'Technological', 'Protection Against Malware', 'Active antimalware protection on endpoints and servers.', true),
('ISO-8.8', 'iso27001', 'Technological', 'Management of Technical Vulnerabilities', 'Patch management process.', true),
('ISO-8.13', 'iso27001', 'Technological', 'Information Backup', 'Regular backup with restore testing.', true),
('ISO-8.15', 'iso27001', 'Technological', 'Logging', 'System event logging.', true),
('ISO-8.16', 'iso27001', 'Technological', 'Monitoring Activities', 'Active network/system monitoring.', true),
('ISO-8.24', 'iso27001', 'Technological', 'Use of Cryptography', 'Encryption of sensitive data at rest and in transit.', true)
ON CONFLICT (id) DO NOTHING;
