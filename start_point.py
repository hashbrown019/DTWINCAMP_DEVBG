import config as c
from flask import Flask, request
import json
from urllib.parse import urlparse
from urllib.parse import parse_qs
import requests

app = Flask(__name__)

WCDTEND = "http://18.142.180.187/"
PATH = c.PATH
SURECART_TOKEN = c.SURECART_TOKEN


@app.route("/")
def index():
	return "DT_WINCAMPAIGN BUSINESS LAYER RUNNING"

@app.route("/api/payload",methods=["POST","GET","PUT"])
def receive_payload():
	PAYLOAD = convertSureCartRawToNestedJSON(request.json)
	f = open(f"{PATH}payloads/last_payload","w")
	f.write(json.dumps(PAYLOAD))
	f.close()
	reconstructPayload(PAYLOAD)
	return {'msg':"done","data_sent":PAYLOAD}

def get_aff_link_from_surecart(query):
	url = f'https://api.surecart.com/v1/affiliations?query={query}'
	headers = {
		'Authorization': SURECART_TOKEN,
		'Content-Type': 'application/json'
	}
	response = requests.get(url, headers=headers)
	return json.loads(response.text)["data"][0]


def reconstructPayload(PAYLOAD):
	used_initial_url = urlparse(PAYLOAD["checkout"]["metadata"]["page_url"])
	url_args = parse_qs(used_initial_url.query)
	myclink = f'{get_aff_link_from_surecart(PAYLOAD["checkout"]["customer"]["name"])["referral_url"]}'
	upclink = f'{get_aff_link_from_surecart(PAYLOAD["checkout"]["customer"]["affiliation"])["referral_url"]}'
	wc_is_active = "active" if f'{get_aff_link_from_surecart(PAYLOAD["checkout"]["customer"]["affiliation"])["active"]}'.lower() == "true" else "inactive"
	print(wc_is_active)
	details_byemail_name = {
		"DTMemberID": url_args['dtid'][0],
		"DTName":PAYLOAD["checkout"]["customer"]["name"],
		"DTEmail":PAYLOAD["checkout"]["customer"]["email"],
		# "DTMemberStatus": "",
		"MyWinCampaignLink":myclink,
		"UpLineAffiliateLink":upclink,
		"statusMyWinCampaignLink": wc_is_active
	}
	FILENAME_PAAYLOAD = PAYLOAD["checkout"]["customer"]["affiliation"]
	f = open(f"{PATH}payloads/{FILENAME_PAAYLOAD}","w")
	f.write(json.dumps(details_byemail_name))
	f.close()
	return details_byemail_name

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
	# return raw_payload
	return (f'''
		<pre id='payload'></pre>
		<hr>
		<pre id='json'></pre>
		<script>
			var True = true
			var False = false
			var None = undefined
			document.getElementById("payload").textContent = JSON.stringify({reconstructPayload(raw_payload)}, undefined, 2);
			document.getElementById("json").textContent = JSON.stringify({raw_payload}, undefined, 2);
			console.log({raw_payload})
		</script>
	''')

# cd /var/www/html/DTWINCAMP_DEVBG/ && sudo git pull && sudo service apache2 restart && sudo tail -f /var/log/apache2/error.log