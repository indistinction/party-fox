# export AWS_PROFILE=chalice
# chalice deploy

import boto3
import stripe
import math
import uuid
import time
import secrets
import requests
import base64
from boto3.dynamodb.conditions import Key, Attr
from chalice import Chalice, Response, BadRequestError, NotFoundError, UnauthorizedError
from datetime import datetime, timedelta
import jinja2, os
import urllib.parse

prices = {
    "party": 60,
    "box1": 6,
    "box1": 6,
    "postage": 5
}

app = Chalice(app_name='backend')
app.api.cors = True
EmptySuccess = Response(body='',
                        status_code=204,
                        headers={'Content-Type': 'text/plain'})

dynamo = boto3.resource('dynamodb',
                        aws_access_key_id='REDACTED',
                        aws_secret_access_key='nothankyousir')
db = dynamo.Table('Party')

sns = boto3.client(
    "sns",
    aws_access_key_id="REDACTED",
    aws_secret_access_key="nothingtoseeherepleasemovealong",
    region_name="eu-west-1"
)

sns.set_sms_attributes(
    attributes={
        "DefaultSenderID": "Party",
        "DefaultSMSType": "Transactional"
    }
)

frontend = "https://nolongeronline"

stripe.api_key = "sk_live_TOPEFFINGSECRET"


def render(tpl_path, context):
    path, filename = os.path.split(tpl_path)
    return jinja2.Environment(loader=jinja2.FileSystemLoader(path or "./")).get_template(filename).render(context)


@app.route('/')
def index():
    return {'message': 'Not allowed.'}


@app.route('/slots')
def get_timeslots():
    date = (datetime.now()+timedelta(0)).strftime("%Y-%m-%d")
    date_list = {}
    response = db.query(
        IndexName='Switched-PKSK',
        KeyConditionExpression=Key('SK').eq('slot') & Key('PK').gt(date)
    )
    for item in response["Items"]:
        date_string = item["PK"].split("#")
        item_date = date_string[0]
        item_time = date_string[1]
        item_available = item["available"]
        if item_date in date_list:
            if item_time in date_list[item_date] and date_list[item_date][item_time] == False and item_available == True:
                date_list[item_date][item_time]=True
            else:
                date_list[item_date][item_time]=item_available
        else:
            date_list[item_date] = {item_time: item["available"]}

    return date_list


@app.route('/checkout', methods=["POST"])
def stripe_buy():

    data = app.current_request.json_body
    print(data)

    date_string = data["dateChosen"].split("T")[0]
    date = datetime.strptime(date_string, "%Y-%m-%d")


    # TODO check if slot is locked, if it is fail, if not then lock it

    boxCount = 0
    for guest in data["guests"]:
        if guest["box"]:
            boxCount += 1
    if data["kidBox"]:
        boxCount += 1

    items = [
        {"desc": f"Party online party at {data['timeslot']} on {date.strftime('%A %-d %B %Y')}", "price": prices["party"], "qty":1},
        {"desc": "Exclusive Party gift boxes", "price": prices["box1"], "qty": boxCount},
        {"desc": "Postage", "price": prices["postage"], "qty": boxCount},
    ]

    temp_id = str(uuid.uuid1())
    data['slot'] = f"{date_string}#{data['timeslot']}#1"  # The 1 at the end is the staff ID
    data['PK'] = temp_id
    data['SK'] = "pending"
    data['ttl'] = int(time.time()) + (7*24*60*60)  # Delete after 1 week
    data['receipt'] = {
        "party":prices["party"],
        "boxes":prices["box1"]*boxCount,
        "postage":prices["postage"]*boxCount
    }
    db.put_item(Item=data)

    total = 0.0
    line_items = []
    for item in items:
        line_items.append({
            'price_data': {
                'currency': 'gbp',
                'product_data': {
                    'name': item['desc'],
                },
                'unit_amount': math.ceil(float(item['price'])*100),
            },
            'quantity': int(item['qty']),
        })
        total += (float(item['qty']) * float(item['price']) * 100)

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=f"{frontend}/success",
        cancel_url=f"{frontend}/book",
        allow_promotion_codes=True,
        metadata={
            "temp_id": temp_id
        },
        payment_intent_data={'application_fee_amount': 200},
        stripe_account="acct_ofthecompany"
    )

    return {'id': session.id}


@app.route('/qz6wqtx1g75citom', methods=["POST"])
def stripe_webhook():
    eventdata = app.current_request.json_body
    event = stripe.Event.construct_from(
        eventdata, stripe.api_key
    )
    if event.type == 'checkout.session.completed':
        checkout_object = event.data.object
        temp_id = checkout_object.metadata["temp_id"]

        # Get original data
        response = db.get_item(
            Key={
                'PK': temp_id,
                'SK': 'pending'
            }
        )
        data = response['Item']
        slot = data['slot']
        del data['slot']
        del data['ttl']

        # Make unavailable
        db.update_item(
            Key={
                'PK': slot,
                'SK': "slot"
            },
            UpdateExpression='SET available = :val1',
            ExpressionAttributeValues={
                ':val1': False
            }
        )

        # Get email
        customer = stripe.Customer.retrieve(checkout_object.customer,
                                            stripe_account="acct_ofthecompany")

        # Create booking
        data['email'] = customer.email
        data['txn'] = checkout_object.payment_intent
        data['PK'] = slot
        data['SK'] = f"booking.{uuid.uuid1().hex}.{secrets.token_urlsafe(8)}"
        db.put_item(Item=data)

        # Create superstar record
        db.put_item(Item={
            'accessKey': "{:x}-{}".format(
                int(time.time()),
                secrets.token_urlsafe(24).replace('-', '').replace('_', '')
            ),
            'box': data['kidBox'],
            'kidName': data['guests'][0]['name'],
            'address': "",
            'isSuperstar': True,
            'notes': "",
            'PK': slot,
            'SK': "guest.0",
            'status': "0"  # 0: no address, 1: email sent, 2: text sent, 3: got an address
        })

        i = 0
        for guest in data['guests']:
            i += 1  # First one's the superstar and done already
            db.put_item(Item={
                'accessKey': "{:x}-{}".format(
                    int(time.time()),
                    secrets.token_urlsafe(27).replace('-', '').replace('_', '')
                ),
                'box': guest['box'],
                'kidName': guest['name'],
                'address': "",
                'isSuperstar': False,
                'superstarName': data['guests'][0]['name'],
                'notes': "",
                'PK': slot,
                'SK': f"guest.{i}",
                'email': "",
                'phone': "",
                'inviteSent': False,
                'status': "0"  # 0: no address, 1: email sent, 2: text sent, 3: got an address
            })

        print(f"Dynamo updated. Sending email to {customer.email}...")

        # Send email
        email = {
            "to": customer.email,
            "subject": "Party booking confirmation",
            "from": "info@party.co.uk",
            "html": render("chalicelib/confirm_email.html", {
                "url_link_data": base64.b64encode(f"{slot}_{data['SK']}".encode("utf-8")).decode("utf-8")
            })
        }

        # Confirm invite email will be url/invite/ g=base64.b64encode(slot_guest.{i}_accessKey)
        r = requests.post(
            "https://api.eu.mailgun.net/v3/mail.party.co.uk/messages",
            auth=("api", "key-mailgunkey"),
            data=email
        )
        print(r.text)

        return EmptySuccess
    else:
        raise BadRequestError("Unexpected event type.")


@app.route('/confirm/{party_id_b64}')
def get_info_for_confirm_page(party_id_b64):
    party_id_string = base64.b64decode(party_id_b64).decode("utf-8")
    party_id_list = party_id_string.split("_")
    slot = party_id_list[0]
    booking_sk = party_id_list[1]
    data = {}
    response = db.get_item(
        Key={
            'PK': slot,
            'SK': booking_sk
        }
    )

    # Yeah, that booking doesn't exist
    if 'Item' not in response:
        time.sleep(0.5)  # Brute force buster
        raise NotFoundError("Party record not found.")

    # If this exists then load data for guests
    data["party"] = response["Item"]
    response = db.query(
        KeyConditionExpression=Key('PK').eq(slot) & Key('SK').begins_with("guest.")
    )
    data["guests"] = response["Items"]
    return data


@app.route('/guest/{slot}/{guest}/{access_key}', methods=['POST'])
def update_guest_details_from_confirm_page(slot, guest, access_key):
    slot = urllib.parse.unquote(slot)
    response = db.get_item(
        Key={
            'PK': slot,
            'SK': guest
        }
    )

    # Yeah, that booking doesn't exist
    if 'Item' not in response:
        time.sleep(0.5)  # Brute force buster
        raise NotFoundError("Guest record not found.")

    guest_data = response["Item"]
    if access_key != guest_data["accessKey"]:
        time.sleep(0.5)  # Brute force buster
        raise UnauthorizedError("Incorrect guest access key.")
    del guest_data["accessKey"]  # Just to stop any 'accidental' overwriting

    req_data = app.current_request.json_body
    if "address" in req_data:
        req_data["address"] = req_data["address"].replace("\n", ", ")

    # 0: no address, 1: email sent, 2: text sent, 3: got an address
    if "status" in req_data:
        if "status" in guest_data["status"] == req_data["status"]:
            raise BadRequestError("this action had already been completed.")

        guest_link = "https://party.co.uk/confirm?g="+base64.b64encode(f"{slot}_{guest}_{access_key}")
        if req_data["status"] == "1":
            # Send email invite
            email = {
                "to": req_data["email"],
                "subject": f"Party Invitiation for {guest_data['kidName']}!",
                "html": render("chalicelib/invite_email.html", {guest_link: guest_link})
            }

            requests.post(
                "https://api.eu.mailgun.net/v3/mail.partyaround.co.uk/messages",
                auth=("api", "key-mailgunkey"),
                data=email
            )
            req_data["inviteEmailSentTs"] = int(time.time())
        elif req_data["status"] == "2":
            # Send text invite
            if req_data["mobile"][0] == "0":
                req_data["mobile"] = f"+44{req_data['mobile'][1:]}"
            sns.publish(
                PhoneNumber=req_data["mobile"],
                Message=f"{guest_data['kidName']} has been invited to a PartyAround virtual party! \
                For further information and to confirm attendance please click \
                {guest_link}"
            )
            req_data["inviteTextSentTs"] = int(time.time())

    # Update merge dicts into dynamodb
    update_expression = 'SET {}'.format(','.join(f'#{k}=:{k}' for k in req_data))
    expression_attribute_values = {f':{k}': v for k, v in req_data.items()}
    expression_attribute_names = {f'#{k}': k for k in req_data}
    response = db.update_item(
        Key={
            'PK': slot,
            'SK': guest
        },
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attribute_values,
        ExpressionAttributeNames=expression_attribute_names
    )
    return EmptySuccess

@app.route('/guestinfo/{guest_id_b64}', methods=['GET'])
def get_party_info_for_guestinfo_page(guest_id_b64):
    guest_id_string = base64.b64decode(guest_id_b64).decode("utf-8")
    guest_id_list = guest_id_string.split("_")

    data = {}
    response = db.get_item(
        Key={
            'PK': guest_id_list[0],
            'SK': guest_id_list[1]
        }
    )

    # Yeah, that booking doesn't exist
    if 'Item' not in response:
        time.sleep(0.5)  # Brute force buster
        raise NotFoundError("Party record not found.")

    data = response["Item"]

    if response['Item']['accessKey'] != guest_id_list[2]:
        time.sleep(0.5)  # Brute force buster
        raise UnauthorizedError("Invalid access key.")

    return data
