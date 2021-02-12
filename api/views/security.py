from flask_restful import Resource
from flask_httpauth import HTTPBasicAuth
from flask import g
from api.models.user import UserModel
from api.schema.user import UserSchema


auth = HTTPBasicAuth()

user_schema = UserSchema()


@auth.verify_password
def verify_user_password(name, password):
    user = UserModel.query.filter_by(name=name).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True


class AuthRequiredResource(Resource):
    method_decorators = [auth.login_required]