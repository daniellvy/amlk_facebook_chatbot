# -*- coding: utf-8 -*-
import os
import sys
import json
import re
from link_parser import *
from datetime import datetime

import requests
from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():
    # endpoint for processing incoming messaging events
    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing
    if data["object"] == "page":
        for entry in data["entry"]:
            if "messaging" in entry:
                for messaging_event in entry["messaging"]:
                    if messaging_event.get("message"):  # someone sent us a message
                        try:
                            sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                            recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                            message_text = messaging_event["message"]["text"]  # the message's text
                        except:
                            return "ok", 200

                        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message_text)
                        if len(urls) == 0:
                            send_message(sender_id, u'שלח לינק לכתבה לקבלת אמ;לק')
                        else:
                            domain = which_domain(urls[0])
                            if domain not in ['ynet', 'walla', 'mako']:
                                send_message(sender_id, u'זוהי גרסה ראשונית של הבוט, האתרים הנתמכים הם ynet, mako ו-walla')
                            else:
                                try:
                                    log("URL " + urls[0])
                                    r = requests.get(urls[0])
                                    log("Got request")
                                    if r.status_code == 200:
                                        log("Status code 200")
                                        log(domain)

                                        t, s, ps = parse_article(str(r.content), domain)
                                        log("Parsed succeeded")
                                        log(t)
                                        log(s)
                                        log(ps[0])


                                        #send_message(sender_id, t.encode("UTF-8"))
                                        log("Sent message")
                                    else:
                                        send_message(sender_id, u'הלינק ששלחת לא תקין')
                                except:
                                    send_message(sender_id, u'שגיאה בקריאת הכתבה')

                    if messaging_event.get("delivery"):  # delivery confirmation
                        pass

                    if messaging_event.get("optin"):  # optin confirmation
                        pass

                    if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                        pass
    return "ok", 200

def send_message(recipient_id, message_text):

    #log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
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


def log(msg, *args, **kwargs):  # simple wrapper for logging to stdout on heroku
    try:
        if type(msg) is dict:
            msg = json.dumps(msg)
        else:
            msg = unicode(msg).format(*args, **kwargs)
        print u"{}: {}".format(datetime.now(), msg)
    except UnicodeEncodeError:
        pass  # squash logging errors in case of non-ascii text
    sys.stdout.flush()


#if __name__ == '__main__':
    #app.run(debug=True)
