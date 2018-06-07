from flask import Flask, request
import requests,json
from flask_sslify import SSLify

app = Flask(__name__)		#creates Flask app

sslify=SSLify(app)

url="https://api.telegram.org/bot<YOUR_BOT_TOKEN>/"

query="Enter origin(DEL),dest(BLR),departdate(yyyymmdd),class,Adults,Child,Infant,airline "

# sends message to our bot
def sendmsg(chatid,text):
	URL=url+'sendMessage'
	ans={'chat_id':chatid,'text':text}
	r=requests.post(URL,json=ans)
	

# finds all the flights from given input
def query(chatid,r,air_name):
	l=[]
	for i in range(0,len(r["data"]["onwardflights"])):
		d={}
		if r["data"]["onwardflights"][i]["airline"].lower()==air_name.lower():
			if r["data"]["onwardflights"][i]["stops"]=="0":
				d["origin"]=r["data"]["onwardflights"][i]["origin"]
				d["depterminal"]=r["data"]["onwardflights"][i]["depterminal"]
				d["deptime"]=r["data"]["onwardflights"][i]["deptime"]
				d["duration"]=r["data"]["onwardflights"][i]["duration"]
				d["destination"]=r["data"]["onwardflights"][i]["destination"]
				d["airline"]=r["data"]["onwardflights"][i]["airline"]
				d["fare"]=r["data"]["onwardflights"][i]["fare"]["grossamount"]
				l.append(d)
	return sorted(l,key=lambda k:k['fare'])
	

@app.route('/', methods=['POST'])
def telegram_webhook():
	if request.method=='POST':
		r = request.get_json()
		text = r["message"]["text"]
		chatid = r["message"]["chat"]["id"]
		#sendmsg(chatid,text)
		if text.lower()=='/start':
			sendmsg(chatid,"Hi there!! Start by typing 'hi' ")
			return "OK"
		if text.lower()=='hi':
			sendmsg(chatid,query)
			return "OK"
		try:
			ls=list(text.split())
			air_name=ls[7:]
			air_name=' '.join(air_name)
			url1='http://developer.goibibo.com/api/search/?app_id=<YOUR_APP_ID>&app_key=<YOUR_APP_KEY>&format=json&source='+ls[0]+'&destination='+ls[1]+'&dateofdeparture='+ls[2]+'&seatingclass='+ls[3]+'&adults='+ls[4]+'&children='+ls[5]+'&infants='+ls[6]+'&counter=100'
			r1=requests.get(url1).json()
			q=query(chatid,r1,air_name)
			if len(q)==0:
				sendmsg(chatid,"Sorry, no direct flights available!")
				return "OK"
			sendmsg(chatid,'Available non-stop flights: ')
			sendmsg(chatid,"Origin Terminal DepartTime Duration Dest Airline Fare")
			for i in q:
				s=str()
				for j in i.values():
					s=str(s)+'    '+str(j)
				sendmsg(chatid,str(s))
			return "OK"
		except Exception as e:
			sendmsg(chatid,'Exception has occurred '+str(e))
			return "OK"

if __name__=="__main__":
	app.debug=True
	app.run()