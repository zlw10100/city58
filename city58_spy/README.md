# 58同城租房信息爬虫程序
此程序使用`scrapy`框架搭建爬虫结构，并引入`scrapy-redis`模块以提供分布式爬取。

# 如何启动
## 数据库配置
`scrapy-redis`模块要求我们提供`redis`数据库作为数据存储和调用，需要配置`redis`数据库且允许远程访问。

* 修改`redis`配置文件，在`redis`安装目录中的`redis.windows.conf/redis.conf`文件中配置：

    ```python3
        bind 0.0.0.0  # 允许远程接入
        protected mode no  # 关闭保护模式以接受远程请求
    ```

* 在`redis`服务器上通过`shell`启动`redis`数据库：

    ```python3
        redis-server.exe redis.windows.conf  # windows系统
        src/redis-server redis.conf  # linux系统

        # 新建一个shell访问redis数据库以测试数据库连接正确并发布下载任务
        lpush city58_zufang_list https://hz.58.com/chuzu/pn1
    ```

## 爬虫程序配置

`scrapy-redis`模块要求我们在爬虫程序中配置访问`redis`数据库的基本信息。

* 在`settings`文件中配置：

    ```python3
        # 分布式爬虫的调度器配置
        DUPEFILTER_CLASS = 'scrapy_redis.dupefilter.RFPDupeFilter'  # 指定去重队列
        SCHEDULER = 'scrapy_redis.scheduler.Scheduler'  # 使用共享调度器
        SCHEDULER_PERSIST = True  # 是否允许暂停,即断点续爬

        # 分布式爬虫环境下，需要指定远程服务器的地址
        REDIS_HOST = 'x.x.x.x'
        REDIS_PORT = 6379
    ```

## 程序启动
在完成分布式的相关配置后，复制`city58_spy`目录到其他电脑终端，准备在电脑终端通过`shell`启动爬虫程序。
* 进入`city58_py/city58_py/spiders`目录并执行命令：

    ```python3
        scrapy list  # 查看当前可用爬虫对象，应该可以看到city58的爬虫名称
        scrapy runspider city58.py  # 启动分布式爬虫
    ```

* 爬虫程序将会启动，并开始下载任务。


# 如何处理代理服务
为了减少爬虫被服务器识别并封禁的概率，本程序默认启用了一个下载中间件`MyRedisProxyDownLoaderMiddleware`用于
提供请求的代理地址。此中间件将会调用`city58_spy.libs.proxy.RedisPool`类，`RedisPool`类帮助爬虫程序获取`redis` 数据库中的代理地址：

* 停用代理服务
    如果要停用代理服务，或者自定义其他的代理服务，只需要注释如下语句即可：
        将`city58_spy.settings.DOWNLOADER_MIDDLEWARES`中对应的： `city58_spy.middlewares.MyRedisProxyDownLoaderMiddleware: xxx` 此行注释即可。


* 代理服务的配置
    此代理模块涉及`redis`服务器的链接，所以需要配置`redis`服务器的相关配置，在`city58_spy.settings`中配置：
    ```python3
        PROXY_REDIS_HOST = 'x.x.x.x'
        PROXY_REDIS_PORT = 6379
        PROXY_REDIS_KEY = 'proxy_address_list'  # redis服务器中保存数据的索引，在redis中是一个无序集合
    ```


* 代理地址
    此代理配置将会链接指定`redis`服务器并尝试获取一个代理地址
    ```python3
    地址数据格式:
        address = {
            'protocol': 'http/https',
            'ip': 'x.x.x.x',
            'port': 'xxx',
        }
    ```
    如果未从`redis`中获取到一个可用的代理地址，则不会对原始的请求对象执行代理信息的修改。


# 如何处理服务拒绝
* 对服务拒绝的判定
    本程序完成了对58同城租房页面的服务拒绝处理。目前发现服务被拒绝有两种判断条件：
    1. 服务器返回的响应码是`403`
    2. 服务器返回的响应对象中`url`形如： `https://callback.58.com/firewall/verifycode?...`

* 如何处理
    默认`scrapy`框架会自动处理`403`的响应码，即如果`http`响应是此码，框架会过滤此响应报文。
    本程序启用中间件`MyAllowHttpForbiddenDownLoaderMiddleware`以开放对`403`响应码的处理。
    同时，启用中间件`MyCatchHttpForbiddenSpiderMiddleware`处理服务拒绝。

* 一旦发生服务拒绝，程序的行为
    此中间件默认会处理上述两种拒绝服务条件的发生，汇总被拒绝的相关信息，并将拒绝的请求`url`存放到如下路径中： `city58_spy.settings.FORBIDDEN_FILE_PATH`。

* 如何停止对服务拒绝的处理
    如果要停用处理拒绝服务，或者自定义其他的实现方式，只需要注释如下语句即可：
        将`city58_spy.settings.SPIDER_MIDDLEWARES`中对应的： `city58_spy.middlewares.MyCatchHttpForbiddenSpiderMiddleware: xxx` 此行注释即可。

