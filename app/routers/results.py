from __future__ import annotations

from fastapi import APIRouter, Response

from app.db import Conn
from app.errors import NotFoundError
from app.ranking import rank_results
from app.repositories import results
from app.schemas import RankingEntry, ResultIn, ResultOut, ResultUnit

router = APIRouter(tags=["results"])


@router.put(
    "/registrations/{registration_id}/result",
    response_model=ResultOut,
    summary="Enregistrer le résultat d'une inscription",
)
def record_result(registration_id: int, data: ResultIn, conn: Conn) -> ResultOut:
    return results.record_result(conn, registration_id, data.performance)


@router.get(
    "/events/{event_id}/ranking",
    response_model=list[RankingEntry],
    summary="Lister le classement d'une épreuve",
)
def get_ranking(event_id: int, conn: Conn) -> list[RankingEntry]:
    event = results.find_event(conn, event_id)
    if not event:
        raise NotFoundError(f"Épreuve {event_id} introuvable")
    return rank_results(results.ranking_rows(conn, event_id), ResultUnit(event["unit"]))


@router.get(
    "/competitions/{competition_id}/results.csv",
    summary="Exporter les résultats d'une compétition en CSV",
)
def export_csv(competition_id: int, conn: Conn) -> Response:
    csv = results.export_csv(conn, competition_id)
    return Response(content=csv, media_type="text/csv")
