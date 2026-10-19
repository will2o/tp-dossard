from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Body, status

from app.db import Conn
from app.errors import UnprocessableError
from app.repositories import athletes
from app.schemas import AthleteCreate, AthleteImportReport, AthleteOut

router = APIRouter(prefix="/athletes", tags=["athletes"])


@router.get("", response_model=list[AthleteOut])
def list_athletes(conn: Conn, club: str | None = None) -> list[AthleteOut]:
    return athletes.list_athletes(conn, club=club)


@router.get("/{athlete_id}", response_model=AthleteOut)
def get_athlete(athlete_id: int, conn: Conn) -> AthleteOut:
    return athletes.get_athlete(conn, athlete_id)


@router.post("", response_model=AthleteOut, status_code=status.HTTP_201_CREATED)
def create_athlete(data: AthleteCreate, conn: Conn) -> AthleteOut:
    return athletes.create_athlete(conn, data)


@router.post("/import", response_model=AthleteImportReport)
def import_athletes(
    body: Annotated[bytes, Body(media_type="text/csv")], conn: Conn
) -> AthleteImportReport:
    try:
        content = body.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise UnprocessableError("Le CSV doit être encodé en UTF-8") from exc
    return athletes.import_athletes(conn, content)
