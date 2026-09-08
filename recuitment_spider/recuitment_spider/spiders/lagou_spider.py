import re
import scrapy
from ..items import RecruitmentSpiderItem

class LagouSpider(scrapy.Spider):
    name = 'lagou'  # 爬虫的唯一标识名称
    platform = 'lagou'  # 招聘平台
    allowed_domains = ['lagou.com']  # 允许爬取的白名单域名列表
    start_urls = ["https://www.lagou.com"]  # 爬虫的起始 URL 列表

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
            url = (f"https://www.lagou.com/wn/zhaopin?fromSearch=true&kd={self.keyword}"
                   f"&city={self.city}&pn={page}")
            # url = (
            #     f'https://www.lagou.com/jobs/list_{self.keyword}?'
            #     f'city={self.city}&cl=false&fromSearch=true&labelWords=&suginput='
            # )
            yield scrapy.Request(url, callback=self.parse)

    def get_start_url(self):
        """
        该方法用于在中间件中获取到当前请求的URL，便于配置自动化浏览器
        中间件可以调用此方法获取URL
        """
        start_url = (f"https://www.lagou.com/wn")
        return start_url

    def parse(self, response):
        """
        回调函数，满足通过xpath提取所需要的信息
        该方法主要是对列表页数据进行解析，将解析结果封装成JobItem对象，最终返回Item对象
        :param response:访问职位列表页返回数据对象
        :return:
        """
        position_list = response.xpath('//div[@class="item__10RTO"]')
        for item in position_list:
            item = RecruitmentSpiderItem(
                platform='lagou',
                job_id='',  # job.css('::attr(data-jobid)').get('')
                task_id=self.taskId,
                title=self.parse_industry_location(item.xpath('.//a[@id="openWinPostion"]/text()').get())[0],
                company=item.xpath('.//div[@class="company-name__2-SjF"]/a/text()').get(),
                city=self.parse_industry_location(item.xpath('.//a[@id="openWinPostion"]/text()').get())[1],
                salary_raw=item.xpath('.//span[@class="money__3Lkgq"]/text()').get(),
                # salary_min=int(item.xpath('.//span[@class="money__3Lkgq"]/text()').get().split('-')[0][-1]),
                salary_min=int(re.findall(r'(\d+)', item.xpath('.//span[@class="money__3Lkgq"]/text()').get())[0]),
                # salary_max=int(item.xpath('.//span[@class="money__3Lkgq"]/text()').get().split('-')[1][-1]),
                salary_max=int(re.findall(r'(\d+)', item.xpath('.//span[@class="money__3Lkgq"]/text()').get())[1]),
                experience=self.parse_job_info(item.xpath('.//div[@class="p-bom__JlNur"]/text()').get()).get("experience"),
                education=self.parse_job_info(item.xpath('.//div[@class="p-bom__JlNur"]/text()').get()).get('education'),
                skills='',
                description='',
            )
            if item['title']:
                yield item

    def parse_industry_location(self, text):
        """
        从格式为 "岗位名称[地点]" 的字符串中提取两部分
        """
        if not text or '[' not in text or ']' not in text:
            raise ValueError(f"无效的格式: {text}")
        # 方式1: 使用正则
        pattern = r'([^[]+)\[([^\]]+)\]'
        match = re.match(pattern, text.strip())
        if match:
            return match.group(1).strip(), match.group(2).strip()
        # 方式2: 使用分割（备用方案）
        try:
            parts = text.split('[')
            industry = parts[0].strip()
            location = parts[1].split(']')[0].strip()
            return industry, location
        except:
            raise ValueError(f"无法解析字符串: {text}")

    def parse_job_info(self, text):
        """
        解析职位信息，提取薪资、经验、学历
        支持格式:
            "15k-25k经验3-5年 / 本科"
            "6k-12k经验不限 / 本科"
            "10K-20K3-5年/本科"
            "8-12K·13薪1-3年/大专"
        Returns:
            dict: {
                'salary_min': 15,
                'salary_max': 25,
                'salary_unit': 'k',
                'experience': '3-5年',
                'education': '本科'
            }
        """
        result = {
            'salary_min': None,
            'salary_max': None,
            'salary_unit': None,
            'experience': None,
            'education': None
        }

        if not text:
            return result

        text = text.strip()

        # 1. 提取薪资（如 15k-25k）
        salary_pattern = r'(\d+)\s*([kK万W]?)\s*[-—～~到至]\s*(\d+)\s*([kK万W]?)'
        salary_match = re.search(salary_pattern, text)

        if salary_match:
            result['salary_min'] = int(salary_match.group(1))
            result['salary_unit'] = (salary_match.group(2) or 'k').lower()
            result['salary_max'] = int(salary_match.group(3))
            # 移除薪资部分
            text = text.replace(salary_match.group(0), '')

        # 2. 提取经验（如 经验3-5年、经验不限、3-5年）
        exp_patterns = [
            r'经验\s*(\d+\s*[-—～~到至]?\s*\d*\s*年?)',  # 经验3-5年
            r'(\d+\s*[-—～~到至]?\s*\d*\s*年)',  # 3-5年
            r'经验不限',  # 经验不限
            r'应届生',  # 应届生
        ]

        for pattern in exp_patterns:
            exp_match = re.search(pattern, text)
            if exp_match:
                result['experience'] = exp_match.group(0).strip()
                text = text.replace(exp_match.group(0), '')
                break

        # 3. 提取学历（如 本科、大专、硕士等）
        edu_patterns = ['本科', '大专', '硕士', '博士', '研究生', '高中', '中专', '不限']
        for edu in edu_patterns:
            if edu in text:
                result['education'] = edu
                break

        # 如果学历在经验后面（如 经验3-5年/本科）
        if not result['education'] and '/' in text:
            parts = text.split('/')
            if len(parts) >= 2:
                result['education'] = parts[-1].strip()

        return result
