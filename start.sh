#!/bin/bash

# Display the environment variables for debug
echo "📊 Variables of the database:"
env | grep -i -E "(database|postgres|pg|db)" | head -10

# Run the migrations
echo "🔄 Running migrations..."
python run_migrations.py

# Start the web server
echo "🌐 Starting the web server..."
exec uvicorn main:app --host 0.0.0.0 --port $PORT

