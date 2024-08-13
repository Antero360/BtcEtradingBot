import httplib
import urllib
import json
import hashlib
import hmac
import time
import array

class Exchange:
	api_key = ""
	api_secret = ""

	def __init__(self, key, secret):
		self.api_key = key
		self.api_secret = secret

	def GetPairs(self):
		conn = httplib.HTTPSConnection("btc-e.com")
		conn.request("POST","/api/3/info")
		response = conn.getresponse()
		respContent = json.load(response)
		pairs = str(respContent["pairs"])
		conn.close()
		return pairs

	def GetCurrentHigh(self,pair):
		conn = httplib.HTTPSConnection("btc-e.com")
		conn.request("POST","/api/3/ticker/{0}".format(pair))
		response = conn.getresponse()
		respContent = json.load(response)
		current = respContent["{0}".format(pair)]["high"]
		conn.close()
		return current

	def OrderInfo(self,orderID):
		nonce = int(round(time.time() - 1398621111,1)*10)
		params = {"method":"OrderInfo",
				  "order_id":orderID,
				  "nonce":nonce}
		params = urllib.urlencode(params)
		hashed = hmac.new(self.api_secret,digestmod=hashlib.sha512)
		hashed.update(params)
		signature = hashed.hexdigest()
		headers = {"Content-type":"application/x-www-form-urlencoded",
				   "Key":self.api_key,
				   "Sign":signature}
		conn = httplib.HTTPSConnection("btc-e.com")
		conn.request("POST","/tapi",params,headers)
		response = conn.getresponse()
		resp = json.load(response)
		success = resp["success"]
		active = resp["return"][str(orderID)]["status"]
		conn.close()
		return active

	def GetBalances(self):
		nonce = int(round(time.time() - 1398621111,1)*10)
		params = {"method":"getInfo",
				  "nonce":nonce}
		params = urllib.urlencode(params)
		hashed = hmac.new(self.api_secret,digestmod=hashlib.sha512)
		hashed.update(params)
		signature = hashed.hexdigest()
		headers = {"Content-type":"application/x-www-form-urlencoded",
				   "Key":self.api_key,
				   "Sign":signature}
		conn = httplib.HTTPSConnection("btc-e.com")
		conn.request("POST","/tapi",params,headers)
		response = conn.getresponse()
		respStat = response.status
		respReason = response.reason
		if respStat != 200:
			successStat = 0
			balances = 0
		else:
			respContent = json.load(response)
			successStat = respContent["success"]
			if successStat != 1:
				balances = 0
			else:
				balances = respContent["return"]["funds"]
		return str(respStat),str(successStat),str(balances)

	def Trade(self,bos,pair,rate,amt):
		nonce = int(round(time.time() - 1398621111,1)*10)
		params = {"method":"Trade",
				  "pair":pair,
				  "type":bos,
				  "rate":rate,
				  "amount":amt,
				  "nonce":nonce}
		params = urllib.urlencode(params)
		hashed = hmac.new(self.api_secret,digestmod=hashlib.sha512)
		hashed.update(params)
		signature = hashed.hexdigest()
		headers = {"Content-type":"application/x-www-form-urlencoded",
				   "Key":self.api_key,
				   "Sign":signature}
		conn = httplib.HTTPSConnection("btc-e.com")
		conn.request("POST","/tapi",params,headers)
		response = conn.getresponse()
		respStat = response.status
		respReason = response.reason
		if respStat != 200:
			successStat = 0
			orderID = 0
		else:
			respContent = json.load(response)
			successStat = respContent["success"]
			if successStat != 1:
				orderID = 0
			else:
				orderID = respContent["return"]["order_id"]
		conn.close()
		return str(respStat),str(successStat),str(orderID)