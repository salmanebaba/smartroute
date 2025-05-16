#!/bin/sh

REGION="morocco"
DATA_DIR="/data"
OSM_PBF="${DATA_DIR}/${REGION}-latest.osm.pbf"
OSRM_FILE="${DATA_DIR}/${REGION}-latest.osrm"

# Téléchargement (seulement si absent)
if [ ! -f "${OSM_PBF}" ]; then
    echo "Téléchargement des données OSM..."
    curl -L -o "${OSM_PBF}" "https://download.geofabrik.de/africa/${REGION}-latest.osm.pbf"
    echo "Début de l'extraction..."
    osrm-extract -p /opt/car.lua "${OSM_PBF}"
    osrm-partition "${OSRM_FILE}"
    osrm-customize "${OSRM_FILE}"
    echo "Traitement OSRM terminé."
else
    echo "Fichiers OSRM déjà présents. Ignorer le traitement."
fi

# Démarrer OSRM
exec osrm-routed --algorithm mld "${OSRM_FILE}"