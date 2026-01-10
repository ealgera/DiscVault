#!/bin/bash

# Configuratie
VERSION="1.0.0"
APP_NAME="discvault"

# Optioneel: Zet hier je Docker Hub gebruikersnaam als je wilt pushen (bijv. "jansen")
# Laat leeg voor lokaal gebruik
REGISTRY=""

# Helper functie voor image naam
get_image_name() {
    if [ -z "$REGISTRY" ]; then
        echo "$APP_NAME-$1:$VERSION"
    else
        echo "$REGISTRY/$APP_NAME-$1:$VERSION"
    fi
}

BACKEND_IMAGE=$(get_image_name "backend")
FRONTEND_IMAGE=$(get_image_name "frontend")

echo "========================================"
echo "Start build voor versie $VERSION"
echo "========================================"

# 1. Backend Bouwen
echo "🔨 Bouwen Backend ($BACKEND_IMAGE)..."
docker build -t "$BACKEND_IMAGE" ./backend

# 2. Frontend Bouwen
echo "🔨 Bouwen Frontend ($FRONTEND_IMAGE)..."
docker build -t "$FRONTEND_IMAGE" ./frontend

echo "========================================"
echo "✅ Klaar!"
echo "Backend image:  $BACKEND_IMAGE"
echo "Frontend image: $FRONTEND_IMAGE"
echo "========================================"

if [ -z "$REGISTRY" ]; then
    echo "Tip: Om deze naar je server te kopiëren als bestand:"
    echo "  docker save $BACKEND_IMAGE | gzip > backend.tar.gz"
    echo "  docker save $FRONTEND_IMAGE | gzip > frontend.tar.gz"
else
    echo "Tip: Om te uploaden naar Docker Hub:"
    echo "  docker push $BACKEND_IMAGE"
    echo "  docker push $FRONTEND_IMAGE"
fi
