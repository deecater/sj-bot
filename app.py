import os
import sys
import json

import requests
from flask import Flask, request

app = Flask(__name__)

#import quick reply dictionaries
import quickReplyDicts

# quick reply dictionaries
#fem_dictionary = [
#            {"content_type":"text",
#            "title":"What is feminism?",
#            "payload":"fem_definition"
#            },
#            {"content_type":"text",
#            "title":"History of feminism",
#            "payload":"fem_history"
#            }]

#start_dictionary = [
#            {"content_type":"text",
#            "title":"Feminism",
#            "payload":"start_fem"
#            },
#            {"content_type":"text",
#            "title":"Racism",
#            "payload":"start_race"
#            },
#            {"content_type":"text",
#            "title":"Gay Rights",
#            "payload":"start_gay"
#            },
#            {"content_type":"text",
#            "title":"Trans Rights",
#            "payload":"start_trans"
#            }]


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
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text

                    if (message_text == "help"):
                        send_message(sender_id, "here's some help")
                    elif (message_text == "hi"):
                        send_message(sender_id, "hi, there!")
                    elif ("okay" in message_text):
                        send_message(sender_id, "affirmative")
                    elif (message_text.lower() == "feminism"):
                        send_quick_reply(sender_id, "Awesome! Let's get started. What would you like to explore about feminism?", fem_dictionary)
                    elif (message_text == "What is feminism?"):
                        send_message(sender_id, "did we fix it?")
                    else:
                        send_quick_reply(sender_id, "Hi! My name is Social Justice Bot, or SJ Bot for short. What topic would you like to learn more about?", start_dictionary)

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message

                    message_text = messaging_event["postback"]["payload"] # the button's payload
                    log("Inside postback")

                    message_text = message_text.lower()

                    sender_id = messaging_event ["sender"]["id"]

                    if (message_text == "fem_definition"):
                        send_message(sender_id, "help")

    return "ok", 200

# send a text message function
def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

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

# send a quick reply
def send_quick_reply(recipient_id, message_text, reply_dictionary):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

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
            "text": message_text,
            "quick_replies": reply_dictionary
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
