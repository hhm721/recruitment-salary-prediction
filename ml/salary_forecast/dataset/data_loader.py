import numpy as np
import pandas as pd
from ml.salary_forecast.dataset.database_engine import DatabaseEngine


class DataLoader:
    """数据加载雷"""
    def __init__(self,db_type='mysql'):
        """
        初始化参数
        :param:engine 引擎
        :param:db_type 数据库类型
        :param:connect 连接对象
        """
        self.db_type = db_type
        self.engine = None
        self.connect()

    def connect(self):
        """连接数据库"""
        if self.db_type == 'mysql':
            self.engine = DatabaseEngine.get_mysql_engine()
        else:
            raise ValueError(f"不支持的数据库类型: {self.db_type}")
        if self.engine is None:
            raise Exception("数据库连接失败....")

    def load_data(self,table_name='job_raw',limit=None,query=None):
        """
        加载数据
        :param table_name: 表名
        :param limit: 限制数据条数
        :param query: 查询对象
        :return:
        """
        try:
            if query:
                sql = query
            else:
                #拼接SQL语句
                sql = (f"SELECT platform, title, company, city, salary_raw, experience, education, skills, description, publish_time "
                       f"FROM {table_name}")
                if limit:
                    sql += f" LIMIT {limit}"
            datas = pd.read_sql(sql, self.engine)
            return datas
        except Exception as e:
            print(f"数据获取失败:{e}")
            return None

    def create_sample_data(self):
        """创建示例数据"""
        print("未查询到数据，创建示例数据")
        np.random.seed(42)
        n_samples = 1000

        salary_options = [
            '8千-1.2万', '1.2-2万', '2-3万', '6-8千',
            '1.5-2.5万', '3-5万', '200元/天', '100元/天'
        ]
        titles = [
            '前端开发工程师', '后端开发工程师', '数据科学家',
            '产品经理', 'UI设计师', '测试工程师', '项目经理'
        ]
        companies = [
            '字节跳动', '阿里巴巴', '腾讯', '百度', '美团',
            '京东', '拼多多', '华为', '小米'
        ]
        cities = ['北京', '上海', '深圳', '杭州', '广州', '成都', '三亚', '万宁']
        experiences = [
            '1-3年', '3-5年', '5-10年', '无需经验',
            '在校生/应届生', '3年及以上', '2-4年'
        ]
        educations = ['本科', '硕士', '大专', '博士', '不限']
        skill_pool = [
            'Python', 'Java', 'SQL', 'Linux', 'React', 'Vue',
            'Docker', 'AWS', '测试', '管理', '方案', 'JavaScript',
            'C++', 'Go', 'Rust', 'Kubernetes', 'TensorFlow',
            'PyTorch', 'Spring', 'Django', 'Flask'
        ]

        data = {
            'id': range(1, n_samples + 1),
            'platform': ['boss'] * n_samples,
            'job_id': [f'JOB{i:05d}' for i in range(n_samples)],
            'task_id': [''] * n_samples,
            'title': np.random.choice(titles, n_samples),
            'company': np.random.choice(companies, n_samples),
            'city': np.random.choice(cities, n_samples),
            'salary_raw': np.random.choice(salary_options, n_samples),
            'experience': np.random.choice(experiences, n_samples),
            'education': np.random.choice(educations, n_samples),
            'skills': [[np.random.choice(skill_pool, size=np.random.randint(1, 5)).tolist()]
                       for _ in range(n_samples)],
            'description': [
                               '岗位要求：有相关经验者优先，提供五险一金，年终奖。'
                               '工作地点：北京·朝阳区。公司类型：国企。'
                           ] * n_samples,
            'publish_time': ['2025/7/17 10:13'] * n_samples,
            'crawl_time': ['2026/8/6 0:00'] * n_samples,
            'is_cleaned': [0] * n_samples
        }

        df = pd.DataFrame(data)
        print(f"示例数据创建完成，共 {len(df)} 条")
        return df

    def get_datas(self,db_type='mysql',table_name='job_raw',limit=None,query=None,use_sample=False):
        """
        获取所有数据
        :param db_type:数据库类型
        :param table_name: 表名
        :param limit: 限制条数
        :param query: 查询语句
        :param ues_sample: 使用示例数据
        :return: DataFrame
        """
        print(f"{'=' * 60}\n正在加载数据\n{'=' * 60}")
        #1.加载数据
        datas = None
        if not use_sample:
            try:
                if query:
                    datas = self.load_data(query=query)
                else:
                    datas = self.load_data(table_name=table_name,limit=limit)
                if datas is not None and len(datas) > 0:
                    print(f"数据获取成功:总共获取到{len(datas)}条数据")
                    return datas
            except Exception as e:
                print(f"数据库操作失败:{e},使用示例数据继续...")
                use_sample = True

        if use_sample:
            datas = self.create_sample_data()
            print(f"获取示例数据成功，共{len(datas)}条")

        if datas is None or len(datas) == 0:
            print("无数据可用")
            return None

if __name__ == '__main__':
    #实例化对象
    data_loader = DataLoader()
    #调用get_datas获取数据
    df = data_loader.get_datas()
    print(df)