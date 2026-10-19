from __future__ import annotations

import sqlite3
from datetime import date

from app.categories import age_category
from app.errors import ConflictError, NotFoundError
from app.schemas import AthleteCreate, AthleteOut


def _to_athlete(row: sqlite3.Row) -> AthleteOut:
    birth_date = date.fromisoformat(row["birth_date"])
    certificate = row["medical_certificate_valid_until"]
    return AthleteOut(
        id=row["id"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        birth_date=birth_date,
        sex=row["sex"],
        club=row["club"],
        license_number=row["license_number"],
        medical_certificate_valid_until=date.fromisoformat(certificate) if certificate else None,
        category=age_category(birth_date),
    )


def list_athletes(conn: sqlite3.Connection, club: str | None = None) -> list[AthleteOut]:
    sql = "SELECT * FROM athletes"
    params: tuple[str, ...] = ()
    if club is not None:
        sql += " WHERE club = ?"
        params = (club,)
    sql += " ORDER BY last_name, first_name, id"
    return [_to_athlete(row) for row in conn.execute(sql, params)]


def get_athlete(conn: sqlite3.Connection, athlete_id: int) -> AthleteOut:
    row = conn.execute("SELECT * FROM athletes WHERE id = ?", (athlete_id,)).fetchone()
    if row is None:
        raise NotFoundError(f"Athlète {athlete_id} introuvable")
    return _to_athlete(row)


def create_athlete(conn: sqlite3.Connection, data: AthleteCreate) -> AthleteOut:
    existing = conn.execute(
        "SELECT id FROM athletes WHERE license_number = ?", (data.license_number,)
    ).fetchone()
    if existing is not None:
        raise ConflictError(f"Licence {data.license_number} déjà enregistrée")

    certificate = data.medical_certificate_valid_until
    cursor = conn.execute(
        "INSERT INTO athletes (first_name, last_name, birth_date, sex, club, license_number,"
        " medical_certificate_valid_until) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            data.first_name,
            data.last_name,
            data.birth_date.isoformat(),
            data.sex.value,
            data.club,
            data.license_number,
            certificate.isoformat() if certificate else None,
        ),
    )
    row = conn.execute("SELECT * FROM athletes WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return _to_athlete(row)
