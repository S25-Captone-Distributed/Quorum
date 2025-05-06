FROM python:3.13-alpine
WORKDIR /app

RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bridge.py .
CMD ["python", "bridge.py"]