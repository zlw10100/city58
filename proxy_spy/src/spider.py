# -*- coding: utf-8 -*-
# 'author':'zlw'


"""
爬虫模块
此爬虫负责向公开代理地址页面爬取地址信息并保存到数据库中。

爬虫程序一共通过两个生成器函数协作实现。
此模式维持其中一个协程，负责接收控制器对象发送的下载任务,
并根据任务需求爬取代理地址保存到redis数据库。
"""


import json
import time

from selenium import webdriver
from bs4 import BeautifulSoup

import settings
from tools import verify_address_usability
from log import logger


class SeleniumWeb(object):
    # 使用selenium下载页面
    web_map = {
        'firefox': webdriver.Firefox,
        'chrome': webdriver.Chrome,
    }
    web_cls = web_map.get(settings.web_name)

    def __init__(self):
        self.bro = self.web_cls(executable_path=settings.web_driver_path)

    def download(self, url):
        self.bro.get(url)
        time.sleep(2)
        html = self.bro.page_source
        self.bro.quit()

        return html


class ProxySpider(object):
    # 公开代理地址所在页面
    url = 'http://www.goubanjia.com/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:61.0) Gecko/20100101 Firefox/61.0',
    }

    # 下载错误次数计数
    error_count = 0

    def __init__(self, db, redis_key):
        # 数据库对象
        self.db = db
        # redis数据库索引
        self.redis_key = redis_key

    # 启动爬取，主接口
    def crawl_address(self):
        # 爬取结果
        crawl_result = 'proxy-spider ready!'

        while True:
            # 无限循环
            target_address_count = yield crawl_result

            # 如果没有目标数量，直接返回
            if not target_address_count:
                crawl_result = f'任务数量为 {target_address_count} ，跳过本次爬取任务执行'
            else:
                try:
                    html = self._crawl()
                except Exception as why:
                    # 发生爬取错误
                    self.error_count += 1
                    crawl_result = f'爬取 {self.url} 发生错误，原因是: {why}，错误次数: {self.error_count}'
                else:
                    # 正确获取
                    address_list = self._parse(html, target_address_count)
                    get_address_count = len(address_list)
                    # 保存
                    self._save(address_list)
                    # 返回结果
                    crawl_result = f'完成代理页面爬取，获取到{get_address_count} 个地址'

    def _crawl(self):
        """爬取函数"""

        # 使用selenium处理页面下载
        bro = SeleniumWeb()
        html = bro.download(self.url)
        logger.info(f'指定公开代理页面下载成功: {self.url}')

        return html

    def _parse(self, html, target_address_count):
        # 美丽汤对象
        soup = BeautifulSoup(html, 'html.parser')
        ip_table = soup.find('table')
        # 获取代理地址列表
        ip_tr_list = ip_table.find('tbody').find_all('tr')

        # 遍历获取代理地址
        items = []
        for ip_tr in ip_tr_list:
            ip_td_list = ip_tr.find_all('td')
            if len(ip_td_list) < 3:
                continue
            # 地址
            address_td = ip_td_list[0]
            # 协议
            protocol_td = ip_td_list[2]
            # 端口
            port_span = address_td.find('span', class_='port')

            # 进一步处理地址格式
            result = address_td.find_all(style=True)
            address = ''
            for ele in result:
                address += ele.text.strip()

            # 协议，ip，port
            protocol = protocol_td.text.strip()
            port = port_span.text.strip()

            # 封装成结构化对象
            item = dict()
            item['protocol'] = protocol
            item['ip'] = address
            item['port'] = port
            items.append(item)
        logger.info(f'解析页面成功,获取代理地址量: {len(items)}')

        if len(items) > target_address_count:
            # 截取指定长度的地址列表
            items = items[0: target_address_count]
        return items

    def _save(self, address_list):
        if address_list:
            address_list = [json.dumps(address) for address in address_list]
            self.db.sadd(self.redis_key, *address_list)
            logger.info(f'数据保存成功，新增代理地址量: {len(address_list)}')
