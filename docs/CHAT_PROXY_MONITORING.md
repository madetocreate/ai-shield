# Chat Proxy Monitoring & Testing Guide

## Overview

This document describes the monitoring setup and testing procedures for the chat proxy endpoints.

## Monitoring

### Metrics Endpoint

The Node Backend exposes Prometheus metrics at `/metrics`:

```bash
curl http://localhost:4000/metrics
```

### Available Metrics

#### Chat Request Metrics
- `chat_requests_total` - Total number of chat requests (HTTP and Stream)
  - Labels: `method`, `status`, `endpoint`
- `chat_request_duration_seconds` - Duration of chat requests
  - Labels: `method`, `endpoint`
  - Buckets: 0.1, 0.5, 1, 2, 5, 10, 30, 60 seconds

#### Chat Stream Metrics
- `chat_stream_requests_total` - Total number of chat stream requests
  - Labels: `status`
- `chat_stream_duration_seconds` - Duration of chat stream connections
  - Labels: `status`
  - Buckets: 1, 5, 10, 30, 60, 120, 300 seconds

#### Error Metrics
- `chat_proxy_errors_total` - Total number of chat proxy errors
  - Labels: `error_type`, `endpoint`
  - Error types: `backend_error`, `proxy_error`, `timeout`, `stream_error`

#### Backend Latency
- `chat_backend_latency_seconds` - Latency to Python backend
  - Labels: `endpoint`
  - Buckets: 0.01, 0.05, 0.1, 0.5, 1, 2, 5 seconds

### Example Queries

```promql
# Total chat requests per minute
rate(chat_requests_total[1m])

# Error rate
rate(chat_proxy_errors_total[5m])

# Average request duration
histogram_quantile(0.95, chat_request_duration_seconds_bucket)

# Backend latency p99
histogram_quantile(0.99, chat_backend_latency_seconds_bucket)
```

### Logging

Chat proxy requests are logged with structured logging:

```json
{
  "requestId": "uuid",
  "tenantId": "aklow-main",
  "sessionId": "session-id",
  "channel": "web_chat",
  "duration": 1.234,
  "backendLatency": 0.567,
  "status": 200
}
```

Log levels:
- `info` - Successful requests
- `warn` - Backend errors (4xx, 5xx)
- `error` - Proxy errors, timeouts, stream errors

## Testing

### Quick Smoke Test

Run the bash script:

```bash
cd Backend
./scripts/test-chat-proxy.sh
```

With authentication:

```bash
export AUTH_TOKEN=your-token
./scripts/test-chat-proxy.sh
```

### Playwright Tests

Run the integration tests:

```bash
cd Backend
npx playwright test tests/chat-proxy.test.ts
```

With environment variables:

```bash
API_GATEWAY_URL=http://localhost:4000 \
PY_BACKEND_URL=http://localhost:8000 \
AUTH_TOKEN=your-token \
npx playwright test tests/chat-proxy.test.ts
```

### Manual Testing

#### 1. Health Check
```bash
curl http://localhost:4000/health
```

#### 2. Metrics
```bash
curl http://localhost:4000/metrics | grep chat_
```

#### 3. Chat HTTP Request
```bash
curl -X POST http://localhost:4000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "tenantId": "test-tenant",
    "sessionId": "test-session",
    "channel": "web_chat",
    "message": "Hello, test message"
  }'
```

#### 4. Chat Stream Request
```bash
curl -X POST http://localhost:4000/chat/stream \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "tenantId": "test-tenant",
    "sessionId": "test-session",
    "channel": "web_chat",
    "message": "Hello, test stream message"
  }'
```

#### 5. Check Metrics After Request
```bash
curl http://localhost:4000/metrics | grep chat_requests_total
```

## Monitoring Dashboard (Optional)

### Grafana Setup

1. Add Prometheus data source pointing to `http://localhost:4000/metrics`
2. Create dashboard with panels:
   - Chat requests per second
   - Error rate
   - Request duration (p50, p95, p99)
   - Backend latency
   - Stream duration

### Example Grafana Queries

```promql
# Requests per second
sum(rate(chat_requests_total[1m])) by (endpoint)

# Error rate
sum(rate(chat_proxy_errors_total[5m])) by (error_type)

# P95 request duration
histogram_quantile(0.95, sum(rate(chat_request_duration_seconds_bucket[5m])) by (le, endpoint))

# Backend latency p99
histogram_quantile(0.99, sum(rate(chat_backend_latency_seconds_bucket[5m])) by (le, endpoint))
```

## Alerts (Optional)

### Example Alert Rules

```yaml
groups:
  - name: chat_proxy
    rules:
      - alert: HighChatErrorRate
        expr: rate(chat_proxy_errors_total[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High chat proxy error rate"
          
      - alert: ChatProxyDown
        expr: up{job="node-backend"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Chat proxy is down"
          
      - alert: HighBackendLatency
        expr: histogram_quantile(0.99, chat_backend_latency_seconds_bucket) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High backend latency (p99 > 2s)"
```

## Troubleshooting

### Common Issues

1. **502 Bad Gateway**
   - Check if Python backend is running
   - Check `PY_BACKEND_URL` environment variable
   - Check backend logs

2. **Timeout Errors**
   - Check `PY_BACKEND_TIMEOUT_MS` (default: 60000ms)
   - Check Python backend performance
   - Check network connectivity

3. **Stream Errors**
   - Check if Python backend `/chat/stream` endpoint is working
   - Check for network interruptions
   - Review stream duration metrics

4. **High Error Rate**
   - Check metrics: `rate(chat_proxy_errors_total[5m])`
   - Review error types in logs
   - Check Python backend health

### Debug Logging

Enable debug logging:

```bash
LOG_LEVEL=debug npm start
```

This will show detailed request/response information in logs.

## Performance Benchmarks

Expected performance:
- HTTP chat request: < 2s (p95)
- Stream connection: < 100ms (initial)
- Backend latency: < 500ms (p95)
- Error rate: < 0.1%

Monitor these metrics and alert if they exceed thresholds.

