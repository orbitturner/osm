# ==============================================
# MAIN STAGE
# ==============================================
# Use a minimal Python base image
FROM python:3.12-alpine

# Install only required dependencies and Ensure setuptools is installed before installing dependencies
RUN apk add --no-cache sqlite-dev figlet py3-setuptools gcc musl-dev python3-dev libffi-dev && pip install --no-cache-dir --upgrade pip setuptools wheel 

# Create a non-root user & group for security
RUN addgroup -S osm && adduser -S osm -G osm

# Set working directory
WORKDIR /app

# Copy application files
COPY osm.py requirements.txt ./ 

# Set the correct permissions for the /app directory & Install Python dependencies securely
RUN  chown -R osm:osm /app && chmod -R 775 /app && pip install --no-cache-dir -r requirements.txt && rm -rf /root/.cache/pip

# Switch to non-root user
USER osm

# Run the application
CMD ["python", "osm.py"]

