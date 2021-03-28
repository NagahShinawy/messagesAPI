from flask_restful import Resource


class Root(Resource):

    def get(self):
        from autoapp import app
        return {
            "status": "OK",
            # "routes": [ for url in app.url_map.iter_rules()]
        }