"""
Общий модуль для логирования микросервисов
Используется для структурированного логирования в формате JSON для Loki
"""
import logging
import json
import sys
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Форматтер для логирования в JSON формате для Loki"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'service': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Добавляем дополнительные поля если есть
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'endpoint'):
            log_entry['endpoint'] = record.endpoint
        if hasattr(record, 'status_code'):
            log_entry['status_code'] = record.status_code
            
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry, ensure_ascii=False)

def setup_logging(service_name, level=logging.INFO):
    """Настройка логирования для микросервиса"""
    logger = logging.getLogger(service_name)
    logger.setLevel(level)
    
    # Удаляем существующие обработчики
    logger.handlers = []
    
    # Создаём обработчик для stdout (для Docker logs и Loki)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(JSONFormatter())
    
    logger.addHandler(handler)
    logger.propagate = False
    
    return logger

