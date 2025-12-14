FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY custom_callbacks.py /app/custom_callbacks.py
COPY tools /app/tools
EXPOSE 4000
CMD ["litellm","--config","/app/config.yaml","--port","4000","--detailed_debug"]
