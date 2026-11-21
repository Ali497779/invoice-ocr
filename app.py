
from flask import Flask, request

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    print("FLASK APP SUCCESSFULLY RUNNING")
    return "SUCCESS: Flask app is running on Vercel!", 200

@app.route("/invoice", methods=["GET", "POST"])
def invoice():
    print("INVOICE ROUTE SUCCESSFULLY REACHED")

    if request.method == "GET":
        return "Invoice endpoint is alive. Send PDF using POST.", 200

    uploaded_file = request.files.get("file")

    if uploaded_file is None:
        return "Missing file field", 400

    return f"File received: {uploaded_file.filename}", 200

