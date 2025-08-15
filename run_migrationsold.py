import os
import subprocess

print("=== DEBUG DES VARIABLES D'ENVIRONNEMENT ===")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
print(f"PORT: {os.getenv('PORT')}")

# print("\n=== TOUTES LES VARIABLES CONTENANT 'DATABASE' OU 'DB' ===")
# for key, value in sorted(os.environ.items()):
#     if 'DATABASE' in key.upper() or 'DB' in key.upper() or 'POSTGRES' in key.upper():
#         print(f"{key}: {value}")

# print("\n=== QUELQUES AUTRES VARIABLES ===")
# for key in ['RAILWAY_ENVIRONMENT', 'RAILWAY_PROJECT_ID', 'RAILWAY_SERVICE_ID']:
#     value = os.getenv(key)
#     if value:
#         print(f"{key}: {value}")
        
print("=== DEBUG DES VARIABLES D'ENVIRONNEMENT ===")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
print(f"PORT: {os.getenv('PORT')}")

print("\n=== TOUTES LES VARIABLES RAILWAY ===")
railway_vars = {k: v for k, v in os.environ.items() if 'RAILWAY' in k.upper()}
for key, value in sorted(railway_vars.items()):
    print(f"{key}: {value}")

print("\n=== TOUTES LES VARIABLES CONTENANT 'DATABASE', 'DB', 'POSTGRES' ===")
for key, value in sorted(os.environ.items()):
    if any(keyword in key.upper() for keyword in ['DATABASE', 'DB', 'POSTGRES', 'USER', 'RAILWAY']):
        print(f"{key}: {value}")

print("\n=== TOUTES LES VARIABLES D'ENVIRONNEMENT (PREVIEW) ===")
all_vars = list(os.environ.keys())
print(f"Total: {len(all_vars)} variables")
for key in sorted(all_vars)[:20]:  # Afficher les 20 premières
    value = os.environ[key]
    # Masquer les valeurs sensibles
    if any(sensitive in key.upper() for sensitive in ['PASSWORD', 'SECRET', 'KEY', 'TOKEN']):
        print(f"{key}: ***HIDDEN***")
    else:
        print(f"{key}: {value}")

if len(all_vars) > 20:
    print(f"... et {len(all_vars) - 20} autres variables")

print("\n=== RECHERCHE DE VARIABLES POSTGRES ===")
postgres_vars = {k: v for k, v in os.environ.items() if any(term in k.upper() for term in ['POSTGRES', 'PGUSER', 'PGHOST', 'PGPORT', 'PGDATABASE'])}
if postgres_vars:
    for key, value in sorted(postgres_vars.items()):
        print(f"{key}: {value}")
else:
    print("Aucune variable PostgreSQL trouvée")



print("Running Alembic migrations in run_migration.py...")
subprocess.run(["alembic", "upgrade", "head"], check=True)
