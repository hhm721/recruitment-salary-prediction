from datetime import datetime
from ..import db

def _fmt_dt(dt):
    """统一时间展示：2026-08-07  23:49:02（日期与时间之间两个空格）"""
    if not dt:
        return None
    return dt.strftime('%Y-%m-%d  %H:%M:%S')

class JobRaw(db.Model):
    __tablename__ = 'job_raw'

    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50), nullable=False, index=True)
    job_id = db.Column(db.String(100))
    task_id = db.Column(db.String(100))
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200))
    city = db.Column(db.String(50), index=True)
    salary_raw = db.Column(db.String(100))
    salary_min = db.Column(db.Numeric(10, 2))
    salary_max = db.Column(db.Numeric(10, 2))
    experience = db.Column(db.String(50))
    education = db.Column(db.String(50))
    skills = db.Column(db.Text)
    description = db.Column(db.Text)
    publish_time = db.Column(db.DateTime)
    crawl_time = db.Column(db.DateTime, default=datetime.now)
    is_cleaned = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'platform': self.platform,
            'job_id': self.job_id,
            'task_id': self.task_id,
            'title': self.title,
            'company': self.company,
            'city': self.city,
            'salary_raw': self.salary_raw,
            'salary_min': float(self.salary_min) if self.salary_min else None,
            'salary_max': float(self.salary_max) if self.salary_max else None,
            'experience': self.experience,
            'education': self.education,
            'skills': self.skills,
            'description': self.description,
            'publish_time': _fmt_dt(self.publish_time),
            'crawl_time': _fmt_dt(self.crawl_time),
            'is_cleaned': self.is_cleaned,
        }