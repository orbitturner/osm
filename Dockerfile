# Dockerfile for Orbit Simple Monitor (OSM)

FROM python:3.11-slim

# System dependencies
RUN apt-get update && apt-get install -y \
    libsqlite3-dev figlet \
    # If you want optional packages for debugging, uncomment:
    # vim less 
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Set environment variable to disable buffering
# ENV PYTHONUNBUFFERED=1

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main script
COPY osm.py .

# Run the application
CMD ["python", "osm.py"]
