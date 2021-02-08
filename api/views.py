from flask import Blueprint, request, jsonify, make_response
from flask_restful import Api, Resource
from models.message import CategoryModel, CategorySchema, MessageModel, MessageSchema
from extensions import db
from sqlalchemy.exc import SQLAlchemyError
from utils.http import status


api_bp = Blueprint("api", __name__)
category_schema = CategorySchema()
message_schema = MessageSchema()
api = Api(api_bp)


class MessageResource(Resource):
    def get(self, _id):
        message = MessageModel.query.get_or_404(_id)
        result = message_schema.dump(message).data
        return result

    def patch(self, _id):
        message = MessageModel.query.get_or_404(_id)
        message_dict = request.get_json(force=True)
        if "message" in message_dict:
            message.message = message_dict["message"]
        if "duration" in message_dict:
            message.duration = message_dict["duration"]
        if "printed_times" in message_dict:
            message.printed_times = message_dict["printed_times"]
        if "printed_once" in message_dict:
            message.printed_once = message_dict["printed_once"]
        dumped_message, dump_errors = message_schema.dump(message)
        if dump_errors:
            return dump_errors, status.HTTP_400_BAD_REQUEST
        validate_errors = message_schema.validate(dumped_message)
        # errors = message_schema.validate(data)
        if validate_errors:
            return validate_errors, status.HTTP_400_BAD_REQUEST
        try:
            message.update()
            return self.get(_id)
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            return resp, status.HTTP_400_BAD_REQUEST

    def delete(self, _id):
        message = MessageModel.query.get_or_404(_id)
        try:
            delete = message.delete(message)
            response = make_response()
            return response, status.HTTP_204_NO_CONTENT
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            return resp, status.HTTP_401_UNAUTHORIZED


class MessageListResource(Resource):
    def get(self):
        messages = MessageModel.query.all()
        result = message_schema.dump(messages, many=True).data
        return result

    def post(self):
        request_dict = request.get_json()
        if not request_dict:
            response = {"message": "No input data provided"}
            return response, status.HTTP_400_BAD_REQUEST
        errors = message_schema.validate(request_dict)
        if errors:
            return errors, status.HTTP_400_BAD_REQUEST
        try:
            category_name = request_dict["category"]["name"]
            category = CategoryModel.query.filter_by(name=category_name).first()
            if category is None:
                # Create a new Category
                category = CategoryModel(name=category_name)
                db.session.add(category)
            # Now that we are sure we have a category
            # create a new Message
            message = MessageModel(
                message=request_dict["message"],
                duration=request_dict["duration"],
                category=category,
            )
            message.add(message)
            query = MessageModel.query.get(message.id)
            result = message_schema.dump(query).data
            return result, status.HTTP_201_CREATED
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            return resp, status.HTTP_400_BAD_REQUEST


class CategoryResource(Resource):
    def get(self, _id):
        category = CategoryModel.query.get_or_404(_id)
        result = category_schema.dump(category).data
        return result

    def patch(self, _id):
        category = CategoryModel.query.get_or_404(_id)
        category_dict = request.get_json()
        if not category_dict:
            resp = {"message": "No input data provided"}
            return resp, status.HTTP_400_BAD_REQUEST
        errors = category_schema.validate(category_dict)
        if errors:
            return errors, status.HTTP_400_BAD_REQUEST
        try:
            if "name" in category_dict:
                category.name = category_dict["name"]
            category.update()
            return self.get(_id)
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            return resp, status.HTTP_400_BAD_REQUEST

    def delete(self, _id):
        category = CategoryModel.query.get_or_404(_id)
        try:
            category.delete(category)
            response = make_response()
            return response, status.HTTP_204_NO_CONTENT
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            return resp, status.HTTP_401_UNAUTHORIZED


class CategoryListResource(Resource):
    def get(self):
        categories = CategoryModel.query.all()
        results = category_schema.dump(categories, many=True)
        return results

    def post(self):
        request_dict = request.get_json()
        if not request_dict:
            resp = {"message": "No input data provided"}
            return resp, status.HTTP_400_BAD_REQUEST
        errors = category_schema.validate(request_dict)
        if errors:
            return errors, status.HTTP_400_BAD_REQUEST
        try:
            category = CategoryModel(request_dict["name"])
            category.add(category)
            query = CategoryModel.query.get(category.id)
            result = category_schema.dump(query)
            return {"data": result}, status.HTTP_201_CREATED
        except SQLAlchemyError as e:
            db.session.rollback()
            # resp = jsonify({"error": str(e)})
            return {"error": str(e)}, status.HTTP_400_BAD_REQUEST


api.add_resource(CategoryListResource, "/categories/")
api.add_resource(CategoryResource, "/categories/<int:id>")
api.add_resource(MessageListResource, "/messages/")
api.add_resource(MessageResource, "/messages/<int:id>")
