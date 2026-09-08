# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json
import os
from datetime import datetime

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
# 放在文件最顶部，最先导入
import pymysql


class ShopSpiderPipeline:
    def process_item(self, item):
        return item
class MysqlPipeline:
    def open_spider(self, spider):
        print(spider.settings["MYSQL_HOST"])
        print(spider.settings["MYSQL_PORT"])
        print(spider.settings["MYSQL_USERNAME"])
        print(spider.settings["MYSQL_PASSWORD"])
        print(spider.settings["MYSQL_DB"])
        self.conn = pymysql.connect(
            host = os.getenv("DB_HOST",spider.settings["MYSQL_HOST"]),
            port = int(os.getenv("DB_PORT",spider.settings["MYSQL_PORT"])),
            user = os.getenv("DB_USER",spider.settings["MYSQL_USERNAME"]),
            password = os.getenv("DB_PASSWORD",spider.settings["MYSQL_PASSWORD"]),
            database = os.getenv("DB_NAME",spider.settings["MYSQL_DB"]),
            charset = "utf8mb4"
        )
        self.cursor = self.conn.cursor()

    def close_spider(self, spider):
        """
        关闭游标与数据库连接
        """
        self.cursor.close()
        self.conn.close()
    def process_item(self, item,spider):
        adaptr = ItemAdapter(item)
        skills = adaptr.get("skills")
        if isinstance(skills, list):
            skills = json.dumps(skills,ensure_ascii=False)
        publish_time = adaptr.get("publish_time")
        if isinstance(publish_time, str):
            try:
                publish_time = datetime.fromisoformat(publish_time,)
            except ValueError:
                publish_time = datetime.now()
        sql = """
            INSERT INTO job_raw (platform, job_id, task_id, title, company, city, salary_raw, salary_min,
            salary_max, experience, education, skills, description, publish_time, crawl_time, is_cleaned)
            VALUES (%s, %s, %s, %s,%s,%s,%s,%s,%s, %s, %s, %s,%s,%s,%s,0)
            ON DUPLICATE KEY UPDATE 
            title = VALUES(title), salary_raw = VALUES(salary_raw), crawl_time = VALUES(crawl_time)
        """
        self.cursor.execute(sql,(
            adaptr.get("platform"),
            adaptr.get("job_id"),
            adaptr.get("task_id"),
            adaptr.get("title"),
            adaptr.get("company"),
            adaptr.get("city"),
            adaptr.get("salary_raw"),
            adaptr.get("salary_min"),
            adaptr.get("salary_max"),
            adaptr.get("experience"),
            adaptr.get("education"),
            skills,
            adaptr.get("description"),
            publish_time,
            datetime.now(),
        ))
        self.conn.commit()
        return item
