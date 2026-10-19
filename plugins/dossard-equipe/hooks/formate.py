"""Hook PostToolUse : formate avec ruff le fichier Python que Claude vient d'écrire."""

from __future__ import annotations

import json
import subprocess
import sys

entree = json.load(sys.stdin)
chemin = str(entree.get("tool_input", {}).get("file_path", ""))
if chemin.endswith(".py"):
    subprocess.run([sys.executable, "-m", "ruff", "format", "--quiet", chemin], check=False)
