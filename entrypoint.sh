#!/usr/bin/env bash
set -euo pipefail

# Numero maximo de intentos para conectarse a PostgreSQL
MAX_INTENTOS=10
contador=0

# Bucle: mientras PostgreSQL NO este disponible, intenta conectarte
while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
  contador=$((contador + 1))

  # Valida si se ha alcanzado el numero maximo de intentos
  [ "$contador" -ge "$MAX_INTENTOS" ] && {
    echo "Error: No se pudo conectar a PostgreSQL despues de $MAX_INTENTOS intentos."
    exit 1
  }

  echo "Intento $contador/$MAX_INTENTOS: Esperando a que PostgreSQL este disponible..."
  sleep 1
done

# PostgreSQL ya respondio en alguno de los intentos
echo "PostgreSQL disponible; ejecutando migraciones..."
flask db upgrade

# Arranca el servidor Flask en el puerto 8090
exec flask run --host=0.0.0.0 --port=8090
