FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

# Wrap the command in sh -c so $PORT evaluates correctly
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
