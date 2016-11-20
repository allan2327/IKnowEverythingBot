import os
import sys
import json
import duckduckgo
import requests
from flask import Flask, request

app = Flask(__name__)
app.config.from_pyfile('flaskapp.cfg')
 
ACCESS_TOKEN = "ACCESS_TOKEN"
 
@app.route('/', methods=['GET'])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        return request.args["hub.challenge"], 200

    return "IKnowEveryrthing", 200


@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):  
                    sender_id = messaging_event["sender"]["id"]        
                    message_text = messaging_event["message"]["text"]  
                    r = duckduckgo.query(message_text)
                    print sender_id,'----> ' ,message_text
                    msg=''
                    if r.abstract.text.encode('ascii', 'ignore')[:320]=='':
                    	msg='Looks like I dont know that ! I need some more training'
                    else:
                    	msg=r.abstract.text.encode('ascii', 'ignore')[:320]
                    send_message(sender_id,msg)

                if messaging_event.get("delivery"): 
                    pass

                if messaging_event.get("optin"):  
                    pass

                if messaging_event.get("postback"):  
                    pass

    return "ok", 200


def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))
    params = {
        "access_token": ACCESS_TOKEN
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)