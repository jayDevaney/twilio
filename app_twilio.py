from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from twilio.twiml.voice_response import VoiceResponse
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from datetime import datetime
import os
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Customers(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    customer = db.Column(db.String(200), unique=True)
    phone = db.Column(db.String(200))
    method = db.Column(db.String(10))
    language = db.Column(db.String(10))

    def __init__(self, customer, phone, method, language):
        self.customer = customer
        self.phone = phone
        self.method = method
        self.language = language

class Responses(db.Model):
    __tablename__ = 'responses'
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(200))
    method = db.Column(db.String(10))
    timestamp = db.Column('timestamp', db.TIMESTAMP(timezone=False), nullable=False, default=datetime.now())

    def __init__(self, phone, method, timestamp):
        self.phone = phone
        self.method = method
        self.timestamp = timestamp
       
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/new')
def new():
    return render_template('newcustomer.html')


@app.route('/submit', methods=['POST'])
def submit():
    phone = request.form['phone']
    campaign = request.form['campaign']
    method = request.form['method']
    comments = request.form['comments']

    # Find your Account SID and Auth Token at twilio.com/console
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)

    """ TODO: Error Handler """
    
    if len(phone) > 0:
        try:
            phone_number = client.lookups \
                .v1 \
                .phone_numbers(phone) \
                .fetch(country_code='ES')
        except TwilioRestException as e:            
            return render_template('index.html', message= 'Not a Spanish number:  ' + e.msg)
        else:
            pass
    else:
        return render_template('index.html', message= 'Please enter a valid number:  ')
        
    if method == '1':
        try:
            message = client.messages \
                .create(
                    body=comments,
                    from_='+12055126263',
                    to=phone,
                    status_callback='http://27ccb13a7c48.ngrok.io/MessageStatus'
                )
        except TwilioRestException as e:            
            return render_template('index.html', message= 'Error:  ' + e.msg) 
        else:
            print(message.sid)
            return render_template('success.html', message=phone + '  ' + message.sid)

    if method == '2':
        try:
            call = client.calls.create(
                twiml='<Response><Say>' + comments + '</Say></Response>',
                to=phone,
                from_='+12055126263',
                status_callback='http://27ccb13a7c48.ngrok.io/MessageStatus'
            )
            print(call.sid)
        except TwilioRestException as e:            
            return render_template('index.html', message= 'Error:  ' + e.msg) 
        else:
            return render_template('success.html', message=phone + '  ' + call.sid + '  ' + method)

    if method == '4':
        
        users = db.session.query(Customers)
        for user in users:
            if user.method == '1':
                message = client.messages \
                    .create(
                        body=comments,
                        from_='+12055126263',
                        to=user.phone,
                        status_callback='http://27ccb13a7c48.ngrok.io/MessageStatus'
                    )
                    
            if user.method == '2':            
                call = client.calls.create(
                    twiml='<Response><Say>' + comments + '</Say></Response>',
                    to=user.phone,
                    from_='+12055126263',
                    status_callback='http://27ccb13a7c48.ngrok.io/MessageStatus'
                )
                print(call.sid)
        return render_template('success.html')
           
"""Twilio Code""" 
@app.route("/answer", methods=['GET', 'POST'])
def answer_call():
    """Respond to incoming phone calls with a brief message."""
    # Start TwiML response
    resp = VoiceResponse()
    resp.say("Thank you for your interest in our products and services.", voice='alice')

    method = '2: Voice'
    from_resp = request.values.get('From', None)
    
    data = Responses(from_resp, method, datetime.now())
    db.session.add(data)
    db.session.commit() 

    return str(resp)

@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    """Respond to incoming SMS with a simple text message."""
    method = '1: SMS'
    body = request.values.get('Body', None)
    to_resp = request.values.get('To', None)
    from_resp = request.values.get('From', None)

    data = Responses(from_resp, method, datetime.now())
    db.session.add(data)
    db.session.commit()    

    print(from_resp)
    # Start our TwiML response
    resp = MessagingResponse()
    # Add a message
    resp.message("Thank you for your interest in our products and services!")

    return str(resp)

@app.route("/MessageStatus", methods=['POST'])
def incoming_sms():
    message_sid = request.values.get('MessageSid', None)
    message_status = request.values.get('MessageStatus', None)
    logging.info('SID: {}, Status: {}'.format(message_sid, message_status))
    return ('', 204)


@app.route('/add', methods=['POST'])
def add():
    if request.method == 'POST':
        customer = request.form['customer']
        phone = request.form['phone']
        language = request.form['language']
        method = request.form['method']
        # print(customer, dealer, rating, comments)
        if customer == '' or phone == '':
            return render_template('newcustomer.html', message='Please enter required fields')
        if db.session.query(Customers).filter(Customers.customer == customer).count() == 0:
            data = Customers(customer, phone, method, language)
            db.session.add(data)
            db.session.commit()
            return render_template('success.html')
        return render_template('newcustomer.html', message='You already have an account.')

if __name__ == "__main__":
    app.run()
