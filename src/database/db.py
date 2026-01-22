import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

server = os.getenv("SQL_SERVER")
database = os.getenv("SQL_DATABASE")
username = os.getenv("SQL_USERNAME")
password = os.getenv("SQL_PASSWORD")

DATABASE_URL = (
    f"mssql+pyodbc://{username}:{password}@{server}:1433/"
    f"{database}?driver=ODBC+Driver+18+for+SQL+Server"
    f"&Encrypt=yes&TrustServerCertificate=no&Connection+Timeout=30"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # Vérifie la connexion avant utilisation
    pool_timeout=30,         # Timeout pour obtenir une connexion du pool
    pool_recycle=300,        # Recycle les connexions après 5 minutes
    pool_size=5,             # Taille du pool
    max_overflow=10,         # Connexions supplémentaires autorisées
    connect_args={
        "timeout": 30        # Timeout de connexion ODBC
    }
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Cette fonction sera utilisée comme dépendance dans les routes FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()