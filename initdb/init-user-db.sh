#!/usr/bin/env bash
set -euo pipefail
 
echo "=== Iniciando inicializacion de base de datos ==="
echo "Usuario PostgreSQL: ${POSTGRES_USER}"
echo "Base de datos: ${POSTGRES_DB}"
 
# Crear la base de datos energuate si no existe
psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" --dbname="${POSTGRES_DB}" <<-EOSQL
    -- Verificar conexion
    SELECT 'Conexion exitosa a PostgreSQL' as status;
    -- Crear base de datos energuate si no existe
    SELECT 'CREATE DATABASE energuate'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'energuate')\gexec
EOSQL
 
echo "=== Inicializacion completada ==="