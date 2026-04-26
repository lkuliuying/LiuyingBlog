import os
from celery import Celery

# 设置Django的默认设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'liuyingblog.settings')

app = Celery('liuyingblog')

# 使用字符串这里意味着worker不必序列化
# 配置对象到子进程。
app.config_from_object('django.conf:settings', namespace='CELERY')

# 从所有已注册的Django app configs中自动发现任务。
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
