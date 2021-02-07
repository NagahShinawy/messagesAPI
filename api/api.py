from flask import Flask
from flask_restful import Api
from resources.message import Message, MessageList


app = Flask(__name__)
api = Api(app)
api.add_resource(MessageList, "/api/messages/")
api.add_resource(Message, "/api/messages/<int:_id>", endpoint="single_message_endpoint")


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5051)
