FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY pod_ws_client.py /app/

CMD ["python", "pod_ws_client.py"]