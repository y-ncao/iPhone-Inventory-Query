#!/usr/bin/env python

# Please use 'pip install requests' if package is not installed
import email.utils
import requests
import smtplib
from email.mime.text import MIMEText

# You can replace your zip code in the url
ZIP_CODE = '94404'
BASE_URL = 'http://www.apple.com/shop/retail/pickup-message?parts.0=MN{}LL%2FA&location={}'
BASE_URL = 'http://www.apple.com/shop/retail/pickup-message?parts.0={}%2FA&location={}'
AIRPOD_URL = 'http://www.apple.com/shop/retail/pickup-message?parts.0=MMEF2AM%2FA&location=94404'

# Only contains iphone 128GB 7 plus
PART_NO_DICT = {
    'jetblack': 'MN572LL',
    'black': 'MN522LL',
    'silver': 'MN532LL',
    'gold': 'MN552LL',
    'rose_gold': 'MN562LL',
    'airpod': 'MMEF2AM',
}

def main():
    final_result = []
    for part_name, part_no in PART_NO_DICT.items():
        store_list = query_item(part_no)
        result_by_color = process_stores(store_list)
        final_result.extend(result_by_color)

    if final_result:
        send_email(final_result)
    print(format_msg(final_result))

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

def format_msg(result):
    msg_string = ''
    for store_name, device_name, availability in result:
        msg_string += '{: <40}{: <20}{: <10}\n'.format(device_name, store_name, availability)
    return msg_string

def send_email(result):
    msg = format_msg(result)
    msg = MIMEText(msg_string)
    msg['To'] = email.utils.formataddr(('Recipient', 'cyandterry@gmail.com'))
    msg['From'] = email.utils.formataddr(('Author', 'cyandterry@gmail.com'))
    msg['Subject'] = 'Go and Purchase your Shiny iPhone!'

    # Don't try my password, it's invalid
    username = 'cyandterry@gmail.com'
    password = '123456'
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username, password)
    server.sendmail('cyandterry@gmail.com', 'cyandterry@gmail.com', msg.as_string())
    server.quit()

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
