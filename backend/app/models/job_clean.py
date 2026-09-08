from datetime import datetime
from ..import db

def _fmt_dt(dt):
    """统一时间展示"""
    if not dt:
        return None
    return dt.strftime('%Y-%m-%d  %H:%M:%S')


class JobClean(db.Model):
    __tablename__ = 'job_clean'

    id = db.Column(db.Integer, primary_key=True)
    raw_id = db.Column(db.Integer, db.ForeignKey('job_raw.id'))
    platform = db.Column(db.String(50), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200))
    city = db.Column(db.String(50), index=True)
    salary_min = db.Column(db.Numeric(10, 2))
    salary_max = db.Column(db.Numeric(10, 2))
    salary_avg = db.Column(db.Numeric(10, 2), index=True)
    experience_years = db.Column(db.Integer)
    education_level = db.Column(db.Integer)
    skills = db.Column(db.Text)
    skill_count = db.Column(db.Integer, default=0)
    city_level = db.Column(db.Integer)
    job_level = db.Column(db.String(20))
    job_features = db.Column(db.Text)
    skill_features = db.Column(db.Text)
    text_features = db.Column(db.Text)
    clean_time = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'raw_id': self.raw_id,
            'platform': self.platform,
            'title': self.title,
            'company': self.company,
            'city': self.city,
            'salary_min': float(self.salary_min) if self.salary_min else None,
            'salary_max': float(self.salary_max) if self.salary_max else None,
            'salary_avg': float(self.salary_avg) if self.salary_avg else None,
            'experience_years': self.experience_years,
            'education_level': self.education_level,
            'skills': self.skills,
            'skill_count': self.skill_count,
            'city_level': self.city_level,
            'job_level': self.job_level,
            'job_features': self.job_features,
            'skill_features': self.skill_features,
            'text_features': self.text_features,
            'clean_time': _fmt_dt(self.clean_time),
        }