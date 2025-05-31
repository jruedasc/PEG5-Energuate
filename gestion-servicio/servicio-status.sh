#!/usr/bin/env bash
set -euo pipefail

# Valido ii no es pegsvc, cambiar de usuario y re-ejecutar
[ "$(whoami)" = "pegsvc" ] || exec sudo -u pegsvc "$0" "$@"

# Verificar estar en el directorio /srv/peg5/PEG5-Energuate
[ -d "/srv/peg5/PEG5-Energuate" ] || { echo "[ERROR] Directorio /srv/peg5/PEG5-Energuate no existe" >&2; exit 1; }

cd /srv/peg5/PEG5-Energuate || exit 1
echo "[INFO] Estado de servicios como usuario pegsvc..."
docker-compose ps