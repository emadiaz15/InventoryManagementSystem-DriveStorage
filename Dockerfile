# 🐍 Imagen base ligera de Python 3.10
FROM python:3.10-slim

# 📂 Establecer el directorio de trabajo
WORKDIR /app

# 📦 Copiar e instalar dependencias
COPY requirements.txt .

# ✅ Instalar las dependencias con resolución más robusta
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --upgrade -r requirements.txt

# 🔥 Copiar el resto del código del proyecto
COPY . .

# 🌍 Exponer el puerto donde corre FastAPI (por defecto 8001)
EXPOSE 8001

# 🚀 Comando para iniciar la API con Uvicorn
CMD ["uvicorn", "app.drive.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
