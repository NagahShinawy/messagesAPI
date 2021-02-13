from flask import json, url_for
from api.utils.http import status
from api.models.message import MessageModel
from api.models.category import CategoryModel
from api.tests.test_user import TestUser


class TestMessage(TestUser):
    def create_message(self, message, duration, category):
        url = url_for("api.messagelistresource", _external=True)
        data = {"message": message, "duration": duration, "category": category}
        response = self.test_client.post(
            url,
            headers=self.get_authentication_headers(
                self.test_user_name, self.test_user_password
            ),
            data=json.dumps(data),
        )
        return response

    def test_create_and_retrieve_message(self):
        """
        Ensure we can create a new message and then retrieve it
        """
        create_user_response = self.create_user(
            self.test_user_name, self.test_user_password
        )
        self.assertEqual(create_user_response.status_code, status.HTTP_201_CREATED)
        new_message_message = "Welcome to the IoT world"
        new_message_category = "Information"
        post_response = self.create_message(
            new_message_message, 15, new_message_category
        )
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MessageModel.query.count(), 1)
        # The message should have created a new category
        self.assertEqual(CategoryModel.query.count(), 1)
        post_response_data = json.loads(post_response.get_data(as_text=True))
        self.assertEqual(post_response_data["message"], new_message_message)
        new_message_url = post_response_data["url"]
        get_response = self.test_client.get(
            new_message_url,
            headers=self.get_authentication_headers(
                self.test_user_name, self.test_user_password
            ),
        )
        get_response_data = json.loads(get_response.get_data(as_text=True))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response_data["message"], new_message_message)
        self.assertEqual(get_response_data["category"]["name"], new_message_category)

    def test_create_duplicated_message(self):
        """
        Ensure we cannot create a duplicated Message
        """
        create_user_response = self.create_user(
            self.test_user_name, self.test_user_password
        )
        self.assertEqual(create_user_response.status_code, status.HTTP_201_CREATED)
        new_message_message = "Welcome to the IoT world"
        new_message_category = "Information"
        post_response = self.create_message(
            new_message_message, 15, new_message_category
        )
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MessageModel.query.count(), 1)
        post_response_data = json.loads(post_response.get_data(as_text=True))
        self.assertEqual(post_response_data["message"], new_message_message)
        new_message_url = post_response_data["url"]
        get_response = self.test_client.get(
            new_message_url,
            headers=self.get_authentication_headers(
                self.test_user_name, self.test_user_password
            ),
        )
        get_response_data = json.loads(get_response.get_data(as_text=True))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response_data["message"], new_message_message)
        self.assertEqual(get_response_data["category"]["name"], new_message_category)
        second_post_response = self.create_message(
            new_message_message, 15, new_message_category
        )
        self.assertEqual(second_post_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(MessageModel.query.count(), 1)

    def test_retrieve_messages_list(self):
        """
        Ensure we can retrieve the messages paginated list
        """
        create_user_response = self.create_user(
            self.test_user_name, self.test_user_password
        )
        self.assertEqual(create_user_response.status_code, status.HTTP_201_CREATED)
        new_message_message_1 = "Welcome to the IoT world"
        new_message_category_1 = "Information"
        post_response = self.create_message(
            new_message_message_1, 15, new_message_category_1
        )
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MessageModel.query.count(), 1)
        new_message_message_2 = "Initialization of the board failed"
        new_message_category_2 = "Error"
        post_response = self.create_message(
            new_message_message_2, 10, new_message_category_2
        )
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MessageModel.query.count(), 2)
        get_first_page_url = url_for("api.messagelistresource", _external=True)
        get_first_page_response = self.test_client.get(
            get_first_page_url,
            headers=self.get_authentication_headers(
                self.test_user_name, self.test_user_password
            ),
        )
        get_first_page_response_data = json.loads(
            get_first_page_response.get_data(as_text=True)
        )
        self.assertEqual(get_first_page_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_first_page_response_data["count"], 2)
        self.assertIsNone(get_first_page_response_data["previous"])
        self.assertIsNone(get_first_page_response_data["next"])
        self.assertIsNotNone(get_first_page_response_data["results"])
        self.assertEqual(len(get_first_page_response_data["results"]), 2)
        self.assertEqual(
            get_first_page_response_data["results"][0]["message"], new_message_message_1
        )
        self.assertEqual(
            get_first_page_response_data["results"][1]["message"], new_message_message_2
        )
        get_second_page_url = url_for("api.messagelistresource", page=2)
        get_second_page_response = self.test_client.get(
            get_second_page_url,
            headers=self.get_authentication_headers(
                self.test_user_name, self.test_user_password
            ),
        )
        get_second_page_response_data = json.loads(
            get_second_page_response.get_data(as_text=True)
        )
        self.assertEqual(get_second_page_response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(get_second_page_response_data["previous"])
        self.assertEqual(
            get_second_page_response_data["previous"],
            url_for("api.messagelistresource", page=1),
        )
        self.assertIsNone(get_second_page_response_data["next"])
        self.assertIsNotNone(get_second_page_response_data["results"])
        self.assertEqual(len(get_second_page_response_data["results"]), 0)

    def test_update_message(self):
        """
        Ensure we can update a single field for an existing message
        """
        create_user_response = self.create_user(
            self.test_user_name, self.test_user_password
        )
        self.assertEqual(create_user_response.status_code, status.HTTP_201_CREATED)
        new_message_message_1 = "Welcome to the IoT world"
        new_message_category_1 = "Information"
        post_response = self.create_message(
            new_message_message_1, 30, new_message_category_1
        )
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MessageModel.query.count(), 1)
        post_response_data = json.loads(post_response.get_data(as_text=True))
        new_message_url = post_response_data["url"]
        new_printed_times = 1
        new_printed_once = True
        data = {"printed_times": new_printed_times, "printed_once": new_printed_once}
        patch_response = self.test_client.patch(
            new_message_url,
            headers=self.get_authentication_headers(
                self.test_user_name, self.test_user_password
            ),
            data=json.dumps(data),
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        get_response = self.test_client.get(
            new_message_url,
            headers=self.get_authentication_headers(
                self.test_user_name, self.test_user_password
            ),
        )
        get_response_data = json.loads(get_response.get_data(as_text=True))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response_data["printed_times"], new_printed_times)
        self.assertEqual(get_response_data["printed_once"], new_printed_once)
