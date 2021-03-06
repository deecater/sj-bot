import os
import sys
import json

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
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text

                    if (message_text.lower() == "help"):
                        send_quick_reply(sender_id, "Happy to help! What do you want to learn more about?", start_dictionary)
                    elif (message_text.lower() == "hi" or message_text.lower() == "hello" or message_text.lower() == "hey" or message_text.lower() == "hiya" or message_text.lower() == "whats up" or message_text.lower() == "what's up"):
                        send_quick_reply(sender_id, "Hi! My name is Social Justice Bot, or SJ Bot for short. What topic would you like to learn more about?", start_dictionary)
                    elif (message_text.lower() == "feminism"):
                        send_quick_reply(sender_id, "Awesome! Let's get started. What would you like to explore about feminism?", fem_dictionary)
                    elif (message_text.lower() == "what is feminism?"):
                        send_quick_reply(sender_id, "Feminism is both an intellectual commitment and a political movement that seeks justice for women and the end of sexism in all forms.\n\nDo you want to learn more?", fem_dictionary)
                    elif(message_text.lower() == "history of feminism"):
                        send_message(sender_id, "history")
                    elif (message_text.lower() == "what feminism isn't"):
                        send_generic_temp(sender_id, "not feminism", not_fem_dictionary)
                    elif (message_text.lower() == "gay rights"):
                        send_quick_reply(sender_id, "Awesome! Let's get started. What would you like to explore about gay rights?", gay_dictionary)
                    elif (message_text.lower() == "what are gay rights?"):
                        send_quick_reply(sender_id, "Gay rights is a movement that is pushing to give homosexuals and homosexual couples the same rights as heterosexuals. These rights include non-discrimination, marriage, adoption, military service, and hospital visitation rights.\nDo you want to learn more?", gay_dictionary)
                    elif(message_text.lower() == "history of gay rights"):
                        send_quick_reply(sender_id, "For many years, homosexual relationships were considered capital offenses in the US with laws forbidding Sodomy or Buggery. One of the first gay rights groups in the US" +
                                                " was the Society for Human Rights established in Chicago in 1924. The major turning point of the gay rights movement was the 1969 Stonewall Riots where angry protestors rioted against police for" +
                                                " three days after a raid on a gay bar. In 2008, California ruled that its previous ban on same-sex marriage was unconstitutional and the Supreme Court ruled in 2015 that same-sex marriages were legal" +
                                                " nationwide. In addition, 'Don't Ask, Don't Tell' was repealed in 2010.\n\nDo you want to learn more?", gay_dictionary)
                            
                    else:
                        send_message(sender_id, "I'm sorry, I don't understand.\nType 'help' if you'd like assistance")

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
        
# send a generic response
def send_generic_temp(recipient_id, message_text, reply_dictionary):

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
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type" : "generic",
                    "elements": reply_dictionary
                }
            }
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

#initial dictionary
start_dictionary = [
            {"content_type":"text",
            "title":"Feminism",
            "payload":"start_fem"
            },
            {"content_type":"text",
            "title":"Racism",
            "payload":"start_race"
            },
            {"content_type":"text",
            "title":"Gay Rights",
            "payload":"start_gay"
            },
            {"content_type":"text",
            "title":"Trans Rights",
            "payload":"start_trans"
            }
]

#feminism dictionary
fem_dictionary = [
            {"content_type":"text",
            "title":"What is feminism?",
            "payload":"fem_definition"
            },
            {"content_type":"text",
            "title":"History of feminism",
            "payload":"fem_history"
            },
            {"content_type":"text",
             "title":"What feminism isn't",
             "payload":"not_feminism"
            }
]

#racism dictionary
race_dictionary = [
            {"content_type":"text",
            "title":"What is racism?",
            "payload":"racism_definition"
            },
            {"content_type":"text",
            "title":"History of racism",
            "payload":"racism_history"
            },
            {"content_type":"text",
             "title":"What racism isn't",
             "payload":"not_racism"
            }
]

#gay rights dictionary
gay_dictionary = [
            {"content_type":"text",
            "title":"What are gay rights",
            "payload":"gay_definition"
            },
            {"content_type":"text",
            "title":"History of gay rights",
            "payload":"gay_history"
            },
            {"content_type":"text",
             "title":"What gay rights aren't",
             "payload":"not_gay"
            }
]

#trans rights dictionary
trans_dictionary = [
            {"content_type":"text",
            "title":"What is trans?",
            "payload":"trans_definition"
            },
            {"content_type":"text",
            "title":"History of trans",
            "payload":"trans_history"
            },
            {"content_type":"text",
             "title":"What trans isn't",
             "payload":"not_trans"
            }
]

not_fem_dictionary = [
{
            "title":"Feminism isn't about hating men",
            "item_url":"http://everydayfeminism.com",
            "image_url":"http://2w6kxc22rrr9mabqt1mglgait6.wpengine.netdna-cdn.com/wp-content/uploads/2016/02/Man-offended-1024x580.jpg",
            "subtitle":"Feminism aims to help both men and women, by creating equality of both sexes.",
            "buttons":[
              {
                "type":"web_url",
                "url":"http://everydayfeminism.com/2015/06/feminism-isnt-about-hating-men/",
                "title":"Learn More"
              },
              {
                "type":"element_share"
              }
            ]
          }
]
