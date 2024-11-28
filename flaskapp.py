from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
	return "DT_WINCAMPAIGN BUSINESS LAYER RUNNING"

@app.route("/received",methods=["POST","GET","PUT"])
def index():
	return "Test"