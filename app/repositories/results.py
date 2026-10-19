from __future__ import annotations

import csv
import io
import sqlite3
from datetime import UTC, datetime

from app.errors import ConflictError, NotFoundError
from app.schemas import ResultOut, ResultUnit

CSV_HEADER = [
    "competition",
    "event",
    "unit",
    "bib",
    "first_name",
    "last_name",
    "birth_date",
    "sex",
    "club",
    "license_number",
    "medical_certificate_valid_until",
    "performance",
]


def record_result(conn: sqlite3.Connection, registration_id: int, performance: float) -> ResultOut:
    registration = conn.execute(
        "SELECT r.id, r.status, c.status AS competition_status"
        " FROM registrations r"
        " JOIN events e ON e.id = r.event_id"
        " JOIN competitions c ON c.id = e.competition_id"
        " WHERE r.id = ?",
        (registration_id,),
    ).fetchone()
    if registration is None:
        raise NotFoundError(f"Inscription {registration_id} introuvable")
    if registration["status"] != "confirmed" or registration["competition_status"] != "closed":
        raise ConflictError(
            "Résultat possible seulement sur une inscription confirmée d'une compétition close",
            code="results_not_allowed",
        )

    recorded_at = datetime.now(UTC)
    conn.execute(
        "INSERT INTO results (registration_id, performance, recorded_at) VALUES (?, ?, ?)"
        " ON CONFLICT (registration_id) DO UPDATE"
        " SET performance = excluded.performance, recorded_at = excluded.recorded_at",
        (registration_id, performance, recorded_at.isoformat()),
    )
    return ResultOut(
        registration_id=registration_id, performance=performance, recorded_at=recorded_at
    )


def find_event(conn: sqlite3.Connection, event_id: int) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()


def ranking_rows(conn: sqlite3.Connection, event_id: int) -> list[sqlite3.Row]:
    """Inscriptions confirmées de l'épreuve qui ont un résultat."""
    return conn.execute(
        "SELECT r.bib, r.athlete_id, a.last_name, a.first_name, a.club, res.performance"
        " FROM results res"
        " JOIN registrations r ON r.id = res.registration_id"
        " JOIN athletes a ON a.id = r.athlete_id"
        " WHERE r.event_id = ? AND r.status = 'confirmed'"
        " ORDER BY r.bib",
        (event_id,),
    ).fetchall()


def format_performance(unit: ResultUnit, value: float) -> float | int:
    """Les points sont entiers ; temps et distances sont arrondis au centième."""
    if unit is ResultUnit.POINTS:
        return int(value)
    return round(value, 2)


def export_csv(conn: sqlite3.Connection, competition_id: int) -> str:
    competition = conn.execute(
        "SELECT * FROM competitions WHERE id = ?", (competition_id,)
    ).fetchone()
    if competition is None:
        raise NotFoundError(f"Compétition {competition_id} introuvable")

    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=CSV_HEADER, lineterminator="\n")
    writer.writeheader()
    events = conn.execute(
        "SELECT * FROM events WHERE competition_id = ? ORDER BY id", (competition_id,)
    ).fetchall()
    for event in events:
        rows = conn.execute(
            "SELECT r.bib, a.*, res.performance FROM results res"
            " JOIN registrations r ON r.id = res.registration_id"
            " JOIN athletes a ON a.id = r.athlete_id"
            " WHERE r.event_id = ? AND r.status = 'confirmed' ORDER BY r.bib",
            (event["id"],),
        ).fetchall()
        unit = ResultUnit(event["unit"])
        for row in rows:
            writer.writerow(
                {
                    "competition": competition["name"],
                    "event": event["name"],
                    "unit": unit.value,
                    "bib": row["bib"],
                    "first_name": row["first_name"],
                    "last_name": row["last_name"],
                    "birth_date": row["birth_date"],
                    "sex": row["sex"],
                    "club": row["club"] or "",
                    "license_number": row["license_number"],
                    "medical_certificate_valid_until": row["medical_certificate_valid_until"] or "",
                    "performance": format_performance(unit, row["performance"]),
                }
            )
    return out.getvalue()
