import re
import time
import scrapy
from ..items import RecruitmentSpiderItem

class QcwySpider(scrapy.Spider):
    name = "qcwy"
    platform = "qcwy"
    allowed_domains = ["we.51job.com"]
    start_urls = ["https://we.51job.com"]

    def __init__(self, keyword, city, pages, task_id):
        """
        初始化方法
        接收搜索关键字、城市名称、爬取页数、任务ID
        :param:
        :return:
        """
        self.keyword = keyword
        self.city = city
        self.pages = pages
        self.taskId = task_id

    def start_requests(self):
        """
        默认的start_requests回调函数
        通过爬取指定页数的数据，拼接url地址
        并将该地址推送给scrapy队列发起请求
        :param:
        :return:
        """
        for page in range(1, int(self.pages) + 1):
            url = f"https://we.51job.com/pc/search?jobArea=060000,260200,070200&keyword={self.keyword}&searchType=2&keywordType="
            time.sleep(1)
            yield scrapy.Request(url, callback=self.parse)

    def get_start_url(self):
        """
        该方法用于在中间件中获取到当前请求的URL，便于配置自动化浏览器
        中间件可以调用此方法获取URL
        """
        start_url = ("https://we.51job.com")
        return start_url

    def parse(self, response):
        """
        回调函数，满足通过xpath提取所需要的信息
        该方法主要是对列表页数据进行解析，将解析结果封装成JobItem对象，最终返回Item对象
        :param response:访问职位列表页返回数据对象
        :return:
        """
        position_list = response.xpath('//div[@class="joblist-item-job-wrapper"]')
        print(position_list)
        for it in position_list:
            # 薪资文本（可能为空，需容错）
            sal_text = it.xpath('.//span[@class="sal text-cut"]/text()').get()
            # sensorsdata 属性是 JSON 字符串，从中提取经验年限与学历
            sensors = it.xpath('.//div[@class="joblist-item-job sensors_exposure"]/@sensorsdata').get()
            exp = re.search(r'jobYear":"(.*?)"', sensors).group(1) if sensors and re.search(r'jobYear":"(.*?)"', sensors) else None
            edu = re.search(r'jobDegree":"(.*?)"', sensors).group(1) if sensors and re.search(r'jobDegree":"(.*?)"', sensors) else None
            item = RecruitmentSpiderItem(
                platform='qcwy',
                job_id='',
                task_id=self.taskId,
                title=it.xpath('.//div[@class="job-info text-cut"]/span/text()').get(),
                company=it.xpath('.//span[@class="cname text-cut"]/text()').get(),
                city=it.xpath('.//div[@class="shrink-0"]/text()').get(),
                salary_raw=sal_text,
                experience=exp,
                education=edu,
                skills='',
                description='',
            )
            print(item)
            if item['title']:
                yield item
