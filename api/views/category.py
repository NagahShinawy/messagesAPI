from flask import request, jsonify, make_response
from flask_restful import Resource
from api.models.category import CategoryModel
from api.extensions import db
from sqlalchemy.exc import SQLAlchemyError
from api.utils.http import status
from api.schema.category import CategorySchema


category_schema = CategorySchema()


class CategoryResource(Resource):
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
                category.name = category_dict["name"]
            category.update()
            return self.get(id)
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            return resp, status.HTTP_400_BAD_REQUEST

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


class CategoryListResource(Resource):
    def get(self):
        categories = CategoryModel.query.all()
        results = category_schema.dump(categories, many=True)
        return results

    def post(self):
        request_dict = request.get_json()
        if not request_dict:
            resp = {"message": "No input data provided"}
            return resp, status.HTTP_400_BAD_REQUEST
        errors = category_schema.validate(request_dict)
        if errors:
            return errors, status.HTTP_400_BAD_REQUEST
        try:
            category = CategoryModel(request_dict["name"])
            category.add(category)
            query = CategoryModel.query.get(category.id)
            result = category_schema.dump(query)
            return {"data": result}, status.HTTP_201_CREATED
        except SQLAlchemyError as e:
            db.session.rollback()
            # resp = jsonify({"error": str(e)})
            return {"error": str(e)}, status.HTTP_400_BAD_REQUEST
