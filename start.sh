#!/bin/bash

if [[ "$1" != "--no-inhibit" ]]; then
  exec systemd-inhibit --why="Smart Bin server running" --what=sleep "$0" --no-inhibit
fi

cleanup() {
    echo "🛑 Arrêt des processus..."
    kill $API_PID $NGROK_PID 2>/dev/null

    echo "🗑️  Recherche du conteneur Docker sur le port 5000..."
    CONTAINER_ID=$(docker ps --filter "publish=5000" --format "{{.ID}}")
    if [ -n "$CONTAINER_ID" ]; then
        echo "🛑 Arrêt du conteneur Docker : $CONTAINER_ID"
        docker rm -f "$CONTAINER_ID"
    fi

    exit 0
}


# Capturer le signal CTRL+C
trap cleanup SIGINT

# Étape 2 : Lancer OSRM en arrière-plan
echo "🗺️ Démarrage du service OSRM..."
make serve > log/osrm.log 2>&1 &
OSRM_PID=$!
sleep 7
# Étape 3 : Lancer FastAPI
echo "🚀 Démarrage de FastAPI..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > log/api.log 2>&1 &
API_PID=$!

# Étape 4 : Lancer Ngrok
sleep 2
echo "🌐 Démarrage du tunnel Ngrok..."
ngrok start --log=stdout api > log/ngrok.log 2>&1 &
NGROK_PID=$!

# Attendre la configuration Ngrok
sleep 4

# Afficher l'URL
# Étape 3 : Afficher et ouvrir l’URL
URL="https://becoming-oarfish-luckily.ngrok-free.app/"
echo "✅ Ton API est accessible publiquement à :"
echo "$URL"
xdg-open "file://"$(pwd)"/local.html"
# Maintenir le script actif
echo "🔁 Appuyez sur CTRL+C pour tout arrêter"


while true; do sleep 1; done