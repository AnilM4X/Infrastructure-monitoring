FROM python:3.11

WORKDIR /app

COPY alert_engine.py .

RUN pip install psycopg2-binary

CMD ["python", "alert_engine.py"]