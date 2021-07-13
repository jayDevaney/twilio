import os
from twilio.rest import Client


# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)

message = client.messages \
    .create(
        body="Thanks for your interest in our products and services.",
        from_='+12055126263',
        to='+34628044418', 
        status_callback='http://6e255c316017.ngrok.io/MessageStatus'
    )
    
print(message.sid)

# +34654953828, status_callback='http://6e255c316017.ngrok.io/MessageStatus'
call = client.calls.create(
        twiml='<Response><Say>Thanks for your interest in our products and services.</Say></Response>',
        to='+34654953828',
        from_='+12055126263'             
        )

print(call.sid)

