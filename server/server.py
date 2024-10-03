from flask import Flask

app = Flask(__name__)

@app.route("/config")
def get_config():
    pass

@app.route("/event")
def event():
    pass


if __name__ == "__main__":
    app.run()