"""轻量级线程安全 TTL 内存缓存。

用于缓存统计可视化等重计算接口的聚合结果，避免每次请求都
全表扫描 + Python 端逐行解析薪资。单进程 Flask 下有效。
"""
import threading
import time
from functools import wraps

from flask import request


class TTLCache:
    """带过期时间的线程安全内存缓存。"""

    def __init__(self, ttl=300):
        self._ttl = ttl
        self._store = {}
        self._lock = threading.Lock()

    def get(self, key):
        """命中返回 (value, True)，否则返回 (None, False)。"""
        with self._lock:
            item = self._store.get(key)
            if not item:
                return None, False
            value, expire_at = item
            if time.time() > expire_at:
                self._store.pop(key, None)
                return None, False
            return value, True

    def set(self, key, value, ttl=None):
        with self._lock:
            self._store[key] = (value, time.time() + (ttl if ttl is not None else self._ttl))

    def clear(self):
        """清空全部缓存（数据写入后调用以立即生效）。"""
        with self._lock:
            self._store.clear()

    def pop(self, prefix):
        """按 key 前缀清除缓存项。"""
        with self._lock:
            keys = [k for k in self._store if k.startswith(prefix)]
            for k in keys:
                self._store.pop(k, None)


# 统计模块全局缓存实例：默认 5 分钟过期
stats_cache = TTLCache(ttl=300)


def cached(key, ttl=300):
    """缓存路由返回值；支持 ?refresh=1 强制刷新。"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = key
            force_refresh = (
                request.args.get('refresh', '').lower() in ('1', 'true', 'yes')
                if has_request_context_safe() else False
            )
            if not force_refresh:
                value, hit = stats_cache.get(cache_key)
                if hit:
                    return value
            result = func(*args, **kwargs)
            stats_cache.set(cache_key, result, ttl=ttl)
            return result
        return wrapper
    return decorator


def has_request_context_safe():
    """安全地判断是否处于请求上下文（装饰器在路由中使用时始终为真）。"""
    try:
        return bool(request)
    except RuntimeError:
        return False


def invalidate_stats_cache():
    """数据写入后调用，清空统计缓存以使新数据立即生效。"""
    stats_cache.clear()
