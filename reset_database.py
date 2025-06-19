# # reset_database.py

# from database.db import engine
# from database.models import Base
# from database.db import engine

# with engine.connect() as conn:
#     # Désactiver temporairement les contraintes de FK
#     conn.execute("EXEC sp_msforeachtable 'ALTER TABLE ? NOCHECK CONSTRAINT all'")
#     print("Suppression des tables...")
#     Base.metadata.drop_all(bind=engine)
#     print("Tables supprimées avec succès.")
#     # Réactiver les contraintes (optionnel mais conseillé)
#     conn.execute("EXEC sp_msforeachtable 'ALTER TABLE ? WITH CHECK CHECK CONSTRAINT all'")

# # Attention : cela supprime toutes les tables de la base de données !
# print("Suppression des tables...")
# Base.metadata.drop_all(engine)

# print("Création des tables...")
# Base.metadata.create_all(engine)

# print(" Base de données réinitialisée avec succès.")
# reset_database.py
# reset_database.py

from database.db import engine
from database.models import Base

# ⚠️ Attention : cela supprime toutes les tables de la base de données !
print("⚠️ Suppression des tables...")
Base.metadata.drop_all(engine)

print("✅ Création des tables...")
Base.metadata.create_all(engine)

print("🎉 Base de données réinitialisée avec succès.")
