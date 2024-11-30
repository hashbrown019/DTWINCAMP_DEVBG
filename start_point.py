import config as c
from flask import Flask, request
import json
from urllib.parse import urlparse
from urllib.parse import parse_qs
import requests

app = Flask(__name__)

WCDTEND = "http://18.142.180.187/"
DTPAYLOAD_RECEIVER = 'https://wcreceivesubscriptionaffiliate.azurewebsites.net/api/SubscriptionAffiliateReceiver?code=yKrrRuXRtkTuIQDuZX7342x4dsG6w5b6ub4FHtlWFERgAzFuBWZUHg%3D%3D'
PATH = c.PATH
SURECART_TOKEN = c.SURECART_TOKEN
PRODUCTS_NAME = c.PROD_LVLDICT
PROD_LVL = c.PROD_LVL

@app.route("/")
def index():return "DT_WINCAMPAIGN BUSINESS LAYER RUNNING"


@app.route("/api/payload/get")
def get_payload():
	return "DT_WINCAMPAIGN BUSINESS LAYER RUNNING"

@app.route("/api/payload/test",methods=["POST","GET"])
def test_payload():
	# headers = {'Content-Type': 'application/json'}
	# params = {
	# 	"expand[]": ["checkout", "checkout.customer"],
	# }
	# print(request.json)
	# customer = request.json
	# _link = f"https://api.surecart.com/v1/orders?query={customer['id']}"
	# print(_link)
	# server_return = requests.post(_link, headers=headers,params=params)
	# # return_data = {"payload":dtpayload,"server_response":server_return.text}
	# # return server_return.text
	return request.json

@app.route("/api/payload/send",methods=["POST","GET"])
def receive_payload():
	print(" -- Setting Payload for Saving--")
	PAYLOAD = convertSureCartRawToNestedJSON(request.json)
	cname = PAYLOAD['checkout']['customer']['name']
	cid = PAYLOAD['checkout']['customer']['id']
	cemail = PAYLOAD['checkout']['customer']['email']
	cid = PAYLOAD['checkout']['customer']['id']
	print(f" Payload email: {cemail}")
	print(f" ** Saving Payload to dir [Payloads/] = {cemail}")
	f = open(f"{PATH}payloads/{cid}","w")
	f.write(json.dumps(PAYLOAD))
	f.close()
	used_initial_url = urlparse(PAYLOAD["checkout"]["metadata"]["page_url"])
	cus = PAYLOAD['checkout']['customer']
	cus['dt_referral_link'] = used_initial_url

	print(f" ** Saving Payload to dir [customers/] = {cemail}")
	f = open(f"{PATH}customers/{cid}","w")
	f.write(json.dumps(cus))
	f.close()

	# ---------------------------------------

	# ---------------------------------------
	PAYLOAD = convertSureCartRawToNestedJSON(request.json)
	f = open(f"{PATH}payloads/last_payload","w")
	f.write(json.dumps(PAYLOAD))
	f.close()
	dtpayload = reconstructPayload(PAYLOAD)
	headers = {'Content-Type': 'application/json'}
	print("------Payload Data-----")
	print(dtpayload)
	# return dtpayload

	# ----------

	server_return = requests.post(DTPAYLOAD_RECEIVER, headers=headers, json=dtpayload)
	return_data = {"payload":dtpayload,"server_response":server_return.text}
	print(return_data)
	return request.json


# ================================================================================================
# ================================================================================================
@app.route("/api/payload/send_to_dt",methods=["POST","GET"])
def preapare_send_payload():
	print("-----------------------------------")
	PAYLOAD = convertSureCartRawToNestedJSON(request.json)
	cemail = PAYLOAD['email']
	url = f"https://api.surecart.com/v1/customers?query={cemail}"
	print(f" ** Getting Customer_details by SURECART API using : {cemail}")

	headers = {'Authorization': SURECART_TOKEN,'Content-Type': 'application/json'}
	response = requests.get(url, headers=headers)

	print(f" ** Rsponse From  : {cemail}")
	customer = response.text
	print(customer)
	# dtpayload = reconstructPayload(PAYLOAD)
	# headers = {'Content-Type': 'application/json'}
	# server_return = requests.post(DTPAYLOAD_RECEIVER, headers=headers, json=dtpayload)
	# return_data = {"payload":dtpayload,"server_response":server_return.text}
	# print(return_data)
	return customer

# ================================================================================================
# ================================================================================================
# ================================================================================================
# ================================================================================================
# ================================================================================================
# ================================================================================================
def get_aff_link_from_surecart(query):
	url = f'https://api.surecart.com/v1/affiliations?query={query}'
	headers = {'Authorization': SURECART_TOKEN,'Content-Type': 'application/json'}
	res = json.loads(requests.get(url, headers=headers).text)
	print(" ====== Aff if any ========")
	print(res)
	return res["data"][0] #aff

def get_subs_from_surecart(query):
	url = f'https://api.surecart.com/v1/subscriptions?checkout_ids[]={query}'
	headers = {'Authorization': SURECART_TOKEN,'Content-Type': 'application/json'}
	res = json.loads(requests.get(url, headers=headers).text)
	print(" ====== Subs Available ========")
	print(res)
	# if("data" in res):
	# 	res["data"] = []
	return res["data"][0] #subs


def reconstructPayload(PAYLOAD):
	used_initial_url = urlparse(PAYLOAD["checkout"]["metadata"]["page_url"])
	url_args = parse_qs(used_initial_url.query)
	myclink = f'{get_aff_link_from_surecart(PAYLOAD["checkout"]["customer"]["email"])["referral_url"]}'
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
		"statusMyWinCampaignLink": wc_is_active,
		# "wc-subscription_logs" : createSubLogs(PAYLOAD['checkout']['line_items']['data'])
		"wc-subscription_logs" : createSubLogs(PAYLOAD["product"],PAYLOAD['checkout']['line_items']['data'])
	}
	FILENAME_PAAYLOAD = PAYLOAD["checkout"]["customer"]["affiliation"]
	f = open(f"{PATH}payloads/{FILENAME_PAAYLOAD}","w")
	f.write(json.dumps(details_byemail_name))
	f.close()
	return details_byemail_name

def createSubLogs(subs,line_items):
	subs_arr = []
	print("---------------CREATING LOGS--------------------")
	print(subs)
	print(line_items)
	for ind in range(len(subs)):
		SUBSLINE_ITEM = get_subs_from_surecart(line_items[ind]['checkout'])
		subs_arr.append({
			"subscription_id": subs[ind]["id"],
			"product_name": PRODUCTS_NAME[subs[ind]["slug"]],
			"subcription_lvl_compared_to_prev": lvlofsubscription(subs[ind]["slug"],subs[ind]["slug"],ind,SUBSLINE_ITEM['status']),
			"subscription_status": SUBSLINE_ITEM['status'],
			"if_cancel_date": SUBSLINE_ITEM['ended_at'],
			"current_period_end_at": SUBSLINE_ITEM['current_period_end_at'],
			"current_period_start_at": SUBSLINE_ITEM['current_period_start_at'],
		})
	return subs_arr


def lvlofsubscription(SUB_SHORT_NAME,subscription_logs,ind,status):
	subcription_lvl_compared_to_prev = "initial"
	if(status=="canceled"):
		subcription_lvl_compared_to_prev = "canceled"
	
	elif(ind>0):
		if(PROD_LVL.index(SUB_SHORT_NAME) > PROD_LVL.index(subscription_logs[ind-1]['product_name']) ):
			subcription_lvl_compared_to_prev = "upgrade"
		elif(PROD_LVL.index(SUB_SHORT_NAME) == PROD_LVL.index(subscription_logs[ind-1]['product_name']) ):
			subcription_lvl_compared_to_prev = "unchanged"
		else:
			subcription_lvl_compared_to_prev = "downgrade"
		
	
	return subcription_lvl_compared_to_prev



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
# from gevent import pywsgi
# http_server = pywsgi.WSGIServer(('0.0.0.0', 443), app, keyfile='server.key', certfile='server.crt')
# http_server.serve_forever()