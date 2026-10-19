# Changelog

## Non publié

- Harmonisation du router des résultats : `GET /events/{event_id}/ranking` renvoie désormais la liste nue des entrées (plus d'enveloppe `{"data", "count"}`) et un 404 au format d'erreur standard (`not_found`) ; `summary` en français ajouté aux trois routes.
- Ajout de la pagination à `GET /athletes` : `?limit=` (1 à 100, défaut 50) et `?offset=` (≥ 0, défaut 0), appliquées après le filtre `?club=`. Valeurs hors bornes : 422.
- Ajout de `POST /athletes/import` : import du CSV des licenciés (licences existantes ignorées, lignes invalides rapportées avec leur numéro). Remplace `scripts/legacy/import_licencies.py`, supprimé.
- Ajout de `GET /athletes/{athlete_id}` : détail d'un athlète (404 si introuvable).
