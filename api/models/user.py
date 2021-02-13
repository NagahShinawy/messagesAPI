from api.extensions import db
from api.models.generic import AddUpdateDelete
from passlib.apps import custom_app_context as password_context
import re
from sqlalchemy import func


class UserModel(db.Model, AddUpdateDelete):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    # I save the hashed password
    password = db.Column(db.String(120), nullable=False)
    creation_date = db.Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False
    )

    def verify_password(self, password):
        return password_context.verify(password, self.password)

    def check_password_strength_and_hash_if_ok(self, password):
        if len(password) < 8:
            return "The password is too short", False
        if len(password) > 32:
            return "The password is too long", False
        if re.search(r"[A-Z]", password) is None:
            return "The password must include at least one uppercase letter", False
        if re.search(r"[a-z]", password) is None:
            return "The password must include at least one lowercase letter", False
        if re.search(r"\d", password) is None:
            return "The password must include at least one number", False
        if re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~" + r'"]', password) is None:
            return "The password must include at least one symbol", False
        self.password = password_context.encrypt(password)
        return "", True

    def __init__(self, name):
        self.name = name

    @classmethod
    def is_unique(cls, id, name):
        # test unique in POST/PATCH
        existing_user = cls.query.filter_by(
            name=func.lower(name)
        ).first()  # case-insensitive-flask-sqlalchemy-query
        if existing_user is None:
            return True
        else:
            if existing_user.id == id:
                return True
            else:
                return False
