# app/models/section.py
from datetime import datetime
from app import db

class Section(db.Model):
    __tablename__ = "sections"

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(128), nullable=False)       
    order       = db.Column(db.Integer, default=0)                
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    pdfs        = db.relationship('Pdf', back_populates='section', lazy='dynamic')
