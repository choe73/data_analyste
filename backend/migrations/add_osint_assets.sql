-- Track discovered OSINT assets (subdomains, IPs, emails, nameservers)
CREATE TABLE IF NOT EXISTS discovered_assets (
    id SERIAL PRIMARY KEY,
    domain TEXT NOT NULL,
    asset_type TEXT NOT NULL, -- 'subdomain', 'ip', 'email', 'nameserver'
    value TEXT NOT NULL,
    source TEXT, -- 'dnsenum', 'theharvester', 'crtsh', 'whatweb', 'manual'
    first_seen TIMESTAMP DEFAULT NOW(),
    last_seen TIMESTAMP DEFAULT NOW(),
    status TEXT DEFAULT 'active', -- 'active', 'inactive', 'down'
    http_status INTEGER,
    ssl_cert_valid BOOLEAN,
    server_type TEXT, -- 'Apache', 'Nginx', etc.
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(domain, asset_type, value)
);

-- Track MINADER ministry contacts for prospection
CREATE TABLE IF NOT EXISTS ministry_contacts (
    id SERIAL PRIMARY KEY,
    ministry TEXT NOT NULL,
    service TEXT,
    contact_name TEXT,
    email TEXT NOT NULL,
    phone TEXT,
    role TEXT,
    last_contacted TIMESTAMP,
    contact_status TEXT DEFAULT 'pending', -- 'pending', 'contacted', 'interested', 'partner'
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(ministry, email)
);

-- Track DNS nameservers for monitoring
CREATE TABLE IF NOT EXISTS dns_nameservers (
    id SERIAL PRIMARY KEY,
    domain TEXT NOT NULL,
    nameserver TEXT NOT NULL,
    ip_address TEXT,
    last_checked TIMESTAMP DEFAULT NOW(),
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(domain, nameserver)
);

-- Create indexes for performance
CREATE INDEX idx_discovered_assets_domain ON discovered_assets(domain);
CREATE INDEX idx_discovered_assets_type ON discovered_assets(asset_type);
CREATE INDEX idx_discovered_assets_status ON discovered_assets(status);
CREATE INDEX idx_ministry_contacts_email ON ministry_contacts(email);
CREATE INDEX idx_dns_nameservers_domain ON dns_nameservers(domain);

-- Insert MINADER OSINT data
INSERT INTO discovered_assets (domain, asset_type, value, source, status, http_status, ssl_cert_valid, server_type, notes)
VALUES
    ('minader.cm', 'subdomain', 'drcq.minader.cm', 'dnsenum', 'active', 200, true, 'Apache', 'Regional Coordination - HTTP 200'),
    ('minader.cm', 'subdomain', 'infophyto.minader.cm', 'dnsenum', 'active', 200, true, 'Apache', 'Phytosanitary Info'),
    ('minader.cm', 'subdomain', 'phytosanitaire.minader.cm', 'dnsenum', 'active', 200, true, 'Apache', 'Plant Health'),
    ('minader.cm', 'subdomain', 'coopgic.minader.cm', 'dnsenum', 'active', 200, true, 'Apache', 'Cooperatives'),
    ('minader.cm', 'subdomain', 'ssise.minader.cm', 'dnsenum', 'active', 200, true, 'Apache', 'Agricultural Statistics'),
    ('minader.cm', 'subdomain', 'simc.minader.cm', 'dnsenum', 'active', 200, true, 'Apache', 'Market Information'),
    ('minader.cm', 'subdomain', 'agrilittoral.minader.cm', 'dnsenum', 'active', 200, true, 'Apache', 'Coastal Agriculture'),
    ('minader.cm', 'subdomain', 'mail.minader.cm', 'dnsenum', 'active', 302, true, 'Apache', 'Mail server - requires auth'),
    ('minader.cm', 'subdomain', 'farmer-registration.minader.cm', 'dnsenum', 'active', 200, true, 'Apache', 'Farmer Registry'),
    ('minader.cm', 'subdomain', 'pmfa-riz.minader.cm', 'dnsenum', 'active', 200, true, 'Apache', 'Rice Program'),
    ('minader.cm', 'subdomain', 'concours.minader.cm', 'dnsenum', 'down', NULL, false, NULL, 'Port 443 closed - timeout'),
    ('minader.cm', 'ip', '195.24.207.147', 'dnsenum', 'active', NULL, NULL, 'Apache', 'Primary hosting IP'),
    ('minader.cm', 'ip', '154.49.137.185', 'dnsenum', 'down', NULL, NULL, NULL, 'Secondary IP - currently down'),
    ('minader.cm', 'nameserver', 'kim.camnet.cm', 'dnsenum', 'active', NULL, NULL, NULL, 'DNS server - zone transfer successful'),
    ('minader.cm', 'nameserver', 'mbam.camnet.cm', 'dnsenum', 'active', NULL, NULL, NULL, 'DNS server'),
    ('minader.cm', 'nameserver', 'wouri.camnet.cm', 'dnsenum', 'active', NULL, NULL, NULL, 'DNS server')
ON CONFLICT DO NOTHING;

-- Insert MINADER contacts
INSERT INTO ministry_contacts (ministry, service, email, role, contact_status, notes)
VALUES
    ('MINADER', 'Statistics Service', 'sg.sdacl@minader.cm', 'Service Head', 'pending', 'Service de la statistique'),
    ('MINADER', 'Cooperation Service', 'sg.celcom@minader.cm', 'Service Head', 'pending', 'Service de la coopération'),
    ('MINADER', 'Economic Service', 'sg.celtique@minader.cm', 'Service Head', 'pending', 'Service économique'),
    ('ANTIC', 'Registry', 'dg@antic.cm', 'Director General', 'pending', 'Domain registrar - administrative contact'),
    ('ANTIC', 'Domain Management', 'dotcm@antic.cm', 'Domain Manager', 'pending', 'Domain registrant contact')
ON CONFLICT DO NOTHING;

-- Insert DNS nameservers
INSERT INTO dns_nameservers (domain, nameserver, ip_address, status)
VALUES
    ('minader.cm', 'kim.camnet.cm', '165.211.16.106', 'active'),
    ('minader.cm', 'mbam.camnet.cm', '195.24.192.44', 'active'),
    ('minader.cm', 'wouri.camnet.cm', '165.210.33.14', 'active')
ON CONFLICT DO NOTHING;
