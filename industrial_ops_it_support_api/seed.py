from datetime import UTC, datetime, timedelta
import sqlite3

DATABASE = "industrial_ops_it.db"


def seed_database():
    with sqlite3.connect(DATABASE) as connection:
        with open("schema.sql", "r", encoding="utf-8") as schema_file:
            connection.executescript(schema_file.read())

        now = datetime.now(UTC)
        incidents = [
            (
                "RF scanner login failures during receiving",
                "Distribution",
                "Warehouse Mobility",
                "Receiving Team",
                "High",
                "In Progress",
                45,
                "Users report intermittent login failures on handheld scanners during inbound workflow.",
                None,
                now - timedelta(hours=7),
                now - timedelta(hours=2),
            ),
            (
                "Label printer queue delay",
                "Manufacturing",
                "Print Services",
                "Packaging Team",
                "Medium",
                "Resolved",
                20,
                "Shipping labels were delayed because a print queue stopped processing jobs.",
                "Restarted print service, cleared failed jobs, and validated output with packaging users.",
                now - timedelta(days=1, hours=4),
                now - timedelta(days=1, hours=2),
            ),
            (
                "Inventory report data mismatch",
                "Inventory Control",
                "Inventory Reporting",
                "Inventory Analyst",
                "Critical",
                "Open",
                90,
                "Daily inventory report totals do not match expected cycle count results.",
                None,
                now - timedelta(hours=3),
                now - timedelta(hours=3),
            ),
            (
                "Workstation cannot reach production dashboard",
                "Facilities",
                "Operations Dashboard",
                "Maintenance Supervisor",
                "Medium",
                "Resolved",
                30,
                "One workstation could not access the dashboard used for shift review.",
                "Updated browser settings, flushed DNS cache, and confirmed dashboard access.",
                now - timedelta(days=2),
                now - timedelta(days=2, minutes=-35),
            ),
        ]

        connection.executemany(
            """
            INSERT INTO incidents (
                title, business_area, system_name, reported_by, priority, status,
                downtime_minutes, description, resolution_notes, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    title,
                    business_area,
                    system_name,
                    reported_by,
                    priority,
                    status,
                    downtime_minutes,
                    description,
                    resolution_notes,
                    created_at.isoformat(timespec="seconds"),
                    updated_at.isoformat(timespec="seconds"),
                )
                for (
                    title,
                    business_area,
                    system_name,
                    reported_by,
                    priority,
                    status,
                    downtime_minutes,
                    description,
                    resolution_notes,
                    created_at,
                    updated_at,
                ) in incidents
            ],
        )

        assets = [
            ("RF-1029", "Handheld Scanner", "Distribution", "Receiving Dock", "In Service", "Warehouse Mobility"),
            ("PR-2214", "Label Printer", "Manufacturing", "Packaging Line 2", "In Service", "Print Services"),
            ("WS-3410", "Workstation", "Facilities", "Maintenance Office", "In Service", "Operations Dashboard"),
            ("NW-7781", "Wireless Access Point", "Distribution", "Aisle 14", "Under Review", "Warehouse Mobility"),
        ]

        connection.executemany(
            """
            INSERT INTO assets (
                asset_tag, asset_type, business_area, location, status, assigned_system
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            assets,
        )


if __name__ == "__main__":
    seed_database()
    print("Seeded industrial_ops_it.db with sample incidents and assets.")
