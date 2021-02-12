from flask import request, jsonify, make_response
from flask_restful import Resource
from api.models.message import MessageModel
from api.models.category import CategoryModel
from api.schema.message import MessageSchema
from api.extensions import db
from sqlalchemy.exc import SQLAlchemyError
from api.utils.http import status
from utils.helpers.pagination import PaginationHelper


class MessageResource(Resource):

    schema_class = MessageSchema

    def get(self, id):
        message = MessageModel.query.get_or_404(id)
        message_schema = self.schema_class()
        result = message_schema.dump(message)
        return result

    def patch(self, id):
        message = MessageModel.query.get_or_404(id)
        message_dict = request.get_json(force=False)
        if not MessageModel.is_unique(id=id, message=message_dict.get("message")):
            return {
                "error": "A message with the same name already exists"
            }, status.HTTP_400_BAD_REQUEST
        if message_dict is not None:
            if "message" in message_dict:
                message.message = message_dict["message"]
            if "duration" in message_dict:
                message.duration = message_dict["duration"]
            if "printed_times" in message_dict:
                message.printed_times = message_dict["printed_times"]
            if "printed_once" in message_dict:
                message.printed_once = message_dict["printed_once"]
        # dumped_message, dump_errors = message_schema.dump(message)
        # if dump_errors:
        #     return dump_errors, status.HTTP_400_BAD_REQUEST
        message_schema = self.schema_class()
        data = message_schema.dump(message)
        # validate_errors = message_schema.validate(data)
        # # errors = message_schema.validate(data)
        # if validate_errors:
        #     return validate_errors, status.HTTP_400_BAD_REQUEST
        try:
            message.update()
            # return self.get(id)
            return data
        except SQLAlchemyError as e:
            db.session.rollback()
            # resp = jsonify({"error": str(e)})
            return {"error": str(e)}, status.HTTP_400_BAD_REQUEST

    def delete(self, id):
        message = MessageModel.query.get_or_404(id)
        try:
            delete = message.delete(message)
            response = make_response()
            return "", status.HTTP_204_NO_CONTENT
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            return {"error": str(e)}, status.HTTP_400_BAD_REQUEST
            # return resp, status.HTTP_401_UNAUTHORIZED


class MessageListResource(Resource):
    message_schema = MessageSchema

    # def get(self):
    #     messages = MessageModel.query.all()
    #     message_schema = self.schema_class()
    #     result = message_schema.dump(messages, many=True)
    #     return result
    #
    def get(self):
        pagination_helper = PaginationHelper(
            request,
            query=MessageModel.query,
            resource_for_url='api.messagelistresource',
            key_name='results',
            schema=self.message_schema())
        result = pagination_helper.paginate_query()
        return result

    def post(self):
        request_dict = request.get_json()
        if not request_dict:
            response = {"message": "No input data provided"}
            return response, status.HTTP_400_BAD_REQUEST
        message_schema = self.schema_class()
        errors = message_schema.validate(request_dict)
        if errors:
            return errors, status.HTTP_400_BAD_REQUEST

        if not MessageModel.is_unique(id=0, message=request_dict.get("message")):
            return {
                "error": "A message with the same name already exists"
            }, status.HTTP_400_BAD_REQUEST
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
                message=request_dict["message"].lower(),
                duration=request_dict["duration"],
                category=category,
            )
            message.add(message)
            query = MessageModel.query.get(message.id)
            result = message_schema.dump(query)
            return result, status.HTTP_201_CREATED
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            # return resp, status.HTTP_400_BAD_REQUEST
            return {"error": str(e)}, status.HTTP_400_BAD_REQUEST
