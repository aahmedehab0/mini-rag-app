# Middleware is gave you details about your request with api

from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time

# Define metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP Request Latency', ['method', 'endpoint'])

class PrometheusMiddleware(BaseHTTPMiddleware):
    
    async def dispatch(self, request: Request, call_next):
        """
        # This middleware collects essential HTTP metrics for monitoring:
        #
        # 1. Measures the execution time (latency) of every HTTP request.
        # 2. Counts the total number of incoming HTTP requests.
        # 3. Records the request method (GET, POST, etc.).
        # 4. Records which endpoint was called (/login, /predict, etc.).
        # 5. Records the response status code (200, 404, 500, ...).
        # 6. Exposes all collected metrics for Prometheus to scrape and monitor.
        """
    
        start_time = time.time()

        # Process the request
        response = await call_next(request)

        # Record metrics after request is processed
        duration = time.time() - start_time
        endpoint = request.url.path

        REQUEST_LATENCY.labels(method=request.method, endpoint=endpoint).observe(duration)
        REQUEST_COUNT.labels(method=request.method, endpoint=endpoint, status=response.status_code).inc()
        return response
    
def setup_metrics(app: FastAPI):
    """
    Setup Prometheus metrics middleware and endpoint
    """
    # Add Prometheus middleware
    app.add_middleware(PrometheusMiddleware)

    @app.get("/TrhBVe_m5gg2002_E5VVqS", include_in_schema=False)
    def metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
