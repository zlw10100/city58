# -*- coding: utf-8 -*-
# 'author':'zlw'


"""
控制模块
此模块负责验证数据库中的代理地址的可用性。


爬虫程序一共通过两个生成器函数协作实现。
此模块维持其中一个协程，负责接收爬虫对象发送的下载成功通知，
并根据通知处理redis数据库中的地址，并发送下一次任务给爬虫对象。
"""


import json

import settings
from tools import verify_address_usability


class ProxyController(object):
    """代理控制器"""

    def __init__(self, db, redis_key):
        # 数据库对象
        self.db = db
        # redis数据库索引
        self.redis_key = redis_key
        # 最大代理地址数量
        self.max_proxy_address = settings.max_proxy_address

    # 启动控制器，主接口
    def proxy_control(self):
        yield 'proxy-control ready!'

        while True:
            # 从redis数据库中获取数据
            values = self.db.smembers(self.redis_key)

            if not values:
                # 如果没有数据，则发出任务指令，让爬虫对象执行任务
                target_address_count = self.max_proxy_address
                yield target_address_count
            else:
                # 如果有数据，清空redis数据库中的地址
                self.db.srem(self.redis_key, *values)

                # 转换地址列表
                address_list = [json.loads(address) for address in values]
                # 遍历并测试可用性
                usable_address_list = self.verify_address_list(address_list)

                # 如果没有任一可用地址，则发出指令，让爬虫执行任务
                if not usable_address_list:
                    target_address_count = self.max_proxy_address
                    yield target_address_count
                else:
                    # 重新写入可用地址列表
                    values = [json.dumps(address) for address in usable_address_list]
                    self.db.sadd(self.redis_key, *values)

                    # 判断还有多少地址数量的空缺，发出任务指令，让爬虫对象执行任务
                    target_address_count = self.max_proxy_address - len(usable_address_list)
                    if target_address_count < 0:
                        target_address_count = 0
                    yield target_address_count

    def verify_address_list(self, address_list):
        """地址列表验证函数"""

        usable_address_list = []

        for address in address_list:
            protocol = address.get('protocol')
            ip = address.get('ip')
            port = address.get('port')
            if verify_address_usability(protocol, ip, port):
                usable_address_list.append(address)

        # 返回可用地址列表
        return usable_address_list
