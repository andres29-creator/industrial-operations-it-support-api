from datetime import UTC, datetime
import sqlite3

from flask import Flask, jsonify, request

DATABASE = "industrial_ops_it.db"

app = Flask(__name__)


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def row_to_dict(row):
    return dict(row) if row else None


def validate_incident(payload, partial=False):
    required = [
        "title",
        "business_area",
        "system_name",
        "reported_by",
        "priority",
        "status",
        "downtime_minutes",
        "description",
    ]
    if not partial:
        missing = [field for field in required if field not in payload]
        if missing:
            return f"Missing required fields: {', '.join(missing)}"

    if "priority" in payload and payload["priority"] not in ["Low", "Medium", "High", "Critical"]:
        return "Priority must be Low, Medium, High, or Critical"

    if "status" in payload and payload["status"] not in ["Open", "In Progress", "Resolved"]:
        return "Status must be Open, In Progress, or Resolved"

    if "downtime_minutes" in payload:
        try:
            downtime = int(payload["downtime_minutes"])
        except (TypeError, ValueError):
            return "Downtime minutes must be an integer"
        if downtime < 0:
            return "Downtime minutes cannot be negative"

    return None


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "Industrial Operations IT Support API"})


@app.get("/incidents")
def list_incidents():
    status = request.args.get("status")
    business_area = request.args.get("business_area")

    query = "SELECT * FROM incidents WHERE 1 = 1"
    values = []

    if status:
        query += " AND status = ?"
        values.append(status)

    if business_area:
        query += " AND business_area = ?"
        values.append(business_area)

    query += " ORDER BY created_at DESC"

    with get_connection() as connection:
        incidents = connection.execute(query, values).fetchall()

    return jsonify([row_to_dict(row) for row in incidents])


@app.post("/incidents")
def create_incident():
    payload = request.get_json(force=True)
    error = validate_incident(payload)
    if error:
        return jsonify({"error": error}), 400

    now = datetime.now(UTC).isoformat(timespec="seconds")
    fields = [
        "title",
        "business_area",
        "system_name",
        "reported_by",
        "priority",
        "status",
        "downtime_minutes",
        "description",
    ]
    values = [payload[field] for field in fields]

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO incidents (
                title, business_area, system_name, reported_by, priority, status,
                downtime_minutes, description, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            values + [now, now],
        )
        incident_id = cursor.lastrowid
        incident = connection.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,)).fetchone()

    return jsonify(row_to_dict(incident)), 201


@app.get("/incidents/<int:incident_id>")
def get_incident(incident_id):
    with get_connection() as connection:
        incident = connection.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,)).fetchone()

    if not incident:
        return jsonify({"error": "Incident not found"}), 404

    return jsonify(row_to_dict(incident))


@app.patch("/incidents/<int:incident_id>")
def update_incident(incident_id):
    payload = request.get_json(force=True)
    error = validate_incident(payload, partial=True)
    if error:
        return jsonify({"error": error}), 400

    allowed_fields = [
        "title",
        "business_area",
        "system_name",
        "reported_by",
        "priority",
        "status",
        "downtime_minutes",
        "description",
        "resolution_notes",
    ]
    updates = [field for field in allowed_fields if field in payload]

    if not updates:
        return jsonify({"error": "No valid fields provided"}), 400

    set_clause = ", ".join([f"{field} = ?" for field in updates])
    values = [payload[field] for field in updates]
    values.append(datetime.now(UTC).isoformat(timespec="seconds"))
    values.append(incident_id)

    with get_connection() as connection:
        existing = connection.execute("SELECT id FROM incidents WHERE id = ?", (incident_id,)).fetchone()
        if not existing:
            return jsonify({"error": "Incident not found"}), 404

        connection.execute(
            f"UPDATE incidents SET {set_clause}, updated_at = ? WHERE id = ?",
            values,
        )
        incident = connection.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,)).fetchone()

    return jsonify(row_to_dict(incident))


@app.get("/assets")
def list_assets():
    with get_connection() as connection:
        assets = connection.execute("SELECT * FROM assets ORDER BY business_area, asset_type").fetchall()

    return jsonify([row_to_dict(row) for row in assets])


@app.post("/assets")
def create_asset():
    payload = request.get_json(force=True)
    required = ["asset_tag", "asset_type", "business_area", "location", "status", "assigned_system"]
    missing = [field for field in required if field not in payload]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    with get_connection() as connection:
        try:
            cursor = connection.execute(
                """
                INSERT INTO assets (
                    asset_tag, asset_type, business_area, location, status, assigned_system
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [payload[field] for field in required],
            )
        except sqlite3.IntegrityError:
            return jsonify({"error": "Asset tag already exists"}), 409

        asset = connection.execute("SELECT * FROM assets WHERE id = ?", (cursor.lastrowid,)).fetchone()

    return jsonify(row_to_dict(asset)), 201


@app.get("/reports/operations-summary")
def operations_summary():
    with get_connection() as connection:
        status_counts = connection.execute(
            "SELECT status, COUNT(*) AS count FROM incidents GROUP BY status"
        ).fetchall()
        priority_counts = connection.execute(
            "SELECT priority, COUNT(*) AS count FROM incidents GROUP BY priority"
        ).fetchall()
        downtime_by_area = connection.execute(
            """
            SELECT business_area, SUM(downtime_minutes) AS downtime_minutes
            FROM incidents
            GROUP BY business_area
            ORDER BY downtime_minutes DESC
            """
        ).fetchall()
        recurring_systems = connection.execute(
            """
            SELECT system_name, COUNT(*) AS incident_count, SUM(downtime_minutes) AS downtime_minutes
            FROM incidents
            GROUP BY system_name
            ORDER BY incident_count DESC, downtime_minutes DESC
            LIMIT 5
            """
        ).fetchall()
        open_high_priority = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM incidents
            WHERE status != 'Resolved' AND priority IN ('High', 'Critical')
            """
        ).fetchone()

    return jsonify(
        {
            "status_counts": [row_to_dict(row) for row in status_counts],
            "priority_counts": [row_to_dict(row) for row in priority_counts],
            "downtime_by_business_area": [row_to_dict(row) for row in downtime_by_area],
            "recurring_systems": [row_to_dict(row) for row in recurring_systems],
            "open_high_priority_incidents": open_high_priority["count"],
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
