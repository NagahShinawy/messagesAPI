from api.extensions import db
from api.models.generic import AddUpdateDelete


class CategoryModel(db.Model, AddUpdateDelete):

    __tablename__ = "category"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name