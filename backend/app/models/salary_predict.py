from datetime import datetime
from .. import db

def _fmt_dt(dt):
    """统一时间展示：2026-08-07  23:49:02（日期与时间之间两个空格）"""
    if not dt:
        return None
    return dt.strftime('%Y-%m-%d  %H:%M:%S')

class SalaryPrediction(db.Model):
    __tablename__ = 'salary_prediction'

    id = db.Column(db.Integer, primary_key=True)
    resume_name = db.Column(db.String(200))
    predicted_salary_min = db.Column(db.Numeric(10, 2))
    predicted_salary_max = db.Column(db.Numeric(10, 2))
    predicted_salary_avg = db.Column(db.Numeric(10, 2))
    matched_jobs = db.Column(db.Integer)
    skills_extracted = db.Column(db.Text)
    experience_years = db.Column(db.Integer)
    education_level = db.Column(db.Integer)
    confidence = db.Column(db.Numeric(5, 4))
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'resume_name': self.resume_name,
            'predicted_salary_min': float(self.predicted_salary_min) if self.predicted_salary_min else None,
            'predicted_salary_max': float(self.predicted_salary_max) if self.predicted_salary_max else None,
            'predicted_salary_avg': float(self.predicted_salary_avg) if self.predicted_salary_avg else None,
            'matched_jobs': self.matched_jobs,
            'skills_extracted': self.skills_extracted,
            'experience_years': self.experience_years,
            'education_level': self.education_level,
            'confidence': float(self.confidence) if self.confidence else None,
            'created_at': _fmt_dt(self.created_at),
        }