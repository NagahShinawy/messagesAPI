from marshmallow import fields
from marshmallow import validate
from extensions import ma


class CategorySchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(3))
    url = ma.URLFor("api.categoryresource", id="<id>", _external=True)
    messages = fields.Nested("MessageSchema", many=True, exclude=("category",))
