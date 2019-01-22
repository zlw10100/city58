# -*- coding: utf-8 -*-
# 'author':'zlw'


"""
程序主入口
"""


import time
import redis
import settings

from src.spider import ProxySpider
from src.controller import ProxyController
from log import logger


def main():
    # 数据库基本信息
    db = redis.Redis(host=settings.redis_host, port=settings.redis_port)

    # 实例化爬虫对象
    spider = ProxySpider(db, settings.redis_key)
    crawl_job = spider.crawl_address()
    crawl_msg = crawl_job.send(None)
    logger.info(crawl_msg)

    # 实例化控制器对象
    controller = ProxyController(db, settings.redis_key)
    control_job = controller.proxy_control()
    control_msg = control_job.send(None)
    logger.info(control_msg)

    # 主循环
    while True:
        # 执行控制操作
        target_address_count = control_job.send('any words')
        logger.info(f'任务需求：需要爬取目标代理地址数量是: {target_address_count}')

        # 执行爬取操作
        crawl_result = crawl_job.send(target_address_count)
        logger.info(f'任务反馈：{crawl_result}\n')

        # 间隔
        time.sleep(settings.time_gap)


if __name__ == '__main__':
    main()
