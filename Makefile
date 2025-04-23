# Configuration dynamique

conty = morocco

OSRM_DIR = ${CURDIR}/maps
OSRM_PREFIX = $(conty)-latest.osrm
start:
	docker run -t -v "${OSRM_DIR}:/data" ghcr.io/project-osrm/osrm-backend osrm-extract -p /opt/car.lua /data/$(conty)-latest.osm.pbf || echo "osrm-extract failed" && docker run -t -v "${OSRM_DIR}:/data" ghcr.io/project-osrm/osrm-backend osrm-partition /data/$(OSRM_PREFIX) || echo "osrm-partition failed" && docker run -t -v "${OSRM_DIR}:/data" ghcr.io/project-osrm/osrm-backend osrm-customize /data/$(OSRM_PREFIX) || echo "osrm-customize failed" $$ ngrok config add-authtoken 2w41vM8bZSyWuK6GR64AyLdG9dK_3Bqf4xSPApqpWSWwgYdAY


serve:
	docker run -p 5000:5000 -v "${OSRM_DIR}:/data" ghcr.io/project-osrm/osrm-backend osrm-routed --algorithm mld /data/$(OSRM_PREFIX)

git:
	git add .
	git commit -m "update"
	git push origin master
	@echo "Mise à jour de la branche principale sur GitHub."
