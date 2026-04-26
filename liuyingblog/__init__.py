# 这将确保在Django启动时Celery app也被加载
from .celery import app as celery_app

__all__ = ('celery_app',)
