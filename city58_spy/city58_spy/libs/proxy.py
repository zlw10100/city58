# -*- coding: utf-8 -*-
# 'author':'zlw'


"""
代理地址池模块
代理地址对象的结构定义:
    address = {
    'protocol': 'http/https',
    'ip': '1.1.1.1',
    'port': 8080,
    }
"""


import redis
import random
import json
import logging

from abc import ABCMeta, abstractmethod


logger = logging.getLogger(__name__)


class AbstractPool(object, metaclass=ABCMeta):
    @abstractmethod
    def get_random_http_address(self):
        pass

    @abstractmethod
    def get_random_https_address(self):
        pass

    @abstractmethod
    def get_address_list(self):
        pass


class RedisPool(AbstractPool):
    def __init__(self, redis_key, redis_host, redis_port, **kw):
        # redis数据库索引名称
        self.redis_key = redis_key
        # 数据库链接对象
        self.db = redis.Redis(host=redis_host, port=redis_port, **kw)

    def get_random_http_address(self):
        # 从数据库获取代理地址,可能会出现没有可用地址的情况
        try:
            random_address = random.choice(self.get_address_list('http'))
        except IndexError:
            logger.warning('当前数据库中没有可用的http代理地址')
            random_address = None

        return random_address

    def get_random_https_address(self):
        # 从数据库获取代理地址,可能会出现没有可用地址的情况
        try:
            random_address = random.choice(self.get_address_list('https'))
        except IndexError:
            logger.warning('当前数据库中没有可用的https代理地址')
            random_address = None

        return random_address

    def get_address_list(self, protocol=None):
        """获取数据库中所有地址"""

        # 处理协议参数错误输入
        if protocol and protocol not in ('http', 'https'):
            raise ValueError(f'你申请的地址协议不正确: {protocol}')

        # 获取所有的地址列表
        address_list = [json.loads(address) for address in self.db.smembers(self.redis_key)]
        if address_list and protocol:
            # 处理协议类别
            # 根据输入的协议参数返回指定的地址列表
            address_list = [address for address in address_list if address.get('protocol') == protocol]

        return address_list
