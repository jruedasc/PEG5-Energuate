#!/bin/sh
# entrypoint.sh

# Espera a que Postgres esté listo
until nc -z $DB_HOST $DB_PORT; do
  echo "Esperando a que PostgreSQL esté disponible..."
  sleep 1
done

# Ejecuta migraciones
flask db upgrade

# Arranca el servidor en el puerto 8090
exec flask run --host=0.0.0.0 --port=8090
