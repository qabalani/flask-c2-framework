import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-prod")
    SQLALCHEMY_DATABASE_URI = "sqlite:///c2.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    OPERATOR_USER = os.environ.get("C2_USER", "operator")
    OPERATOR_PASS = os.environ.get("C2_PASS", "changeme")

    DEFAULT_SLEEP = 5
    DEFAULT_JITTER = 0.2
