# Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app .
CMD ["bokeh", "serve", "--port", "5006", "--allow-websocket-origin=*", "app.py"]