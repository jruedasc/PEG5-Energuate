# app/models/user.py
from datetime import datetime
from zoneinfo import ZoneInfo
from app import db
from sqlalchemy import Text, LargeBinary
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = "users"

    id              = db.Column(db.Integer, primary_key=True)
    cod_usuario     = db.Column(db.String(64), unique=True, nullable=False)
    nombre_completo = db.Column(db.String(128), nullable=False)
    apellido        = db.Column(db.String(128), nullable=False)
    correo          = db.Column(db.String(120), unique=True, nullable=False)
    pais            = db.Column(db.String(2), nullable=False, default='GT')
    telefono        = db.Column(db.String(20))
    pais_2          = db.Column(db.String(2))  
    telefono_2      = db.Column(db.String(20))  
    avatar          = db.Column(LargeBinary)
    estado          = db.Column(db.String(20), nullable=False, default="Activo")
    rol             = db.Column(db.String(64), nullable=False, default="Usuario")
    empresa         = db.Column(db.String(128))
    password_hash   = db.Column(Text, nullable=False)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


