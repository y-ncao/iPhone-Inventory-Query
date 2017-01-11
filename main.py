#!/usr/bin/env python

# Please use 'pip install requests' if package is not installed
import difflib
import email.utils
import requests
import smtplib
from ConfigParser import SafeConfigParser
from email.mime.text import MIMEText
from twilio.rest import TwilioRestClient

config_parser = SafeConfigParser()
config_parser.read('config')


TWILIO_CONFIG = dict(
    account_sid = config_parser.get('Twilio', 'account_sid'),
    auth_token = config_parser.get('Twilio', 'auth_token'),
    twilio_phone_number = config_parser.get('Twilio', 'twilio_phone_number'),
    receipient_phone_number = config_parser.get('Twilio', 'receipient_phone_number'),
)
EMAIL_CONFIG = dict(
    username = config_parser.get('Gmail', 'username'),
    password = config_parser.get('Gmail', 'password'),
)

# You can replace your zip code in the url
ZIP_CODE = '94404'
BASE_URL = 'http://www.apple.com/shop/retail/pickup-message?parts.0=MN{}LL%2FA&location={}'
BASE_URL = 'http://www.apple.com/shop/retail/pickup-message?parts.0={}%2FA&location={}'
AIRPOD_URL = 'http://www.apple.com/shop/retail/pickup-message?parts.0=MMEF2AM%2FA&location=94404'

# Only contains iphone 128GB 7 plus
PART_NO_DICT = {
    'airpod': 'MMEF2AM',
}

def main():
    final_result = []
    for part_name, part_no in PART_NO_DICT.items():
        store_list = query_item(part_no)
        result_by_color = process_stores(store_list)
        final_result.extend(result_by_color)

    new_data = parse_result(final_result)

    try:
        with open('data.txt', 'r') as f:
            old_data = f.readlines()
    except IOError:
        old_data = []

    msg_string = ''
    for line in difflib.unified_diff(old_data, new_data, fromfile='old', tofile='new', lineterm=''):
        msg_string += line

    if msg_string:
        sms_sid = send_sms()
        send_email(msg_string + '\n' + 'sms sid: ' + sms_sid)
        print(msg_string)

        with open('data.txt', 'w') as f:
            old_data = f.writelines(new_data)

def query_item(part_no):
    r = requests.get(BASE_URL.format(part_no, ZIP_CODE))
    response = r.json()
    return response['body']['stores']

def process_stores(store_list):
    result = []
    for store in store_list:
        store_name = store['storeName'].encode('utf-8')
        zip_code = store['address']['postalCode'].encode('utf-8')
        parts = store['partsAvailability']
        for part_name, part_info in parts.items():
            availability = part_info['pickupSearchQuote'].encode('utf-8')
            device_name = part_info['storePickupProductTitle'].encode('utf-8')
            if 'Available' in availability:
                result.append((store_name, device_name, availability.replace('<br/>', ' ')))

    return result

def parse_result(result):
    parsed_result = []
    for store_name, device_name, availability in result:
        parsed_result.append('{: <40}{: <20}{: <10}\n'.format(device_name, store_name, availability))
    return parsed_result

def send_email(msg_string):
    msg = MIMEText(msg_string)
    msg['To'] = email.utils.formataddr(('Recipient', EMAIL_CONFIG['username']))
    msg['From'] = email.utils.formataddr(('Yan Cao', EMAIL_CONFIG['username']))
    msg['Subject'] = 'Go and Purchase!'

    # Don't try my password, it's invalid
    username = EMAIL_CONFIG['username']
    password = EMAIL_CONFIG['password']
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username, password)
    server.sendmail(EMAIL_CONFIG['username'], EMAIL_CONFIG['username'], msg.as_string())
    server.quit()

def send_sms():
    client = TwilioRestClient(TWILIO_CONFIG['account_sid'], TWILIO_CONFIG['auth_token'])
    message = client.messages.create(
        body="There's change in Airpod stock. Please check your email for more information.",
        to=TWILIO_CONFIG['receipient_phone_number'],
        from_=TWILIO_CONFIG['twilio_phone_number'],
    )
    return message.sid

if __name__ == '__main__':
    main()


'''
# Airpod
http://www.apple.com/shop/retail/pickup-message?parts.0=MMEF2AM%2FA&location=94404

# Jetblack
http://www.apple.com/shop/retail/pickup-message?parts.0=MN572LL%2FA&location=94404&little=true&cppart=ATT%2FUS
parts.0:MN572LL/A
location:94404
little:true
cppart:ATT/US

# Black
http://www.apple.com/shop/retail/pickup-message?parts.0=MN522LL%2FA&location=94404&little=true&cppart=ATT%2FUS
parts.0:MN522LL/A
location:94404
little:true
cppart:ATT/US

# Silver
http://www.apple.com/shop/retail/pickup-message?parts.0=MN532LL%2FA&location=94404&little=true&cppart=ATT%2FUS
parts.0:MN532LL/A
location:94404
little:true
cppart:ATT/US

# Gold
http://www.apple.com/shop/retail/pickup-message?parts.0=MN552LL%2FA&location=94404&little=true&cppart=ATT%2FUS
parts.0:MN552LL/A
location:94404
little:true
cppart:ATT/US

# Rose gold
http://www.apple.com/shop/retail/pickup-message?parts.0=MN562LL%2FA&location=94404&little=true&cppart=ATT%2FUS
parts.0:MN562LL/A
location:94404
little:true
cppart:ATT/US
'''
