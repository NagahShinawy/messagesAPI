from flask_jwt_extended import create_access_token
from flask_restful import Resource
from flask import request
from sqlalchemy.exc import SQLAlchemyError
from api.extensions import db
from api.views.security import AuthRequiredResource
from api.views.security import auth
from api.models.user import UserModel
from api.schema.user import UserSchema
from api.utils.helpers.pagination import PaginationHelper
from api.utils.http import status
from werkzeug.security import generate_password_hash, check_password_hash


user_schema = UserSchema()


class UserResource(AuthRequiredResource):
    def get(self, id):
        user = UserModel.query.get_or_404(id)
        result = user_schema.dump(user)
        return result


class UserListResource(
    Resource
):  # inherit from Resource not AuthRequiredResource because we need just auth on get not on all
    # methods of UserListResource
    @auth.login_required
    def get(self):
        pagination_helper = PaginationHelper(
            request,
            query=UserModel.query,
            resource_for_url="api.userlistresource",
            key_name="results",
            schema=user_schema,
        )
        result = pagination_helper.paginate_query()
        return result

    def post(self):
        request_dict = request.get_json()
        if not request_dict:
            response = {"user": "No input data provided"}
            return response, status.HTTP_400_BAD_REQUEST
        errors = user_schema.validate(request_dict)
        if errors:
            return errors, status.HTTP_400_BAD_REQUEST
        name = request_dict["name"]
        existing_user = UserModel.is_unique(id=0, name=name)
        if not existing_user:
            response = {"user": "An user with the same name already exists"}

            return response, status.HTTP_400_BAD_REQUEST
        try:
            password = request_dict.get("password")
            user = UserModel(name=name.lower())
            error_message, password_ok = user.check_password_strength_and_hash_if_ok(
                password
            )
            if password_ok:
                # user.password = generate_password_hash(password)
                user.add(user)
                query = UserModel.query.get(user.id)
                result = user_schema.dump(query)
                return result, status.HTTP_201_CREATED
            else:
                return {"error": error_message}, status.HTTP_400_BAD_REQUEST
        except SQLAlchemyError as e:
            db.session.rollback()
            # resp = {"error": str(e)}
            return {"error": str(e)}, status.HTTP_400_BAD_REQUEST


class UserLogin(Resource):
    def post(self):
        if request.is_json:  # check if data comes from json or html form
            data = request.json
        else:
            data = request.form
        name = data.get("name")
        password = data.get("password")
        user = UserModel.query.filter_by(name=name).first()
        if user:
            hashed_password = user.password
            if check_password_hash(hashed_password, password):
                token = create_access_token(identity=name)
                return {"token": token}, status.HTTP_200_OK
        return {
            "msg": "incorrect name or password"
        }, status.HTTP_401_UNAUTHORIZED  # means permissions denied
