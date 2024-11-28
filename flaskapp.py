from flask import Flask, request

app = Flask(__name__)

WCDTEND = "http://18.142.180.187/"


@app.route("/")
def index():
	return "DT_WINCAMPAIGN BUSINESS LAYER RUNNING"

@app.route("/api/payload",methods=["POST","GET","PUT"])
def receive_payload():
	PAYLOAD = request.json
	print(PAYLOAD)
	return {'msg':"done","data_sent":PAYLOAD}

# sudo git pull && sudo service apache2 restart && sudo tail -f /var/log/apache2/error.log