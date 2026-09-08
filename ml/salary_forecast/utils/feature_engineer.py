import re
from collections import Counter
import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler, LabelEncoder
from ml.salary_forecast.dataset.data_loader import DataLoader

class FeatureEngineer:
    """特征工程类"""

    def __init__(self):
        self.df = DataLoader().get_datas()
        self.scaler = RobustScaler()
        self.label_encoder = {}
        self.feature_importance = None

    def clean_data(self):
        """清洗数据"""
        print("开始清洗数据")
        #删除完全重复的行
        self.df = self.df.drop_duplicates()
        #处理岗位名称字段
        if"title" in self.df.columns:
            self.df["title"] = self.df["title"].fillna("")

        #处理技能字段
        if "skills" in self.df.columns:
            #判断技能字段是不是字符串
            if isinstance(self.df["skills"].iloc[0], str):
                self.df["skills"] = self.df["skills"].apply(
                    #检查skills列是否存在，如果只是字符串且以列表的形式开头 将其转化为真值
                    lambda x: eval(x) if isinstance(x, str) and x.startswith("[")
                    # 如果值是非空的普通字符串如（python）将其包装成单元素列表
                    else [x] if pd.notnull(x) and x !="" else []
                )

        #处理经验字段
        if"experience" in self.df.columns:
            self.df["experience"] = self.df["experience"].fillna("无需经验")

        #处理教育字段
        if"education" in self.df.columns:
            self.df["education"] = self.df["education"].fillna("不限学历")

        #处理描述字段
        if"description" in self.df.columns:
            self.df["description"] = self.df["description"].fillna("")

        print(f"数据清晰完成，剩余{len(self.df)}条数据")
        return self

    def parse_salary(self):
        """薪资解析"""
        #类中的局部函数 raw参数是当前该函数时自动传递
        def parse_salary_row(row):
            raw = str(row.get("salary_raw",""))
            #清洗薪资格式 将字符串中所有·替换为空字符
            #清洗薪资格式
            raw = raw.replace("·","").replace("薪资","").strip()
            try:
                #处理日薪
                if '元/天' in raw:
                    #从薪资中提取薪资数字（10k-15k）->[10,15]
                    nums = re.findall(r'(\d+\.?\d*)', raw)
                    #第一个数字nums[0]转换为浮点数
                    daily = float(nums[0])
                    #按照22个工作日计算月薪
                    monthly = daily * 22
                    #返回薪资区间
                    return monthly * 0.9,monthly * 1.1

                #处理时薪
                if '元/时' in raw or '元/小时' in raw:
                    #提取薪资数据
                    nums = re.findall(r'(\d+\.?\d*)', raw)
                    if nums:
                        hourly = float(nums[0])
                        monthly = hourly * 8 * 22
                        return monthly * 0.9,monthly * 1.1

                #处理年薪
                if '万/年' in raw:
                    nums = re.findall(r'(\d+\.?\d*)', raw)
                    if nums:
                        annual = float(nums[0]) * 10000
                        monthly = annual / 12
                        if len(nums) >= 2:
                            return float(nums[0]) * 10000 / 12, float(nums[1]) * 10000 / 12
                        return monthly * 0.85,monthly * 1.15

                #处理以千为单位的
                if '千' in raw:
                    nums = re.findall(r'(\d+\.?\d*)', raw)
                    if len(nums) >=2:
                        return float(nums[0]) * 1000, float(nums[1]) * 1000
                    elif nums:
                        val = float(nums[0]) * 1000
                        return val * 0.8, val * 1.2

                #处理以万为单位
                if '万' in raw:
                    nums = re.findall(r'(\d+\.?\d*)', raw)
                    if len(nums) >= 2:
                        return float(nums[0]) * 10000, float(nums[1]) * 10000
                    elif nums:
                        val = float(nums[0]) * 10000
                        return val * 0.8, val * 1.2

                if '以上' in raw:
                    nums = re.findall(r'(\d+\.?\d*)', raw)
                    if nums:
                        val = float(nums[0])
                        if '千' in raw:
                            val *= 1000
                        elif '万' in raw:
                            val *= 10000
                        return val, val * 1.5

                #处理蠢数字或范围
                nums = re.findall(r'(\d+\.?\d*)', raw)
                if len(nums) >= 2:
                    return float(nums[0]), float(nums[1])
                elif len(nums) == 1:
                    val = float(nums[0])
                    #判断单位
                    if '千' in raw:
                        val *= 1000
                    elif '万' in raw:
                        val *= 10000
                    return val, val * 1.5
            except Exception as e:
                pass
            return np.nan, np.nan


    # 应用解析 作用到每一条数据上
        self.df[["salary_min_parsed", "salary_max_parsed"]] = self.df.apply(
            parse_salary_row, axis=1, result_type="expand"
        )
        # 过滤无效数据
        self.df = self.df.dropna(subset=["salary_min_parsed", "salary_max_parsed"])

        # 过滤异常薪资
        self.df = self.df[
            (self.df["salary_min_parsed"] >= 2000) &
            (self.df["salary_max_parsed"] <= 80000)
            ]

        if len(self.df) == 0:
            print("无有效薪资数据")
            return self

        # 计算目标值
        self.df["salary_target"] = (self.df["salary_max_parsed"] + self.df["salary_min_parsed"]) / 2
        # 将薪资目标值进行对数变换，每个值执行log(1+x)变换
        self.df["salary_target_log"] = np.log1p(self.df["salary_target"])

        #异常值处理 使用IQR（四分位距）识别和限制薪资数据中的异常值
        Q1 = self.df["salary_target"].quantile(0.02)
        Q3 = self.df["salary_target"].quantile(0.98)
        IQR = Q3 - Q1
        lower_bound = max(2000, Q1 - 2 * IQR)
        upper_bound = min(80000, Q3 + 2 * IQR)
        #过滤数据
        self.df = self.df[
            (self.df["salary_target"] >= lower_bound) &
            (self.df["salary_target"] <= upper_bound)
        ]
        print(f"薪资解析完成,有效数据：{len(self.df)}条")
        print(f"薪资范围：{self.df['salary_target'].min():.0f}~{self.df['salary_target'].max():.0f}")
        print(f"平均薪资：{self.df['salary_target'].mean():.0f}")

        return self

    def encode_experience(self):
        """经验编码"""
        def encode_exp(exp):
            if pd.isna(exp):
                return 0
            #将变量exp 转换为字符串并同意转换为小写
            exp = str(exp).lower()

            #处理特殊情况
            if '在校生' in exp or '应届生' in exp:
                return 0
            if '无需' in exp or '不限' in exp:
                return 0

            #提取对应数字
            nums = re.findall(r'(\d+\.?\d*)', exp)
            if nums:
                if len(nums) >= 2:
                    #计算平均经验
                    exp_val = (float(nums[0]) + float(nums[1])) / 2
                else:
                    exp_val = float(nums[0])


                #经验分类
                if exp_val <= 1:
                    return 1
                elif exp_val <= 3:
                    return 2
                elif exp_val <= 5:
                    return 3
                elif exp_val <= 10:
                    return 4
                else:
                    return 5
            return 0
        self.df["experience_level"] = self.df["experience"].apply(encode_exp)
        self.df["experience_years"] = self.df["experience"].apply(
            lambda x: float (re.findall(r'(\d+\.?\d*)', str(x))[0]) if re.findall(r'(\d+\.?\d*)', str(x)) else 0
        )

        return self

    def encode_education(self):
        """学历编码"""
        edu_level_map= {
            '博士': 6, '硕士': 5, '研究生': 5,
            '本科':4, '大专':3, '中专':2,
            '高中':2, '初中':1, '小学':1
        }

        edu_category_map = {
            '博士':'博士',
            '硕士':'硕士',
            '研究生':'研究生',
            '本科':'本科',
            '大专':'大专',
            '中专':'中专',
            '高中':'高中',
            '初中':'初中',
            '小学':'小学',
        }

        def map_education(edu):
            if pd.isna(edu):
                return 3 #默认大专
            edu = str(edu)
            if '不限' in edu:
                return 3
            #获取字典中对应的值
            for key ,val in edu_level_map.items():
                if key in edu:
                    return val
                return 3
            self.df["education_level"] = self.df["education"].apply(map_education)

            def map_education_category(edu):
                if pd.isna(edu):
                    return '大专'
                edu = str(edu)
                if '不限' in edu:
                    return '大专'
                for key, val in edu_category_map.items():
                    if key in edu:
                        return val
                return "大专"
            self.df["education_category"] = self.df["education"].apply(map_education_category)
            return self

    def company_features(self):
        """公司特征"""
        #公司类型
        company_types = {
            "国企","民营","上市公司","外资","合资","私营"
        }
        for ctype in company_types:
            self.df[f'company_type_{ctype}'] = self.df["description"].apply(
                lambda x: 1 if isinstance(x,str) and ctype in x else 0
            )

        #公司规模
        scale_map = {
            '少于50人': 1,
            '50-100人': 2,
            '150-500人':3,
            '500-1000人':4,
            '1000-5000人':5,
            '5000人以上':6,
        }

        def extract_scale(desc):
            if not isinstance(desc, str):
                return 0
            for key, val in scale_map.items():
                if key in desc:
                    return val
            return 0
        self.df['company_scale_level'] = self.df["description"].apply(extract_scale)

        #公司行业
        industries = [
            "互联网","金融","电商","医疗","教育","服务业","制造业"
        ]
        for industry in industries:
            self.df[f'industry_{industry}'] = self.df["description"].apply(
                lambda x: 1 if isinstance(x,str) and industry in x else 0
            )
        print(f"进行处理后的所有数据：{self.df}")
        return self

    def extract_skills(self):
        """技能特征"""
        #技能数量
        self.df["skill_count"] = self.df["skills"].apply(
            lambda x: len(x) if isinstance(x,list) else 0
        )

        #提取所有技能
        all_skills = []
        for skills in self.df['skills']:
            if isinstance (skills, list):
                for skill in skills:
                    if isinstance(skill, list):
                        all_skills.extend([str(s.lower())for s in skill])
                    else:
                        all_skills.append(str(skill).lower())
            elif isinstance (skills, str):
                all_skills.extend([s.strip().lower() for s in skills.split(",") if s.strip()])

        skill_counter = Counter(all_skills)
        print(f"总共有{len(skill_counter)}个不同技能")

        #定义技能分类字典
        #将多种可能的技能关键词进行归类
        skill_categories = {
            'programming': ['python', 'java', 'c++', 'go', 'rust', 'javascript', 'typescript'],
            'web': ['react', 'vue', 'angular', 'html', 'css', 'node', 'spring', 'django'],
            'data': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch'],
            'cloud': ['docker', 'kubernetes', 'aws', 'azure', 'gcp', 'linux'],
            'ml': ['tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy'],
            'management': ['管理', '项目', '团队', '领导', '协调']
        }

        #批量计算技能类别匹配
        for category, skills in skill_categories.items():
            self.df[f"skill_category_{category}"] = self.df["skills"].apply(
                lambda x, skills=skills: sum(1 for s in x if isinstance(x, list) and
                                             any(skill in str(s).lower() for skill in skills))
                                                if isinstance(x, list) else 0
            )

        #使用前30个高频技能
        top_skills = [s for s, _ in skill_counter.most_common(30)]

        #创建技能特征
        for skill in top_skills[:25]:
            col_name = f"skill_{skill.replace(' ', '_').replace('-', '_')[:20]}"
            self.df[col_name] = self.df["skills"].apply(
                lambda x, skill=skill: 1 if isinstance(x, list) and any(
                    skill in str(s).lower() for s in x
                ) else (1 if isinstance(x,str) and skill in x.lower() else 0)
            )

        key_skill_combinations = [
            ['python', 'sql'], ['python', 'java'], ['react', 'node'],
            ['docker', 'kubernetes'], ['管理', '项目'], ['测试', '自动化']
        ]

        for combo in key_skill_combinations:
            combo_name = '_'.join(combo)
            self.df[f"skill_combo_{combo_name}"] = self.df["skills"].apply(
                lambda x, combo=combo: 1 if isinstance(x, list) and all(
                    any(skill in str(s).lower() for s in x) for skill in combo
                ) else 0
            )

        return self

    def extract_city(self):
        """城市特征"""
        def clean_city_name(city_text):
            # 从文本中提取标准城市名称 北京-丰台-看丹 -》北京
            if pd.isna(city_text) or not isinstance(city_text, str):
                return "未知"
            city_text = city_text.strip()
            #提取城市名 取第一个分隔符之前的部分
            for sep in ['·','-','（','(']:
                if sep in city_text:
                    city_text = city_text.split(sep)[0]
                    break
            return city_text
        self.df['city_clean'] = self.df["city"].apply(clean_city_name)

        #城市等级编码
        city_tier_map = {
            # 一线 (5)
            '北京': 5, '上海': 5, '广州': 5, '深圳': 5,
            # 新一线 (4)
            '成都': 4, '杭州': 4, '武汉': 4, '南京': 4, '重庆': 4,
            '西安': 4, '苏州': 4, '天津': 4, '长沙': 4, '郑州': 4,
            '东莞': 4, '青岛': 4, '合肥': 4, '宁波': 4, '无锡': 4,
            # 二线 (3)
            '佛山': 3, '济南': 3, '长春': 3, '大连': 3, '厦门': 3,
            '沈阳': 3, '昆明': 3, '石家庄': 3, '南昌': 3, '哈尔滨': 3,
            '太原': 3, '贵阳': 3, '乌鲁木齐': 3, '兰州': 3, '南宁': 3,
            '福州': 3, '中山': 3, '潍坊': 3, '盐城': 3, '洛阳': 3,
            '芜湖': 3, '扬州': 3,
            # 三线及以下 (2)
            '三亚': 2, '万宁': 2,
        }

        #应用映射 未匹配到的城市设置为默认等级3（二线城市）
        self.df["city_level"] = self.df["city_clean"].map(city_tier_map).fillna(3)
        
        #城市编码 使用标签编码器
        le = LabelEncoder()
        self.df["city_encoded"] = le.fit_transform(self.df["city"].fillna("未知"))
        self.label_encoder["city"] = le
        
        #区域特征，提取直辖市/一线城市
        self.df["is_tirer1"] = (self.df["city_level"] >= 4).astype(int)
        
        return self

    def extract_text_features(self):
        """文本特征"""
        #构建文件
        title_col = 'title' if 'title' in self.df.columns else 'job_title'
        desc_col = 'description' if 'description' in self.df.columns else 'job_description'

        #对以上两个特征进行合并
        self.df["text"] = self.df[title_col].fillna('') + ' ' + self.df[desc_col].fillna('')
        if self.df["text"].str.len().sum() == 0:
            print("文本数据为空")
            for i in range(10):
                self.df[f"text_feature_{i}"] = 0
            return self

        try:
            #使用字符集和刺激特征
            tfidf_char = TfidfVectorizer(
                max_features=30,  #保留最重要的30个特征
                analyzer='char',  #使用字符更新单元
                ngram_range=(2,4), #提取2-4给字符进行组合
            )

            tfidf_word = TfidfVectorizer(
                max_features=20,  # 保留最重要的20个特征
                analyzer='word',  #过滤英文引用词the is at
                stop_words="english",
                ngram_range=(1, 2),  # 提取1-2给单词进行组合
            )

            #字符集特征
            char_matrix = tfidf_char.fit_transform(self.df["text"].fillna(""))
            char_features = char_matrix.toarray()

            #词级特征
            word_matrix = tfidf_word.fit_transform(self.df["text"].fillna(""))
            word_features = word_matrix.toarray()

            #合并特征
            combined_features = np.hstack([char_features, word_features])

            #降维
            #如果特征少于20列全保留 超过20取20
            n_components = min(20,combined_features.shape[1])
            #通过SVD压缩成20列稠密数值特征 在拼接到原始数据中 作为后续模型训练新特征
            if n_components > 1:
                svd = TruncatedSVD(n_components=n_components,random_state=42)
                text_features = svd.fit_transform(combined_features)
                for i in range(text_features.shape[1]):
                    self.df[f"text_feature_{i}"] = text_features[:,i]

            else:
                for i in range(min(10,combined_features.shape[1])):
                    self.df[f"text_feature_{i}"] = combined_features[:,i]


        except Exception as e:
            print(f"文本特征提取出错：{e}")
            for i in range(10):
                self.df[f"text_feature_{i}"] = 0

        return self

    def create_derived_features(self):
        """衍生特征"""
        # 薪资范围比例
        self.df['salary_range_ratio'] = (self.df['salary_max_parsed'] - self.df['salary_min_parsed']) / \
                                        (self.df['salary_min_parsed'] + 1)

        # 经验和教育交互
        if 'experience_years' in self.df.columns and 'education_level' in self.df.columns:
            self.df['exp_edu_interaction'] = self.df['experience_years'] * self.df['education_level']
            self.df['exp_edu_ratio'] = self.df['experience_years'] / (self.df['education_level'] + 1)

        # 技能丰富
        self.df['skill_richness'] = self.df['skill_count'] / 10

        # 薪资等级
        self.df['salary_level'] = pd.qcut(self.df['salary_target'], q=5, labels=False)

        # 工作经验等级
        if 'experience_level' in self.df.columns:
            self.df['experience_level_squared'] = self.df['experience_level'] ** 2

        return self

    def prepare_features(self):
        """准备特征"""
        # 基础特征
        feature_cols = [
            'skill_count', 'salary_range_ratio', 'skill_richness',
            'city_level', 'city_encoded', 'company_scale_level'
        ]

        # 经验特征
        if 'experience_years' in self.df.columns:
            feature_cols.append('experience_years')
        if 'experience_level' in self.df.columns:
            feature_cols.append('experience_level')
        if 'experience_level_squared' in self.df.columns:
            feature_cols.append('experience_level_squared')

        # 教育特征
        if 'education_level' in self.df.columns:
            feature_cols.append('education_level')

        # 交互特征
        interaction_cols = ['exp_edu_interaction', 'exp_edu_ratio']
        for col in interaction_cols:
            if col in self.df.columns:
                feature_cols.append(col)

        # 公司特征
        company_cols = [col for col in self.df.columns if col.startswith('company_type_')]
        feature_cols.extend(company_cols)

        # 行业特征
        industry_cols = [col for col in self.df.columns if col.startswith('industry_')]
        feature_cols.extend(industry_cols)

        # 技能特征
        skill_cols = [col for col in self.df.columns if col.startswith('skill_') and
                      col not in ['skill_count', 'skill_richness']]
        feature_cols.extend(skill_cols[:25])

        # 技能组合
        combo_cols = [col for col in self.df.columns if col.startswith('skill_combo_')]
        feature_cols.extend(combo_cols)

        # 技能类别
        category_cols = [col for col in self.df.columns if col.startswith('skill_category_')]
        feature_cols.extend(category_cols)

        # 文本特征
        text_cols = [col for col in self.df.columns if col.startswith('text_feature_')]
        feature_cols.extend(text_cols[:15])

        # 区域特征
        region_cols = [col for col in self.df.columns if col.startswith('region_')]
        feature_cols.extend(region_cols)

        # 去重
        feature_cols = list(set(feature_cols))
        available_cols = [c for c in feature_cols if c in self.df.columns]

        print(f"特征工程完成，共 {len(available_cols)} 个特征")
        print(f"特征列表: {available_cols[:15]}...")

        # 处理缺失值
        for col in available_cols:
            if self.df[col].isnull().any():
                self.df[col] = self.df[col].fillna(0)

        self.feature_cols = available_cols
        return self.df, available_cols

    def data_partition(self):
        # 特征工程
        print(f"{'=' * 50}\n开始特征工程\n{'=' * 50}")
        # 调用特征工程类完成特征工程
        self.clean_data()
        self.parse_salary()
        self.encode_experience()
        self.encode_education()
        self.extract_skills()
        self.company_features()
        self.extract_city()
        self.extract_text_features()
        self.create_derived_features()
        df_processed, feature_names = self.prepare_features()

        # 3. 准备训练数据
        # X = df_processed[feature_cols].values
        # y = df_processed['salary_target'].values
        #
        # if len(X) == 0 or len(y) == 0:
        #     print("没有有效数据")
        #     return None, None
        #
        # # 标准化
        # scaler = RobustScaler()
        # X_scaled = scaler.fit_transform(X)
        #
        # # 划分数据
        # X_train, X_test, y_train, y_test = train_test_split(
        #     X_scaled, y, test_size=0.2, random_state=42
        # )
        # print(f"X_train: {X_train}, X_test: {X_test}, y_train: {y_train}, y_test: {y_test}")
        # print(f"\n训练集大小: {len(X_train)}, 测试集大小: {len(X_test)}")
        return df_processed, feature_names



if __name__ == '__main__':
    engineer = FeatureEngineer()
    # engineer.parse_salary()
    # engineer.company_features()
    # engineer.extract_skills()
    engineer.data_partition()
    # engineer.extract_text_features()
