# -*- coding: utf-8 -*-
# 'author':'zlw'


# redis服务器信息
redis_host = '127.0.0.1'
redis_port = 6379
# 数据库索引
redis_key = 'proxy_address_list'

# 每次代理爬取之间的间隔(秒)
time_gap = 15

# 最大代理地址数量
max_proxy_address = 30

# 屏幕日志格式
stream_format = '[%(levelname)s]  时间:%(asctime)s  内容:%(message)s'

# selenium执行web浏览器的驱动路径
web_name = 'firefox'
# web_name = 'chrome'
web_driver_path = 'web_drivers/firefox/geckodriver.exe'
