"""SUTMS dashboard and reporting API.

This module intentionally exposes only the dashboard/reporting surface. Core
user, timetable editing, and scheduler modules remain owned by their teams.
"""

import csv
import io
import os
from datetime import date

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://sutms:sutms@localhost:5432/sutms")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

app = FastAPI(title="SUTMS Dashboard & Reports API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


def query_all(statement: str, **params: object) -> list[dict]:
    try:
        with engine.connect() as connection:
            return [dict(row) for row in connection.execute(text(statement), params).mappings()]
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Reporting database is unavailable") from exc


@app.get("/health")
def health() -> dict[str, str]:
    query_all("SELECT 1 AS status")
    return {"status": "ok", "service": "dashboard-reports"}


@app.get("/api/dashboard/summary")
def dashboard_summary(semester_id: int = Query(1, ge=1)) -> dict:
    """Return the four summary cards consumed by the dashboard."""
    rows = query_all("SELECT * FROM dashboard_summary WHERE semester_id = :semester_id", semester_id=semester_id)
    if not rows:
        raise HTTPException(status_code=404, detail="No reporting data for this semester")
    return rows[0]


@app.get("/api/dashboard/room-utilization")
def room_utilization(semester_id: int = Query(1, ge=1)) -> list[dict]:
    return query_all(
        "SELECT room_code, room_name, scheduled_hours, available_hours, utilization_percent "
        "FROM room_utilization_report WHERE semester_id = :semester_id ORDER BY utilization_percent DESC, room_code",
        semester_id=semester_id,
    )


@app.get("/api/dashboard/department-sessions")
def department_sessions(semester_id: int = Query(1, ge=1)) -> list[dict]:
    return query_all(
        "SELECT department_name, scheduled_sessions, session_share_percent "
        "FROM department_session_report WHERE semester_id = :semester_id ORDER BY scheduled_sessions DESC",
        semester_id=semester_id,
    )


@app.get("/api/dashboard/lecturer-workload")
def lecturer_workload(semester_id: int = Query(1, ge=1)) -> list[dict]:
    return query_all(
        "SELECT lecturer_name, department_name, assigned_hours, max_teaching_hours, load_percent, status "
        "FROM lecturer_workload_report WHERE semester_id = :semester_id ORDER BY load_percent DESC, lecturer_name",
        semester_id=semester_id,
    )


@app.get("/api/dashboard/conflicts")
def conflict_watch(semester_id: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)) -> list[dict]:
    return query_all(
        "SELECT conflict_type, description, severity, status, detected_at "
        "FROM conflict_report WHERE semester_id = :semester_id ORDER BY detected_at DESC LIMIT :limit",
        semester_id=semester_id,
        limit=limit,
    )


REPORTS = {
    "room-utilization": "SELECT room_code, room_name, scheduled_hours, available_hours, utilization_percent FROM room_utilization_report WHERE semester_id = :semester_id ORDER BY room_code",
    "lecturer-workload": "SELECT lecturer_name, department_name, assigned_hours, max_teaching_hours, load_percent, status FROM lecturer_workload_report WHERE semester_id = :semester_id ORDER BY lecturer_name",
    "conflicts": "SELECT conflict_type, description, severity, status, detected_at FROM conflict_report WHERE semester_id = :semester_id ORDER BY detected_at DESC",
}


@app.get("/api/reports/{report_name}.csv")
def export_report(report_name: str, semester_id: int = Query(1, ge=1)) -> StreamingResponse:
    """Download one report as a CSV file that opens in Excel/Google Sheets."""
    statement = REPORTS.get(report_name)
    if statement is None:
        raise HTTPException(status_code=404, detail="Unknown report")
    rows = query_all(statement, semester_id=semester_id)
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]) if rows else ["message"])
    writer.writeheader()
    writer.writerows(rows if rows else [{"message": "No data"}])
    filename = f"sutms-{report_name}-{date.today().isoformat()}.csv"
    return StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
