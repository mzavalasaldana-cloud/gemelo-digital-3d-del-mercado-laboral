# Imagen base oficial de Python fijada
FROM python:3.12.9-slim

# Evitar escritura de bytecode y habilitar buffer sin retraso
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar herramientas del sistema necesarias (make)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    make \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python fijadas
COPY requirements-itdt.txt .
RUN pip install --no-cache-dir -r requirements-itdt.txt

# Copiar el código del modelo, datos oficiales, tests y Makefile
COPY itdt/ ./itdt/
COPY data/ ./data/
COPY tests/ ./tests/
COPY Makefile .
COPY LICENSE .

# Directorio de salidas
RUN mkdir -p outputs

# Por defecto ejecuta make smoke (< 1 minuto)
CMD ["make", "smoke"]
