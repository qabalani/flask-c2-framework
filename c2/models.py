from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(64), unique=True, nullable=False)
    hostname = db.Column(db.String(128))
    username = db.Column(db.String(128))
    os_info = db.Column(db.String(256))
    ip_address = db.Column(db.String(64))
    aes_key = db.Column(db.String(128))
    sleep = db.Column(db.Integer, default=5)
    jitter = db.Column(db.Float, default=0.2)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    alive = db.Column(db.Boolean, default=True)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agent_uid = db.Column(db.String(64), db.ForeignKey("agent.uid"))
    command = db.Column(db.Text, nullable=False)
    output = db.Column(db.Text)
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    status = db.Column(db.String(16), default="pending")
