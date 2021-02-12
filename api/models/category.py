from api.extensions import db
from api.models.generic import AddUpdateDelete
from sqlalchemy import func


class CategoryModel(db.Model, AddUpdateDelete):

    __tablename__ = "category"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name

    @classmethod
    def is_unique(cls, name):
        # case-insensitive-flask-sqlalchemy-query
        existing_category = cls.query.filter_by(name=func.lower(name)).first()
        if existing_category is None:
            return True
        return False
