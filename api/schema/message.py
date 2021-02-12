from marshmallow import fields, pre_load, post_load
from marshmallow import validate
from api.extensions import ma
from api.schema.category import CategorySchema


class MessageSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    message = fields.String(required=True, validate=validate.Length(1))
    duration = fields.Integer()
    creation_date = fields.DateTime()
    category = fields.Nested(CategorySchema, only=["id", "url", "name"], required=True)
    printed_times = fields.Integer()
    printed_once = fields.Boolean()
    url = ma.URLFor("api.messageresource", id="<id>", _external=True)

    @pre_load(pass_many=True)
    # @post_load
    def process_category(self, data, many, **kwargs):
        category = data.get("category")
        if category:
            if isinstance(category, dict):
                category_name = category.get("name")
            else:
                category_name = category
            category_dict = dict(name=category_name)
        else:
            category_dict = {}
        data["category"] = category_dict
        return data
