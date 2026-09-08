import scrapy
from ..items import RecruitmentSpiderItem

class ZhilianSpider(scrapy.Spider):
    #爬虫文件的名称
    name = "zhilian"
    #允许爬取的域名
    allowed_domains = ["zhaopin.com"]
    #爬取起始url列表
    start_urls = ["https://www.zhaopin.com/sou"]
    def __init__(self, keyword,city,pages,task_id):
        self.keyword = keyword
        self.city = city
        self.pages = pages
        self.taskId = task_id

    def start_requests(self):
        for page in range(1, int(self.pages) + 1):
            url = (f"https://www.zhaopin.com/sou?jl={self.city}&kw={self.keyword}&p={page}")
            yield scrapy.Request(url, callback=self.parse)


    def parse(self, response):
        #处理需要结果
        position_list = response.xpath('//div[@class="joblist-box__item clearfix joblist-box__item-unlogin"]')
        #遍历职位列表
        for position in position_list:
            #获取方位名称
            position_name = position.xpath("./div//a[@class='jobinfo__name']/text()").get()
            #获取岗位薪资
            position_salary = position.xpath("./div//p[@class='jobinfo__salary']/text()").get().strip()
            #获取技能
            position_skills = position.xpath(".//div[@class='jobinfo']//div[@class='joblist-box__item-tag']")
            skills = []
            for skill in position_skills:
                position_skill = skill.xpath(".//text()").get().strip()
                skills.append(position_skill)
            #获取工作地点
            position_location = position.xpath("./div//div[@class='jobinfo__other-info-item']/span/text()").get()
            #工作年限
            position_year = position.xpath("./div//div[@class='jobinfo__other-info-item'][2]/text()").get().strip()
            #获取公司名称
            company_name = position.xpath(".//a[@class='companyinfo__name']/text()").get().strip() if position.xpath(".//a[@class='companyinfo__name']/text()") else ""
            #学历
            position_education = position.xpath("./div//div[@class='jobinfo__other-info-item'][3]/text()").get().strip()

            item = RecruitmentSpiderItem(
                platform = "zhilian",
                job_id = "",
                task_id = self.taskId,
                title = position_name,
                company=company_name,
                city=position_location,
                salary_raw = position_salary,
                experience = position_year,
                education = position_education,
                skills = skills,
                description = "",

            )
            if item:
                yield item