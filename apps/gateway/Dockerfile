FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY config.yaml /app/config.yaml
COPY custom_callbacks.py /app/custom_callbacks.py
COPY policies /app/policies
COPY tools /app/tools

CMD ["litellm","--config","/app/config.yaml","--port","4000","--host","0.0.0.0"]
