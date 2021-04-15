FROM python:3.8

WORKDIR /usr/dealify

ENV DEALIFY_DB_PASSWORD="None"

ENV DEV_MODE_ENABLED="False"

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "./worker/dealify_worker.py"]