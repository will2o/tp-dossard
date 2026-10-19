from __future__ import annotations

from fastapi import APIRouter, status

from app.db import Conn
from app.repositories import athletes
from app.schemas import AthleteCreate, AthleteOut

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
