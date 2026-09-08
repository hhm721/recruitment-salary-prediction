import os
import subprocess
import sys
import threading
import time
from datetime import datetime
from .. import db
from .. import create_app
from ..config import Config
from ..models import CrawlTask, JobRaw
from ..utils.cache import invalidate_stats_cache  # 爬虫入库后失效统计缓存


PLATFORM_SPIDER_MAP = {  # 业务平台名 → Scrapy 爬虫名映射
    'lagou': 'lagou',
    'liepin': 'liepin',
    'qcwy': 'qcwy',
    'zhilian': 'zhilian',
    'zhaopin': 'zhilian',  # 前端「智联招聘」value 为 zhaopin，映射到 zhilian 爬虫
    'all': 'all',
}

# Scrapy 日志中表示爬取阶段已结束（浏览器清理可能仍卡住）
_SCRAPY_DONE_MARKERS = (
    'Dumping Scrapy stats',
    'Spider closed',
    'Closing spider',
)


class CrawlService:
    """爬虫调度服务"""

    _running_tasks = {}
    # 串行执行，避免多平台同时拉起 Selenium/Chrome 互相抢占资源
    _spider_lock = threading.Lock()
    _poll_interval = 2  # 主循环轮询间隔（秒）
    _stall_rounds = 4  # 数据不再增长约 8s 且已出现完成日志时，判定任务完成
    _timeout = 600  # 单任务最长运行时间（秒）

    @classmethod
    def start_crawl(cls, platform='all', keyword=None, city=None, pages=None):
        keyword = keyword or Config.CRAWL_KEYWORD
        city = city or Config.CRAWL_CITY
        pages = pages or Config.CRAWL_PAGES

        platforms = list(PLATFORM_SPIDER_MAP.keys())
        platforms.remove('all')
        if platform != 'all':
            platforms = [platform]

        tasks = []
        for p in platforms:
            task = CrawlTask(
                platform=p,
                keyword=keyword,
                city=city,
                status='pending',
                created_at=datetime.now(),
            )
            db.session.add(task)
            db.session.flush()
            tasks.append(task)
        db.session.commit()
        for task in tasks:
            thread = threading.Thread(
                target=cls._run_spider,
                args=(task.id, task.platform, keyword, city, pages),
                daemon=True,  # 主进程退出时随主进程结束
            )
            thread.start()  # 异步启动，不阻塞 API 响应

        return [t.to_dict() for t in tasks]  # 返回任务摘要列表

    @classmethod
    def _run_spider(cls, task_id, platform, keyword, city, pages):
        app = create_app()  # 后台线程需独立 Flask 应用上下文

        with app.app_context():
            task = CrawlTask.query.get(task_id)
            if not task:
                return
            task.status = 'running'  # 标记开始执行
            task.start_time = datetime.now()
            task.error_msg = None
            db.session.commit()
            start_time = task.start_time  # 供回退计数与超时计算

            spider_name = PLATFORM_SPIDER_MAP.get(platform, platform)  # 解析 scrapy 爬虫名
            scrapy_dir = Config.SCRAPY_DIR
            cmd = cls._build_scrapy_cmd(spider_name, keyword, city, pages, task_id)
            env = cls._build_spider_env(keyword, city, pages, task_id)

            proc = None
            stdout_lines = []  # 标准输出日志缓冲
            stderr_lines = []  # 标准错误日志缓冲
            try:
                with cls._spider_lock:  # 全局串行：同时只跑一个 spider 进程
                    proc = subprocess.Popen(
                        cmd,
                        cwd=scrapy_dir,  # 工作目录为 scrapy 项目
                        env=env,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        encoding='utf-8',
                        errors='replace',  # 非法 UTF-8 替换而非崩溃
                    )
                    cls._running_tasks[task_id] = proc.pid  # 登记活跃 PID

                    threading.Thread(
                        target=cls._drain_pipe, args=(proc.stdout, stdout_lines), daemon=True
                    ).start()  # 异步读 stdout
                    threading.Thread(
                        target=cls._drain_pipe, args=(proc.stderr, stderr_lines), daemon=True
                    ).start()  # 异步读 stderr

                    deadline = time.time() + cls._timeout  # 绝对超时时刻
                    last_count = 0  # 上一轮入库数
                    stall_rounds = 0  # 连续无增长的轮数
                    scrapy_done = False  # 日志是否出现结束标记
                    returncode = None

                    while True:
                        returncode = proc.poll()  # 非阻塞检查进程是否结束
                        db.session.expire_all()
                        count = cls._count_task_jobs(task_id, platform, start_time)
                        print(count)
                        # 运行中同步采集数，前端刷新可见进度
                        if count != last_count:
                            last_count = count
                            stall_rounds = 0  # 有新增数据则重置停滞计数
                            running_task = CrawlTask.query.get(task_id)
                            if running_task:
                                running_task.total_count = count
                                db.session.commit()
                        elif count > 0:
                            stall_rounds += 1  # 有历史数据但本轮未增长
                        else:
                            # 无新增数据也计一次停滞：修复反爬空页任务 count 恒为 0，
                            # 原逻辑 stall_rounds 永不递增，任务一直 running，前端一直转圈
                            stall_rounds += 1

                        log_text = ''.join(stderr_lines) + ''.join(stdout_lines)
                        if any(marker in log_text for marker in _SCRAPY_DONE_MARKERS):
                            scrapy_done = True  # Scrapy 主流程已结束

                        if returncode is not None:
                            break  # 进程自然退出，跳出轮询

                        # Scrapy 已收尾且数据不再增长：结束卡住的浏览器进程并标记完成
                        if scrapy_done and stall_rounds >= cls._stall_rounds:
                            cls._kill_process(proc)
                            returncode = proc.poll()
                            cls._finalize_task(
                                task_id, platform,
                                returncode=returncode if returncode is not None else 0,
                                force_completed=True,
                            )
                            return

                        # 已有入库数据且长时间无增长，即使日志未捕获到结束标记也收尾
                        if count > 0 and stall_rounds >= cls._stall_rounds * 3:
                            cls._kill_process(proc)
                            returncode = proc.poll()
                            cls._finalize_task(
                                task_id, platform,
                                returncode=returncode if returncode is not None else 0,
                                force_completed=True,
                            )
                            return

                        if time.time() > deadline:
                            cls._kill_process(proc)  # 超时强杀
                            err = (''.join(stderr_lines) + '\n' + ''.join(stdout_lines)).strip()
                            cls._finalize_task(
                                task_id, platform,
                                returncode=-1,
                                error_msg=err or f'Crawl timeout ({cls._timeout}s)',
                            )
                            return

                        time.sleep(cls._poll_interval)  # 等待下一轮检查

                    err = (''.join(stderr_lines) + '\n' + ''.join(stdout_lines)).strip()
                    cls._finalize_task(
                        task_id,
                        platform,
                        returncode=returncode,
                        error_msg=err if returncode not in (0, None) else None,
                    )

            except FileNotFoundError as e:
                cls._finalize_task(
                    task_id, platform, returncode=-1,
                    error_msg=f'无法启动 scrapy: {e}. 请确认已安装 scrapy 且 Python 环境正确。',
                )
            except Exception as e:
                if proc is not None:
                    cls._kill_process(proc)  # 异常时清理子进程
                cls._finalize_task(task_id, platform, returncode=-1, error_msg=str(e))
            finally:
                cls._running_tasks.pop(task_id, None)  # 从活跃表移除
                # 若异常路径未写 end_time，兜底关闭
                task = CrawlTask.query.get(task_id)
                if task and task.status == 'running':
                    cls._finalize_task(task_id, platform, returncode=-1, error_msg='任务异常中断')

    @classmethod
    def _build_scrapy_cmd(cls, spider_name, keyword, city, pages, task_id):
        """用当前 Python 解释器启动 scrapy，避免 Windows PATH/脚本关联问题。"""
        return [
            sys.executable, '-u', '-m', 'scrapy', 'crawl', spider_name,  # -u 关闭缓冲，日志实时输出到管道
            '-a', f'keyword={keyword}',
            '-a', f'city={city}',
            '-a', f'pages={pages}',
            '-a', f'task_id={task_id}',
        ]

    @classmethod
    def _build_spider_env(cls, keyword, city, pages, task_id):
        """
        传递与 Flask Config / Scrapy settings 一致的数据库环境变量。
        注意：不可把缺省密码写成空字符串，否则会覆盖 Scrapy settings 中的 MYSQL_PASSWORD。
        """
        env = os.environ.copy()  # 继承当前进程环境
        env['CRAWL_KEYWORD'] = str(keyword)
        env['CRAWL_CITY'] = str(city)
        env['CRAWL_PAGES'] = str(pages)
        env['CRAWL_TASK_ID'] = str(task_id)
        env['DB_HOST'] = os.getenv('DB_HOST', 'localhost')
        env['DB_PORT'] = os.getenv('DB_PORT', '3306')
        env['DB_USER'] = os.getenv('DB_USER', 'root')
        env['DB_PASSWORD'] = os.getenv('DB_PASSWORD', 'root')  # 缺省与 Scrapy settings 一致
        env['DB_NAME'] = os.getenv('DB_NAME', 'recruitment_db')
        scrapy_dir = Config.SCRAPY_DIR  # Scrapy 项目根目录
        pythonpath = env.get('PYTHONPATH', '')
        if scrapy_dir not in pythonpath.split(os.pathsep):
            # 将 scrapy 目录加入 PYTHONPATH，便于导入 spider 包
            env['PYTHONPATH'] = scrapy_dir + (os.pathsep + pythonpath if pythonpath else '')
        return env

    @classmethod
    def _drain_pipe(cls, pipe, bucket):
        """后台线程持续读取 stdout/stderr，避免管道缓冲区满阻塞子进程。"""
        try:
            for line in iter(pipe.readline, ''):
                bucket.append(line)  # 累积日志行供后续判断
        except Exception:
            pass  # 管道关闭等异常忽略
        finally:
            try:
                pipe.close()
            except Exception:
                pass

    @classmethod
    def _count_task_jobs(cls, task_id, platform=None, start_time=None):
        """按 task_id 统计入库数；若无 task_id 关联则回退到平台+时间窗口。"""
        if task_id is None:
            return 0
        tid = str(task_id).strip()
        # 兼容 task_id 以字符串/数字形式入库
        count = JobRaw.query.filter(JobRaw.task_id == tid).count()
        if count == 0 and tid.isdigit():
            count = JobRaw.query.filter(JobRaw.task_id == str(int(tid))).count()
        if count == 0 and platform and start_time:
            # 旧数据无 task_id，或 ON DUPLICATE 未更新 task_id 时，用平台与开始时间近似统计
            count = JobRaw.query.filter(
                JobRaw.platform == platform,
                JobRaw.crawl_time >= start_time,
            ).count()
        return int(count or 0)

    @classmethod
    def _refresh_task_total_count(cls, task):
        """按库内实际入库数回写任务 total_count（统计总数区域）。"""
        if not task:
            return False
        count = cls._count_task_jobs(task.id, task.platform, task.start_time)
        if count != (task.total_count or 0):
            task.total_count = count
            return True
        return False

    @classmethod
    def _kill_process(cls, proc):
        if proc.poll() is not None:
            return  # 进程已退出
        try:
            if os.name == 'nt':
                # Windows：强制终止进程树（含 Chrome 子进程）
                subprocess.run(
                    ['taskkill', '/F', '/T', '/PID', str(proc.pid)],
                    capture_output=True,
                    timeout=30,
                )
            else:
                proc.terminate()  # Unix：先 SIGTERM 优雅退出
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()  # 超时再 SIGKILL
        except Exception:
            try:
                proc.kill()  # 兜底强杀
            except Exception:
                pass  # 忽略二次失败

    @classmethod
    def _finalize_task(cls, task_id, platform, returncode=None, error_msg=None, force_completed=False):
        """
        根据入库结果回写任务状态：
        - 进程成功退出，或已有数据入库 → 已完成
        - 强制完成（检测到 Scrapy 结束但进程卡住）→ 已完成
        - 否则 → 失败
        """
        task = CrawlTask.query.get(task_id)
        if not task:
            return  # 任务已被删除则跳过

        # 避免读取到会话缓存的旧计数
        db.session.expire_all()
        count = cls._count_task_jobs(task_id, platform, task.start_time)
        task.total_count = count  # 写入最终采集条数

        success = force_completed or returncode == 0 or count > 0  # 判定是否算成功
        if success:
            task.status = 'completed'
            # 有数据入库时，即使进程非 0 退出也不再展示失败信息
            if count > 0 or returncode == 0 or force_completed:
                if returncode not in (0, None) and count == 0 and error_msg:
                    task.error_msg = error_msg  # 极少数：强制完成但无数据仍保留错误
                else:
                    task.error_msg = None  # 正常完成清空错误
        else:
            task.status = 'failed'
            task.error_msg = (error_msg or f'scrapy exited with code {returncode}')[:2000]  # 截断防过长

        task.end_time = datetime.now()
        db.session.commit()
        # 进程刚结束时可能仍有少量 item 未提交：短暂后再统计一次并回写
        if count == 0:
            try:
                time.sleep(1.5)
                db.session.expire_all()
                task = CrawlTask.query.get(task_id)
                if task and cls._refresh_task_total_count(task):
                    if task.total_count > 0 and task.status != 'completed':
                        task.status = 'completed'
                        task.error_msg = None
                    db.session.commit()
            except Exception:
                db.session.rollback()
        # 爬虫入库已完成，失效统计缓存以使新数据立即生效
        try:
            invalidate_stats_cache()
        except Exception:
            pass


    @classmethod
    def get_tasks(cls, page=1, per_page=10):
        # 列表查询时，纠正僵尸运行状态，并回写未更新的采集总数
        cls._reconcile_stale_running_tasks()
        pagination = CrawlTask.query.order_by(
            CrawlTask.created_at.desc()  # 最新任务在前
        ).paginate(page=page, per_page=per_page, error_out=False)
        # 当前页任务再同步一次 total_count，确保前端采集数与库内一致
        page_changed = False
        for task in pagination.items:
            if cls._refresh_task_total_count(task):
                page_changed = True
        if page_changed:
            db.session.commit()
        return {
            'items': [t.to_dict() for t in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
        }

    @classmethod
    def _reconcile_stale_running_tasks(cls):
        """把已入库或超时仍显示运行中的任务修正为已完成/失败，并回写采集总数。"""
        running = CrawlTask.query.filter(CrawlTask.status == 'running').all()
        # 已结束但 total_count 仍为 0 的任务：数据可能在收尾后才提交，需补统计
        pending_count = (
            CrawlTask.query.filter(
                CrawlTask.status.in_(['completed', 'failed']),
                CrawlTask.total_count == 0,
            )
            .order_by(CrawlTask.id.desc())
            .limit(30)
            .all()
        )
        now = datetime.now()
        changed = False  # 是否有记录被修正
        for task in running:
            # 仍由当前进程调度跟踪的任务跳过
            if task.id in cls._running_tasks:
                continue
            count = cls._count_task_jobs(task.id, task.platform, task.start_time)
            elapsed = (now - task.start_time).total_seconds() if task.start_time else 0
            if count > 0:
                task.status = 'completed'  # 有数据则视为已成功
                task.total_count = count
                task.end_time = task.end_time or now
                task.error_msg = None
                changed = True
            elif elapsed >= cls._timeout:
                task.status = 'failed'  # 超时且无数据则失败
                task.end_time = task.end_time or now
                task.error_msg = task.error_msg or f'Crawl timeout ({cls._timeout}s)'
                changed = True
        print(pending_count)
        for task in pending_count:
            if cls._refresh_task_total_count(task):
                if task.total_count > 0 and task.status == 'failed':
                    # 实际已有入库数据时，失败态改为已完成更合理
                    task.status = 'completed'
                    task.error_msg = None
                    task.end_time = task.end_time or now
                changed = True
        if changed:
            db.session.commit()

    @classmethod
    def delete_task(cls, task_id):
        task = CrawlTask.query.get(task_id)
        if not task:
            return False, '任务不存在'
        cls._running_tasks.pop(task_id, None)  # 清除内存跟踪（不杀进程）
        db.session.delete(task)
        db.session.commit()
        return True, '任务已删除'
