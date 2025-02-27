# ==============================================
# MAIN STAGE
# ==============================================
FROM python:3.12-alpine

# Install only required dependencies and Ensure setuptools is installed before installing dependencies
RUN apk add --no-cache sqlite-dev figlet py3-setuptools gcc musl-dev python3-dev libffi-dev su-exec && pip install --no-cache-dir --upgrade pip setuptools wheel 

# Create a non-root user & group for security
RUN addgroup -S osm && adduser -S osm -G osm

# Set working directory
WORKDIR /app

# Copy application files
COPY osm.py requirements.txt entrypoint.sh ./ 

# Create a directory for the SQLite database
RUN mkdir -p /data && chown -R osm:osm /data

# Set the correct permissions for the /app directory & Install Python dependencies securely
RUN  chown -R osm:osm /app && chmod -R 775 /app && pip install --no-cache-dir -r requirements.txt && rm -rf /root/.cache/pip

# Ensure the entrypoint script is executable
RUN chmod +x /app/entrypoint.sh

# Switch to non-root user
USER osm

# # Define entrypoint
# ENTRYPOINT ["/app/entrypoint.sh"]

# Run the application
CMD ["python", "osm.py"]
