import config as c
from flask import Flask, request
import json

app = Flask(__name__)

WCDTEND = "http://18.142.180.187/"
PATH = c.PATH

@app.route("/")
def index():
	return "DT_WINCAMPAIGN BUSINESS LAYER RUNNING"

@app.route("/api/payload",methods=["POST","GET","PUT"])
def receive_payload():
	PAYLOAD = convertSureCartRawToNestedJSON(request.json)
	f = open(f"{PATH}payloads/last_payload","w")
	f.write(json.dumps(PAYLOAD))
	f.close()
	return {'msg':"done","data_sent":PAYLOAD}


def reconstructPaload():
	pass



def convertSureCartRawToNestedJSON(raw):
	data_out = {}
	for key, value in raw.items():
		cur = data_out
		*keys, leaf = key.split('.')
		for k in keys:
			cur = cur.setdefault(k, {})
		cur[leaf] = value
	return data_out


# ===================================================================
@app.route("/api/test",methods=["POST","GET","PUT"])
def test_last_payload():
	f = open(f"{PATH}payloads/last_payload","r")
	content = f.read()
	f.close()
	raw_payload = json.loads(content)
	return convertSureCartRawToNestedJSON(raw_payload)

# cd /var/www/html/DTWINCAMP_DEVBG/ && sudo git pull && sudo service apache2 restart && sudo tail -f /var/log/apache2/error.log