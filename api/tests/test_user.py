from api.tests.test_views import InitialTests
from api.models.user import UserModel
from flask import json, url_for
from api.utils.http import status


class TestUser(InitialTests):
    def create_user(self, name, password):
        url = url_for("api.userlistresource", _external=True)
        data = {"name": name, "password": password}
        response = self.test_client.post(
            url, headers=self.get_accept_content_type_headers(), data=json.dumps(data)
        )
        return response

    def test_create_and_retrieve_user(self):
        """
        Ensure we can create a new User and then retrieve it
        """
        new_user_name = self.test_user_name
        new_user_password = self.test_user_password
        post_response = self.create_user(new_user_name, new_user_password)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserModel.query.count(), 1)
        post_response_data = json.loads(post_response.get_data(as_text=True))
        self.assertEqual(post_response_data["name"], new_user_name)
        new_user_url = post_response_data["url"]
        get_response = self.test_client.get(
            new_user_url,
            headers=self.get_authentication_headers(
                self.test_user_name, self.test_user_password
            ),
        )
        get_response_data = json.loads(get_response.get_data(as_text=True))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response_data["name"], new_user_name)
