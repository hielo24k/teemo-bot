# Imagen oficial de Python optimizada
FROM python:3.11-slim

# Directorio de trabajo en el contenedor
WORKDIR /app

# Desactivar buffer de salida para que los logs aparezcan inmediatamente en consola
ENV PYTHONUNBUFFERED=1

# Instalar dependencias primero para aprovechar la caché de capas de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código del bot
COPY . .

# Comando de inicio del bot
CMD ["python", "bot.py"]
