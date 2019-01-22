# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import os
import random
import logging

from city58_spy.libs.proxy import RedisPool
from city58_spy.libs.tools import verify_address_usability
from city58_spy import settings


logger = logging.getLogger(__name__)


class MyUADownLoaderMiddleware(object):
    """自定义user-agent下载中间件
    处理user-agent的随机设置以减小被ban的几率
    """

    # user-agent池
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    ]

    def process_request(self, request, spider):
        request.headers['User-Agent'] = random.choice(self.user_agent_list)


class MyRedisProxyDownLoaderMiddleware(object):
    """自定义代理地址下载中间件
    提供代理ip的设置以减小被ban的几率
    """

    # 动态代理地址池
    pool = RedisPool(settings.PROXY_REDIS_KEY,
                     settings.PROXY_REDIS_HOST,
                     settings.PROXY_REDIS_PORT)

    def process_request(self, request, spider):
        # 判断协议类型
        protocol = request.url.split(':')[0].strip()

        if protocol == 'http':
            # 获取一个动态代理地址
            random_address = self.pool.get_random_http_address()
        elif protocol == 'https':
            # 获取一个动态代理地址
            random_address = self.pool.get_random_https_address()
        else:
            raise ValueError(f'请求对象的url协议类型错误: {request.url}')

        if random_address:
            # 如果当前数据库中有可用的地址，则设置代理地址格式
            protocol, ip, port = random_address.get('protocol'), random_address.get('ip'), random_address.get('port')
            # 判断地址可用性
            if verify_address_usability(protocol, ip, port):
                proxy_address = ''.join([ip, ':', port])
                logger.info(f'获取的随机 {protocol} 地址是: {random_address}')
                # 增加到请求对象中
                request.meta['proxy'] = proxy_address
            else:
                logger.info(f'代理地址 {random_address} 不可用，使用本机地址')
        else:
            # 否则只是记录日志
            logger.info('未获取到随机地址，使用本机地址')


class MyAllowHttpForbiddenDownLoaderMiddleware(object):
    """自定义http响应code的下载处理中间件"""

    # 允许spider处理403状态的响应对象
    def process_request(self, request, spider):
        request.meta['handle_httpstatus_list'] = [403]


# 定义spider中间件，处理服务器拒绝服务的响应
class MyCatchHttpForbiddenSpiderMiddleware(object):
    total_count = 0
    forbidden_count = 0
    success_count = 0

    # 创建文件，存放被拒绝服务的url信息
    forbidden_urls_root = os.path.dirname(__file__)
    forbidden_urls_path = settings.FORBIDDEN_FILE_PATH
    forbidden_urls_filename = os.path.join(forbidden_urls_root, forbidden_urls_path)
    file = open(forbidden_urls_filename, 'w', encoding='utf-8')

    def process_spider_input(self, response, spider):
        self.total_count += 1
        status_code = response.status

        if status_code == 403 or 'firewall' in response.url:
            # 此请求被服务器禁止，需要记录以便后续再次请求
            self.file.write(response.request.url + '\n')
            self.forbidden_count += 1

            raise PermissionError()
        else:
            self.success_count += 1

    def process_spider_exception(self, response, exception, spider):
        if isinstance(exception, PermissionError):
            logger.info(
            f'''
            此http请求被服务器拒绝服务
                status:{response.status}
                url:{response.url}
            '''
            )
            return []

    def __del__(self):
        # 关闭文件资源
        self.file.close()
        # 负责展示工作数据
        logger.info(
            f'''
            =======下载量统计========
            目标下载url数据量: {self.total_count}
            成功量: {self.success_count}
            失败量: {self.forbidden_count}
            成功率: {self.success_count * 100 // self.total_count if self.total_count else 0}%
            '''
        )
