# Dockerfile (corregido)
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del SO
RUN apt-get update \
 && apt-get install -y --no-install-recommends netcat-openbsd gcc \
 && rm -rf /var/lib/apt/lists/*

# Copiar y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código de la aplicación
COPY . .

# Dar permiso de ejecución al entrypoint
RUN chmod +x entrypoint.sh

# Punto de entrada
ENTRYPOINT ["./entrypoint.sh"]
