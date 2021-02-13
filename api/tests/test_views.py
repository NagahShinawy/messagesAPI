from api.app import create_app
from base64 import b64encode
from flask import url_for
from api.extensions import db
from api.utils.http import status
from unittest import TestCase
from requests.auth import _basic_auth_str


class InitialTests(TestCase):
    def setUp(self):
        self.app = create_app("api.config.test_config")
        self.test_client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.test_user_name = "testuser"
        self.test_user_password = "T3s!p4s5w0RDd12#"
        db.create_all()

    def tearDown(self):
        """
        executed after every unittest run
        it deletes db every time of run unittest
        :return:
        """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_accept_content_type_headers(self):
        return {"Accept": "application/json", "Content-Type": "application/json"}

    def get_authentication_headers(self, username, password):
        authentication_headers = self.get_accept_content_type_headers()

        authentication_headers["Authorization"] = "Basic " + b64encode(
            (username + ":" + password).encode("utf-8")
        ).decode("utf-8")

        # credentials = b64encode(b"testuser:T3s!p4s5w0RDd12#").decode('utf-8')
        # authentication_headers['Authorization'] = "Basic " + credentials

        # authentication_headers['Authorization'] = _basic_auth_str(username, password)

        # user_credentials = b64encode(b"testuser:T3s!p4s5w0RDd12#").decode()
        # authentication_headers.update({"Authorization": "Basic {}".format(user_credentials)})

        return authentication_headers

    def test_request_without_authentication(self):
        """
        Ensure we cannot access a resource that requirest authentication without an appropriate authentication header
        """
        response = self.test_client.get(
            url_for("api.messagelistresource", _external=True),
            headers=self.get_accept_content_type_headers(),
        )
        self.assertTrue(response.status_code == status.HTTP_401_UNAUTHORIZED)
