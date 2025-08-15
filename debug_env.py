import os

print("=== DEBUG DES VARIABLES D'ENVIRONNEMENT ===")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
print(f"PORT: {os.getenv('PORT')}")

print("\n=== TOUTES LES VARIABLES CONTENANT 'DATABASE' OU 'DB' ===")
for key, value in sorted(os.environ.items()):
    if 'DATABASE' in key.upper() or 'DB' in key.upper() or 'POSTGRES' in key.upper():
        print(f"{key}: {value}")

print("\n=== QUELQUES AUTRES VARIABLES ===")
for key in ['RAILWAY_ENVIRONMENT', 'RAILWAY_PROJECT_ID', 'RAILWAY_SERVICE_ID']:
    value = os.getenv(key)
    if value:
        print(f"{key}: {value}")