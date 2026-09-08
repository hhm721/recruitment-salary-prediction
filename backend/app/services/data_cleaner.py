"""数据清洗服务：全量 ETL 与专项字段清洗（薪资/学历/经验/城市/岗位/技能/描述）。"""
from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime
from typing import Optional

from .. import db
from ..models import JobRaw, JobClean
from .geo_data import normalize_city
from ..utils.logger import get_logger

logger = get_logger(__name__)


EDUCATION_MAP = {  # 学历文本到有序等级 0-5 的映射表
    '不限': 0, '经验不限': 0, '学历不限': 0,
    '初中': 1, '高中': 1, '中专': 2, '中技': 2,
    '大专': 2, '本科': 3, '学士': 3, '硕士': 4, '研究生': 4, '博士': 5,
}

EXPERIENCE_MAP = {  # 经验文本到近似年数的映射表
    '不限': 0, '经验不限': 0, '应届': 0, '应届生': 0, '实习生': 0,
    '在校生': 0, '1年以下': 0, '一年以下': 0,
    '1-3年': 2, '1到3年': 2, '3-5年': 4, '3到5年': 4,
    '5-10年': 7, '5到10年': 7, '10年以上': 10, '十年以上': 10,
}

# 城市经济等级：数值越高代表薪资溢价越高（一线 > 新一线 > 二线 > 其他）
CITY_LEVEL_MAP = {  # 城市名到经济等级编码
    '北京': 4, '上海': 4, '广州': 4, '深圳': 4,
    '杭州': 3, '成都': 3, '重庆': 3, '武汉': 3, '西安': 3,
    '苏州': 3, '南京': 3, '天津': 3, '长沙': 3, '郑州': 3,
    '东莞': 3, '佛山': 3, '宁波': 3, '青岛': 3, '无锡': 3,
    '合肥': 2, '济南': 2, '福州': 2, '厦门': 2, '大连': 2,
    '昆明': 2, '沈阳': 2, '哈尔滨': 2, '长春': 2, '南昌': 2,
    '石家庄': 2, '贵阳': 2, '南宁': 2, '太原': 2, '兰州': 2,
}

JOB_LEVELS = ('管理', '高级', '初级', '技术', '其他')  # 岗位级别分类枚举

# 技能关键词表：从职位描述中提取技能的基准词表
SKILL_KEYWORDS = [
    'Python', 'Java', 'JavaScript', 'Go', 'C++', 'C#', 'PHP', 'Ruby', 'Swift', 'Kotlin',
    'MySQL', 'Redis', 'MongoDB', 'Oracle', 'PostgreSQL', 'SQLServer', 'SQLite',
    'Django', 'Flask', 'Spring', 'SpringBoot', 'SpringMVC', 'MyBatis', 'Vue', 'React', 'Angular',
    'Node.js', 'Express', 'Nginx', 'Apache', 'Tomcat',
    'Linux', 'Docker', 'Kubernetes', 'Git', 'SVN', 'Jenkins',
    'HTML', 'CSS', 'TypeScript', 'Webpack', 'Vite',
    '机器学习', '深度学习', 'TensorFlow', 'PyTorch', '数据分析', '数据挖掘', '算法', '数据结构',
    'Hadoop', 'Spark', 'Flink', 'Kafka', 'Elasticsearch',
    '微服务', '分布式', '高并发', '性能优化', '面向对象',
    '后端开发', '前端开发', '全栈开发', '数据库开发', '测试开发', '运维开发',
    'Windows', 'macOS', 'Android', 'iOS', 'Flutter', 'React Native',
    '爬虫', 'Scrapy', 'Selenium', '自动化测试', '单元测试',
    'RESTful', 'GraphQL', 'WebSocket', 'TCP/IP', 'HTTP',
    '设计模式', '架构设计', '领域驱动', '敏捷开发',
    # 简历常见补充技能（2026-09 扩充）
    'Excel', 'Word', 'PowerPoint', 'WPS',
    'Maven', 'Gradle', 'npm', 'Yarn', 'jQuery', 'Bootstrap', 'ElementUI', 'UniApp', '微信小程序',
    'Hive', 'HBase', 'ClickHouse', 'SparkSQL', 'FlinkSQL', 'DataX', 'Airflow',
    'Tableau', 'PowerBI', 'SPSS', 'MATLAB', 'R语言',
    'Photoshop', 'Axure', 'Figma',
    'AWS', '阿里云', '腾讯云',
    'AI', 'NLP', '计算机视觉', '推荐系统', 'ChatGPT', 'LangChain',
    'Vue3', 'Vuex', 'Pinia', 'Web3.js',
    # 常见写法变体（normalize 阶段统一为标准名）
    'Golang', 'Nodejs', 'Node', 'Reactjs', 'Vuejs', 'K8s', 'SQL', 'Postgres', 'Mongo',
]

# 技能名标准化映射：各种写法 → 标准名
SKILL_NORMALIZE_MAP = {
    # Go 语言
    'golang': 'Go', 'go语言': 'Go', 'go lang': 'Go',
    # JavaScript
    'js': 'JavaScript', 'javascript': 'JavaScript', 'java script': 'JavaScript',
    # Python
    'python3': 'Python', 'python2': 'Python', 'py': 'Python',
    # Vue
    'vue.js': 'Vue', 'vuejs': 'Vue', 'vue3': 'Vue',
    # React
    'react.js': 'React', 'reactjs': 'React', 'react.jsx': 'React',
    # Node.js
    'nodejs': 'Node.js', 'node': 'Node.js', 'nodejs ': 'Node.js',
    # C 系列
    'c++': 'C++', 'cpp': 'C++', 'c plus plus': 'C++',
    'c#': 'C#', 'csharp': 'C#', 'c sharp': 'C#',
    # 数据库
    'mysql': 'MySQL', 'my sql': 'MySQL',
    'mongodb': 'MongoDB', 'mongo': 'MongoDB',
    'postgresql': 'PostgreSQL', 'postgres': 'PostgreSQL', 'pg': 'PostgreSQL',
    'oracle数据库': 'Oracle', 'oracle': 'Oracle',
    'redis': 'Redis',
    'sql': 'SQL', 'sqlserver': 'SQL Server', 'mssql': 'SQL Server', 'mssqlserver': 'SQL Server', 'sqlite': 'SQLite',
    # 其他常见
    'html5': 'HTML', 'html': 'HTML',
    'css3': 'CSS', 'css': 'CSS',
    'typescript': 'TypeScript', 'ts': 'TypeScript',
    'kubernetes': 'Kubernetes', 'k8s': 'Kubernetes',
    'docker': 'Docker',
    'linux': 'Linux',
    'git': 'Git',
    'nginx': 'Nginx',
    'springboot': 'Spring Boot', 'spring boot': 'Spring Boot', 'springmvc': 'Spring MVC',
    'django': 'Django', 'flask': 'Flask',
    '机器学习': '机器学习', '深度学习': '深度学习',
    '数据分析': '数据分析', '数据挖掘': '数据挖掘',
    '算法': '算法', '数据结构': '数据结构',
    '面向对象': '面向对象', '后端开发': '后端开发',
    '数据库开发': '数据库开发', 'windows': 'Windows',
}


def normalize_skill_name(skill: str) -> str:
    """将各种写法的技能名统一为标准名。"""
    if not skill:
        return ''
    key = str(skill).strip().lower().replace(' ', '')
    if key in SKILL_NORMALIZE_MAP:
        return SKILL_NORMALIZE_MAP[key]
    # 不在映射表中的，返回首字母大写的原词
    original = str(skill).strip()
    return original if original else ''

# 简易中文停用词（职位描述 TF-IDF 用）
CN_STOP_WORDS = {  # 分词后需过滤的无信息词
    '的', '了', '和', '是', '在', '有', '与', '及', '等', '为', '对', '中', '上',
    '下', '到', '以', '将', '并', '或', '也', '都', '很', '更', '最', '可', '能',
    '会', '要', '被', '把', '从', '而', '但', '如果', '因为', '所以', '我们',
    '你们', '他们', '以及', '进行', '工作', '公司', '岗位', '职位', '要求',
    '负责', '相关', '具有', '以上', '以下', '优先', '良好', '熟悉', '了解',
    '掌握', '具备', '能力', '经验', '年', '岁', '元', '万', '千', 'the', 'and',
    'or', 'to', 'of', 'in', 'a', 'an', 'for', 'with', 'on', 'at', 'is', 'are',
}

# 福利/待遇噪声词：爬虫常写入 skills，会污染 Top-N One-Hot 与 TF-IDF 词表
BENEFIT_NOISE = {
    '五险一金', '补充医疗保险', '定期体检', '年终奖', '年底双薪', '带薪年假',
    '餐补', '餐饮补贴', '交通补助', '交通补贴', '通讯补贴', '住房补贴',
    '加班补助', '全勤奖', '节日福利', '员工旅游', '免费班车', '弹性工作',
    '股票期权', '绩效奖金', '专业培训', '周末双休', '双休', '朝九晚五',
    '包吃', '包住', '食宿', '无试用期', '不加班', '加班费', '高温补贴',
    '通讯津贴', '话补', '房补', '饭补', '团建', '下午茶', '零食',
    # 补充爬虫常见福利/待遇噪声
    '做五休二', '做六休一', '出国机会', '出国旅游', '年度旅游', '定期团建',
    '零食下午茶', '员工食堂', '免费宿舍', '提供住宿', '免费住宿', '带薪病假',
    '弹性上下班', '加班调休', '年度调薪', '调薪', '绩效工资', '岗位晋升',
    '晋升通道', '晋升空间', '技能培训', '员工培训', '节日礼品', '生日福利',
    '生日会', '交通方便', '地铁直达', '团队聚餐', '六险一金', '五险',
    '六险', '13薪', '14薪', '15薪', '16薪', '13薪/14薪', '年底双薪',
    '工作氛围好', '氛围好', '发展空间大', '平台大', '成长快', '大牛带队',
    '牛人带教', '核心团队', '业务稳定', '管理规范', '周末双休',
    '包住宿', '包吃住', '免费住宿', '包食宿', '管吃管住', '提供食宿',
    '包吃包住', '工作餐', '免费三餐',
}

# 经验/身份类噪声词：爬虫将经验要求混入技能标签
EXPERIENCE_NOISE = {
    '在校生', '应届生', '应届', '实习生', '实习', '经验不限', '不限经验',
    '无需经验', '无经验', '一年以下', '一年以上', '经验', '应届毕业生',
    '0-1年', '1年以下', '3-5年', '5-10年', '10年以上', '1-3年', '3-5年',
    '3-4年', '4-5年', '5-8年', '8-10年', '10年', '1年', '3年', '5年',
}

# 明显非技能的模糊词：领域/描述词混入技能榜，按需过滤
NON_SKILL_WORDS = {
    '方案', '培训', '计算机', '办公软件', '编程语言', '计算机科学',
    '软件开发', '软件工程', '技术支持', '需求分析', '解决方案',
    '在校生', '应届生', '实习生', '工作内容', '任职要求', '岗位职责',
    '福利待遇', '团队氛围', '公司文化', '弹性', '双休', '加班', '出差',
    # 学科/领域/动作类非技能词
    '机械', '数学', '英语', '通信', '维护', '电子', '开发', '管理',
    '编程', 'erp', '数据库', '调试', '网络', '运维', '测试', '自动化',
    '维护', '沟通', '协调', '文档', '汇报', '项目', '团队', '领导',
    # 岗位/文档/领域类补充
    '项目管理', '电气', '新能源', '测试用例', '技术文档', '技术方案',
    '软件测试', '方案设计', '软件', 'it', '服务器', '编程', '研发',
    '产品', '运营', '销售', '客服', '行政', '人事', '财务', '市场',
}



# 技能包含关系：已有 A 技能则自动视为已有 B 技能（避免建议补充重复/从属技能）
SKILL_INCLUDE_MAP = {
    # 关系型数据库 → 都包含 SQL 语言
    'MySQL': ['SQL'],
    'PostgreSQL': ['SQL'],
    'Oracle': ['SQL'],
    'SQL Server': ['SQL'],
    'SQLite': ['SQL'],
    # 前端框架 → 都基于 JavaScript + HTML + CSS
    'Vue': ['JavaScript', 'HTML', 'CSS'],
    'React': ['JavaScript', 'HTML', 'CSS'],
    'Angular': ['JavaScript', 'HTML', 'CSS'],
    'TypeScript': ['JavaScript'],
    'Node.js': ['JavaScript'],
    'Next.js': ['React', 'JavaScript', 'HTML', 'CSS'],
    'Nuxt.js': ['Vue', 'JavaScript', 'HTML', 'CSS'],
    # 后端框架 → 对应语言
    'Django': ['Python'],
    'Flask': ['Python'],
    'FastAPI': ['Python'],
    'Scrapy': ['Python'],
    'Spring': ['Java'],
    'Spring Boot': ['Java'],
    'Spring MVC': ['Java'],
    'MyBatis': ['Java'],
    'Express': ['JavaScript', 'Node.js'],
    # 移动开发
    'React Native': ['JavaScript', 'React'],
    'Flutter': ['Dart'],
    # 运维/云原生
    'Kubernetes': ['Docker', 'Linux'],
    'Docker': ['Linux'],
    'Nginx': ['Linux'],
    # 其他常见包含
    'Selenium': ['Python', '自动化测试'],
    'Appium': ['Python', '自动化测试'],
    'JUnit': ['Java', '单元测试'],
    'Pytest': ['Python', '单元测试'],
}


def expand_user_skills(user_skills: list) -> set:
    """根据技能包含关系，扩展用户已有技能集合。"""
    expanded = set(str(s).strip().lower() for s in user_skills if str(s).strip())
    changed = True
    while changed:
        changed = False
        for skill in list(expanded):
            # 找标准名
            std = normalize_skill_name(skill)
            if std in SKILL_INCLUDE_MAP:
                for included in SKILL_INCLUDE_MAP[std]:
                    key = included.strip().lower()
                    if key not in expanded:
                        expanded.add(key)
                        changed = True
    return expanded


def _to_yuan(num, unit):
    """将数字按单位折算为元。"""
    unit = (unit or '').strip()  # 规范化单位字符串
    unit_lower = unit.lower()  # 转小写以匹配 k/w 等英文单位
    if unit in ('万',) or unit_lower == 'w':  # 万元单位
        return num * 10000  # 折算为元
    if unit in ('千',) or unit_lower == 'k':  # 千元单位
        return num * 1000  # 折算为元
    return num  # 无单位则原样返回（视为元）


def _wan_amounts_in_text(text):
    """提取文本中以「万/W」为单位的数额（含「50-70万」左侧无单位的数字）。"""
    if not text:
        return []
    nums = []
    # 明确带万/W 的数字：50万、1.5万
    for m in re.finditer(r'(\d+\.?\d*)\s*[万wW]', text):
        nums.append(float(m.group(1)))
    # 区间右侧带万、左侧可省略：50-70万、40-70万/年
    m = re.search(
        r'(\d+\.?\d*)\s*[万wW]?\s*[-~～至到]\s*(\d+\.?\d*)\s*[万wW]',
        text,
    )
    if m:
        nums.extend([float(m.group(1)), float(m.group(2))])
    return nums


def _has_valid_salary_raw(raw_job: Optional[JobRaw]) -> bool:
    """原始薪资文本是否可清洗：salary_raw 为空/空白则跳过。"""
    if raw_job is None:
        return False
    text = raw_job.salary_raw
    if text is None:
        return False
    return bool(str(text).strip())


def _is_annual_salary(text):
    """
    判断薪资文本是否为年薪（需 ÷12 得到月薪）。
    - 显式 /年、年薪 → 年薪
    - 显式 /月、月薪 → 月薪
    - 类似「50-70万」「40-70万/年」：带「万」且达到年包量级（≥8万）→ 年薪
    """
    if not text:
        return False
    # 明确写了月薪则不当作年薪
    if re.search(r'[/／]\s*月|每月|月薪', text):
        return False
    if re.search(r'[/／]\s*年|每年|年薪|年度', text):
        return True
    lower = text.lower()
    if '/year' in lower or 'per year' in lower or 'annually' in lower:
        return True

    # 「50-70万」「20-40万」等未写 /年 的年包：万元数额 ≥8 视为年薪
    wan_nums = _wan_amounts_in_text(text)
    if wan_nums and max(wan_nums) >= 8:
        return True
    return False


def _to_monthly(low, high, avg, *, is_annual, months=12):
    """将解析得到的金额统一折算为月薪（元）。年薪按 12 个月均摊；月薪可按 N 薪放大。"""
    if is_annual:
        # 年包总额 ÷ 12 → 月薪；已是年薪时不再叠加 N 薪
        return low / 12.0, high / 12.0, avg / 12.0
    if months != 12:
        factor = months / 12.0
        return low * factor, high * factor, avg * factor
    return low, high, avg


def parse_salary(salary_text):
    """
    解析薪资文本，返回 (min_k, max_k, avg_k)，单位为 K（千元/月）。
    年薪（如 35-50万/年、50-70万）会先按 12 个月折算为月薪再转 K。
    无法解析（面议/空值/非法格式）返回 (None, None, None)。
    """
    result = parse_salary_yuan(salary_text)  # 先按元解析
    if result is None:  # 无法解析
        return None, None, None  # 返回三元空值
    low, high, avg = result  # 解构元为单位的区间
    return round(low / 1000, 2), round(high / 1000, 2), round(avg / 1000, 2)  # 转为 K 并保留两位小数


def parse_salary_yuan(salary_text):
    """
    解析薪资文本，返回 (min_yuan, max_yuan, avg_yuan) 月薪（元）。
    支持：万/千/K/元 区间、年薪÷12（含未标注的大额「万」年包）、N薪折算、日薪×22、K以上取 1.25 倍中值。
    """
    if salary_text is None:  # 空输入
        return None  # 无法解析
    text = str(salary_text).strip()  # 转为字符串并去首尾空白
    if not text or '面议' in text:  # 空文本或面议
        return None  # 无法解析

    original = text  # 保留原文供年薪推断
    is_annual = _is_annual_salary(original)  # 是否年薪（在去掉修饰前判断）

    # 提取 N 薪（如 ·14薪）；年包不再叠加 N 薪
    months = 12  # 默认按 12 薪计算
    m_salary = re.search(r'[·\-.]?\s*(\d+)\s*薪', text)  # 匹配 N 薪后缀
    if m_salary:  # 找到 N 薪
        months = int(m_salary.group(1))  # 读取薪数
        text = re.sub(r'[·\-.]\s*\d+\s*薪', '', text)  # 去掉带分隔符的薪数描述
        text = re.sub(r'\d+\s*薪', '', text)  # 去掉剩余薪数描述

    text = text.replace(' ', '').replace('，', ',').replace('～', '-')  # 统一分隔符与空白
    # 去掉周期后缀，避免干扰数字匹配（金额语义已由 is_annual 记录）
    text = re.sub(r'[/／]\s*(?:年|月|year)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'年薪|每年|每月|月薪|年度', '', text)

    # 日薪：90-110/天 或 100元/天
    daily_range = re.search(  # 匹配日薪区间
        r'(\d+\.?\d*)\s*[-~至到]\s*(\d+\.?\d*)\s*(?:元)?\s*/?\s*天', text
    )
    if daily_range:  # 命中日薪区间
        low = float(daily_range.group(1)) * 22  # 日薪下限 × 22 工作日得月薪
        high = float(daily_range.group(2)) * 22  # 日薪上限 × 22
        avg = (low + high) / 2  # 取区间中值
        return low, high, avg  # 返回月薪（元）

    daily_single = re.search(r'(\d+\.?\d*)\s*(?:元)?\s*/\s*天', text)  # 匹配单一日薪
    if daily_single:  # 命中单一日薪
        val = float(daily_single.group(1)) * 22  # 折算月薪
        return val, val, val  # 上下限与中值相同

    # 下限型：20K以上 / 20k+ / 20万起
    above = re.search(r'(\d+\.?\d*)\s*([万Ww千Kk])?\s*(以上|\+|起)', text)  # 匹配「以上/+/起」
    if above:  # 命中下限型薪资
        base = _to_yuan(float(above.group(1)), above.group(2))  # 下限折算为元
        # 上限按下限 1.5 倍；中值取 1.25 倍
        low, high, avg = base, base * 1.5, base * 1.25  # 估算区间与中值
        return _to_monthly(low, high, avg, is_annual=is_annual, months=months)

    # 区间：1.2万-2万 / 6千-1.2万 / 5000-8000元 / 15-25K / 35-50万/年 / 50-70万
    range_pat = re.search(  # 匹配带单位的薪资区间
        r'(\d+\.?\d*)\s*([万Ww千Kk])?\s*[-~至到]\s*(\d+\.?\d*)\s*([万Ww千Kk])?\s*元?',
        text,
    )
    if range_pat:  # 命中区间型
        u1, u2 = range_pat.group(2), range_pat.group(4)  # 两侧单位
        # 仅一侧有单位时两侧共用（如 15-25K）
        if u1 and not u2:  # 仅左侧有单位
            u2 = u1  # 右侧沿用左侧单位
        elif u2 and not u1:  # 仅右侧有单位
            u1 = u2  # 左侧沿用右侧单位
        low = _to_yuan(float(range_pat.group(1)), u1)  # 下限折算为元
        high = _to_yuan(float(range_pat.group(3)), u2)  # 上限折算为元
        # 无单位且数值较小，按 K 理解（如 15-25）
        if not u1 and not u2 and low < 1000 and high < 1000:  # 小数值无单位
            low *= 1000  # 按 K 乘 1000
            high *= 1000
        avg = (low + high) / 2  # 区间中值
        low, high, avg = _to_monthly(low, high, avg, is_annual=is_annual, months=months)
        # 兜底：解析后仍呈离谱月薪且原文含「万」→ 再按年薪 ÷12
        if not is_annual and ('万' in original or 'w' in original.lower()) and avg >= 80000:
            low, high, avg = low / 12.0, high / 12.0, avg / 12.0
        return low, high, avg

    # 单值带单位：20K / 2万 / 50万/年
    single = re.search(r'(\d+\.?\d*)\s*([万Ww千Kk])\s*(?:元)?', text)  # 匹配单值带单位
    if single:  # 命中单值
        val = _to_yuan(float(single.group(1)), single.group(2))  # 折算为元
        low, high, avg = _to_monthly(val, val, val, is_annual=is_annual, months=months)
        if not is_annual and ('万' in original or 'w' in original.lower()) and avg >= 80000:
            low, high, avg = low / 12.0, high / 12.0, avg / 12.0
        return low, high, avg

    # 纯数字（较大视为元）
    plain = re.search(r'(\d+\.?\d*)\s*元?', text)  # 匹配纯数字
    if plain:  # 命中纯数字
        val = float(plain.group(1))  # 读取数值
        if val < 1000:  # 小数值按 K 理解
            val *= 1000
        low, high, avg = _to_monthly(val, val, val, is_annual=is_annual, months=months)
        return low, high, avg

    return None  # 所有规则均未匹配


def parse_experience(exp_text):
    """将经验文本转为数值年数。"""
    if not exp_text:  # 空经验
        return 0  # 默认 0 年
    text = str(exp_text).strip()  # 规范化文本
    for key, val in EXPERIENCE_MAP.items():  # 遍历预定义映射
        if key in text:  # 关键词命中
            return int(val)  # 返回对应年数

    # 3-5年 / 1年以上
    range_m = re.search(r'(\d+)\s*[-~至到]\s*(\d+)\s*年', text)  # 匹配「N-M年」
    if range_m:  # 命中区间
        return round((int(range_m.group(1)) + int(range_m.group(2))) / 2)  # 取区间中值年数

    above_m = re.search(r'(\d+)\s*年\s*以上', text)  # 匹配「N年以上」
    if above_m:  # 命中下限型
        return int(above_m.group(1))  # 返回下限年数

    single_m = re.search(r'(\d+)\s*年', text)  # 匹配「N年」
    if single_m:  # 命中单值
        return int(single_m.group(1))  # 返回年数

    match = re.search(r'(\d+)', text)  # 兜底提取任意数字
    if match:  # 找到数字
        return int(match.group(1))  # 作为年数返回
    return 0  # 无法解析则默认 0


def parse_education(edu_text):
    """将学历文本转为有序等级 0-5。"""
    if not edu_text:  # 空学历
        return 0  # 默认不限
    text = str(edu_text).strip()  # 规范化文本
    for key, val in EDUCATION_MAP.items():  # 遍历学历映射
        if key in text:  # 关键词命中
            return val  # 返回等级
    return 0  # 未匹配则默认不限


def parse_city_level(city_text):
    """按城市经济水平编码为等级数值。"""
    if not city_text:  # 空城市
        return 1  # 默认最低档
    city = normalize_city(str(city_text))  # 规范化城市名
    if city in CITY_LEVEL_MAP:  # 精确命中
        return CITY_LEVEL_MAP[city]  # 返回等级
    for key, level in CITY_LEVEL_MAP.items():  # 模糊匹配（包含关系）
        if key in city or city in key:
            return level  # 返回匹配等级
    return 1  # 未知城市默认最低档


def clean_job_title(title):
    """从岗位名称提取级别/类别。"""
    if title is None:  # 空标题
        return '其他'  # 归为其他
    t = str(title).lower()  # 转小写便于关键词匹配
    if any(k in t for k in ('总监', '经理', '主管', '负责人')):  # 管理岗关键词
        return '管理'
    if any(k in t for k in ('高级', '资深', '专家')):  # 高级岗关键词
        return '高级'
    if any(k in t for k in ('实习', '助理', '初级')):  # 初级岗关键词
        return '初级'
    if any(k in t for k in ('工程师', '开发', '技术')):  # 技术岗关键词
        return '技术'
    return '其他'  # 未命中则归为其他


def job_level_onehot(level):
    """岗位级别 One-Hot。"""
    return {f'job_{lv}': 1 if level == lv else 0 for lv in JOB_LEVELS}  # 为每个级别生成 0/1 特征


def parse_skills_field(skill_str):
    """解析 skills 字段（JSON 数组或逗号分隔）。"""
    if skill_str is None:  # 空字段
        return []  # 无技能
    if isinstance(skill_str, list):  # 已是列表
        return [str(s).strip() for s in skill_str if str(s).strip()]  # 去空白后返回
    text = str(skill_str).strip()  # 转为字符串
    if not text:  # 空字符串
        return []
    try:
        skills = json.loads(text)  # 尝试 JSON 解析
        if isinstance(skills, list):  # JSON 数组
            return [str(s).strip() for s in skills if str(s).strip()]  # 规范化列表项
    except (json.JSONDecodeError, TypeError):  # JSON 非法
        pass  # 降级为分隔符切分
    return [s.strip() for s in re.split(r'[,，、;/|]', text) if s.strip()]  # 按常见分隔符切分


_SKILL_PATTERNS = None


def _build_skill_patterns():
    """
    预编译技能匹配正则（模块加载后首次调用时构建一次）：
    - 英文/符号技能：前后加「非字母数字」边界，防止 Java 误匹配 JavaScript、Go 误匹配 Google；
    - 中文技能：子串匹配（中文无词边界概念）；
    - 按名称长度降序排列，长技能（JavaScript）先于短技能（Java）匹配，避免短词抢占。
    """
    patterns = []
    for skill in SKILL_KEYWORDS:
        if re.search(r'[\u4e00-\u9fff]', skill):
            patterns.append((skill, re.compile(re.escape(skill))))
        else:
            patterns.append((
                skill,
                re.compile(r'(?<![A-Za-z0-9])' + re.escape(skill) + r'(?![A-Za-z0-9])', re.IGNORECASE),
            ))
    patterns.sort(key=lambda x: len(x[0]), reverse=True)
    return patterns


def _normalize_skill_text(text):
    """归一化解析文本：PDF 提取常见的不换行空格/零宽字符改为普通空格或删除。"""
    if not text:
        return text
    text = text.replace('\xa0', ' ')  # 不换行空格 → 普通空格
    text = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', text)  # 删除零宽字符
    return text


def _is_chinese_skill(skill):
    """技能名是否含中文（中文匹配无词边界概念）。"""
    return bool(re.search(r'[\u4e00-\u9fff]', skill))


def _find_span_in(text, skill, occupied, compact_mode=False):
    """
    在文本中查找技能首个不与已占用区间重叠的匹配位置。
    - compact_mode=False：原始文本（保留空格），英文技能带词边界；
    - compact_mode=True ：紧凑文本（去空白），词条也去空格，PDF 拆词兜底；
    - 中文技能一律子串匹配（中文无词边界）；
    - occupied 记录长技能位置，防止短技能命中长技能内部（javascript 里的 java）。
    """
    esc = re.escape(skill.replace(' ', '') if compact_mode else skill)
    if _is_chinese_skill(skill):
        for m in re.finditer(esc, text):
            if any(s <= m.start() < e for s, e in occupied):
                continue
            return (m.start(), m.end())
        return None
    pat = re.compile(r'(?<![A-Za-z0-9])' + esc + r'(?![A-Za-z0-9])', re.IGNORECASE)
    for m in pat.finditer(text):
        if any(s <= m.start() < e for s, e in occupied):
            continue  # 落在已识别长技能内部，视为子串覆盖，跳过
        return (m.start(), m.end())
    return None


def extract_skills(text):
    """从文本中按关键词表提取技能（词边界匹配 + PDF 拆词兜底，防子串误报）。"""
    if not text:  # 空文本
        return []
    text = _normalize_skill_text(text)  # 清理 PDF 提取的不可见字符
    global _SKILL_PATTERNS
    if _SKILL_PATTERNS is None:  # 首次调用时构建并缓存
        _SKILL_PATTERNS = _build_skill_patterns()
    compact = re.sub(r'\s+', '', text)  # 去所有空白：处理 PDF 把单词拆开的情况
    occupied_raw = []  # 原始文本坐标系占用区间（主匹配）
    occupied_compact = []  # 紧凑文本坐标系占用区间（兜底匹配）
    found = []  # 命中技能列表（保序去重）
    seen = set()
    for skill, pattern in _SKILL_PATTERNS:  # 遍历预编译模式（长技能在前）
        key = skill.lower()
        if key in seen:  # 该写法已处理过
            continue
        hit = False
        if pattern.search(text):  # 主匹配：词边界（原始归一化文本）
            span = _find_span_in(text, skill, occupied_raw)
            if span is not None:
                occupied_raw.append(span)  # 原始文本坐标系登记占位
                hit = True
        if not hit:
            # 兜底匹配：紧凑文本（处理 PDF 拆词如 'P y t h o n'），同样带词边界防误报
            span = _find_span_in(compact, skill, occupied_compact, compact_mode=True)
            if span is not None:
                occupied_compact.append(span)  # 紧凑文本坐标系登记占位
                hit = True
        if not hit:
            continue  # 未命中，或被更长技能覆盖（如 javascript 内的 java）
        seen.add(key)
        std = normalize_skill_name(skill) or skill  # 统一为标准技能名
        std_key = std.lower()
        if std_key != key and std_key in seen:
            # 标准名已被其他写法识别（如 nodejs→Node.js 已被 Node.js 识别），跳过不重复
            continue
        if std_key != key:  # 标准名与原始写法不同（如 golang→Go），登记标准名
            seen.add(std_key)
        found.append(std)
    return found


def _is_benefit_tag(skill: str) -> bool:
    """判断是否为福利/经验/非技能噪声标签。"""
    s = (skill or '').strip()
    if not s:
        return True
    if s in BENEFIT_NOISE or s in EXPERIENCE_NOISE or s in NON_SKILL_WORDS:
        return True
    # 经验年限类：3-5年 / 3-4年 / 1-3年 / 5-10年 / 3年以上 / 1年以下 / 2年
    if re.fullmatch(r'\d+(\.\d+)?\s*[-~至到]\s*\d+(\.\d+)?\s*年', s) or \
       re.fullmatch(r'\d+(\.\d+)?\s*年以上', s) or \
       re.fullmatch(r'\d+(\.\d+)?\s*年以下', s) or \
       re.fullmatch(r'\d+\s*年', s):
        return True
    # 短中文福利短语（无英文技术特征）常见于爬虫 skills
    if re.fullmatch(r'[\u4e00-\u9fff]{2,6}', s) and s not in SKILL_KEYWORDS:
        welfare_hints = ('险', '假', '补', '奖', '福利', '双休', '班车', '体检', '旅游', '餐', '团', '薪', '训', '待', '勤', '房')
        if any(h in s for h in welfare_hints):
            return True
    return False


def _filter_tech_skills(skills: list) -> list:
    """过滤福利噪声，保留技术向技能标签。"""
    out = []
    seen = set()
    for s in skills or []:
        name = str(s).strip()
        if not name or _is_benefit_tag(name):
            continue
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(name)
    return out


def tokenize_job_text(text: str) -> list:
    """职位文本简易分词：中文 ≥2 字 + 英文/数字技术 token。"""
    if not text:
        return []
    tokens = re.findall(r'[\u4e00-\u9fff]{2,}|[A-Za-z][A-Za-z0-9.+#]*', str(text))
    return [
        t for t in tokens
        if t.lower() not in CN_STOP_WORDS
        and t not in CN_STOP_WORDS
        and t not in BENEFIT_NOISE
        and not _is_benefit_tag(t)
    ]


def build_skill_features_payload(skills: list, vocab: list) -> dict:
    """构建 skill_features JSON 结构（固定词表 One-Hot）。"""
    skill_set = {str(s).strip().lower() for s in (skills or []) if str(s).strip()}
    features = {}
    for s in vocab:
        key = f'skill_{str(s).replace(" ", "_")}'
        features[key] = 1 if str(s).strip().lower() in skill_set else 0
    return {'top_skills': list(vocab), 'features': features}


def build_provisional_text_features(text: str, vocab: list = None) -> dict:
    """
    ETL 阶段无全局语料时的文本特征：按技能关键词表做二值袋。
    专项 clean_description 会用 TF-IDF 覆盖为更优向量。
    """
    vocab = list(vocab or SKILL_KEYWORDS)
    text_l = (text or '').lower()
    features = {}
    top_terms = []
    for i, term in enumerate(vocab):
        hit = 1.0 if (term.lower() in text_l or term in (text or '')) else 0.0
        features[f'text_{i}'] = hit
        if hit > 0:
            top_terms.append({'term': term, 'weight': 1.0})
    return {
        'features': features,
        'vocab': vocab,
        'top_terms': top_terms[:10],
        'source': 'keyword',
    }


def build_tfidf_text_features(vec, feature_names: list) -> dict:
    """将 TF-IDF 行向量写成稠密 features（含 0），保证列对齐可被下游使用。"""
    features = {
        f'text_{j}': round(float(vec[j]), 6)
        for j in range(len(feature_names))
    }
    top_terms = sorted(
        (
            (feature_names[j], float(vec[j]))
            for j in range(len(feature_names))
            if vec[j] > 0
        ),
        key=lambda x: -x[1],
    )[:10]
    return {
        'features': features,
        'vocab': list(feature_names),
        'top_terms': [{'term': t, 'weight': round(w, 4)} for t, w in top_terms],
        'source': 'tfidf',
    }


def resolve_job_skills(raw: Optional[JobRaw], clean_job: Optional[JobClean] = None) -> list:
    """综合原始/清洗表技能字段与标题描述，提取并过滤技术技能。"""
    source = None
    if raw and raw.skills:
        source = raw.skills
    elif clean_job and clean_job.skills:
        source = clean_job.skills
    skills = _filter_tech_skills(parse_skills_field(source))
    title = ''
    desc = ''
    if raw:
        title = raw.title or ''
        desc = raw.description or ''
    elif clean_job:
        title = clean_job.title or ''
    if not skills:
        skills = extract_skills(f'{title} {desc} {source or ""}')
    else:
        # 补充关键词表命中，避免 skills 字段过短
        extra = extract_skills(f'{title} {desc}')
        merged = list(skills)
        seen = {s.lower() for s in merged}
        for s in extra:
            if s.lower() not in seen:
                merged.append(s)
                seen.add(s.lower())
        skills = merged
    skills = _filter_tech_skills(skills)
    # 最后统一技能名标准化
    normalized = []
    seen_std = set()
    for s in skills:
        std = normalize_skill_name(s)
        if std and std.lower() not in seen_std:
            normalized.append(std)
            seen_std.add(std.lower())
    return normalized


def _get_raw_for_clean(clean_job: JobClean) -> Optional[JobRaw]:  # 根据清洗记录取关联原始岗位
    if clean_job.raw_id:  # 有关联原始记录 ID
        return db.session.get(JobRaw, clean_job.raw_id)  # 按 ID 查询原始岗位
    return None  # 无关联则返回空


class DataCleaner:  # 数据清洗服务类
    """数据清洗服务"""

    @staticmethod  # 静态方法
    def clean_single(raw_job: JobRaw) -> JobClean:  # 单条原始记录 → 清洗记录
        salary_min, salary_max, salary_avg = parse_salary(raw_job.salary_raw)  # 解析原始薪资文本
        if salary_min is None and raw_job.salary_min:  # 文本解析失败但有结构化下限
            salary_min = float(raw_job.salary_min)  # 使用已有下限
        if salary_max is None and raw_job.salary_max:  # 文本解析失败但有结构化上限
            salary_max = float(raw_job.salary_max)  # 使用已有上限
        if salary_avg is None:  # 仍无平均值
            if salary_min is not None and salary_max is not None:  # 上下限齐全
                salary_avg = (salary_min + salary_max) / 2  # 取算术平均
            elif salary_min is not None:  # 仅下限
                salary_avg = salary_min  # 用下限代替
            elif salary_max is not None:  # 仅上限
                salary_avg = salary_max  # 用上限代替

        skills_list = parse_skills_field(raw_job.skills)  # 解析 skills 字段
        skills_list = _filter_tech_skills(skills_list)
        normalized = []
        seen_std = set()
        for s in skills_list:
            std = normalize_skill_name(s)
            if std and std.lower() not in seen_std:
                normalized.append(std)
                seen_std.add(std.lower())
        skills_list = normalized
        if not skills_list:  # 字段无技能
            combined = f"{raw_job.title or ''} {raw_job.description or ''}"  # 拼接标题与描述
            skills_list = extract_skills(combined)  # 从文本提取技能
        else:
            extra = extract_skills(f"{raw_job.title or ''} {raw_job.description or ''}")
            seen = {s.lower() for s in skills_list}
            for s in extra:
                if s.lower() not in seen:
                    skills_list.append(s)
                    seen.add(s.lower())
            skills_list = _filter_tech_skills(skills_list)

        city = normalize_city(raw_job.city) or raw_job.city  # 规范化城市名，失败保留原值
        job_level = clean_job_title(raw_job.title)  # 从标题推断岗位级别

        # ETL 阶段即写入技能/文本特征，避免专项清洗未跑或失败时字段为空
        skill_payload = build_skill_features_payload(skills_list, SKILL_KEYWORDS)
        text_blob = f"{raw_job.title or ''} {raw_job.description or ''} {' '.join(skills_list)}"
        text_payload = build_provisional_text_features(text_blob, SKILL_KEYWORDS)

        clean_job = JobClean(  # 构建清洗后记录
            raw_id=raw_job.id,  # 关联原始 ID
            platform=raw_job.platform,  # 平台
            title=raw_job.title,  # 岗位标题
            company=raw_job.company,  # 公司
            city=city,  # 规范化城市
            salary_min=salary_min,  # 薪资下限（K）
            salary_max=salary_max,  # 薪资上限（K）
            salary_avg=salary_avg,  # 薪资均值（K）
            experience_years=parse_experience(raw_job.experience),  # 经验年数
            education_level=parse_education(raw_job.education),  # 学历等级
            skills=json.dumps(skills_list, ensure_ascii=False),  # 技能 JSON 字符串
            skill_count=len(skills_list),  # 技能数量
            city_level=parse_city_level(city),  # 城市经济等级
            job_level=job_level,  # 岗位级别类别
            job_features=json.dumps(job_level_onehot(job_level), ensure_ascii=False),  # 岗位 One-Hot
            skill_features=json.dumps(skill_payload, ensure_ascii=False),  # 技能 One-Hot
            text_features=json.dumps(text_payload, ensure_ascii=False),  # 文本特征（关键词袋，可被专项覆盖）
            clean_time=datetime.now(),  # 清洗时间
        )
        return clean_job  # 返回清洗结果（未入库）

    @staticmethod  # 静态方法
    def _apply_clean_to_existing(existing: JobClean, clean_job: JobClean):
        """将新清洗结果覆盖到已有 job_clean 记录。"""
        existing.platform = clean_job.platform
        existing.title = clean_job.title
        existing.company = clean_job.company
        existing.city = clean_job.city
        existing.salary_min = clean_job.salary_min
        existing.salary_max = clean_job.salary_max
        existing.salary_avg = clean_job.salary_avg
        existing.experience_years = clean_job.experience_years
        existing.education_level = clean_job.education_level
        existing.skills = clean_job.skills
        existing.skill_count = clean_job.skill_count
        existing.city_level = clean_job.city_level
        existing.job_level = clean_job.job_level
        existing.job_features = clean_job.job_features
        # 同步写入特征，不再清空（专项清洗可再次覆盖优化）
        existing.skill_features = clean_job.skill_features
        existing.text_features = clean_job.text_features
        existing.clean_time = clean_job.clean_time

    @staticmethod  # 静态方法
    def clean_batch(platform=None, limit=1000, after_id=0):
        """批量清洗原始数据：salary_raw 为空的记录直接跳过；已存在则覆盖更新。"""
        query = JobRaw.query.filter(JobRaw.id > after_id)  # 按 ID 游标分页
        if platform:  # 指定平台
            query = query.filter_by(platform=platform)  # 按平台过滤
        raw_jobs = query.order_by(JobRaw.id.asc()).limit(limit).all()  # 限制批量条数

        if not raw_jobs:  # 本批无原始行
            return 0, after_id, 0  # cleaned, cursor, fetched

        cleaned_count = 0  # 本批成功清洗计数
        last_id = after_id
        for raw_job in raw_jobs:  # 逐条处理
            last_id = raw_job.id
            # 需求：salary_raw 为空不清洗，直接过滤
            if not _has_valid_salary_raw(raw_job):
                continue
            clean_job = DataCleaner.clean_single(raw_job)  # 执行单条清洗
            existing = JobClean.query.filter_by(raw_id=raw_job.id).first()  # 是否已有清洗记录
            if existing:  # 已存在则覆盖更新
                DataCleaner._apply_clean_to_existing(existing, clean_job)
            else:  # 不存在则新增
                db.session.add(clean_job)
            if hasattr(raw_job, 'is_cleaned'):
                raw_job.is_cleaned = 1  # 兼容旧字段，不再作为是否清洗的判断依据
            cleaned_count += 1  # 计数加一

        db.session.commit()  # 提交本批事务
        return cleaned_count, last_id, len(raw_jobs)  # 清洗数、游标、本批拉取数

    @staticmethod  # 静态方法
    def clean_all_uncleaned(platform=None):
        """清洗全部原始数据（跳过 salary_raw 为空；每次点击全量执行）。"""
        logger.info('开始全量数据清洗 platform=%s', platform or 'all')
        total = 0  # 累计清洗总数
        after_id = 0  # ID 游标
        while True:  # 循环直到无更多原始数据
            count, after_id, fetched = DataCleaner.clean_batch(
                platform=platform, limit=500, after_id=after_id,
            )
            if fetched == 0:  # 本批无原始行，结束
                break
            total += count  # 累加清洗成功数
            logger.info(
                '全量清洗进度 cleaned=%s fetched=%s after_id=%s total=%s',
                count, fetched, after_id, total,
            )
        logger.info('全量数据清洗完成 platform=%s cleaned_total=%s', platform or 'all', total)
        return total  # 返回总清洗条数（兼容原接口）

    # ── 专项清洗 ──────────────────────────────────────────────

    @staticmethod  # 静态方法
    def clean_salary(platform=None):  # 专项：重新解析并更新薪资字段
        """薪资数据清洗：salary_raw 为空则跳过；年包（如 50-70万）按 ÷12 写回月薪。"""
        logger.info('开始薪资数据清洗 platform=%s', platform or 'all')
        query = JobClean.query  # 从清洗表查询
        if platform:  # 可选平台过滤
            query = query.filter_by(platform=platform)
        jobs = query.all()  # 加载全部目标记录

        updated, cleared, skipped = 0, 0, 0  # 成功更新 / 清空 / 跳过计数
        for job in jobs:  # 逐条更新薪资
            raw = _get_raw_for_clean(job)  # 取关联原始记录
            # 需求：salary_raw 为空不清洗，直接过滤
            if not _has_valid_salary_raw(raw):
                skipped += 1
                continue

            salary_text = raw.salary_raw
            parsed = parse_salary(salary_text)  # 重新解析（含年薪 ÷12）
            if parsed[0] is None:  # 解析失败
                job.salary_min = None  # 清空下限
                job.salary_max = None  # 清空上限
                job.salary_avg = None  # 清空均值
                cleared += 1  # 清空计数
            else:  # 解析成功
                job.salary_min, job.salary_max, job.salary_avg = parsed  # 写回三元组
                updated += 1  # 更新计数
            job.clean_time = datetime.now()  # 刷新清洗时间

        db.session.commit()  # 提交变更
        result = {
            'updated': updated,
            'cleared': cleared,
            'skipped': skipped,
            'total': len(jobs),
        }
        logger.info('薪资数据清洗完成 %s', result)
        return result

    @staticmethod  # 静态方法
    def clean_education(platform=None):  # 专项：更新学历等级字段
        """学历数据清洗：文本学历 → 有序等级 0-5。"""
        logger.info('开始学历数据清洗 platform=%s', platform or 'all')
        query = JobClean.query
        if platform:
            query = query.filter_by(platform=platform)
        jobs = query.all()

        updated = 0  # 更新计数
        for job in jobs:
            raw = _get_raw_for_clean(job)  # 取原始记录
            edu_text = raw.education if raw else None  # 原始学历文本
            job.education_level = parse_education(edu_text)  # 写入等级
            job.clean_time = datetime.now()
            updated += 1

        db.session.commit()
        result = {'updated': updated, 'total': len(jobs)}
        logger.info('学历数据清洗完成 %s', result)
        return result

    @staticmethod  # 静态方法
    def clean_experience(platform=None):  # 专项：更新经验年数字段
        """工作经验数据清洗：文本经验 → 数值年数。"""
        logger.info('开始工作经验数据清洗 platform=%s', platform or 'all')
        query = JobClean.query
        if platform:
            query = query.filter_by(platform=platform)
        jobs = query.all()

        updated = 0
        for job in jobs:
            raw = _get_raw_for_clean(job)
            exp_text = raw.experience if raw else None  # 原始经验文本
            years = parse_experience(exp_text)  # 解析为年数
            job.experience_years = int(years) if years is not None else 0  # 写入整型年数
            job.clean_time = datetime.now()
            updated += 1

        db.session.commit()
        result = {'updated': updated, 'total': len(jobs)}
        logger.info('工作经验数据清洗完成 %s', result)
        return result

    @staticmethod  # 静态方法
    def clean_city(platform=None):  # 专项：规范化城市并更新等级
        """城市数据清洗：规范化城市名 + 经济等级编码。"""
        logger.info('开始城市数据清洗 platform=%s', platform or 'all')
        query = JobClean.query
        if platform:
            query = query.filter_by(platform=platform)
        jobs = query.all()

        updated = 0
        for job in jobs:
            raw = _get_raw_for_clean(job)
            city_text = (raw.city if raw and raw.city else job.city) or ''  # 优先原始城市
            city = normalize_city(city_text) or city_text  # 规范化，失败保留原文
            job.city = city  # 写回城市
            job.city_level = parse_city_level(city)  # 写回经济等级
            job.clean_time = datetime.now()
            updated += 1

        db.session.commit()
        result = {'updated': updated, 'total': len(jobs)}
        logger.info('城市数据清洗完成 %s', result)
        return result

    @staticmethod  # 静态方法
    def clean_job(platform=None):  # 专项：更新岗位级别与 One-Hot
        """岗位数据清洗：从 title 提取级别并 One-Hot。"""
        logger.info('开始岗位数据清洗 platform=%s', platform or 'all')
        query = JobClean.query
        if platform:
            query = query.filter_by(platform=platform)
        jobs = query.all()

        updated = 0
        for job in jobs:
            level = clean_job_title(job.title)  # 从标题推断级别
            job.job_level = level  # 写回级别
            job.job_features = json.dumps(job_level_onehot(level), ensure_ascii=False)  # 写回 One-Hot
            job.clean_time = datetime.now()
            updated += 1

        db.session.commit()
        result = {'updated': updated, 'total': len(jobs)}
        logger.info('岗位数据清洗完成 %s', result)
        return result

    @staticmethod  # 静态方法
    def clean_skills(platform=None, top_n=30):  # 专项：解析技能并生成固定词表 One-Hot
        """技能数据清洗：提取技术技能，按 SKILL_KEYWORDS(+数据补充) 写 skill_features。"""
        logger.info('开始技能数据清洗 platform=%s top_n=%s', platform or 'all', top_n)
        query = JobClean.query
        if platform:
            query = query.filter_by(platform=platform)
        jobs = query.all()

        skills_lists = []  # 每条岗位的技能列表
        for job in jobs:
            raw = _get_raw_for_clean(job)
            skills_lists.append(resolve_job_skills(raw, job))

        # 固定技术词表优先，再用数据高频技术技能补齐到 top_n
        vocab = list(SKILL_KEYWORDS)
        seen = {s.lower() for s in vocab}
        all_skills = [s for lst in skills_lists for s in lst]
        for s, _ in Counter(all_skills).most_common(max(top_n * 3, 50)):
            if s.lower() in seen or _is_benefit_tag(s):
                continue
            vocab.append(s)
            seen.add(s.lower())
            if len(vocab) >= max(len(SKILL_KEYWORDS), top_n):
                break

        updated = 0
        for i, (job, skills) in enumerate(zip(jobs, skills_lists)):
            payload = build_skill_features_payload(skills, vocab)
            job.skills = json.dumps(skills, ensure_ascii=False)
            job.skill_count = len(skills)
            job.skill_features = json.dumps(payload, ensure_ascii=False)
            job.clean_time = datetime.now()
            updated += 1
            if (i + 1) % 1000 == 0:  # 分批提交，降低长事务风险
                db.session.commit()

        db.session.commit()
        result = {
            'updated': updated,
            'total': len(jobs),
            'top_skills': vocab,
            'top_n': len(vocab),
        }
        logger.info(
            '技能数据清洗完成 updated=%s total=%s top_n=%s',
            result['updated'], result['total'], result['top_n'],
        )
        return result

    @staticmethod  # 静态方法
    def clean_description(platform=None, max_features=100):  # 专项：TF-IDF 向量化职位描述
        """职位描述数据清洗：标题+描述+技能 TF-IDF，写满稠密 text_features。"""
        from sklearn.feature_extraction.text import TfidfVectorizer  # 延迟导入 TF-IDF

        logger.info(
            '开始职位描述数据清洗 platform=%s max_features=%s',
            platform or 'all', max_features,
        )
        query = JobClean.query
        if platform:
            query = query.filter_by(platform=platform)
        jobs = query.all()
        if not jobs:  # 无数据
            logger.info('职位描述数据清洗跳过：无清洗数据')
            return {'updated': 0, 'total': 0, 'feature_count': 0}  # 空结果

        corpus = []  # 分词后的语料列表
        text_blobs = []  # 原始拼接文本（TF-IDF 全零时回退关键词特征）
        for job in jobs:
            raw = _get_raw_for_clean(job)
            title = (raw.title if raw else job.title) or ''
            desc = (raw.description if raw else '') or ''
            skills = (raw.skills if raw and raw.skills else job.skills) or ''
            if isinstance(skills, (list, dict)):
                skills = json.dumps(skills, ensure_ascii=False)
            raw_text = f'{title} {desc} {skills}'
            text_blobs.append(raw_text)
            tokens = tokenize_job_text(raw_text)
            corpus.append(' '.join(tokens))

        try:
            tfidf = TfidfVectorizer(
                max_features=max_features,
                ngram_range=(1, 1),  # 单字词优先，避免福利 bigram 霸占词表
                min_df=2 if len(jobs) >= 2 else 1,
                sublinear_tf=True,
                token_pattern=r'(?u)\S+',
            )
            matrix = tfidf.fit_transform(corpus)
            feature_names = list(tfidf.get_feature_names_out())
        except ValueError:
            # 语料过少无法向量化：回退关键词袋，保证字段非空
            for i, job in enumerate(jobs):
                payload = build_provisional_text_features(text_blobs[i], SKILL_KEYWORDS)
                job.text_features = json.dumps(payload, ensure_ascii=False)
                job.clean_time = datetime.now()
            db.session.commit()
            result = {'updated': len(jobs), 'total': len(jobs), 'feature_count': len(SKILL_KEYWORDS)}
            logger.info('职位描述数据清洗完成（关键词回退） %s', result)
            return result

        updated = 0
        for i, job in enumerate(jobs):
            row = matrix.getrow(i).toarray().ravel()
            if float(row.max()) <= 0:
                # 文档未命中全局词表时，回退关键词特征，避免 features 实际全空
                payload = build_provisional_text_features(text_blobs[i], SKILL_KEYWORDS)
            else:
                payload = build_tfidf_text_features(row, feature_names)
            job.text_features = json.dumps(payload, ensure_ascii=False)
            job.clean_time = datetime.now()
            updated += 1
            if (i + 1) % 1000 == 0:
                db.session.commit()

        db.session.commit()
        result = {
            'updated': updated,
            'total': len(jobs),
            'feature_count': len(feature_names),
        }
        logger.info('职位描述数据清洗完成 %s', result)
        return result
