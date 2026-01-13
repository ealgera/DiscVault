#!/bin/bash

# Configuratie
VERSION="1.5.0"
APP_NAME="discvault"
REGISTRY="ealgera"

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

# 1. Backend Bouwen (Context: root)
echo "🔨 Bouwen Backend ($BACKEND_IMAGE)..."
sudo docker build -f Dockerfile.backend -t "$BACKEND_IMAGE" .

# 2. Frontend Bouwen (Context: root)
echo "🔨 Bouwen Frontend ($FRONTEND_IMAGE)..."
sudo docker build -f Dockerfile.frontend -t "$FRONTEND_IMAGE" .

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
