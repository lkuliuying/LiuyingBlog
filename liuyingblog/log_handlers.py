import os
import logging
from datetime import date, timedelta


class DailyFileHandler(logging.FileHandler):
    """
    按日期自动分文件的日志处理器。
    每天写入 {base_dir}/{YYYY-MM-DD}.log，跨天自动切换新文件，
    并清理超过 backup_count 天的旧日志。
    """

    def __init__(self, base_dir, backup_count=30, encoding='utf-8'):
        self.base_dir = base_dir
        self.backup_count = backup_count
        os.makedirs(base_dir, exist_ok=True)
        self._current_date = date.today()
        filepath = self._get_filepath(self._current_date)
        super().__init__(filepath, mode='a', encoding=encoding)

    def _get_filepath(self, d):
        return os.path.join(self.base_dir, f"{d.isoformat()}.log")

    def emit(self, record):
        today = date.today()
        if today != self._current_date:
            self._current_date = today
            self.close()
            self.baseFilename = os.path.abspath(self._get_filepath(today))
            self.stream = self._open()
            self._cleanup()
        super().emit(record)

    def _cleanup(self):
        """删除超过 backup_count 天的日志文件。"""
        if self.backup_count <= 0:
            return
        cutoff = date.today() - timedelta(days=self.backup_count)
        try:
            for filename in os.listdir(self.base_dir):
                if not filename.endswith('.log'):
                    continue
                date_str = filename.removesuffix('.log')
                try:
                    file_date = date.fromisoformat(date_str)
                except ValueError:
                    continue
                if file_date < cutoff:
                    os.remove(os.path.join(self.base_dir, filename))
        except OSError:
            pass