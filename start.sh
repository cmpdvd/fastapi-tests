#!/bin/bash

echo "🚀 Démarrage de l'application..."

# Afficher les variables d'environnement pour debug
echo "📊 Variables de base de données disponibles:"
env | grep -i -E "(database|postgres|pg|db)" | head -10

# Exécuter les migrations
echo "🔄 Exécution des migrations..."
python run_migrations.py

# Démarrer l'application
echo "🌐 Démarrage du serveur web..."
exec uvicorn main:app --host 0.0.0.0 --port $PORT

