# Python Flask Twilio Communications App

> Python Flask app that uses the Twilio API to send outbound calls and sms messages.Outbound calls and messages can be inititiated from the form in index.html. Messages and calls can be initiated individually or in bulk via database lookup. 
> The application uses Twilio webhook to listen for incoming calls and sms messages to my twilio phone number. Incoming communications are logged in the PG database.
> The app provides a simple html form to add resgistered users with twilio validated numebers to a PostgreSQL database. nstances of inbound calls and messages are stored in PostgreSQL database.

# Install dependencies
pipenv shell
pipenv install


# Serve on localhost:5000
python app_twilio.py
```




