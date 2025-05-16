FROM ghcr.io/project-osrm/osrm-backend:v6.0.0

RUN apk update && apk add --no-cache curl

COPY osrm-init.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/osrm-init.sh

ENTRYPOINT ["/usr/local/bin/osrm-init.sh"]