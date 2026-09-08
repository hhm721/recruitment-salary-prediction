# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from dataclasses import dataclass
import scrapy

class RecruitmentSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name: str | None = None
    platform = scrapy.Field() #平台名称
    job_id = scrapy.Field()  #职位id
    task_id = scrapy.Field() #任务id
    title = scrapy.Field() #职位名称
    salary_raw = scrapy.Field()#薪资范围
    city = scrapy.Field()  #工作城市
    experience = scrapy.Field()#工作经验
    education = scrapy.Field()#学历要求
    skills = scrapy.Field()  #技能要求
    description = scrapy.Field()#描述信息
    company = scrapy.Field() #公司名称
    job_url = scrapy.Field()