from app import db
from sqlalchemy.ext.mutable import MutableDict


class Deposition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meta_data = db.Column(MutableDict.as_mutable(db.JSON), nullable=False, default=lambda: {})
    status = db.Column(db.String(50), nullable=False, default="draft")
    doi = db.Column(db.String(250), unique=True, nullable=True)

    def __repr__(self):
        return f'Deposition<{self.id}>'

    def init(self, doi, meta_data):
        self.doi = doi
        self.meta_data = meta_data
