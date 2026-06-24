# Industrial Operations IT Support API

Portfolio project for an Industrial Operations IT Engineer I role. This backend system models how an IT team can support users, hardware, software, and operational systems in a warehouse, manufacturing, or distribution environment.

## Why This Project Fits Industrial Operations IT

This project demonstrates:

- IT/business systems support through incident tracking and asset records
- Business process analysis through downtime, priority, and resolution metrics
- Statistical reporting for operational support decisions
- Support of users, hardware, software, and IT infrastructure
- Clean REST API design with SQLite persistence
- Documentation that can be used to train users or team members

## Features

- Create, view, update, and close support incidents
- Track affected systems, business areas, equipment, severity, and downtime
- Manage industrial IT assets such as scanners, label printers, workstations, and network devices
- Generate operational reports for open incidents, mean time to resolve, recurring systems, and downtime impact
- Seed realistic sample data for demonstration and interview walkthroughs

## Tech Stack

- Python
- Flask
- SQLite
- REST APIs
- SQL queries and aggregate reporting

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python seed.py
python app.py
```

The API runs at:

```text
http://127.0.0.1:5000
```

## Example Requests

Health check:

```bash
curl http://127.0.0.1:5000/health
```

List incidents:

```bash
curl http://127.0.0.1:5000/incidents
```

Create an incident:

```bash
curl -X POST http://127.0.0.1:5000/incidents \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Warehouse scanner cannot connect to Wi-Fi",
    "business_area": "Distribution",
    "system_name": "RF Scanner Network",
    "reported_by": "Receiving Team",
    "priority": "High",
    "status": "Open",
    "downtime_minutes": 25,
    "description": "Scanner disconnects during inbound receiving workflow."
  }'
```

Close an incident:

```bash
curl -X PATCH http://127.0.0.1:5000/incidents/1 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "Resolved",
    "resolution_notes": "Reconfigured wireless profile and validated scanner connectivity with user."
  }'
```

View reports:

```bash
curl http://127.0.0.1:5000/reports/operations-summary
```

## Interview Talking Points

- I built this project to mirror the type of support, reporting, and process improvement work Industrial Operations IT teams perform.
- The system tracks incidents by business area, affected system, priority, status, downtime, and resolution notes.
- I used aggregate SQL reports to identify recurring issues, systems with the most downtime, and support workload.
- The project connects my Publix retail operations experience with my CS coursework and backend API skills.
- A future version could add authentication, Power BI dashboards, automated alerting, and barcode scanner device logs.

