import flask

# Create a simple hello world application.
app = flask.Flask(__name__)


@app.route('/')
def hello_world():
    #Enable basic access authentication.
    username = "admin"
    password = "admin"
    if flask.request.authorization and flask.request.authorization.username == username and flask.request.authorization.password == password:
        return 'Hello, World!'


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="33")
