# ==============================================
# MAIN STAGE
# ==============================================
FROM python:3.12-alpine

# Install only required dependencies and Ensure setuptools is installed before installing dependencies
RUN apk add --no-cache sqlite-dev figlet py3-setuptools gcc meson musl-dev python3-dev libffi-dev su-exec && pip install --no-cache-dir --upgrade pip setuptools wheel 

# Create a non-root user & group for security
RUN addgroup -S osm && adduser -S osm -G osm
 

COPY context/profile   /home/osm/.profile
ENV  ENV=/home/osm/.profile

COPY osm.py    /usr/local/bin/osm  
COPY config/osmconf.cfg   /etc/osm/osmconf.cfg

# Set working directory
WORKDIR /app

# Copy application files
COPY meson.build requirements.txt entrypoint.sh   ./ 
COPY src ./src 

# Create a directory for the SQLite database
RUN mkdir -p /data && chown -R osm:osm /data 

# BUILDING
#---------
# Compile C sources files 
RUN  meson setup build  && meson compile -C build 
# Install  bin 
RUN  meson install -C build  

# Set the correct permissions for the /app directory & Install Python dependencies securely
RUN  chown -R osm:osm ./ && chmod -R 775 ./ && pip install --no-cache-dir -r requirements.txt && rm -rf /root/.cache/pip

RUN chown -R osm:osm /etc/osm
# SET X MODE 
#---------- 
# Ensure the entrypoint script is executable
RUN chmod +x ./entrypoint.sh
RUN chmod +x  /usr/local/bin/osm

# Switch to non-root user
USER osm  

# # Define entrypoint
# ENTRYPOINT ["/app/entrypoint.sh"]

# Run the Osm  manager that handle the osm application
CMD ["osmon"]
