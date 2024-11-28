from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
	return "DT_WINCAMPAIGN BUSINESS LAYER RUNNING"

@app.route("/api/payload",methods=["POST","GET","PUT"])
def receive_payload():
	return "Test"