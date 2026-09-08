from datetime import datetime
from ..import db


def _fmt_dt(dt):
    """统一时间展示"""
    if not dt:
        return None
    return dt.strftime('%Y-%m-%d  %H:%M:%S')

class CrawlTask(db.Model):
    __tablename__ = 'crawl_task'

    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50), nullable=False)
    keyword = db.Column(db.String(100))
    city = db.Column(db.String(50))
    status = db.Column(db.Enum('pending', 'running', 'completed', 'failed'), default='pending')
    total_count = db.Column(db.Integer, default=0)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    error_msg = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'platform': self.platform,
            'keyword': self.keyword,
            'city': self.city,
            'status': self.status,
            'total_count': self.total_count,
            'start_time': _fmt_dt(self.start_time),
            'end_time': _fmt_dt(self.end_time),
            'error_msg': self.error_msg,
            'created_at': _fmt_dt(self.created_at),
        }