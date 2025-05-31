# Etapa de construcción
FROM python:3.11-slim
WORKDIR /app

# Copiar y instalar dependencias Python
COPY requirements.txt .

RUN set -eux \
    && echo "Validando existensia de archivo requirements.txt" \
    && [ -f requirements.txt ] || { echo "no existe requirements.txt"; exit 1; } \
    && echo "Instalando librerias" \
    && pip install --no-cache-dir -r requirements.txt || { echo "Error al instalar las librerias"; exit 1; } \
    && echo "Librerias instaladas exitosamente" 

COPY app/ ./app
COPY entrypoint.sh .

RUN set -eux \
    && echo "Validando existensia de archivo entrypoint.sh" \
    && [ -f entrypoint.sh ] || { echo "no existe entrypoint.sh"; exit 1; } \
    && echo "El archivo entrypoint.sh existe"

ENV PYTHONUNBUFFERED=1 \
    FLASK_APP=app:create_app \
    FLASK_ENV=production

# Instalar dependencias del SO
# Dar permiso de ejecución al entrypoint - chmod +x entrypoint.sh
RUN set -eux \
    && apt-get -qq update \
    && apt-get -yqq --no-install-recommends install netcat-openbsd gcc \
    && rm -rf /var/lib/apt/lists/* || { echo "Error al realizar limpieza de cache de apt"; exit 1; } \
    && chmod +x entrypoint.sh || { echo "Error al asignar permisos"; exit 1; }

# Punto de entrada
ENTRYPOINT ["./entrypoint.sh"]
