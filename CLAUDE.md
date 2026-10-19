# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commandes

- Lancer les tests : `pytest` (un seul test : `pytest tests/test_athletes.py::test_list_athletes_filters_by_club`).
- Lancer `pytest` avant tout commit ; ne pas committer si un test échoue.
- Après toute modification Python, lancer `ruff check . && ruff format .`.

## Erreurs

- Lever une sous-classe d'`ApiError` définie dans `app/errors.py` ; ne jamais lever `HTTPException`.
- Le format d'erreur est `{"error": {"code": "...", "message": "..."}}`, produit par le handler global de `app/main.py`.

## Tests

- Réutiliser les fixtures de `tests/conftest.py` : `client`, `make_competition`, `make_event`, `make_athlete`, `make_registration`.
- Un fichier de test par router : `tests/test_<router>.py`.
- Tester les cas d'erreur de chaque route : 404, 409 et 422.

## Documentation

- Toute route ajoutée ou modifiée : ajouter ou modifier sa ligne dans `docs/api.md`.
- Toute route ajoutée ou modifiée : ajouter une entrée en tête de la section « Non publié » de `CHANGELOG.md` (créer le fichier s'il n'existe pas).

## Interdits

- `scripts/legacy/` : lecture autorisée ; ne rien modifier ni supprimer sans demande explicite.
- Ne pas ajouter de dépendance (`pyproject.toml`) sans demander.
- Ne jamais lire ni afficher .env : il contient des secrets.
