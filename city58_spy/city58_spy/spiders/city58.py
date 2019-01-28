# -*- coding: utf-8 -*-


import logging
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from bs4 import BeautifulSoup

from city58_spy.items import City58SpyItem
from scrapy_redis.spiders import RedisCrawlSpider


logger = logging.getLogger(__name__)


class City58Spider(RedisCrawlSpider):
    name = 'city58'

    # 首页租房页面
    # 'https://hz.58.com/chuzu/pn1/',

    redis_key = 'city58_zufang_list'

    # 每一页租房概览页面模型
    page_pattern = 'https://hz.58.com/chuzu/pn\d+/'
    page_link = LinkExtractor(allow=page_pattern)

    # 规则映射器
    rules = [
        # 对每一页租房概览页面执行爬取动作，获取详细的房屋地址并发起请求
        Rule(page_link, callback='parse_page', follow=False),
    ]

    def parse_page(self, response):
        logger.info(f'当前租房概览信息页面是: {response}')

        # 获取每一张租房页面的房屋链接列表
        # 房屋详情url存在于a.strongbox的href中
        soup = BeautifulSoup(response.text, 'html.parser')
        house_link_list = soup.find_all('a', class_='strongbox')

        logger.info(f'在 {response.url} 中找到 {len(house_link_list)} 条房屋详情url')

        # 获取每一条房屋详情url
        for house_link in house_link_list:
            item = City58SpyItem()
            # 完善结构化数据
            url = 'https:' + house_link['href'] if hasattr(house_link, 'href') else ''
            item['url'] = url

            # 对房屋详情页面发起请求，并传递结构化数据对象以便继续完善
            if url:
                detail_request = scrapy.Request(url=url, callback=self.parse_detail)
                detail_request.meta['item'] = item
                yield detail_request

    def parse_detail(self, response):
        """解析房屋详情页面"""
        logger.info(f'当前处理房屋详情页面是: {response}')

        # 爬取房屋详情页面的房屋详情数据
        item = response.meta['item']
        soup = BeautifulSoup(response.text, 'html.parser')

        # 房屋名称
        item['title'] = self.parse_detail_title(soup)

        # 房屋详情页面url
        item['url'] = response.url

        # 房屋更新信息
        item['update_info'] = self.parse_detail_update_info(soup)

        # 房屋描述信息
        pay_money, pay_way, basic_info = self.parse_detail_desc(soup)
        item['pay_money'] = pay_money
        item['pay_way'] = pay_way
        item['basic_info'] = basic_info

        # 房屋联系人信息
        contact_name, contact_tel, config_info = self.parse_detail_config_info(soup)
        item['contact_name'] = contact_name
        item['contact_tel'] = contact_tel
        item['config_info'] = config_info

        # 房屋图集
        item['img_url_list'] = self.parse_detail_img_url_list(soup)

        # 小区信息
        district_name, district_addr, district_info = self.parse_detail_district(soup)
        item['district_name'] = district_name
        item['district_addr'] = district_addr
        item['district_info'] = district_info

        yield item

    def parse_detail_title(self, soup):
        # 房屋名称
        title_div = soup.find('div', class_='house-title')
        title = title_div.find('h1').text.strip()

        return title

    def parse_detail_update_info(self, soup):
        # 房屋更新信息
        update_info_p = soup.find('p', class_='house-update-info')
        update_info = update_info_p.text.strip()

        return update_info

    def parse_detail_desc(self, soup):
        # 房屋描述信息
        desc_div = soup.find('div', class_='house-desc-item')
        # 支付方式
        pay_way_div = desc_div.find('div', class_='house-pay-way')
        pay_money = pay_way_div.find('b', class_='strongbox').text.strip()
        pay_way = pay_way_div.find('span', class_='c_333').text.strip()
        # 基本信息
        basic_info_ul = desc_div.find('ul')
        # 只获取前3个基本信息
        basic_info = ''
        important_li_list = basic_info_ul.find_all('li')[:3]
        for important_li in important_li_list:
            important_text = important_li.text
            if important_text:
                basic_info += important_text.strip()

        return pay_money, pay_way, basic_info

    def parse_detail_config_info(self, soup):
        # 房屋联系信息
        # 联系人
        contact_name_ele = soup.find('p', class_='agent-name')
        contact_name = contact_name_ele.text.strip() if contact_name_ele else ''
        # 联系电话
        contact_tel_ele = soup.find('p', class_='phone-num')
        contact_tel = contact_tel_ele.text.strip() if contact_tel_ele else ''

        # 房屋配置信息
        config_ul = soup.find('ul', class_='house-disposal')
        config_info = config_ul.text.strip() if config_ul else ''

        return contact_name, contact_tel, config_info

    def parse_detail_img_url_list(self, soup):
        # 房屋图集
        img_ul = soup.find('ul', id='housePicList')
        img_url_list = []
        for img in img_ul.find_all('img'):
            img_url = 'https:' + img['lazy_src'] if hasattr(img, 'lazy_src') else ''
            img_url_list.append(img_url)

        return img_url_list

    def parse_detail_district(self, soup):
        # 小区基本信息
        district_div = soup.find('div', id='district-wrap')
        # 小区名称
        district_name = district_div.find('p', class_='title').text.strip() if district_div else ''
        # 小区地址
        district_addr = district_div.find('p', class_='addr').text.strip() if district_div else ''

        # 小区详细信息
        district_info_ul = soup.find('ul', class_='district-info-list')
        district_info = district_info_ul.text.strip() if district_info_ul else ''

        return district_name, district_addr, district_info
