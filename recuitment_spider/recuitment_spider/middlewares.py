# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.http.response.html import HtmlResponse
from selenium import webdriver
import time
from selenium.webdriver.edge.options import Options
import tldextract  # 提取域名信息库


class RecruitmentSpidersSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RecruitmentSpidersDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class SeleniumMiddlewares(object):
    """
    创建使用selenium访问网页的中间件
    功能说明：
    1. 在爬虫启动时初始化 Chrome 浏览器实例
    2. 拦截所有请求，使用 Selenium 动态加载 JavaScript 渲染的页面
    3. 将渲染后的页面源码封装成 Scrapy Response 对象返回
    4. 在爬虫关闭时自动销毁浏览器实例，释放资源

    使用场景：
    - 需要处理 JavaScript 动态渲染的页面（如拉勾网、Boss直聘等）
    - 需要模拟用户操作（如点击、滚动等）
    - 需要绕过简单的反爬机制
    """
    def __init__(self):
        """
        初始化中间件实例
        作用：
        - 初始化浏览器配置对象（options）为 None
        - 初始化浏览器驱动对象（driver）为 None
        注意：
        - 不在 __init__ 中直接创建浏览器，而是延迟到 spider_opened 中创建
        - 这样做的目的是避免在 Scrapy 启动时过早占用资源
        - 同时也方便在爬虫启动时根据爬虫配置动态调整浏览器参数
        """
        self.options = None # Chrome 浏览器配置对象，用于设置启动参数
        self.driver = None # Selenium WebDriver 实例，用于控制浏览器

    @classmethod
    def from_crawler(cls, crawler):
        """
        从 Crawler 实例创建中间件对象（Scrapy 框架要求的类方法）
        作用：
        - 这是 Scrapy 中间件的标准工厂方法
        - 用于创建中间件实例并绑定 Scrapy 信号
        参数：
            crawler: Scrapy 的 Crawler 对象，包含项目配置、信号系统等
        返回：
            SeleniumMiddlewares: 中间件实例
        绑定的信号：
            spider_opened: 爬虫启动时触发，用于创建浏览器
            spider_closed: 爬虫关闭时触发，用于销毁浏览器
        为什么使用 @classmethod：
        - Scrapy 要求中间件通过 from_crawler 方法实例化
        - 这样可以访问 Crawler 对象，实现更灵活的配置
        """
        # 1. 创建中间件实例
        middleware = cls()
        # 2. 绑定爬虫启动信号：当爬虫打开时，调用 spider_opened 方法
        crawler.signals.connect(middleware.spider_opened, signals.spider_opened)
        # 3. 绑定爬虫关闭信号：当爬虫关闭时，调用 spider_closed 方法
        crawler.signals.connect(middleware.spider_closed, signals.spider_closed)
        # 4. 返回配置好的中间件实例
        return middleware

    def spider_opened(self, spider):
        """
        爬虫启动时的回调方法
        执行时机：
        - 由 Scrapy 信号系统自动调用
        - 在爬虫正式开始爬取之前执行
        主要功能：
        1. 创建 Chrome 浏览器配置对象（Options）
        2. 根据爬虫配置动态设置浏览器参数
        3. 创建并启动 Chrome 浏览器实例
        参数：
            spider: 当前启动的爬虫实例，可用于获取爬虫配置信息
        配置说明：
        - 无头模式（headless）：默认注释，如需启用取消注释
        - 窗口大小：无头模式下建议设置，避免元素不可见
        - GPU 加速：禁用可提高兼容性
        - debugger_address：连接已启动的 Chrome 调试实例
        注意事项：
        - 确保 ChromeDriver 与 Chrome 浏览器版本匹配
        - 在 Linux 服务器上运行可能需要额外参数（如 --no-sandbox）
        """
        # ========== 1. 创建浏览器配置对象 ==========
        # Options 用于设置 Chrome/Edge 启动时的各种参数
        self.options = Options()
        # ========== 2. 设置浏览器启动参数 ==========
        # 【关键】反自动化检测：招聘网站会识别 webdriver 特征并降级/拦截（返回空页或验证码）
        # 不加这些参数，智联/猎聘等会直接返回空页面，导致 0 条数据
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.options.add_experimental_option('useAutomationExtension', False)
        # 【禁用GPU加速】提高兼容性
        self.options.add_argument('--disable-gpu')
        # 【窗口大小】
        self.options.add_argument('--window-size=1920,1080')
        # 检查爬虫是否有 get_start_url 方法
        if hasattr(spider, 'get_start_url'):
            # 获取爬虫的起始 URL
            start_url = spider.get_start_url()
            # 使用 tldextract 提取域名信息
            extracted = tldextract.extract(start_url)
            # 提取主域名
            domain = extracted.domain  # "lagou"
            # 原逻辑：lagou/51job/zhipin 连接 127.0.0.1:8888 已启动的调试浏览器，
            # 若未提前启动会直接失败。现改为普通启动 + 反检测，保证爬虫能独立运行。
            spider.logger.info(f'浏览器已启动，起始URL: {start_url}, 主域名: {domain}')
        else:
            spider.logger.info('浏览器已启动')
        # ========== 4. 创建并启动浏览器 ==========
        # options 是 Edge Options，故显式用 Edge 驱动。
        # 原因：本机只有 Microsoft Edge；且 webdriver.Chrome(options=edge_options)
        # 会导致 execute_cdp_cmd 端点 404（无法隐藏 webdriver 特征），反爬严格的站点会拒绝加载。
        try:
            self.driver = webdriver.Edge(options=self.options)
        except Exception:
            # 兜底：某些机器只有 Chrome 时回退到 Chrome
            self.driver = webdriver.Chrome(options=self.options)
        # 隐藏 webdriver 特征（配合反检测参数，避免被识别为自动化）
        try:
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
            })
        except Exception:
            pass
        spider.logger.info('浏览器已启动')

    def spider_closed(self, spider):
        """
        爬虫关闭时的回调方法
        执行时机：
        - 由 Scrapy 信号系统自动调用
        - 在爬虫完成所有任务或异常终止时执行
        主要功能：
        - 关闭 Chrome 浏览器，释放系统资源
        参数：
            spider: 当前关闭的爬虫实例
        注意事项：
        - 必须确保浏览器被正确关闭，否则可能导致内存泄漏
        - 即使爬虫异常退出，此方法也会被调用（Scrapy 保证）
        """
        # 检查 driver 是否存在（避免重复关闭）
        if self.driver:
            try:
                # 关闭浏览器并释放资源
                # quit() 会关闭所有窗口并终止 Chrome 进程
                self.driver.quit()
                spider.logger.info('浏览器已关闭')
            except Exception as e:
                # 捕获异常，避免影响爬虫关闭流程
                spider.logger.error(f'关闭浏览器时发生异常: {e}')

    # 访问时使用webdriver浏览器加载
    def process_request(self, request, spider):
        """
        处理单个请求的核心方法
        执行时机：
        - 每次 Scrapy 发送请求前，经过下载器中间件时调用
        - 对于标记了 'use_selenium': True 的请求，使用 Selenium 处理
        主要功能：
        1. 检查是否需要使用 Selenium（通过 request.meta 标记）
        2. 使用 Chrome 浏览器访问目标 URL
        3. 等待页面加载完成（JavaScript 渲染）
        4. 获取完整的页面源码
        5. 封装成 Scrapy Response 对象返回
        参数：
            request: Scrapy 的 Request 对象，包含 URL、headers、meta 等信息
            spider: 当前运行的爬虫实例
        返回：
            HtmlResponse: Scrapy 的响应对象，供爬虫解析
            None: 如果不需要处理，返回 None 继续执行其他中间件
        工作流程：
            1. 检查 driver 是否可用
            2. 使用 Selenium 访问 URL
            3. 等待页面加载（硬等待或智能等待）
            4. 获取页面源码
            5. 封装成 HtmlResponse 返回
        注意事项：
            - 使用 time.sleep() 是硬等待，建议改用 WebDriverWait
            - 页面加载时间可能因网络、反爬等因素变化
            - 需要处理超时和异常情况
        """
        # ========== 1. 检查浏览器驱动是否可用 ==========
        # 如果 driver 不存在，说明浏览器未正常启动
        # 此时无法处理请求，返回 None 让 Scrapy 使用默认下载器
        if not self.driver:
            spider.logger.warning('浏览器驱动不可用，跳过 Selenium 处理')
            return None
        # ========== 2. 使用 Selenium 访问目标 URL ==========
        # 你的 Selenium 逻辑
        try:
            # 使用浏览器访问目标 URL
            self.driver.get(request.url)
            spider.logger.debug(f'页面加载完成: {request.url}')
        except Exception as e:
            # 如果访问失败，记录错误并返回 None
            # 让 Scrapy 使用默认下载器重试
            spider.logger.error(f'Selenium 访问失败: {e}')
            return None
        # ========== 3. 等待页面加载 ==========
        # 智联/猎聘/前程无忧等 SPA 站点职位列表由 JS 异步渲染，固定等 3 秒往往不够。
        # 按平台等待职位列表容器出现（比按页面体积判断更精准：51job 页面即使未渲染
        # 职位也超过 100KB，若只看体积会误判为已就绪导致 0 条）。
        PLATFORM_JOB_MARKERS = {
            'zhilian': 'joblist-box__item',
            'qcwy': 'joblist-item-job-wrapper',
            'liepin': 'job-card',
            'lagou': 'item__10RSC',
        }
        marker = None
        for plat, m in PLATFORM_JOB_MARKERS.items():
            if plat in getattr(spider, 'name', ''):
                marker = m
                break
        time.sleep(3)
        for _ in range(9):  # 最多再等 9 秒
            try:
                src = self.driver.page_source
            except Exception:
                break
            if marker:
                if marker in src:  # 职位列表已渲染出来
                    break
            elif len(src) > 100000:  # 无匹配平台时兜底按体积判断
                break
            time.sleep(1)
        # 获取页面的源码
        # page_source 包含完整的 HTML 内容（包括 JavaScript 渲染后的 DOM）
        source = self.driver.page_source
        spider.logger.debug(f'页面数据内容: {source}')
        # 记录页面大小，便于调试
        # spider.logger.debug(f'页面源码大小: {len(source)} 字符')
        # ========== 4. 封装成 Scrapy Response ==========
        response = HtmlResponse(url=self.driver.current_url, body=source, request=request, encoding='utf-8')
        # ========== 5. 返回响应 ==========
        spider.logger.info(f'Selenium 处理完成: {request.url}')
        return response

