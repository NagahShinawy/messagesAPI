from flask_restful import fields


class MessageManager:
    last_id = 0

    def __init__(self):
        self.messages = {}

    def insert_message(self, message):
        self.__class__.last_id += 1
        message._id = self.__class__.last_id
        self.messages[self.__class__.last_id] = message

    def get_message(self, _id):
        return self.messages[_id]

    def delete_message(self, _id):
        del self.messages[_id]


message_fields = {
    "_id": fields.Integer,
    "uri": fields.Url("single_message_endpoint"),
    "message": fields.String,
    "duration": fields.Integer,
    "creation_date": fields.DateTime,
    "message_category": fields.String,
    "printed_times": fields.Integer,
    "printed_once": fields.Boolean,
}


message_manager = MessageManager()
