from flask_restful import abort, marshal_with, reqparse, Resource
from datetime import datetime
from models.message import MessageModel
from utils.http import status
from pytz import utc
from managers.message_manager import message_manager, message_fields


class Message(Resource):
    def abort_if_message_doesnt_exist(self, _id):
        if _id not in message_manager.messages:
            abort(
                status.HTTP_404_NOT_FOUND,
                message="Message {0} doesn't exist".format(_id),
            )

    @marshal_with(message_fields)
    def get(self, _id):
        self.abort_if_message_doesnt_exist(_id)
        return message_manager.get_message(_id)

    def delete(self, _id):
        self.abort_if_message_doesnt_exist(_id)
        message_manager.delete_message(_id)
        return "", status.HTTP_204_NO_CONTENT

    @marshal_with(message_fields)
    def patch(self, _id):
        self.abort_if_message_doesnt_exist(_id)
        message = message_manager.get_message(_id)
        parser = reqparse.RequestParser()
        parser.add_argument("message", type=str)
        parser.add_argument("duration", type=int)
        parser.add_argument("printed_times", type=int)
        parser.add_argument("printed_once", type=bool)
        parser.add_argument("message_category", type=str)
        args = parser.parse_args()
        if args.get("message"):
            message.message = args["message"]
        if args.get("duration"):
            message.duration = args["duration"]
        if args.get("printed_times"):
            message.printed_times = args["printed_times"]
        if "printed_once" in args:
            message.printed_once = args["printed_once"]
        if args.get("message_category"):
            message.message_category = args["message_category"]
        return message, status.HTTP_202_ACCEPTED
        # use 'marshal' to return serializer message or use @marshal_with(message_fields)
        # message: obj to be serialized and 'message_fields' which fields to be serialized
        # return marshal(message, message_fields), status.HTTP_202_ACCEPTED


class MessageList(Resource):
    @marshal_with(message_fields)  # fields to be serialized
    def get(self):
        return [message for message in message_manager.messages.values()]

    @marshal_with(message_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "message", type=str, required=True, help="Message cannot be blank!"
        )
        parser.add_argument(
            "duration", type=int, required=True, help="Duration cannot be blank!"
        )
        parser.add_argument(
            "message_category",
            type=str,
            required=True,
            help="Message category cannot be blank!",
        )
        args = parser.parse_args()
        message = MessageModel(
            message=args["message"],
            duration=args["duration"],
            creation_date=datetime.now(utc),
            message_category=args["message_category"],
        )
        message_manager.insert_message(message)
        return message, status.HTTP_201_CREATED
