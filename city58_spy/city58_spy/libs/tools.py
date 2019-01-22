# -*- coding: utf-8 -*-
# 'author':'zlw'

import requests

test_url = 'https://www.sogo.com/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:61.0) Gecko/20100101 Firefox/61.0',
}


def verify_address_usability(protocol, ip, port):
    proxy_address = ''.join([protocol, '://', ip, ':', port])
    proxies = {
        protocol: proxy_address,
    }

    ok = False
    try:
        res = requests.get(test_url, headers=headers, proxies=proxies)
        if res.status_code == 200:
            ok = True
    except:
        pass

    return ok
