# app/models/pdf.py
from datetime import datetime
from app import db

class Pdf(db.Model):
    __tablename__ = "pdfs"

    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(256), nullable=False)
    filename    = db.Column(db.String(256), nullable=False)
    file_data   = db.Column(db.LargeBinary, nullable=False)
    section_id  = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    section     = db.relationship('Section', back_populates='pdfs')
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Pdf {self.id} {self.title}>"
