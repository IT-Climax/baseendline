from ..core import db
from sqlalchemy import func, Enum


class Section(db.Model):
    __tablename__ = 'sections'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp())

    def serialize(self):
        """Convert object to JSON-serializable format"""
        return {
            'id': self.id,
            'name': self.title
        }

# class Section(db.Model):
#     __tablename__ = 'sections'
#
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(255), nullable=False)
#     created_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp())

