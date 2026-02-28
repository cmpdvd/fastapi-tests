#!/bin/bash
echo "Running Alembic migrations..."
python -m alembic upgrade head

# Display the environment variables for debug
echo "📊 Variables of the database:"
env | grep -i -E "(database|postgres|pg|db)" | head -10


echo "Starting web server..."
# python -m uvicorn app.fastApi.main:app --host 0.0.0.0 --port 8000
python -m uvicorn app.fastApi.main:app --host 0.0.0.0 --port ${PORT:-8000}



# # Run the migrations
# echo "🔄 Running migrations..."
# python run_migrations.py

# # Start the web server
# echo "🌐 Starting the web server..."
# exec uvicorn main:app --host 0.0.0.0 --port $PORT

