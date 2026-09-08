"""
数据模型包
"""

from .user import User
from .job_raw import JobRaw
from .crawl_task import CrawlTask
from .job_clean import JobClean
from .salary_predict import SalaryPrediction

__all__ = ["User","JobRaw","CrawlTask","JobClean","SalaryPrediction"]