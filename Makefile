# Configuration dynamique
include Makefile.ng
wor = africa
contry = morocco

OSRM_DIR = ${CURDIR}/maps
OSRM_PREFIX = $(contry)-latest.osrm
start:
	wget -qO maps wget https://download.geofabrik.de/$(wor)/$(contry)-latest.osm.pbf && docker run -t -v "${OSRM_DIR}:/data" ghcr.io/project-osrm/osrm-backend osrm-extract -p /opt/car.lua /data/$(conty)-latest.osm.pbf || echo "osrm-extract failed" && docker run -t -v "${OSRM_DIR}:/data" ghcr.io/project-osrm/osrm-backend osrm-partition /data/$(OSRM_PREFIX) || echo "osrm-partition failed" && docker run -t -v "${OSRM_DIR}:/data" ghcr.io/project-osrm/osrm-backend osrm-customize /data/$(OSRM_PREFIX) || echo "osrm-customize failed" && chmod +x start.sh
serve:
	docker run -p 5000:5000 -v "${OSRM_DIR}:/data" ghcr.io/project-osrm/osrm-backend osrm-routed --algorithm mld /data/$(OSRM_PREFIX)
st:
	./start.sh --no-inhibit