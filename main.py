from client import FtxClient
import os
from dotenv import load_dotenv
import numpy as np
import mailgun
import time

load_dotenv()
ftx_session = FtxClient(os.getenv('API_KEY'), os.getenv('API_SECRET'))

def get_market():
    return ftx_session.get_market(os.getenv('MARKET'))

def set_size(market):
    if os.getenv('SLIP_FROM') == 'INVESTMENT':
        return int(os.getenv('INVESTMENT')) / market['price']
    elif os.getenv('SLIP_FROM') == 'PRICE':
        return (int(os.getenv('INVESTMENT')) - int(os.getenv('INVESTMENT')) * float(os.getenv('SLIP'))) / market['price']

def set_price(size, market):
    if os.getenv('SLIP_FROM') == 'INVESTMENT':
        return round(int(os.getenv('INVESTMENT')) * float(os.getenv('SLIP')) + market['price'], 2)
    elif os.getenv('SLIP_FROM') == 'PRICE':
        return round(int(os.getenv('INVESTMENT')) / size, 2)

def place_order(price, size):
    return ftx_session.place_order(
        os.getenv('MARKET'),
        os.getenv('SIDE'),
        price,
        size,
        os.getenv('TYPE'),
        False,	# reduce_only
        False,	# ioc
        False,	# post_only
        None	# client_id
    )

def check_if_filled(id):
    filled = False
    start = time.time()

    while time.time() < start + 30:
        filled = ftx_session.is_filled(id)
        time.sleep(10)

    return filled

def send_mail(order_response, market, filled):
    stats = 'markkina: ' + str(order_response['market']) + ', kurssi: ' + str(order_response['price']) + ' (orig: ' + str(market['price']) + '), sijoitus: ' + os.getenv('INVESTMENT') + ', osuus: ' + str(order_response['size'])

    if filled == True:
        mailgun.send_simple_message('Uusi ' + os.getenv('SIDE') + ' onnistui', stats)
    else:
        mailgun.send_simple_message('Uusi ' + os.getenv('SIDE') + ' ei onnistunut heti', stats)

def print_result(order_response, filled):
    if filled == True:
        print('[SUCCESS] ' + str(order_response))
    else:
        print('[FAIL] ' + str(order_response))

def main():
    market = get_market()
    size = set_size(market)
    price = set_price(size, market)
    order_response = place_order(price, size)
    filled = check_if_filled(order_response['id'])
    send_mail(order_response, market, filled)
    print_result(order_response, filled)


if __name__ == "__main__":
    main()