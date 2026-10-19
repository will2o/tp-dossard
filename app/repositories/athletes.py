from __future__ import annotations

import csv
import io
import sqlite3
from datetime import date, datetime

from pydantic import ValidationError

from app.categories import age_category
from app.errors import ConflictError, NotFoundError, UnprocessableError
from app.schemas import AthleteCreate, AthleteImportReport, AthleteOut, ImportLineError

IMPORT_COLUMNS = (
    "nom",
    "prenom",
    "date_naissance",
    "sexe",
    "club",
    "licence",
    "certificat_valide_jusqu",
)


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


def _parse_import_date(value: str) -> date | None:
    """Convertit jj/mm/aaaa en date ; une valeur vide donne None."""
    value = value.strip()
    if not value:
        return None
    return datetime.strptime(value, "%d/%m/%Y").date()


def _to_athlete_create(row: dict[str, str]) -> AthleteCreate:
    birth_date = _parse_import_date(row["date_naissance"])
    if birth_date is None:
        raise ValueError("date_naissance manquante")
    return AthleteCreate(
        last_name=row["nom"].strip(),
        first_name=row["prenom"].strip(),
        birth_date=birth_date,
        sex=row["sexe"].strip(),
        club=row["club"].strip() or None,
        license_number=row["licence"].strip(),
        medical_certificate_valid_until=_parse_import_date(row["certificat_valide_jusqu"]),
    )


def import_athletes(conn: sqlite3.Connection, content: str) -> AthleteImportReport:
    """Importe un CSV de licenciés (séparateur ;, dates jj/mm/aaaa), ligne par ligne."""
    reader = csv.DictReader(io.StringIO(content), delimiter=";")
    missing = [column for column in IMPORT_COLUMNS if column not in (reader.fieldnames or [])]
    if missing:
        raise UnprocessableError(f"Colonnes manquantes : {', '.join(missing)}")

    created = 0
    skipped = 0
    errors: list[ImportLineError] = []
    for row in reader:
        line = reader.line_num
        if None in row or None in row.values():
            errors.append(ImportLineError(line=line, message="Nombre de colonnes incorrect"))
            continue
        try:
            data = _to_athlete_create(row)
        except ValidationError as exc:
            first = exc.errors()[0]
            field = ".".join(str(part) for part in first["loc"])
            errors.append(ImportLineError(line=line, message=f"{field} : {first['msg']}"))
            continue
        except ValueError as exc:
            errors.append(ImportLineError(line=line, message=f"Date invalide : {exc}"))
            continue
        try:
            create_athlete(conn, data)
        except ConflictError:
            skipped += 1
        else:
            created += 1
    return AthleteImportReport(created=created, skipped=skipped, errors=errors)
