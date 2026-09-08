import os
import re
from ..services.data_cleaner import EDUCATION_MAP, extract_skills

# RapidOCR 引擎全局复用（懒加载，首次使用才初始化）
_ocr_engine = None


def _needs_ocr(text):
    """判断提取文本是否疑似乱码/图片型 PDF，需要 OCR 兜底。"""
    if not text or len(text.strip()) < 20:
        return True  # 几乎无文本 → 图片型
    if '\ufffd' in text:
        return True  # 替换符 → 编码损坏
    cn = sum(1 for ch in text if '\u4e00' <= ch <= '\u9fff')  # 中文字符数
    dots = sum(1 for ch in text if ch == '·')  # 乱码占位符（点号）
    if cn < 5 and dots > max(5, len(text) * 0.05):
        return True  # 中文简历但中文字符极少 + 大量点号 → 字体映射丢失
    return False


def _ocr_pdf(filepath):
    """把 PDF 每页渲染为图片并用 RapidOCR 识别（图片型/乱码 PDF 兜底）。"""
    global _ocr_engine
    try:
        import pymupdf
    except ImportError:
        try:
            import fitz as pymupdf
        except ImportError:
            return ''
    try:
        if _ocr_engine is None:  # 首次调用时加载模型（约 3-5 秒）
            from rapidocr_onnxruntime import RapidOCR
            _ocr_engine = RapidOCR()
        import numpy as np
        doc = pymupdf.open(filepath)
        parts = []
        for page in doc:
            pix = page.get_pixmap(dpi=150)  # 150 DPI 兼顾清晰度与速度
            samples = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                pix.height, pix.width, pix.n
            )
            if pix.n == 4:  # RGBA → RGB
                samples = samples[:, :, :3]
            result, _ = _ocr_engine(samples)
            if result:
                parts.append('\n'.join(item[1] for item in result))
        doc.close()
        return '\n'.join(parts)
    except Exception:
        return ''


class ResumeParser:
    """简历解析服务"""
    @staticmethod
    def parse_text(text):
        skills = extract_skills(text)
        experience = ResumeParser._extract_experience(text)
        education = ResumeParser._extract_education(text)
        return {
            'skills': skills,
            'experience_years': experience,
            'education_level': education,
            'city': ResumeParser._extract_city(text),
            'job_title': ResumeParser._extract_job_title(text),
            'company_size': ResumeParser._extract_company_size(text),
            'text_length': len(text),
        }

    @staticmethod
    def _extract_city(text):
        # 常见城市列表，按优先级匹配
        cities = [
            '北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '南京',
            '西安', '重庆', '苏州', '天津', '长沙', '郑州', '青岛', '大连',
            '厦门', '合肥', '济南', '福州', '东莞', '佛山', '无锡', '宁波',
        ]
        for city in cities:
            if city in text:
                return city
        return ''

    @staticmethod
    def _extract_job_title(text):
        # 应聘意向、技术岗位等正则模式
        patterns = [
            r'(?:应聘|求职|目标|意向)[职位岗位]*[：:\s]*([^\n，,。；;]{2,20})',
            r'(Python|Java|前端|后端|算法|数据|测试|运维|产品)[^\n]{0,12}(?:工程师|开发|经理|专员)',
        ]
        # 依次尝试匹配
        for pattern in patterns:
            # 忽略大小写搜索
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # 取捕获组或整段匹配
                return (match.group(1) if match.lastindex else match.group(0)).strip()
        return ''

    @staticmethod
    def _extract_company_size(text):
        # 人数区间、以上、少于等规模表述
        patterns = [
            r'(\d+\s*[-~到至]\s*\d+\s*人)',
            r'(\d+\s*人\s*以上)',
            r'(少于\s*\d+\s*人)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                # 去掉空格后返回
                return match.group(1).replace(' ', '')
        return ''

    @staticmethod
    def _extract_experience(text):
        # 中文/英文工作年限表述
        patterns = [
            r'(\d+)\s*年\s*(以上)?\s*(工作|开发|相关)?经验',
            r'工作(\d+)年',
            r'(\d+)years?',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # 上限 20 年，避免异常大数
                return min(int(match.group(1)), 20)
        return 0

    @staticmethod
    def _extract_education(text):
        # 遍历学历关键词映射
        for key, val in EDUCATION_MAP.items():
            if key in text:
                return val
        return 3

    @staticmethod
    def extract_text(filepath):
        """从简历文件提取纯文本，供预览与解析共用"""
        ext = os.path.splitext(filepath)[1].lower()
        text = ''

        if ext == '.txt':
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
        elif ext == '.pdf':
            # 第一优先 pymupdf（提取质量最好，保留单词完整性）
            try:
                import pymupdf
            except ImportError:
                try:
                    import fitz as pymupdf  # 旧版包名兼容
                except ImportError:
                    pymupdf = None
            if pymupdf is not None:
                try:
                    doc = pymupdf.open(filepath)
                    text = '\n'.join(page.get_text() for page in doc)
                    doc.close()
                except Exception:
                    text = ''
            # 第二优先 PyPDF2 回退
            if not text:
                try:
                    from PyPDF2 import PdfReader
                    reader = PdfReader(filepath)
                    for page in reader.pages:
                        text += page.extract_text() or ''
                except Exception:
                    text = ''
            # 第三优先 OCR 兜底：乱码 / 图片型 / 特殊字体编码
            if _needs_ocr(text):
                ocr_text = _ocr_pdf(filepath)
                if ocr_text:
                    text = ocr_text
        elif ext in ('.doc', '.docx'):
            # docx：XML 全文本解析（段落/表格/文本框/结构化标签全覆盖）
            # doc（老格式二进制）：python-docx 无法读取，给用户明确提示
            try:
                import zipfile
                if zipfile.is_zipfile(filepath):  # 标准 docx 是 zip 容器
                    with zipfile.ZipFile(filepath) as z:
                        xml = z.read('word/document.xml').decode('utf-8', errors='ignore')
                    # 按 <w:p> 分块（段落/表格单元格/文本框都按段落结构包含 w:p）
                    blocks = []
                    for pm in re.finditer(r'<w:p[ >].*?</w:p>', xml, re.S):
                        t_vals = re.findall(r'<w:t[^>]*>(.*?)</w:t>', pm.group(0), re.S)
                        line = ''.join(t_vals).replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
                        if line.strip():
                            blocks.append(line.strip())
                    text = '\n'.join(blocks)
                else:
                    text = '[提示] 该文件是旧版 .doc 二进制格式，python-docx 无法直接读取，请在 Word/WPS 中另存为 .docx 后重新上传。'
            except Exception:
                text = ''
        else:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()

        return text or ''

    @staticmethod
    def parse_file(filepath):
        text = ResumeParser.extract_text(filepath)  # 先提取纯文本
        return ResumeParser.parse_text(text)  # 对提取文本做结构化解析