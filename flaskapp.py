from flask import Flask

app = Flask(__name__)

@app.route("/received",methods=["POST","GET","PUT"])
def index():
	return "hi"