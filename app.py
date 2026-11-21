
from flask import Flask

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    print("FLASK APP SUCCESSFULLY RUNNING")
    return "SUCCESS: Flask app is running on Vercel!"

@app.route("/invoice", methods=["GET", "POST"])
def invoice():
    print("INVOICE ROUTE SUCCESSFULLY REACHED")

    if request.method == "GET":
        return "Invoice endpoint is alive. Send PDF using POST."

    return "POST route is working."

from flask import request
