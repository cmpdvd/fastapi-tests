import os
import subprocess

print("Running Alembic migrations...")
subprocess.run(["alembic", "upgrade", "head"], check=True)
