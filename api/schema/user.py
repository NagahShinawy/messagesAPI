from marshmallow import fields
from marshmallow import validate
from api.extensions import ma


class UserSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(
        required=True, validate=validate.Length(3)
    )  # min length of name is 3
    url = ma.URLFor("api.userresource", id="<id>", _external=True)
    password = fields.String(
        required=True, validate=validate.Length(8)
    )  # min length of name is 8
