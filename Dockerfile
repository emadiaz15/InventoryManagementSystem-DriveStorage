# 🐍 Imagen base ligera de Python 3.10
FROM python:3.10-slim

# 📂 Establecer el directorio de trabajo
WORKDIR /app

# 📦 Instalar dependencias del sistema necesarias para Google API Client
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# 📜 Copiar solo el archivo de requerimientos primero
COPY requirements.txt .

# ✅ Instalar las dependencias
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 🔥 Copiar el resto de la aplicación
COPY . .

# 📌 Variables de entorno por defecto
ENV PYTHONUNBUFFERED=1
ENV PORT=8001

# 🌍 Exponer el puerto (default 8001, Railway lo sobreescribe si quiere)
EXPOSE ${PORT}

# ⚡ Comando de arranque flexible (por defecto uvicorn sin --reload)
CMD ["uvicorn", "app.drive.main:app", "--host", "0.0.0.0", "--port", "8001"]
