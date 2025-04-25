# Configuration dynamique
include Makefile.ng
conty = morocco

OSRM_DIR = ${CURDIR}/maps
OSRM_PREFIX = $(conty)-latest.osrm
start:
	docker run -t -v "${OSRM_DIR}:/data" ghcr.io/project-osrm/osrm-backend osrm-extract -p /opt/car.lua /data/$(conty)-latest.osm.pbf || echo "osrm-extract failed" && docker run -t -v "${OSRM_DIR}:/data" ghcr.io/project-osrm/osrm-backend osrm-partition /data/$(OSRM_PREFIX) || echo "osrm-partition failed" && docker run -t -v "${OSRM_DIR}:/data" ghcr.io/project-osrm/osrm-backend osrm-customize /data/$(OSRM_PREFIX) || echo "osrm-customize failed" && chmod +x start.sh
serve:
	docker run -p 5000:5000 -v "${OSRM_DIR}:/data" ghcr.io/project-osrm/osrm-backend osrm-routed --algorithm mld /data/$(OSRM_PREFIX)
