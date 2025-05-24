# Configuration for database and JWT
class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///neofi.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "super-secret-key"