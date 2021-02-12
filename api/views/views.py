from flask import Blueprint
from flask_restful import Api
from api.views.message import MessageResource, MessageListResource
from api.views.category import CategoryResource, CategoryListResource

api_bp = Blueprint("api", __name__)


api = Api(api_bp)


api.add_resource(CategoryListResource, "/categories/")
api.add_resource(CategoryResource, "/categories/<int:id>/")
api.add_resource(MessageListResource, "/messages/")
api.add_resource(MessageResource, "/messages/<int:id>")
