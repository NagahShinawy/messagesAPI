from api.app import create_app

app = create_app("api.config.develop")  # app/config/develop.py


if __name__ == "__main__":
    app.run(
        debug=app.config["DEBUG"],
        host=app.config["DB_ADDR"],
        port=app.config["SERVER_PORT"],
    )
