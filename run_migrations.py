import subprocess

print("Running Alembic migrations in run_migration.py...")
subprocess.run(["alembic", "upgrade", "head"], check=True)
