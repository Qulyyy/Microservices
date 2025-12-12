"""
Общий модуль для метрик Prometheus
Используется во всех микросервисах для сбора метрик
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client.exposition import REGISTRY
from functools import wraps
import time

# Метрики для HTTP запросов
http_requests_total = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['service', 'method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['service', 'method', 'endpoint'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

# Метрики для бизнес-логики
business_operations_total = Counter(
    'business_operations_total',
    'Total number of business operations',
    ['service', 'operation', 'status']
)

active_connections = Gauge(
    'active_connections',
    'Number of active connections',
    ['service']
)

def track_request(service_name):
    """Декоратор для отслеживания HTTP запросов"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            endpoint = request.endpoint or 'unknown'
            method = request.method
            
            try:
                response = f(*args, **kwargs)
                status_code = response.status_code if hasattr(response, 'status_code') else 200
                
                # Записываем метрики
                http_requests_total.labels(
                    service=service_name,
                    method=method,
                    endpoint=endpoint,
                    status=status_code
                ).inc()
                
                http_request_duration_seconds.labels(
                    service=service_name,
                    method=method,
                    endpoint=endpoint
                ).observe(time.time() - start_time)
                
                return response
            except Exception as e:
                # Записываем ошибку
                http_requests_total.labels(
                    service=service_name,
                    method=method,
                    endpoint=endpoint,
                    status=500
                ).inc()
                raise
        return wrapper
    return decorator

