from api.tests.test_views import InitialTests
from flask import json, url_for
from api.utils.http import status
from api.models.category import CategoryModel
from api.tests.test_user import TestUser


class TestCategory(TestUser):
    def create_category(self, name):
        url = url_for("api.categorylistresource", _external=True)
        data = {"name": name}
        response = self.test_client.post(
            url,
            headers=self.get_authentication_headers(
                self.test_user_name, self.test_user_password
            ),
            data=json.dumps(data),
        )
        return response

    def test_create_and_retrieve_category(self):
        """
        Ensure we can create a new Category and then retrieve it
        """
        create_user_response = self.create_user(
            self.test_user_name, self.test_user_password
        )
        self.assertEqual(create_user_response.status_code, status.HTTP_201_CREATED)
        new_category_name = "New Information"
        post_response = self.create_category(new_category_name)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CategoryModel.query.count(), 1)
        post_response_data = json.loads(post_response.get_data(as_text=True))
        self.assertEqual(post_response_data["name"], new_category_name)
        new_category_url = post_response_data["url"]
        get_response = self.test_client.get(
            new_category_url,
            headers=self.get_authentication_headers(
                self.test_user_name, self.test_user_password
            ),
        )
        get_response_data = json.loads(get_response.get_data(as_text=True))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response_data["name"], new_category_name)

    def test_create_duplicated_category(self):
        """
        Ensure we cannot create a duplicated Category
        """
        create_user_response = self.create_user(
            self.test_user_name, self.test_user_password
        )
        self.assertEqual(create_user_response.status_code, status.HTTP_201_CREATED)
        new_category_name = "New Information"
        post_response = self.create_category(new_category_name)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CategoryModel.query.count(), 1)
        post_response_data = json.loads(post_response.get_data(as_text=True))
        self.assertEqual(post_response_data["name"], new_category_name)
        second_post_response = self.create_category(new_category_name)
        self.assertEqual(second_post_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(CategoryModel.query.count(), 1)

    def test_retrieve_categories_list(self):
        """
        Ensure we can retrieve the categories list
        """
        create_user_response = self.create_user(
            self.test_user_name, self.test_user_password
        )
        self.assertEqual(create_user_response.status_code, status.HTTP_201_CREATED)
        new_category_name_1 = "Error"
        post_response_1 = self.create_category(new_category_name_1)
        self.assertEqual(post_response_1.status_code, status.HTTP_201_CREATED)
        new_category_name_2 = "Warning"
        post_response_2 = self.create_category(new_category_name_2)
        self.assertEqual(post_response_2.status_code, status.HTTP_201_CREATED)
        url = url_for("api.categorylistresource", _external=True)
        get_response = self.test_client.get(
            url,
            headers=self.get_authentication_headers(
                self.test_user_name, self.test_user_password
            ),
        )
        get_response_data = json.loads(get_response.get_data(as_text=True))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(get_response_data), 2)
        self.assertEqual(get_response_data[0]["name"], new_category_name_1)
        self.assertEqual(get_response_data[1]["name"], new_category_name_2)

    def test_update_category(self):
        """
        Ensure we can update the name for an existing category
        """
        create_user_response = self.create_user(
            self.test_user_name, self.test_user_password
        )
        self.assertEqual(create_user_response.status_code, status.HTTP_201_CREATED)
        new_category_name_1 = "Error 1"
        post_response_1 = self.create_category(new_category_name_1)
        self.assertEqual(post_response_1.status_code, status.HTTP_201_CREATED)
        post_response_data_1 = json.loads(post_response_1.get_data(as_text=True))
        new_category_url = post_response_data_1["url"]
        new_category_name_2 = "Error 2"
        data = {"name": new_category_name_2}
        patch_response = self.test_client.patch(
            new_category_url,
            headers=self.get_authentication_headers(
                self.test_user_name, self.test_user_password
            ),
            data=json.dumps(data),
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        get_response = self.test_client.get(
            new_category_url,
            headers=self.get_authentication_headers(
                self.test_user_name, self.test_user_password
            ),
        )
        get_response_data = json.loads(get_response.get_data(as_text=True))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response_data["name"], new_category_name_2)
