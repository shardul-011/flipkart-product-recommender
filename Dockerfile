## Parent image
FROM python:3.11-slim

## Essential environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

## Work directory inside the docker container
WORKDIR /app

## Installing system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

## Copy only requirements first (layer caching)
COPY requirements.txt .

## Install Python dependencies (Flask included)
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

## Copy rest of the app
COPY . .

## Install your project (editable)
RUN pip install --no-cache-dir -e .

## Used PORTS
EXPOSE 5000

## Run the app
CMD ["python", "app.py"]
