import os
import tempfile

import app as support_api


def setup_test_database():
    database_file = tempfile.NamedTemporaryFile(delete=False)
    database_file.close()
    support_api.DATABASE = database_file.name

    with support_api.get_connection() as connection:
        with open("schema.sql", "r", encoding="utf-8") as schema_file:
            connection.executescript(schema_file.read())

    return database_file.name


def test_create_and_report_incident():
    database_path = setup_test_database()
    client = support_api.app.test_client()

    response = client.post(
        "/incidents",
        json={
            "title": "Scanner battery dock failure",
            "business_area": "Distribution",
            "system_name": "Warehouse Mobility",
            "reported_by": "Shipping Team",
            "priority": "High",
            "status": "Open",
            "downtime_minutes": 15,
            "description": "Battery dock does not charge scanners before shift start.",
        },
    )

    assert response.status_code == 201
    assert response.get_json()["priority"] == "High"

    report_response = client.get("/reports/operations-summary")
    report = report_response.get_json()

    assert report_response.status_code == 200
    assert report["open_high_priority_incidents"] == 1
    assert report["recurring_systems"][0]["system_name"] == "Warehouse Mobility"

    os.unlink(database_path)

