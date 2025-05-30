from datetime import datetime
from app import db
from app.models.user import User

class Letter(db.Model):
    __tablename__ = "letters"

    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user         = db.relationship('User', backref=db.backref('letters', lazy='dynamic'))
    filename     = db.Column(db.String(128), nullable=False)
    file_data    = db.Column(db.LargeBinary, nullable=False)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
