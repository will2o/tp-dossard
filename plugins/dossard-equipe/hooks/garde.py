#!/usr/bin/env python3
"""Hook PreToolUse : bloque les commandes shell destructrices.

Lit le JSON de Claude Code sur l'entrée standard. Pour les outils Bash et
PowerShell, sort avec le code 2 (et un message sur stderr) si la commande
contient rm -rf, git push --force / -f, ou DROP TABLE / DROP VIEW.
"""

import json
import re
import sys

SHELLS = {"Bash", "PowerShell"}
SEPARATEURS = re.compile(r"[;&|\n]+")
SQL_DESTRUCTEUR = re.compile(r"\bDROP\s+(TABLE|VIEW)\b", re.IGNORECASE)


def options_courtes(jetons: list[str]) -> tuple[set[str], set[str]]:
    """Lettres des options courtes (-rf, -r -f...) et noms des options longues."""
    courtes, longues = set(), set()
    for jeton in jetons:
        if jeton.startswith("--"):
            longues.add(jeton.split("=", 1)[0])
        elif jeton.startswith("-") and len(jeton) > 1:
            courtes.update(jeton[1:])
    return courtes, longues


def est_rm_rf(jetons: list[str]) -> bool:
    if "rm" not in jetons:
        return False
    courtes, longues = options_courtes(jetons[jetons.index("rm") + 1 :])
    recursif = "r" in courtes or "R" in courtes or "--recursive" in longues
    force = "f" in courtes or "--force" in longues
    return recursif and force


def est_push_force(jetons: list[str]) -> bool:
    if "git" not in jetons:
        return False
    apres_git = jetons[jetons.index("git") + 1 :]
    if "push" not in apres_git:
        return False
    courtes, longues = options_courtes(apres_git[apres_git.index("push") + 1 :])
    return "f" in courtes or "--force" in longues


def raison_du_blocage(commande: str) -> str | None:
    if SQL_DESTRUCTEUR.search(commande):
        return "DROP TABLE / DROP VIEW interdit"
    for segment in SEPARATEURS.split(commande):
        jetons = segment.split()
        if est_rm_rf(jetons):
            return "rm -rf interdit"
        if est_push_force(jetons):
            return "git push --force interdit"
    return None


def main() -> int:
    try:
        donnees = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    if not isinstance(donnees, dict) or donnees.get("tool_name") not in SHELLS:
        return 0
    entree = donnees.get("tool_input")
    commande = entree.get("command") if isinstance(entree, dict) else None
    if not isinstance(commande, str):
        return 0
    raison = raison_du_blocage(commande)
    if raison is None:
        return 0
    sys.stderr.reconfigure(encoding="utf-8")
    print(f"Bloqué par le hook garde.py : {raison}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
