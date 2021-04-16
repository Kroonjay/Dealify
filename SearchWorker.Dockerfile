FROM python:3.8

WORKDIR /usr/dealify

ENV DEALIFY_DB_PASSWORD="None"

ENV DEV_MODE_ENABLED="False"

ENV DEALIFY_WORKER_ID=1

COPY ./worker/dealify_worker.py ./

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "./dealify_worker.py"]