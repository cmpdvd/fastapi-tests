import os
import subprocess
import re

def debug_environment():
    """Debug complet de l'environnement Railway"""
    
    print("=" * 60)
    print("🔍 DEBUG COMPLET DES VARIABLES D'ENVIRONNEMENT")
    print("=" * 60)
    
    # 1. Variables Railway spécifiques
    print("\n🚂 VARIABLES RAILWAY SYSTÈME:")
    railway_vars = {k: v for k, v in os.environ.items() if k.startswith('RAILWAY')}
    for key, value in sorted(railway_vars.items()):
        print(f"  {key}: {value}")
    
    # 2. Variables PostgreSQL potentielles
    print("\n🐘 VARIABLES POSTGRESQL POTENTIELLES:")
    pg_patterns = ['PG', 'POSTGRES', 'DATABASE', 'DB']
    pg_vars = {}
    for key, value in os.environ.items():
        if any(pattern in key.upper() for pattern in pg_patterns):
            pg_vars[key] = value
    
    if pg_vars:
        for key, value in sorted(pg_vars.items()):
            # Masquer les mots de passe
            if 'PASSWORD' in key.upper() or 'PASS' in key.upper():
                print(f"  {key}: ***MASKED***")
            else:
                print(f"  {key}: {value}")
    else:
        print("  ❌ Aucune variable PostgreSQL trouvée")
    
    # 3. Recherche de patterns d'URL
    print("\n🔗 RECHERCHE D'URLs DE BASE DE DONNÉES:")
    url_patterns = ['URL', 'URI', 'CONNECTION']
    for key, value in os.environ.items():
        if any(pattern in key.upper() for pattern in url_patterns):
            if 'postgres' in value.lower() or 'postgresql' in value.lower():
                print(f"  {key}: {value[:50]}...") # Afficher seulement le début
    
    # 4. Variables contenant "localhost", "127.0.0.1", ou des domaines railway
    print("\n🌐 VARIABLES CONTENANT DES HOSTS:")
    for key, value in os.environ.items():
        if any(host in value.lower() for host in ['localhost', '127.0.0.', 'railway.app', '.railway.internal']):
            print(f"  {key}: {value}")
    
    # 5. Toutes les variables (limitées pour éviter le spam)
    print(f"\n📊 RÉSUMÉ: {len(os.environ)} variables d'environnement au total")
    
    # 6. Variables suspectes qui pourraient être les bonnes
    print("\n🎯 VARIABLES CANDIDATES POUR DATABASE_URL:")
    candidates = []
    for key, value in os.environ.items():
        # Chercher des variables qui ressemblent à des URLs de BDD
        if ('postgres' in value.lower() or 'postgresql' in value.lower()) and '://' in value:
            candidates.append((key, value))
        # Ou des variables avec des noms suspects
        elif any(name in key.upper() for name in ['URL', 'CONNECTION', 'CONNECT']) and any(db in key.upper() for db in ['DB', 'DATABASE', 'POSTGRES']):
            candidates.append((key, value))
    
    for key, value in candidates:
        print(f"  🔍 {key}: {value[:70]}...")
    
    if not candidates:
        print("  ❌ Aucune URL de base de données candidate trouvée")
    
    # 7. Tentative de construction d'URL
    print("\n🔧 TENTATIVE DE CONSTRUCTION D'URL:")
    try:
        host = None
        port = None
        user = None
        password = None
        database = None
        
        # Chercher les composants individuels
        for key, value in os.environ.items():
            key_upper = key.upper()
            if 'HOST' in key_upper and any(pg in key_upper for pg in ['PG', 'POSTGRES', 'DB']):
                host = value
                print(f"  Host trouvé: {key} = {value}")
            elif 'PORT' in key_upper and any(pg in key_upper for pg in ['PG', 'POSTGRES', 'DB']):
                port = value
                print(f"  Port trouvé: {key} = {value}")
            elif 'USER' in key_upper and any(pg in key_upper for pg in ['PG', 'POSTGRES', 'DB']):
                user = value
                print(f"  User trouvé: {key} = {value}")
            elif 'PASSWORD' in key_upper and any(pg in key_upper for pg in ['PG', 'POSTGRES', 'DB']):
                password = "***FOUND***"
                print(f"  Password trouvé: {key} = ***MASKED***")
            elif any(name in key_upper for name in ['DATABASE', 'DBNAME', 'DB']) and key_upper not in ['DATABASE_URL']:
                database = value
                print(f"  Database trouvée: {key} = {value}")
        
        if host and user and password != "***FOUND***":  # Si on n'a pas trouvé le mot de passe
            print("  ⚠️ Composants insuffisants pour construire l'URL")
        elif host and user:
            port = port or "5432"
            database = database or user  # Souvent le nom de la DB = nom d'utilisateur
            print(f"  ✅ Composants suffisants trouvés!")
            print(f"     Host: {host}, Port: {port}, User: {user}, DB: {database}")
            
    except Exception as e:
        print(f"  ❌ Erreur lors de la construction: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    debug_environment()

# print("Running Alembic migrations in run_migration.py...")
# subprocess.run(["alembic", "upgrade", "head"], check=True)
