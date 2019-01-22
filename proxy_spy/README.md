代理地址爬取程序

此程序将会爬取页面的代理ip地址信息并保存到redis数据库中，此程序通过两个协程完成代理ip地址信息的爬取和更新：
    协程src.spider.ProxySpider.crawl_address(): 根据指定的数量，爬取指定页面的代理地址信息并存入数据库
    协程src.controller.ProxyController.proxy_control(): 定期验证数据库中代理地址的可用性并发布需要爬取的地址数量

# ==================================QuickStart===========================================

数据库配置
在proxy_spy.settings文件中配置redis数据库的链接信息:
    # redis服务器信息
    redis_host = 'x.x.x.x'
    redis_port = 6379
    # 数据库索引
    redis_key = 'proxy_address_list'

    在redis安装目录中的redis.windows.conf/redis.conf文件中配置：
        # 允许远程接入redis
        bind 0.0.0.0
        # 关闭保护模式以接受远程请求
        protected mode no

    在redis服务器上通过shell启动redis数据库：
        # windows系统
        redis-server.exe redis.windows.conf
        # linux系统
        src/redis-server redis.conf

    新建一个shell访问redis数据库以测试数据库连接正确。

程序启动
在proxy_spy目录中，执行如下命令即可启动：
    python main.py

# ==================================特别注意===========================================

特别注意：http://www.goubanjia.com/页面做了反爬措施：
    最初访问页面的时候，公开代理地址列表中的所有端口号都是错误的，页面会通过浏览器执行一个js文件：
        http://www.goubanjia.com/theme/goubanjia/javascript/pde.js?v=1.0
    此js将会执行一个算法，将错误的端口转换成正确的端口并刷新到html页面中。
    如果直接使用requests或者scrapy进行爬取，获得错误的端口号后，不能执行js文件，这样的代理地址是错误的。

    解决办法：
        使用selenium模拟浏览器向页面发起请求，selenium会执行页面上的js并返回正确端口的页面html数据。

    缺点：
        速度慢，消耗内存资源。

# ==================================协程说明===========================================

crawl_address协程：
此协程将会根据收取到的任务数量爬取指定页面，并解析页面html源码，获取代理地址数据并存放到redis数据库中。
此模块引用了selenium模块用以处理页面的下载。
此模块并不对代理地址执行可用性验证，在存放数据库完毕后线程控制权将会交由proxy_control协程。

proxy_control协程：
此协程将会定时验证数据库中的代理地址是否可用，并删除不可用地址。根据配置的最大存储代理地址数量，
发布下载任务，然后线程控制权将会交由crawl_address协程
