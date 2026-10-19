# Changelog

## Non publié

- Ajout de `POST /athletes/import` : import du CSV des licenciés (licences existantes ignorées, lignes invalides rapportées avec leur numéro). Remplace `scripts/legacy/import_licencies.py`, supprimé.
- Ajout de `GET /athletes/{athlete_id}` : détail d'un athlète (404 si introuvable).
