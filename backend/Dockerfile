# Usa una imagen oficial de Python delgada como base
FROM python:3.12-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Establece variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instala las dependencias del sistema operativo si fueran necesarias (en este caso no)
# RUN apt-get update && apt-get install -y ...

# Copia primero el archivo de requerimientos para aprovechar el caché de Docker
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación
COPY . .

# Expone el puerto en el que Uvicorn se ejecutará
EXPOSE 8000

# El comando para iniciar la aplicación cuando el contenedor arranque
# Usamos 0.0.0.0 para que sea accesible desde fuera del contenedor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]