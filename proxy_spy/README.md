# 代理地址爬取程序
此程序将会爬取网络上公开的代理`ip`地址信息并保存到`redis`数据库中。



# 如何启动
## 数据库配置
* 在`proxy_spy.settings`文件中配置`redis`数据库的链接信息:
    ```python3
        redis_host = 'x.x.x.x'  # redis服务器信息
        redis_port = 6379  # redis服务器信息
        redis_key = 'proxy_address_list'  # 数据库索引
    ```


* 在`redis`安装目录中的`redis.windows.conf/redis.conf`文件中配置：
    ```python3
        bind 0.0.0.0  # 允许远程接入redis
        protected mode no  # 关闭保护模式以接受远程请求
    ```

* 在`redis`服务器上通过`shell`启动`redis`数据库：
    ```python3
        redis-server.exe redis.windows.conf  # windows系统
        src/redis-server redis.conf  # linux系统
    ```
    新建一个`shell`访问`redis`数据库以测试数据库连接正确。


## 程序启动
在`proxy_spy`目录中，执行如下命令启动程序：

```python3
    python main.py
```

# 如何处理页面反爬
* 本程序爬取的公开代理`ip`地址页面地址是: `http://www.goubanjia.com/`。
* 此页面的反爬措施如下:
    1. 最初访问页面的时候，公开代理地址列表中的所有端口号都是错误的，页面会通过浏览器执行一个`js`文件: `http://www.goubanjia.com/theme/goubanjia/javascript/pde.js?v=1.0`。
    2. 此`js`将会执行一个算法，将错误的端口转换成正确的端口并刷新到`html`页面中。
    3. 如果直接使用`requests`或者`scrapy`进行爬取，在获得错误的端口号后，无法执行`js`文件转换成正确端口，这样的代理地址是错误的。
* 解决办法
    使用`selenium`模拟浏览器向页面发起请求，`selenium`会执行页面上的`js`并返回正确端口的页面`html`数据。

# 如何验证代理地址的正确性

## 使用协程

此程序通过两个协程完成代理地址信息的爬取和更新操作。

* 协程`crawl_address`
    根据指定的数量，爬取指定页面的代理地址信息并存入数据库。
    接口定义: `src.spider.ProxySpider.crawl_address()`

    此协程将会根据收取到的任务数量爬取指定页面，并解析页面`html`源码，获取代理地址数据并存放到`redis`数据库中。
    此模块引用了`selenium`模块以处理页面的下载。
    此模块并不对代理地址执行可用性验证，在存放数据库完毕后线程控制权将会交由协程`proxy_control`处理。


* 协程`proxy_control`
    定期验证数据库中代理地址的可用性并发布需要补充爬取的地址数量
    接口定义: `src.controller.ProxyController.proxy_control()`

    此协程将会定时验证数据库中的代理地址是否可用，并删除不可用地址。
    根据配置的最大存储代理地址数量，发布下载任务，然后线程控制权将会交由协程`crawl_address`处理。
