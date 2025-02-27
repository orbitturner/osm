#!/bin/sh

echo "🔧 Checking permissions for /data..."

# Vérifier si /data est monté
if [ -d "/data" ]; then
    echo "📁 Found /data, adjusting user permissions..."
    
    # Récupérer l'UID/GID du dossier monté
    HOST_UID=$(stat -c "%u" /data)
    HOST_GID=$(stat -c "%g" /data)
    
    echo "👤 Host UID: $HOST_UID, GID: $HOST_GID"

    # Si le dossier appartient à root, ne pas modifier osm
    if [ "$HOST_UID" -ne 0 ]; then
        echo "🔄 Updating osm user to match host UID/GID..."
        usermod -u "$HOST_UID" osm && groupmod -g "$HOST_GID" osm
    else
        echo "⚠️ Warning: /data is owned by root, keeping default osm user"
    fi

    # Vérifier si les permissions sont correctes
    chown -R osm:osm /data || echo "⚠️ Warning: Failed to change ownership of /data"
    chmod -R 775 /data || echo "⚠️ Warning: Failed to set permissions on /data"
else
    echo "⚠️ Warning: /data volume not found, proceeding anyway..."
fi

echo "🚀 Starting Orbit Simple Monitor as user osm..."
exec "$@"
