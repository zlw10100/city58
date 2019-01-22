# -*- coding: utf-8 -*-
# 'author':'zlw'


import logging

import settings


def build_stream_handler():
    # 屏幕输出格式
    stream_format = settings.stream_format
    # 屏幕输出格式对象
    stream_formatter = logging.Formatter(stream_format)
    # 屏幕输出处理对象
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(stream_formatter)

    return stream_handler


def create_logger(name):
    # 日志对象
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 绑定日志处理对象
    stream_handler = build_stream_handler()
    logger.addHandler(stream_handler)

    return logger


# 创建日志对象
logger_name = 'city58_logger'
logger = create_logger(logger_name)
