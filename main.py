#!/usr/bin/env python

# Please use 'pip install requests' if package is not installed
import email.utils
import requests
import smtplib
from email.mime.text import MIMEText

# You can replace your zip code in the url
BASE_URL = 'http://www.apple.com/shop/retail/pickup-message?parts.0=MN{}LL%2FA&location=94404&little=true&cppart=ATT%2FUS'
JETBLACK_ONLY = True

def main(jetblack_only=True):
    if jetblack_only:
        part_no_dict = {'jetblack': 572}
    else:
        # Only contains iphone 128GB 7 plus
        part_no_dict = {
            'jetblack': 572,
            'black': 522,
            'silver': 532,
            'gold': 552,
            'rose_gold': 562,
        }

    final_result = []
    for color, part_no in part_no_dict.items():
        store_list = query_phone(part_no)
        result_by_color = process_stores(store_list)
        final_result.extend(result_by_color)

    if final_result:
        send_email(final_result)


def query_phone(part_no):
    r = requests.get(BASE_URL.format(part_no))
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
                result.append((store_name, device_name, availability))

    return result


def send_email(result):
    msg_string = ''
    for store_name, device_name, availability in result:
        msg_string += '{} {} {} \n'.format(store_name, device_name, availability)
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
    main(jetblack_only=JETBLACK_ONLY)


'''
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
