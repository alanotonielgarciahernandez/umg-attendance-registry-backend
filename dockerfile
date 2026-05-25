FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Instalar dependencias del sistema y ODBC Driver 17 para SQL Server.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        gnupg \
        unixodbc \
        unixodbc-dev \
    && curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/microsoft-prod.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql17 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar código de la aplicación.
COPY . .

# Crear directorio para archivos estáticos.
RUN mkdir -p /app/media

# Crear directorio para certificados SSL.
RUN mkdir -p /app/secrets

# Instalar dependencias de Python.
RUN pip install --upgrade pip && python -m pip install --no-cache-dir -r requirements.txt

# Hacer el script de entrada ejecutable.
RUN chmod +x /app/entrypoint.sh

# Puerto expuesto para el servidor de desarrollo o producción.
EXPOSE 80

# Usar el script de entrada para iniciar el servidor.
ENTRYPOINT [ "/app/entrypoint.sh" ]