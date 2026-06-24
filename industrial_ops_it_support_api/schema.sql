DROP TABLE IF EXISTS incidents;
DROP TABLE IF EXISTS assets;

CREATE TABLE incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    business_area TEXT NOT NULL,
    system_name TEXT NOT NULL,
    reported_by TEXT NOT NULL,
    priority TEXT NOT NULL CHECK (priority IN ('Low', 'Medium', 'High', 'Critical')),
    status TEXT NOT NULL CHECK (status IN ('Open', 'In Progress', 'Resolved')),
    downtime_minutes INTEGER NOT NULL DEFAULT 0,
    description TEXT NOT NULL,
    resolution_notes TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_tag TEXT NOT NULL UNIQUE,
    asset_type TEXT NOT NULL,
    business_area TEXT NOT NULL,
    location TEXT NOT NULL,
    status TEXT NOT NULL,
    assigned_system TEXT NOT NULL
);

