from flask import request, jsonify, make_response
from api.models.category import CategoryModel
from api.extensions import db
from sqlalchemy.exc import SQLAlchemyError
from api.utils.http import status
from api.schema.category import CategorySchema
from api.utils.helpers.pagination import PaginationHelper
from api.views.security import AuthRequiredResource

category_schema = CategorySchema()


class CategoryResource(AuthRequiredResource):
    def get(self, id):
        category = CategoryModel.query.get_or_404(id)
        result = category_schema.dump(category)
        return result

    def patch(self, id):
        category = CategoryModel.query.get_or_404(id)
        category_dict = request.get_json()
        if not category_dict:
            resp = {"message": "No input data provided"}
            return resp, status.HTTP_400_BAD_REQUEST
        errors = category_schema.validate(category_dict)
        if errors:
            return errors, status.HTTP_400_BAD_REQUEST
        try:
            if "name" in category_dict:
                category_name = category_dict["name"]
                if CategoryModel.is_unique(id, name=category_name):
                    category.name = category_name
                else:
                    return {
                        "error": "A category with the same name already exists"
                    }, status.HTTP_400_BAD_REQUEST
            category.update()
            return self.get(id)
        except SQLAlchemyError as e:
            db.session.rollback()
            # resp = jsonify({"error": str(e)})
            return {"error": str(e)}, status.HTTP_400_BAD_REQUEST

    def delete(self, id):
        category = CategoryModel.query.get_or_404(id)
        try:
            category.delete(category)
            response = make_response()
            # return response, status.HTTP_204_NO_CONTENT
            return "", status.HTTP_204_NO_CONTENT
        except SQLAlchemyError as e:
            db.session.rollback()
            # resp = jsonify({"error": str(e)})
            return {"error": str(e)}, status.HTTP_400_BAD_REQUEST


class CategoryListResource(AuthRequiredResource):

    category_schema = CategorySchema()

    # def get(self):
    #     categories = CategoryModel.query.all()
    #     results = category_schema.dump(categories, many=True)
    #     return results

    def get(self):
        pagination_helper = PaginationHelper(
            request,
            query=CategoryModel.query,
            resource_for_url="api.categorylistresource",  # api.categorylistresource > api: is blueprint name
            key_name="results",
            schema=self.category_schema,
        )
        result = pagination_helper.paginate_query()
        return result

    def post(self):
        request_dict = request.get_json()
        if not request_dict:
            resp = {"message": "No input data provided"}
            return resp, status.HTTP_400_BAD_REQUEST
        errors = category_schema.validate(request_dict)
        if errors:
            return errors, status.HTTP_400_BAD_REQUEST

        category_name = request_dict.get("name")
        if not CategoryModel.is_unique(id=0, name=category_name):
            return {
                "error": "A category with the same name already exists"
            }, status.HTTP_400_BAD_REQUEST
        try:
            category = CategoryModel(category_name.lower())
            category.add(category)
            query = CategoryModel.query.get(category.id)
            result = category_schema.dump(query)
            return {"data": result}, status.HTTP_201_CREATED
        except SQLAlchemyError as e:
            db.session.rollback()
            # resp = jsonify({"error": str(e)})
            return {"error": str(e)}, status.HTTP_400_BAD_REQUEST
