-- Real SOC2 catalog — Trust Services Criteria (AICPA 2017, revised 2022)
-- Part 1: the 9 "anchor" Common Criteria (CC1.1-CC9.1), mandatory in every
-- SOC2 report (Security category). Each CCx has additional sub-criteria
-- (CC6 alone has 8) — completed in later parts, same logic as NR1's
-- Master Hazard Bank.
-- Source: AICPA Trust Services Criteria, cross-referenced with Secureframe/Drata/SANS.
-- English-only content — international/US market product.

SET search_path TO copilots;

INSERT INTO frameworks (id, nome, versao) VALUES
  ('soc2', 'SOC 2', 'AICPA TSC 2017 (rev. 2022)') ON CONFLICT (id) DO NOTHING;

INSERT INTO controles (id, framework_id, categoria, nome, descricao, obrigatorio) VALUES
('CC1.1', 'soc2', 'Control Environment', 'Integrity and Ethical Values',
 'The organization demonstrates a commitment to integrity and ethical values.', true),
('CC2.1', 'soc2', 'Communication and Information', 'Security Information Communication',
 'The organization obtains/generates and uses quality information to support the functioning of internal control.', true),
('CC3.1', 'soc2', 'Risk Assessment', 'Risk Assessment Objectives',
 'The organization specifies objectives with sufficient clarity to enable identification and assessment of risks.', true),
('CC4.1', 'soc2', 'Monitoring Activities', 'Ongoing and Independent Evaluations',
 'The organization selects, develops, and performs ongoing and/or separate evaluations to ascertain whether internal control components are present and functioning.', true),
('CC5.1', 'soc2', 'Control Activities', 'Control Activity Selection and Development',
 'The organization selects and develops control activities that contribute to the mitigation of risks to acceptable levels.', true),
('CC6.1', 'soc2', 'Logical and Physical Access Controls', 'Logical Access Controls',
 'The organization implements logical access controls to protect against threats from sources outside its system boundaries.', true),
('CC6.2', 'soc2', 'Logical and Physical Access Controls', 'Access Provisioning and Deprovisioning',
 'Prior to granting access, user identity is registered and authorized; access is removed when no longer required.', true),
('CC6.3', 'soc2', 'Logical and Physical Access Controls', 'Access Privilege Management',
 'The organization authorizes, modifies, or removes access based on roles, responsibilities, or system design, applying the principle of least privilege.', true),
('CC7.1', 'soc2', 'System Operations', 'Vulnerability Detection',
 'The organization uses detection and monitoring procedures to identify configuration changes that introduce vulnerabilities and malicious components.', true),
('CC7.2', 'soc2', 'System Operations', 'Security Event Monitoring',
 'The organization monitors system components and the operation of those components for anomalies.', true),
('CC8.1', 'soc2', 'Change Management', 'Change Management',
 'The organization authorizes, designs, develops/acquires, configures, documents, tests, approves, and implements changes to infrastructure, data, software, and procedures.', true),
('CC9.1', 'soc2', 'Risk Mitigation', 'Business Risk Mitigation',
 'The organization identifies, selects, and develops risk mitigation activities for risks arising from potential business disruptions.', true),
('A1.2', 'soc2', 'Availability', 'Capacity and Availability Monitoring',
 'The organization monitors infrastructure and software for performance and availability, and implements recovery measures (backup, DR) to meet availability objectives.', false)
ON CONFLICT (id) DO NOTHING;

INSERT INTO perguntas (id, controle_id, texto) VALUES
('Q-CC1.1', 'CC1.1', 'Is there a formalized code of conduct/ethics communicated to employees?'),
('Q-CC2.1', 'CC2.1', 'Is there a documented and communicated information security policy?'),
('Q-CC3.1', 'CC3.1', 'Is there a documented, formal risk assessment process?'),
('Q-CC4.1', 'CC4.1', 'Are periodic internal audits or independent evaluations of controls performed?'),
('Q-CC5.1', 'CC5.1', 'Are documented controls mapped to the identified risks?'),
('Q-CC6.1', 'CC6.1', 'Is logical access control (firewall, VPN, authentication) documented?'),
('Q-CC6.2', 'CC6.2', 'Is there a formal onboarding/offboarding process for system access?'),
('Q-CC6.3', 'CC6.3', 'Is access granted by role/function with periodic privilege review?'),
('Q-CC7.1', 'CC7.1', 'Is a vulnerability scanning tool run periodically?'),
('Q-CC7.2', 'CC7.2', 'Is there a SIEM or security event monitoring tool in place?'),
('Q-CC8.1', 'CC8.1', 'Is there a formal change management process (approval, testing, deployment)?'),
('Q-CC9.1', 'CC9.1', 'Is there a documented business continuity / incident response plan?'),
('Q-A1.2', 'A1.2', 'Is there automated backup and a tested disaster recovery plan?')
ON CONFLICT (id) DO NOTHING;
