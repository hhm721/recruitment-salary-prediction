import scrapy
from ..items import RecruitmentSpiderItem

class LiepinSpider(scrapy.Spider):
    name = 'liepin'
    platform = 'liepin'
    allowed_domains = ['liepin.com']
    start_urls = ["https://www.liepin.com/zhaopin/?inputFrom=www_index&workYearCode=0&key=%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD&scene=input&ckId=4a4yyru8fxdq1rn714ujp54qdc4yumob&dq="]
    citys = {
        '全国': '410', '北京': '010', '上海': '020', '天津': '030', '重庆': '040',
        '广州': '050020', '深圳': '050090', '苏州': '060080', '南京': '060020', '杭州': '070020',
        '大连': '210040', '成都': '280020', '武汉': '170020', '西安': '270020', '其他': '000',
    }

    def __init__(self, keyword, city, pages, task_id):
        self.keyword = keyword
        self.city = city
        self.pages = pages
        self.taskId = task_id

    def start_requests(self):
        for page in range(int(self.pages)):
            # 在爬虫中使用这些参数
            url = (f"https://www.liepin.com/zhaopin/?key={self.keyword}&city={self.citys[self.city]}"
                   f"&dq={self.citys[self.city]}&currentPage={page}&pageSize=40")
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        position_list = response.xpath('//div[@class="job-list-box"]/div')
        for index, item in enumerate(position_list):
            master_node = '//html/body/div/div[3]/section[1]/div[2]/div[' + str(index) + ']'
            item = RecruitmentSpiderItem(
                platform='liepin',
                job_id='', # job.css('::attr(data-jobid)').get('')
                task_id=self.taskId,
                title=item.xpath(master_node+'/div/div[1]/div/a/div[1]/div/div[@class="ellipsis-1"]/text()').get(),
                company=item.xpath(master_node+'/div/div[1]/div/div/div/span/text()').get(),
                city=item.xpath(master_node+'/div/div[1]/div/a/div[1]/div/div[2]/span[2]/text()').get(),
                salary_raw=item.xpath(master_node+'/div/div[1]/div/a/div[1]/span/text()').get(),
                experience=item.xpath(master_node+'/div/div[1]/div/a/div[2]/span[1]/text()').get(),
                education=item.xpath(master_node+'/div/div[1]/div/a/div[2]/span[2]/text()').get(),
                skills='',
                description='',
            )
            if item['title']:
                yield item
