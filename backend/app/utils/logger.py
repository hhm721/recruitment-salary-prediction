"""
后端日志工具：控制台 + 文件双输出，日志落盘至 backend/logs。
- 业务功能执行日志 / 错误写入 app.log、error.log
"""
from __future__ import annotations

import logging
import os
import threading
import time
from logging.handlers import RotatingFileHandler
from typing import List, Optional

# 根业务 logger 名，子模块用 get_logger(__name__) 继承配置
APP_LOGGER_NAME = 'recruitment'

_initialized = False
_cleanup_started = False
_log_paths: List[str] = []
_file_handlers: List[logging.Handler] = []
_cleanup_lock = threading.Lock()


def _resolve_log_dir(explicit: Optional[str] = None) -> str:
    """解析日志目录：优先入参 / 环境变量，默认 backend/logs。"""
    if explicit:
        log_dir = explicit
    else:
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        log_dir = os.getenv('LOG_DIR', os.path.join(backend_dir, 'logs'))
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


def _make_file_handler(path: str, level: int, formatter: logging.Formatter,
                       max_bytes: int, backup_count: int) -> RotatingFileHandler:
    handler = RotatingFileHandler(
        path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8',
    )
    handler.setLevel(level)
    handler.setFormatter(formatter)
    return handler


def clear_log_files(log_dir: Optional[str] = None) -> int:
    """
    清空日志文件内容（含滚动备份），释放磁盘占用。
    返回清理的文件数量。
    """
    cleared = 0
    paths = list(_log_paths)
    if log_dir:
        try:
            for name in os.listdir(log_dir):
                if name.endswith('.log') or '.log.' in name:
                    paths.append(os.path.join(log_dir, name))
        except OSError:
            pass

    # 先刷盘，再截断打开中的 handler 流
    with _cleanup_lock:
        for handler in list(_file_handlers):
            try:
                handler.acquire()
                try:
                    handler.flush()
                    stream = getattr(handler, 'stream', None)
                    if stream and hasattr(stream, 'seek') and hasattr(stream, 'truncate'):
                        stream.seek(0)
                        stream.truncate(0)
                        stream.flush()
                        cleared += 1
                finally:
                    handler.release()
            except Exception:
                continue

        seen = set()
        for path in paths:
            if not path or path in seen:
                continue
            seen.add(path)
            try:
                # 主文件已由 handler truncate；备份文件直接清空或删除
                if not os.path.isfile(path):
                    continue
                base = os.path.basename(path)
                if base.endswith('.log') and '.log.' not in base:
                    # 主日志：若未被 handler 覆盖则再 truncate 一次
                    with open(path, 'w', encoding='utf-8'):
                        pass
                    cleared += 1
                else:
                    os.remove(path)
                    cleared += 1
            except OSError:
                continue
    return cleared


def _start_log_cleanup_worker(log_dir: str, interval_seconds: int) -> None:
    """后台线程：每隔 interval_seconds 清空一次日志文件。"""
    global _cleanup_started
    if _cleanup_started or interval_seconds <= 0:
        return
    _cleanup_started = True

    def _loop():
        logger = logging.getLogger(APP_LOGGER_NAME)
        while True:
            time.sleep(interval_seconds)
            try:
                n = clear_log_files(log_dir)
                logger.info(
                    '定时清理日志完成 interval=%ss cleared=%s dir=%s',
                    interval_seconds, n, log_dir,
                )
            except Exception:
                # 清理失败不影响主业务
                try:
                    logger.exception('定时清理日志失败')
                except Exception:
                    pass

    thread = threading.Thread(
        target=_loop,
        name='log-cleaner',
        daemon=True,
    )
    thread.start()


def setup_logging(
    app=None,
    *,
    log_dir: Optional[str] = None,
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    error_file: Optional[str] = None,
    max_bytes: Optional[int] = None,
    backup_count: Optional[int] = None,
    clean_interval_minutes: Optional[int] = None,
) -> logging.Logger:
    """
    初始化全局日志（幂等）：
    - app.log：INFO+ 业务执行日志
    - error.log：ERROR+ 错误信息
    - 每隔 N 分钟清空日志文件内容（默认 30）
    """
    global _initialized

    cfg = getattr(app, 'config', {}) if app is not None else {}

    level_name = (log_level or cfg.get('LOG_LEVEL') or os.getenv('LOG_LEVEL', 'INFO')).upper()
    level = getattr(logging, level_name, logging.INFO)
    directory = _resolve_log_dir(log_dir or cfg.get('LOG_DIR'))
    filename = log_file or cfg.get('LOG_FILE') or os.getenv('LOG_FILE', 'app.log')
    err_filename = error_file or cfg.get('LOG_ERROR_FILE') or os.getenv('LOG_ERROR_FILE', 'error.log')
    max_bytes = int(max_bytes or cfg.get('LOG_MAX_BYTES') or os.getenv('LOG_MAX_BYTES', 10 * 1024 * 1024))
    backup_count = int(backup_count or cfg.get('LOG_BACKUP_COUNT') or os.getenv('LOG_BACKUP_COUNT', 5))
    clean_minutes = int(
        clean_interval_minutes
        if clean_interval_minutes is not None
        else cfg.get('LOG_CLEAN_INTERVAL_MINUTES')
        or os.getenv('LOG_CLEAN_INTERVAL_MINUTES', 30)
    )

    log_path = os.path.join(directory, filename)
    error_path = os.path.join(directory, err_filename)
    formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    root_app_logger = logging.getLogger(APP_LOGGER_NAME)
    root_app_logger.setLevel(level)
    root_app_logger.propagate = False

    if not _initialized:
        file_handler = _make_file_handler(log_path, level, formatter, max_bytes, backup_count)
        error_handler = _make_file_handler(
            error_path, logging.ERROR, formatter, max_bytes, backup_count,
        )
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)

        root_app_logger.addHandler(file_handler)
        root_app_logger.addHandler(error_handler)
        root_app_logger.addHandler(console_handler)

        _file_handlers.extend([file_handler, error_handler])
        _log_paths.extend([log_path, error_path])

        if app is not None:
            app.logger.handlers.clear()
            app.logger.setLevel(level)
            app.logger.propagate = False
            for handler in root_app_logger.handlers:
                app.logger.addHandler(handler)

        _initialized = True
        root_app_logger.info(
            '日志系统已初始化 app=%s error=%s level=%s clean_every=%smin',
            log_path, error_path, level_name, clean_minutes,
        )
        _start_log_cleanup_worker(directory, max(60, clean_minutes * 60))
    elif app is not None:
        if not app.logger.handlers:
            app.logger.setLevel(level)
            app.logger.propagate = False
            for handler in root_app_logger.handlers:
                app.logger.addHandler(handler)

    if app is not None:
        app.config['LOG_DIR'] = directory
        app.config['LOG_FILE_PATH'] = log_path
        app.config['LOG_ERROR_FILE_PATH'] = error_path
        app.config['LOG_CLEAN_INTERVAL_MINUTES'] = clean_minutes

    return root_app_logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    获取业务 logger。
    - name 为空：返回根业务 logger
    - name 为模块名：挂到 recruitment.* 下，继承文件/控制台 handler
    """
    if not name or name == APP_LOGGER_NAME:
        return logging.getLogger(APP_LOGGER_NAME)
    if name.startswith(APP_LOGGER_NAME + '.'):
        return logging.getLogger(name)
    return logging.getLogger(f'{APP_LOGGER_NAME}.{name}')
